import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_lists_filtering(authed_client: AsyncClient, auth_headers: dict):
    """Test filtering lists by archived status."""
    group_id = int(auth_headers["X-Group-ID"])

    # 1. Create active lists
    active_lists = ["Active 1", "Active 2"]
    for name in active_lists:
        list_data = {
            "name": name,
            "type": "SHOPPING",
            "group_id": group_id,
        }
        res = await authed_client.post("/lists", json=list_data, headers=auth_headers)
        assert res.status_code == 201

    # 2. Create archived lists (create then update)
    archived_lists = ["Archived 1", "Archived 2", "Archived 3"]
    for name in archived_lists:
        # Create
        list_data = {
            "name": name,
            "type": "SHOPPING",
            "group_id": group_id,
        }
        res = await authed_client.post("/lists", json=list_data, headers=auth_headers)
        assert res.status_code == 201
        list_id = res.json()["id"]

        # Archive
        update_data = {"is_archived": True}
        res = await authed_client.patch(f"/lists/{list_id}", json=update_data, headers=auth_headers)
        assert res.status_code == 200

    # 3. Fetch all lists (default)
    res = await authed_client.get("/lists", headers=auth_headers)
    assert res.status_code == 200
    all_lists = res.json()
    # Should include both active and archived
    names = [lst["name"] for lst in all_lists]
    for name in active_lists + archived_lists:
        assert name in names

    # 4. Fetch only active lists (is_archived=false)
    res = await authed_client.get("/lists?is_archived=false", headers=auth_headers)
    assert res.status_code == 200
    active_fetched = res.json()
    active_names = [lst["name"] for lst in active_fetched]

    # Assert correctness
    assert len(active_fetched) == len(active_lists)
    for name in active_lists:
        assert name in active_names
    for name in archived_lists:
        assert name not in active_names

    # 5. Fetch only archived lists (is_archived=true)
    res = await authed_client.get("/lists?is_archived=true", headers=auth_headers)
    assert res.status_code == 200
    archived_fetched = res.json()
    archived_names = [lst["name"] for lst in archived_fetched]

    # Assert correctness
    assert len(archived_fetched) == len(archived_lists)
    for name in archived_lists:
        assert name in archived_names
    for name in active_lists:
        assert name not in archived_names

import pytest
from httpx import AsyncClient

from mitlist.modules.lists import interface
from mitlist.modules.lists.models import InventoryItem


@pytest.mark.asyncio
async def test_lists_lifecycle(authed_client: AsyncClient, auth_headers: dict):
    """Test lists CRUD and list items lifecycle."""
    group_id = int(auth_headers["X-Group-ID"])

    # 1. Get lists (empty)
    response = await authed_client.get("/lists", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

    # 2. Create list
    list_data = {
        "name": "Weekly groceries",
        "type": "SHOPPING",
        "group_id": group_id,
    }
    response = await authed_client.post("/lists", json=list_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    list_id = data["id"]
    assert data["name"] == "Weekly groceries"
    assert data["type"] == "SHOPPING"
    assert data["group_id"] == group_id

    # 3. Get list by id
    response = await authed_client.get(f"/lists/{list_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == list_id
    assert response.json()["name"] == "Weekly groceries"

    # 4. Get lists (with filter)
    response = await authed_client.get("/lists", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    response = await authed_client.get("/lists?list_type=TODO", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

    # 5. Update list
    update_data = {"name": "Monthly groceries", "is_archived": False}
    response = await authed_client.patch(f"/lists/{list_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Monthly groceries"

    # 6. Add item to list
    item_data = {
        "list_id": list_id,
        "name": "Milk",
        "quantity_value": 2.0,
        "quantity_unit": "L",
        "is_checked": False,
    }
    response = await authed_client.post(f"/lists/{list_id}/items", json=item_data, headers=auth_headers)
    assert response.status_code == 201
    item_id = response.json()["id"]
    assert response.json()["name"] == "Milk"
    assert response.json()["quantity_value"] == 2.0

    # 7. Get list items
    response = await authed_client.get(f"/lists/{list_id}/items", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Milk"

    # 8. Update item (check it)
    response = await authed_client.patch(
        f"/lists/{list_id}/items/{item_id}",
        json={"is_checked": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_checked"] is True

    # 9. Bulk add items
    bulk_data = {
        "items": [
            {"name": "Bread", "quantity_value": 1},
            {"name": "Eggs", "quantity_value": 12, "quantity_unit": "pcs"},
        ]
    }
    response = await authed_client.post(f"/lists/{list_id}/items/bulk", json=bulk_data, headers=auth_headers)
    assert response.status_code == 201
    created = response.json()["items"]
    assert len(created) == 2

    # 10. Delete one item
    bread_id = next(i["id"] for i in created if i["name"] == "Bread")
    response = await authed_client.delete(f"/lists/{list_id}/items/{bread_id}", headers=auth_headers)
    assert response.status_code == 204

    response = await authed_client.get(f"/lists/{list_id}/items", headers=auth_headers)
    assert response.status_code == 200
    names = [i["name"] for i in response.json()]
    assert "Bread" not in names
    assert "Milk" in names
    assert "Eggs" in names


@pytest.mark.asyncio
async def test_list_not_found(authed_client: AsyncClient, auth_headers: dict):
    """Test 404 when list does not exist or belongs to another group."""
    response = await authed_client.get("/lists/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_list_group_mismatch(authed_client: AsyncClient, auth_headers: dict):
    """Test validation error when group_id in body does not match current group."""
    group_id = int(auth_headers["X-Group-ID"])
    list_data = {
        "name": "Other list",
        "type": "TODO",
        "group_id": group_id + 1,
    }
    response = await authed_client.post("/lists", json=list_data, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_item_list_mismatch(authed_client: AsyncClient, auth_headers: dict, db_session):
    """Test error when list_id in body does not match path."""
    group_id = int(auth_headers["X-Group-ID"])
    list_obj = await interface.create_list(db_session, group_id, "Test", "SHOPPING")
    await db_session.commit()
    list_id = list_obj.id
    item_data = {"list_id": list_id + 1, "name": "Item"}
    response = await authed_client.post(
        f"/lists/{list_id}/items",
        json=item_data,
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_inventory_empty(authed_client: AsyncClient, auth_headers: dict):
    """Test get inventory when empty."""
    response = await authed_client.get("/inventory", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_inventory_patch(authed_client: AsyncClient, auth_headers: dict, db_session):
    """Test patch inventory item (create via DB, update via API)."""
    group_id = int(auth_headers["X-Group-ID"])
    inv = InventoryItem(
        group_id=group_id,
        quantity_value=5.0,
        quantity_unit="kg",
    )
    db_session.add(inv)
    await db_session.flush()
    await db_session.refresh(inv)
    await db_session.commit()
    inv_id = inv.id

    response = await authed_client.patch(
        f"/inventory/{inv_id}",
        json={"quantity_value": 3.0, "restock_threshold": 1.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["quantity_value"] == 3.0
    assert response.json()["restock_threshold"] == 1.0

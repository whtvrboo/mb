import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_bulk_add_items_limit(client: AsyncClient, test_group):
    # 1. Create a list
    list_data = {
        "name": "Huge List",
        "type": "SHOPPING",
        "group_id": test_group.id
    }
    response = await client.post("/api/v1/lists", json=list_data)
    assert response.status_code == 201
    list_id = response.json()["id"]

    # 2. Create payload with 150 items
    items = []
    for i in range(150):
        items.append({"name": f"Item {i}", "quantity_value": 1})

    payload = {"items": items}

    # 3. Send bulk create request
    response = await client.post(f"/api/v1/lists/{list_id}/items/bulk", json=payload)

    # 4. It should now fail with 422 Unprocessable Entity
    assert response.status_code == 422
    error_data = response.json()
    assert error_data["code"] == "VALIDATION_ERROR"
    # Check that the validation error is about the list length
    assert error_data["errors"][0]["type"] == "too_long"
    assert error_data["errors"][0]["loc"] == ["body", "items"]

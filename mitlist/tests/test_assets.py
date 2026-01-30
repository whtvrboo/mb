import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_assets_lifecycle(authed_client: AsyncClient, auth_headers: dict):
    # 1. Create Asset
    asset_data = {
        "name": "Refrigerator",
        "asset_type": "APPLIANCE",
        "brand": "Samsung",
        "purchase_price": 1200.00,
        "group_id": int(auth_headers["X-Group-ID"])
    }
    response = await authed_client.post("/assets", json=asset_data, headers=auth_headers)
    assert response.status_code == 201
    asset_id = response.json()["id"]
    
    # 2. Get Asset
    response = await authed_client.get(f"/assets/{asset_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # 3. Create Maintenance Task
    task_data = {
        "asset_id": asset_id,
        "name": "Change Water Filter",
        "frequency_days": 180,
        "priority": "MEDIUM"
    }
    response = await authed_client.post(f"/assets/{asset_id}/tasks", json=task_data, headers=auth_headers)
    assert response.status_code == 201
    task_id = response.json()["id"]
    
    # 4. Create Log (Complete Task)
    log_data = {
        "actual_duration_minutes": 10,
        "notes": "Fast change"
    }
    response = await authed_client.post(f"/assets/tasks/{task_id}/logs", json=log_data, headers=auth_headers)
    assert response.status_code == 201
    
    # 5. Create Insurance
    ins_data = {
        "group_id": int(auth_headers["X-Group-ID"]),
        "policy_number": "POL123",
        "provider_name": "SafeHome",
        "coverage_type": "HOMEOWNERS",
        "premium_amount": 500.0,
        "premium_frequency": "YEARLY",
        "start_date": datetime.now(timezone.utc).isoformat()
    }
    response = await authed_client.post("/assets/insurance", json=ins_data, headers=auth_headers)
    assert response.status_code == 201

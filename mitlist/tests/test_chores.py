import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chores_lifecycle(authed_client: AsyncClient, auth_headers: dict):
    # 1. Create Chore 1
    chore1_data = {
        "name": "Clean Kitchen",
        "effort_value": 5,
        "frequency_type": "DAILY",
        "interval_value": 1,
        "group_id": int(auth_headers["X-Group-ID"])
    }
    response = await authed_client.post("/chores", json=chore1_data, headers=auth_headers)
    if response.status_code != 201:
        with open("debug_error.txt", "w") as f:
            f.write(response.text)
    assert response.status_code == 201
    c1_id = response.json()["id"]
    
    # 2. Create Chore 2
    chore2_data = {
        "name": "Cook Dinner",
        "effort_value": 8,
        "frequency_type": "DAILY",
        "interval_value": 1,
        "group_id": int(auth_headers["X-Group-ID"])
    }
    response = await authed_client.post("/chores", json=chore2_data, headers=auth_headers)
    assert response.status_code == 201
    c2_id = response.json()["id"]
    
    # 3. Add Dependency (Cook depends on Clean - wait, actually opposite usually, but let's say Cook requires Clean Kitchen first)
    dep_data = {
        "chore_id": c2_id,
        "depends_on_chore_id": c1_id,
        "dependency_type": "BLOCKING"
    }
    response = await authed_client.post(f"/chores/{c2_id}/dependencies", json=dep_data, headers=auth_headers)
    assert response.status_code == 201
    
    # 4. Create Template
    tpl_data = {
        "name": "Weekend Cleaning",
        "description": "Deep clean",
        "effort_value": 8,
        "frequency_type": "WEEKLY",
        "interval_value": 1,
        "estimated_duration_minutes": 120,
        "group_id": int(auth_headers["X-Group-ID"])
    }
    response = await authed_client.post("/chores/templates", json=tpl_data, headers=auth_headers)
    assert response.status_code == 201
    tpl_id = response.json()["id"]
    
    # 5. Instantiate Template
    inst_data = {
        "template_id": tpl_id,
        "group_id": int(auth_headers["X-Group-ID"]),
        "name": "Deep Clean Living Room"
    }
    response = await authed_client.post(f"/chores/templates/{tpl_id}/instantiate", json=inst_data, headers=auth_headers)
    assert response.status_code == 201, f"Response: {response.text}"
    
    # 6. Stats
    response = await authed_client.get("/chores/stats", headers=auth_headers)
    assert response.status_code == 200

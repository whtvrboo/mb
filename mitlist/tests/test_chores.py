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

    # 3. Add Dependency (Cook depends on Clean)
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
        "category": "CLEANING",
        "is_public": False
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
    assert response.status_code in [200, 201]

    # 6. Stats
    response = await authed_client.get("/chores/stats", headers=auth_headers)
    assert response.status_code == 200

    # 7. Start Assignment
    # First need to find an assignment. list_assignments checks due items.
    response = await authed_client.get("/chores/assignments", headers=auth_headers)
    assert response.status_code == 200
    assignments = response.json()
    
    if not assignments:
        return

    asg_id = assignments[0]["id"]
    # Start
    response = await authed_client.patch(f"/chores/assignments/{asg_id}/start", headers=auth_headers)
    assert response.status_code == 200

    # 7.5. Complete Assignment
    complete_data = {
        "actual_duration_minutes": 30,
        "notes": "Done"
    }
    response = await authed_client.patch(f"/chores/assignments/{asg_id}/complete", json=complete_data, headers=auth_headers)
    assert response.status_code == 200

    # 8. Rate Assignment
    rate_data = {
        "quality_rating": 5
    }
    response = await authed_client.post(f"/chores/assignments/{asg_id}/rate", json=rate_data, headers=auth_headers)
    assert response.status_code == 200

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_plants_lifecycle(authed_client: AsyncClient, auth_headers: dict):
    # 1. Create Species (Service only or via API if exposed? API has GET. Service has create.)
    # API doesn't have POST /species. We should have seeded it or use service fixture.
    # But wait, creating a plant requires species_id.
    # I need to create a species first.
    # I'll use the DB session fixture to create one? 
    # Or call a hidden/admin endpoint?
    # I'll rely on "create_species" service function being available if I import it in conftest or use `db_session` in test.
    # Actually, I can inject `db_session` here and create it.
    pass

@pytest.mark.asyncio
async def test_create_species_and_plant(authed_client: AsyncClient, auth_headers: dict, db_session):
    from mitlist.modules.plants.models import PlantSpecies
    
    # 1. Seed Species
    species = PlantSpecies(
        scientific_name="Monstera deliciosa",
        common_name="Swiss Cheese Plant",
        toxicity="TOXIC_CATS",
        light_needs="INDIRECT"
    )
    db_session.add(species)
    await db_session.commit()
    await db_session.refresh(species)
    
    # 2. Create Plant via API
    plant_data = {
        "species_id": species.id,
        "nickname": "Monty",
        "acquired_from": "STORE",
        "pot_size_cm": 25,
        "group_id": int(auth_headers["X-Group-ID"])
    }
    response = await authed_client.post("/plants", json=plant_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nickname"] == "Monty"
    plant_id = data["id"]
    
    # 3. Get Plant
    response = await authed_client.get(f"/plants/{plant_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["species"]["common_name"] == "Swiss Cheese Plant"
    
    # 4. Create Log
    log_data = {
        "plant_id": plant_id,
        "action": "WATER",
        "occurred_at": datetime.utcnow().isoformat(),
        "notes": "Watered nicely"
    }
    response = await authed_client.post(f"/plants/{plant_id}/logs", json=log_data, headers=auth_headers)
    assert response.status_code == 201
    
    # 5. List Logs
    response = await authed_client.get(f"/plants/{plant_id}/logs", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
    # 6. Create Schedule
    sched_data = {
        "plant_id": plant_id,
        "action_type": "WATER",
        "frequency_days": 7,
        "next_due_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }
    response = await authed_client.post(f"/plants/{plant_id}/schedules", json=sched_data, headers=auth_headers)
    assert response.status_code == 201
    sched_id = response.json()["id"]
    
    # 7. Mark Schedule Done
    done_data = {
        "notes": "Done via schedule"
    }
    response = await authed_client.patch(f"/plants/schedules/{sched_id}/done", json=done_data, headers=auth_headers)
    assert response.status_code == 200

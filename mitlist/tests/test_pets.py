import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone


@pytest.mark.asyncio
async def test_pets_lifecycle(authed_client: AsyncClient, auth_headers: dict):
    # 1. Create Pet
    pet_data = {
        "name": "Buddy",
        "species": "DOG",
        "breed": "Golden Retriever",
        "sex": "MALE",
        "group_id": int(auth_headers["X-Group-ID"]),
    }
    response = await authed_client.post("/pets", json=pet_data, headers=auth_headers)
    assert response.status_code == 201
    pet_id = response.json()["id"]

    # 2. Get Pet
    response = await authed_client.get(f"/pets/{pet_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Buddy"

    # 3. Create Medical Record (Vaccine)
    med_data = {
        "pet_id": pet_id,
        "type": "VACCINE",
        "description": "Rabies",
        "performed_at": datetime.now(timezone.utc).isoformat(),
        # "expires_at": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
        "performed_by": "Dr. Vet",
    }
    response = await authed_client.post(
        f"/pets/{pet_id}/medical", json=med_data, headers=auth_headers
    )
    assert response.status_code == 201

    # 4. Check Expiring Vaccines (should be none or one if we manipulate dates, but just calling endpoint is good)
    response = await authed_client.get(
        "/pets/vaccines/expiring?days_ahead=300", headers=auth_headers
    )
    assert response.status_code == 200

    # 5. Create Log
    log_data = {
        "pet_id": pet_id,
        "action": "WALK",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Good walk",
    }
    response = await authed_client.post(f"/pets/{pet_id}/logs", json=log_data, headers=auth_headers)
    assert response.status_code == 201

    # 6. Create Schedule
    sched_data = {
        "pet_id": pet_id,
        "action_type": "FEED",
        "frequency_type": "DAILY",
        "time_of_day": "08:00:00",
    }
    response = await authed_client.post(
        f"/pets/{pet_id}/schedules", json=sched_data, headers=auth_headers
    )
    assert response.status_code == 201
    sched_id = response.json()["id"]

    # 7. Mark Schedule Done
    done_data = {"notes": "Fed breakfast"}
    response = await authed_client.patch(
        f"/pets/schedules/{sched_id}/done", json=done_data, headers=auth_headers
    )
    assert response.status_code == 200

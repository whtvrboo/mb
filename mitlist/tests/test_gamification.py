import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gamification_points_and_summary(authed_client: AsyncClient, auth_headers: dict):
    """Get points (creates record if missing) and summary."""
    response = await authed_client.get("/gamification/points", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_points" in data
    assert "monthly_points" in data
    assert data["total_points"] >= 0
    assert data["monthly_points"] >= 0

    response = await authed_client.get("/gamification/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_points" in data
    assert "achievements_earned" in data
    assert "active_streaks" in data
    assert "longest_streak_ever" in data


@pytest.mark.asyncio
async def test_gamification_award_points_admin(
    authed_client: AsyncClient, auth_headers: dict, test_user, test_group
):
    """Admin can award points to a user."""
    award_data = {
        "user_id": test_user.id,
        "group_id": test_group.id,
        "points": 10,
        "reason": "Test award",
    }
    response = await authed_client.post(
        "/gamification/points/award", json=award_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["points_awarded"] == 10
    assert data["new_total"] >= 10
    assert data["new_monthly"] >= 10
    assert data["reason"] == "Test award"

    response = await authed_client.get("/gamification/points", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total_points"] >= 10


@pytest.mark.asyncio
async def test_gamification_achievements_list_and_me(
    authed_client: AsyncClient, auth_headers: dict
):
    """List all achievements and current user's earned achievements."""
    response = await authed_client.get("/gamification/achievements", headers=auth_headers)
    assert response.status_code == 200
    achievements = response.json()
    assert isinstance(achievements, list)

    response = await authed_client.get("/gamification/achievements/me", headers=auth_headers)
    assert response.status_code == 200
    my_achievements = response.json()
    assert isinstance(my_achievements, list)


@pytest.mark.asyncio
async def test_gamification_check_achievements(authed_client: AsyncClient, auth_headers: dict):
    """Check and award any new achievements for current user."""
    response = await authed_client.post("/gamification/achievements/check", headers=auth_headers)
    assert response.status_code == 200
    newly_awarded = response.json()
    assert isinstance(newly_awarded, list)


@pytest.mark.asyncio
async def test_gamification_streaks_record_and_list(authed_client: AsyncClient, auth_headers: dict):
    """Record activity for streak and list streaks."""
    record_data = {
        "activity_type": "CHORES",
        "group_id": int(auth_headers["X-Group-ID"]),
    }
    response = await authed_client.post(
        "/gamification/streaks/record", json=record_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "streak" in data
    assert "streak_extended" in data
    assert "is_new_record" in data
    assert data["streak"]["activity_type"] == "CHORES"
    assert data["streak"]["current_streak_days"] >= 1

    response = await authed_client.get("/gamification/streaks", headers=auth_headers)
    assert response.status_code == 200
    streaks = response.json()
    assert isinstance(streaks, list)


@pytest.mark.asyncio
async def test_gamification_leaderboard(authed_client: AsyncClient, auth_headers: dict):
    """Get group leaderboard."""
    response = await authed_client.get(
        "/gamification/leaderboard?period_type=MONTHLY&metric=POINTS",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert "total_participants" in data
    assert isinstance(data["entries"], list)

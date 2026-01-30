import pytest
from datetime import date, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_calendar_feed_empty(authed_client: AsyncClient, auth_headers: dict):
    """Get calendar feed with no events (default range)."""
    response = await authed_client.get("/calendar/feed", headers=auth_headers)
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)


@pytest.mark.asyncio
async def test_calendar_feed_with_date_range(authed_client: AsyncClient, auth_headers: dict):
    """Get calendar feed with explicit start_date and end_date."""
    start = date.today()
    end = start + timedelta(days=30)
    response = await authed_client.get(
        f"/calendar/feed?start_date={start.isoformat()}&end_date={end.isoformat()}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)


@pytest.mark.asyncio
async def test_calendar_feed_returns_event_shape(authed_client: AsyncClient, auth_headers: dict):
    """Calendar feed returns list of events with expected keys when present."""
    response = await authed_client.get("/calendar/feed", headers=auth_headers)
    assert response.status_code == 200
    events = response.json()
    for event in events:
        assert "id" in event
        assert "type" in event
        assert "title" in event
        assert "date" in event

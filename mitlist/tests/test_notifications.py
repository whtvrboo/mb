"""Tests for notifications, preferences, comments, and reactions API."""

import pytest
from httpx import AsyncClient

from mitlist.modules.auth.models import User
from mitlist.modules.auth.models import Group
from mitlist.modules.notifications.interface import (
    create_notification,
    create_comment,
)


@pytest.fixture
async def sample_notification(db_session, test_user: User, test_group: Group):
    """Create one notification for the test user."""
    n = await create_notification(
        db_session,
        user_id=test_user.id,
        type="TASK",
        title="Test notification",
        body="You have a task",
        group_id=test_group.id,
        priority="MEDIUM",
    )
    await db_session.commit()
    return n


@pytest.mark.asyncio
async def test_notifications_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List notifications when none exist returns empty list and zero unread."""
    response = await authed_client.get("/notifications", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["notifications"] == []
    assert body["unread_count"] == 0
    assert body["total_count"] == 0


@pytest.mark.asyncio
async def test_notifications_list_with_one(
    authed_client: AsyncClient, auth_headers: dict, sample_notification
):
    """List notifications returns created notification."""
    response = await authed_client.get("/notifications", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body["notifications"]) >= 1
    n = next(
        (x for x in body["notifications"] if x["id"] == sample_notification.id),
        None,
    )
    assert n is not None
    assert n["title"] == "Test notification"
    assert n["is_read"] is False
    assert body["unread_count"] >= 1


@pytest.mark.asyncio
async def test_notifications_mark_read(
    authed_client: AsyncClient, auth_headers: dict, sample_notification
):
    """PATCH /notifications/{id}/read marks notification as read."""
    response = await authed_client.patch(
        f"/notifications/{sample_notification.id}/read", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_read"] is True
    assert body["id"] == sample_notification.id


@pytest.mark.asyncio
async def test_notifications_mark_all_read(
    authed_client: AsyncClient, auth_headers: dict, sample_notification
):
    """POST /notifications/clear marks all as read."""
    response = await authed_client.post(
        "/notifications/clear", json={}, headers=auth_headers
    )
    assert response.status_code == 204

    response = await authed_client.get("/notifications", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_notifications_count(authed_client: AsyncClient, auth_headers: dict):
    """GET /notifications/count returns unread count."""
    response = await authed_client.get("/notifications/count", headers=auth_headers)
    assert response.status_code == 200
    assert "unread_count" in response.json()


@pytest.mark.asyncio
async def test_notifications_preferences_get_empty(
    authed_client: AsyncClient, auth_headers: dict
):
    """GET /notifications/preferences returns list (may be empty)."""
    response = await authed_client.get(
        "/notifications/preferences", headers=auth_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_notifications_preferences_update(
    authed_client: AsyncClient, auth_headers: dict
):
    """PATCH /notifications/preferences creates or updates a preference."""
    data = {
        "event_type": "TASK_DUE",
        "channel": "IN_APP",
        "enabled": True,
        "advance_notice_hours": 24,
    }
    response = await authed_client.patch(
        "/notifications/preferences", json=data, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["event_type"] == "TASK_DUE"
    assert body["channel"] == "IN_APP"
    assert body["enabled"] is True
    assert body.get("advance_notice_hours") == 24


# ---------- Comments ----------
@pytest.mark.asyncio
async def test_comments_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List comments for an entity with no comments returns empty list."""
    response = await authed_client.get(
        "/comments?parent_type=CHORE&parent_id=99999", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_comments_create_list_update_delete(
    authed_client: AsyncClient, auth_headers: dict, db_session, test_user, test_group
):
    """Create comment, list it, update it, delete it."""
    # Use a real parent - e.g. a chore. We need parent_id. Create a minimal chore
    # or use an existing entity. Comments parent_type can be CHORE, EXPENSE, etc.
    # Use CHORE and create a chore via interface so we have a valid parent_id.
    from mitlist.modules.chores.interface import create_chore

    chore = await create_chore(
        db_session,
        group_id=test_group.id,
        name="Comment test chore",
        frequency_type="WEEKLY",
        effort_value=5,
        description="For comment tests",
    )
    await db_session.commit()
    parent_id = chore.id

    # Create comment via API
    data = {
        "parent_type": "CHORE",
        "parent_id": parent_id,
        "content": "First comment",
        "mentioned_user_ids": [],
    }
    response = await authed_client.post("/comments", json=data, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["content"] == "First comment"
    assert body["author_id"] == test_user.id
    comment_id = body["id"]

    # List comments
    response = await authed_client.get(
        f"/comments?parent_type=CHORE&parent_id={parent_id}", headers=auth_headers
    )
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) >= 1
    assert any(c["id"] == comment_id for c in comments)

    # Update comment
    response = await authed_client.patch(
        f"/comments/{comment_id}",
        json={"content": "Updated comment"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Updated comment"

    # Delete comment
    response = await authed_client.delete(
        f"/comments/{comment_id}", headers=auth_headers
    )
    assert response.status_code == 204


# ---------- Reactions ----------
@pytest.mark.asyncio
async def test_reactions_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List reactions for a target with none returns empty list."""
    response = await authed_client.get(
        "/reactions?target_type=COMMENT&target_id=99999", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_reactions_toggle_and_list(
    authed_client: AsyncClient, auth_headers: dict, db_session, test_user, test_group
):
    """Toggle reaction adds it, toggle again removes it; list shows reactions."""
    # Create a comment to react to
    from mitlist.modules.chores.interface import create_chore

    chore = await create_chore(
        db_session,
        group_id=test_group.id,
        name="Reaction test chore",
        frequency_type="WEEKLY",
        effort_value=5,
    )
    await db_session.commit()
    comment = await create_comment(
        db_session,
        author_id=test_user.id,
        parent_type="CHORE",
        parent_id=chore.id,
        content="React to this",
    )
    await db_session.commit()
    target_id = comment.id

    # Toggle reaction (add)
    data = {
        "target_type": "COMMENT",
        "target_id": target_id,
        "emoji_code": "thumbs_up",
    }
    response = await authed_client.post(
        "/reactions/toggle", json=data, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "added"
    assert body.get("reaction") is not None
    assert body["reaction"]["emoji_code"] == "thumbs_up"

    # List reactions
    response = await authed_client.get(
        f"/reactions?target_type=COMMENT&target_id={target_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    reactions = response.json()
    assert len(reactions) >= 1
    assert any(r["emoji_code"] == "thumbs_up" for r in reactions)

    # Toggle again (remove)
    response = await authed_client.post(
        "/reactions/toggle", json=data, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["action"] == "removed"

    # List should be empty (or one less)
    response = await authed_client.get(
        f"/reactions?target_type=COMMENT&target_id={target_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    reactions_after = response.json()
    assert len(reactions_after) == len(reactions) - 1

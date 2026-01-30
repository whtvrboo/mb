"""Tests for audit module: tags and entity history."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_audit_trail_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List audit logs when none exist."""
    response = await authed_client.get("/admin/audit-trail", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert data["total_count"] >= 0
    assert isinstance(data["logs"], list)


@pytest.mark.asyncio
async def test_entity_history_empty(authed_client: AsyncClient, auth_headers: dict):
    """Get entity history when no logs exist for entity."""
    response = await authed_client.get(
        "/admin/audit-trail/entity",
        params={"entity_type": "expense", "entity_id": 99999},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["entity_type"] == "expense"
    assert data["entity_id"] == 99999
    assert data["total_changes"] == 0
    assert data["history"] == []


@pytest.mark.asyncio
async def test_tags_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List tags when none exist."""
    response = await authed_client.get("/admin/tags", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_tag_create_list_patch_delete(authed_client: AsyncClient, auth_headers: dict):
    """Create tag, list, patch, and delete."""
    group_id = int(auth_headers["X-Group-ID"])

    # Create tag
    create_data = {
        "group_id": group_id,
        "name": "urgent",
        "color_hex": "#ff0000",
    }
    response = await authed_client.post("/admin/tags", json=create_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    tag_id = data["id"]
    assert data["name"] == "urgent"
    assert data["group_id"] == group_id
    assert data["color_hex"] == "#ff0000"

    # List tags
    response = await authed_client.get("/admin/tags", headers=auth_headers)
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) >= 1
    assert any(t["id"] == tag_id for t in tags)

    # Patch tag
    response = await authed_client.patch(
        f"/admin/tags/{tag_id}",
        json={"name": "high-priority", "color_hex": "#cc0000"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "high-priority"
    assert response.json()["color_hex"] == "#cc0000"

    # Assign tag to entity
    assign_data = {
        "tag_id": tag_id,
        "entity_type": "expense",
        "entity_id": 1,
    }
    response = await authed_client.post(
        "/admin/tags/assign",
        json=assign_data,
        headers=auth_headers,
    )
    assert response.status_code == 201
    assign_resp = response.json()
    assert assign_resp["tag_id"] == tag_id
    assert assign_resp["entity_type"] == "expense"
    assert assign_resp["entity_id"] == 1

    # Get entity tags
    response = await authed_client.get(
        "/admin/tags/entity",
        params={"entity_type": "expense", "entity_id": 1},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["entity_type"] == "expense"
    assert data["entity_id"] == 1
    assert len(data["tags"]) >= 1
    assert any(t["id"] == tag_id for t in data["tags"])

    # Delete tag
    response = await authed_client.delete(f"/admin/tags/{tag_id}", headers=auth_headers)
    assert response.status_code == 204

    # List tags again (tag gone)
    response = await authed_client.get("/admin/tags", headers=auth_headers)
    assert response.status_code == 200
    tags_after = response.json()
    assert not any(t["id"] == tag_id for t in tags_after)


@pytest.mark.asyncio
async def test_tag_not_found(authed_client: AsyncClient, auth_headers: dict):
    """Patch/delete non-existent tag returns 404."""
    response = await authed_client.patch(
        "/admin/tags/99999",
        json={"name": "x"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json().get("code") == "TAG_NOT_FOUND"

    response = await authed_client.delete("/admin/tags/99999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json().get("code") == "TAG_NOT_FOUND"

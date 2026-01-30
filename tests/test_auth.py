"""Tests for auth module."""

from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.auth.models import Group, Invite, User, UserGroup


class TestGroups:
    """Test group endpoints."""

    async def test_create_group(self, client: AsyncClient, test_user: User):
        """Test creating a group."""
        response = await client.post(
            "/api/v1/groups",
            json={
                "name": "New Group",
                "description": "A new test group",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Group"
        assert data["description"] == "A new test group"
        assert "id" in data

    async def test_list_groups(self, client: AsyncClient, test_group: Group):
        """Test listing groups."""
        response = await client.get("/api/v1/groups")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(g["id"] == test_group.id for g in data)

    async def test_get_group(self, client: AsyncClient, test_group: Group):
        """Test getting a group."""
        response = await client.get(f"/api/v1/groups/{test_group.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_group.id
        assert data["name"] == test_group.name

    async def test_update_group(self, client: AsyncClient, test_group: Group):
        """Test updating a group."""
        response = await client.patch(
            f"/api/v1/groups/{test_group.id}",
            json={"name": "Updated Group Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Group Name"

    async def test_get_group_members(self, client: AsyncClient, test_group: Group, test_user: User):
        """Test getting group members."""
        response = await client.get(f"/api/v1/groups/{test_group.id}/members")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(m["user_id"] == test_user.id for m in data)


class TestInvites:
    """Test invite endpoints."""

    async def test_create_invite(self, client: AsyncClient, test_group: Group):
        """Test creating a group invite."""
        response = await client.post(
            f"/api/v1/groups/{test_group.id}/invites",
            json={
                "email": "newuser@example.com",
                "role": "MEMBER",
                "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "MEMBER"
        assert data["status"] == "PENDING"
        assert "invite_code" in data

    async def test_list_invites(self, client: AsyncClient, test_group: Group, db: AsyncSession):
        """Test listing group invites."""
        invite = Invite(
            group_id=test_group.id,
            email="invite@example.com",
            role="MEMBER",
            invite_code="TEST123",
            status="PENDING",
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.add(invite)
        await db.flush()

        response = await client.get(f"/api/v1/groups/{test_group.id}/invites")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(i["email"] == "invite@example.com" for i in data)

    async def test_revoke_invite(self, client: AsyncClient, test_group: Group, db: AsyncSession):
        """Test revoking an invite."""
        invite = Invite(
            group_id=test_group.id,
            email="revoke@example.com",
            role="MEMBER",
            invite_code="REVOKE123",
            status="PENDING",
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.add(invite)
        await db.flush()
        await db.refresh(invite)

        response = await client.delete(f"/api/v1/groups/{test_group.id}/invites/{invite.id}")
        assert response.status_code == 204


class TestMembers:
    """Test member management endpoints."""

    async def test_add_member(
        self, client: AsyncClient, test_group: Group, test_user2: User, db: AsyncSession
    ):
        """Test adding a member to a group."""
        response = await client.post(
            f"/api/v1/groups/{test_group.id}/members",
            json={"user_id": test_user2.id, "role": "MEMBER"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == test_user2.id
        assert data["role"] == "MEMBER"

        result = await db.execute(
            select(UserGroup).where(
                UserGroup.group_id == test_group.id, UserGroup.user_id == test_user2.id
            )
        )
        membership = result.scalar_one_or_none()
        assert membership is not None

    async def test_update_member_role(
        self, client: AsyncClient, test_group: Group, test_user2: User, db: AsyncSession
    ):
        """Test updating a member's role."""
        membership = UserGroup(
            user_id=test_user2.id,
            group_id=test_group.id,
            role="MEMBER",
            joined_at=datetime.utcnow(),
        )
        db.add(membership)
        await db.flush()

        response = await client.patch(
            f"/api/v1/groups/{test_group.id}/members/{test_user2.id}",
            json={"role": "ADMIN"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "ADMIN"

    async def test_remove_member(
        self, client: AsyncClient, test_group: Group, test_user2: User, db: AsyncSession
    ):
        """Test removing a member from a group."""
        membership = UserGroup(
            user_id=test_user2.id,
            group_id=test_group.id,
            role="MEMBER",
            joined_at=datetime.utcnow(),
        )
        db.add(membership)
        await db.flush()

        response = await client.delete(f"/api/v1/groups/{test_group.id}/members/{test_user2.id}")
        assert response.status_code == 204

        result = await db.execute(
            select(UserGroup).where(
                UserGroup.group_id == test_group.id,
                UserGroup.user_id == test_user2.id,
                UserGroup.left_at.is_(None),
            )
        )
        membership = result.scalar_one_or_none()
        assert membership is None

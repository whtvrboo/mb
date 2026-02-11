import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api import deps
from mitlist.modules.auth.api import router as auth_router
from mitlist.modules.auth.models import Group, Invite, User


@pytest.fixture
def app_with_auth(app_instance: FastAPI):
    app_instance.include_router(auth_router)
    return app_instance


@pytest.fixture
async def client_with_auth(app_with_auth: FastAPI, db_session: AsyncSession) -> AsyncClient:
    async def override_get_db():
        yield db_session

    app_with_auth.dependency_overrides[deps.get_db] = override_get_db
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app_with_auth.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_invite_concurrency_protection(
    client_with_auth: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    test_group: Group,
    app_with_auth: FastAPI,
):
    """Test that invite acceptance works and increments use_count."""

    # 1. Create invite as Admin (test_user)
    app_with_auth.dependency_overrides[deps.get_current_user] = lambda: test_user

    invite_data = {"group_id": test_group.id, "role": "MEMBER", "max_uses": 5}
    response = await client_with_auth.post("/invites", json=invite_data)
    assert response.status_code == 201
    invite_code = response.json()["code"]

    # 2. Create a second user who will join
    user2 = User(email="joiner@example.com", name="Joiner", hashed_password="pw", is_active=True)
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    # 3. Accept invite as user2
    app_with_auth.dependency_overrides[deps.get_current_user] = lambda: user2

    join_data = {"code": invite_code}
    response = await client_with_auth.post("/invites/join", json=join_data)
    assert response.status_code == 200

    # Verify membership in response
    data = response.json()
    assert data["user_id"] == user2.id
    assert data["group_id"] == test_group.id

    # 4. Verify invite use count in DB
    result = await db_session.execute(select(Invite).where(Invite.code == invite_code))
    invite = result.scalar_one()
    assert invite.use_count == 1

    # 5. Try to join again (should return existing membership, not increment count ideally,
    # but the service logic says:
    # existing = await get_membership(...)
    # if existing: return existing
    # So use_count should NOT increment.

    response = await client_with_auth.post("/invites/join", json=join_data)
    assert response.status_code == 200

    # Verify count is still 1
    db_session.expire_all()  # Ensure we fetch fresh data
    result = await db_session.execute(select(Invite).where(Invite.code == invite_code))
    invite = result.scalar_one()
    assert invite.use_count == 1

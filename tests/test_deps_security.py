import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from mitlist.modules.auth.models import User
from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError

@pytest.mark.asyncio
async def test_account_takeover_protection(db: AsyncSession):
    """
    Verify that an existing user linked to one Zitadel sub cannot be taken over
    by a token with the same email but a different sub.
    """
    # Setup: User linked to sub1
    user = User(
        email="victim@example.com",
        hashed_password="EXTERNAL_AUTH:sub1",
        name="Victim User",
        is_active=True,
        preferences={"zitadel_sub": "sub1"},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Attempt: Login with same email but sub2
    claims = {"sub": "sub2", "email": "victim@example.com", "name": "Victim User"}

    # Expect: UnauthorizedError (currently fails because logic is broken)
    # Once fixed, this should raise UnauthorizedError
    try:
        await get_current_user(claims=claims, db=db)
        # If no error raised, assert failure (demonstrating vulnerability)
        # For reproduction, we might want to assert that it DOES succeed to prove it's broken?
        # But standard TDD is write failing test.
        # So I expect it to raise UnauthorizedError, and it will fail to raise it.
    except UnauthorizedError as e:
        assert e.code == "SUB_MISMATCH"
        return

    # If we get here, the vulnerability exists!
    pytest.fail("Vulnerability exposed: Account takeover allowed via sub substitution")

@pytest.mark.asyncio
async def test_tofu_linking(db: AsyncSession):
    """
    Verify that a user without a linked sub (Trust On First Use) gets linked correctly.
    """
    # Setup: User NOT linked to any sub
    user = User(
        email="newuser@example.com",
        hashed_password="EXTERNAL_AUTH:none",
        name="New User",
        is_active=True,
        preferences={}, # No zitadel_sub
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Attempt: Login with sub3
    claims = {"sub": "sub3", "email": "newuser@example.com", "name": "New User"}

    # Expect: Success and linking
    updated_user = await get_current_user(claims=claims, db=db)

    assert updated_user.id == user.id
    assert updated_user.preferences["zitadel_sub"] == "sub3"

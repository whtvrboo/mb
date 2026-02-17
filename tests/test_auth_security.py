import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock

from mitlist.modules.auth.models import User
from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError

@pytest.mark.asyncio
async def test_prevent_account_takeover_on_sub_mismatch(db: AsyncSession):
    """Verify that a user with an existing zitadel_sub cannot be accessed with a different sub."""
    email = "victim@example.com"
    original_sub = "original-sub-123"
    attacker_sub = "attacker-sub-666"

    # Setup: Create user with existing sub link
    user = User(
        email=email,
        hashed_password="hashed_pw",
        name="Victim",
        avatar_url=None,
        is_active=True,
        preferences={"zitadel_sub": original_sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Attack: Try to login with different sub
    claims = {
        "sub": attacker_sub,
        "email": email,
        "name": "Attacker"
    }

    # Expect UnauthorizedError
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims=claims, db=db)

    assert excinfo.value.code == "TOKEN_SUB_MISMATCH"

    # Verify database state remained unchanged
    await db.refresh(user)
    assert user.preferences["zitadel_sub"] == original_sub

@pytest.mark.asyncio
async def test_allow_login_on_sub_match(db: AsyncSession):
    """Verify that a user can login with the correct sub."""
    email = "user@example.com"
    sub = "correct-sub-123"

    user = User(
        email=email,
        hashed_password="hashed_pw",
        name="User",
        avatar_url=None,
        is_active=True,
        preferences={"zitadel_sub": sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()

    claims = {
        "sub": sub,
        "email": email,
        "name": "User"
    }

    authenticated_user = await get_current_user(claims=claims, db=db)
    assert authenticated_user.id == user.id

@pytest.mark.asyncio
async def test_trust_on_first_use_sets_sub(db: AsyncSession):
    """Verify that a user without a stored sub gets it set on first login (TOFU)."""
    email = "newuser@example.com"
    sub = "new-sub-123"

    # User created (e.g. via invite) without sub
    user = User(
        email=email,
        hashed_password="hashed_pw",
        name="New User",
        avatar_url=None,
        is_active=True,
        preferences={}, # Empty preferences
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    claims = {
        "sub": sub,
        "email": email,
        "name": "New User"
    }

    # First login should succeed and set the sub
    authenticated_user = await get_current_user(claims=claims, db=db)

    # Verify sub was set
    await db.refresh(authenticated_user)
    assert authenticated_user.preferences.get("zitadel_sub") == sub

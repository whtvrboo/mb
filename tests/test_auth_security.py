
import pytest
from mitlist.modules.auth.models import User
from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_account_takeover_prevention(db):
    """
    Test that the vulnerability is fixed.
    If a user exists with a linked zitadel_sub, an attacker with a different sub
    but same email SHOULD NOT be able to take over the account.
    """
    # 1. Setup: Create a user with an existing link
    original_sub = "original-sub-123"
    attacker_sub = "attacker-sub-999"
    email = "victim@example.com"

    user = User(
        email=email,
        hashed_password="EXTERNAL_AUTH:original-sub-123",
        name="Victim User",
        is_active=True,
        preferences={"zitadel_sub": original_sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # 2. Simulate login with same email but DIFFERENT sub
    claims = {
        "sub": attacker_sub,
        "email": email,
        "name": "Attacker Name"
    }

    # 3. Call get_current_user and expect UnauthorizedError
    with pytest.raises(UnauthorizedError) as exc:
        await get_current_user(claims=claims, db=db)

    assert exc.value.code == "SUB_MISMATCH"

@pytest.mark.asyncio
async def test_valid_login(db):
    """Test that a valid login with matching sub still works."""
    sub = "valid-sub-123"
    email = "user@example.com"

    user = User(
        email=email,
        hashed_password="EXTERNAL_AUTH:valid-sub-123",
        name="Valid User",
        is_active=True,
        preferences={"zitadel_sub": sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    claims = {
        "sub": sub,
        "email": email,
        "name": "Valid User"
    }

    authenticated_user = await get_current_user(claims=claims, db=db)
    assert authenticated_user.id == user.id

@pytest.mark.asyncio
async def test_trust_on_first_use(db):
    """
    Test that a legacy user (without zitadel_sub linked)
    can be linked on first login (Trust On First Use).
    """
    email = "legacy@example.com"
    new_sub = "new-sub-456"

    # Create user without zitadel_sub in preferences
    user = User(
        email=email,
        hashed_password="LEGACY_PASSWORD",
        name="Legacy User",
        is_active=True,
        preferences={}, # Empty preferences
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    claims = {
        "sub": new_sub,
        "email": email,
        "name": "Legacy User"
    }

    # Should succeed and link the sub
    authenticated_user = await get_current_user(claims=claims, db=db)

    assert authenticated_user.id == user.id
    assert authenticated_user.preferences["zitadel_sub"] == new_sub

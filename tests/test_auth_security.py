import pytest

from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError
from mitlist.modules.auth.models import User


@pytest.mark.asyncio
async def test_account_takeover_prevention(db):
    """
    Verify that an attacker with a different 'sub' but same email
    is BLOCKED from taking over an existing account.
    """
    email = "victim@example.com"
    original_sub = "original-sub-123"
    attacker_sub = "attacker-sub-456"

    # 1. Create original user linked to original_sub
    user = User(
        email=email,
        hashed_password="hashed_pw",
        name="Victim",
        is_active=True,
        preferences={"zitadel_sub": original_sub},
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # 2. Simulate login with same email but different sub (attacker)
    claims = {"sub": attacker_sub, "email": email, "name": "Attacker"}

    # 3. Call get_current_user and expect UnauthorizedError
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims=claims, db=db)

    assert excinfo.value.code == "TOKEN_SUB_MISMATCH"


@pytest.mark.asyncio
async def test_legacy_user_migration(db):
    """
    Verify that a legacy user (no linked sub) gets linked on first login.
    """
    email = "legacy@example.com"
    new_sub = "new-sub-789"

    # 1. Create legacy user (no preferences or missing zitadel_sub)
    user = User(
        email=email, hashed_password="hashed_pw", name="Legacy User", is_active=True, preferences={}
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # 2. Simulate login
    claims = {"sub": new_sub, "email": email, "name": "Legacy User"}

    # 3. Call get_current_user
    logged_in_user = await get_current_user(claims=claims, db=db)

    # 4. Verify sub was linked
    assert logged_in_user.id == user.id
    assert logged_in_user.preferences["zitadel_sub"] == new_sub

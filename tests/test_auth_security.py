import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError
from mitlist.modules.auth.models import User


@pytest.mark.asyncio
async def test_account_takeover_prevention(db: AsyncSession):
    # Setup: Create a victim user
    victim_email = "victim@example.com"
    original_sub = "original-sub"
    victim = User(
        email=victim_email,
        hashed_password="EXTERNAL_AUTH:original-sub",
        name="Victim User",
        is_active=True,
        preferences={"zitadel_sub": original_sub},
    )
    db.add(victim)
    await db.flush()
    await db.refresh(victim)

    # Action: Try to authenticate with same email but DIFFERENT sub (attacker)
    attacker_sub = "attacker-sub"
    claims = {"sub": attacker_sub, "email": victim_email, "name": "Attacker User"}

    # Assert: Verify that it raises UnauthorizedError
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims=claims, db=db)

    assert excinfo.value.code == "IDENTITY_MISMATCH"


@pytest.mark.asyncio
async def test_valid_login(db: AsyncSession):
    # Setup: Create a user
    email = "valid@example.com"
    sub = "valid-sub"
    user = User(
        email=email,
        hashed_password="EXTERNAL_AUTH:valid-sub",
        name="Valid User",
        is_active=True,
        preferences={"zitadel_sub": sub},
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    claims = {"sub": sub, "email": email, "name": "Valid User"}

    # Should succeed
    result_user = await get_current_user(claims=claims, db=db)
    assert result_user.id == user.id


@pytest.mark.asyncio
async def test_first_login_linking(db: AsyncSession):
    # Setup: Create a user without zitadel_sub (e.g. manually created)
    email = "legacy@example.com"
    user = User(
        email=email,
        hashed_password="EXTERNAL_AUTH:legacy",
        name="Legacy User",
        is_active=True,
        preferences={},  # No zitadel_sub
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    sub = "new-sub"
    claims = {"sub": sub, "email": email, "name": "Legacy User"}

    # Should succeed and LINK the sub
    result_user = await get_current_user(claims=claims, db=db)
    assert result_user.id == user.id
    assert result_user.preferences["zitadel_sub"] == sub

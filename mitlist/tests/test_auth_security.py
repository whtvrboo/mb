import pytest
from datetime import datetime, timezone
from mitlist.modules.auth.models import User
from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError

@pytest.mark.asyncio
async def test_prevent_account_takeover_sub_mismatch(db_session):
    """
    Verify that login fails if the token subject does not match the linked Zitadel identity.
    """
    original_sub = "user-original-sub"
    attacker_sub = "attacker-sub"
    email = "victim@example.com"

    # Setup: User linked to original_sub
    user = User(
        email=email,
        hashed_password="hashed_secret",
        name="Victim User",
        is_active=True,
        preferences={"zitadel_sub": original_sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()

    # Attempt login with same email but different sub
    claims = {
        "sub": attacker_sub,
        "email": email,
        "name": "Attacker"
    }

    # Expect UnauthorizedError
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims, db_session)

    assert excinfo.value.code == "TOKEN_SUB_MISMATCH"

@pytest.mark.asyncio
async def test_allow_valid_login(db_session):
    """
    Verify that login succeeds if the token subject matches the linked identity.
    """
    sub = "valid-sub"
    email = "user@example.com"

    user = User(
        email=email,
        hashed_password="hashed_secret",
        name="Valid User",
        is_active=True,
        preferences={"zitadel_sub": sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()

    claims = {
        "sub": sub,
        "email": email,
        "name": "Valid User"
    }

    authenticated_user = await get_current_user(claims, db_session)
    assert authenticated_user.id == user.id
    assert authenticated_user.preferences["zitadel_sub"] == sub

@pytest.mark.asyncio
async def test_trust_on_first_use_linking(db_session):
    """
    Verify that if a user has no linked identity (legacy/invite/etc),
    the first login links the token subject.
    """
    email = "newuser@example.com"
    sub = "new-sub-123"

    # Setup: User exists but has no zitadel_sub in preferences
    user = User(
        email=email,
        hashed_password="hashed_secret",
        name="New User",
        is_active=True,
        preferences={}, # Empty preferences
        last_login_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()

    claims = {
        "sub": sub,
        "email": email,
        "name": "New User"
    }

    authenticated_user = await get_current_user(claims, db_session)

    # Verify sub was linked
    assert authenticated_user.id == user.id
    assert authenticated_user.preferences["zitadel_sub"] == sub

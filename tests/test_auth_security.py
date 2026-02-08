import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from mitlist.modules.auth.models import User
from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError

@pytest.mark.asyncio
async def test_account_takeover_vulnerability(db: AsyncSession):
    """
    VULNERABILITY REPRODUCTION:
    Demonstrate that an attacker can take over an account by changing their email
    in the IDP (Zitadel) to match a victim's email, if the application relies solely on email lookup.
    """
    # 1. Setup Victim User (simulating an existing user linked to Zitadel)
    victim_email = "victim@example.com"
    victim_sub = "victim-sub-123"

    victim = User(
        email=victim_email,
        hashed_password="EXTERNAL_AUTH:victim-sub-123",
        name="Victim User",
        is_active=True,
        preferences={"zitadel_sub": victim_sub},
    )
    db.add(victim)
    await db.flush()
    await db.refresh(victim)

    # 2. Attacker Claims (simulating a different user who managed to verify the victim's email in Zitadel)
    # or simply a misconfiguration where email is reused.
    attacker_sub = "attacker-sub-999"
    attacker_claims = {
        "sub": attacker_sub,
        "email": victim_email, # Attacker has verified this email in IDP
        "email_verified": True,
        "name": "Attacker"
    }

    # 3. Call get_current_user with Attacker's token claims
    # Expectation (FIXED): Should raise UnauthorizedError (IDENTITY_CONFLICT)
    with pytest.raises(UnauthorizedError) as exc:
        await get_current_user(claims=attacker_claims, db=db)

    assert exc.value.code == "IDENTITY_CONFLICT"
    assert "associated with another account" in exc.value.detail

@pytest.mark.asyncio
async def test_legacy_user_migration(db: AsyncSession):
    """
    Test that a legacy user (no zitadel_sub) is automatically linked
    to the IDP sub upon first login with matching email.
    """
    email = "legacy@example.com"
    sub = "legacy-sub-123"

    # 1. Create legacy user (no preferences or empty preferences)
    user = User(
        email=email,
        hashed_password="hashed",
        name="Legacy User",
        is_active=True,
        preferences={}, # No zitadel_sub
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # 2. Login with matching email
    claims = {
        "sub": sub,
        "email": email,
        "email_verified": True
    }

    # 3. Call get_current_user
    u = await get_current_user(claims=claims, db=db)

    # 4. Assert user is returned and LINKED
    assert u.id == user.id
    assert u.preferences["zitadel_sub"] == sub

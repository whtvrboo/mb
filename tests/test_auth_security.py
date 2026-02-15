
import pytest

from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError
from mitlist.modules.auth.models import User


@pytest.mark.asyncio
async def test_security_account_takeover_prevention(db):
    """
    Test that an attacker CANNOT takeover an account by providing a valid email but different sub.
    This ensures that the `zitadel_sub` claim is immutable once linked to a user.
    """
    # 1. Setup: Create a victim user with a linked subject
    victim_email = "victim@example.com"
    original_sub = "original-subject-123"
    attacker_sub = "attacker-subject-456"

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

    # 2. Simulate attacker logging in with same email but different sub
    attacker_claims = {
        "sub": attacker_sub,
        "email": victim_email,
        "name": "Attacker Name",
        "preferred_username": victim_email
    }

    # 3. Assert that the system rejects the attempt
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims=attacker_claims, db=db)

    assert "Identity provider subject mismatch" in str(excinfo.value.detail)

    # 4. Verify that the subject was NOT changed
    await db.refresh(victim)
    current_sub = victim.preferences.get("zitadel_sub")
    assert current_sub == original_sub

@pytest.mark.asyncio
async def test_security_trust_on_first_use(db):
    """
    Test that a user without a linked subject gets linked on first login (TOFU).
    """
    # 1. Setup: User exists but has no zitadel_sub in preferences
    user_email = "newuser@example.com"
    user_sub = "new-subject-789"

    user = User(
        email=user_email,
        hashed_password="EXTERNAL_AUTH:legacy",
        name="Legacy User",
        is_active=True,
        preferences={}, # No sub linked yet
    )
    db.add(user)
    await db.flush()

    # 2. Login with a token containing a sub
    claims = {
        "sub": user_sub,
        "email": user_email,
        "name": "Legacy User",
    }

    authenticated_user = await get_current_user(claims=claims, db=db)

    # 3. Verify successful login
    assert authenticated_user.id == user.id

    # 4. Verify subject was linked
    await db.refresh(authenticated_user)
    assert authenticated_user.preferences.get("zitadel_sub") == user_sub

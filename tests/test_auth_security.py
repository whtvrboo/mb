import pytest
from mitlist.api.deps import get_current_user
from mitlist.modules.auth.models import User
from mitlist.core.errors import UnauthorizedError
from sqlalchemy import select

@pytest.mark.asyncio
async def test_account_takeover_protection_subject_mismatch(db):
    """
    Test that an attacker cannot takeover an account by presenting a valid token
    with a matching email but different subject (sub) than the one already linked.
    """
    # 1. Create a user linked to a specific Zitadel subject
    original_sub = "original-sub-123"
    email = "target@example.com"

    user = User(
        email=email,
        name="Target User",
        hashed_password="hashed_pw",
        is_active=True,
        preferences={"zitadel_sub": original_sub}
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # 2. Simulate a login attempt with the same email but DIFFERENT subject
    # This could happen if:
    # - The IDP allows email recycling/changes and doesn't propagate sub changes safely
    # - The attacker compromised the IDP to issue a token for this email with their sub
    attacker_claims = {
        "sub": "attacker-sub-999",
        "email": email,
        "name": "Attacker"
    }

    # 3. Attempt to authenticate
    # This MUST fail to prevent account takeover.
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims=attacker_claims, db=db)

    assert "different identity subject" in str(excinfo.value.detail) or "Subject mismatch" in str(excinfo.value.detail) or "Account already linked" in str(excinfo.value.detail)

    # 4. Verify the user's subject was NOT updated
    await db.refresh(user)
    assert user.preferences["zitadel_sub"] == original_sub

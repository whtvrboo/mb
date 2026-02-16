import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from mitlist.modules.auth.models import User
from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError

@pytest.mark.asyncio
async def test_account_takeover_prevention(db: AsyncSession):
    """
    Test that an existing user linked to a specific Identity Provider subject (sub)
    cannot be accessed by a token with the same email but a different subject.
    This prevents Account Takeover via Weak Identity Linking (Trust On First Use only).
    """
    # Setup: Create a user linked to a specific sub
    victim_email = "victim@example.com"
    original_sub = "original-sub-123"
    attacker_sub = "attacker-sub-456"

    user = User(
        email=victim_email,
        hashed_password="EXTERNAL_AUTH:original-sub",
        name="Victim User",
        is_active=True,
        preferences={"zitadel_sub": original_sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Action: Try to authenticate with the same email but different sub (attacker)
    claims = {
        "sub": attacker_sub,
        "email": victim_email,
        "name": "Attacker User",
        "preferred_username": victim_email
    }

    # Expectation: Should raise UnauthorizedError due to sub mismatch
    # Currently (before fix), this will fail because get_current_user updates the sub instead of raising error.
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims=claims, db=db)

    assert excinfo.value.code == "IDENTITY_MISMATCH"

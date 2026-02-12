import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from mitlist.modules.auth.models import User
from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_account_takeover_vulnerability(db: AsyncSession):
    """
    Test that currently an attacker can log in as a victim if they have the same email,
    even if the sub (subject) is different.
    """
    # 1. Create a victim user
    victim_email = "victim@example.com"
    original_sub = "original-sub"

    victim = User(
        email=victim_email,
        hashed_password="EXTERNAL_AUTH:original-sub",
        name="Victim User",
        is_active=True,
        preferences={"zitadel_sub": original_sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(victim)
    await db.flush()
    await db.refresh(victim)

    # 2. Attacker token claims (same email, different sub)
    attacker_claims = {
        "sub": "attacker-sub",
        "email": victim_email,
        "name": "Attacker",
    }

    # 3. Call get_current_user
    # Expected behavior after fix: Login should be blocked due to sub mismatch
    try:
        await get_current_user(claims=attacker_claims, db=db)
        pytest.fail("UnauthorizedError not raised - account takeover still possible!")
    except UnauthorizedError as e:
        assert e.code == "SUB_MISMATCH"

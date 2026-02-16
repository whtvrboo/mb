import pytest
from datetime import datetime, timezone
from mitlist.modules.auth.models import User
from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_account_takeover_prevention(db: AsyncSession):
    """
    Test that an existing user linked to one ZITADEL sub CANNOT be taken over
    by a token with the same email but a different ZITADEL sub.
    """
    # 1. Setup: Create a user linked to 'original-sub'
    original_email = "victim@example.com"
    original_sub = "original-sub"

    user = User(
        email=original_email,
        hashed_password="EXTERNAL_AUTH:original-sub",
        name="Victim User",
        is_active=True,
        preferences={"zitadel_sub": original_sub},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Verify setup
    assert user.email == original_email
    assert user.preferences["zitadel_sub"] == original_sub

    # 2. Simulate Attack: Token with same email but DIFFERENT sub
    attacker_sub = "attacker-sub"
    fake_claims = {
        "sub": attacker_sub,
        "email": original_email,
        "name": "Attacker User",
        "preferred_username": original_email
    }

    # 3. Execution: Call get_current_user
    # This should raise UnauthorizedError to prevent account takeover
    # Note: Initially this test will FAIL (it will not raise) because the vulnerability exists.
    with pytest.raises(UnauthorizedError) as exc:
        await get_current_user(claims=fake_claims, db=db)

    assert "Token subject mismatch" in exc.value.detail

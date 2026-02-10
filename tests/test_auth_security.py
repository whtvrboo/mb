from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError
from mitlist.modules.auth.models import User


@pytest.mark.asyncio
async def test_account_takeover_prevention(db: AsyncSession):
    # Setup existing user linked to 'original-sub'
    user = User(
        email="target@example.com",
        hashed_password="EXTERNAL_AUTH:original-sub",
        name="Target User",
        is_active=True,
        preferences={"zitadel_sub": "original-sub"},
        last_login_at=datetime.now(UTC),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Attacker tries to login with same email but different sub
    attacker_claims = {
        "sub": "attacker-sub",
        "email": "target@example.com",
        "email_verified": True,
        "name": "Attacker",
    }

    # Should raise UnauthorizedError, NOT update the user
    with pytest.raises(UnauthorizedError) as exc:
        await get_current_user(claims=attacker_claims, db=db)

    assert exc.value.code == "TOKEN_SUB_MISMATCH"

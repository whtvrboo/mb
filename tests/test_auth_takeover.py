import pytest

from mitlist.api.deps import get_current_user
from mitlist.core.errors import UnauthorizedError
from mitlist.modules.auth.models import User


@pytest.mark.asyncio
async def test_account_takeover_via_sub_mismatch(db):
    # 1. Setup victim user
    victim_email = "victim@example.com"
    original_sub = "original-sub"

    victim = User(
        email=victim_email,
        hashed_password="hashed",
        name="Victim",
        is_active=True,
        preferences={"zitadel_sub": original_sub},
    )
    db.add(victim)
    await db.flush()
    await db.refresh(victim)

    # 2. Attacker claims with same email but different sub
    attacker_sub = "attacker-sub"
    claims = {"sub": attacker_sub, "email": victim_email, "name": "Attacker"}

    # 3. Call get_current_user
    # This should RAISE UnauthorizedError because the sub doesn't match the bound identity
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims=claims, db=db)

    assert "Token subject mismatch" in str(excinfo.value.detail)

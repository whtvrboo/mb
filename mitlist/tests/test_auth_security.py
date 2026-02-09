import pytest
from mitlist.api.deps import get_current_user
from mitlist.modules.auth.models import User
from mitlist.core.errors import UnauthorizedError

@pytest.mark.asyncio
async def test_account_takeover_prevention(db_session):
    # 1. Create a user with an existing linked sub
    original_sub = "original-sub-123"
    email = "victim@example.com"
    user = User(
        email=email,
        name="Victim",
        hashed_password="hashed",
        is_active=True,
        preferences={"zitadel_sub": original_sub}
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    # 2. Simulate a login attempt with the SAME email but DIFFERENT sub
    attacker_sub = "attacker-sub-999"
    claims = {
        "sub": attacker_sub,
        "email": email,
        "name": "Attacker"
    }

    # 3. Assert that get_current_user raises UnauthorizedError
    # Currently (before fix), this will NOT raise, so the test will fail.
    with pytest.raises(UnauthorizedError) as excinfo:
        await get_current_user(claims=claims, db=db_session)

    # 4. Verify that logging in with the CORRECT sub works
    correct_claims = {
        "sub": original_sub,
        "email": email,
        "name": "Victim"
    }

    # Should not raise
    user = await get_current_user(claims=correct_claims, db=db_session)
    assert user.email == email

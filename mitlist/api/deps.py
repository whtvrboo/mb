"""FastAPI dependencies for database and authentication."""

from datetime import datetime
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.db.engine import get_db as get_db_session
from mitlist.core.auth.zitadel import ZitadelTokenError, require_active_token, verify_access_token
from mitlist.core.config import settings
from mitlist.core.errors import UnauthorizedError
from mitlist.core.request_context import set_user_id
from mitlist.modules.auth.models import User

# Re-export for convenience
__all__ = [
    "get_db",
    "get_bearer_token",
    "get_current_principal",
    "get_current_user",
    "require_introspection_user",
]


def get_db() -> AsyncSession:
    """
    Dependency that yields an async database session.

    This is a re-export from mitlist.db.engine for API convenience.
    """
    return get_db_session()


security = HTTPBearer(auto_error=False)


async def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """Extract Bearer token from Authorization header."""
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError(code="MISSING_BEARER_TOKEN", detail="Missing Bearer token")
    return credentials.credentials


async def get_current_principal(token: str = Depends(get_bearer_token)) -> dict[str, Any]:
    """Validate the token (JWKS) and return its claims."""
    try:
        verified = await verify_access_token(token)
        return verified.claims
    except ZitadelTokenError as e:
        raise UnauthorizedError(code="INVALID_TOKEN", detail=str(e)) from e


async def get_current_user(
    claims: dict[str, Any] = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Map Zitadel subject to a local User row (create-on-first-seen if enabled)."""
    sub = claims.get("sub")
    email = claims.get("email") or claims.get("preferred_username")
    if not sub:
        raise UnauthorizedError(code="TOKEN_MISSING_SUB", detail="Token missing subject (sub)")

    if not email:
        # fallback: stable synthetic email to satisfy local uniqueness/NOT NULL constraint
        email = f"{sub}@zitadel.local"

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        if not settings.ZITADEL_USER_AUTOCREATE:
            raise UnauthorizedError(code="USER_NOT_PROVISIONED", detail="User not provisioned")

        user = User(
            email=email,
            hashed_password=f"EXTERNAL_AUTH:{sub}",
            name=claims.get("name") or claims.get("given_name") or email,
            avatar_url=claims.get("picture"),
            is_active=True,
            preferences={"zitadel_sub": sub},
            last_login_at=datetime.utcnow(),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        # update last_login and ensure we remember sub
        user.last_login_at = datetime.utcnow()
        prefs = user.preferences or {}
        if prefs.get("zitadel_sub") != sub:
            prefs["zitadel_sub"] = sub
            user.preferences = prefs
        await db.flush()
        await db.refresh(user)

    set_user_id(user.id)
    return user


async def require_introspection_user(
    token: str = Depends(get_bearer_token),
    user: User = Depends(get_current_user),
) -> User:
    """Critical-path dependency: require token to be active via introspection."""
    try:
        await require_active_token(token)
        return user
    except ZitadelTokenError as e:
        raise UnauthorizedError(code="TOKEN_NOT_ACTIVE", detail=str(e)) from e

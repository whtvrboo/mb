"""FastAPI dependencies for database and authentication."""

from datetime import UTC, datetime
from typing import Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.core.auth.zitadel import ZitadelTokenError, require_active_token, verify_access_token
from mitlist.core.config import settings
from mitlist.core.errors import ForbiddenError, UnauthorizedError, ValidationError
from mitlist.core.request_context import set_group_id, set_user_id
from mitlist.db.engine import get_db as get_db_session
from mitlist.modules.auth.models import User, UserGroup

# Re-export for convenience
__all__ = [
    "get_db",
    "get_bearer_token",
    "get_current_principal",
    "get_current_user",
    "get_current_group_id",
    "require_group_admin",
    "require_introspection_user",
]


async def get_db() -> AsyncSession:
    """
    Dependency that yields an async database session.

    This is a re-export wrapper around mitlist.db.engine.get_db.
    """
    async for session in get_db_session():
        yield session


security = HTTPBearer(auto_error=False)


async def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """Extract Bearer token from Authorization header."""
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError(code="MISSING_BEARER_TOKEN", detail="Missing Bearer token")
    return credentials.credentials


def _parse_dev_token(token: str) -> dict[str, Any] | None:
    """If DEV_TEST_USER_ENABLED and token is dev:<email> or dev:<email>:<name>, return fake claims."""
    if not settings.DEV_TEST_USER_ENABLED or not token.startswith("dev:"):
        return None
    parts = token[4:].split(":", 1)  # after "dev:"
    email = (parts[0] or "test@test.local").strip()
    name = (parts[1] or email).strip() if len(parts) > 1 else email
    sub = f"dev-{email.replace('@', '-at-')}"
    return {"sub": sub, "email": email, "name": name, "preferred_username": email}


async def get_current_principal(token: str = Depends(get_bearer_token)) -> dict[str, Any]:
    """Validate the token (JWKS or dev token) and return its claims."""
    dev_claims = _parse_dev_token(token)
    if dev_claims is not None:
        return dev_claims
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
            last_login_at=datetime.now(UTC),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        # update last_login and ensure we remember sub
        user.last_login_at = datetime.now(UTC)
        prefs = user.preferences or {}

        # Security: Enforce immutability of zitadel_sub to prevent account takeover
        existing_sub = prefs.get("zitadel_sub")
        if existing_sub and existing_sub != sub:
            raise UnauthorizedError(
                code="TOKEN_SUB_MISMATCH",
                detail="Identity provider subject mismatch",
            )

        if existing_sub != sub:
            # First time seeing sub for this user (Trust On First Use)
            prefs["zitadel_sub"] = sub
            user.preferences = dict(prefs)

        await db.flush()
        await db.refresh(user)

    set_user_id(user.id)
    return user


async def require_introspection_user(
    token: str = Depends(get_bearer_token),
    user: User = Depends(get_current_user),
) -> User:
    """Critical-path dependency: require token to be active via introspection (or dev token when enabled)."""
    if settings.DEV_TEST_USER_ENABLED and token.startswith("dev:"):
        return user
    try:
        await require_active_token(token)
        return user
    except ZitadelTokenError as e:
        raise UnauthorizedError(code="TOKEN_NOT_ACTIVE", detail=str(e)) from e


async def get_current_group_id(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> int:
    """
    Resolve current group scope for request.

    Priority:
    1) Header `X-Group-ID`
    2) Query parameter `group_id` (backward compat)
    """
    raw = request.headers.get("X-Group-ID") or request.query_params.get("group_id")
    if not raw:
        raise ValidationError(
            code="MISSING_GROUP_ID",
            detail="Missing group scope. Provide X-Group-ID header (preferred) or group_id query param.",
        )
    try:
        group_id = int(raw)
    except ValueError as e:
        raise ValidationError(code="INVALID_GROUP_ID", detail="group_id must be an integer") from e

    result = await db.execute(
        select(UserGroup).where(UserGroup.group_id == group_id, UserGroup.user_id == user.id)
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise ForbiddenError(code="NOT_A_MEMBER", detail="User is not a member of this group")

    set_group_id(group_id)
    return group_id


async def require_group_admin(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> int:
    """Require ADMIN role in the current group."""
    result = await db.execute(
        select(UserGroup).where(UserGroup.group_id == group_id, UserGroup.user_id == user.id)
    )
    membership = result.scalar_one_or_none()
    if not membership or membership.role != "ADMIN":
        raise ForbiddenError(code="ADMIN_REQUIRED", detail="Admin role required for this action")
    return group_id

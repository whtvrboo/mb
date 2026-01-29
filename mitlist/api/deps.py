"""FastAPI dependencies for database and common operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.db.engine import get_db as get_db_session

# Re-export for convenience
__all__ = ["get_db"]


def get_db() -> AsyncSession:
    """
    Dependency that yields an async database session.

    This is a re-export from mitlist.db.engine for API convenience.
    """
    return get_db_session()

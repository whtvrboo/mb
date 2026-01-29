"""Health check endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    """
    Liveness probe - returns 200 OK instantly.

    Kubernetes will restart the pod if this fails.
    """
    return {"status": "alive", "service": settings.PROJECT_NAME}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Readiness probe - checks database connectivity.

    Load balancer removes from pool if this fails.
    """
    try:
        # Lightweight DB query to verify connectivity
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {
            "status": "not_ready",
            "database": "disconnected",
            "error": str(e),
        }

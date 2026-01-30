"""System & ops routes: /system/info."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.config import settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/info")
async def get_system_info(db: AsyncSession = Depends(get_db)):
    """Version and environment info."""
    return {
        "app_name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "server_time": datetime.utcnow().isoformat(),
        "api_version": "v1",
    }

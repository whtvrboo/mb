"""System & ops routes: /system/info."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError

router = APIRouter(prefix="/system", tags=["system"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/info")
async def get_system_info(db: AsyncSession = Depends(get_db)):
    """Version and environment info."""
    _stub("GET /system/info is not yet implemented")

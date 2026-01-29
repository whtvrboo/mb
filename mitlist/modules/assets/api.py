"""Assets & Maintenance module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.assets import schemas

router = APIRouter(prefix="/assets", tags=["assets"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("", response_model=ListType[schemas.HomeAssetResponse])
async def get_assets(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /assets is not yet implemented")


@router.post("", response_model=schemas.HomeAssetResponse, status_code=status.HTTP_201_CREATED)
async def post_assets(data: schemas.HomeAssetCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /assets is not yet implemented")


@router.get("/{asset_id}/maintenance", response_model=ListType[schemas.MaintenanceTaskResponse])
async def get_asset_maintenance(asset_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /assets/{id}/maintenance is not yet implemented")


@router.post("/{asset_id}/maintenance", response_model=schemas.MaintenanceLogResponse, status_code=status.HTTP_201_CREATED)
async def post_asset_maintenance(asset_id: int, data: schemas.MaintenanceLogCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /assets/{id}/maintenance is not yet implemented")

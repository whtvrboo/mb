"""Flora (Plants) module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.plants import schemas

router = APIRouter(prefix="/plants", tags=["plants"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/species", response_model=ListType[schemas.PlantSpeciesResponse])
async def get_plant_species(db: AsyncSession = Depends(get_db)):
    _stub("GET /plant-species is not yet implemented")


@router.get("", response_model=ListType[schemas.PlantResponse])
async def get_plants(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /plants is not yet implemented")


@router.post("", response_model=schemas.PlantResponse, status_code=status.HTTP_201_CREATED)
async def post_plants(data: schemas.PlantCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /plants is not yet implemented")


@router.get("/{plant_id}", response_model=schemas.PlantWithSpeciesResponse)
async def get_plant(plant_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /plants/{id} is not yet implemented")


@router.patch("/{plant_id}", response_model=schemas.PlantResponse)
async def patch_plant(plant_id: int, data: schemas.PlantUpdate, db: AsyncSession = Depends(get_db)):
    _stub("PATCH /plants/{id} is not yet implemented")


@router.get("/{plant_id}/logs", response_model=ListType[schemas.PlantLogResponse])
async def get_plant_logs(plant_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /plants/{id}/logs is not yet implemented")


@router.post("/{plant_id}/logs", response_model=schemas.PlantLogResponse, status_code=status.HTTP_201_CREATED)
async def post_plant_log(plant_id: int, data: schemas.PlantLogCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /plants/{id}/logs is not yet implemented")

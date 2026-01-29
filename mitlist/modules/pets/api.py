"""Fauna (Pets) module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.pets import schemas

router = APIRouter(prefix="/pets", tags=["pets"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("", response_model=ListType[schemas.PetResponse])
async def get_pets(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /pets is not yet implemented")


@router.post("", response_model=schemas.PetResponse, status_code=status.HTTP_201_CREATED)
async def post_pets(data: schemas.PetCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /pets is not yet implemented")


@router.patch("/{pet_id}", response_model=schemas.PetResponse)
async def patch_pet(pet_id: int, data: schemas.PetUpdate, db: AsyncSession = Depends(get_db)):
    _stub("PATCH /pets/{id} is not yet implemented")


@router.get("/{pet_id}/medical", response_model=ListType[schemas.PetMedicalRecordResponse])
async def get_pet_medical(pet_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /pets/{id}/medical is not yet implemented")


@router.post("/{pet_id}/medical", response_model=schemas.PetMedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def post_pet_medical(pet_id: int, data: schemas.PetMedicalRecordCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /pets/{id}/medical is not yet implemented")


@router.get("/{pet_id}/logs", response_model=ListType[schemas.PetLogResponse])
async def get_pet_logs(pet_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /pets/{id}/logs is not yet implemented")


@router.post("/{pet_id}/logs", response_model=schemas.PetLogResponse, status_code=status.HTTP_201_CREATED)
async def post_pet_log(pet_id: int, data: schemas.PetLogCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /pets/{id}/logs is not yet implemented")

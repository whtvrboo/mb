"""Flora (Plants) module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db, get_current_group_id, get_current_user
from mitlist.core.errors import NotFoundError, ValidationError
from mitlist.modules.plants import interface, schemas

router = APIRouter(prefix="/plants", tags=["plants"])


# ---------- Schedules (Top Level) ----------
@router.patch("/schedules/{schedule_id}/done", response_model=schemas.PlantScheduleResponse)
async def mark_schedule_completed(
    schedule_id: int,
    data: schemas.PlantScheduleMarkDoneRequest,
    group_id: int = Depends(get_current_group_id),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark schedule as done."""
    sched = await interface.get_schedule_by_id(db, schedule_id)
    if not sched or sched.plant.group_id != group_id:
        raise NotFoundError(code="SCHEDULE_NOT_FOUND", detail=f"Schedule {schedule_id} not found")
    updated = await interface.mark_schedule_done(
        db,
        schedule_id=schedule_id,
        user_id=user.id,
        notes=data.notes,
        quantity_value=data.quantity_value,
        quantity_unit=data.quantity_unit,
    )
    return schemas.PlantScheduleResponse.model_validate(updated)


# ---------- Species ----------
@router.get("/species", response_model=ListType[schemas.PlantSpeciesResponse])
async def get_plant_species(db: AsyncSession = Depends(get_db)):
    """List all plant species."""
    species = await interface.list_species(db)
    return [schemas.PlantSpeciesResponse.model_validate(s) for s in species]


# ---------- Plants ----------
@router.get("", response_model=ListType[schemas.PlantResponse])
async def get_plants(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """List plants in the group."""
    plants = await interface.list_plants(db, group_id)
    return [schemas.PlantResponse.model_validate(p) for p in plants]


@router.post("", response_model=schemas.PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    data: schemas.PlantCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new plant."""
    if data.group_id != group_id:
        raise ValidationError(code="GROUP_MISMATCH", detail="group_id mismatch")

    plant = await interface.create_plant(
        db,
        group_id=group_id,
        species_id=data.species_id,
        nickname=data.nickname,
        location_id=data.location_id,
        acquired_at=data.acquired_at,
        acquired_from=data.acquired_from,
        pot_size_cm=data.pot_size_cm,
        photo_url=data.photo_url,
        notes=data.notes,
        parent_plant_id=data.parent_plant_id,
    )
    return schemas.PlantResponse.model_validate(plant)


@router.get("/{plant_id}", response_model=schemas.PlantWithSpeciesResponse)
async def get_plant(
    plant_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get plant details."""
    plant = await interface.get_plant_by_id(db, plant_id)
    if not plant or plant.group_id != group_id:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")
    return schemas.PlantWithSpeciesResponse.model_validate(plant)


@router.patch("/{plant_id}", response_model=schemas.PlantResponse)
async def update_plant(
    plant_id: int,
    data: schemas.PlantUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Update plant details."""
    plant = await interface.get_plant_by_id(db, plant_id)
    if not plant or plant.group_id != group_id:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    updated = await interface.update_plant(
        db,
        plant_id=plant_id,
        location_id=data.location_id,
        nickname=data.nickname,
        pot_size_cm=data.pot_size_cm,
        photo_url=data.photo_url,
        notes=data.notes,
    )
    return schemas.PlantResponse.model_validate(updated)


@router.post("/{plant_id}/mark-dead", response_model=schemas.PlantResponse)
async def mark_plant_as_dead(
    plant_id: int,
    data: schemas.PlantMarkDeadRequest,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Mark plant as dead."""
    plant = await interface.get_plant_by_id(db, plant_id)
    if not plant or plant.group_id != group_id:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    updated = await interface.mark_plant_dead(db, plant_id, data.death_reason)
    return schemas.PlantResponse.model_validate(updated)


# ---------- Logs ----------
@router.get("/{plant_id}/logs", response_model=ListType[schemas.PlantLogResponse])
async def get_plant_logs(
    plant_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get care logs."""
    plant = await interface.get_plant_by_id(db, plant_id)
    if not plant or plant.group_id != group_id:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    logs = await interface.list_plant_logs(db, plant_id)
    return [schemas.PlantLogResponse.model_validate(l) for l in logs]


@router.post(
    "/{plant_id}/logs", response_model=schemas.PlantLogResponse, status_code=status.HTTP_201_CREATED
)
async def post_plant_log(
    plant_id: int,
    data: schemas.PlantLogCreate,
    group_id: int = Depends(get_current_group_id),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log a care action."""
    plant = await interface.get_plant_by_id(db, plant_id)
    if not plant or plant.group_id != group_id:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    log = await interface.create_plant_log(
        db,
        plant_id=plant_id,
        user_id=user.id,
        action=data.action,
        occurred_at=data.occurred_at,
        quantity_value=data.quantity_value,
        quantity_unit=data.quantity_unit,
        notes=data.notes,
        photo_url=data.photo_url,
    )
    return schemas.PlantLogResponse.model_validate(log)


# ---------- Schedules ----------
@router.get("/{plant_id}/schedules", response_model=ListType[schemas.PlantScheduleResponse])
async def get_plant_schedules(
    plant_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get plant schedules."""
    plant = await interface.get_plant_by_id(db, plant_id)
    if not plant or plant.group_id != group_id:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    schedules = await interface.list_plant_schedules(db, plant_id)
    return [schemas.PlantScheduleResponse.model_validate(s) for s in schedules]


@router.post(
    "/{plant_id}/schedules",
    response_model=schemas.PlantScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_plant_schedule(
    plant_id: int,
    data: schemas.PlantScheduleCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new schedule."""
    plant = await interface.get_plant_by_id(db, plant_id)
    if not plant or plant.group_id != group_id:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    sched = await interface.create_schedule(
        db,
        plant_id=plant_id,
        action_type=data.action_type,
        frequency_days=data.frequency_days,
        next_due_date=data.next_due_date,
        assigned_to_id=data.assigned_to_id,
    )
    return schemas.PlantScheduleResponse.model_validate(sched)

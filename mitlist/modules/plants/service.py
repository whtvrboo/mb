"""Plants module service layer. PRIVATE - other modules import from interface.py."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError
from mitlist.modules.plants.models import (
    Plant,
    PlantLog,
    PlantSchedule,
    PlantSpecies,
)


# ---------- Species ----------
async def list_species(db: AsyncSession) -> list[PlantSpecies]:
    """List all plant species."""
    result = await db.execute(select(PlantSpecies).order_by(PlantSpecies.scientific_name))
    return list(result.scalars().all())


async def get_species_by_id(db: AsyncSession, species_id: int) -> PlantSpecies | None:
    """Get species by ID."""
    result = await db.execute(select(PlantSpecies).where(PlantSpecies.id == species_id))
    return result.scalar_one_or_none()


async def create_species(
    db: AsyncSession,
    scientific_name: str,
    toxicity: str,
    light_needs: str,
    common_name: str | None = None,
    water_interval_summer: int | None = None,
    water_interval_winter: int | None = None,
    humidity_preference: str | None = None,
    fertilize_frequency_weeks: int | None = None,
    growth_rate: str | None = None,
    mature_height_cm: int | None = None,
    propagation_method: str | None = None,
    care_difficulty: str | None = None,
) -> PlantSpecies:
    """Create a new species."""
    species = PlantSpecies(
        scientific_name=scientific_name,
        common_name=common_name,
        toxicity=toxicity,
        light_needs=light_needs,
        water_interval_summer=water_interval_summer,
        water_interval_winter=water_interval_winter,
        humidity_preference=humidity_preference,
        fertilize_frequency_weeks=fertilize_frequency_weeks,
        growth_rate=growth_rate,
        mature_height_cm=mature_height_cm,
        propagation_method=propagation_method,
        care_difficulty=care_difficulty,
    )
    db.add(species)
    await db.flush()
    await db.refresh(species)
    return species


# ---------- Plants ----------
async def list_plants(db: AsyncSession, group_id: int) -> list[Plant]:
    """List plants in a group."""
    result = await db.execute(
        select(Plant)
        .where(Plant.group_id == group_id)
        .options(selectinload(Plant.species))
        .order_by(Plant.id)
    )
    return list(result.scalars().all())


async def get_plant_by_id(db: AsyncSession, plant_id: int) -> Plant | None:
    """Get plant by ID."""
    result = await db.execute(
        select(Plant).where(Plant.id == plant_id).options(selectinload(Plant.species))
    )
    return result.scalar_one_or_none()


async def create_plant(
    db: AsyncSession,
    group_id: int,
    species_id: int,
    nickname: str | None = None,
    location_id: int | None = None,
    acquired_at: datetime | None = None,
    acquired_from: str | None = None,
    pot_size_cm: int | None = None,
    photo_url: str | None = None,
    notes: str | None = None,
    parent_plant_id: int | None = None,
) -> Plant:
    """Create a new plant."""
    species = await get_species_by_id(db, species_id)
    if not species:
        raise NotFoundError(code="SPECIES_NOT_FOUND", detail=f"Species {species_id} not found")

    plant = Plant(
        group_id=group_id,
        species_id=species_id,
        nickname=nickname,
        location_id=location_id,
        acquired_at=acquired_at or datetime.now(UTC),
        acquired_from=acquired_from,
        pot_size_cm=pot_size_cm,
        photo_url=photo_url,
        notes=notes,
        parent_plant_id=parent_plant_id,
        is_alive=True,
    )
    db.add(plant)
    await db.flush()
    await db.refresh(plant)
    # eager load species for response
    await db.refresh(plant, ["species"])
    return plant


async def update_plant(
    db: AsyncSession,
    plant_id: int,
    location_id: int | None = None,
    nickname: str | None = None,
    pot_size_cm: int | None = None,
    photo_url: str | None = None,
    notes: str | None = None,
) -> Plant:
    """Update plant details."""
    plant = await get_plant_by_id(db, plant_id)
    if not plant:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    if location_id is not None:
        plant.location_id = location_id
    if nickname is not None:
        plant.nickname = nickname
    if pot_size_cm is not None:
        plant.pot_size_cm = pot_size_cm
    if photo_url is not None:
        plant.photo_url = photo_url
    if notes is not None:
        plant.notes = notes

    await db.flush()
    await db.refresh(plant)
    return plant


async def mark_plant_dead(
    db: AsyncSession,
    plant_id: int,
    death_reason: str | None = None,
) -> Plant:
    """Mark plant as dead."""
    plant = await get_plant_by_id(db, plant_id)
    if not plant:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    plant.is_alive = False
    plant.died_at = datetime.now(UTC)
    plant.death_reason = death_reason

    await db.flush()
    await db.refresh(plant)
    return plant


# ---------- Care Logs ----------
async def list_plant_logs(db: AsyncSession, plant_id: int, limit: int = 50) -> list[PlantLog]:
    """List care logs for a plant."""
    result = await db.execute(
        select(PlantLog)
        .where(PlantLog.plant_id == plant_id)
        .order_by(PlantLog.occurred_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_plant_log(
    db: AsyncSession,
    plant_id: int,
    user_id: int,
    action: str,
    occurred_at: datetime,
    quantity_value: float | None = None,
    quantity_unit: str | None = None,
    notes: str | None = None,
    photo_url: str | None = None,
) -> PlantLog:
    """Log a care action."""
    # Verify plant exists
    plant = await get_plant_by_id(db, plant_id)
    if not plant:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    log = PlantLog(
        plant_id=plant_id,
        user_id=user_id,
        action=action,
        occurred_at=occurred_at,
        quantity_value=quantity_value,
        quantity_unit=quantity_unit,
        notes=notes,
        photo_url=photo_url,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)

    # Update active schedules for this action_type
    schedules = await list_plant_schedules(db, plant_id)
    for sched in schedules:
        if sched.action_type == action:
            # Update next due date to occurred_at + frequency
            sched.next_due_date = occurred_at + timedelta(days=sched.frequency_days)
            await db.flush()

    return log


# ---------- Schedules ----------
async def get_schedule_by_id(db: AsyncSession, schedule_id: int) -> PlantSchedule | None:
    """Get plant schedule by ID with plant loaded (for group ownership check)."""
    result = await db.execute(
        select(PlantSchedule)
        .where(PlantSchedule.id == schedule_id)
        .options(selectinload(PlantSchedule.plant))
    )
    return result.scalar_one_or_none()


async def list_plant_schedules(db: AsyncSession, plant_id: int) -> list[PlantSchedule]:
    """List schedules for a plant."""
    result = await db.execute(select(PlantSchedule).where(PlantSchedule.plant_id == plant_id))
    return list(result.scalars().all())


async def create_schedule(
    db: AsyncSession,
    plant_id: int,
    action_type: str,
    frequency_days: int,
    next_due_date: datetime,
    assigned_to_id: int | None = None,
) -> PlantSchedule:
    """Create a care schedule."""
    plant = await get_plant_by_id(db, plant_id)
    if not plant:
        raise NotFoundError(code="PLANT_NOT_FOUND", detail=f"Plant {plant_id} not found")

    sched = PlantSchedule(
        plant_id=plant_id,
        action_type=action_type,
        frequency_days=frequency_days,
        next_due_date=next_due_date,
        assigned_to_id=assigned_to_id,
    )
    db.add(sched)
    await db.flush()
    await db.refresh(sched)
    return sched


async def mark_schedule_done(
    db: AsyncSession,
    schedule_id: int,
    user_id: int,
    notes: str | None = None,
    quantity_value: float | None = None,
    quantity_unit: str | None = None,
) -> PlantSchedule:
    """Mark a schedule as done (creates log and advances date)."""
    result = await db.execute(select(PlantSchedule).where(PlantSchedule.id == schedule_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise NotFoundError(code="SCHEDULE_NOT_FOUND", detail=f"Schedule {schedule_id} not found")

    # Create log
    now = datetime.now(UTC)
    await create_plant_log(
        db,
        plant_id=sched.plant_id,
        user_id=user_id,
        action=sched.action_type,
        occurred_at=now,
        notes=notes,
        quantity_value=quantity_value,
        quantity_unit=quantity_unit,
    )
    # create_plant_log already advances the schedule date via automatic hook
    await db.refresh(sched)
    return sched


async def get_overdue_schedules(db: AsyncSession, group_id: int) -> list[PlantSchedule]:
    """Get overdue schedules for a group."""
    now = datetime.now(UTC)
    result = await db.execute(
        select(PlantSchedule)
        .join(Plant)
        .where(
            and_(
                Plant.group_id == group_id,
                Plant.is_alive.is_(True),
                PlantSchedule.next_due_date < now,
            )
        )
        .options(selectinload(PlantSchedule.plant).selectinload(Plant.species))
        .order_by(PlantSchedule.next_due_date)
    )
    return list(result.scalars().all())

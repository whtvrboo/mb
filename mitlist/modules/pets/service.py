"""Pets module service layer. PRIVATE - other modules import from interface.py."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError
from mitlist.modules.pets.models import (
    Pet,
    PetLog,
    PetMedicalRecord,
    PetSchedule,
)


# ---------- Pets ----------
async def list_pets(db: AsyncSession, group_id: int) -> list[Pet]:
    """List pets in a group."""
    result = await db.execute(select(Pet).where(Pet.group_id == group_id))
    return list(result.scalars().all())


async def get_pet_by_id(db: AsyncSession, pet_id: int) -> Pet | None:
    """Get pet by ID."""
    result = await db.execute(
        select(Pet).where(Pet.id == pet_id)
        # .options(selectinload(Pet.medical_records)) # Maybe too heavy?
    )
    return result.scalar_one_or_none()


async def create_pet(
    db: AsyncSession,
    group_id: int,
    name: str,
    species: str,
    breed: str | None = None,
    sex: str | None = None,
    date_of_birth: datetime | None = None,
    adoption_date: datetime | None = None,
    chip_id: str | None = None,
    weight_kg: float | None = None,
    color_markings: str | None = None,
    photo_url: str | None = None,
    vet_contact_id: int | None = None,
    insurance_policy_number: str | None = None,
    insurance_provider: str | None = None,
    diet_instructions: str | None = None,
    medication_schedule: dict[str, Any] | None = None,
    special_needs: str | None = None,
) -> Pet:
    """Create a new pet."""
    pet = Pet(
        group_id=group_id,
        name=name,
        species=species,
        breed=breed,
        sex=sex,
        date_of_birth=date_of_birth,
        adoption_date=adoption_date,
        chip_id=chip_id,
        weight_kg=weight_kg,
        color_markings=color_markings,
        photo_url=photo_url,
        vet_contact_id=vet_contact_id,
        insurance_policy_number=insurance_policy_number,
        insurance_provider=insurance_provider,
        diet_instructions=diet_instructions,
        medication_schedule=medication_schedule,
        special_needs=special_needs,
        is_alive=True,
    )
    db.add(pet)
    await db.flush()
    await db.refresh(pet)
    return pet


async def update_pet(
    db: AsyncSession,
    pet_id: int,
    name: str | None = None,
    breed: str | None = None,
    sex: str | None = None,
    date_of_birth: datetime | None = None,
    chip_id: str | None = None,
    weight_kg: float | None = None,
    color_markings: str | None = None,
    photo_url: str | None = None,
    vet_contact_id: int | None = None,
    insurance_policy_number: str | None = None,
    insurance_provider: str | None = None,
    diet_instructions: str | None = None,
    medication_schedule: dict[str, Any] | None = None,
    special_needs: str | None = None,
) -> Pet:
    """Update pet details."""
    pet = await get_pet_by_id(db, pet_id)
    if not pet:
        raise NotFoundError(code="PET_NOT_FOUND", detail=f"Pet {pet_id} not found")

    if name is not None:
        pet.name = name
    if breed is not None:
        pet.breed = breed
    if sex is not None:
        pet.sex = sex
    if date_of_birth is not None:
        pet.date_of_birth = date_of_birth
    if chip_id is not None:
        pet.chip_id = chip_id
    if weight_kg is not None:
        pet.weight_kg = weight_kg
    if color_markings is not None:
        pet.color_markings = color_markings
    if photo_url is not None:
        pet.photo_url = photo_url
    if vet_contact_id is not None:
        pet.vet_contact_id = vet_contact_id
    if insurance_policy_number is not None:
        pet.insurance_policy_number = insurance_policy_number
    if insurance_provider is not None:
        pet.insurance_provider = insurance_provider
    if diet_instructions is not None:
        pet.diet_instructions = diet_instructions
    if medication_schedule is not None:
        pet.medication_schedule = medication_schedule
    if special_needs is not None:
        pet.special_needs = special_needs

    await db.flush()
    await db.refresh(pet)
    return pet


async def mark_pet_deceased(
    db: AsyncSession,
    pet_id: int,
    died_at: datetime,
) -> Pet:
    """Mark a pet as deceased."""
    pet = await get_pet_by_id(db, pet_id)
    if not pet:
        raise NotFoundError(code="PET_NOT_FOUND", detail=f"Pet {pet_id} not found")

    pet.is_alive = False
    pet.died_at = died_at

    await db.flush()
    await db.refresh(pet)
    return pet


# ---------- Medical Records ----------
async def list_medical_records(db: AsyncSession, pet_id: int) -> list[PetMedicalRecord]:
    """List medical records for a pet."""
    result = await db.execute(
        select(PetMedicalRecord)
        .where(PetMedicalRecord.pet_id == pet_id)
        .order_by(PetMedicalRecord.performed_at.desc())
    )
    return list(result.scalars().all())


async def create_medical_record(
    db: AsyncSession,
    pet_id: int,
    type: str,
    description: str,
    performed_at: datetime,
    performed_by: str | None = None,
    expires_at: datetime | None = None,
    reminder_days_before: int | None = None,
    notes: str | None = None,
    cost_expense_id: int | None = None,
    document_id: int | None = None,
) -> PetMedicalRecord:
    """Create a medical record."""
    pet = await get_pet_by_id(db, pet_id)
    if not pet:
        raise NotFoundError(code="PET_NOT_FOUND", detail=f"Pet {pet_id} not found")

    # Force conversion if needed (SQLite fix)
    if isinstance(performed_at, str):
        performed_at = datetime.fromisoformat(performed_at)

    record = PetMedicalRecord(
        pet_id=pet_id,
        type=type,
        description=description,
        performed_at=performed_at,
        performed_by=performed_by,
        expires_at=expires_at,
        reminder_days_before=reminder_days_before,
        notes=notes,
        cost_expense_id=cost_expense_id,
        document_id=document_id,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_expiring_vaccines(
    db: AsyncSession, group_id: int, days_ahead: int = 30
) -> list[PetMedicalRecord]:
    """Get vaccines expiring soon."""
    now = datetime.now(UTC)
    target_date = now + timedelta(days=days_ahead)

    result = await db.execute(
        select(PetMedicalRecord)
        .join(Pet)
        .where(
            and_(
                Pet.group_id == group_id,
                Pet.is_alive.is_(True),
                # Record type check? The requirement implies vaccines.
                PetMedicalRecord.type == "VACCINE",
                PetMedicalRecord.expires_at.is_not(None),
                PetMedicalRecord.expires_at > now,
                PetMedicalRecord.expires_at <= target_date,
            )
        )
        .options(selectinload(PetMedicalRecord.pet))
        .order_by(PetMedicalRecord.expires_at)
    )
    return list(result.scalars().all())


# ---------- Logs ----------
async def list_pet_logs(db: AsyncSession, pet_id: int, limit: int = 50) -> list[PetLog]:
    """List care logs."""
    result = await db.execute(
        select(PetLog)
        .where(PetLog.pet_id == pet_id)
        .order_by(PetLog.occurred_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_pet_log(
    db: AsyncSession,
    pet_id: int,
    user_id: int,
    action: str,
    occurred_at: datetime,
    value_amount: float | None = None,
    value_unit: str | None = None,
    notes: str | None = None,
    photo_url: str | None = None,
) -> PetLog:
    """Log an activity."""
    pet = await get_pet_by_id(db, pet_id)
    if not pet:
        raise NotFoundError(code="PET_NOT_FOUND", detail=f"Pet {pet_id} not found")

    log = PetLog(
        pet_id=pet_id,
        user_id=user_id,
        action=action,
        occurred_at=occurred_at,
        value_amount=value_amount,
        value_unit=value_unit,
        notes=notes,
        photo_url=photo_url,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)

    return log


# ---------- Schedules ----------
async def get_schedule_by_id(db: AsyncSession, schedule_id: int) -> PetSchedule | None:
    """Get pet schedule by ID with pet loaded (for group ownership check)."""
    result = await db.execute(
        select(PetSchedule)
        .where(PetSchedule.id == schedule_id)
        .options(selectinload(PetSchedule.pet))
    )
    return result.scalar_one_or_none()


async def list_pet_schedules(db: AsyncSession, pet_id: int) -> list[PetSchedule]:
    """List schedules."""
    result = await db.execute(select(PetSchedule).where(PetSchedule.pet_id == pet_id))
    return list(result.scalars().all())


async def create_pet_schedule(
    db: AsyncSession,
    pet_id: int,
    action_type: str,
    frequency_type: str,
    time_of_day: Any | None = None,  # datetime.time
    assigned_to_id: int | None = None,
    is_rotating: bool = False,
) -> PetSchedule:
    """Create a schedule."""
    from datetime import time as time_type

    pet = await get_pet_by_id(db, pet_id)
    if not pet:
        raise NotFoundError(code="PET_NOT_FOUND", detail=f"Pet {pet_id} not found")

    # Convert time object to string for SQLite compatibility if needed
    # SQLite stores TIME as string, but SQLAlchemy expects datetime for DateTime columns
    # Since the model uses datetime, we'll convert time to a datetime with today's date
    time_value = None
    if time_of_day is not None:
        if isinstance(time_of_day, time_type):
            # Convert time to datetime for SQLite compatibility
            from datetime import date, datetime

            time_value = datetime.combine(date.today(), time_of_day)
        else:
            time_value = time_of_day

    sched = PetSchedule(
        pet_id=pet_id,
        action_type=action_type,
        frequency_type=frequency_type,
        time_of_day=time_value,
        assigned_to_id=assigned_to_id,
        is_rotating=is_rotating,
        is_active=True,
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
    value_amount: float | None = None,
    value_unit: str | None = None,
) -> PetSchedule:
    """Mark schedule as done -> creates log."""
    result = await db.execute(select(PetSchedule).where(PetSchedule.id == schedule_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise NotFoundError(code="SCHEDULE_NOT_FOUND", detail=f"Schedule {schedule_id} not found")

    # Log it
    await create_pet_log(
        db,
        pet_id=sched.pet_id,
        user_id=user_id,
        action=sched.action_type,
        occurred_at=datetime.now(UTC),
        notes=notes,
        value_amount=value_amount,
        value_unit=value_unit,
    )

    # Refresh schedule to ensure it's in a valid state
    await db.refresh(sched)
    return sched

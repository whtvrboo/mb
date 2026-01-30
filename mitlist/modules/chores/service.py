"""Chores module service layer - business logic. PRIVATE - other modules import from interface.py."""

from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy import select, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError, ValidationError
from mitlist.modules.chores.models import (
    Chore,
    ChoreAssignment,
    ChoreDependency,
    ChoreTemplate,
)


async def list_chores(db: AsyncSession, group_id: int, active_only: bool = True) -> list[Chore]:
    """List chore definitions for a group."""
    q = select(Chore).where(Chore.group_id == group_id)
    if active_only:
        q = q.where(Chore.is_active.is_(True))
    q = q.order_by(Chore.id)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_chore_by_id(db: AsyncSession, chore_id: int) -> Optional[Chore]:
    """Get a chore by ID."""
    result = await db.execute(
        select(Chore).options(selectinload(Chore.assignments)).where(Chore.id == chore_id)
    )
    return result.scalar_one_or_none()


async def create_chore(
    db: AsyncSession,
    group_id: int,
    name: str,
    frequency_type: str,
    effort_value: int,
    description: Optional[str] = None,
    interval_value: int = 1,
    estimated_duration_minutes: Optional[int] = None,
    category: Optional[str] = None,
    is_rotating: bool = False,
    rotation_strategy: Optional[str] = None,
    required_item_concept_id: Optional[int] = None,
) -> Chore:
    """Create a new chore."""
    chore = Chore(
        group_id=group_id,
        name=name,
        description=description,
        frequency_type=frequency_type,
        interval_value=interval_value,
        effort_value=effort_value,
        estimated_duration_minutes=estimated_duration_minutes,
        category=category,
        is_rotating=is_rotating,
        rotation_strategy=rotation_strategy,
        required_item_concept_id=required_item_concept_id,
    )
    db.add(chore)
    await db.flush()
    await db.refresh(chore)
    return chore


async def update_chore(
    db: AsyncSession,
    chore_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    frequency_type: Optional[str] = None,
    interval_value: Optional[int] = None,
    effort_value: Optional[int] = None,
    estimated_duration_minutes: Optional[int] = None,
    category: Optional[str] = None,
    is_rotating: Optional[bool] = None,
    rotation_strategy: Optional[str] = None,
    required_item_concept_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> Chore:
    """Update a chore."""
    result = await db.execute(select(Chore).where(Chore.id == chore_id))
    chore = result.scalar_one_or_none()
    if not chore:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
    if name is not None:
        chore.name = name
    if description is not None:
        chore.description = description
    if frequency_type is not None:
        chore.frequency_type = frequency_type
    if interval_value is not None:
        chore.interval_value = interval_value
    if effort_value is not None:
        chore.effort_value = effort_value
    if estimated_duration_minutes is not None:
        chore.estimated_duration_minutes = estimated_duration_minutes
    if category is not None:
        chore.category = category
    if is_rotating is not None:
        chore.is_rotating = is_rotating
    if rotation_strategy is not None:
        chore.rotation_strategy = rotation_strategy
    if required_item_concept_id is not None:
        chore.required_item_concept_id = required_item_concept_id
    if is_active is not None:
        chore.is_active = is_active
    await db.flush()
    await db.refresh(chore)
    return chore


async def delete_chore(db: AsyncSession, chore_id: int) -> None:
    """Remove a chore definition."""
    result = await db.execute(select(Chore).where(Chore.id == chore_id))
    chore = result.scalar_one_or_none()
    if not chore:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
    await db.delete(chore)
    await db.flush()


# ---------- Assignments ----------
async def list_assignments(
    db: AsyncSession,
    group_id: int,
    due_date: Optional[datetime] = None,
    status_filter: Optional[str] = None,
) -> list[ChoreAssignment]:
    """List chore assignments (e.g. what is due today). Filter by group via chore.group_id."""
    q = (
        select(ChoreAssignment)
        .join(Chore, ChoreAssignment.chore_id == Chore.id)
        .where(Chore.group_id == group_id)
        .options(selectinload(ChoreAssignment.chore))
    )
    if due_date is not None:
        day_start = due_date if isinstance(due_date, datetime) else datetime.combine(due_date, time.min)
        day_end = day_start + timedelta(days=1)
        q = q.where(ChoreAssignment.due_date >= day_start).where(ChoreAssignment.due_date < day_end)
    if status_filter is not None:
        q = q.where(ChoreAssignment.status == status_filter)
    q = q.order_by(ChoreAssignment.due_date, ChoreAssignment.id)
    result = await db.execute(q)
    return list(result.unique().scalars().all())


async def get_assignment_by_id(db: AsyncSession, assignment_id: int) -> Optional[ChoreAssignment]:
    """Get a chore assignment by ID."""
    result = await db.execute(
        select(ChoreAssignment)
        .options(selectinload(ChoreAssignment.chore))
        .where(ChoreAssignment.id == assignment_id)
    )
    return result.scalar_one_or_none()


async def complete_assignment(
    db: AsyncSession,
    assignment_id: int,
    completed_by_id: int,
    actual_duration_minutes: Optional[int] = None,
    notes: Optional[str] = None,
) -> ChoreAssignment:
    """Mark chore assignment as done (awards points)."""
    result = await db.execute(select(ChoreAssignment).where(ChoreAssignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a.status = "COMPLETED"
    a.completed_at = datetime.utcnow()
    a.completed_by_id = completed_by_id
    if actual_duration_minutes is not None:
        a.actual_duration_minutes = actual_duration_minutes
    if notes is not None:
        a.notes = notes
    await db.flush()
    await db.refresh(a)
    return a


async def skip_assignment(db: AsyncSession, assignment_id: int) -> ChoreAssignment:
    """Skip a rotation."""
    result = await db.execute(select(ChoreAssignment).where(ChoreAssignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a.status = "SKIPPED"
    await db.flush()
    await db.refresh(a)
    return a


async def reassign_assignment(db: AsyncSession, assignment_id: int, assigned_to_id: int) -> ChoreAssignment:
    """Pass chore to another member."""
    result = await db.execute(select(ChoreAssignment).where(ChoreAssignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a.assigned_to_id = assigned_to_id
    await db.flush()
    await db.refresh(a)
    return a


async def list_chore_history(
    db: AsyncSession,
    group_id: int,
    limit: int = 50,
    offset: int = 0,
) -> list[ChoreAssignment]:
    """View log of completed chores."""
    from sqlalchemy import and_

    q = (
        select(ChoreAssignment)
        .join(Chore, ChoreAssignment.chore_id == Chore.id)
        .where(and_(Chore.group_id == group_id, ChoreAssignment.status == "COMPLETED"))
        .options(selectinload(ChoreAssignment.chore))
        .order_by(ChoreAssignment.completed_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(q)
    return list(result.unique().scalars().all())

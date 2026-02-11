"""Chores module service layer - business logic. PRIVATE - other modules import from interface.py."""

from datetime import UTC, datetime, time, timedelta

from sqlalchemy import and_, case, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload

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


async def get_chore_by_id(db: AsyncSession, chore_id: int) -> Chore | None:
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
    description: str | None = None,
    interval_value: int = 1,
    estimated_duration_minutes: int | None = None,
    category: str | None = None,
    is_rotating: bool = False,
    rotation_strategy: str | None = None,
    required_item_concept_id: int | None = None,
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
    name: str | None = None,
    description: str | None = None,
    frequency_type: str | None = None,
    interval_value: int | None = None,
    effort_value: int | None = None,
    estimated_duration_minutes: int | None = None,
    category: str | None = None,
    is_rotating: bool | None = None,
    rotation_strategy: str | None = None,
    required_item_concept_id: int | None = None,
    is_active: bool | None = None,
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
    due_date: datetime | None = None,
    status_filter: str | None = None,
) -> list[ChoreAssignment]:
    """List chore assignments (e.g. what is due today). Filter by group via chore.group_id."""
    q = (
        select(ChoreAssignment)
        .join(Chore, ChoreAssignment.chore_id == Chore.id)
        .where(Chore.group_id == group_id)
        .options(contains_eager(ChoreAssignment.chore))
    )
    if due_date is not None:
        day_start = (
            due_date if isinstance(due_date, datetime) else datetime.combine(due_date, time.min)
        )
        day_end = day_start + timedelta(days=1)
        q = q.where(ChoreAssignment.due_date >= day_start).where(ChoreAssignment.due_date < day_end)
    if status_filter is not None:
        q = q.where(ChoreAssignment.status == status_filter)
    q = q.order_by(ChoreAssignment.due_date, ChoreAssignment.id)
    result = await db.execute(q)
    return list(result.unique().scalars().all())


async def get_assignment_by_id(db: AsyncSession, assignment_id: int) -> ChoreAssignment | None:
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
    actual_duration_minutes: int | None = None,
    notes: str | None = None,
) -> ChoreAssignment:
    """Mark chore assignment as done (awards points)."""
    result = await db.execute(select(ChoreAssignment).where(ChoreAssignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise NotFoundError(
            code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found"
        )
    a.status = "COMPLETED"
    a.completed_at = datetime.now(UTC)
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
        raise NotFoundError(
            code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found"
        )
    a.status = "SKIPPED"
    await db.flush()
    await db.refresh(a)
    return a


async def reassign_assignment(
    db: AsyncSession, assignment_id: int, assigned_to_id: int
) -> ChoreAssignment:
    """Pass chore to another member."""
    result = await db.execute(select(ChoreAssignment).where(ChoreAssignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise NotFoundError(
            code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found"
        )
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


# ---------- Dependencies ----------
async def add_dependency(
    db: AsyncSession,
    chore_id: int,
    depends_on_chore_id: int,
    dependency_type: str = "BLOCKING",
) -> ChoreDependency:
    """Add a dependency between two chores."""
    # Verify both chores exist
    c1 = await get_chore_by_id(db, chore_id)
    c2 = await get_chore_by_id(db, depends_on_chore_id)
    if not c1 or not c2:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail="One or both chores not found")

    # Check against circular dependency (basic check)
    if chore_id == depends_on_chore_id:
        raise ValidationError(code="INVALID_DEPENDENCY", detail="Chore cannot depend on itself")

    dep = ChoreDependency(
        chore_id=chore_id,
        depends_on_chore_id=depends_on_chore_id,
        dependency_type=dependency_type,
    )
    db.add(dep)
    try:
        await db.flush()
    except Exception:
        raise ValidationError(code="DEPENDENCY_EXISTS", detail="Dependency already exists")
    await db.refresh(dep)
    return dep


async def get_dependency_by_id(db: AsyncSession, dependency_id: int) -> ChoreDependency | None:
    """Get dependency by ID (for group ownership check via chore_id)."""
    result = await db.execute(select(ChoreDependency).where(ChoreDependency.id == dependency_id))
    return result.scalar_one_or_none()


async def remove_dependency(db: AsyncSession, dependency_id: int) -> None:
    """Remove a dependency."""
    result = await db.execute(select(ChoreDependency).where(ChoreDependency.id == dependency_id))
    dep = result.scalar_one_or_none()
    if not dep:
        raise NotFoundError(
            code="DEPENDENCY_NOT_FOUND", detail=f"Dependency {dependency_id} not found"
        )
    await db.delete(dep)
    await db.flush()


async def get_dependencies(db: AsyncSession, chore_id: int) -> list[ChoreDependency]:
    """Get dependencies for a chore."""
    result = await db.execute(select(ChoreDependency).where(ChoreDependency.chore_id == chore_id))
    return list(result.scalars().all())


async def check_dependencies_met(db: AsyncSession, assignment_id: int) -> bool:
    """Check if all blocking dependencies for an assignment are completed."""
    # 1. Get the chore for this assignment
    assignment = await get_assignment_by_id(db, assignment_id)
    if not assignment:
        return True  # Fail safe? Or throw?

    # 2. Get dependencies for this chore
    deps = await get_dependencies(db, assignment.chore_id)
    blocking_deps = [d for d in deps if d.dependency_type == "BLOCKING"]

    if not blocking_deps:
        return True

    # 3. For each dependency, check if there is a COMPLETED assignment for that chore
    # within the relevant time window. This is complex logic (e.g. "did I do the pre-req TODAY?").
    # Simplified: Check if the LATEST assignment of the dependency chore is completed.

    # Optimized: Fetch latest status for all dependencies in one query using Window Function
    from sqlalchemy import func

    blocking_dep_ids = [d.depends_on_chore_id for d in blocking_deps]

    # Subquery: Rank assignments by due_date desc for each chore
    subq = (
        select(
            ChoreAssignment.chore_id,
            ChoreAssignment.status,
            func.row_number()
            .over(
                partition_by=ChoreAssignment.chore_id,
                order_by=ChoreAssignment.due_date.desc(),
            )
            .label("rn"),
        )
        .where(ChoreAssignment.chore_id.in_(blocking_dep_ids))
        .subquery()
    )

    # Query: Get status of the latest assignment (rn=1)
    q = select(subq.c.chore_id, subq.c.status).where(subq.c.rn == 1)

    result = await db.execute(q)
    rows = result.all()

    # Map chore_id -> status
    latest_status_map = {row.chore_id: row.status for row in rows}

    for dep in blocking_deps:
        status = latest_status_map.get(dep.depends_on_chore_id)
        # If never assigned, or last assignment not completed, then blocked.
        if not status or status != "COMPLETED":
            return False

    return True


# ---------- Templates ----------
async def list_templates(db: AsyncSession, include_public: bool = True) -> list[ChoreTemplate]:
    """List chore templates."""
    q = select(ChoreTemplate)
    if not include_public:
        q = q.where(ChoreTemplate.is_public.is_(False))
    result = await db.execute(q)
    return list(result.scalars().all())


async def create_template(
    db: AsyncSession,
    name: str,
    frequency_type: str,
    effort_value: int,
    description: str | None = None,
    interval_value: int = 1,
    category: str | None = None,
    is_public: bool = False,
) -> ChoreTemplate:
    """Create a new chore template."""
    tmpl = ChoreTemplate(
        name=name,
        description=description,
        frequency_type=frequency_type,
        interval_value=interval_value,
        effort_value=effort_value,
        category=category,
        is_public=is_public,
    )
    db.add(tmpl)
    await db.flush()
    await db.refresh(tmpl)
    return tmpl


async def create_chore_from_template(
    db: AsyncSession,
    template_id: int,
    group_id: int,
    overrides: dict,
) -> Chore:
    """Instantiate a chore from a template."""
    result = await db.execute(select(ChoreTemplate).where(ChoreTemplate.id == template_id))
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        raise NotFoundError(code="TEMPLATE_NOT_FOUND", detail=f"Template {template_id} not found")

    # Increment use count
    tmpl.use_count += 1

    # Create chore
    chore = Chore(
        group_id=group_id,
        name=overrides.get("name", tmpl.name),
        description=overrides.get("description", tmpl.description),
        frequency_type=overrides.get("frequency_type", tmpl.frequency_type),
        interval_value=overrides.get("interval_value", tmpl.interval_value),
        effort_value=tmpl.effort_value,
        category=tmpl.category,
        # Default others
        is_rotating=False,
        is_active=True,
    )
    db.add(chore)
    await db.flush()
    await db.refresh(chore)
    return chore


# ---------- Stats & Actions ----------
async def get_group_stats(db: AsyncSession, group_id: int) -> dict:
    """Get high level stats for a group."""
    from sqlalchemy import func

    # Total/Active Chores
    result_chores = await db.execute(
        select(
            func.count(Chore.id),
            func.sum(case((Chore.is_active.is_(True), 1), else_=0)),
        ).where(Chore.group_id == group_id)
    )
    total_chores, active_chores = result_chores.one()

    # Assignments Stats
    result_assigns = await db.execute(
        select(
            func.count(ChoreAssignment.id),
            func.sum(case((ChoreAssignment.status == "COMPLETED", 1), else_=0)),
            func.sum(case((ChoreAssignment.status == "PENDING", 1), else_=0)),
            # Simple heuristic for overdue: PENDING and due date < now
            func.sum(
                case(
                    (
                        and_(
                            ChoreAssignment.status == "PENDING",
                            ChoreAssignment.due_date < datetime.now(UTC),
                        ),
                        1,
                    ),
                    else_=0,
                )
            ),
        )
        .join(Chore)
        .where(Chore.group_id == group_id)
    )
    (
        total_assigns,
        completed_assigns,
        pending_assigns,
        overdue_assigns,
    ) = result_assigns.one()

    total_assigns = total_assigns or 0
    completed_assigns = completed_assigns or 0
    pending_assigns = pending_assigns or 0
    overdue_assigns = overdue_assigns or 0

    completion_rate = 0.0
    if total_assigns > 0:
        completion_rate = completed_assigns / total_assigns

    # Calculate average completion time from actual_duration_minutes
    avg_time_result = await db.execute(
        select(func.avg(ChoreAssignment.actual_duration_minutes))
        .join(Chore)
        .where(
            Chore.group_id == group_id,
            ChoreAssignment.status == "COMPLETED",
            ChoreAssignment.actual_duration_minutes.isnot(None),
        )
    )
    avg_completion_time = avg_time_result.scalar_one() or 0.0

    return {
        "total_chores": total_chores or 0,
        "active_chores": active_chores or 0,
        "total_assignments": total_assigns,
        "completed_assignments": completed_assigns,
        "pending_assignments": pending_assigns,
        "overdue_assignments": overdue_assigns,
        "completion_rate": completion_rate,
        "average_completion_time_minutes": float(avg_completion_time),
    }


async def get_user_stats(db: AsyncSession, group_id: int, user_id: int) -> dict:
    """Get stats for a specific user in a group."""
    from sqlalchemy import func

    result = await db.execute(
        select(
            func.count(ChoreAssignment.id),
            func.sum(case((ChoreAssignment.status == "COMPLETED", 1), else_=0)),
            func.sum(case((ChoreAssignment.status == "PENDING", 1), else_=0)),
            func.sum(case((ChoreAssignment.status == "SKIPPED", 1), else_=0)),
            func.avg(ChoreAssignment.quality_rating),
        )
        .join(Chore)
        .where(and_(Chore.group_id == group_id, ChoreAssignment.assigned_to_id == user_id))
    )
    total, completed, pending, skipped, avg_rating = result.one()

    total = total or 0
    completed = completed or 0
    pending = pending or 0
    skipped = skipped or 0

    # Calculate effort points (sum of chore.effort_value for completed assignments)
    result_effort = await db.execute(
        select(func.sum(Chore.effort_value))
        .join(ChoreAssignment, Chore.id == ChoreAssignment.chore_id)
        .where(
            and_(
                Chore.group_id == group_id,
                ChoreAssignment.assigned_to_id == user_id,
                ChoreAssignment.status == "COMPLETED",
            )
        )
    )
    total_effort = result_effort.scalar() or 0

    completion_rate = 0.0
    if total > 0:
        completion_rate = completed / total

    return {
        "user_id": user_id,
        "total_assigned": total,
        "completed": completed,
        "pending": pending,
        "skipped": skipped,
        "total_effort_points": total_effort,
        "average_quality_rating": avg_rating,
        "completion_rate": completion_rate,
    }


async def get_leaderboard(db: AsyncSession, group_id: int, period="monthly") -> list[dict]:
    """Get leaderboard rankings."""
    from sqlalchemy import func

    # Optimized: Single query aggregation
    stmt = (
        select(
            ChoreAssignment.assigned_to_id,
            func.count(ChoreAssignment.id).label("total_assigned"),
            func.sum(case((ChoreAssignment.status == "COMPLETED", 1), else_=0)).label("completed"),
            func.sum(case((ChoreAssignment.status == "PENDING", 1), else_=0)).label("pending"),
            func.sum(case((ChoreAssignment.status == "SKIPPED", 1), else_=0)).label("skipped"),
            func.avg(ChoreAssignment.quality_rating).label("average_quality_rating"),
            func.sum(
                case((ChoreAssignment.status == "COMPLETED", Chore.effort_value), else_=0)
            ).label("total_effort_points"),
        )
        .join(Chore, ChoreAssignment.chore_id == Chore.id)
        .where(Chore.group_id == group_id)
        .group_by(ChoreAssignment.assigned_to_id)
        .order_by(text("total_effort_points DESC"))
    )

    result = await db.execute(stmt)
    rows = result.all()

    rankings = []
    for row in rows:
        total = row.total_assigned or 0
        completed = row.completed or 0
        completion_rate = (completed / total) if total > 0 else 0.0

        rankings.append(
            {
                "user_id": row.assigned_to_id,
                "total_assigned": total,
                "completed": completed,
                "pending": row.pending or 0,
                "skipped": row.skipped or 0,
                "total_effort_points": row.total_effort_points or 0,
                "average_quality_rating": float(row.average_quality_rating or 0.0),
                "completion_rate": completion_rate,
            }
        )

    return rankings


async def start_assignment(db: AsyncSession, assignment_id: int, user_id: int) -> ChoreAssignment:
    """Mark assignment as IN_PROGRESS."""
    result = await db.execute(select(ChoreAssignment).where(ChoreAssignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise NotFoundError(
            code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found"
        )

    a.status = "IN_PROGRESS"
    a.started_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(a)
    return a


async def rate_assignment(
    db: AsyncSession,
    assignment_id: int,
    rated_by_id: int,
    quality_rating: int,
) -> ChoreAssignment:
    """Rate a completed assignment."""
    result = await db.execute(select(ChoreAssignment).where(ChoreAssignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise NotFoundError(
            code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found"
        )

    if a.status != "COMPLETED":
        raise ValidationError(code="INVALID_STATUS", detail="Cannot rate an uncompleted assignment")

    a.quality_rating = quality_rating
    a.rated_by_id = rated_by_id
    await db.flush()
    await db.refresh(a)
    return a

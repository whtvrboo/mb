"""Chores & Tasks module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_group_id, get_current_user, get_db
from mitlist.core.errors import NotFoundError, ValidationError
from mitlist.modules.chores import interface, schemas

router = APIRouter(prefix="/chores", tags=["chores"])


@router.get("", response_model=ListType[schemas.ChoreResponse])
async def get_chores(
    group_id: int = Depends(get_current_group_id),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.ChoreResponse]:
    """List chore definitions for the group."""
    chores = await interface.list_chores(db, group_id, active_only=active_only)
    return [schemas.ChoreResponse.model_validate(c) for c in chores]


@router.post("", response_model=schemas.ChoreResponse, status_code=status.HTTP_201_CREATED)
async def create_chore(
    data: schemas.ChoreCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreResponse:
    """Create a new chore (sets frequency/rotation)."""
    if data.group_id != group_id:
        raise ValidationError(code="GROUP_MISMATCH", detail="group_id in body must match current group")
    chore = await interface.create_chore(
        db,
        group_id=group_id,
        name=data.name,
        frequency_type=data.frequency_type,
        effort_value=data.effort_value,
        description=data.description,
        interval_value=data.interval_value,
        estimated_duration_minutes=data.estimated_duration_minutes,
        category=data.category,
        is_rotating=data.is_rotating,
        rotation_strategy=data.rotation_strategy,
        required_item_concept_id=data.required_item_concept_id,
    )
    return schemas.ChoreResponse.model_validate(chore)


@router.get("/assignments", response_model=ListType[schemas.ChoreAssignmentWithChoreResponse])
async def get_chore_assignments(
    group_id: int = Depends(get_current_group_id),
    due_date: str | None = Query(None, description="ISO date for 'due today' filter"),
    status_filter: str | None = Query(None, pattern="^(PENDING|IN_PROGRESS|COMPLETED|SKIPPED)$"),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.ChoreAssignmentWithChoreResponse]:
    """List active assignments (what is due today)."""
    from datetime import datetime

    due_dt = None
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            pass
    assignments = await interface.list_assignments(db, group_id, due_date=due_dt, status_filter=status_filter)
    return [schemas.ChoreAssignmentWithChoreResponse.model_validate(a) for a in assignments]


@router.patch(
    "/assignments/{assignment_id}/complete",
    response_model=schemas.ChoreAssignmentResponse,
)
async def complete_chore_assignment(
    assignment_id: int,
    data: schemas.ChoreAssignmentCompleteRequest,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.ChoreAssignmentResponse:
    """Mark chore as done (awards points)."""
    a = await interface.get_assignment_by_id(db, assignment_id)
    if not a or a.chore.group_id != group_id:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a = await interface.complete_assignment(
        db,
        assignment_id=assignment_id,
        completed_by_id=user.id,
        actual_duration_minutes=data.actual_duration_minutes,
        notes=data.notes,
    )
    return schemas.ChoreAssignmentResponse.model_validate(a)


@router.patch("/assignments/{assignment_id}/skip", response_model=schemas.ChoreAssignmentResponse)
async def skip_chore_assignment(
    assignment_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreAssignmentResponse:
    """Skip a rotation."""
    a = await interface.get_assignment_by_id(db, assignment_id)
    if not a or a.chore.group_id != group_id:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a = await interface.skip_assignment(db, assignment_id)
    return schemas.ChoreAssignmentResponse.model_validate(a)


@router.patch("/assignments/{assignment_id}/reassign", response_model=schemas.ChoreAssignmentResponse)
async def reassign_chore(
    assignment_id: int,
    data: schemas.ChoreAssignmentReassignRequest,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreAssignmentResponse:
    """Pass chore to another member."""
    a = await interface.get_assignment_by_id(db, assignment_id)
    if not a or a.chore.group_id != group_id:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a = await interface.reassign_assignment(db, assignment_id, data.assigned_to_id)
    return schemas.ChoreAssignmentResponse.model_validate(a)


@router.get("/history", response_model=ListType[schemas.ChoreAssignmentWithChoreResponse])
async def get_chore_history(
    group_id: int = Depends(get_current_group_id),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.ChoreAssignmentWithChoreResponse]:
    """View log of completed chores."""
    assignments = await interface.list_chore_history(db, group_id, limit=limit, offset=offset)
    return [schemas.ChoreAssignmentWithChoreResponse.model_validate(a) for a in assignments]



# ---------- Stats ----------
@router.get("/stats", response_model=schemas.ChoreStatisticsResponse)
async def get_chore_stats(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get group chore statistics."""
    stats = await interface.get_group_stats(db, group_id)
    return schemas.ChoreStatisticsResponse(**stats)


@router.get("/stats/me", response_model=schemas.UserChoreStatsResponse)
async def get_my_chore_stats(
    group_id: int = Depends(get_current_group_id),
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get statistics for current user."""
    stats = await interface.get_user_stats(db, group_id, user.id)
    return schemas.UserChoreStatsResponse(**stats)


@router.get("/leaderboard", response_model=schemas.ChoreLeaderboardResponse)
async def get_chore_leaderboard(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get leaderboard for the group."""
    rankings = await interface.get_leaderboard(db, group_id)
    from datetime import datetime
    now = datetime.utcnow()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # period: current month 
    
    return schemas.ChoreLeaderboardResponse(
        group_id=group_id,
        period_start=start,
        period_end=now,
        rankings=[schemas.UserChoreStatsResponse(**r) for r in rankings]
    )

@router.get("/{chore_id}", response_model=schemas.ChoreResponse)
async def get_chore(
    chore_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreResponse:
    """Get a chore by ID."""
    chore = await interface.get_chore_by_id(db, chore_id)
    if not chore or chore.group_id != group_id:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
    return schemas.ChoreResponse.model_validate(chore)


@router.patch("/{chore_id}", response_model=schemas.ChoreResponse)
async def update_chore(
    chore_id: int,
    data: schemas.ChoreUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreResponse:
    """Update frequency or assigned users."""
    chore_existing = await interface.get_chore_by_id(db, chore_id)
    if not chore_existing or chore_existing.group_id != group_id:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
    chore = await interface.update_chore(
        db,
        chore_id=chore_id,
        name=data.name,
        description=data.description,
        frequency_type=data.frequency_type,
        interval_value=data.interval_value,
        effort_value=data.effort_value,
        estimated_duration_minutes=data.estimated_duration_minutes,
        category=data.category,
        is_rotating=data.is_rotating,
        rotation_strategy=data.rotation_strategy,
        required_item_concept_id=data.required_item_concept_id,
        is_active=data.is_active,
    )
    return schemas.ChoreResponse.model_validate(chore)


@router.delete("/{chore_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chore(
    chore_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove chore definition."""
    chore = await interface.get_chore_by_id(db, chore_id)
    if not chore or chore.group_id != group_id:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
    await interface.delete_chore(db, chore_id)


# ---------- Dependencies ----------
@router.get("/{chore_id}/dependencies", response_model=ListType[schemas.ChoreDependencyResponse])
async def get_chore_dependencies(
    chore_id: int,
    db: AsyncSession = Depends(get_db),
    group_id: int = Depends(get_current_group_id),
):
    """Get dependencies for a chore."""
    chore = await interface.get_chore_by_id(db, chore_id)
    if not chore or chore.group_id != group_id:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
        
    deps = await interface.get_dependencies(db, chore_id)
    return [schemas.ChoreDependencyResponse.model_validate(d) for d in deps]


@router.post("/{chore_id}/dependencies", response_model=schemas.ChoreDependencyResponse, status_code=status.HTTP_201_CREATED)
async def add_chore_dependency(
    chore_id: int,
    data: schemas.ChoreDependencyCreate,
    db: AsyncSession = Depends(get_db),
    group_id: int = Depends(get_current_group_id),
):
    """Add a dependency."""
    c1 = await interface.get_chore_by_id(db, chore_id)
    if not c1 or c1.group_id != group_id:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
    
    if data.chore_id != chore_id:
         raise ValidationError(code="ID_MISMATCH", detail="Body chore_id must match path")

    c2 = await interface.get_chore_by_id(db, data.depends_on_chore_id)
    if not c2 or c2.group_id != group_id:
         raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {data.depends_on_chore_id} not found")

    dep = await interface.add_dependency(
        db, chore_id, data.depends_on_chore_id, data.dependency_type
    )
    return schemas.ChoreDependencyResponse.model_validate(dep)


@router.delete("/dependencies/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_chore_dependency(
    dependency_id: int,
    db: AsyncSession = Depends(get_db),
    group_id: int = Depends(get_current_group_id),
):
    """Remove a dependency."""
    dep = await interface.get_dependency_by_id(db, dependency_id)
    if not dep:
        raise NotFoundError(code="DEPENDENCY_NOT_FOUND", detail=f"Dependency {dependency_id} not found")
    chore = await interface.get_chore_by_id(db, dep.chore_id)
    if not chore or chore.group_id != group_id:
        raise NotFoundError(code="DEPENDENCY_NOT_FOUND", detail=f"Dependency {dependency_id} not found")
    await interface.remove_dependency(db, dependency_id)


# ---------- Templates ----------
@router.get("/templates", response_model=ListType[schemas.ChoreTemplateResponse])
async def list_chore_templates(
    include_public: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """List available chore templates."""
    tmpls = await interface.list_templates(db, include_public=include_public)
    return [schemas.ChoreTemplateResponse.model_validate(t) for t in tmpls]


@router.post("/templates", response_model=schemas.ChoreTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_chore_template(
    data: schemas.ChoreTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chore template."""
    tmpl = await interface.create_template(
        db,
        name=data.name,
        frequency_type=data.frequency_type,
        effort_value=data.effort_value,
        description=data.description,
        interval_value=data.interval_value,
        category=data.category,
        is_public=data.is_public,
    )
    return schemas.ChoreTemplateResponse.model_validate(tmpl)


@router.post("/templates/{template_id}/instantiate", response_model=schemas.ChoreResponse)
async def create_chore_from_template(
    template_id: int,
    data: schemas.ChoreFromTemplateRequest,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a chore in the group from a template."""
    if data.group_id != group_id:
        raise ValidationError(code="GROUP_MISMATCH", detail="group_id mismatch")
    
    if data.template_id != template_id:
         raise ValidationError(code="ID_MISMATCH", detail="template_id mismatch")

    overrides = {}
    if data.name: overrides["name"] = data.name
    if data.frequency_type: overrides["frequency_type"] = data.frequency_type
    if data.interval_value: overrides["interval_value"] = data.interval_value

    chore = await interface.create_chore_from_template(
        db, template_id, group_id, overrides
    )
    return schemas.ChoreResponse.model_validate(chore)




# ---------- Assignment Actions ----------
@router.patch("/assignments/{assignment_id}/start", response_model=schemas.ChoreAssignmentResponse)
async def start_chore_assignment(
    assignment_id: int,
    group_id: int = Depends(get_current_group_id),
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start an assignment."""
    a = await interface.get_assignment_by_id(db, assignment_id)
    if not a or a.chore.group_id != group_id:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail="Assignment not found")
    
    updated_a = await interface.start_assignment(db, assignment_id, user.id)
    return schemas.ChoreAssignmentResponse.model_validate(updated_a)


@router.post("/assignments/{assignment_id}/rate", response_model=schemas.ChoreAssignmentResponse)
async def rate_chore_assignment(
    assignment_id: int,
    data: schemas.ChoreAssignmentRateRequest,
    group_id: int = Depends(get_current_group_id),
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rate a completed assignment."""
    a = await interface.get_assignment_by_id(db, assignment_id)
    if not a or a.chore.group_id != group_id:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail="Assignment not found")
        
    updated_a = await interface.rate_assignment(db, assignment_id, user.id, data.quality_rating)
    return schemas.ChoreAssignmentResponse.model_validate(updated_a)

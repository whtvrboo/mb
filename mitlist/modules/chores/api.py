"""Chores & Tasks module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotFoundError
from mitlist.modules.chores import interface, schemas

router = APIRouter(prefix="/chores", tags=["chores"])


@router.get("", response_model=ListType[schemas.ChoreResponse])
async def get_chores(
    group_id: int,
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.ChoreResponse]:
    """List chore definitions for the group."""
    chores = await interface.list_chores(db, group_id, active_only=active_only)
    return [schemas.ChoreResponse.model_validate(c) for c in chores]


@router.post("", response_model=schemas.ChoreResponse, status_code=status.HTTP_201_CREATED)
async def create_chore(
    data: schemas.ChoreCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreResponse:
    """Create a new chore (sets frequency/rotation)."""
    chore = await interface.create_chore(
        db,
        group_id=data.group_id,
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
    group_id: int,
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
    completed_by_id: int = Query(..., description="User completing the chore"),
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreAssignmentResponse:
    """Mark chore as done (awards points)."""
    a = await interface.get_assignment_by_id(db, assignment_id)
    if not a:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a = await interface.complete_assignment(
        db,
        assignment_id=assignment_id,
        completed_by_id=completed_by_id,
        actual_duration_minutes=data.actual_duration_minutes,
        notes=data.notes,
    )
    return schemas.ChoreAssignmentResponse.model_validate(a)


@router.patch("/assignments/{assignment_id}/skip", response_model=schemas.ChoreAssignmentResponse)
async def skip_chore_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreAssignmentResponse:
    """Skip a rotation."""
    a = await interface.get_assignment_by_id(db, assignment_id)
    if not a:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a = await interface.skip_assignment(db, assignment_id)
    return schemas.ChoreAssignmentResponse.model_validate(a)


@router.patch("/assignments/{assignment_id}/reassign", response_model=schemas.ChoreAssignmentResponse)
async def reassign_chore(
    assignment_id: int,
    data: schemas.ChoreAssignmentReassignRequest,
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreAssignmentResponse:
    """Pass chore to another member."""
    a = await interface.get_assignment_by_id(db, assignment_id)
    if not a:
        raise NotFoundError(code="ASSIGNMENT_NOT_FOUND", detail=f"Assignment {assignment_id} not found")
    a = await interface.reassign_assignment(db, assignment_id, data.assigned_to_id)
    return schemas.ChoreAssignmentResponse.model_validate(a)


@router.get("/history", response_model=ListType[schemas.ChoreAssignmentWithChoreResponse])
async def get_chore_history(
    group_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.ChoreAssignmentWithChoreResponse]:
    """View log of completed chores."""
    assignments = await interface.list_chore_history(db, group_id, limit=limit, offset=offset)
    return [schemas.ChoreAssignmentWithChoreResponse.model_validate(a) for a in assignments]


@router.get("/{chore_id}", response_model=schemas.ChoreResponse)
async def get_chore(
    chore_id: int,
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreResponse:
    """Get a chore by ID."""
    chore = await interface.get_chore_by_id(db, chore_id)
    if not chore:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
    return schemas.ChoreResponse.model_validate(chore)


@router.patch("/{chore_id}", response_model=schemas.ChoreResponse)
async def update_chore(
    chore_id: int,
    data: schemas.ChoreUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ChoreResponse:
    """Update frequency or assigned users."""
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
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove chore definition."""
    chore = await interface.get_chore_by_id(db, chore_id)
    if not chore:
        raise NotFoundError(code="CHORE_NOT_FOUND", detail=f"Chore {chore_id} not found")
    await interface.delete_chore(db, chore_id)

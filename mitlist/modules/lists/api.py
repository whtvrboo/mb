"""Lists module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotFoundError
from mitlist.modules.lists import interface, schemas

router = APIRouter(prefix="/lists", tags=["lists"])


@router.get("", response_model=ListType[schemas.ListResponse])
async def get_lists(
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.ListResponse]:
    """
    Get all lists for a group.

    Returns list directly (no envelope) per API contract.
    """
    # TODO: Implement filtering logic
    return []


@router.get("/{list_id}", response_model=schemas.ListResponse)
async def get_list(
    list_id: int,
    db: AsyncSession = Depends(get_db),
) -> schemas.ListResponse:
    """
    Get a single list by ID.

    Returns list directly (no envelope) per API contract.
    """
    list_obj = await interface.get_list_by_id(db, list_id)
    if not list_obj:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")
    return schemas.ListResponse.model_validate(list_obj)


@router.post("", response_model=schemas.ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    data: schemas.ListCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ListResponse:
    """
    Create a new list.

    Returns created list directly (no envelope) per API contract.
    """
    list_obj = await interface.create_list(db, data.group_id, data.name, data.type)
    return schemas.ListResponse.model_validate(list_obj)


@router.patch("/{list_id}", response_model=schemas.ListResponse)
async def update_list(
    list_id: int,
    data: schemas.ListUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ListResponse:
    """
    Update a list.

    Returns updated list directly (no envelope) per API contract.
    Handles StaleDataError from optimistic locking.
    """
    list_obj = await interface.update_list(
        db,
        list_id,
        name=data.name,
        deadline=data.deadline,
        is_archived=data.is_archived,
    )
    return schemas.ListResponse.model_validate(list_obj)

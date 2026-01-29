"""Lists module service layer - business logic."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError, StaleDataError
from mitlist.modules.lists.models import Item, List

# Note: This is PRIVATE - other modules should import from interface.py


async def get_list_by_id(db: AsyncSession, list_id: int) -> Optional[List]:
    """Get a list by ID with items loaded."""
    result = await db.execute(
        select(List).options(selectinload(List.items)).where(List.id == list_id)
    )
    return result.scalar_one_or_none()


async def create_list(db: AsyncSession, group_id: int, name: str, list_type: str) -> List:
    """Create a new list."""
    new_list = List(
        group_id=group_id,
        name=name,
        type=list_type,
    )
    db.add(new_list)
    await db.flush()
    await db.refresh(new_list)
    return new_list


async def update_list(
    db: AsyncSession,
    list_id: int,
    name: Optional[str] = None,
    deadline: Optional[datetime] = None,
    is_archived: Optional[bool] = None,
) -> List:
    """
    Update a list with optimistic locking.

    Raises StaleDataError if version_id mismatch (concurrent modification).
    """
    # Use with_for_update() for critical path (though for lists, optimistic locking is usually sufficient)
    result = await db.execute(
        select(List).where(List.id == list_id).with_for_update()
    )
    list_obj = result.scalar_one_or_none()

    if not list_obj:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")

    if name is not None:
        list_obj.name = name
    if deadline is not None:
        list_obj.deadline = deadline
    if is_archived is not None:
        list_obj.is_archived = is_archived
        if is_archived:
            list_obj.archived_at = datetime.utcnow()
        else:
            list_obj.archived_at = None

    try:
        await db.flush()
        await db.refresh(list_obj)
        return list_obj
    except Exception as e:
        # SQLAlchemy will raise StaleDataError on version mismatch
        if "version" in str(e).lower() or "stale" in str(e).lower():
            raise StaleDataError(detail=f"List {list_id} was modified by another request")
        raise


async def decrement_item_quantity(
    db: AsyncSession, item_id: int, quantity: float
) -> Item:
    """
    Decrement item quantity - example of critical path using with_for_update().

    This demonstrates pessimistic locking for inventory-style operations.
    """
    # REQUIRED: Use with_for_update() for inventory decrements
    result = await db.execute(
        select(Item).where(Item.id == item_id).with_for_update()
    )
    item = result.scalar_one_or_none()

    if not item:
        raise NotFoundError(code="ITEM_NOT_FOUND", detail=f"Item {item_id} not found")

    if item.quantity_value is None or item.quantity_value < quantity:
        raise ValueError(f"Insufficient quantity: {item.quantity_value} < {quantity}")

    item.quantity_value -= quantity
    await db.flush()
    await db.refresh(item)
    return item

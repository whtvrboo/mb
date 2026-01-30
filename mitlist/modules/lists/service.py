"""Lists module service layer - business logic."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError, StaleDataError
from mitlist.modules.lists.models import InventoryItem, Item, List

# Note: This is PRIVATE - other modules should import from interface.py


async def list_lists(
    db: AsyncSession,
    group_id: int,
    is_archived: Optional[bool] = None,
    list_type: Optional[str] = None,
) -> list[List]:
    """List all lists for a group with optional filters."""
    q = select(List).where(List.group_id == group_id)
    if is_archived is not None:
        q = q.where(List.is_archived == is_archived)
    if list_type is not None:
        q = q.where(List.type == list_type)
    q = q.order_by(List.id)
    result = await db.execute(q)
    return list(result.scalars().all())


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
            list_obj.archived_at = datetime.now(timezone.utc)
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


# ---------- List items ----------
async def get_items_by_list_id(db: AsyncSession, list_id: int) -> list[Item]:
    """Get all items for a list."""
    result = await db.execute(select(Item).where(Item.list_id == list_id).order_by(Item.id))
    return list(result.scalars().all())


async def get_item_by_id(db: AsyncSession, item_id: int) -> Optional[Item]:
    """Get a single item by ID."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()


async def create_item(
    db: AsyncSession,
    list_id: int,
    name: str,
    quantity_value: Optional[float] = None,
    quantity_unit: Optional[str] = None,
    is_checked: bool = False,
    price_estimate: Optional[float] = None,
    priority: Optional[str] = None,
    notes: Optional[str] = None,
) -> Item:
    """Add an item to a list."""
    item = Item(
        list_id=list_id,
        name=name,
        quantity_value=quantity_value,
        quantity_unit=quantity_unit,
        is_checked=is_checked,
        price_estimate=price_estimate,
        priority=priority,
        notes=notes,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def update_item(
    db: AsyncSession,
    item_id: int,
    name: Optional[str] = None,
    quantity_value: Optional[float] = None,
    quantity_unit: Optional[str] = None,
    is_checked: Optional[bool] = None,
    price_estimate: Optional[float] = None,
    priority: Optional[str] = None,
    notes: Optional[str] = None,
) -> Item:
    """Update an item (e.g. check/uncheck)."""
    result = await db.execute(select(Item).where(Item.id == item_id).with_for_update())
    item = result.scalar_one_or_none()
    if not item:
        raise NotFoundError(code="ITEM_NOT_FOUND", detail=f"Item {item_id} not found")
    if name is not None:
        item.name = name
    if quantity_value is not None:
        item.quantity_value = quantity_value
    if quantity_unit is not None:
        item.quantity_unit = quantity_unit
    if is_checked is not None:
        item.is_checked = is_checked
        item.checked_at = datetime.now(timezone.utc) if is_checked else None
    if price_estimate is not None:
        item.price_estimate = price_estimate
    if priority is not None:
        item.priority = priority
    if notes is not None:
        item.notes = notes
    await db.flush()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item_id: int) -> None:
    """Remove an item from a list."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise NotFoundError(code="ITEM_NOT_FOUND", detail=f"Item {item_id} not found")
    await db.delete(item)
    await db.flush()


async def bulk_add_items(db: AsyncSession, list_id: int, items_data: list[dict]) -> list[Item]:
    """Add multiple items to a list. items_data: list of dicts with name and optional ItemBase fields."""
    created = []
    for d in items_data:
        item = Item(
            list_id=list_id,
            name=d["name"],
            quantity_value=d.get("quantity_value"),
            quantity_unit=d.get("quantity_unit"),
            is_checked=d.get("is_checked", False),
            price_estimate=d.get("price_estimate"),
            priority=d.get("priority"),
            notes=d.get("notes"),
        )
        db.add(item)
        await db.flush()
        await db.refresh(item)
        created.append(item)
    return created


# ---------- Inventory ----------
async def list_inventory(db: AsyncSession, group_id: int) -> list[InventoryItem]:
    """List inventory items for a group."""
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.group_id == group_id).order_by(InventoryItem.id)
    )
    return list(result.scalars().all())


async def get_inventory_item_by_id(db: AsyncSession, inventory_id: int) -> Optional[InventoryItem]:
    """Get a single inventory item by ID."""
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == inventory_id))
    return result.scalar_one_or_none()


async def update_inventory_item(
    db: AsyncSession,
    inventory_id: int,
    quantity_value: Optional[float] = None,
    quantity_unit: Optional[str] = None,
    expiration_date: Optional[datetime] = None,
    opened_date: Optional[datetime] = None,
    restock_threshold: Optional[float] = None,
) -> InventoryItem:
    """Update quantity or other fields (e.g. mark out of stock by setting quantity_value to 0)."""
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == inventory_id).with_for_update()
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise NotFoundError(code="INVENTORY_ITEM_NOT_FOUND", detail=f"Inventory item {inventory_id} not found")
    if quantity_value is not None:
        inv.quantity_value = quantity_value
    if quantity_unit is not None:
        inv.quantity_unit = quantity_unit
    if expiration_date is not None:
        inv.expiration_date = expiration_date
    if opened_date is not None:
        inv.opened_date = opened_date
    if restock_threshold is not None:
        inv.restock_threshold = restock_threshold
    await db.flush()
    await db.refresh(inv)
    return inv

"""Lists module FastAPI router. Lists + Items + Inventory."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_group_id, get_db
from mitlist.core.errors import NotFoundError, ValidationError
from mitlist.modules.lists import interface, schemas

router = APIRouter(prefix="/lists", tags=["lists"])
inventory_router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=ListType[schemas.ListResponse])
async def get_lists(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
    is_archived: bool | None = None,
    list_type: str | None = None,
) -> ListType[schemas.ListResponse]:
    """
    Get all lists for a group.

    Returns list directly (no envelope) per API contract.
    """
    lists = await interface.list_lists(db, group_id, is_archived=is_archived, list_type=list_type)
    return [schemas.ListResponse.model_validate(lst) for lst in lists]


@router.get("/{list_id}", response_model=schemas.ListResponse)
async def get_list(
    list_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ListResponse:
    """
    Get a single list by ID.

    Returns list directly (no envelope) per API contract.
    """
    list_obj = await interface.get_list_by_id(db, list_id)
    if not list_obj:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")
    if list_obj.group_id != group_id:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")
    return schemas.ListResponse.model_validate(list_obj)


@router.post("", response_model=schemas.ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    data: schemas.ListCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ListResponse:
    """
    Create a new list.

    Returns created list directly (no envelope) per API contract.
    """
    if data.group_id != group_id:
        raise ValidationError(code="GROUP_MISMATCH", detail="group_id in body must match current group")
    list_obj = await interface.create_list(db, group_id, data.name, data.type)
    return schemas.ListResponse.model_validate(list_obj)


@router.patch("/{list_id}", response_model=schemas.ListResponse)
async def update_list(
    list_id: int,
    data: schemas.ListUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ListResponse:
    """
    Update a list.

    Returns updated list directly (no envelope) per API contract.
    Handles StaleDataError from optimistic locking.
    """
    list_obj = await interface.get_list_by_id(db, list_id)
    if not list_obj or list_obj.group_id != group_id:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")

    list_obj = await interface.update_list(
        db,
        list_id,
        name=data.name,
        deadline=data.deadline,
        is_archived=data.is_archived,
    )
    return schemas.ListResponse.model_validate(list_obj)


# ---------- List items ----------
@router.get("/{list_id}/items", response_model=ListType[schemas.ItemResponse])
async def get_list_items(
    list_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.ItemResponse]:
    """Get all items on a specific list."""
    list_obj = await interface.get_list_by_id(db, list_id)
    if not list_obj or list_obj.group_id != group_id:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")
    items = await interface.get_items_by_list_id(db, list_id)
    return [schemas.ItemResponse.model_validate(i) for i in items]


@router.post(
    "/{list_id}/items",
    response_model=schemas.ItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_list_item(
    list_id: int,
    data: schemas.ItemCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ItemResponse:
    """Add item to list."""
    if data.list_id != list_id:
        raise NotFoundError(code="LIST_MISMATCH", detail="list_id in body must match path")
    list_obj = await interface.get_list_by_id(db, list_id)
    if not list_obj or list_obj.group_id != group_id:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")
    item = await interface.create_item(
        db,
        list_id=list_id,
        name=data.name,
        quantity_value=data.quantity_value,
        quantity_unit=data.quantity_unit,
        is_checked=data.is_checked,
        price_estimate=data.price_estimate,
        priority=data.priority,
        notes=data.notes,
    )
    return schemas.ItemResponse.model_validate(item)


@router.patch("/{list_id}/items/{item_id}", response_model=schemas.ItemResponse)
async def update_list_item(
    list_id: int,
    item_id: int,
    data: schemas.ItemUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ItemResponse:
    """Check/uncheck or update item."""
    item = await interface.get_item_by_id(db, item_id)
    if not item or item.list_id != list_id:
        raise NotFoundError(code="ITEM_NOT_FOUND", detail=f"Item {item_id} not found")
    list_obj = await interface.get_list_by_id(db, list_id)
    if not list_obj or list_obj.group_id != group_id:
        raise NotFoundError(code="ITEM_NOT_FOUND", detail=f"Item {item_id} not found")
    item = await interface.update_item(
        db,
        item_id=item_id,
        name=data.name,
        quantity_value=data.quantity_value,
        quantity_unit=data.quantity_unit,
        is_checked=data.is_checked,
        price_estimate=data.price_estimate,
        priority=data.priority,
        notes=data.notes,
    )
    return schemas.ItemResponse.model_validate(item)


@router.delete("/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list_item(
    list_id: int,
    item_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove item from list."""
    item = await interface.get_item_by_id(db, item_id)
    if not item or item.list_id != list_id:
        raise NotFoundError(code="ITEM_NOT_FOUND", detail=f"Item {item_id} not found")
    list_obj = await interface.get_list_by_id(db, list_id)
    if not list_obj or list_obj.group_id != group_id:
        raise NotFoundError(code="ITEM_NOT_FOUND", detail=f"Item {item_id} not found")
    await interface.delete_item(db, item_id)


@router.post(
    "/{list_id}/items/bulk",
    response_model=schemas.ItemBulkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def bulk_add_list_items(
    list_id: int,
    data: schemas.ItemBulkCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ItemBulkResponse:
    """Add multiple items to list (e.g. from recipe)."""
    list_obj = await interface.get_list_by_id(db, list_id)
    if not list_obj or list_obj.group_id != group_id:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")
    items_data = [i.model_dump() for i in data.items]
    created = await interface.bulk_add_items(db, list_id, items_data)
    return schemas.ItemBulkResponse(items=[schemas.ItemResponse.model_validate(i) for i in created])


# ---------- Inventory ----------
@inventory_router.get("", response_model=ListType[schemas.InventoryItemResponse])
async def get_inventory(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.InventoryItemResponse]:
    """List current pantry/household inventory for a group."""
    items = await interface.list_inventory(db, group_id)
    return [schemas.InventoryItemResponse.model_validate(i) for i in items]


@inventory_router.patch("/{inventory_id}", response_model=schemas.InventoryItemResponse)
async def patch_inventory_item(
    inventory_id: int,
    data: schemas.InventoryItemUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.InventoryItemResponse:
    """Update quantity or mark out of stock."""
    inv = await interface.get_inventory_item_by_id(db, inventory_id)
    if not inv or inv.group_id != group_id:
        raise NotFoundError(code="INVENTORY_ITEM_NOT_FOUND", detail=f"Inventory item {inventory_id} not found")
    inv = await interface.update_inventory_item(
        db,
        inventory_id=inventory_id,
        quantity_value=data.quantity_value,
        quantity_unit=data.quantity_unit,
        expiration_date=data.expiration_date,
        opened_date=data.opened_date,
        restock_threshold=data.restock_threshold,
    )
    return schemas.InventoryItemResponse.model_validate(inv)

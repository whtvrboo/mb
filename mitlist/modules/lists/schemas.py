"""Lists module Pydantic schemas for request/response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ListBase(BaseModel):
    """Base list schema."""

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(SHOPPING|TODO)$")
    deadline: datetime | None = None
    store_name: str | None = Field(None, max_length=255)
    estimated_total: float | None = Field(None, ge=0)


class ListCreate(ListBase):
    """Schema for creating a list."""

    group_id: int


class ListUpdate(BaseModel):
    """Schema for updating a list."""

    name: str | None = Field(None, min_length=1, max_length=255)
    deadline: datetime | None = None
    store_name: str | None = Field(None, max_length=255)
    estimated_total: float | None = Field(None, ge=0)
    is_archived: bool | None = None


class ListResponse(ListBase):
    """Schema for list response - returned directly, no envelope."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_by_id: int | None = None
    is_archived: bool
    archived_at: datetime | None = None
    version_id: int
    created_at: datetime
    updated_at: datetime


class ItemBase(BaseModel):
    """Base item schema."""

    name: str = Field(..., min_length=1, max_length=255)
    quantity_value: float | None = Field(None, ge=0)
    quantity_unit: str | None = Field(None, max_length=50)
    is_checked: bool = False
    price_estimate: float | None = Field(None, ge=0)
    priority: str | None = Field(None, pattern="^(HIGH|MEDIUM|LOW)$")
    notes: str | None = Field(None, max_length=1000)


class ItemCreate(ItemBase):
    """Schema for creating an item."""

    list_id: int


class ItemUpdate(BaseModel):
    """Schema for updating an item."""

    name: str | None = Field(None, min_length=1, max_length=255)
    quantity_value: float | None = Field(None, ge=0)
    quantity_unit: str | None = Field(None, max_length=50)
    is_checked: bool | None = None
    checked_at: datetime | None = None
    price_estimate: float | None = Field(None, ge=0)
    priority: str | None = Field(None, pattern="^(HIGH|MEDIUM|LOW)$")
    notes: str | None = Field(None, max_length=1000)


class ItemResponse(ItemBase):
    """Schema for item response - returned directly, no envelope."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    list_id: int
    checked_at: datetime | None = None
    added_by_id: int | None = None
    assigned_to_id: int | None = None
    version_id: int
    created_at: datetime
    updated_at: datetime


class ItemBulkCreate(BaseModel):
    """Schema for bulk-adding items to a list."""

    items: list[ItemBase] = Field(..., min_length=1, max_length=100)


class ItemBulkResponse(BaseModel):
    """Schema for bulk-add response - list of created items."""

    items: list[ItemResponse]


# ====================
# InventoryItem Schemas
# ====================
class InventoryItemBase(BaseModel):
    """Base inventory item schema."""

    quantity_value: float | None = Field(None, ge=0)
    quantity_unit: str | None = Field(None, max_length=50)
    expiration_date: datetime | None = None
    opened_date: datetime | None = None
    restock_threshold: float | None = Field(None, ge=0)


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating an inventory item."""

    group_id: int
    location_id: int | None = None
    concept_id: int | None = None


class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item (quantity, mark out of stock)."""

    quantity_value: float | None = Field(None, ge=0)
    quantity_unit: str | None = Field(None, max_length=50)
    expiration_date: datetime | None = None
    opened_date: datetime | None = None
    restock_threshold: float | None = Field(None, ge=0)


class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    location_id: int | None = None
    concept_id: int | None = None
    created_at: datetime
    updated_at: datetime

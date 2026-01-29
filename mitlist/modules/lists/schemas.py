"""Lists module Pydantic schemas for request/response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ListBase(BaseModel):
    """Base list schema."""

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(SHOPPING|TODO)$")
    deadline: Optional[datetime] = None
    store_name: Optional[str] = Field(None, max_length=255)
    estimated_total: Optional[float] = Field(None, ge=0)


class ListCreate(ListBase):
    """Schema for creating a list."""

    group_id: int


class ListUpdate(BaseModel):
    """Schema for updating a list."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    deadline: Optional[datetime] = None
    store_name: Optional[str] = Field(None, max_length=255)
    estimated_total: Optional[float] = Field(None, ge=0)
    is_archived: Optional[bool] = None


class ListResponse(ListBase):
    """Schema for list response - returned directly, no envelope."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_by_id: Optional[int] = None
    is_archived: bool
    archived_at: Optional[datetime] = None
    version_id: int
    created_at: datetime
    updated_at: datetime


class ItemBase(BaseModel):
    """Base item schema."""

    name: str = Field(..., min_length=1, max_length=255)
    quantity_value: Optional[float] = Field(None, ge=0)
    quantity_unit: Optional[str] = Field(None, max_length=50)
    is_checked: bool = False
    price_estimate: Optional[float] = Field(None, ge=0)
    priority: Optional[str] = Field(None, pattern="^(HIGH|MEDIUM|LOW)$")
    notes: Optional[str] = None


class ItemCreate(ItemBase):
    """Schema for creating an item."""

    list_id: int


class ItemUpdate(BaseModel):
    """Schema for updating an item."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity_value: Optional[float] = Field(None, ge=0)
    quantity_unit: Optional[str] = Field(None, max_length=50)
    is_checked: Optional[bool] = None
    checked_at: Optional[datetime] = None
    price_estimate: Optional[float] = Field(None, ge=0)
    priority: Optional[str] = Field(None, pattern="^(HIGH|MEDIUM|LOW)$")
    notes: Optional[str] = None


class ItemResponse(ItemBase):
    """Schema for item response - returned directly, no envelope."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    list_id: int
    checked_at: Optional[datetime] = None
    added_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    version_id: int
    created_at: datetime
    updated_at: datetime


class ItemBulkCreate(BaseModel):
    """Schema for bulk-adding items to a list."""

    items: list[ItemBase] = Field(..., min_length=1)


class ItemBulkResponse(BaseModel):
    """Schema for bulk-add response - list of created items."""

    items: list[ItemResponse]


# ====================
# InventoryItem Schemas
# ====================
class InventoryItemBase(BaseModel):
    """Base inventory item schema."""

    quantity_value: Optional[float] = Field(None, ge=0)
    quantity_unit: Optional[str] = Field(None, max_length=50)
    expiration_date: Optional[datetime] = None
    opened_date: Optional[datetime] = None
    restock_threshold: Optional[float] = Field(None, ge=0)


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating an inventory item."""

    group_id: int
    location_id: Optional[int] = None
    concept_id: Optional[int] = None


class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item (quantity, mark out of stock)."""

    quantity_value: Optional[float] = Field(None, ge=0)
    quantity_unit: Optional[str] = Field(None, max_length=50)
    expiration_date: Optional[datetime] = None
    opened_date: Optional[datetime] = None
    restock_threshold: Optional[float] = Field(None, ge=0)


class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    location_id: Optional[int] = None
    concept_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

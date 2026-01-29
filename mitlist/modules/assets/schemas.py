"""Assets module Pydantic schemas for request/response models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ====================
# HomeAsset Schemas
# ====================
class HomeAssetBase(BaseModel):
    """Base home asset schema."""

    name: str = Field(..., min_length=1, max_length=255)
    asset_type: str = Field(
        ...,
        pattern="^(APPLIANCE|HVAC|PLUMBING|ELECTRICAL|FURNITURE|ELECTRONICS|OTHER)$",
    )
    location_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=255)
    model_number: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    purchase_store: Optional[str] = Field(None, max_length=255)
    warranty_end_date: Optional[datetime] = None
    warranty_type: Optional[str] = Field(
        None, pattern="^(MANUFACTURER|EXTENDED|NONE)$"
    )
    energy_rating: Optional[str] = Field(None, max_length=10)
    photo_url: Optional[str] = Field(None, max_length=500)


class HomeAssetCreate(HomeAssetBase):
    """Schema for creating a home asset."""

    group_id: int
    manual_document_id: Optional[int] = None
    receipt_document_id: Optional[int] = None
    service_contact_id: Optional[int] = None


class HomeAssetUpdate(BaseModel):
    """Schema for updating a home asset."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    asset_type: Optional[str] = Field(
        None,
        pattern="^(APPLIANCE|HVAC|PLUMBING|ELECTRICAL|FURNITURE|ELECTRONICS|OTHER)$",
    )
    location_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=255)
    model_number: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    purchase_store: Optional[str] = Field(None, max_length=255)
    warranty_end_date: Optional[datetime] = None
    warranty_type: Optional[str] = Field(
        None, pattern="^(MANUFACTURER|EXTENDED|NONE)$"
    )
    energy_rating: Optional[str] = Field(None, max_length=10)
    photo_url: Optional[str] = Field(None, max_length=500)
    manual_document_id: Optional[int] = None
    receipt_document_id: Optional[int] = None
    service_contact_id: Optional[int] = None
    is_active: Optional[bool] = None


class HomeAssetDisposeRequest(BaseModel):
    """Schema for disposing of an asset."""

    disposed_at: datetime = Field(default_factory=datetime.utcnow)


class HomeAssetResponse(HomeAssetBase):
    """Schema for home asset response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    manual_document_id: Optional[int] = None
    receipt_document_id: Optional[int] = None
    service_contact_id: Optional[int] = None
    is_active: bool
    disposed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ====================
# MaintenanceTask Schemas
# ====================
class MaintenanceTaskBase(BaseModel):
    """Base maintenance task schema."""

    name: str = Field(..., min_length=1, max_length=255)
    frequency_days: int = Field(..., ge=1)
    priority: Optional[str] = Field(
        None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$"
    )
    instructions: Optional[str] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    estimated_cost: Optional[float] = Field(None, ge=0)


class MaintenanceTaskCreate(MaintenanceTaskBase):
    """Schema for creating a maintenance task."""

    asset_id: int
    required_item_concept_id: Optional[int] = None


class MaintenanceTaskUpdate(BaseModel):
    """Schema for updating a maintenance task."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    frequency_days: Optional[int] = Field(None, ge=1)
    priority: Optional[str] = Field(
        None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$"
    )
    instructions: Optional[str] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    estimated_cost: Optional[float] = Field(None, ge=0)
    required_item_concept_id: Optional[int] = None
    is_active: Optional[bool] = None


class MaintenanceTaskResponse(MaintenanceTaskBase):
    """Schema for maintenance task response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    last_completed_at: Optional[datetime] = None
    next_due_date: Optional[datetime] = None
    required_item_concept_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ====================
# MaintenanceLog Schemas
# ====================
class MaintenanceLogBase(BaseModel):
    """Base maintenance log schema."""

    completed_at: datetime
    actual_duration_minutes: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)


class MaintenanceLogCreate(MaintenanceLogBase):
    """Schema for creating a maintenance log."""

    task_id: int
    cost_expense_id: Optional[int] = None


class MaintenanceLogResponse(MaintenanceLogBase):
    """Schema for maintenance log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user_id: int
    cost_expense_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class MaintenanceCompleteRequest(BaseModel):
    """Schema for completing a maintenance task."""

    actual_duration_minutes: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    cost_expense_id: Optional[int] = None


# ====================
# AssetInsurance Schemas
# ====================
class AssetInsuranceBase(BaseModel):
    """Base asset insurance schema."""

    policy_number: str = Field(..., min_length=1, max_length=100)
    provider_name: str = Field(..., min_length=1, max_length=255)
    coverage_type: str = Field(
        ..., pattern="^(RENTERS|HOMEOWNERS|VEHICLE|OTHER)$"
    )
    premium_amount: float = Field(..., ge=0)
    premium_frequency: str = Field(..., pattern="^(MONTHLY|YEARLY)$")
    start_date: datetime
    end_date: Optional[datetime] = None
    deductible_amount: Optional[float] = Field(None, ge=0)


class AssetInsuranceCreate(AssetInsuranceBase):
    """Schema for creating asset insurance."""

    group_id: int
    document_id: Optional[int] = None


class AssetInsuranceUpdate(BaseModel):
    """Schema for updating asset insurance."""

    policy_number: Optional[str] = Field(None, min_length=1, max_length=100)
    provider_name: Optional[str] = Field(None, min_length=1, max_length=255)
    coverage_type: Optional[str] = Field(
        None, pattern="^(RENTERS|HOMEOWNERS|VEHICLE|OTHER)$"
    )
    premium_amount: Optional[float] = Field(None, ge=0)
    premium_frequency: Optional[str] = Field(None, pattern="^(MONTHLY|YEARLY)$")
    end_date: Optional[datetime] = None
    deductible_amount: Optional[float] = Field(None, ge=0)
    document_id: Optional[int] = None


class AssetInsuranceResponse(AssetInsuranceBase):
    """Schema for asset insurance response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# ====================
# Aggregation/Summary Schemas
# ====================
class AssetMaintenanceStatusResponse(BaseModel):
    """Schema for asset maintenance status."""

    asset_id: int
    asset_name: str
    asset_type: str
    is_active: bool
    warranty_status: str  # ACTIVE, EXPIRED, NONE
    warranty_days_remaining: Optional[int] = None
    overdue_tasks: list[dict]  # task_id, name, days_overdue
    upcoming_tasks: list[dict]  # task_id, name, due_date
    last_maintenance_at: Optional[datetime] = None


class GroupAssetSummaryResponse(BaseModel):
    """Schema for group asset summary."""

    group_id: int
    total_assets: int
    active_assets: int
    disposed_assets: int
    assets_by_type: dict[str, int]
    assets_needing_maintenance: int
    expiring_warranties_count: int
    total_asset_value: Optional[float] = None


class WarrantyAlertResponse(BaseModel):
    """Schema for warranty expiration alert."""

    asset_id: int
    asset_name: str
    warranty_type: str
    expires_at: datetime
    days_until_expiry: int
    is_expired: bool
    service_contact_id: Optional[int] = None


class MaintenanceScheduleResponse(BaseModel):
    """Schema for maintenance schedule."""

    group_id: int
    upcoming_tasks: list[dict]  # asset_id, asset_name, task_id, task_name, due_date
    overdue_tasks: list[dict]  # Same structure with days_overdue
    completed_this_month: int
    total_estimated_cost_upcoming: Optional[float] = None

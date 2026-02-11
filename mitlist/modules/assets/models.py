"""Assets module ORM models."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import BaseModel, TimestampMixin


class AssetType(str):
    """Asset types."""

    APPLIANCE = "APPLIANCE"
    HVAC = "HVAC"
    PLUMBING = "PLUMBING"
    ELECTRICAL = "ELECTRICAL"
    FURNITURE = "FURNITURE"
    ELECTRONICS = "ELECTRONICS"
    OTHER = "OTHER"


class WarrantyType(str):
    """Warranty types."""

    MANUFACTURER = "MANUFACTURER"
    EXTENDED = "EXTENDED"
    NONE = "NONE"


class Priority(str):
    """Priority levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CoverageType(str):
    """Insurance coverage types."""

    RENTERS = "RENTERS"
    HOMEOWNERS = "HOMEOWNERS"
    VEHICLE = "VEHICLE"
    OTHER = "OTHER"


class PremiumFrequency(str):
    """Premium frequency."""

    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class HomeAsset(BaseModel, TimestampMixin):
    """Home asset - appliance, furniture, etc."""

    __tablename__ = "home_assets"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purchase_date: Mapped[datetime | None] = mapped_column(nullable=True)
    purchase_price: Mapped[float | None] = mapped_column(nullable=True)
    purchase_store: Mapped[str | None] = mapped_column(String(255), nullable=True)
    warranty_end_date: Mapped[datetime | None] = mapped_column(nullable=True)
    warranty_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    energy_rating: Mapped[str | None] = mapped_column(String(10), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    manual_document_id: Mapped[int | None] = mapped_column(nullable=True)  # FK to documents
    receipt_document_id: Mapped[int | None] = mapped_column(nullable=True)  # FK to documents
    service_contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_contacts.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    disposed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    maintenance_tasks: Mapped[list["MaintenanceTask"]] = relationship(
        "MaintenanceTask", back_populates="asset", cascade="all, delete-orphan"
    )


class MaintenanceTask(BaseModel, TimestampMixin):
    """Maintenance task - recurring maintenance for an asset."""

    __tablename__ = "maintenance_tasks"

    asset_id: Mapped[int] = mapped_column(ForeignKey("home_assets.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    frequency_days: Mapped[int] = mapped_column(nullable=False)
    last_completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    next_due_date: Mapped[datetime | None] = mapped_column(nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(nullable=True)
    required_item_concept_id: Mapped[int | None] = mapped_column(
        ForeignKey("common_item_concepts.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    asset: Mapped["HomeAsset"] = relationship("HomeAsset", back_populates="maintenance_tasks")
    logs: Mapped[list["MaintenanceLog"]] = relationship(
        "MaintenanceLog", back_populates="task", cascade="all, delete-orphan"
    )


class MaintenanceLog(BaseModel, TimestampMixin):
    """Maintenance log - completed maintenance record."""

    __tablename__ = "maintenance_logs"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("maintenance_tasks.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(nullable=False)
    actual_duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    cost_expense_id: Mapped[int | None] = mapped_column(nullable=True)  # FK to expenses
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quality_rating: Mapped[int | None] = mapped_column(nullable=True)

    # Relationships
    task: Mapped["MaintenanceTask"] = relationship("MaintenanceTask", back_populates="logs")

    __table_args__ = (
        CheckConstraint(
            "quality_rating IS NULL OR (quality_rating >= 1 AND quality_rating <= 5)",
            name="ck_maintenance_rating",
        ),
    )


class AssetInsurance(BaseModel, TimestampMixin):
    """Asset insurance - insurance policies."""

    __tablename__ = "asset_insurances"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    policy_number: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(255), nullable=False)
    coverage_type: Mapped[str] = mapped_column(String(50), nullable=False)
    premium_amount: Mapped[float] = mapped_column(nullable=False)
    premium_frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(nullable=True)
    deductible_amount: Mapped[float | None] = mapped_column(nullable=True)
    document_id: Mapped[int | None] = mapped_column(nullable=True)  # FK to documents

    __table_args__ = (
        CheckConstraint("premium_amount >= 0", name="ck_insurance_premium_non_negative"),
    )

"""Chores module ORM models."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import BaseModel, TimestampMixin


class FrequencyType(str):
    """Chore frequency types."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"
    SEASONAL = "SEASONAL"


class ChoreCategory(str):
    """Chore categories."""

    CLEANING = "CLEANING"
    OUTDOOR = "OUTDOOR"
    MAINTENANCE = "MAINTENANCE"
    ADMIN = "ADMIN"
    OTHER = "OTHER"


class RotationStrategy(str):
    """Rotation strategies."""

    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_BUSY = "LEAST_BUSY"
    RANDOM = "RANDOM"


class ChoreAssignmentStatus(str):
    """Chore assignment status."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class DependencyType(str):
    """Chore dependency types."""

    BLOCKING = "BLOCKING"
    SUGGESTED = "SUGGESTED"


class Chore(BaseModel, TimestampMixin):
    """Chore template - recurring task definition."""

    __tablename__ = "chores"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency_type: Mapped[str] = mapped_column(String(20), nullable=False)
    interval_value: Mapped[int] = mapped_column(default=1, nullable=False)
    effort_value: Mapped[int] = mapped_column(nullable=False)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    required_item_concept_id: Mapped[int | None] = mapped_column(
        ForeignKey("common_item_concepts.id"), nullable=True
    )
    is_rotating: Mapped[bool] = mapped_column(default=False, nullable=False)
    rotation_strategy: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    assignments: Mapped[list["ChoreAssignment"]] = relationship(
        "ChoreAssignment", back_populates="chore", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_chores_group_active", "group_id", "is_active"),
    )


class ChoreAssignment(BaseModel, TimestampMixin):
    """Chore assignment - specific instance of a chore."""

    __tablename__ = "chore_assignments"

    chore_id: Mapped[int] = mapped_column(ForeignKey("chores.id"), nullable=False)
    assigned_to_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    due_date: Mapped[datetime] = mapped_column(nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    actual_duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    quality_rating: Mapped[int | None] = mapped_column(nullable=True)
    rated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    attachment_id: Mapped[int | None] = mapped_column(nullable=True)  # FK to documents
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    chore: Mapped["Chore"] = relationship("Chore", back_populates="assignments")

    __table_args__ = (
        CheckConstraint("quality_rating IS NULL OR (quality_rating >= 1 AND quality_rating <= 5)", name="ck_chore_rating"),
        Index("ix_chore_assignments_chore_status_due", "chore_id", "status", "due_date"),
        Index("ix_chore_assignments_assigned_status_due", "assigned_to_id", "status", "due_date"),
    )


class ChoreDependency(BaseModel, TimestampMixin):
    """Chore dependency - chore X must be done before Y."""

    __tablename__ = "chore_dependencies"

    chore_id: Mapped[int] = mapped_column(ForeignKey("chores.id"), nullable=False)
    depends_on_chore_id: Mapped[int] = mapped_column(ForeignKey("chores.id"), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(20), nullable=False)  # BLOCKING, SUGGESTED


class ChoreTemplate(BaseModel, TimestampMixin):
    """Chore template - marketplace/library of common chores."""

    __tablename__ = "chore_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency_type: Mapped[str] = mapped_column(String(20), nullable=False)
    interval_value: Mapped[int] = mapped_column(default=1, nullable=False)
    effort_value: Mapped[int] = mapped_column(nullable=False)
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_public: Mapped[bool] = mapped_column(default=False, nullable=False)
    use_count: Mapped[int] = mapped_column(default=0, nullable=False)

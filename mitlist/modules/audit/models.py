"""Audit module ORM models."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from mitlist.db.base import BaseModel, TimestampMixin


class Action(str):
    """Audit log actions."""

    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    VIEWED = "VIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ReportType(str):
    """Report types."""

    MONTHLY_EXPENSES = "MONTHLY_EXPENSES"
    CHORE_COMPLETION = "CHORE_COMPLETION"
    BUDGET_STATUS = "BUDGET_STATUS"


class AuditLog(BaseModel, TimestampMixin):
    """Audit log - track all changes."""

    __tablename__ = "audit_logs"

    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(nullable=False, index=True)
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(nullable=False)

    __table_args__ = (
        Index("ix_audit_logs_group_occurred", "group_id", "occurred_at"),
    )


class ReportSnapshot(BaseModel, TimestampMixin):
    """Report snapshot - pre-computed reports."""

    __tablename__ = "report_snapshots"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    period_start_date: Mapped[datetime] = mapped_column(nullable=False)
    period_end_date: Mapped[datetime] = mapped_column(nullable=False)
    data_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(nullable=False)


class Tag(BaseModel, TimestampMixin):
    """Tag - universal tagging system."""

    __tablename__ = "tags"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color_hex: Mapped[str | None] = mapped_column(String(7), nullable=True)


class TagAssignment(BaseModel, TimestampMixin):
    """Tag assignment - tag an entity."""

    __tablename__ = "tag_assignments"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(nullable=False, index=True)

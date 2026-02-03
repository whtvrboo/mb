"""Finance module ORM models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Index,
    JSON,
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import Base, BaseModel, TimestampMixin, VersionMixin


class PaymentMethod(str, Enum):
    """Payment method enumeration."""

    CARD = "CARD"
    CASH = "CASH"
    TRANSFER = "TRANSFER"
    OTHER = "OTHER"


class SettlementMethod(str, Enum):
    """Settlement method enumeration."""

    CASH = "CASH"
    VENMO = "VENMO"
    ZELLE = "ZELLE"
    BANK_TRANSFER = "BANK_TRANSFER"


class FrequencyType(str, Enum):
    """Frequency type for recurring expenses."""

    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


class SplitMethod(str, Enum):
    """Split preset method."""

    EQUAL = "EQUAL"
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    BY_INCOME = "BY_INCOME"


class PeriodType(str, Enum):
    """Budget period type."""

    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class Category(BaseModel, TimestampMixin):
    """Expense category - can be global (group_id=null) or group-specific."""

    __tablename__ = "categories"

    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon_emoji: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    color_hex: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    parent_category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    is_income: Mapped[bool] = mapped_column(default=False, nullable=False)


class Expense(BaseModel, TimestampMixin, VersionMixin):
    """Expense model with splits and links to other entities."""

    __tablename__ = "expenses"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    paid_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    receipt_img_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    expense_date: Mapped[datetime] = mapped_column(nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_reimbursable: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_recurring_generated: Mapped[bool] = mapped_column(default=False, nullable=False)
    linked_proposal_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # FK to proposals
    linked_pet_medical_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # FK to pet_medical_records
    linked_maintenance_log_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # FK to maintenance_logs
    linked_recurring_expense_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recurring_expenses.id"), nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    version_id: Mapped[int] = mapped_column(nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version_id}

    # Relationships
    splits: Mapped[list["ExpenseSplit"]] = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_expense_amount_positive"),
        # Optimization: Composite index for efficient querying by group_id and sorting by expense_date
        Index("ix_expenses_group_date", "group_id", "expense_date"),
        # Optimization: Composite index for efficient budget calc (filter by category, sort by date)
        Index("ix_expenses_group_category_date", "group_id", "category_id", "expense_date"),
        # Optimization: Composite index for efficient user filtering (filter by user, sort by date)
        Index("ix_expenses_group_user_date", "group_id", "paid_by_user_id", "expense_date"),
    )


class ExpenseSplit(BaseModel, TimestampMixin):
    """Expense split - how much each user owes for an expense."""

    __tablename__ = "expense_splits"

    expense_id: Mapped[int] = mapped_column(ForeignKey("expenses.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owed_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_paid: Mapped[bool] = mapped_column(default=False, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    manual_override: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    expense: Mapped["Expense"] = relationship("Expense", back_populates="splits")

    __table_args__ = (
        CheckConstraint("owed_amount >= 0", name="ck_expense_split_amount_non_negative"),
    )


class RecurringExpense(BaseModel, TimestampMixin):
    """Recurring expense template (subscriptions, rent, etc.)."""

    __tablename__ = "recurring_expenses"
    __table_args__ = (
        # Optimization: Composite index for efficient querying by group_id and sorting by next_due_date
        Index("ix_recurring_expenses_group_next_due", "group_id", "next_due_date"),
    )

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    paid_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    frequency_type: Mapped[str] = mapped_column(String(20), nullable=False)  # WEEKLY, MONTHLY, YEARLY, CUSTOM
    interval_value: Mapped[int] = mapped_column(default=1, nullable=False)
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    next_due_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    auto_create_expense: Mapped[bool] = mapped_column(default=True, nullable=False)
    split_preset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("split_presets.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Settlement(BaseModel, TimestampMixin):
    """Settlement between users - payment record."""

    __tablename__ = "settlements"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    payer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    payee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)  # CASH, VENMO, ZELLE, BANK_TRANSFER
    settled_at: Mapped[datetime] = mapped_column(nullable=False)
    confirmation_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_settlement_amount_positive"),
        # Optimization: Composite index for efficient querying by group_id and sorting by settled_at
        Index("ix_settlements_group_date", "group_id", "settled_at"),
    )


class SplitPreset(BaseModel, TimestampMixin):
    """Split preset - reusable split configuration."""

    __tablename__ = "split_presets"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)  # EQUAL, PERCENTAGE, FIXED_AMOUNT, BY_INCOME

    # Relationships
    members: Mapped[list["SplitPresetMember"]] = relationship(
        "SplitPresetMember", back_populates="preset", cascade="all, delete-orphan"
    )


class SplitPresetMember(BaseModel, TimestampMixin):
    """Split preset member configuration."""

    __tablename__ = "split_preset_members"

    preset_id: Mapped[int] = mapped_column(ForeignKey("split_presets.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    fixed_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Relationships
    preset: Mapped["SplitPreset"] = relationship("SplitPreset", back_populates="members")

    __table_args__ = (
        UniqueConstraint("preset_id", "user_id", name="uq_split_preset_member"),
    )


class Budget(BaseModel, TimestampMixin):
    """Budget - spending limit per category."""

    __tablename__ = "budgets"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    amount_limit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)  # WEEKLY, MONTHLY, YEARLY
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    alert_threshold_percentage: Mapped[int] = mapped_column(default=80, nullable=False)

    __table_args__ = (
        CheckConstraint("amount_limit > 0", name="ck_budget_amount_positive"),
        CheckConstraint("alert_threshold_percentage BETWEEN 0 AND 100", name="ck_budget_threshold"),
    )


class BalanceSnapshot(BaseModel, TimestampMixin):
    """Balance snapshot - pre-computed user balances for performance."""

    __tablename__ = "balance_snapshots"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    balance_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    snapshot_date: Mapped[datetime] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", "snapshot_date", name="uq_balance_snapshot"),
    )

"""Finance module Pydantic schemas for request/response models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ====================
# Category Schemas
# ====================
class CategoryBase(BaseModel):
    """Base category schema."""

    name: str = Field(..., min_length=1, max_length=255)
    icon_emoji: Optional[str] = Field(None, max_length=10)
    color_hex: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    parent_category_id: Optional[int] = None
    is_income: bool = False


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    group_id: Optional[int] = None  # null = global category


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    icon_emoji: Optional[str] = Field(None, max_length=10)
    color_hex: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    parent_category_id: Optional[int] = None
    is_income: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# ====================
# Expense Schemas
# ====================
class ExpenseSplitInput(BaseModel):
    """Input schema for expense split when creating an expense."""

    user_id: int
    owed_amount: Decimal = Field(..., ge=0)
    manual_override: Optional[dict] = None


class ExpenseBase(BaseModel):
    """Base expense schema."""

    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    currency_code: str = Field("USD", max_length=3, pattern="^[A-Z]{3}$")
    category_id: int
    expense_date: datetime
    payment_method: Optional[str] = Field(
        None, pattern="^(CARD|CASH|TRANSFER|OTHER)$"
    )
    vendor_name: Optional[str] = Field(None, max_length=255)
    receipt_img_url: Optional[str] = Field(None, max_length=500)
    is_reimbursable: bool = False


class ExpenseCreate(ExpenseBase):
    """Schema for creating an expense."""

    group_id: int
    paid_by_user_id: int
    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    splits: list[ExpenseSplitInput] = Field(default_factory=list, max_length=100)
    linked_proposal_id: Optional[int] = None
    linked_pet_medical_id: Optional[int] = None
    linked_maintenance_log_id: Optional[int] = None


class ExpenseCreateRequest(ExpenseBase):
    """Request schema for creating expense (omits group_id and paid_by_user_id)."""

    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    splits: list[ExpenseSplitInput] = Field(default_factory=list, max_length=100)
    linked_proposal_id: Optional[int] = None
    linked_pet_medical_id: Optional[int] = None
    linked_maintenance_log_id: Optional[int] = None


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    currency_code: Optional[str] = Field(None, max_length=3, pattern="^[A-Z]{3}$")
    category_id: Optional[int] = None
    expense_date: Optional[datetime] = None
    payment_method: Optional[str] = Field(
        None, pattern="^(CARD|CASH|TRANSFER|OTHER)$"
    )
    vendor_name: Optional[str] = Field(None, max_length=255)
    receipt_img_url: Optional[str] = Field(None, max_length=500)
    is_reimbursable: Optional[bool] = None
    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    version_id: int  # Required for optimistic locking


class ExpenseSplitResponse(BaseModel):
    """Schema for expense split response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    expense_id: int
    user_id: int
    owed_amount: Decimal
    is_paid: bool
    paid_at: Optional[datetime] = None
    manual_override: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class ExpenseResponse(ExpenseBase):
    """Schema for expense response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    paid_by_user_id: int
    exchange_rate: Optional[Decimal] = None
    is_recurring_generated: bool
    linked_proposal_id: Optional[int] = None
    linked_pet_medical_id: Optional[int] = None
    linked_maintenance_log_id: Optional[int] = None
    linked_recurring_expense_id: Optional[int] = None
    version_id: int
    created_at: datetime
    updated_at: datetime
    splits: list[ExpenseSplitResponse] = Field(default_factory=list)


# ====================
# RecurringExpense Schemas
# ====================
class RecurringExpenseBase(BaseModel):
    """Base recurring expense schema."""

    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    currency_code: str = Field("USD", max_length=3, pattern="^[A-Z]{3}$")
    category_id: int
    frequency_type: str = Field(..., pattern="^(WEEKLY|MONTHLY|YEARLY|CUSTOM)$")
    interval_value: int = Field(1, ge=1)
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_create_expense: bool = True


class RecurringExpenseCreate(RecurringExpenseBase):
    """Schema for creating a recurring expense."""

    group_id: int
    paid_by_user_id: int
    split_preset_id: Optional[int] = None


class RecurringExpenseCreateRequest(RecurringExpenseBase):
    """Request schema for creating recurring expense (omits group_id and paid_by_user_id)."""

    split_preset_id: Optional[int] = None


class RecurringExpenseUpdate(BaseModel):
    """Schema for updating a recurring expense."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    currency_code: Optional[str] = Field(None, max_length=3, pattern="^[A-Z]{3}$")
    category_id: Optional[int] = None
    frequency_type: Optional[str] = Field(
        None, pattern="^(WEEKLY|MONTHLY|YEARLY|CUSTOM)$"
    )
    interval_value: Optional[int] = Field(None, ge=1)
    end_date: Optional[datetime] = None
    auto_create_expense: Optional[bool] = None
    split_preset_id: Optional[int] = None
    is_active: Optional[bool] = None


class RecurringExpenseResponse(RecurringExpenseBase):
    """Schema for recurring expense response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    paid_by_user_id: int
    next_due_date: Optional[datetime] = None
    split_preset_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ====================
# Settlement Schemas
# ====================
class SettlementBase(BaseModel):
    """Base settlement schema."""

    amount: Decimal = Field(..., gt=0)
    currency_code: str = Field("USD", max_length=3, pattern="^[A-Z]{3}$")
    method: str = Field(..., pattern="^(CASH|VENMO|ZELLE|BANK_TRANSFER)$")
    settled_at: datetime
    confirmation_code: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class SettlementCreate(SettlementBase):
    """Schema for creating a settlement."""

    group_id: int
    payer_id: int
    payee_id: int


class SettlementCreateRequest(SettlementBase):
    """Request schema for creating settlement (omits group_id, payer_id from auth)."""

    payee_id: int


class SettlementResponse(SettlementBase):
    """Schema for settlement response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    payer_id: int
    payee_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# SplitPreset Schemas
# ====================
class SplitPresetMemberInput(BaseModel):
    """Input schema for split preset member."""

    user_id: int
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    fixed_amount: Optional[Decimal] = Field(None, ge=0)


class SplitPresetBase(BaseModel):
    """Base split preset schema."""

    name: str = Field(..., min_length=1, max_length=255)
    is_default: bool = False
    method: str = Field(
        ..., pattern="^(EQUAL|PERCENTAGE|FIXED_AMOUNT|BY_INCOME)$"
    )


class SplitPresetCreate(SplitPresetBase):
    """Schema for creating a split preset."""

    group_id: int
    members: list[SplitPresetMemberInput] = Field(default_factory=list, max_length=100)


class SplitPresetCreateRequest(SplitPresetBase):
    """Request schema for creating split preset (omits group_id)."""

    members: list[SplitPresetMemberInput] = Field(default_factory=list, max_length=100)


class SplitPresetUpdate(BaseModel):
    """Schema for updating a split preset."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_default: Optional[bool] = None
    method: Optional[str] = Field(
        None, pattern="^(EQUAL|PERCENTAGE|FIXED_AMOUNT|BY_INCOME)$"
    )
    members: Optional[list[SplitPresetMemberInput]] = Field(None, max_length=100)


class SplitPresetMemberResponse(BaseModel):
    """Schema for split preset member response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    preset_id: int
    user_id: int
    percentage: Optional[Decimal] = None
    fixed_amount: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime


class SplitPresetResponse(SplitPresetBase):
    """Schema for split preset response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime
    members: list[SplitPresetMemberResponse] = Field(default_factory=list)


# ====================
# Budget Schemas
# ====================
class BudgetBase(BaseModel):
    """Base budget schema."""

    category_id: int
    amount_limit: Decimal = Field(..., gt=0)
    currency_code: str = Field("USD", max_length=3, pattern="^[A-Z]{3}$")
    period_type: str = Field(..., pattern="^(WEEKLY|MONTHLY|YEARLY)$")
    start_date: datetime
    end_date: Optional[datetime] = None
    alert_threshold_percentage: int = Field(80, ge=0, le=100)


class BudgetCreate(BudgetBase):
    """Schema for creating a budget."""

    group_id: int


class BudgetCreateRequest(BudgetBase):
    """Request schema for creating budget (omits group_id)."""

    pass


class BudgetUpdate(BaseModel):
    """Schema for updating a budget."""

    amount_limit: Optional[Decimal] = Field(None, gt=0)
    end_date: Optional[datetime] = None
    alert_threshold_percentage: Optional[int] = Field(None, ge=0, le=100)


class BudgetResponse(BudgetBase):
    """Schema for budget response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime


class BudgetStatusResponse(BudgetResponse):
    """Schema for budget with current spending status."""

    current_spent: Decimal = Field(default=Decimal("0.00"))
    remaining: Decimal = Field(default=Decimal("0.00"))
    percentage_used: float = Field(default=0.0)
    is_over_budget: bool = False
    is_alert_threshold_reached: bool = False


# ====================
# BalanceSnapshot Schemas
# ====================
class BalanceSnapshotBase(BaseModel):
    """Base balance snapshot schema."""

    balance_amount: Decimal
    currency_code: str = Field("USD", max_length=3, pattern="^[A-Z]{3}$")
    snapshot_date: datetime


class BalanceSnapshotCreate(BalanceSnapshotBase):
    """Schema for creating a balance snapshot."""

    group_id: int
    user_id: int


class BalanceSnapshotResponse(BalanceSnapshotBase):
    """Schema for balance snapshot response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# Aggregation/Summary Schemas
# ====================
class UserBalanceResponse(BaseModel):
    """Schema for user balance in a group."""

    user_id: int
    balance: Decimal  # Positive = owed by others, Negative = owes others
    currency_code: str


class GroupBalanceSummaryResponse(BaseModel):
    """Schema for group balance summary."""

    group_id: int
    balances: list[UserBalanceResponse]
    total_owed: Decimal
    currency_code: str


class ExpenseSummaryResponse(BaseModel):
    """Schema for expense summary."""

    total_amount: Decimal
    count: int
    by_category: dict[int, Decimal] = Field(default_factory=dict)
    by_user: dict[int, Decimal] = Field(default_factory=dict)
    period_start: datetime
    period_end: datetime

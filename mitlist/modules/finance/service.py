"""Finance module service layer - business logic. PRIVATE - other modules import from interface.py."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError, StaleDataError
from mitlist.modules.finance.models import Expense, ExpenseSplit


async def list_expenses(
    db: AsyncSession,
    group_id: int,
    user_id: Optional[int] = None,
    category_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Expense]:
    """List group expenses with optional filters."""
    q = (
        select(Expense)
        .where(Expense.group_id == group_id, Expense.deleted_at.is_(None))
        .options(selectinload(Expense.splits))
    )
    if user_id is not None:
        q = q.where(Expense.paid_by_user_id == user_id)
    if category_id is not None:
        q = q.where(Expense.category_id == category_id)
    if date_from is not None:
        q = q.where(Expense.expense_date >= date_from)
    if date_to is not None:
        q = q.where(Expense.expense_date <= date_to)
    q = q.order_by(Expense.expense_date.desc(), Expense.id.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_expense_by_id(db: AsyncSession, expense_id: int) -> Optional[Expense]:
    """Get expense by ID with splits."""
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .where(Expense.id == expense_id, Expense.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def create_expense(
    db: AsyncSession,
    group_id: int,
    paid_by_user_id: int,
    description: str,
    amount: Decimal,
    category_id: int,
    expense_date: datetime,
    currency_code: str = "USD",
    exchange_rate: Optional[Decimal] = None,
    payment_method: Optional[str] = None,
    vendor_name: Optional[str] = None,
    receipt_img_url: Optional[str] = None,
    is_reimbursable: bool = False,
    splits: Optional[list[dict]] = None,
    linked_proposal_id: Optional[int] = None,
    linked_pet_medical_id: Optional[int] = None,
    linked_maintenance_log_id: Optional[int] = None,
) -> Expense:
    """Create expense and optional splits (auto-split when splits empty can be added later)."""
    expense = Expense(
        group_id=group_id,
        paid_by_user_id=paid_by_user_id,
        description=description,
        amount=amount,
        currency_code=currency_code,
        exchange_rate=exchange_rate,
        category_id=category_id,
        expense_date=expense_date,
        payment_method=payment_method,
        vendor_name=vendor_name,
        receipt_img_url=receipt_img_url,
        is_reimbursable=is_reimbursable,
        linked_proposal_id=linked_proposal_id,
        linked_pet_medical_id=linked_pet_medical_id,
        linked_maintenance_log_id=linked_maintenance_log_id,
    )
    db.add(expense)
    await db.flush()
    if splits:
        for s in splits:
            split = ExpenseSplit(
                expense_id=expense.id,
                user_id=s["user_id"],
                owed_amount=s["owed_amount"],
                manual_override=s.get("manual_override"),
            )
            db.add(split)
        await db.flush()
    await db.refresh(expense)
    return expense


async def update_expense(
    db: AsyncSession,
    expense_id: int,
    version_id: int,
    description: Optional[str] = None,
    amount: Optional[Decimal] = None,
    currency_code: Optional[str] = None,
    category_id: Optional[int] = None,
    expense_date: Optional[datetime] = None,
    payment_method: Optional[str] = None,
    vendor_name: Optional[str] = None,
    receipt_img_url: Optional[str] = None,
    is_reimbursable: Optional[bool] = None,
    exchange_rate: Optional[Decimal] = None,
) -> Expense:
    """Update expense (may trigger re-split later). Raises StaleDataError on version mismatch."""
    result = await db.execute(select(Expense).where(Expense.id == expense_id).with_for_update())
    expense = result.scalar_one_or_none()
    if not expense:
        raise NotFoundError(code="EXPENSE_NOT_FOUND", detail=f"Expense {expense_id} not found")
    if expense.version_id != version_id:
        raise StaleDataError(detail=f"Expense {expense_id} was modified by another request")
    if description is not None:
        expense.description = description
    if amount is not None:
        expense.amount = amount
    if currency_code is not None:
        expense.currency_code = currency_code
    if category_id is not None:
        expense.category_id = category_id
    if expense_date is not None:
        expense.expense_date = expense_date
    if payment_method is not None:
        expense.payment_method = payment_method
    if vendor_name is not None:
        expense.vendor_name = vendor_name
    if receipt_img_url is not None:
        expense.receipt_img_url = receipt_img_url
    if is_reimbursable is not None:
        expense.is_reimbursable = is_reimbursable
    if exchange_rate is not None:
        expense.exchange_rate = exchange_rate
    await db.flush()
    await db.refresh(expense)
    return expense


async def delete_expense(db: AsyncSession, expense_id: int) -> None:
    """Soft-delete expense (re-calculates balances when we add balance logic)."""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise NotFoundError(code="EXPENSE_NOT_FOUND", detail=f"Expense {expense_id} not found")
    expense.deleted_at = datetime.utcnow()
    await db.flush()

"""Finance module service layer - business logic. PRIVATE - other modules import from interface.py."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError, StaleDataError, ValidationError
from mitlist.modules.finance.models import (
    BalanceSnapshot,
    Budget,
    Category,
    Expense,
    ExpenseSplit,
    RecurringExpense,
    Settlement,
    SplitPreset,
    SplitPresetMember,
)


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
    
    # Reload expense with splits relationship loaded
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .where(Expense.id == expense.id)
    )
    expense = result.scalar_one()
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
    
    # Reload expense with splits relationship loaded
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .where(Expense.id == expense.id)
    )
    expense = result.scalar_one()
    return expense


async def delete_expense(db: AsyncSession, expense_id: int) -> None:
    """Soft-delete expense (re-calculates balances when we add balance logic)."""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise NotFoundError(code="EXPENSE_NOT_FOUND", detail=f"Expense {expense_id} not found")
    expense.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def list_categories(
    db: AsyncSession,
    group_id: Optional[int] = None,
) -> list[Category]:
    """List categories."""
    q = select(Category)
    if group_id is not None:
        q = q.where((Category.group_id.is_(None)) | (Category.group_id == group_id))
    else:
        q = q.where(Category.group_id.is_(None))

    q = q.order_by(Category.name)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_category_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
    """Get category by ID."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def create_category(
    db: AsyncSession,
    name: str,
    group_id: Optional[int] = None,
    icon_emoji: Optional[str] = None,
    color_hex: Optional[str] = None,
    parent_category_id: Optional[int] = None,
    is_income: bool = False,
) -> Category:
    """Create category."""
    category = Category(
        group_id=group_id,
        name=name,
        icon_emoji=icon_emoji,
        color_hex=color_hex,
        parent_category_id=parent_category_id,
        is_income=is_income,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession,
    category_id: int,
    name: Optional[str] = None,
    icon_emoji: Optional[str] = None,
    color_hex: Optional[str] = None,
    parent_category_id: Optional[int] = None,
    is_income: Optional[bool] = None,
) -> Category:
    """Update category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise NotFoundError(code="CATEGORY_NOT_FOUND", detail=f"Category {category_id} not found")

    if name is not None:
        category.name = name
    if icon_emoji is not None:
        category.icon_emoji = icon_emoji
    if color_hex is not None:
        category.color_hex = color_hex
    if parent_category_id is not None:
        category.parent_category_id = parent_category_id
    if is_income is not None:
        category.is_income = is_income

    await db.flush()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> None:
    """Hard delete category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise NotFoundError(code="CATEGORY_NOT_FOUND", detail=f"Category {category_id} not found")

    await db.delete(category)
    await db.flush()


async def calculate_group_balances(
    db: AsyncSession,
    group_id: int,
) -> tuple[int, list[dict], Decimal, str]:
    """Calculate real-time balances for all group members."""
    from decimal import Decimal as D

    from sqlalchemy import func

    from mitlist.modules.auth.models import UserGroup

    members_result = await db.execute(
        select(UserGroup.user_id).where(
            UserGroup.group_id == group_id, UserGroup.left_at.is_(None)
        )
    )
    member_ids = [row[0] for row in members_result.all()]

    balances = []
    total_owed = D("0.00")
    currency_code = "USD"

    for user_id in member_ids:
        paid_result = await db.execute(
            select(func.coalesce(func.sum(Expense.amount), D("0.00"))).where(
                Expense.group_id == group_id,
                Expense.paid_by_user_id == user_id,
                Expense.deleted_at.is_(None),
            )
        )
        paid_total = paid_result.scalar() or D("0.00")

        owed_result = await db.execute(
            select(func.coalesce(func.sum(ExpenseSplit.owed_amount), D("0.00")))
            .join(Expense, ExpenseSplit.expense_id == Expense.id)
            .where(
                Expense.group_id == group_id,
                ExpenseSplit.user_id == user_id,
                ExpenseSplit.is_paid == False,
                Expense.deleted_at.is_(None),
            )
        )
        owed_total = owed_result.scalar() or D("0.00")

        settled_in_result = await db.execute(
            select(func.coalesce(func.sum(Settlement.amount), D("0.00"))).where(
                Settlement.group_id == group_id, Settlement.payee_id == user_id
            )
        )
        settled_in = settled_in_result.scalar() or D("0.00")

        settled_out_result = await db.execute(
            select(func.coalesce(func.sum(Settlement.amount), D("0.00"))).where(
                Settlement.group_id == group_id, Settlement.payer_id == user_id
            )
        )
        settled_out = settled_out_result.scalar() or D("0.00")

        balance = paid_total - owed_total + settled_in - settled_out

        balances.append(
            {
                "user_id": user_id,
                "balance": balance,
                "currency_code": currency_code,
            }
        )

        if balance > 0:
            total_owed += balance

    return group_id, balances, total_owed, currency_code


async def list_balance_snapshots(
    db: AsyncSession,
    group_id: int,
    user_id: Optional[int] = None,
    limit: int = 100,
) -> list[BalanceSnapshot]:
    """List historical balance snapshots."""
    q = select(BalanceSnapshot).where(BalanceSnapshot.group_id == group_id)
    if user_id is not None:
        q = q.where(BalanceSnapshot.user_id == user_id)

    q = q.order_by(BalanceSnapshot.snapshot_date.desc()).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def create_balance_snapshot(
    db: AsyncSession,
    group_id: int,
    user_id: int,
    balance_amount: Decimal,
    currency_code: str,
    snapshot_date: datetime,
) -> BalanceSnapshot:
    """Create a balance snapshot."""
    snapshot = BalanceSnapshot(
        group_id=group_id,
        user_id=user_id,
        balance_amount=balance_amount,
        currency_code=currency_code,
        snapshot_date=snapshot_date,
    )
    db.add(snapshot)
    await db.flush()
    await db.refresh(snapshot)
    return snapshot


async def list_settlements(
    db: AsyncSession,
    group_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[Settlement]:
    """List group settlements."""
    q = (
        select(Settlement)
        .where(Settlement.group_id == group_id)
        .order_by(Settlement.settled_at.desc(), Settlement.id.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_settlement_by_id(db: AsyncSession, settlement_id: int) -> Optional[Settlement]:
    """Get settlement by ID."""
    result = await db.execute(select(Settlement).where(Settlement.id == settlement_id))
    return result.scalar_one_or_none()


async def create_settlement(
    db: AsyncSession,
    group_id: int,
    payer_id: int,
    payee_id: int,
    amount: Decimal,
    currency_code: str,
    method: str,
    settled_at: datetime,
    confirmation_code: Optional[str] = None,
    notes: Optional[str] = None,
) -> Settlement:
    """Create settlement record."""
    settlement = Settlement(
        group_id=group_id,
        payer_id=payer_id,
        payee_id=payee_id,
        amount=amount,
        currency_code=currency_code,
        method=method,
        settled_at=settled_at,
        confirmation_code=confirmation_code,
        notes=notes,
    )
    db.add(settlement)
    await db.flush()
    await db.refresh(settlement)
    return settlement


async def delete_settlement(db: AsyncSession, settlement_id: int) -> None:
    """Hard delete settlement."""
    result = await db.execute(select(Settlement).where(Settlement.id == settlement_id))
    settlement = result.scalar_one_or_none()
    if not settlement:
        raise NotFoundError(
            code="SETTLEMENT_NOT_FOUND", detail=f"Settlement {settlement_id} not found"
        )

    await db.delete(settlement)
    await db.flush()


async def list_budgets(
    db: AsyncSession,
    group_id: int,
) -> list[Budget]:
    """List group budgets."""
    q = select(Budget).where(Budget.group_id == group_id).order_by(Budget.start_date.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_budget_by_id(db: AsyncSession, budget_id: int) -> Optional[Budget]:
    """Get budget by ID."""
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
    return result.scalar_one_or_none()


async def create_budget(
    db: AsyncSession,
    group_id: int,
    category_id: int,
    amount_limit: Decimal,
    currency_code: str,
    period_type: str,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    alert_threshold_percentage: int = 80,
) -> Budget:
    """Create budget."""
    budget = Budget(
        group_id=group_id,
        category_id=category_id,
        amount_limit=amount_limit,
        currency_code=currency_code,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
        alert_threshold_percentage=alert_threshold_percentage,
    )
    db.add(budget)
    await db.flush()
    await db.refresh(budget)
    return budget


async def update_budget(
    db: AsyncSession,
    budget_id: int,
    amount_limit: Optional[Decimal] = None,
    end_date: Optional[datetime] = None,
    alert_threshold_percentage: Optional[int] = None,
) -> Budget:
    """Update budget."""
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise NotFoundError(code="BUDGET_NOT_FOUND", detail=f"Budget {budget_id} not found")

    if amount_limit is not None:
        budget.amount_limit = amount_limit
    if end_date is not None:
        budget.end_date = end_date
    if alert_threshold_percentage is not None:
        budget.alert_threshold_percentage = alert_threshold_percentage

    await db.flush()
    await db.refresh(budget)
    return budget


async def delete_budget(db: AsyncSession, budget_id: int) -> None:
    """Hard delete budget."""
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise NotFoundError(code="BUDGET_NOT_FOUND", detail=f"Budget {budget_id} not found")

    await db.delete(budget)
    await db.flush()


async def calculate_budget_status(
    db: AsyncSession,
    budget: Budget,
) -> dict:
    """Calculate current spending status for a budget."""
    from decimal import Decimal as D

    from sqlalchemy import func

    q = select(func.coalesce(func.sum(Expense.amount), D("0.00")))
    q = q.where(
        Expense.group_id == budget.group_id,
        Expense.category_id == budget.category_id,
        Expense.expense_date >= budget.start_date,
        Expense.deleted_at.is_(None),
    )

    if budget.end_date:
        q = q.where(Expense.expense_date <= budget.end_date)

    result = await db.execute(q)
    current_spent = result.scalar() or D("0.00")

    remaining = budget.amount_limit - current_spent
    percentage_used = (
        float((current_spent / budget.amount_limit) * 100) if budget.amount_limit > 0 else 0.0
    )
    is_over_budget = current_spent > budget.amount_limit
    is_alert_threshold_reached = percentage_used >= budget.alert_threshold_percentage

    return {
        "current_spent": current_spent,
        "remaining": remaining,
        "percentage_used": percentage_used,
        "is_over_budget": is_over_budget,
        "is_alert_threshold_reached": is_alert_threshold_reached,
    }


def _calculate_next_due_date(
    start_date: datetime,
    frequency_type: str,
    interval_value: int,
) -> datetime:
    """Calculate next due date based on frequency."""
    from dateutil.relativedelta import relativedelta

    if frequency_type == "WEEKLY":
        return start_date + relativedelta(weeks=interval_value)
    elif frequency_type == "MONTHLY":
        return start_date + relativedelta(months=interval_value)
    elif frequency_type == "YEARLY":
        return start_date + relativedelta(years=interval_value)
    else:
        return start_date + relativedelta(days=interval_value)


async def list_recurring_expenses(
    db: AsyncSession,
    group_id: int,
    active_only: bool = True,
) -> list[RecurringExpense]:
    """List recurring expenses."""
    q = select(RecurringExpense).where(RecurringExpense.group_id == group_id)
    if active_only:
        q = q.where(RecurringExpense.is_active == True)

    q = q.order_by(RecurringExpense.next_due_date.asc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_recurring_expense_by_id(
    db: AsyncSession,
    recurring_expense_id: int,
) -> Optional[RecurringExpense]:
    """Get recurring expense by ID."""
    result = await db.execute(
        select(RecurringExpense).where(RecurringExpense.id == recurring_expense_id)
    )
    return result.scalar_one_or_none()


async def create_recurring_expense(
    db: AsyncSession,
    group_id: int,
    paid_by_user_id: int,
    description: str,
    amount: Decimal,
    currency_code: str,
    category_id: int,
    frequency_type: str,
    interval_value: int,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    auto_create_expense: bool = True,
    split_preset_id: Optional[int] = None,
) -> RecurringExpense:
    """Create recurring expense."""
    next_due = _calculate_next_due_date(start_date, frequency_type, interval_value)

    recurring = RecurringExpense(
        group_id=group_id,
        paid_by_user_id=paid_by_user_id,
        description=description,
        amount=amount,
        currency_code=currency_code,
        category_id=category_id,
        frequency_type=frequency_type,
        interval_value=interval_value,
        start_date=start_date,
        end_date=end_date,
        next_due_date=next_due,
        auto_create_expense=auto_create_expense,
        split_preset_id=split_preset_id,
    )
    db.add(recurring)
    await db.flush()
    await db.refresh(recurring)
    return recurring


async def update_recurring_expense(
    db: AsyncSession,
    recurring_expense_id: int,
    description: Optional[str] = None,
    amount: Optional[Decimal] = None,
    currency_code: Optional[str] = None,
    category_id: Optional[int] = None,
    frequency_type: Optional[str] = None,
    interval_value: Optional[int] = None,
    end_date: Optional[datetime] = None,
    auto_create_expense: Optional[bool] = None,
    split_preset_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> RecurringExpense:
    """Update recurring expense."""
    result = await db.execute(
        select(RecurringExpense).where(RecurringExpense.id == recurring_expense_id)
    )
    recurring = result.scalar_one_or_none()
    if not recurring:
        raise NotFoundError(
            code="RECURRING_EXPENSE_NOT_FOUND",
            detail=f"Recurring expense {recurring_expense_id} not found",
        )

    if description is not None:
        recurring.description = description
    if amount is not None:
        recurring.amount = amount
    if currency_code is not None:
        recurring.currency_code = currency_code
    if category_id is not None:
        recurring.category_id = category_id
    if frequency_type is not None:
        recurring.frequency_type = frequency_type
    if interval_value is not None:
        recurring.interval_value = interval_value
    if end_date is not None:
        recurring.end_date = end_date
    if auto_create_expense is not None:
        recurring.auto_create_expense = auto_create_expense
    if split_preset_id is not None:
        recurring.split_preset_id = split_preset_id
    if is_active is not None:
        recurring.is_active = is_active

    if frequency_type is not None or interval_value is not None:
        recurring.next_due_date = _calculate_next_due_date(
            recurring.start_date,
            recurring.frequency_type,
            recurring.interval_value,
        )

    await db.flush()
    await db.refresh(recurring)
    return recurring


async def deactivate_recurring_expense(
    db: AsyncSession,
    recurring_expense_id: int,
) -> RecurringExpense:
    """Deactivate recurring expense."""
    return await update_recurring_expense(db, recurring_expense_id, is_active=False)


async def generate_expense_from_recurring(
    db: AsyncSession,
    recurring_expense_id: int,
) -> Expense:
    """Manually generate an expense from a recurring template."""
    result = await db.execute(
        select(RecurringExpense).where(RecurringExpense.id == recurring_expense_id)
    )
    recurring = result.scalar_one_or_none()
    if not recurring:
        raise NotFoundError(
            code="RECURRING_EXPENSE_NOT_FOUND",
            detail=f"Recurring expense {recurring_expense_id} not found",
        )

    expense = await create_expense(
        db,
        group_id=recurring.group_id,
        paid_by_user_id=recurring.paid_by_user_id,
        description=recurring.description,
        amount=recurring.amount,
        category_id=recurring.category_id,
        expense_date=datetime.now(timezone.utc),
        currency_code=recurring.currency_code,
    )

    expense.linked_recurring_expense_id = recurring.id
    expense.is_recurring_generated = True

    recurring.next_due_date = _calculate_next_due_date(
        recurring.next_due_date or recurring.start_date,
        recurring.frequency_type,
        recurring.interval_value,
    )

    await db.flush()
    
    # Reload expense with splits relationship loaded
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .where(Expense.id == expense.id)
    )
    expense = result.scalar_one()
    return expense


async def list_split_presets(
    db: AsyncSession,
    group_id: int,
) -> list[SplitPreset]:
    """List split presets for a group."""
    q = (
        select(SplitPreset)
        .where(SplitPreset.group_id == group_id)
        .options(selectinload(SplitPreset.members))
        .order_by(SplitPreset.is_default.desc(), SplitPreset.name)
    )
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_split_preset_by_id(
    db: AsyncSession,
    preset_id: int,
) -> Optional[SplitPreset]:
    """Get split preset by ID with members."""
    result = await db.execute(
        select(SplitPreset)
        .where(SplitPreset.id == preset_id)
        .options(selectinload(SplitPreset.members))
    )
    return result.scalar_one_or_none()


async def create_split_preset(
    db: AsyncSession,
    group_id: int,
    name: str,
    method: str,
    is_default: bool = False,
    members: Optional[list[dict]] = None,
) -> SplitPreset:
    """Create split preset with members."""
    preset = SplitPreset(
        group_id=group_id,
        name=name,
        method=method,
        is_default=is_default,
    )
    db.add(preset)
    await db.flush()

    if members:
        for m in members:
            member = SplitPresetMember(
                preset_id=preset.id,
                user_id=m["user_id"],
                percentage=m.get("percentage"),
                fixed_amount=m.get("fixed_amount"),
            )
            db.add(member)
        await db.flush()

    # Refresh with members loaded
    await db.refresh(preset)
    # Load members relationship
    result = await db.execute(
        select(SplitPreset)
        .where(SplitPreset.id == preset.id)
        .options(selectinload(SplitPreset.members))
    )
    preset = result.scalar_one()
    return preset


async def update_split_preset(
    db: AsyncSession,
    preset_id: int,
    name: Optional[str] = None,
    method: Optional[str] = None,
    is_default: Optional[bool] = None,
    members: Optional[list[dict]] = None,
) -> SplitPreset:
    """Update split preset."""
    result = await db.execute(
        select(SplitPreset)
        .where(SplitPreset.id == preset_id)
        .options(selectinload(SplitPreset.members))
    )
    preset = result.scalar_one_or_none()
    if not preset:
        raise NotFoundError(code="PRESET_NOT_FOUND", detail=f"Split preset {preset_id} not found")

    if name is not None:
        preset.name = name
    if method is not None:
        preset.method = method
    if is_default is not None:
        preset.is_default = is_default

    if members is not None:
        for member in preset.members:
            await db.delete(member)
        await db.flush()

        for m in members:
            member = SplitPresetMember(
                preset_id=preset.id,
                user_id=m["user_id"],
                percentage=m.get("percentage"),
                fixed_amount=m.get("fixed_amount"),
            )
            db.add(member)
        await db.flush()

    # Reload preset with members for response
    result = await db.execute(
        select(SplitPreset)
        .where(SplitPreset.id == preset_id)
        .options(selectinload(SplitPreset.members))
    )
    preset = result.scalar_one()
    return preset


async def delete_split_preset(db: AsyncSession, preset_id: int) -> None:
    """Hard delete split preset."""
    result = await db.execute(select(SplitPreset).where(SplitPreset.id == preset_id))
    preset = result.scalar_one_or_none()
    if not preset:
        raise NotFoundError(code="PRESET_NOT_FOUND", detail=f"Split preset {preset_id} not found")

    await db.delete(preset)
    await db.flush()

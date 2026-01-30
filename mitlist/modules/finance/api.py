"""Finance & Settlements module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_group_id, get_current_user, get_db
from mitlist.core.errors import NotFoundError, NotImplementedAppError, ValidationError
from mitlist.modules.finance import interface, schemas

router = APIRouter(tags=["finance"])


@router.get("/expenses", response_model=ListType[schemas.ExpenseResponse])
async def get_expenses(
    group_id: int = Depends(get_current_group_id),
    user_id: int | None = Query(None),
    category_id: int | None = Query(None),
    date_from: str | None = Query(None, description="ISO datetime"),
    date_to: str | None = Query(None, description="ISO datetime"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.ExpenseResponse]:
    """List group expenses (filter by date, user, category)."""
    from datetime import datetime

    date_from_dt = None
    date_to_dt = None
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
        except ValueError:
            pass
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
        except ValueError:
            pass
    expenses = await interface.list_expenses(
        db,
        group_id=group_id,
        user_id=user_id,
        category_id=category_id,
        date_from=date_from_dt,
        date_to=date_to_dt,
        limit=limit,
        offset=offset,
    )
    return [schemas.ExpenseResponse.model_validate(e) for e in expenses]


@router.post("/expenses", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: schemas.ExpenseCreateRequest,
    group_id: int = Depends(get_current_group_id),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> schemas.ExpenseResponse:
    """Create expense (triggers auto-split when splits provided)."""
    splits_data = [
        {
            "user_id": s.user_id,
            "owed_amount": s.owed_amount,
            "manual_override": s.manual_override,
        }
        for s in data.splits
    ]

    expense = await interface.create_expense(
        db,
        group_id=group_id,
        paid_by_user_id=user.id,
        description=data.description,
        amount=data.amount,
        category_id=data.category_id,
        expense_date=data.expense_date,
        currency_code=data.currency_code,
        exchange_rate=data.exchange_rate,
        payment_method=data.payment_method,
        vendor_name=data.vendor_name,
        receipt_img_url=data.receipt_img_url,
        is_reimbursable=data.is_reimbursable,
        splits=splits_data if splits_data else None,
        linked_proposal_id=data.linked_proposal_id,
        linked_pet_medical_id=data.linked_pet_medical_id,
        linked_maintenance_log_id=data.linked_maintenance_log_id,
    )
    return schemas.ExpenseResponse.model_validate(expense)


@router.get("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
async def get_expense(
    expense_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ExpenseResponse:
    """Get full split details and comments."""
    expense = await interface.get_expense_by_id(db, expense_id)
    if not expense or expense.group_id != group_id:
        raise NotFoundError(code="EXPENSE_NOT_FOUND", detail=f"Expense {expense_id} not found")
    return schemas.ExpenseResponse.model_validate(expense)


@router.patch("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
async def update_expense(
    expense_id: int,
    data: schemas.ExpenseUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ExpenseResponse:
    """Update amount/desc (may trigger re-split)."""
    existing = await interface.get_expense_by_id(db, expense_id)
    if not existing or existing.group_id != group_id:
        raise NotFoundError(code="EXPENSE_NOT_FOUND", detail=f"Expense {expense_id} not found")
    expense = await interface.update_expense(
        db,
        expense_id=expense_id,
        version_id=data.version_id,
        description=data.description,
        amount=data.amount,
        currency_code=data.currency_code,
        category_id=data.category_id,
        expense_date=data.expense_date,
        payment_method=data.payment_method,
        vendor_name=data.vendor_name,
        receipt_img_url=data.receipt_img_url,
        is_reimbursable=data.is_reimbursable,
        exchange_rate=data.exchange_rate,
    )
    return schemas.ExpenseResponse.model_validate(expense)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete expense (re-calculates balances)."""
    expense = await interface.get_expense_by_id(db, expense_id)
    if not expense or expense.group_id != group_id:
        raise NotFoundError(code="EXPENSE_NOT_FOUND", detail=f"Expense {expense_id} not found")
    await interface.delete_expense(db, expense_id)


# ---------- Stubs: balances, categories, settlements, budgets, recurring ----------
def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/balances", response_model=schemas.GroupBalanceSummaryResponse)
async def get_balances(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.GroupBalanceSummaryResponse:
    """Calculate real-time group balances."""
    gid, balances, total_owed, currency = await interface.calculate_group_balances(db, group_id)

    balance_responses = [schemas.UserBalanceResponse.model_validate(b) for b in balances]

    return schemas.GroupBalanceSummaryResponse(
        group_id=gid,
        balances=balance_responses,
        total_owed=total_owed,
        currency_code=currency,
    )


@router.get("/balances/history", response_model=ListType[schemas.BalanceSnapshotResponse])
async def get_balance_history(
    group_id: int = Depends(get_current_group_id),
    user_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.BalanceSnapshotResponse]:
    """Get historical balance snapshots."""
    snapshots = await interface.list_balance_snapshots(
        db, group_id=group_id, user_id=user_id, limit=limit
    )
    return [schemas.BalanceSnapshotResponse.model_validate(s) for s in snapshots]


@router.get("/categories", response_model=ListType[schemas.CategoryResponse])
async def get_categories(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.CategoryResponse]:
    """List global + group-specific categories."""
    categories = await interface.list_categories(db, group_id=group_id)
    return [schemas.CategoryResponse.model_validate(c) for c in categories]


@router.post("/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: schemas.CategoryCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.CategoryResponse:
    """Create category."""
    if data.group_id is not None and data.group_id != group_id:
        raise ValidationError(code="GROUP_MISMATCH", detail="group_id in body must match current group")

    category = await interface.create_category(
        db,
        name=data.name,
        group_id=data.group_id,
        icon_emoji=data.icon_emoji,
        color_hex=data.color_hex,
        parent_category_id=data.parent_category_id,
        is_income=data.is_income,
    )
    return schemas.CategoryResponse.model_validate(category)


@router.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> schemas.CategoryResponse:
    """Get category by ID."""
    category = await interface.get_category_by_id(db, category_id)
    if not category:
        raise NotFoundError(code="CATEGORY_NOT_FOUND", detail=f"Category {category_id} not found")
    return schemas.CategoryResponse.model_validate(category)


@router.patch("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: int,
    data: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.CategoryResponse:
    """Update category."""
    category = await interface.update_category(
        db,
        category_id=category_id,
        name=data.name,
        icon_emoji=data.icon_emoji,
        color_hex=data.color_hex,
        parent_category_id=data.parent_category_id,
        is_income=data.is_income,
    )
    return schemas.CategoryResponse.model_validate(category)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete category."""
    await interface.delete_category(db, category_id)


@router.get("/settlements", response_model=ListType[schemas.SettlementResponse])
async def get_settlements(
    group_id: int = Depends(get_current_group_id),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.SettlementResponse]:
    """List group settlements."""
    settlements = await interface.list_settlements(
        db, group_id=group_id, limit=limit, offset=offset
    )
    return [schemas.SettlementResponse.model_validate(s) for s in settlements]


@router.post("/settlements", response_model=schemas.SettlementResponse, status_code=status.HTTP_201_CREATED)
async def create_settlement(
    data: schemas.SettlementCreateRequest,
    group_id: int = Depends(get_current_group_id),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> schemas.SettlementResponse:
    """Record settlement (payer = current user)."""
    settlement = await interface.create_settlement(
        db,
        group_id=group_id,
        payer_id=user.id,
        payee_id=data.payee_id,
        amount=data.amount,
        currency_code=data.currency_code,
        method=data.method,
        settled_at=data.settled_at,
        confirmation_code=data.confirmation_code,
        notes=data.notes,
    )
    return schemas.SettlementResponse.model_validate(settlement)


@router.get("/settlements/{settlement_id}", response_model=schemas.SettlementResponse)
async def get_settlement(
    settlement_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.SettlementResponse:
    """Get settlement by ID."""
    settlement = await interface.get_settlement_by_id(db, settlement_id)
    if not settlement or settlement.group_id != group_id:
        raise NotFoundError(
            code="SETTLEMENT_NOT_FOUND", detail=f"Settlement {settlement_id} not found"
        )
    return schemas.SettlementResponse.model_validate(settlement)


@router.delete("/settlements/{settlement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_settlement(
    settlement_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete/reverse settlement."""
    settlement = await interface.get_settlement_by_id(db, settlement_id)
    if not settlement or settlement.group_id != group_id:
        raise NotFoundError(
            code="SETTLEMENT_NOT_FOUND", detail=f"Settlement {settlement_id} not found"
        )
    await interface.delete_settlement(db, settlement_id)


@router.get("/budgets", response_model=ListType[schemas.BudgetStatusResponse])
async def get_budgets(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.BudgetStatusResponse]:
    """List budgets with current spending status."""
    budgets = await interface.list_budgets(db, group_id=group_id)

    responses = []
    for budget in budgets:
        status_data = await interface.calculate_budget_status(db, budget)

        response = schemas.BudgetStatusResponse(
            id=budget.id,
            group_id=budget.group_id,
            category_id=budget.category_id,
            amount_limit=budget.amount_limit,
            currency_code=budget.currency_code,
            period_type=budget.period_type,
            start_date=budget.start_date,
            end_date=budget.end_date,
            alert_threshold_percentage=budget.alert_threshold_percentage,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
            **status_data,
        )
        responses.append(response)

    return responses


@router.post("/budgets", response_model=schemas.BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: schemas.BudgetCreateRequest,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.BudgetResponse:
    """Create budget."""
    budget = await interface.create_budget(
        db,
        group_id=group_id,
        category_id=data.category_id,
        amount_limit=data.amount_limit,
        currency_code=data.currency_code,
        period_type=data.period_type,
        start_date=data.start_date,
        end_date=data.end_date,
        alert_threshold_percentage=data.alert_threshold_percentage,
    )
    return schemas.BudgetResponse.model_validate(budget)


@router.get("/budgets/{budget_id}", response_model=schemas.BudgetStatusResponse)
async def get_budget(
    budget_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.BudgetStatusResponse:
    """Get budget with current spending status."""
    budget = await interface.get_budget_by_id(db, budget_id)
    if not budget or budget.group_id != group_id:
        raise NotFoundError(code="BUDGET_NOT_FOUND", detail=f"Budget {budget_id} not found")

    status_data = await interface.calculate_budget_status(db, budget)

    return schemas.BudgetStatusResponse(
        id=budget.id,
        group_id=budget.group_id,
        category_id=budget.category_id,
        amount_limit=budget.amount_limit,
        currency_code=budget.currency_code,
        period_type=budget.period_type,
        start_date=budget.start_date,
        end_date=budget.end_date,
        alert_threshold_percentage=budget.alert_threshold_percentage,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
        **status_data,
    )


@router.patch("/budgets/{budget_id}", response_model=schemas.BudgetResponse)
async def update_budget(
    budget_id: int,
    data: schemas.BudgetUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.BudgetResponse:
    """Update budget."""
    existing = await interface.get_budget_by_id(db, budget_id)
    if not existing or existing.group_id != group_id:
        raise NotFoundError(code="BUDGET_NOT_FOUND", detail=f"Budget {budget_id} not found")

    budget = await interface.update_budget(
        db,
        budget_id=budget_id,
        amount_limit=data.amount_limit,
        end_date=data.end_date,
        alert_threshold_percentage=data.alert_threshold_percentage,
    )
    return schemas.BudgetResponse.model_validate(budget)


@router.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete budget."""
    budget = await interface.get_budget_by_id(db, budget_id)
    if not budget or budget.group_id != group_id:
        raise NotFoundError(code="BUDGET_NOT_FOUND", detail=f"Budget {budget_id} not found")
    await interface.delete_budget(db, budget_id)


@router.get("/recurring-expenses", response_model=ListType[schemas.RecurringExpenseResponse])
async def get_recurring_expenses(
    group_id: int = Depends(get_current_group_id),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.RecurringExpenseResponse]:
    """List recurring expenses."""
    recurring = await interface.list_recurring_expenses(
        db, group_id=group_id, active_only=active_only
    )
    return [schemas.RecurringExpenseResponse.model_validate(r) for r in recurring]


@router.post("/recurring-expenses", response_model=schemas.RecurringExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_expense(
    data: schemas.RecurringExpenseCreateRequest,
    group_id: int = Depends(get_current_group_id),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> schemas.RecurringExpenseResponse:
    """Create recurring expense."""
    recurring = await interface.create_recurring_expense(
        db,
        group_id=group_id,
        paid_by_user_id=user.id,
        description=data.description,
        amount=data.amount,
        currency_code=data.currency_code,
        category_id=data.category_id,
        frequency_type=data.frequency_type,
        interval_value=data.interval_value,
        start_date=data.start_date,
        end_date=data.end_date,
        auto_create_expense=data.auto_create_expense,
        split_preset_id=data.split_preset_id,
    )
    return schemas.RecurringExpenseResponse.model_validate(recurring)


@router.get("/recurring-expenses/{recurring_id}", response_model=schemas.RecurringExpenseResponse)
async def get_recurring_expense(
    recurring_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.RecurringExpenseResponse:
    """Get recurring expense by ID."""
    recurring = await interface.get_recurring_expense_by_id(db, recurring_id)
    if not recurring or recurring.group_id != group_id:
        raise NotFoundError(
            code="RECURRING_EXPENSE_NOT_FOUND",
            detail=f"Recurring expense {recurring_id} not found",
        )
    return schemas.RecurringExpenseResponse.model_validate(recurring)


@router.patch("/recurring-expenses/{recurring_id}", response_model=schemas.RecurringExpenseResponse)
async def update_recurring_expense(
    recurring_id: int,
    data: schemas.RecurringExpenseUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.RecurringExpenseResponse:
    """Update recurring expense."""
    existing = await interface.get_recurring_expense_by_id(db, recurring_id)
    if not existing or existing.group_id != group_id:
        raise NotFoundError(
            code="RECURRING_EXPENSE_NOT_FOUND",
            detail=f"Recurring expense {recurring_id} not found",
        )

    recurring = await interface.update_recurring_expense(
        db,
        recurring_expense_id=recurring_id,
        description=data.description,
        amount=data.amount,
        currency_code=data.currency_code,
        category_id=data.category_id,
        frequency_type=data.frequency_type,
        interval_value=data.interval_value,
        end_date=data.end_date,
        auto_create_expense=data.auto_create_expense,
        split_preset_id=data.split_preset_id,
        is_active=data.is_active,
    )
    return schemas.RecurringExpenseResponse.model_validate(recurring)


@router.delete("/recurring-expenses/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_expense(
    recurring_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deactivate recurring expense."""
    recurring = await interface.get_recurring_expense_by_id(db, recurring_id)
    if not recurring or recurring.group_id != group_id:
        raise NotFoundError(
            code="RECURRING_EXPENSE_NOT_FOUND",
            detail=f"Recurring expense {recurring_id} not found",
        )
    await interface.deactivate_recurring_expense(db, recurring_id)


@router.post("/recurring-expenses/{recurring_id}/generate", response_model=schemas.ExpenseResponse)
async def generate_recurring_expense(
    recurring_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.ExpenseResponse:
    """Manually generate an expense from recurring template."""
    recurring = await interface.get_recurring_expense_by_id(db, recurring_id)
    if not recurring or recurring.group_id != group_id:
        raise NotFoundError(
            code="RECURRING_EXPENSE_NOT_FOUND",
            detail=f"Recurring expense {recurring_id} not found",
        )

    expense = await interface.generate_expense_from_recurring(db, recurring_id)
    return schemas.ExpenseResponse.model_validate(expense)


# ---------- Split Presets ----------
@router.get("/split-presets", response_model=ListType[schemas.SplitPresetResponse])
async def get_split_presets(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> ListType[schemas.SplitPresetResponse]:
    """List split presets for group."""
    presets = await interface.list_split_presets(db, group_id=group_id)
    return [schemas.SplitPresetResponse.model_validate(p) for p in presets]


@router.post("/split-presets", response_model=schemas.SplitPresetResponse, status_code=status.HTTP_201_CREATED)
async def create_split_preset(
    data: schemas.SplitPresetCreateRequest,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.SplitPresetResponse:
    """Create split preset."""
    members_data = [
        {
            "user_id": m.user_id,
            "percentage": m.percentage,
            "fixed_amount": m.fixed_amount,
        }
        for m in data.members
    ]

    preset = await interface.create_split_preset(
        db,
        group_id=group_id,
        name=data.name,
        method=data.method,
        is_default=data.is_default,
        members=members_data if members_data else None,
    )
    return schemas.SplitPresetResponse.model_validate(preset)


@router.get("/split-presets/{preset_id}", response_model=schemas.SplitPresetResponse)
async def get_split_preset(
    preset_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.SplitPresetResponse:
    """Get split preset by ID."""
    preset = await interface.get_split_preset_by_id(db, preset_id)
    if not preset or preset.group_id != group_id:
        raise NotFoundError(
            code="PRESET_NOT_FOUND", detail=f"Split preset {preset_id} not found"
        )
    return schemas.SplitPresetResponse.model_validate(preset)


@router.patch("/split-presets/{preset_id}", response_model=schemas.SplitPresetResponse)
async def update_split_preset(
    preset_id: int,
    data: schemas.SplitPresetUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> schemas.SplitPresetResponse:
    """Update split preset."""
    existing = await interface.get_split_preset_by_id(db, preset_id)
    if not existing or existing.group_id != group_id:
        raise NotFoundError(
            code="PRESET_NOT_FOUND", detail=f"Split preset {preset_id} not found"
        )

    members_data = None
    if data.members is not None:
        members_data = [
            {
                "user_id": m.user_id,
                "percentage": m.percentage,
                "fixed_amount": m.fixed_amount,
            }
            for m in data.members
        ]

    preset = await interface.update_split_preset(
        db,
        preset_id=preset_id,
        name=data.name,
        method=data.method,
        is_default=data.is_default,
        members=members_data,
    )
    return schemas.SplitPresetResponse.model_validate(preset)


@router.delete("/split-presets/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_split_preset(
    preset_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete split preset."""
    preset = await interface.get_split_preset_by_id(db, preset_id)
    if not preset or preset.group_id != group_id:
        raise NotFoundError(
            code="PRESET_NOT_FOUND", detail=f"Split preset {preset_id} not found"
        )
    await interface.delete_split_preset(db, preset_id)

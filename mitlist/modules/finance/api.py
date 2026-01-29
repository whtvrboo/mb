"""Finance & Settlements module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotFoundError, NotImplementedAppError
from mitlist.modules.finance import interface, schemas

router = APIRouter(tags=["finance"])


@router.get("/expenses", response_model=ListType[schemas.ExpenseResponse])
async def get_expenses(
    group_id: int,
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
    data: schemas.ExpenseCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ExpenseResponse:
    """Create expense (triggers auto-split when splits provided)."""
    splits_data = [{"user_id": s.user_id, "owed_amount": s.owed_amount, "manual_override": s.manual_override} for s in data.splits]
    expense = await interface.create_expense(
        db,
        group_id=data.group_id,
        paid_by_user_id=data.paid_by_user_id,
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
    db: AsyncSession = Depends(get_db),
) -> schemas.ExpenseResponse:
    """Get full split details and comments."""
    expense = await interface.get_expense_by_id(db, expense_id)
    if not expense:
        raise NotFoundError(code="EXPENSE_NOT_FOUND", detail=f"Expense {expense_id} not found")
    return schemas.ExpenseResponse.model_validate(expense)


@router.patch("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
async def update_expense(
    expense_id: int,
    data: schemas.ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ExpenseResponse:
    """Update amount/desc (may trigger re-split)."""
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
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete expense (re-calculates balances)."""
    expense = await interface.get_expense_by_id(db, expense_id)
    if not expense:
        raise NotFoundError(code="EXPENSE_NOT_FOUND", detail=f"Expense {expense_id} not found")
    await interface.delete_expense(db, expense_id)


# ---------- Stubs: balances, categories, settlements, budgets, recurring ----------
def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/balances", response_model=schemas.GroupBalanceSummaryResponse)
async def get_balances(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /balances is not yet implemented")


@router.get("/categories", response_model=ListType[schemas.CategoryResponse])
async def get_categories(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /categories is not yet implemented")


@router.post("/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
async def post_categories(data: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /categories is not yet implemented")


@router.get("/settlements", response_model=ListType[schemas.SettlementResponse])
async def get_settlements(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /settlements is not yet implemented")


@router.post("/settlements", response_model=schemas.SettlementResponse, status_code=status.HTTP_201_CREATED)
async def post_settlements(data: schemas.SettlementCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /settlements is not yet implemented")


@router.get("/budgets", response_model=ListType[schemas.BudgetResponse])
async def get_budgets(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /budgets is not yet implemented")


@router.post("/budgets", response_model=schemas.BudgetResponse, status_code=status.HTTP_201_CREATED)
async def post_budgets(data: schemas.BudgetCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /budgets is not yet implemented")


@router.get("/recurring-expenses", response_model=ListType[schemas.RecurringExpenseResponse])
async def get_recurring_expenses(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /recurring-expenses is not yet implemented")


@router.post("/recurring-expenses", response_model=schemas.RecurringExpenseResponse, status_code=status.HTTP_201_CREATED)
async def post_recurring_expenses(data: schemas.RecurringExpenseCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /recurring-expenses is not yet implemented")

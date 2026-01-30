---
name: Finance Module Implementation
overview: Implement the complete finance module service layer and API endpoints for categories, balances, settlements, budgets, recurring expenses, and split presets. All endpoints will use group-scoped authentication via `get_current_group_id` and `paid_by_user_id` will always use the authenticated user.
todos:
  - id: schemas
    content: Add request schemas (without user_id/group_id) for Expense, Settlement, Budget, RecurringExpense, SplitPreset
    status: pending
  - id: categories
    content: Implement Categories service functions + wire to API
    status: pending
  - id: balances
    content: Implement balance calculation service + wire to API
    status: pending
  - id: settlements
    content: Implement Settlements CRUD service + wire to API
    status: pending
  - id: budgets
    content: Implement Budgets CRUD + status calculation service + wire to API
    status: pending
  - id: recurring
    content: Implement Recurring Expenses CRUD + manual generation service + wire to API
    status: pending
  - id: presets
    content: Implement Split Presets CRUD service + wire to API
    status: pending
  - id: interface
    content: Update interface.py to re-export all new service functions
    status: pending
  - id: expense-refactor
    content: Update POST /expenses to use current_user.id as paid_by_user_id
    status: pending
isProject: false
---

# Finance Module Implementation

## Current State

**Models exist** (no migrations needed):

- `Category`, `Expense`, `ExpenseSplit`, `RecurringExpense`, `Settlement`, `SplitPreset`, `SplitPresetMember`, `Budget`, `BalanceSnapshot`

**Schemas exist** in `[mitlist/modules/finance/schemas.py](mitlist/modules/finance/schemas.py)`:

- All Create/Update/Response schemas are already defined

**Currently implemented** in `[mitlist/modules/finance/service.py](mitlist/modules/finance/service.py)`:

- Only `Expense` CRUD (list, get, create, update, delete)

**API stubs** in `[mitlist/modules/finance/api.py](mitlist/modules/finance/api.py)`:

- 9 endpoints return 501 Not Implemented

---

## Implementation Plan

### 1. Update Expense Endpoints - Use Auth Context for `paid_by_user_id`

**File:** `[mitlist/modules/finance/api.py](mitlist/modules/finance/api.py)`

- Remove `paid_by_user_id` from `ExpenseCreate` schema usage in `POST /expenses`
- Always use `user.id` from `Depends(get_current_user)` as `paid_by_user_id`
- Update schema to make `paid_by_user_id` optional or create `ExpenseCreateRequest` that omits it

**File:** `[mitlist/modules/finance/schemas.py](mitlist/modules/finance/schemas.py)`

- Create `ExpenseCreateRequest` (without `paid_by_user_id`, without `group_id`)
- Same for `RecurringExpenseCreateRequest`, `SettlementCreateRequest`, `BudgetCreateRequest`

---

### 2. Categories Service + API

**Service functions** to add in `[mitlist/modules/finance/service.py](mitlist/modules/finance/service.py)`:

```python
async def list_categories(db, group_id: int | None) -> list[Category]
    # Returns global (group_id=None) + group-specific categories

async def get_category_by_id(db, category_id: int) -> Category | None

async def create_category(db, name, group_id=None, ...) -> Category

async def update_category(db, category_id, **updates) -> Category

async def delete_category(db, category_id) -> None
    # Hard delete (no soft delete on categories)
```

**API endpoints** to add:

| Method   | Path               | Description                    |
| -------- | ------------------ | ------------------------------ |
| `GET`    | `/categories`      | List global + group categories |
| `POST`   | `/categories`      | Create category                |
| `GET`    | `/categories/{id}` | Get category                   |
| `PATCH`  | `/categories/{id}` | Update category                |
| `DELETE` | `/categories/{id}` | Delete category                |

---

### 3. Balances Service + API

**Service functions** in `[mitlist/modules/finance/service.py](mitlist/modules/finance/service.py)`:

```python
async def calculate_group_balances(db, group_id: int) -> GroupBalanceSummary
    # For each group member:
    # - paid_total = SUM(expenses.amount) where paid_by_user_id = user
    # - owed_total = SUM(expense_splits.owed_amount) where user_id = user AND is_paid = false
    # - settled_in = SUM(settlements.amount) where payee_id = user
    # - settled_out = SUM(settlements.amount) where payer_id = user
    # - balance = paid_total - owed_total + settled_in - settled_out

async def create_balance_snapshot(db, group_id, user_id, amount, date) -> BalanceSnapshot
```

**API endpoints:**

| Method | Path                | Description                        |
| ------ | ------------------- | ---------------------------------- |
| `GET`  | `/balances`         | Calculate real-time group balances |
| `GET`  | `/balances/history` | Get historical balance snapshots   |

---

### 4. Settlements Service + API

**Service functions:**

```python
async def list_settlements(db, group_id, limit, offset) -> list[Settlement]

async def get_settlement_by_id(db, settlement_id) -> Settlement | None

async def create_settlement(db, group_id, payer_id, payee_id, amount, ...) -> Settlement
    # Validate payer_id and payee_id are group members
    # Optionally mark related expense_splits as paid

async def delete_settlement(db, settlement_id) -> None
    # Hard delete (reverses the settlement)
```

**API endpoints:**

| Method   | Path                | Description                              |
| -------- | ------------------- | ---------------------------------------- |
| `GET`    | `/settlements`      | List group settlements                   |
| `POST`   | `/settlements`      | Record settlement (payer = current user) |
| `GET`    | `/settlements/{id}` | Get settlement                           |
| `DELETE` | `/settlements/{id}` | Delete/reverse settlement                |

---

### 5. Budgets Service + API

**Service functions:**

```python
async def list_budgets(db, group_id) -> list[Budget]

async def get_budget_by_id(db, budget_id) -> Budget | None

async def create_budget(db, group_id, category_id, amount_limit, ...) -> Budget

async def update_budget(db, budget_id, **updates) -> Budget

async def delete_budget(db, budget_id) -> None

async def get_budget_status(db, budget_id) -> BudgetStatusResponse
    # Calculate current_spent from expenses in budget period + category
    # Return remaining, percentage_used, is_over_budget, is_alert_reached
```

**API endpoints:**

| Method   | Path            | Description              |
| -------- | --------------- | ------------------------ |
| `GET`    | `/budgets`      | List budgets with status |
| `POST`   | `/budgets`      | Create budget            |
| `GET`    | `/budgets/{id}` | Get budget with status   |
| `PATCH`  | `/budgets/{id}` | Update budget            |
| `DELETE` | `/budgets/{id}` | Delete budget            |

---

### 6. Recurring Expenses Service + API

**Service functions:**

```python
async def list_recurring_expenses(db, group_id, active_only=True) -> list[RecurringExpense]

async def get_recurring_expense_by_id(db, recurring_expense_id) -> RecurringExpense | None

async def create_recurring_expense(db, group_id, paid_by_user_id, ...) -> RecurringExpense
    # Calculate next_due_date based on start_date + frequency

async def update_recurring_expense(db, recurring_expense_id, **updates) -> RecurringExpense

async def deactivate_recurring_expense(db, recurring_expense_id) ->
```

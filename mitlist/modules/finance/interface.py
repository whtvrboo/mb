"""
Finance module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
"""

from mitlist.modules.finance import schemas, service

__all__ = [
    "schemas",
    # Expenses
    "list_expenses",
    "get_expense_by_id",
    "create_expense",
    "update_expense",
    "delete_expense",
    # Categories
    "list_categories",
    "get_category_by_id",
    "create_category",
    "update_category",
    "delete_category",
    # Balances
    "calculate_group_balances",
    "list_balance_snapshots",
    "create_balance_snapshot",
    # Settlements
    "list_settlements",
    "get_settlement_by_id",
    "create_settlement",
    "delete_settlement",
    # Budgets
    "list_budgets",
    "get_budget_by_id",
    "create_budget",
    "update_budget",
    "delete_budget",
    "calculate_budget_status",
    # Recurring Expenses
    "list_recurring_expenses",
    "get_recurring_expense_by_id",
    "create_recurring_expense",
    "update_recurring_expense",
    "deactivate_recurring_expense",
    "generate_expense_from_recurring",
    # Split Presets
    "list_split_presets",
    "get_split_preset_by_id",
    "create_split_preset",
    "update_split_preset",
    "delete_split_preset",
]

# Expenses
list_expenses = service.list_expenses
get_expense_by_id = service.get_expense_by_id
create_expense = service.create_expense
update_expense = service.update_expense
delete_expense = service.delete_expense

# Categories
list_categories = service.list_categories
get_category_by_id = service.get_category_by_id
create_category = service.create_category
update_category = service.update_category
delete_category = service.delete_category

# Balances
calculate_group_balances = service.calculate_group_balances
list_balance_snapshots = service.list_balance_snapshots
create_balance_snapshot = service.create_balance_snapshot

# Settlements
list_settlements = service.list_settlements
get_settlement_by_id = service.get_settlement_by_id
create_settlement = service.create_settlement
delete_settlement = service.delete_settlement

# Budgets
list_budgets = service.list_budgets
get_budget_by_id = service.get_budget_by_id
create_budget = service.create_budget
update_budget = service.update_budget
delete_budget = service.delete_budget
calculate_budget_status = service.calculate_budget_status

# Recurring Expenses
list_recurring_expenses = service.list_recurring_expenses
get_recurring_expense_by_id = service.get_recurring_expense_by_id
create_recurring_expense = service.create_recurring_expense
update_recurring_expense = service.update_recurring_expense
deactivate_recurring_expense = service.deactivate_recurring_expense
generate_expense_from_recurring = service.generate_expense_from_recurring

# Split Presets
list_split_presets = service.list_split_presets
get_split_preset_by_id = service.get_split_preset_by_id
create_split_preset = service.create_split_preset
update_split_preset = service.update_split_preset
delete_split_preset = service.delete_split_preset

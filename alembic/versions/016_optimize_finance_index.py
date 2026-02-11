"""Optimize finance index

Revision ID: 016_optimize_finance_index
Revises: 015_optimize_items_index
Create Date: 2026-02-05 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "016_optimize_finance_index"
down_revision: str | None = "015_optimize_items_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create new composite index for expenses
    op.create_index(
        "ix_expenses_group_category_date",
        "expenses",
        ["group_id", "category_id", "expense_date"],
        unique=False,
    )


def downgrade() -> None:
    # Drop the composite index
    op.drop_index("ix_expenses_group_category_date", table_name="expenses")

"""Optimize expense splits

Revision ID: 018_optimize_expense_splits
Revises: 016_optimize_chores_indexes, 017_optimize_finance_user_index
Create Date: 2026-02-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_expense_splits'
down_revision: Union[str, Sequence[str], None] = ('016_optimize_chores_indexes', '017_optimize_finance_user_index')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create partial index for unpaid expense splits to optimize balance calculation
    op.create_index(
        'ix_expense_splits_unpaid',
        'expense_splits',
        ['expense_id', 'user_id', 'owed_amount'],
        unique=False,
        sqlite_where=sa.text('is_paid = 0'),
        postgresql_where=sa.text('is_paid = false')
    )


def downgrade() -> None:
    # Drop the partial index
    op.drop_index('ix_expense_splits_unpaid', table_name='expense_splits')

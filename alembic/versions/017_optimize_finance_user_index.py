"""Optimize finance user index

Revision ID: 017_optimize_finance_user_index
Revises: 016_optimize_finance_index
Create Date: 2026-02-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '017_optimize_finance_user_index'
down_revision: Union[str, None] = '016_optimize_finance_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create simple index for paid_by_user_id (for FK checks)
    op.create_index(
        'ix_expenses_paid_by_user_id',
        'expenses',
        ['paid_by_user_id'],
        unique=False
    )

    # Create composite index for filtering by group + user + date
    op.create_index(
        'ix_expenses_group_user_date',
        'expenses',
        ['group_id', 'paid_by_user_id', 'expense_date'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_expenses_group_user_date', table_name='expenses')
    op.drop_index('ix_expenses_paid_by_user_id', table_name='expenses')

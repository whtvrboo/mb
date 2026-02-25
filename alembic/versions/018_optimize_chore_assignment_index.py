"""Optimize chore assignment index

Revision ID: 018_optimize_chore_assignment_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_chore_assignment_index'
down_revision: Union[str, None] = '017_optimize_finance_user_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create composite index
    op.create_index(
        'ix_chore_assignments_chore_id_due_date',
        'chore_assignments',
        ['chore_id', 'due_date'],
        unique=False
    )
    # Drop single index on chore_id (now covered by composite index)
    op.drop_index('ix_chore_assignments_chore_id', table_name='chore_assignments')


def downgrade() -> None:
    # Recreate single index
    op.create_index(
        'ix_chore_assignments_chore_id',
        'chore_assignments',
        ['chore_id'],
        unique=False
    )
    # Drop composite index
    op.drop_index('ix_chore_assignments_chore_id_due_date', table_name='chore_assignments')

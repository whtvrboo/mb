"""Optimize chore history and missing indexes

Revision ID: 018_optimize_chore_history
Revises: 017_optimize_finance_user_index
Create Date: 2026-03-01 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_chore_history'
down_revision: str | None = '017_optimize_finance_user_index'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create missing indexes for chore assignments (previously attempted in detached migration 016)
    op.create_index(
        'ix_chore_assignments_assigned_to_id',
        'chore_assignments',
        ['assigned_to_id'],
        unique=False
    )
    op.create_index(
        'ix_chore_assignments_due_date',
        'chore_assignments',
        ['due_date'],
        unique=False
    )

    # Create new index for optimizing history queries (sort by completed_at)
    op.create_index(
        'ix_chore_assignments_completed_at',
        'chore_assignments',
        ['completed_at'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_chore_assignments_completed_at', table_name='chore_assignments')
    op.drop_index('ix_chore_assignments_due_date', table_name='chore_assignments')
    op.drop_index('ix_chore_assignments_assigned_to_id', table_name='chore_assignments')

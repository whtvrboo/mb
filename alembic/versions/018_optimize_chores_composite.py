"""Optimize chores composite indexes

Revision ID: 018_optimize_chores_composite
Revises: 016_optimize_chores_indexes, 017_optimize_finance_user_index
Create Date: 2026-03-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_chores_composite'
down_revision: Union[str, Sequence[str], None] = ('016_optimize_chores_indexes', '017_optimize_finance_user_index')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create new composite indexes

    # Chore: group_id + is_active
    op.create_index(
        'ix_chores_group_active',
        'chores',
        ['group_id', 'is_active'],
        unique=False
    )

    # ChoreAssignment: assigned_to_id + status + due_date
    op.create_index(
        'ix_chore_assignments_assigned_status_due',
        'chore_assignments',
        ['assigned_to_id', 'status', 'due_date'],
        unique=False
    )

    # ChoreAssignment: chore_id + status
    op.create_index(
        'ix_chore_assignments_chore_status',
        'chore_assignments',
        ['chore_id', 'status'],
        unique=False
    )

    # 2. Drop redundant single-column indexes

    # chores.group_id is prefix of ix_chores_group_active
    op.drop_index('ix_chores_group_id', table_name='chores')

    # chore_assignments.chore_id is prefix of ix_chore_assignments_chore_status
    op.drop_index('ix_chore_assignments_chore_id', table_name='chore_assignments')

    # chore_assignments.assigned_to_id is prefix of ix_chore_assignments_assigned_status_due
    op.drop_index('ix_chore_assignments_assigned_to_id', table_name='chore_assignments')


def downgrade() -> None:
    # 1. Restore single-column indexes
    op.create_index(
        'ix_chore_assignments_assigned_to_id',
        'chore_assignments',
        ['assigned_to_id'],
        unique=False
    )
    op.create_index(
        'ix_chore_assignments_chore_id',
        'chore_assignments',
        ['chore_id'],
        unique=False
    )
    op.create_index(
        'ix_chores_group_id',
        'chores',
        ['group_id'],
        unique=False
    )

    # 2. Drop composite indexes
    op.drop_index('ix_chore_assignments_chore_status', table_name='chore_assignments')
    op.drop_index('ix_chore_assignments_assigned_status_due', table_name='chore_assignments')
    op.drop_index('ix_chores_group_active', table_name='chores')

"""Optimize chores indexes

Revision ID: 018_optimize_chores
Revises: 017_optimize_finance_user_index
Create Date: 2024-05-26 12:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_chores'
down_revision: str | None = '017_optimize_finance_user_index'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create new composite indexes
    op.create_index(
        'ix_chores_group_active',
        'chores',
        ['group_id', 'is_active'],
        unique=False
    )
    op.create_index(
        'ix_chore_assignments_assigned_status_due',
        'chore_assignments',
        ['assigned_to_id', 'status', 'due_date'],
        unique=False
    )
    op.create_index(
        'ix_chore_assignments_chore_status_due',
        'chore_assignments',
        ['chore_id', 'status', 'due_date'],
        unique=False
    )

    # Drop existing single-column indexes if they exist (standard naming)
    # Using 'if_exists' logic is hard in pure alembic without inspection,
    # but we assume standard state.
    # Note: 016_optimize_chores_indexes created ix_chore_assignments_assigned_to_id
    # so we should drop it.

    # We use explicit names based on sqlalchemy defaults
    try:
        op.drop_index('ix_chores_group_id', table_name='chores')
    except Exception:
        pass # Ignore if not exists (e.g. fresh db)

    try:
        op.drop_index('ix_chore_assignments_chore_id', table_name='chore_assignments')
    except Exception:
        pass

    try:
        op.drop_index('ix_chore_assignments_assigned_to_id', table_name='chore_assignments')
    except Exception:
        pass


def downgrade() -> None:
    # Drop new indexes
    op.drop_index('ix_chore_assignments_chore_status_due', table_name='chore_assignments')
    op.drop_index('ix_chore_assignments_assigned_status_due', table_name='chore_assignments')
    op.drop_index('ix_chores_group_active', table_name='chores')

    # Recreate old indexes
    op.create_index(
        "ix_chore_assignments_assigned_to_id",
        "chore_assignments",
        ["assigned_to_id"],
        unique=False,
    )
    op.create_index(
        "ix_chore_assignments_chore_id",
        "chore_assignments",
        ["chore_id"],
        unique=False,
    )
    op.create_index("ix_chores_group_id", "chores", ["group_id"], unique=False)

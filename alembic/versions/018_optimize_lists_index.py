"""Optimize lists index

Revision ID: 018_optimize_lists_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-15 12:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_lists_index'
down_revision: str | None = '017_optimize_finance_user_index'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop existing index on group_id
    op.drop_index('ix_lists_group_id', table_name='lists')
    # Create new composite index on (group_id, is_archived, id)
    op.create_index(
        'ix_lists_group_archived_id',
        'lists',
        ['group_id', 'is_archived', 'id'],
        unique=False
    )


def downgrade() -> None:
    # Drop new composite index
    op.drop_index('ix_lists_group_archived_id', table_name='lists')
    # Recreate index on group_id
    op.create_index(
        'ix_lists_group_id',
        'lists',
        ['group_id'],
        unique=False
    )

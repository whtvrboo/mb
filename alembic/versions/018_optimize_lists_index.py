"""Optimize lists index

Revision ID: 018_optimize_lists_index
Revises: 016_optimize_chores_indexes, 017_optimize_finance_user_index
Create Date: 2026-02-15 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_lists_index'
down_revision: str | Sequence[str] | None = (
    '016_optimize_chores_indexes',
    '017_optimize_finance_user_index',
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop old index
    op.drop_index('ix_lists_group_id', table_name='lists')
    # Create new composite index
    op.create_index(
        'ix_lists_group_archived_id', 'lists', ['group_id', 'is_archived', 'id'], unique=False
    )


def downgrade() -> None:
    # Drop new composite index
    op.drop_index('ix_lists_group_archived_id', table_name='lists')
    # Recreate old index
    op.create_index('ix_lists_group_id', 'lists', ['group_id'], unique=False)

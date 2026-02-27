"""Optimize lists index

Revision ID: 018_optimize_lists_index
Revises: 017_optimize_finance_user_index, 016_optimize_chores_indexes
Create Date: 2026-02-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_lists_index'
down_revision: Union[str, None] = ('017_optimize_finance_user_index', '016_optimize_chores_indexes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old index on group_id
    op.drop_index('ix_lists_group_id', table_name='lists')

    # Create new composite index on (group_id, id)
    op.create_index(
        'ix_lists_group_id_id',
        'lists',
        ['group_id', 'id'],
        unique=False
    )


def downgrade() -> None:
    # Drop the new composite index
    op.drop_index('ix_lists_group_id_id', table_name='lists')

    # Recreate the old index
    op.create_index(
        'ix_lists_group_id',
        'lists',
        ['group_id'],
        unique=False
    )

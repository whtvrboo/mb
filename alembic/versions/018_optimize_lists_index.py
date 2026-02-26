"""Optimize lists index

Revision ID: 018_optimize_lists_index
Revises: 017_optimize_finance_user_index, 016_optimize_chores_indexes
Create Date: 2026-02-14 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_lists_index'
down_revision: Union[str, Sequence[str], None] = ('017_optimize_finance_user_index', '016_optimize_chores_indexes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create composite index for group_id + id (sorting optimization)
    op.create_index(
        'ix_lists_group_id_id',
        'lists',
        ['group_id', 'id'],
        unique=False
    )

    # Drop the old single column index as it is now redundant (covered by prefix of new index)
    # Note: Alembic/SQLAlchemy creates 'ix_lists_group_id' by default for index=True
    op.drop_index('ix_lists_group_id', table_name='lists')


def downgrade() -> None:
    # Restore the old single column index
    op.create_index(
        'ix_lists_group_id',
        'lists',
        ['group_id'],
        unique=False
    )

    # Drop the composite index
    op.drop_index('ix_lists_group_id_id', table_name='lists')

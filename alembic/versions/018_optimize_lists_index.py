"""Optimize lists index

Revision ID: 018_optimize_lists_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_lists_index'
down_revision: Union[str, None] = '017_optimize_finance_user_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop single column index
    op.drop_index('ix_lists_group_id', table_name='lists')
    # Create composite index on (group_id, is_archived, id)
    op.create_index(
        'ix_lists_group_archived_id',
        'lists',
        ['group_id', 'is_archived', 'id'],
        unique=False
    )


def downgrade() -> None:
    # Drop composite index
    op.drop_index('ix_lists_group_archived_id', table_name='lists')
    # Recreate single column index
    op.create_index('ix_lists_group_id', 'lists', ['group_id'], unique=False)

"""Optimize list indexes

Revision ID: 018_optimize_list_indexes
Revises: 016_optimize_chores_indexes, 017_optimize_finance_user_index
Create Date: 2026-03-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_list_indexes'
down_revision: Union[str, None] = ('016_optimize_chores_indexes', '017_optimize_finance_user_index')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old indexes
    op.drop_index('ix_lists_group_id', table_name='lists')
    op.drop_index('ix_inventory_items_group_id', table_name='inventory_items')

    # Create new composite indexes
    op.create_index('ix_lists_group_id_id', 'lists', ['group_id', 'id'], unique=False)
    op.create_index('ix_inventory_items_group_id_id', 'inventory_items', ['group_id', 'id'], unique=False)


def downgrade() -> None:
    # Drop new composite indexes
    op.drop_index('ix_inventory_items_group_id_id', table_name='inventory_items')
    op.drop_index('ix_lists_group_id_id', table_name='lists')

    # Recreate old indexes
    op.create_index('ix_inventory_items_group_id', 'inventory_items', ['group_id'], unique=False)
    op.create_index('ix_lists_group_id', 'lists', ['group_id'], unique=False)

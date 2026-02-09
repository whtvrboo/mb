"""Optimize lists index

Revision ID: 018_optimize_lists_index
Revises: 016_optimize_chores_indexes, 017_optimize_finance_user_index
Create Date: 2026-02-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_lists_index'
down_revision: Union[str, Sequence[str], None] = ('016_optimize_chores_indexes', '017_optimize_finance_user_index')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Lists
    op.drop_index('ix_lists_group_id', table_name='lists')
    op.create_index('ix_lists_group_id_id', 'lists', ['group_id', 'id'], unique=False)

    # Inventory Items
    op.drop_index('ix_inventory_items_group_id', table_name='inventory_items')
    op.create_index('ix_inventory_items_group_id_id', 'inventory_items', ['group_id', 'id'], unique=False)


def downgrade() -> None:
    # Inventory Items
    op.drop_index('ix_inventory_items_group_id_id', table_name='inventory_items')
    op.create_index('ix_inventory_items_group_id', 'inventory_items', ['group_id'], unique=False)

    # Lists
    op.drop_index('ix_lists_group_id_id', table_name='lists')
    op.create_index('ix_lists_group_id', 'lists', ['group_id'], unique=False)

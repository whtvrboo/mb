"""Optimize lists and inventory indexes

Revision ID: 018_optimize_lists_indexes
Revises: 017_optimize_finance_user_index, 016_optimize_chores_indexes
Create Date: 2026-02-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_lists_indexes'
down_revision: Union[str, None] = ('017_optimize_finance_user_index', '016_optimize_chores_indexes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Lists: Drop old index, create new composite index
    op.drop_index('ix_lists_group_id', table_name='lists')
    op.create_index(
        'ix_lists_group_id_id',
        'lists',
        ['group_id', 'id'],
        unique=False
    )

    # InventoryItems: Drop old index, create new composite index
    op.drop_index('ix_inventory_items_group_id', table_name='inventory_items')
    op.create_index(
        'ix_inventory_items_group_id_id',
        'inventory_items',
        ['group_id', 'id'],
        unique=False
    )


def downgrade() -> None:
    # InventoryItems: Drop new composite index, recreate old index
    op.drop_index('ix_inventory_items_group_id_id', table_name='inventory_items')
    op.create_index(
        'ix_inventory_items_group_id',
        'inventory_items',
        ['group_id'],
        unique=False
    )

    # Lists: Drop new composite index, recreate old index
    op.drop_index('ix_lists_group_id_id', table_name='lists')
    op.create_index(
        'ix_lists_group_id',
        'lists',
        ['group_id'],
        unique=False
    )

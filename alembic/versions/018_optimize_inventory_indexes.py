"""Optimize inventory indexes

Revision ID: 018_optimize_inventory_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_inventory_indexes'
down_revision: Union[str, None] = '017_optimize_finance_user_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old index
    op.drop_index('ix_inventory_items_group_id', table_name='inventory_items')
    # Create new composite index
    op.create_index('ix_inventory_items_group_id_id', 'inventory_items', ['group_id', 'id'], unique=False)


def downgrade() -> None:
    # Drop new composite index
    op.drop_index('ix_inventory_items_group_id_id', table_name='inventory_items')
    # Recreate old index
    op.create_index('ix_inventory_items_group_id', 'inventory_items', ['group_id'], unique=False)

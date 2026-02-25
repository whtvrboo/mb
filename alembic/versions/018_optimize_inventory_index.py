"""Optimize inventory index

Revision ID: 018_optimize_inventory_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-14 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_inventory_index'
down_revision: Union[str, None] = '017_optimize_finance_user_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old single-column index
    op.drop_index('ix_inventory_items_group_id', table_name='inventory_items')

    # Create the new composite index
    op.create_index(
        'ix_inventory_items_group_id_id',
        'inventory_items',
        ['group_id', 'id'],
        unique=False
    )


def downgrade() -> None:
    # Drop the new composite index
    op.drop_index('ix_inventory_items_group_id_id', table_name='inventory_items')

    # Recreate the old single-column index
    op.create_index(
        'ix_inventory_items_group_id',
        'inventory_items',
        ['group_id'],
        unique=False
    )

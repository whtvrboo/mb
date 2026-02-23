"""Optimize list and inventory indexes

Revision ID: 018_optimize_list_inventory_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-15 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018_optimize_list_inventory_indexes"
down_revision: str | None = "017_optimize_finance_user_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Lists
    # Drop old index
    op.drop_index("ix_lists_group_id", table_name="lists")
    # Create new composite index
    op.create_index("ix_lists_group_id_id", "lists", ["group_id", "id"], unique=False)

    # Inventory Items
    op.drop_index("ix_inventory_items_group_id", table_name="inventory_items")
    op.create_index(
        "ix_inventory_items_group_id_id", "inventory_items", ["group_id", "id"], unique=False
    )


def downgrade() -> None:
    # Inventory Items
    op.drop_index("ix_inventory_items_group_id_id", table_name="inventory_items")
    op.create_index("ix_inventory_items_group_id", "inventory_items", ["group_id"], unique=False)

    # Lists
    op.drop_index("ix_lists_group_id_id", table_name="lists")
    op.create_index("ix_lists_group_id", "lists", ["group_id"], unique=False)

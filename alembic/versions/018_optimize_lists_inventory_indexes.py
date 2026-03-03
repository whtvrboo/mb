"""Optimize lists and inventory_items indexes

Revision ID: 018_optimize_lists_inventory_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2024-05-24 10:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "018_optimize_lists_inventory_indexes"
down_revision = "017_optimize_finance_user_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # lists table
    op.drop_index("ix_lists_group_id", table_name="lists")
    op.create_index("ix_lists_group_id_id", "lists", ["group_id", "id"], unique=False)

    # inventory_items table
    op.drop_index("ix_inventory_items_group_id", table_name="inventory_items")
    op.create_index(
        "ix_inventory_items_group_id_id", "inventory_items", ["group_id", "id"], unique=False
    )


def downgrade() -> None:
    # inventory_items table
    op.drop_index("ix_inventory_items_group_id_id", table_name="inventory_items")
    op.create_index("ix_inventory_items_group_id", "inventory_items", ["group_id"], unique=False)

    # lists table
    op.drop_index("ix_lists_group_id_id", table_name="lists")
    op.create_index("ix_lists_group_id", "lists", ["group_id"], unique=False)

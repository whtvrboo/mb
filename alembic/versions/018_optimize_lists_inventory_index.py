"""Optimize lists and inventory fetch-and-sort indexing

Revision ID: 018_optimize_lists_inventory_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-03-10 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018_optimize_lists_inventory_index"
down_revision: str | None = "017_optimize_finance_user_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # lists
    op.drop_index("ix_lists_group_id", table_name="lists")
    op.create_index("ix_lists_group_id_id", "lists", ["group_id", "id"])

    # inventory_items
    op.drop_index("ix_inventory_items_group_id", table_name="inventory_items")
    op.create_index("ix_inventory_items_group_id_id", "inventory_items", ["group_id", "id"])


def downgrade() -> None:
    # inventory_items
    op.drop_index("ix_inventory_items_group_id_id", table_name="inventory_items")
    op.create_index("ix_inventory_items_group_id", "inventory_items", ["group_id"])

    # lists
    op.drop_index("ix_lists_group_id_id", table_name="lists")
    op.create_index("ix_lists_group_id", "lists", ["group_id"])

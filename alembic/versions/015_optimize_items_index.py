"""Optimize items index

Revision ID: 015_optimize_items_index
Revises: 014_audit
Create Date: 2026-02-04 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "015_optimize_items_index"
down_revision: Union[str, None] = "014_audit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old index
    op.drop_index("ix_items_list_id", table_name="items")
    # Create new composite index
    op.create_index("ix_items_list_id_id", "items", ["list_id", "id"], unique=False)


def downgrade() -> None:
    # Drop new composite index
    op.drop_index("ix_items_list_id_id", table_name="items")
    # Recreate old index
    op.create_index("ix_items_list_id", "items", ["list_id"], unique=False)

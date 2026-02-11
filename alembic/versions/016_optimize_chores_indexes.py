"""Optimize chores indexes

Revision ID: 016_optimize_chores_indexes
Revises: 015_optimize_items_index
Create Date: 2024-05-25 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "016_optimize_chores_indexes"
down_revision: str | None = "015_optimize_items_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create indexes for frequently queried columns in chore_assignments
    op.create_index(
        "ix_chore_assignments_assigned_to_id", "chore_assignments", ["assigned_to_id"], unique=False
    )
    op.create_index(
        "ix_chore_assignments_due_date", "chore_assignments", ["due_date"], unique=False
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_chore_assignments_due_date", table_name="chore_assignments")
    op.drop_index("ix_chore_assignments_assigned_to_id", table_name="chore_assignments")

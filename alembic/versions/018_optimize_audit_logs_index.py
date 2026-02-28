"""Optimize audit logs index

Revision ID: 018_optimize_audit_logs_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-28 21:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018_optimize_audit_logs_index"
down_revision: str | None = "017_optimize_finance_user_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop the old index on entity_id
    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")

    # Create composite index for filtering by entity_type, entity_id and sorting by occurred_at
    op.create_index(
        "ix_audit_logs_entity_lookup",
        "audit_logs",
        ["entity_type", "entity_id", "occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop the composite index
    op.drop_index("ix_audit_logs_entity_lookup", table_name="audit_logs")

    # Recreate the old index on entity_id
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"], unique=False)

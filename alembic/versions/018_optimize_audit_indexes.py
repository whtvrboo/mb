"""Optimize audit and tag assignment indexes

Revision ID: 018_optimize_audit_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-03-01 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018_optimize_audit_indexes"
down_revision: str | None = "017_optimize_finance_user_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Drop old single-column indexes on entity_id
    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")
    op.drop_index("ix_tag_assignments_entity_id", table_name="tag_assignments")

    # 2. Create composite indexes for polymorphic relationships
    op.create_index(
        "ix_audit_logs_entity_type_id_time",
        "audit_logs",
        ["entity_type", "entity_id", "occurred_at"],
        unique=False,
    )
    op.create_index(
        "ix_tag_assignments_entity_type_id",
        "tag_assignments",
        ["entity_type", "entity_id"],
        unique=False,
    )


def downgrade() -> None:
    # 1. Drop new composite indexes
    op.drop_index("ix_tag_assignments_entity_type_id", table_name="tag_assignments")
    op.drop_index("ix_audit_logs_entity_type_id_time", table_name="audit_logs")

    # 2. Recreate old single-column indexes
    op.create_index("ix_tag_assignments_entity_id", "tag_assignments", ["entity_id"], unique=False)
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"], unique=False)

"""optimize_audit_indexes

Revision ID: 018_optimize_audit_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-03-12 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018_optimize_audit_indexes"
down_revision: str | None = "017_optimize_finance_user_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop old single-column indexes on entity_id
    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")
    op.drop_index("ix_tag_assignments_entity_id", table_name="tag_assignments")

    # Create new composite indexes for polymorphic lookups
    op.create_index(
        op.f("ix_audit_logs_entity_lookup"),
        "audit_logs",
        ["entity_type", "entity_id", "occurred_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tag_assignments_entity_lookup"),
        "tag_assignments",
        ["entity_type", "entity_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop composite indexes
    op.drop_index(op.f("ix_tag_assignments_entity_lookup"), table_name="tag_assignments")
    op.drop_index(op.f("ix_audit_logs_entity_lookup"), table_name="audit_logs")

    # Recreate single-column indexes
    op.create_index("ix_tag_assignments_entity_id", "tag_assignments", ["entity_id"], unique=False)
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"], unique=False)

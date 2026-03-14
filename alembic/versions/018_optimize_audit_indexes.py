"""Add composite indexes to audit models

Revision ID: 018_optimize_audit_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2024-05-24 10:00:00.000000

"""


from alembic import op

# revision identifiers, used by Alembic.
revision = "018_optimize_audit_indexes"
down_revision = "017_optimize_finance_user_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # AuditLog index changes
    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")
    op.create_index(
        "ix_audit_logs_entity_lookup",
        "audit_logs",
        ["entity_type", "entity_id", "occurred_at"],
        unique=False,
    )

    # TagAssignment index changes
    op.drop_index("ix_tag_assignments_entity_id", table_name="tag_assignments")
    op.create_index(
        "ix_tag_assignments_entity_lookup",
        "tag_assignments",
        ["entity_type", "entity_id"],
        unique=False,
    )


def downgrade() -> None:
    # TagAssignment index changes
    op.drop_index("ix_tag_assignments_entity_lookup", table_name="tag_assignments")
    op.create_index("ix_tag_assignments_entity_id", "tag_assignments", ["entity_id"], unique=False)

    # AuditLog index changes
    op.drop_index("ix_audit_logs_entity_lookup", table_name="audit_logs")
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"], unique=False)

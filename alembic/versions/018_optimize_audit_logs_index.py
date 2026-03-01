"""Optimize polymorphic indexing for audit logs and tag assignments

Revision ID: 018_optimize_audit_logs_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-03-01 12:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_logs_index'
down_revision: str | None = '017_optimize_finance_user_index'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- Audit Logs ---
    # Drop the old single-column index on entity_id
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')

    # Create the new composite index for polymorphic querying + sorting
    op.create_index(
        'ix_audit_logs_entity_type_id_occurred_at',
        'audit_logs',
        ['entity_type', 'entity_id', 'occurred_at'],
        unique=False
    )

    # --- Tag Assignments ---
    # Drop the old single-column index on entity_id
    op.drop_index('ix_tag_assignments_entity_id', table_name='tag_assignments')

    # Create the new composite index for polymorphic querying
    op.create_index(
        'ix_tag_assignments_entity_type_id',
        'tag_assignments',
        ['entity_type', 'entity_id'],
        unique=False
    )


def downgrade() -> None:
    # --- Tag Assignments ---
    op.drop_index('ix_tag_assignments_entity_type_id', table_name='tag_assignments')
    op.create_index('ix_tag_assignments_entity_id', 'tag_assignments', ['entity_id'], unique=False)

    # --- Audit Logs ---
    op.drop_index('ix_audit_logs_entity_type_id_occurred_at', table_name='audit_logs')
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'], unique=False)

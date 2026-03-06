"""Optimize audit polymorphic indexes

Revision ID: 018_optimize_audit_polymorphic_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-03-01 12:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_polymorphic_indexes'
down_revision: str | None = '017_optimize_finance_user_index'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- audit_logs ---
    # Drop single-column index on entity_id
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')

    # Create composite index for polymorphic entity history queries
    op.create_index(
        'ix_audit_logs_entity_history',
        'audit_logs',
        ['entity_type', 'entity_id', 'occurred_at'],
        unique=False
    )

    # --- tag_assignments ---
    # Drop single-column index on entity_id
    op.drop_index('ix_tag_assignments_entity_id', table_name='tag_assignments')

    # Create composite index for polymorphic entity tag queries
    op.create_index(
        'ix_tag_assignments_entity',
        'tag_assignments',
        ['entity_type', 'entity_id'],
        unique=False
    )


def downgrade() -> None:
    # --- tag_assignments ---
    op.drop_index('ix_tag_assignments_entity', table_name='tag_assignments')
    op.create_index(
        'ix_tag_assignments_entity_id',
        'tag_assignments',
        ['entity_id'],
        unique=False
    )

    # --- audit_logs ---
    op.drop_index('ix_audit_logs_entity_history', table_name='audit_logs')
    op.create_index(
        'ix_audit_logs_entity_id',
        'audit_logs',
        ['entity_id'],
        unique=False
    )

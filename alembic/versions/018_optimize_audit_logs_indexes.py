"""Optimize audit_logs indexes

Revision ID: 018_optimize_audit_logs_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-14 12:30:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_logs_indexes'
down_revision: str | None = '017_optimize_finance_user_index'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop old single-column indexes
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_group_id', table_name='audit_logs')

    # Create optimized composite indexes
    op.create_index(
        'ix_audit_logs_group_date',
        'audit_logs',
        ['group_id', 'occurred_at'],
        unique=False
    )
    op.create_index(
        'ix_audit_logs_entity_date',
        'audit_logs',
        ['entity_type', 'entity_id', 'occurred_at'],
        unique=False
    )


def downgrade() -> None:
    # Drop new composite indexes
    op.drop_index('ix_audit_logs_entity_date', table_name='audit_logs')
    op.drop_index('ix_audit_logs_group_date', table_name='audit_logs')

    # Restore old single-column indexes
    op.create_index(
        'ix_audit_logs_group_id',
        'audit_logs',
        ['group_id'],
        unique=False
    )
    op.create_index(
        'ix_audit_logs_entity_id',
        'audit_logs',
        ['entity_id'],
        unique=False
    )

"""Optimize audit logs indexing for entity history

Revision ID: 018_optimize_audit_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-15 12:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_index'
down_revision: str | None = '017_optimize_finance_user_index'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop redundant single column index on entity_id since we add composite
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')

    # Create composite index for entity history sorting
    op.create_index(
        'ix_audit_logs_entity_type_entity_id_occurred_at',
        'audit_logs',
        ['entity_type', 'entity_id', 'occurred_at'],
        unique=False
    )


def downgrade() -> None:
    # Drop composite index
    op.drop_index(
        'ix_audit_logs_entity_type_entity_id_occurred_at',
        table_name='audit_logs'
    )

    # Recreate single column index
    op.create_index(
        'ix_audit_logs_entity_id',
        'audit_logs',
        ['entity_id'],
        unique=False
    )

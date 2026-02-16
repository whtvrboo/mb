"""Optimize audit logs index

Revision ID: 018_optimize_audit_logs_index
Revises: 016_optimize_chores_indexes, 017_optimize_finance_user_index
Create Date: 2026-02-15 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_logs_index'
down_revision: str | Sequence[str] | None = (
    '016_optimize_chores_indexes',
    '017_optimize_finance_user_index',
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop old single-column index
    op.drop_index('ix_audit_logs_group_id', table_name='audit_logs')

    # Create new composite index for group + occurred_at
    op.create_index(
        'ix_audit_logs_group_occurred',
        'audit_logs',
        ['group_id', 'occurred_at'],
        unique=False
    )


def downgrade() -> None:
    # Drop composite index
    op.drop_index('ix_audit_logs_group_occurred', table_name='audit_logs')

    # Recreate old single-column index
    op.create_index(
        'ix_audit_logs_group_id',
        'audit_logs',
        ['group_id'],
        unique=False
    )

"""Optimize audit index

Revision ID: 018_optimize_audit_index
Revises: 017_optimize_finance_user_index, 016_optimize_chores_indexes
Create Date: 2026-02-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_index'
down_revision: Union[str, Sequence[str], None] = ('017_optimize_finance_user_index', '016_optimize_chores_indexes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create composite index for audit logs (group_id + occurred_at)
    op.create_index(
        'ix_audit_logs_group_occurred',
        'audit_logs',
        ['group_id', 'occurred_at'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_audit_logs_group_occurred', table_name='audit_logs')

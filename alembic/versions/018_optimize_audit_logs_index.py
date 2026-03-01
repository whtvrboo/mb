"""Optimize audit logs index

Revision ID: 018_optimize_audit_logs_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-02-14 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_logs_index'
down_revision: Union[str, None] = '017_optimize_finance_user_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old single-column index
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')

    # Create new composite index
    op.create_index(
        'ix_audit_logs_entity_type_id_time',
        'audit_logs',
        ['entity_type', 'entity_id', 'occurred_at'],
        unique=False
    )


def downgrade() -> None:
    # Drop new composite index
    op.drop_index('ix_audit_logs_entity_type_id_time', table_name='audit_logs')

    # Recreate old single-column index
    op.create_index(
        'ix_audit_logs_entity_id',
        'audit_logs',
        ['entity_id'],
        unique=False
    )

"""Optimize audit index

Revision ID: 018_optimize_audit_index
Revises: 017_optimize_finance_user_index
Create Date: 2026-03-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_index'
down_revision: Union[str, None] = '017_optimize_finance_user_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old index on entity_id
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')

    # Create composite index for filtering by entity_type + entity_id and sorting by occurred_at
    op.create_index(
        'ix_audit_logs_entity_lookup',
        'audit_logs',
        ['entity_type', 'entity_id', 'occurred_at'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_audit_logs_entity_lookup', table_name='audit_logs')

    op.create_index(
        'ix_audit_logs_entity_id',
        'audit_logs',
        ['entity_id'],
        unique=False
    )

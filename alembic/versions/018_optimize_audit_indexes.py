"""Optimize audit logs and tag assignments indexes.

Revision ID: 018_optimize_audit_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-01-30 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_indexes'
down_revision: Union[str, None] = '017_optimize_finance_user_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Audit Logs
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id', 'occurred_at'], unique=False)

    # Tag Assignments
    op.drop_index('ix_tag_assignments_entity_id', table_name='tag_assignments')
    op.create_index('ix_tag_assignments_entity', 'tag_assignments', ['entity_type', 'entity_id'], unique=False)


def downgrade() -> None:
    # Tag Assignments
    op.drop_index('ix_tag_assignments_entity', table_name='tag_assignments')
    op.create_index('ix_tag_assignments_entity_id', 'tag_assignments', ['entity_id'], unique=False)

    # Audit Logs
    op.drop_index('ix_audit_logs_entity', table_name='audit_logs')
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'], unique=False)

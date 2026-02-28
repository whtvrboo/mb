"""Optimize audit indexes

Revision ID: 018_optimize_audit_indexes
Revises: 018_optimize_lists_index
Create Date: 2024-05-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_optimize_audit_indexes'
down_revision: Union[str, None] = ('016_optimize_chores_indexes', '017_optimize_finance_user_index')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # AuditLog changes
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_group_id', table_name='audit_logs')
    op.create_index('ix_audit_logs_entity_lookup', 'audit_logs', ['entity_type', 'entity_id', 'occurred_at'], unique=False)
    op.create_index('ix_audit_logs_group_occurred_at', 'audit_logs', ['group_id', 'occurred_at'], unique=False)

    # TagAssignment changes
    op.drop_index('ix_tag_assignments_entity_id', table_name='tag_assignments')
    op.create_index('ix_tag_assignments_entity_lookup', 'tag_assignments', ['entity_type', 'entity_id'], unique=False)


def downgrade() -> None:
    # TagAssignment changes
    op.drop_index('ix_tag_assignments_entity_lookup', table_name='tag_assignments')
    op.create_index('ix_tag_assignments_entity_id', 'tag_assignments', ['entity_id'], unique=False)

    # AuditLog changes
    op.drop_index('ix_audit_logs_group_occurred_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_entity_lookup', table_name='audit_logs')
    op.create_index('ix_audit_logs_group_id', 'audit_logs', ['group_id'], unique=False)
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'], unique=False)

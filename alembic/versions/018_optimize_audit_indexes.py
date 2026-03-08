"""Optimize audit logs and tag assignments indexes

Revision ID: 018_optimize_audit_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-05-24 10:00:00.000000

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
    # AuditLog optimizations
    # Drop the inefficient single-column index on entity_id
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')
    # Create composite index for polymorphic entity queries and sorting
    op.create_index(
        'ix_audit_logs_entity_history',
        'audit_logs',
        ['entity_type', 'entity_id', 'occurred_at']
    )

    # TagAssignment optimizations
    # Drop the inefficient single-column index on entity_id
    op.drop_index('ix_tag_assignments_entity_id', table_name='tag_assignments')
    # Create composite index for polymorphic entity queries
    op.create_index(
        'ix_tag_assignments_entity',
        'tag_assignments',
        ['entity_type', 'entity_id']
    )


def downgrade() -> None:
    # Revert TagAssignment optimizations
    op.drop_index('ix_tag_assignments_entity', table_name='tag_assignments')
    op.create_index('ix_tag_assignments_entity_id', 'tag_assignments', ['entity_id'], unique=False)

    # Revert AuditLog optimizations
    op.drop_index('ix_audit_logs_entity_history', table_name='audit_logs')
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'], unique=False)

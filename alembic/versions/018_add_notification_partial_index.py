"""Add notification partial index

Revision ID: 018_add_notification_partial_index
Revises: 017_optimize_finance_user_index, 016_optimize_chores_indexes
Create Date: 2024-05-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_add_notification_partial_index'
down_revision: Union[str, Sequence[str], None] = ('017_optimize_finance_user_index', '016_optimize_chores_indexes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create partial index for unread notifications
    # This optimizes get_unread_count and list_notifications(unread_only=True)
    op.create_index(
        'ix_notifications_unread',
        'notifications',
        ['user_id', 'created_at'],
        unique=False,
        postgresql_where=sa.text('is_read = false'),
        sqlite_where=sa.text('is_read = 0')
    )


def downgrade() -> None:
    op.drop_index('ix_notifications_unread', table_name='notifications')

"""Add reaction indexes

Revision ID: 018_add_reaction_indexes
Revises: 017_optimize_finance_user_index
Create Date: 2026-03-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_add_reaction_indexes'
down_revision: Union[str, None] = '017_optimize_finance_user_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create index for comment_id in reactions (optimizes loading comments with reactions)
    op.create_index(
        'ix_reactions_comment_id',
        'reactions',
        ['comment_id'],
        unique=False
    )

    # Drop incomplete index on target_id (created in 011_notifications)
    # Using if_exists logic implicitly by catching error or just assuming state
    # Alembic usually knows state, but for safety against partial runs:
    # We assume 011 ran, so it exists.
    op.drop_index('ix_reactions_target_id', table_name='reactions')

    # Create composite index for target lookup (optimizes polymorphic queries)
    op.create_index(
        'ix_reactions_target_lookup',
        'reactions',
        ['target_type', 'target_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_reactions_target_lookup', table_name='reactions')
    op.create_index('ix_reactions_target_id', 'reactions', ['target_id'], unique=False)
    op.drop_index('ix_reactions_comment_id', table_name='reactions')

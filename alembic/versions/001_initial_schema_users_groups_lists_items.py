"""Initial schema: users, groups, lists, items

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create groups table
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create common_item_concepts table
    op.create_table(
        'common_item_concepts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create lists table
    op.create_table(
        'lists',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('store_name', sa.String(length=255), nullable=True),
        sa.Column('estimated_total', sa.Float(), nullable=True),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lists_group_id'), 'lists', ['group_id'], unique=False)

    # Create items table
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('list_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('quantity_value', sa.Float(), nullable=True),
        sa.Column('quantity_unit', sa.String(length=50), nullable=True),
        sa.Column('concept_id', sa.Integer(), nullable=True),
        sa.Column('is_checked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('checked_at', sa.DateTime(), nullable=True),
        sa.Column('price_estimate', sa.Float(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('added_by_id', sa.Integer(), nullable=True),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['added_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['concept_id'], ['common_item_concepts.id'], ),
        sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_list_id'), 'items', ['list_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_items_list_id'), table_name='items')
    op.drop_table('items')
    op.drop_index(op.f('ix_lists_group_id'), table_name='lists')
    op.drop_table('lists')
    op.drop_table('common_item_concepts')
    op.drop_table('groups')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

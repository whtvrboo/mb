"""Core extension: extend users/groups, add auth tables

Revision ID: 002_auth_core_ext
Revises: 001_initial
Create Date: 2026-01-29 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_auth_core_ext'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter users table - add missing columns
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=False, server_default=''))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('birth_date', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('users', sa.Column('language_code', sa.String(length=10), nullable=False, server_default='en'))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)

    # Alter groups table - add missing columns
    op.add_column('groups', sa.Column('default_currency', sa.String(length=3), nullable=False, server_default='USD'))
    op.add_column('groups', sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'))
    op.add_column('groups', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    op.add_column('groups', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('groups', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('groups', sa.Column('lease_start_date', sa.DateTime(), nullable=True))
    op.add_column('groups', sa.Column('lease_end_date', sa.DateTime(), nullable=True))
    op.add_column('groups', sa.Column('landlord_contact_id', sa.Integer(), nullable=True))
    op.add_column('groups', sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # Alter common_item_concepts table - add missing columns
    op.add_column('common_item_concepts', sa.Column('default_category_id', sa.Integer(), nullable=True))
    op.add_column('common_item_concepts', sa.Column('barcode', sa.String(length=100), nullable=True))
    op.add_column('common_item_concepts', sa.Column('average_price', sa.Float(), nullable=True))
    op.add_column('common_item_concepts', sa.Column('image_url', sa.String(length=500), nullable=True))

    # Create user_groups table
    op.create_table(
        'user_groups',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('nickname', sa.String(length=255), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'group_id', name='uq_user_group_active'),
        sa.CheckConstraint("role IN ('ADMIN', 'MEMBER', 'GUEST', 'CHILD')", name='ck_user_group_role')
    )
    op.create_index(op.f('ix_user_groups_user_id'), 'user_groups', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_groups_group_id'), 'user_groups', ['group_id'], unique=False)

    # Create invites table
    op.create_table(
        'invites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('email_hint', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='MEMBER'),
        sa.Column('max_uses', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('use_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_invites_group_id'), 'invites', ['group_id'], unique=False)
    op.create_index(op.f('ix_invites_code'), 'invites', ['code'], unique=True)

    # Create locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('floor_level', sa.Integer(), nullable=True),
        sa.Column('sunlight_direction', sa.String(length=20), nullable=True),
        sa.Column('humidity_level', sa.String(length=20), nullable=True),
        sa.Column('temperature_avg_celsius', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_group_id'), 'locations', ['group_id'], unique=False)

    # Create service_contacts table
    op.create_table(
        'service_contacts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('job_title', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('emergency_contact', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_contacts_group_id'), 'service_contacts', ['group_id'], unique=False)

    # Add FK from groups.landlord_contact_id to service_contacts (deferred, will be added after service_contacts exists)
    op.create_foreign_key('fk_groups_landlord_contact', 'groups', 'service_contacts', ['landlord_contact_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_groups_landlord_contact', 'groups', type_='foreignkey')
    op.drop_index(op.f('ix_service_contacts_group_id'), table_name='service_contacts')
    op.drop_table('service_contacts')
    op.drop_index(op.f('ix_locations_group_id'), table_name='locations')
    op.drop_table('locations')
    op.drop_index(op.f('ix_invites_code'), table_name='invites')
    op.drop_index(op.f('ix_invites_group_id'), table_name='invites')
    op.drop_table('invites')
    op.drop_index(op.f('ix_user_groups_group_id'), table_name='user_groups')
    op.drop_index(op.f('ix_user_groups_user_id'), table_name='user_groups')
    op.drop_table('user_groups')
    op.drop_column('common_item_concepts', 'image_url')
    op.drop_column('common_item_concepts', 'average_price')
    op.drop_column('common_item_concepts', 'barcode')
    op.drop_column('common_item_concepts', 'default_category_id')
    op.drop_column('groups', 'deleted_at')
    op.drop_column('groups', 'landlord_contact_id')
    op.drop_column('groups', 'lease_end_date')
    op.drop_column('groups', 'lease_start_date')
    op.drop_column('groups', 'address')
    op.drop_column('groups', 'description')
    op.drop_column('groups', 'avatar_url')
    op.drop_column('groups', 'timezone')
    op.drop_column('groups', 'default_currency')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'language_code')
    op.drop_column('users', 'preferences')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'is_superuser')
    op.drop_column('users', 'birth_date')
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'hashed_password')

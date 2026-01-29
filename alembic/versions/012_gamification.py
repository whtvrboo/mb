"""Gamification module: points, achievements, streaks, leaderboards

Revision ID: 012_gamification
Revises: 011_notifications
Create Date: 2026-01-29 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '012_gamification'
down_revision: Union[str, None] = '011_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create achievements table (needed before user_achievements)
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('badge_icon_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('requirement_type', sa.String(length=20), nullable=False),
        sa.Column('requirement_value', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_points table
    op.create_table(
        'user_points',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('total_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('monthly_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_reset_at', sa.DateTime(), nullable=True),
        sa.Column('rank_position', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('total_points >= 0', name='ck_user_points_total_non_negative'),
        sa.CheckConstraint('monthly_points >= 0', name='ck_user_points_monthly_non_negative')
    )
    op.create_index(op.f('ix_user_points_user_id'), 'user_points', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_points_group_id'), 'user_points', ['group_id'], unique=False)

    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('earned_at', sa.DateTime(), nullable=False),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='ck_user_achievement_progress')
    )
    op.create_index(op.f('ix_user_achievements_user_id'), 'user_achievements', ['user_id'], unique=False)

    # Create streaks table
    op.create_table(
        'streaks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('current_streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('current_streak_days >= 0', name='ck_streak_current_non_negative'),
        sa.CheckConstraint('longest_streak_days >= 0', name='ck_streak_longest_non_negative')
    )
    op.create_index(op.f('ix_streaks_user_id'), 'streaks', ['user_id'], unique=False)
    op.create_index(op.f('ix_streaks_group_id'), 'streaks', ['group_id'], unique=False)

    # Create leaderboards table
    op.create_table(
        'leaderboards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('metric', sa.String(length=50), nullable=False),
        sa.Column('period_start_date', sa.DateTime(), nullable=False),
        sa.Column('period_end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leaderboards_group_id'), 'leaderboards', ['group_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_leaderboards_group_id'), table_name='leaderboards')
    op.drop_table('leaderboards')
    op.drop_index(op.f('ix_streaks_group_id'), table_name='streaks')
    op.drop_index(op.f('ix_streaks_user_id'), table_name='streaks')
    op.drop_table('streaks')
    op.drop_index(op.f('ix_user_achievements_user_id'), table_name='user_achievements')
    op.drop_table('user_achievements')
    op.drop_index(op.f('ix_user_points_group_id'), table_name='user_points')
    op.drop_index(op.f('ix_user_points_user_id'), table_name='user_points')
    op.drop_table('user_points')
    op.drop_table('achievements')

"""Recipes module: recipes, ingredients, steps, meal plans, plus list extensions

Revision ID: 010_recipes
Revises: 009_assets
Create Date: 2026-01-29 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '010_recipes'
down_revision: Union[str, None] = '009_assets'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create list_shares table (from lists module)
    op.create_table(
        'list_shares',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('list_id', sa.Integer(), nullable=False),
        sa.Column('share_code', sa.String(length=100), nullable=False),
        sa.Column('can_edit', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('share_code')
    )
    op.create_index(op.f('ix_list_shares_list_id'), 'list_shares', ['list_id'], unique=False)
    op.create_index(op.f('ix_list_shares_share_code'), 'list_shares', ['share_code'], unique=True)

    # Create inventory_items table (from lists module)
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('concept_id', sa.Integer(), nullable=True),
        sa.Column('quantity_value', sa.Float(), nullable=True),
        sa.Column('quantity_unit', sa.String(length=50), nullable=True),
        sa.Column('expiration_date', sa.DateTime(), nullable=True),
        sa.Column('opened_date', sa.DateTime(), nullable=True),
        sa.Column('restock_threshold', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['concept_id'], ['common_item_concepts.id'], ),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_items_group_id'), 'inventory_items', ['group_id'], unique=False)

    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('owner_user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cuisine_type', sa.String(length=100), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=True),
        sa.Column('prep_time_minutes', sa.Integer(), nullable=False),
        sa.Column('cook_time_minutes', sa.Integer(), nullable=False),
        sa.Column('servings', sa.Integer(), nullable=False),
        sa.Column('calories_per_serving', sa.Integer(), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('times_cooked', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('prep_time_minutes >= 0', name='ck_recipe_prep_time'),
        sa.CheckConstraint('cook_time_minutes >= 0', name='ck_recipe_cook_time'),
        sa.CheckConstraint('servings > 0', name='ck_recipe_servings_positive')
    )
    op.create_index(op.f('ix_recipes_group_id'), 'recipes', ['group_id'], unique=False)

    # Create recipe_ingredients table
    op.create_table(
        'recipe_ingredients',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('quantity_value', sa.Float(), nullable=True),
        sa.Column('quantity_unit', sa.String(length=50), nullable=True),
        sa.Column('item_concept_id', sa.Integer(), nullable=True),
        sa.Column('is_optional', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('preparation_note', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['item_concept_id'], ['common_item_concepts.id'], ),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipe_ingredients_recipe_id'), 'recipe_ingredients', ['recipe_id'], unique=False)

    # Create recipe_steps table
    op.create_table(
        'recipe_steps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('instruction', sa.Text(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create meal_plans table
    op.create_table(
        'meal_plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('plan_date', sa.Date(), nullable=False),
        sa.Column('meal_type', sa.String(length=20), nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('assigned_cook_id', sa.Integer(), nullable=True),
        sa.Column('servings_planned', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_cook_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_plans_group_id'), 'meal_plans', ['group_id'], unique=False)

    # Create meal_plan_shopping_syncs table
    op.create_table(
        'meal_plan_shopping_syncs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('meal_plan_id', sa.Integer(), nullable=False),
        sa.Column('list_id', sa.Integer(), nullable=False),
        sa.Column('synced_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ),
        sa.ForeignKeyConstraint(['meal_plan_id'], ['meal_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_plan_shopping_syncs_meal_plan_id'), 'meal_plan_shopping_syncs', ['meal_plan_id'], unique=False)
    op.create_index(op.f('ix_meal_plan_shopping_syncs_list_id'), 'meal_plan_shopping_syncs', ['list_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_meal_plan_shopping_syncs_list_id'), table_name='meal_plan_shopping_syncs')
    op.drop_index(op.f('ix_meal_plan_shopping_syncs_meal_plan_id'), table_name='meal_plan_shopping_syncs')
    op.drop_table('meal_plan_shopping_syncs')
    op.drop_index(op.f('ix_meal_plans_group_id'), table_name='meal_plans')
    op.drop_table('meal_plans')
    op.drop_table('recipe_steps')
    op.drop_index(op.f('ix_recipe_ingredients_recipe_id'), table_name='recipe_ingredients')
    op.drop_table('recipe_ingredients')
    op.drop_index(op.f('ix_recipes_group_id'), table_name='recipes')
    op.drop_table('recipes')
    op.drop_index(op.f('ix_inventory_items_group_id'), table_name='inventory_items')
    op.drop_table('inventory_items')
    op.drop_index(op.f('ix_list_shares_share_code'), table_name='list_shares')
    op.drop_index(op.f('ix_list_shares_list_id'), table_name='list_shares')
    op.drop_table('list_shares')

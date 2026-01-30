"""Recipes module service layer. PRIVATE - other modules import from interface.py."""

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError
from mitlist.modules.recipes.models import (
    MealPlan,
    MealPlanShoppingSync,
    Recipe,
    RecipeIngredient,
    RecipeStep,
)


# ---------- Recipes ----------
async def list_recipes(
    db: AsyncSession,
    group_id: int,
    cuisine_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_favorite: Optional[bool] = None,
) -> list[Recipe]:
    """List recipes for a group with optional filters."""
    q = (
        select(Recipe)
        .where(Recipe.group_id == group_id)
        .options(selectinload(Recipe.ingredients), selectinload(Recipe.steps))
    )
    if cuisine_type is not None:
        q = q.where(Recipe.cuisine_type == cuisine_type)
    if difficulty is not None:
        q = q.where(Recipe.difficulty == difficulty)
    if is_favorite is not None:
        q = q.where(Recipe.is_favorite == is_favorite)
    q = q.order_by(Recipe.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_recipe_by_id(db: AsyncSession, recipe_id: int) -> Optional[Recipe]:
    """Get a recipe by ID with ingredients and steps."""
    result = await db.execute(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(selectinload(Recipe.ingredients), selectinload(Recipe.steps))
    )
    return result.scalar_one_or_none()


async def create_recipe(
    db: AsyncSession,
    group_id: int,
    owner_user_id: int,
    title: str,
    prep_time_minutes: int,
    cook_time_minutes: int,
    servings: int,
    description: Optional[str] = None,
    cuisine_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    calories_per_serving: Optional[int] = None,
    photo_url: Optional[str] = None,
    source_url: Optional[str] = None,
    ingredients: Optional[list[dict]] = None,
    steps: Optional[list[dict]] = None,
) -> Recipe:
    """Create a new recipe with ingredients and steps."""
    recipe = Recipe(
        group_id=group_id,
        owner_user_id=owner_user_id,
        title=title,
        description=description,
        cuisine_type=cuisine_type,
        difficulty=difficulty,
        prep_time_minutes=prep_time_minutes,
        cook_time_minutes=cook_time_minutes,
        servings=servings,
        calories_per_serving=calories_per_serving,
        photo_url=photo_url,
        source_url=source_url,
    )
    db.add(recipe)
    await db.flush()
    await db.refresh(recipe)

    # Add ingredients
    if ingredients:
        for ing in ingredients:
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                name=ing["name"],
                quantity_value=ing.get("quantity_value"),
                quantity_unit=ing.get("quantity_unit"),
                item_concept_id=ing.get("item_concept_id"),
                is_optional=ing.get("is_optional", False),
                preparation_note=ing.get("preparation_note"),
            )
            db.add(ingredient)

    # Add steps
    if steps:
        for step in steps:
            recipe_step = RecipeStep(
                recipe_id=recipe.id,
                step_number=step["step_number"],
                instruction=step["instruction"],
                duration_minutes=step.get("duration_minutes"),
                photo_url=step.get("photo_url"),
            )
            db.add(recipe_step)

    await db.flush()
    await db.refresh(recipe)
    return recipe


async def update_recipe(
    db: AsyncSession,
    recipe_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    cuisine_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    prep_time_minutes: Optional[int] = None,
    cook_time_minutes: Optional[int] = None,
    servings: Optional[int] = None,
    calories_per_serving: Optional[int] = None,
    photo_url: Optional[str] = None,
    source_url: Optional[str] = None,
    is_favorite: Optional[bool] = None,
) -> Recipe:
    """Update a recipe."""
    recipe = await get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise NotFoundError(code="RECIPE_NOT_FOUND", detail=f"Recipe {recipe_id} not found")

    if title is not None:
        recipe.title = title
    if description is not None:
        recipe.description = description
    if cuisine_type is not None:
        recipe.cuisine_type = cuisine_type
    if difficulty is not None:
        recipe.difficulty = difficulty
    if prep_time_minutes is not None:
        recipe.prep_time_minutes = prep_time_minutes
    if cook_time_minutes is not None:
        recipe.cook_time_minutes = cook_time_minutes
    if servings is not None:
        recipe.servings = servings
    if calories_per_serving is not None:
        recipe.calories_per_serving = calories_per_serving
    if photo_url is not None:
        recipe.photo_url = photo_url
    if source_url is not None:
        recipe.source_url = source_url
    if is_favorite is not None:
        recipe.is_favorite = is_favorite

    await db.flush()
    await db.refresh(recipe)
    return recipe


async def delete_recipe(db: AsyncSession, recipe_id: int) -> None:
    """Delete a recipe."""
    recipe = await get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise NotFoundError(code="RECIPE_NOT_FOUND", detail=f"Recipe {recipe_id} not found")
    await db.delete(recipe)
    await db.flush()


async def record_cooked(db: AsyncSession, recipe_id: int) -> Recipe:
    """Record that a recipe was cooked (increment times_cooked)."""
    recipe = await get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise NotFoundError(code="RECIPE_NOT_FOUND", detail=f"Recipe {recipe_id} not found")
    recipe.times_cooked += 1
    await db.flush()
    await db.refresh(recipe)
    return recipe


# ---------- Meal Plans ----------
async def list_meal_plans(
    db: AsyncSession,
    group_id: int,
    week_start: Optional[date] = None,
) -> list[MealPlan]:
    """List meal plans for a group, optionally for a specific week."""
    q = select(MealPlan).where(MealPlan.group_id == group_id)
    if week_start:
        week_end = week_start + timedelta(days=7)
        q = q.where(MealPlan.plan_date >= week_start, MealPlan.plan_date < week_end)
    q = q.order_by(MealPlan.plan_date, MealPlan.meal_type)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_meal_plan_by_id(db: AsyncSession, meal_plan_id: int) -> Optional[MealPlan]:
    """Get a meal plan by ID."""
    result = await db.execute(select(MealPlan).where(MealPlan.id == meal_plan_id))
    return result.scalar_one_or_none()


async def create_meal_plan(
    db: AsyncSession,
    group_id: int,
    plan_date: date,
    meal_type: str,
    recipe_id: Optional[int] = None,
    assigned_cook_id: Optional[int] = None,
    servings_planned: Optional[int] = None,
    notes: Optional[str] = None,
) -> MealPlan:
    """Create a new meal plan."""
    meal_plan = MealPlan(
        group_id=group_id,
        plan_date=plan_date,
        meal_type=meal_type,
        recipe_id=recipe_id,
        assigned_cook_id=assigned_cook_id,
        servings_planned=servings_planned,
        notes=notes,
    )
    db.add(meal_plan)
    await db.flush()
    await db.refresh(meal_plan)
    return meal_plan


async def update_meal_plan(
    db: AsyncSession,
    meal_plan_id: int,
    plan_date: Optional[date] = None,
    meal_type: Optional[str] = None,
    recipe_id: Optional[int] = None,
    assigned_cook_id: Optional[int] = None,
    servings_planned: Optional[int] = None,
    notes: Optional[str] = None,
    is_completed: Optional[bool] = None,
) -> MealPlan:
    """Update a meal plan."""
    meal_plan = await get_meal_plan_by_id(db, meal_plan_id)
    if not meal_plan:
        raise NotFoundError(code="MEAL_PLAN_NOT_FOUND", detail=f"Meal plan {meal_plan_id} not found")

    if plan_date is not None:
        meal_plan.plan_date = plan_date
    if meal_type is not None:
        meal_plan.meal_type = meal_type
    if recipe_id is not None:
        meal_plan.recipe_id = recipe_id
    if assigned_cook_id is not None:
        meal_plan.assigned_cook_id = assigned_cook_id
    if servings_planned is not None:
        meal_plan.servings_planned = servings_planned
    if notes is not None:
        meal_plan.notes = notes
    if is_completed is not None:
        meal_plan.is_completed = is_completed

    await db.flush()
    await db.refresh(meal_plan)
    return meal_plan


async def delete_meal_plan(db: AsyncSession, meal_plan_id: int) -> None:
    """Delete a meal plan."""
    meal_plan = await get_meal_plan_by_id(db, meal_plan_id)
    if not meal_plan:
        raise NotFoundError(code="MEAL_PLAN_NOT_FOUND", detail=f"Meal plan {meal_plan_id} not found")
    await db.delete(meal_plan)
    await db.flush()


async def sync_recipe_to_list(
    db: AsyncSession,
    recipe_id: int,
    list_id: int,
) -> list[dict]:
    """
    Sync recipe ingredients to a shopping list.

    Returns list of items added.
    """
    recipe = await get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise NotFoundError(code="RECIPE_NOT_FOUND", detail=f"Recipe {recipe_id} not found")

    # Import list service to add items
    from mitlist.modules.lists.interface import bulk_add_items, get_list_by_id

    list_obj = await get_list_by_id(db, list_id)
    if not list_obj:
        raise NotFoundError(code="LIST_NOT_FOUND", detail=f"List {list_id} not found")

    # Prepare items from ingredients
    items_to_add = []
    for ing in recipe.ingredients:
        items_to_add.append({
            "name": ing.name,
            "quantity_value": ing.quantity_value,
            "quantity_unit": ing.quantity_unit,
            "notes": ing.preparation_note,
        })

    # Add items to list
    created_items = await bulk_add_items(db, list_id, items_to_add)

    return [{"id": item.id, "name": item.name} for item in created_items]


def get_weekly_meal_plan_summary(
    meal_plans: list[MealPlan],
    group_id: int,
    week_start: date,
) -> dict:
    """Generate weekly meal plan summary."""
    week_end = week_start + timedelta(days=6)
    recipe_ids = {mp.recipe_id for mp in meal_plans if mp.recipe_id}

    return {
        "group_id": group_id,
        "week_start": week_start,
        "week_end": week_end,
        "meal_plans": meal_plans,
        "total_meals_planned": len(meal_plans),
        "recipes_used": len(recipe_ids),
    }

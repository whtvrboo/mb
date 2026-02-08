"""Recipes & Meal Planning module FastAPI router."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_group_id, get_current_user, get_db
from mitlist.core.errors import NotFoundError
from mitlist.modules.auth.interface import require_member
from mitlist.modules.auth.models import User
from mitlist.modules.recipes import schemas, service

router = APIRouter(tags=["recipes", "content"])


@router.get("/recipes", response_model=list[schemas.RecipeResponse])
async def get_recipes(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cuisine_type: str | None = None,
    difficulty: str | None = None,
    is_favorite: bool | None = None,
):
    """List recipes for the current group."""
    await require_member(db, group_id, user.id)
    recipes = await service.list_recipes(
        db,
        group_id,
        cuisine_type=cuisine_type,
        difficulty=difficulty,
        is_favorite=is_favorite,
    )
    return [schemas.RecipeResponse.model_validate(r) for r in recipes]


@router.post("/recipes", response_model=schemas.RecipeResponse, status_code=status.HTTP_201_CREATED)
async def post_recipes(
    data: schemas.RecipeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new recipe."""
    await require_member(db, data.group_id, user.id)
    recipe = await service.create_recipe(
        db,
        group_id=data.group_id,
        owner_user_id=user.id,
        title=data.title,
        description=data.description,
        cuisine_type=data.cuisine_type,
        difficulty=data.difficulty,
        prep_time_minutes=data.prep_time_minutes,
        cook_time_minutes=data.cook_time_minutes,
        servings=data.servings,
        calories_per_serving=data.calories_per_serving,
        photo_url=data.photo_url,
        source_url=data.source_url,
        ingredients=[ing.model_dump() for ing in data.ingredients],
        steps=[step.model_dump() for step in data.steps],
    )
    # Re-fetch with relationships loaded so response serializes without lazy-load
    recipe = await service.get_recipe_by_id(db, recipe.id)
    return schemas.RecipeResponse.model_validate(recipe)


@router.get("/recipes/{recipe_id}", response_model=schemas.RecipeResponse)
async def get_recipe(
    recipe_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific recipe by ID."""
    recipe = await service.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise NotFoundError(code="RECIPE_NOT_FOUND", detail=f"Recipe {recipe_id} not found")
    await require_member(db, recipe.group_id, user.id)
    return schemas.RecipeResponse.model_validate(recipe)


@router.get("/meal-plans", response_model=schemas.WeeklyMealPlanResponse)
async def get_meal_plans(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    week_start: date | None = Query(None, description="Start of week (defaults to current week)"),
):
    """Get weekly meal plans for the current group."""
    await require_member(db, group_id, user.id)

    # Default to current week start (Monday)
    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    # Performance: Load recipes eagerly to avoid N+1 queries during serialization
    meal_plans = await service.list_meal_plans(
        db, group_id, week_start=week_start, load_recipes=True
    )

    # Get recipes for meal plans that have them
    meal_plan_responses = []
    for mp in meal_plans:
        mp_response = schemas.MealPlanResponse.model_validate(mp)
        recipe = None
        if mp.recipe:
            recipe = schemas.RecipeResponse.model_validate(mp.recipe)
        meal_plan_responses.append(
            schemas.MealPlanWithRecipeResponse(
                **mp_response.model_dump(),
                recipe=recipe,
            )
        )

    week_end = week_start + timedelta(days=6)
    recipe_ids = {mp.recipe_id for mp in meal_plans if mp.recipe_id}

    return schemas.WeeklyMealPlanResponse(
        group_id=group_id,
        week_start=week_start,
        week_end=week_end,
        meal_plans=meal_plan_responses,
        total_meals_planned=len(meal_plans),
        recipes_used=len(recipe_ids),
    )


@router.post("/meal-plans", response_model=schemas.MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def post_meal_plans(
    data: schemas.MealPlanCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new meal plan."""
    await require_member(db, data.group_id, user.id)
    meal_plan = await service.create_meal_plan(
        db,
        group_id=data.group_id,
        plan_date=data.plan_date,
        meal_type=data.meal_type,
        recipe_id=data.recipe_id,
        assigned_cook_id=data.assigned_cook_id,
        servings_planned=data.servings_planned,
        notes=data.notes,
    )
    return schemas.MealPlanResponse.model_validate(meal_plan)


@router.post("/recipes/{recipe_id}/sync-to-list")
async def post_recipes_sync_to_list(
    recipe_id: int,
    list_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync recipe ingredients to a shopping list."""
    recipe = await service.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise NotFoundError(code="RECIPE_NOT_FOUND", detail=f"Recipe {recipe_id} not found")
    await require_member(db, recipe.group_id, user.id)

    added_items = await service.sync_recipe_to_list(db, recipe_id, list_id)
    return {"items_added": len(added_items), "items": added_items}

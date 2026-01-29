"""Recipes & Meal Planning module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.recipes import schemas

router = APIRouter(tags=["recipes", "content"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/recipes", response_model=ListType[schemas.RecipeResponse])
async def get_recipes(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /recipes is not yet implemented")


@router.post("/recipes", response_model=schemas.RecipeResponse, status_code=status.HTTP_201_CREATED)
async def post_recipes(data: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /recipes is not yet implemented")


@router.get("/recipes/{recipe_id}", response_model=schemas.RecipeResponse)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /recipes/{id} is not yet implemented")


@router.get("/meal-plans", response_model=schemas.WeeklyMealPlanResponse)
async def get_meal_plans(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /meal-plans is not yet implemented")


@router.post("/meal-plans", response_model=schemas.MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def post_meal_plans(data: schemas.MealPlanCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /meal-plans is not yet implemented")


@router.post("/recipes/{recipe_id}/sync-to-list")
async def post_recipes_sync_to_list(recipe_id: int, list_id: int, db: AsyncSession = Depends(get_db)):
    _stub("POST /recipes/{id}/sync-to-list is not yet implemented")

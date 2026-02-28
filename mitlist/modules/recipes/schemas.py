"""Recipes module Pydantic schemas for request/response models."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ====================
# Recipe Schemas
# ====================
class RecipeIngredientInput(BaseModel):
    """Input schema for recipe ingredient when creating a recipe."""

    name: str = Field(..., min_length=1, max_length=255)
    quantity_value: Optional[float] = Field(None, ge=0)
    quantity_unit: Optional[str] = Field(None, max_length=50)
    item_concept_id: Optional[int] = None
    is_optional: bool = False
    preparation_note: Optional[str] = Field(None, max_length=500)


class RecipeStepInput(BaseModel):
    """Input schema for recipe step when creating a recipe."""

    step_number: int = Field(..., ge=1)
    instruction: str = Field(..., min_length=1)
    duration_minutes: Optional[int] = Field(None, ge=1)
    photo_url: Optional[str] = Field(None, max_length=500)


class RecipeBase(BaseModel):
    """Base recipe schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cuisine_type: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[str] = Field(None, pattern="^(EASY|MEDIUM|HARD)$")
    prep_time_minutes: int = Field(..., ge=0)
    cook_time_minutes: int = Field(..., ge=0)
    servings: int = Field(..., ge=1)
    calories_per_serving: Optional[int] = Field(None, ge=0)
    photo_url: Optional[str] = Field(None, max_length=500)
    source_url: Optional[str] = Field(None, max_length=500)


class RecipeCreate(RecipeBase):
    """Schema for creating a recipe."""

    group_id: int
    ingredients: list[RecipeIngredientInput] = Field(default_factory=list, max_length=100)
    steps: list[RecipeStepInput] = Field(default_factory=list, max_length=100)


class RecipeUpdate(BaseModel):
    """Schema for updating a recipe."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    cuisine_type: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[str] = Field(None, pattern="^(EASY|MEDIUM|HARD)$")
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    calories_per_serving: Optional[int] = Field(None, ge=0)
    photo_url: Optional[str] = Field(None, max_length=500)
    source_url: Optional[str] = Field(None, max_length=500)
    is_favorite: Optional[bool] = None


class RecipeIngredientResponse(BaseModel):
    """Schema for recipe ingredient response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    recipe_id: int
    name: str
    quantity_value: Optional[float] = None
    quantity_unit: Optional[str] = None
    item_concept_id: Optional[int] = None
    is_optional: bool
    preparation_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RecipeStepResponse(BaseModel):
    """Schema for recipe step response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    recipe_id: int
    step_number: int
    instruction: str
    duration_minutes: Optional[int] = None
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RecipeResponse(RecipeBase):
    """Schema for recipe response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    owner_user_id: int
    is_favorite: bool
    times_cooked: int
    created_at: datetime
    updated_at: datetime
    ingredients: list[RecipeIngredientResponse] = Field(default_factory=list)
    steps: list[RecipeStepResponse] = Field(default_factory=list)


class RecipeRecordCookedRequest(BaseModel):
    """Schema for recording that a recipe was cooked."""

    servings_made: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None


# ====================
# RecipeIngredient Management Schemas
# ====================
class RecipeIngredientCreate(RecipeIngredientInput):
    """Schema for adding an ingredient to existing recipe."""

    recipe_id: int


class RecipeIngredientUpdate(BaseModel):
    """Schema for updating an ingredient."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity_value: Optional[float] = Field(None, ge=0)
    quantity_unit: Optional[str] = Field(None, max_length=50)
    item_concept_id: Optional[int] = None
    is_optional: Optional[bool] = None
    preparation_note: Optional[str] = Field(None, max_length=500)


# ====================
# RecipeStep Management Schemas
# ====================
class RecipeStepCreate(RecipeStepInput):
    """Schema for adding a step to existing recipe."""

    recipe_id: int


class RecipeStepUpdate(BaseModel):
    """Schema for updating a step."""

    step_number: Optional[int] = Field(None, ge=1)
    instruction: Optional[str] = Field(None, min_length=1)
    duration_minutes: Optional[int] = Field(None, ge=1)
    photo_url: Optional[str] = Field(None, max_length=500)


# ====================
# MealPlan Schemas
# ====================
class MealPlanBase(BaseModel):
    """Base meal plan schema."""

    plan_date: date
    meal_type: str = Field(..., pattern="^(BREAKFAST|LUNCH|DINNER|SNACK)$")
    recipe_id: Optional[int] = None
    assigned_cook_id: Optional[int] = None
    servings_planned: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None


class MealPlanCreate(MealPlanBase):
    """Schema for creating a meal plan."""

    group_id: int


class MealPlanUpdate(BaseModel):
    """Schema for updating a meal plan."""

    plan_date: Optional[date] = None
    meal_type: Optional[str] = Field(
        None, pattern="^(BREAKFAST|LUNCH|DINNER|SNACK)$"
    )
    recipe_id: Optional[int] = None
    assigned_cook_id: Optional[int] = None
    servings_planned: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    is_completed: Optional[bool] = None


class MealPlanResponse(MealPlanBase):
    """Schema for meal plan response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class MealPlanWithRecipeResponse(MealPlanResponse):
    """Schema for meal plan with embedded recipe details."""

    recipe: Optional[RecipeResponse] = None


# ====================
# MealPlanShoppingSync Schemas
# ====================
class MealPlanShoppingSyncBase(BaseModel):
    """Base meal plan shopping sync schema."""

    synced_at: datetime


class MealPlanShoppingSyncCreate(BaseModel):
    """Schema for creating a meal plan shopping sync."""

    meal_plan_id: int
    list_id: int


class MealPlanShoppingSyncResponse(MealPlanShoppingSyncBase):
    """Schema for meal plan shopping sync response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    meal_plan_id: int
    list_id: int
    created_at: datetime
    updated_at: datetime


class GenerateShoppingListRequest(BaseModel):
    """Schema for generating shopping list from meal plans."""

    meal_plan_ids: list[int] = Field(..., min_length=1, max_length=100)
    list_name: Optional[str] = Field(None, max_length=255)
    combine_duplicates: bool = True


class GenerateShoppingListResponse(BaseModel):
    """Schema for generated shopping list response."""

    list_id: int
    items_added: int
    meal_plans_synced: list[int]


# ====================
# Aggregation/Summary Schemas
# ====================
class WeeklyMealPlanResponse(BaseModel):
    """Schema for weekly meal plan."""

    group_id: int
    week_start: date
    week_end: date
    meal_plans: list[MealPlanWithRecipeResponse]
    total_meals_planned: int
    recipes_used: int


class RecipeSearchRequest(BaseModel):
    """Schema for recipe search."""

    group_id: int
    query: Optional[str] = None
    cuisine_type: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(EASY|MEDIUM|HARD)$")
    max_prep_time_minutes: Optional[int] = Field(None, ge=0)
    max_cook_time_minutes: Optional[int] = Field(None, ge=0)
    max_calories_per_serving: Optional[int] = Field(None, ge=0)
    is_favorite: Optional[bool] = None
    ingredient_names: Optional[list[str]] = None


class RecipeSuggestionResponse(BaseModel):
    """Schema for recipe suggestion based on available ingredients."""

    recipe: RecipeResponse
    match_percentage: float
    missing_ingredients: list[str]
    available_ingredients: list[str]


class CookingHistoryResponse(BaseModel):
    """Schema for cooking history."""

    recipe_id: int
    recipe_title: str
    times_cooked: int
    last_cooked_at: Optional[datetime] = None
    average_rating: Optional[float] = None

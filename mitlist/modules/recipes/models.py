"""Recipes module ORM models."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import Base, BaseModel, TimestampMixin


class Difficulty(str):
    """Recipe difficulty."""

    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class MealType(str):
    """Meal types."""

    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    SNACK = "SNACK"


class Recipe(BaseModel, TimestampMixin):
    """Recipe - cooking recipe."""

    __tablename__ = "recipes"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cuisine_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    prep_time_minutes: Mapped[int] = mapped_column(nullable=False)
    cook_time_minutes: Mapped[int] = mapped_column(nullable=False)
    servings: Mapped[int] = mapped_column(nullable=False)
    calories_per_serving: Mapped[Optional[int]] = mapped_column(nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_favorite: Mapped[bool] = mapped_column(default=False, nullable=False)
    times_cooked: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relationships
    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    steps: Mapped[list["RecipeStep"]] = relationship(
        "RecipeStep", back_populates="recipe", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("prep_time_minutes >= 0", name="ck_recipe_prep_time"),
        CheckConstraint("cook_time_minutes >= 0", name="ck_recipe_cook_time"),
        CheckConstraint("servings > 0", name="ck_recipe_servings_positive"),
    )


class RecipeIngredient(BaseModel, TimestampMixin):
    """Recipe ingredient."""

    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    quantity_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    item_concept_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("common_item_concepts.id"), nullable=True
    )
    is_optional: Mapped[bool] = mapped_column(default=False, nullable=False)
    preparation_note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")


class RecipeStep(BaseModel, TimestampMixin):
    """Recipe step - cooking instruction step."""

    __tablename__ = "recipe_steps"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="steps")


class MealPlan(BaseModel, TimestampMixin):
    """Meal plan - planned meal for a date."""

    __tablename__ = "meal_plans"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    plan_date: Mapped[date] = mapped_column(nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    recipe_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recipes.id"), nullable=True)
    assigned_cook_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    servings_planned: Mapped[Optional[int]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    recipe: Mapped[Optional["Recipe"]] = relationship("Recipe")


class MealPlanShoppingSync(BaseModel, TimestampMixin):
    """Meal plan shopping sync - link meal plan to shopping list."""

    __tablename__ = "meal_plan_shopping_syncs"

    meal_plan_id: Mapped[int] = mapped_column(
        ForeignKey("meal_plans.id"), nullable=False, index=True
    )
    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id"), nullable=False, index=True)
    synced_at: Mapped[datetime] = mapped_column(nullable=False)

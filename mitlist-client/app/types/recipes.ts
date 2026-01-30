/** Recipes module types: Recipe, MealPlan, Ingredient, Step */

export interface RecipeIngredientResponse {
  id: number
  recipe_id: number
  name: string
  quantity_value: number
  quantity_unit: string | null
  item_concept_id: number | null
  is_optional: boolean
  preparation_note: string | null
  created_at: string
  updated_at: string
}

export interface RecipeStepResponse {
  id: number
  recipe_id: number
  step_number: number
  instruction: string
  duration_minutes: number | null
  photo_url: string | null
  created_at: string
  updated_at: string
}

export interface RecipeResponse {
  id: number
  group_id: number
  owner_user_id: number
  title: string
  description: string | null
  cuisine_type: string | null
  difficulty: string | null
  prep_time_minutes: number | null
  cook_time_minutes: number | null
  servings: number | null
  calories_per_serving: number | null
  photo_url: string | null
  source_url: string | null
  is_favorite: boolean
  times_cooked: number
  created_at: string
  updated_at: string
  ingredients: RecipeIngredientResponse[]
  steps: RecipeStepResponse[]
}

export interface RecipeIngredientCreate {
  name: string
  quantity_value: number
  quantity_unit?: string | null
  item_concept_id?: number | null
  is_optional?: boolean
  preparation_note?: string | null
}

export interface RecipeStepCreate {
  step_number: number
  instruction: string
  duration_minutes?: number | null
  photo_url?: string | null
}

export interface RecipeCreate {
  group_id: number
  title: string
  description?: string | null
  cuisine_type?: string | null
  difficulty?: string | null
  prep_time_minutes?: number | null
  cook_time_minutes?: number | null
  servings?: number | null
  calories_per_serving?: number | null
  photo_url?: string | null
  source_url?: string | null
  ingredients: RecipeIngredientCreate[]
  steps: RecipeStepCreate[]
}

export interface MealPlanResponse {
  id: number
  group_id: number
  plan_date: string
  meal_type: string
  recipe_id: number | null
  assigned_cook_id: number | null
  servings_planned: number | null
  notes: string | null
  is_completed: boolean
  created_at: string
  updated_at: string
}

export interface MealPlanWithRecipeResponse extends MealPlanResponse {
  recipe: RecipeResponse | null
}

export interface WeeklyMealPlanResponse {
  group_id: number
  week_start: string
  week_end: string
  meal_plans: MealPlanWithRecipeResponse[]
  total_meals_planned: number
  recipes_used: number
}

export interface MealPlanCreate {
  group_id: number
  plan_date: string
  meal_type: string
  recipe_id?: number | null
  assigned_cook_id?: number | null
  servings_planned?: number | null
  notes?: string | null
}

import type {
  RecipeResponse,
  RecipeCreate,
  MealPlanResponse,
  MealPlanWithRecipeResponse,
  WeeklyMealPlanResponse,
  MealPlanCreate,
} from '~/types/recipes'

export function useRecipes() {
  const $api = useNuxtApp().$api

  return {
    listRecipes: (params?: {
      cuisine_type?: string
      difficulty?: string
      is_favorite?: boolean
    }) => useApi<RecipeResponse[]>('/recipes', { query: params }),
    getRecipe: (recipeId: number) =>
      useApi<RecipeResponse>(`/recipes/${recipeId}`),
    createRecipe: (data: RecipeCreate) =>
      $api<RecipeResponse>('/recipes', { method: 'POST', body: data }),

    getMealPlans: (params?: { week_start?: string }) =>
      useApi<WeeklyMealPlanResponse>('/meal-plans', { query: params }),
    createMealPlan: (data: MealPlanCreate) =>
      $api<MealPlanResponse>('/meal-plans', { method: 'POST', body: data }),

    syncRecipeToList: (recipeId: number, listId: number) =>
      $api<{ items_added: number; items: unknown[] }>(
        `/recipes/${recipeId}/sync-to-list`,
        { method: 'POST', query: { list_id: listId } },
      ),
  }
}

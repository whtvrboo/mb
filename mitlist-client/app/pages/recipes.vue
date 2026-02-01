<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRecipes } from '~/composables/useRecipes'
import RecipeCard from '~/components/RecipeCard.vue'
import type { RecipeResponse, WeeklyMealPlanResponse } from '~/types/recipes'

const { listRecipes, getMealPlans } = useRecipes()

const recipes = ref<RecipeResponse[]>([])
const mealPlan = ref<WeeklyMealPlanResponse | null>(null)
const isLoading = ref(true)

const fetchData = async () => {
    isLoading.value = true
    try {
        const [recipesData, mealPlanData] = await Promise.all([
            listRecipes({ limit: 10 }),
            getMealPlans()
        ])
        recipes.value = recipesData
        mealPlan.value = mealPlanData
        // Fix:
        // mealPlan.value = mealPlanData -> wait, type is WeeklyMealPlanResponse, so...
        // Actually getMealPlans returns WeeklyMealPlanResponse.
    } catch (e) {
        console.error('Failed to fetch recipes', e)
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchData()
})
</script>

<template>
    <div class="bg-background-light dark:bg-background-dark min-h-screen text-background-dark font-display pb-24">
        <header
            class="sticky top-0 z-50 bg-background-light border-b-[3px] border-background-dark px-5 h-16 flex items-center justify-between shadow-sm">
            <div class="flex items-center gap-3">
                <NuxtLink to="/"
                    class="flex items-center justify-center size-10 rounded-lg border-[2px] border-transparent hover:border-background-dark hover:bg-black/5 transition-colors">
                    <span class="material-symbols-outlined text-[28px]">arrow_back</span>
                </NuxtLink>
            </div>
            <h1 class="text-xl font-bold tracking-tight uppercase">Kitchen</h1>
            <div class="size-10 flex items-center justify-end">
                <span class="material-symbols-outlined text-[24px]">search</span>
            </div>
        </header>

        <main class="flex flex-col gap-8 p-5 max-w-lg mx-auto w-full">

            <!-- Meal Plan Section -->
            <section class="flex flex-col gap-4">
                <h2 class="text-lg font-bold uppercase tracking-wide flex items-center gap-2">
                    <span class="material-symbols-outlined">calendar_month</span> Weekly Menu
                </h2>

                <div
                    class="bg-white border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism min-h-[100px] flex items-center justify-center">
                    <span class="text-gray-400 font-medium">Meal plan coming soon...</span>
                </div>
            </section>

            <!-- Recipes List -->
            <section class="flex flex-col gap-4">
                <div class="flex items-center justify-between">
                    <h2 class="text-lg font-bold uppercase tracking-wide flex items-center gap-2">
                        <span class="material-symbols-outlined">menu_book</span> Cookbook
                    </h2>
                    <button
                        class="bg-primary px-3 py-1 rounded border-[2px] border-background-dark font-bold text-xs uppercase shadow-sm hover:translate-y-0.5 hover:shadow-none transition-all">
                        + New
                    </button>
                </div>

                <div v-if="isLoading" class="text-center py-10 opacity-50">Loading recipes...</div>
                <div v-else-if="recipes.length === 0" class="text-center py-10 opacity-50 font-bold">No recipes found.
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <RecipeCard v-for="recipe in recipes" :key="recipe.id" :recipe="recipe" />
                </div>
            </section>

        </main>
    </div>
</template>

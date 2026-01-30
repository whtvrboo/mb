<script setup lang="ts">
import type { RecipeResponse } from '~/types/recipes'

defineProps<{
    recipe: RecipeResponse
}>()
</script>

<template>
    <div
        class="group relative bg-white border-[3px] border-background-dark rounded-xl overflow-hidden shadow-neobrutalism hover:-translate-y-1 transition-transform cursor-pointer h-full flex flex-col">
        <!-- Image Placeholder -->
        <div
            class="h-40 bg-gray-200 border-b-[3px] border-background-dark flex items-center justify-center relative overflow-hidden">
            <span class="material-symbols-outlined text-6xl opacity-20 text-background-dark">restaurant_menu</span>
            <div
                class="absolute top-2 right-2 bg-white border-[2px] border-background-dark px-2 py-0.5 rounded text-xs font-bold uppercase shadow-sm">
                {{ recipe.cuisine_type || 'General' }}
            </div>
        </div>

        <div class="p-4 flex flex-col flex-1 gap-2">
            <h3 class="font-bold text-xl leading-tight line-clamp-2">{{ recipe.name }}</h3>

            <div class="flex flex-wrap gap-2 mt-auto pt-2">
                <span v-if="recipe.prep_time_minutes"
                    class="text-xs font-bold bg-background-light px-2 py-1 rounded border border-background-dark flex items-center gap-1">
                    <span class="material-symbols-outlined text-[14px]">schedule</span> {{ recipe.prep_time_minutes }}m
                </span>
                <span v-if="recipe.difficulty"
                    class="text-xs font-bold bg-background-light px-2 py-1 rounded border border-background-dark capitalize">
                    {{ recipe.difficulty }}
                </span>
            </div>
        </div>
    </div>
</template>

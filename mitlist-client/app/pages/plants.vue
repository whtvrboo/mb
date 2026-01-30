<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePlants } from '~/composables/usePlants'
import type { PlantResponse } from '~/types/plants'

const { listPlants } = usePlants()

const plants = ref<PlantResponse[]>([])
const isLoading = ref(true)

const fetchData = async () => {
    isLoading.value = true
    try {
        plants.value = await listPlants()
    } catch (e) {
        console.error('Failed to fetch plants', e)
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
            <h1 class="text-xl font-bold tracking-tight uppercase">My Plants</h1>
            <div class="size-10 flex items-center justify-end">
                <span class="material-symbols-outlined text-[24px]">add_circle</span>
            </div>
        </header>

        <main class="flex flex-col gap-6 p-5 max-w-lg mx-auto w-full">
            <div v-if="isLoading" class="text-center py-10 opacity-50">Loading jungle...</div>
            <div v-if="!isLoading && plants.length === 0" class="text-center py-10 opacity-50 font-bold">No plants added
                yet.</div>

            <div class="grid grid-cols-2 gap-4">
                <div v-for="plant in plants" :key="plant.id"
                    class="bg-[#A3B18A] border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism flex flex-col gap-3 group hover:-translate-y-1 transition-transform">
                    <div class="flex justify-between items-start">
                        <div
                            class="bg-white/90 border-[2px] border-background-dark px-2 py-0.5 rounded text-[10px] font-bold uppercase truncate max-w-[80px]">
                            {{ plant.location_id ? 'Living Room' : 'Valid Location' }}
                        </div>
                        <button
                            class="bg-white size-8 rounded-full border-[2px] border-background-dark flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <span class="material-symbols-outlined text-sm">water_drop</span>
                        </button>
                    </div>

                    <div class="mt-2">
                        <h3 class="font-bold text-xl leading-tight text-white drop-shadow-sm">{{ plant.nickname }}</h3>
                        <!-- <p class="text-xs font-bold text-white/70">{{ plant.species_name }}</p> -->
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

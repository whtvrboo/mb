<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePets } from '~/composables/usePets'
import type { PetResponse, PetScheduleResponse, PetMedicalRecordResponse } from '~/types/pets'

const { listPets, listSchedules, getExpiringVaccines } = usePets()

const pets = ref<PetResponse[]>([])
// For simplicity in this view, we'll store schedules in a map or just fetch for the first pet for now
const schedules = ref<Record<number, PetScheduleResponse[]>>({})
const alerts = ref<PetMedicalRecordResponse[]>([])
const isLoading = ref(true)

const fetchData = async () => {
    isLoading.value = true
    try {
        const [petsData, alertsData] = await Promise.all([
            listPets(),
            getExpiringVaccines({ days_ahead: 30 })
        ])
        pets.value = petsData
        alerts.value = alertsData

        // Fetch schedules for each pet
        // Parallelizing requests
        await Promise.all(pets.value.map(async (pet) => {
            const sched = await listSchedules(pet.id)
            schedules.value[pet.id] = sched
        }))
    } catch (e) {
        console.error('Failed to fetch pets data', e)
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchData()
})

const getPetIcon = (species: string) => {
    const s = species.toLowerCase()
    if (s.includes('cat')) return 'pets' // Specific cat icon if available? No, uses 'pets' usually
    if (s.includes('dog')) return 'pets'
    return 'pets'
}
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
            <h1 class="text-xl font-bold tracking-tight uppercase">Pet Care</h1>
            <div class="size-10 flex items-center justify-end">
                <span class="material-symbols-outlined text-[24px]">add_circle</span>
            </div>
        </header>

        <main class="flex flex-col gap-6 p-5 max-w-lg mx-auto w-full">

            <!-- Alerts -->
            <div v-if="alerts.length > 0"
                class="bg-red-100 border-[3px] border-red-500 rounded-xl p-4 flex items-start gap-3 shadow-neobrutalism-sm">
                <span class="material-symbols-outlined text-red-600">warning</span>
                <div class="flex flex-col">
                    <h3 class="font-bold text-red-700 uppercase">Vaccines Due</h3>
                    <ul class="text-sm font-bold text-red-600/80 list-disc list-inside">
                        <li v-for="alert in alerts" :key="alert.id">
                            {{ alert.record_type }} expiring soon
                        </li>
                    </ul>
                </div>
            </div>

            <div v-if="isLoading" class="text-center py-10 opacity-50">Loading pets...</div>
            <div v-if="!isLoading && pets.length === 0" class="text-center py-10 opacity-50 font-bold">No pets added
                yet.</div>

            <div v-for="pet in pets" :key="pet.id"
                class="flex flex-col gap-0 bg-[#8E9DB3] border-[3px] border-background-dark rounded-xl overflow-hidden shadow-neobrutalism">
                <!-- Header -->
                <div class="p-4 flex items-center justify-between bg-white border-b-[3px] border-background-dark">
                    <div class="flex items-center gap-3">
                        <div
                            class="size-12 rounded-full border-[2px] border-background-dark bg-gray-100 flex items-center justify-center overflow-hidden">
                            <span class="material-symbols-outlined text-2xl">{{ getPetIcon(pet.species) }}</span>
                        </div>
                        <div class="flex flex-col">
                            <h2 class="font-bold text-xl leading-none">{{ pet.name }}</h2>
                            <span class="text-xs font-bold opacity-60 uppercase">{{ pet.breed || pet.species }}</span>
                        </div>
                    </div>
                    <button
                        class="size-8 rounded border-[2px] border-background-dark flex items-center justify-center hover:bg-gray-100">
                        <span class="material-symbols-outlined">edit</span>
                    </button>
                </div>

                <!-- Schedules / Tasks -->
                <div class="p-4 flex flex-col gap-2">
                    <h3 class="font-bold text-white text-sm uppercase tracking-wider mb-1">Care Schedule</h3>

                    <div v-if="!schedules[pet.id] || schedules[pet.id].length === 0"
                        class="text-white/60 text-sm font-medium italic">
                        No schedules set.
                    </div>

                    <div v-for="task in schedules[pet.id]" :key="task.id"
                        class="bg-white border-[2px] border-background-dark rounded-lg p-3 flex items-center justify-between shadow-sm">
                        <div class="flex flex-col">
                            <span class="font-bold">{{ task.task_type }}</span>
                            <span class="text-xs opacity-60 font-bold">{{ task.frequency_cron || 'Daily' }}</span>
                        </div>
                        <button
                            class="bg-primary size-8 rounded border-[2px] border-background-dark flex items-center justify-center hover:scale-105 transition-transform">
                            <span class="material-symbols-outlined text-sm font-bold">check</span>
                        </button>
                    </div>
                </div>
            </div>

        </main>
    </div>
</template>

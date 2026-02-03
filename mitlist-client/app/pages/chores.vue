<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useChores } from '~/composables/useChores'
import type { UserChoreStatsResponse, ChoreAssignmentWithChoreResponse } from '~/types/chores'

const { getMyStats, listAssignments, completeAssignment } = useChores()

const stats = ref<UserChoreStatsResponse | null>(null)
const assignments = ref<ChoreAssignmentWithChoreResponse[]>([])
const isLoading = ref(true)
const filterMode = ref<'mine' | 'all'>('mine')

const filteredAssignments = computed(() => {
    if (filterMode.value === 'all') return assignments.value
    // If stats not loaded yet, show all or empty. defaulting to assignments.value to avoid empty flash if delayed
    if (!stats.value) return assignments.value
    return assignments.value.filter(a => a.assigned_to_id === stats.value?.user_id)
})

const fetchData = async () => {
    isLoading.value = true
    try {
        const [statsData, assignmentsData] = await Promise.all([
            getMyStats(),
            listAssignments({ status_filter: 'pending' }) // Fetch pending assignments
        ])
        stats.value = statsData
        assignments.value = assignmentsData
    } catch (e) {
        console.error('Failed to fetch chores data', e)
    } finally {
        isLoading.value = false
    }
}

const handleComplete = async (assignmentId: number) => {
    try {
        await completeAssignment(assignmentId, { completed_at: new Date().toISOString() })
        // Refresh or optimistically update
        assignments.value = assignments.value.filter(a => a.id !== assignmentId)
    } catch (e) {
        console.error('Failed to complete assignment', e)
    }
}

onMounted(() => {
    fetchData()
})
</script>

<template>
    <div class="bg-background-light dark:bg-background-dark min-h-screen text-background-dark font-display pb-28">
        <!-- Header -->
        <header
            class="sticky top-0 z-50 bg-background-light border-b-[3px] border-background-dark px-5 h-16 flex items-center justify-between shadow-sm">
            <div class="flex items-center gap-3">
                <NuxtLink to="/"
                    aria-label="Back to dashboard"
                    class="flex items-center justify-center size-10 rounded-lg border-[2px] border-transparent hover:border-background-dark hover:bg-black/5 transition-all">
                    <span class="material-symbols-outlined text-[28px]">arrow_back</span>
                </NuxtLink>
            </div>
            <h1 class="text-xl font-bold tracking-tight uppercase truncate">House Chores</h1>
            <div class="size-10 flex items-center justify-end">
                <div class="relative">
                    <span class="material-symbols-outlined text-[28px]">filter_list</span>
                    <div class="absolute -top-1 -right-1 size-3 bg-primary rounded-full border border-background-dark">
                    </div>
                </div>
            </div>
        </header>

        <main class="flex flex-col gap-6 p-5 max-w-lg mx-auto w-full">

            <!-- Stats / Points Card -->
            <section class="grid grid-cols-2 gap-4">
                <div
                    class="bg-white border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism flex flex-col justify-between h-32 relative overflow-hidden group">
                    <div
                        class="absolute -right-4 -top-4 bg-primary/20 size-20 rounded-full blur-xl group-hover:bg-primary/40 transition-colors">
                    </div>
                    <div class="flex flex-col z-10">
                        <span class="text-xs font-black uppercase tracking-widest opacity-60">Your Effort</span>
                        <h2 class="text-4xl font-black mt-1">{{ stats?.total_points || 0 }}</h2>
                    </div>
                    <div class="flex items-center gap-1 text-xs font-bold z-10">
                        <span class="text-green-600 bg-green-100 px-1 rounded">+15 pts</span>
                        <span class="opacity-60">this week</span>
                    </div>
                </div>

                <div
                    class="bg-background-dark text-white border-[3px] border-background-dark rounded-xl p-4 shadow-[4px_4px_0px_0px_#8E9DB3] flex flex-col justify-between h-32">
                    <div class="flex flex-col">
                        <span class="text-xs font-black uppercase tracking-widest opacity-60">Next Goal</span>
                        <h2 class="text-xl font-bold leading-tight mt-1">Pizza Night</h2>
                    </div>
                    <div class="w-full bg-white/20 h-2 rounded-full overflow-hidden">
                        <div class="bg-primary h-full w-3/4"></div>
                    </div>
                </div>
            </section>

            <!-- Toggle (My Tasks vs All) -->
            <div class="flex bg-white border-[3px] border-background-dark rounded-lg p-1 shadow-neobrutalism-sm" role="group" aria-label="Filter chores">
                <button
                    type="button"
                    @click="filterMode = 'mine'"
                    :aria-pressed="filterMode === 'mine'"
                    class="flex-1 py-2 rounded font-bold text-sm uppercase transition-all"
                    :class="filterMode === 'mine' ? 'bg-background-dark text-white shadow-sm' : 'hover:bg-gray-100 text-gray-500'">
                    My Tasks
                </button>
                <button
                    type="button"
                    @click="filterMode = 'all'"
                    :aria-pressed="filterMode === 'all'"
                    class="flex-1 py-2 rounded font-bold text-sm uppercase transition-all"
                    :class="filterMode === 'all' ? 'bg-background-dark text-white shadow-sm' : 'hover:bg-gray-100 text-gray-500'">
                    All Chores
                </button>
            </div>

            <!-- Task List -->
            <div class="flex flex-col gap-4">
                <h3 class="font-bold text-lg uppercase tracking-wide opacity-80 pl-1">Results</h3>

                <div v-if="isLoading" class="text-center py-4">Loading chores...</div>
                <div v-if="!isLoading && filteredAssignments.length === 0" class="text-center py-4 font-bold opacity-50">No
                    pending chores!</div>

                <div v-for="assignment in filteredAssignments" :key="assignment.id"
                    class="group relative bg-white border-[3px] border-background-dark rounded-xl p-0 shadow-neobrutalism transition-all hover:bg-gray-50 overflow-hidden">

                    <div class="flex p-4 gap-4 items-start">
                        <div class="mt-1">
                            <label class="relative cursor-pointer">
                                <input
                                    type="checkbox"
                                    class="peer sr-only"
                                    :aria-labelledby="`chore-title-${assignment.id}`"
                                    @change="handleComplete(assignment.id)"
                                />
                                <div
                                    class="size-7 border-[3px] border-background-dark rounded bg-white peer-checked:bg-primary transition-colors flex items-center justify-center hover:bg-gray-100">
                                    <span
                                        class="material-symbols-outlined text-sm opacity-0 peer-checked:opacity-100 font-bold">check</span>
                                </div>
                            </label>
                        </div>
                        <div class="flex-1 flex flex-col gap-1">
                            <div class="flex justify-between items-start">
                                <h4 :id="`chore-title-${assignment.id}`" class="font-bold text-xl leading-tight">{{ assignment.chore.name }}</h4>
                                <span
                                    class="text-xs font-black bg-primary/20 text-background-dark border border-background-dark/10 px-1.5 py-0.5 rounded uppercase">
                                    {{ assignment.chore.points_value }} pts
                                </span>
                            </div>
                            <div class="flex items-center gap-2 mt-1">
                                <span
                                    class="text-xs font-bold text-red-600 bg-red-50 border border-red-200 px-1.5 py-0.5 rounded flex items-center gap-1">
                                    <span class="material-symbols-outlined text-[14px]">calendar_today</span>
                                    {{ assignment.due_date ? new Date(assignment.due_date).toLocaleDateString() : 'No due date' }}
                                </span>
                                <span class="text-xs font-bold text-gray-500">• {{ assignment.chore.frequency_type ||
                                    'One-time' }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Completed Section -->
            <div
                class="mt-4 pt-4 border-t-[3px] border-dashed border-background-dark/30 opacity-60 hover:opacity-100 transition-opacity">
                <h3 class="font-bold text-sm uppercase tracking-widest text-gray-500 mb-3 flex items-center gap-2">
                    Completed Recently <span class="material-symbols-outlined text-lg">history</span>
                </h3>
                <!-- Placeholder for completed -->
            </div>

        </main>

        <!-- Floating Action Button -->
        <div class="fixed bottom-6 right-6 z-40">
            <NuxtLink to="/chores/rotation"
                aria-label="Manage chore rotations"
                class="size-16 bg-primary border-[3px] border-background-dark rounded-full shadow-neobrutalism-lg flex items-center justify-center hover:scale-110 active:scale-95 transition-all">
                <span class="material-symbols-outlined text-4xl font-bold">autorenew</span>
            </NuxtLink>
        </div>
    </div>
</template>

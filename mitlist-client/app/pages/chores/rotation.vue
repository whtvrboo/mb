<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useChores } from '~/composables/useChores'
import { useAuth } from '~/composables/useAuth'
import type { ChoreResponse } from '~/types/chores'
import type { GroupMemberResponse, UserResponse } from '~/types/auth'

const { listChores, updateChore } = useChores()
const { listGroupMembers, listGroups, getMe } = useAuth()

// State
const chores = ref<ChoreResponse[]>([])
const members = ref<GroupMemberResponse[]>([])
const currentUser = ref<UserResponse | null>(null)
const isLoading = ref(true)

// Settings
const rotationLogic = ref('ROUND_ROBIN')
// These two are currently mocked as client-side preferences because they aren't in the API yet.
// In a real scenario, we'd store these in group preferences or iterate chores to simulated them.
// For now, we'll pretend they persist to the Chore Rotation Strategy or just keep them as UI state for the calculation preview.
const skipAway = ref(true)
const autoReassign = ref(false)
const workloadBalance = ref(65)

const fetchData = async () => {
    isLoading.value = true
    try {
        const { data: groupsData } = await listGroups() // Assuming cached or fast
        const groups = groupsData.value || []
        const groupId = groups[0]?.id

        if (groupId) {
            const [choresResult, membersResult, meResult] = await Promise.all([
                listChores({ active_only: true }),
                listGroupMembers(groupId),
                getMe()
            ])
            chores.value = choresResult.data.value || []
            members.value = membersResult.data.value || []
            currentUser.value = meResult.data.value

            // Determine current logic from chores (majority wins)
            const strategies = chores.value.map(c => c.rotation_strategy).filter(Boolean)
            if (strategies.length > 0) {
                // Pick most common
                const counts = strategies.reduce((acc, val) => {
                    acc[val!] = (acc[val!] || 0) + 1
                    return acc
                }, {} as Record<string, number>)
                rotationLogic.value = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b)
            }
        }
    } catch (e) {
        console.error('Failed to fetch rotation data', e)
    } finally {
        isLoading.value = false
    }
}

const handleSave = async () => {
    // Batch update all rotating chores to the new strategy
    const rotatingChores = chores.value.filter(c => c.is_rotating)

    // Optimistic UI updates
    try {
        await Promise.all(rotatingChores.map(chore =>
            updateChore(chore.id, { rotation_strategy: rotationLogic.value as any })
        ))
        alert('Rotation settings saved!')
    } catch (e) {
        console.error('Failed to save settings', e)
        alert('Failed to save settings.')
    }
}

// Logic: Calculate a preview based on current chores and members
// This replaces the hardcoded mock data with a computation based on real data
const rotationPreview = computed(() => {
    if (members.value.length === 0) return []

    // Simulate next few assignments
    // This is a naive simulation for visualization purposes
    const previewItems = []

    const sortedMembers = [...members.value].sort((a, b) => a.id - b.id)

    // Create 3 slots
    const today = new Date()

    for (let i = 0; i < 3; i++) {
        const member = sortedMembers[i % sortedMembers.length]
        const date = new Date(today)
        date.setDate(date.getDate() + (i * 7)) // Weekly spacing simulation

        previewItems.push({
            name: member.user.name,
            dates: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            type: i === 0 ? 'Current' : (i === 1 ? 'Next' : 'Later'),
            isNext: i === 1,
            isUser: currentUser.value ? member.user.id === currentUser.value.id : false
        })
    }
    return previewItems
})

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
                <NuxtLink to="/chores"
                    class="flex items-center justify-center size-10 rounded-lg border-[2px] border-transparent hover:border-background-dark hover:bg-black/5 transition-all">
                    <span class="material-symbols-outlined text-[28px]">arrow_back</span>
                </NuxtLink>
            </div>
            <h1 class="text-xl font-bold tracking-tight uppercase truncate">Smart Rotation</h1>
            <div class="size-10 flex items-center justify-end">
                <span class="material-symbols-outlined text-[24px]">help</span>
            </div>
        </header>

        <main class="flex flex-col gap-8 p-5 max-w-lg mx-auto w-full">
            <div v-if="isLoading" class="text-center py-10 opacity-50">Loading rotation settings...</div>

            <div v-if="!isLoading" class="contents">
                <!-- Intro -->
                <div class="flex flex-col gap-1">
                    <h2 class="text-3xl font-bold leading-tight">Rotation Logic</h2>
                    <p class="text-base font-medium opacity-70">Decide how chores are dealt across the house.</p>
                </div>

                <!-- Logic Selection -->
                <section class="grid grid-cols-2 gap-4">
                    <label class="cursor-pointer group relative">
                        <input type="radio" value="ROUND_ROBIN" v-model="rotationLogic" class="peer sr-only" />
                        <div
                            class="h-full flex flex-col gap-3 p-4 bg-white border-[3px] border-background-dark rounded-xl shadow-neobrutalism transition-transform peer-checked:bg-primary peer-checked:translate-x-[2px] peer-checked:translate-y-[2px] peer-checked:shadow-none hover:shadow-neobrutalism-sm active:shadow-none active:translate-y-1 active:translate-x-1">
                            <div class="flex justify-between items-start">
                                <span class="material-symbols-outlined text-[32px]">sync</span>
                                <div
                                    class="size-6 bg-background-dark rounded-full flex items-center justify-center opacity-0 peer-checked:opacity-100 transition-opacity">
                                    <span
                                        class="material-symbols-outlined text-white text-[16px] font-bold">check</span>
                                </div>
                            </div>
                            <div>
                                <h3 class="font-bold text-lg leading-tight mb-1">Round Robin</h3>
                                <p class="text-xs font-medium opacity-80 leading-snug">Assignments rotate cyclically
                                    every
                                    period.</p>
                            </div>
                        </div>
                    </label>

                    <label class="cursor-pointer group relative">
                        <input type="radio" value="LEAST_BUSY" v-model="rotationLogic" class="peer sr-only" />
                        <div
                            class="h-full flex flex-col gap-3 p-4 bg-white border-[3px] border-background-dark rounded-xl shadow-neobrutalism transition-transform hover:bg-gray-50 peer-checked:bg-primary peer-checked:translate-x-[2px] peer-checked:translate-y-[2px] peer-checked:shadow-none active:shadow-none active:translate-y-1 active:translate-x-1">
                            <div class="flex justify-between items-start">
                                <span class="material-symbols-outlined text-[32px]">balance</span>
                                <div
                                    class="size-6 bg-background-dark rounded-full flex items-center justify-center opacity-0 peer-checked:opacity-100 transition-opacity">
                                    <span
                                        class="material-symbols-outlined text-white text-[16px] font-bold">check</span>
                                </div>
                            </div>
                            <div>
                                <h3 class="font-bold text-lg leading-tight mb-1">Least Busy</h3>
                                <p class="text-xs font-medium opacity-70 leading-snug">Assigns to whoever has the fewest
                                    points.</p>
                            </div>
                        </div>
                    </label>
                </section>

                <div class="w-full h-0.5 bg-background-dark/10 rounded-full"></div>

                <!-- Toggles -->
                <section class="flex flex-col gap-6">
                    <div class="flex items-center justify-between">
                        <div class="flex flex-col">
                            <h3 class="text-lg font-bold">Skip if Away</h3>
                            <p class="text-sm opacity-60 font-medium">Don't assign to users marked 'Away'.</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" v-model="skipAway" class="sr-only peer">
                            <div
                                class="w-16 h-9 bg-white peer-focus:outline-none border-[3px] border-background-dark rounded-full peer peer-checked:bg-sage transition-colors shadow-neobrutalism-sm">
                            </div>
                            <div
                                class="absolute left-[5px] top-[5px] bg-background-dark border border-background-dark h-6 w-6 rounded-full transition-all peer-checked:translate-x-[28px] peer-checked:bg-white peer-checked:border-background-dark">
                            </div>
                        </label>
                    </div>

                    <div class="flex items-center justify-between">
                        <div class="flex flex-col">
                            <h3 class="text-lg font-bold">Auto-Reassign</h3>
                            <p class="text-sm opacity-60 font-medium">If overdue by 3 days.</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" v-model="autoReassign" class="sr-only peer">
                            <div
                                class="w-16 h-9 bg-white peer-focus:outline-none border-[3px] border-background-dark rounded-full peer peer-checked:bg-sage transition-colors shadow-neobrutalism-sm">
                            </div>
                            <div
                                class="absolute left-[5px] top-[5px] bg-white border-[3px] border-background-dark h-6 w-6 rounded-full transition-all peer-checked:translate-x-[28px]">
                            </div>
                        </label>
                    </div>
                </section>

                <!-- Slider -->
                <section
                    class="bg-[#E0E7F1] border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism relative overflow-hidden">
                    <div class="absolute top-0 right-0 p-3 opacity-10 pointer-events-none">
                        <span class="material-symbols-outlined text-[80px]">tune</span>
                    </div>
                    <div class="flex items-center gap-2 mb-4 relative z-10">
                        <span class="material-symbols-outlined">equalizer</span>
                        <h3 class="font-bold text-lg uppercase tracking-wide">Workload Balance</h3>
                    </div>
                    <div class="relative z-10 flex flex-col gap-4">
                        <input type="range" v-model="workloadBalance" min="0" max="100"
                            class="w-full h-2 bg-transparent appearance-none cursor-pointer range-slider" />
                        <div
                            class="flex justify-between text-xs font-bold uppercase tracking-wider text-background-dark/70">
                            <span>Strict Rotation</span>
                            <span>Weighted</span>
                        </div>
                    </div>
                </section>

                <!-- Preview -->
                <section class="flex flex-col gap-4">
                    <div class="flex items-center justify-between border-b-[3px] border-background-dark pb-2">
                        <h2 class="text-xl font-bold uppercase tracking-wide flex items-center gap-2">
                            <span class="material-symbols-outlined">visibility</span> Preview (Simulation)
                        </h2>
                        <span
                            class="bg-primary px-2 py-0.5 text-xs font-bold border-[2px] border-background-dark rounded shadow-neobrutalism-sm">UPCOMING</span>
                    </div>

                    <div class="flex flex-col gap-0 relative pl-4">
                        <div
                            class="absolute left-[29px] top-4 bottom-4 w-[3px] bg-background-dark/20 border-l-[3px] border-dashed border-background-dark">
                        </div>

                        <div v-for="(item, idx) in rotationPreview" :key="idx"
                            class="relative flex items-center gap-4 py-3 group"
                            :class="{ 'opacity-60': !item.isUser && !item.isNext }">
                            <div
                                class="z-10 relative size-14 shrink-0 flex items-center justify-center transition-transform group-hover:scale-110">
                                <div v-if="item.isNext"
                                    class="w-full h-full bg-primary star-shape absolute top-0 left-0 border border-background-dark">
                                </div>

                                <div
                                    class="size-14 rounded-full border-[3px] border-background-dark overflow-hidden bg-gray-200 shadow-neobrutalism-sm relative z-10">
                                    <div
                                        class="w-full h-full bg-gray-300 flex items-center justify-center font-bold text-xs">
                                        {{ item.name?.[0] || '?' }}
                                    </div>
                                </div>
                            </div>

                            <div class="flex-1 rounded-lg p-3 flex justify-between items-center"
                                :class="item.isUser ? 'bg-white border-[3px] border-background-dark shadow-neobrutalism' : (item.isNext ? 'bg-background-light border-[3px] border-background-dark/30 border-dashed opacity-80' : 'p-2')">
                                <div>
                                    <span v-if="item.isUser"
                                        class="text-[10px] font-bold uppercase bg-sage text-white px-1.5 py-0.5 rounded border border-background-dark mb-1 inline-block">Current</span>
                                    <span v-if="item.isNext"
                                        class="text-[10px] font-bold uppercase bg-background-dark/10 text-background-dark px-1.5 py-0.5 rounded border border-background-dark/30 mb-1 inline-block">Next</span>
                                    <p class="font-bold text-lg leading-none">{{ item.name }}</p>
                                </div>
                                <span class="font-bold text-sm opacity-50">{{ item.dates }}</span>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </main>

        <!-- Footer Action -->
        <div
            class="fixed bottom-0 left-0 w-full p-5 bg-white/95 backdrop-blur-sm border-t-[3px] border-background-dark z-50">
            <button @click="handleSave"
                class="w-full h-14 bg-background-dark text-white rounded-xl font-bold text-lg shadow-[4px_4px_0px_0px_#8E9DB3] active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all flex items-center justify-center gap-2">
                <span class="material-symbols-outlined">save</span>
                Save Settings
            </button>
        </div>
    </div>
</template>

<style scoped>
.star-shape {
    clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
}

.range-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    height: 24px;
    width: 24px;
    border-radius: 0;
    background: #eecd2b;
    border: 3px solid #221f10;
    cursor: pointer;
    box-shadow: 2px 2px 0px 0px #221f10;
    margin-top: -10px;
}

.range-slider::-webkit-slider-runnable-track {
    width: 100%;
    height: 4px;
    cursor: pointer;
    background: #221f10;
    border-radius: 0;
}
</style>

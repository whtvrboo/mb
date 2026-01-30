<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useGamification } from '~/composables/useGamification'
import type {
    LeaderboardWithEntriesResponse,
    UserGamificationSummaryResponse,
    AchievementResponse,
    UserAchievementWithDetailsResponse
} from '~/types/gamification'

const { getLeaderboard, getSummary, listAchievements, getMyAchievements } = useGamification()

const activeTab = ref<'rankings' | 'achievements'>('rankings')
const leaderboard = ref<LeaderboardWithEntriesResponse | null>(null)
const summary = ref<UserGamificationSummaryResponse | null>(null)
const allAchievements = ref<AchievementResponse[]>([])
const myAchievements = ref<UserAchievementWithDetailsResponse[]>([])
const isLoading = ref(true)

const fetchData = async () => {
    isLoading.value = true
    try {
        const [lbData, summaryData, allAch, myAch] = await Promise.all([
            getLeaderboard({ period_type: 'monthly', metric: 'points' }),
            getSummary(),
            listAchievements(),
            getMyAchievements()
        ])
        leaderboard.value = lbData
        summary.value = summaryData
        allAchievements.value = allAch
        myAchievements.value = myAch
    } catch (e) {
        console.error('Failed to fetch gamification data', e)
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchData()
})

const isUnlocked = (achievementId: number) => {
    return myAchievements.value.some(a => a.achievement_id === achievementId)
}

const getRankColor = (rank: number) => {
    if (rank === 1) return 'bg-[#ffd700] border-[#ffd700]' // Gold
    if (rank === 2) return 'bg-[#c0c0c0] border-[#c0c0c0]' // Silver
    if (rank === 3) return 'bg-[#cd7f32] border-[#cd7f32]' // Bronze
    return 'bg-white border-background-dark'
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
            <h1 class="text-xl font-bold tracking-tight uppercase">Leaderboard</h1>
            <div class="size-10 flex items-center justify-end">
                <span class="material-symbols-outlined text-[24px]">emoji_events</span>
            </div>
        </header>

        <main class="flex flex-col gap-6 p-5 max-w-lg mx-auto w-full">

            <!-- User Summary Card -->
            <section
                class="bg-primary border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism flex items-center justify-between relative overflow-hidden">
                <div class="flex flex-col z-10">
                    <span class="text-xs font-black uppercase tracking-widest opacity-60 text-background-dark">My
                        Rank</span>
                    <div class="flex items-baseline gap-1">
                        <h2 class="text-5xl font-black leading-none">#{{ summary?.rank_position || '-' }}</h2>
                        <span class="text-sm font-bold opacity-70">/ {{ leaderboard?.total_participants || '-' }}</span>
                    </div>
                    <div class="mt-2 flex gap-4">
                        <div class="flex flex-col">
                            <span class="text-[10px] font-bold uppercase opacity-60">Points</span>
                            <span class="font-bold text-lg leading-none">{{ summary?.monthly_points || 0 }}</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-[10px] font-bold uppercase opacity-60">Badges</span>
                            <span class="font-bold text-lg leading-none">{{ summary?.achievements_earned || 0 }}</span>
                        </div>
                    </div>
                </div>
                <span
                    class="material-symbols-outlined text-9xl absolute -right-4 -bottom-4 opacity-10 rotate-12">military_tech</span>
            </section>

            <!-- Tabs -->
            <div
                class="flex bg-white border-[3px] border-background-dark rounded-xl overflow-hidden shadow-neobrutalism-sm">
                <button @click="activeTab = 'rankings'" class="flex-1 py-3 font-bold uppercase transition-colors"
                    :class="activeTab === 'rankings' ? 'bg-background-dark text-white' : 'hover:bg-gray-100'">
                    Rankings
                </button>
                <div class="w-[3px] bg-background-dark"></div>
                <button @click="activeTab = 'achievements'" class="flex-1 py-3 font-bold uppercase transition-colors"
                    :class="activeTab === 'achievements' ? 'bg-background-dark text-white' : 'hover:bg-gray-100'">
                    Badges
                </button>
            </div>

            <div v-if="isLoading" class="text-center py-10 opacity-50">Loading stats...</div>

            <!-- Leaderboard -->
            <div v-if="activeTab === 'rankings' && !isLoading" class="flex flex-col gap-3">
                <div v-if="!leaderboard?.entries || leaderboard.entries.length === 0"
                    class="text-center py-10 opacity-50 font-bold">No data yet.</div>

                <div v-for="(entry, idx) in leaderboard?.entries" :key="entry.user_id"
                    class="flex items-center gap-4 bg-white border-[3px] border-background-dark rounded-xl p-3 shadow-sm hover:translate-x-1 transition-transform"
                    :class="{ 'border-primary bg-primary/10': entry.user_id === summary?.user_id }">

                    <div class="size-8 flex items-center justify-center font-black text-lg text-background-dark/50">
                        {{ entry.rank }}
                    </div>

                    <div
                        class="size-12 rounded-full border-[2px] border-background-dark overflow-hidden bg-gray-200 shrink-0">
                        <img v-if="entry.avatar_url" :src="entry.avatar_url" class="w-full h-full object-cover" />
                        <div v-else class="w-full h-full flex items-center justify-center font-bold text-sm">{{
                            entry.user_name?.[0] || '?' }}</div>
                    </div>

                    <div class="flex flex-col flex-1">
                        <h3 class="font-bold text-lg leading-none">{{ entry.user_name }}</h3>
                        <span class="text-xs font-bold opacity-50">Level {{ Math.floor(entry.value / 100) + 1 }}</span>
                    </div>

                    <div class="font-black text-xl">{{ entry.value }}</div>
                </div>
            </div>

            <!-- Achievements -->
            <div v-if="activeTab === 'achievements' && !isLoading" class="grid grid-cols-3 gap-3">
                <div v-for="ach in allAchievements" :key="ach.id"
                    class="aspect-square bg-white border-[3px] border-background-dark rounded-xl flex flex-col items-center justify-center p-2 text-center gap-1 transition-all"
                    :class="isUnlocked(ach.id) ? 'shadow-neobrutalism hover:-translate-y-1' : 'opacity-50 grayscale bg-gray-100'">
                    <div class="size-10 rounded-full bg-primary/20 flex items-center justify-center mb-1">
                        <span class="material-symbols-outlined text-2xl">{{ ach.badge_icon_url || 'stars' }}</span>
                    </div>
                    <span class="font-bold text-[10px] uppercase leading-tight">{{ ach.name }}</span>
                </div>
            </div>

        </main>
    </div>
</template>

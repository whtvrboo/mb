<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuth } from '~/composables/useAuth'
import type { GroupResponse, GroupMemberResponse } from '~/types/auth'

const { listGroups, listGroupMembers, groupId } = useAuth()

// State
const houses = ref<GroupResponse[]>([])
const members = ref<GroupMemberResponse[]>([])
const isLoading = ref(true)

// Computed
const currentHouseId = computed(() => groupId.value)

// Fetch Data
const fetchData = async () => {
    isLoading.value = true
    try {
        // 1. Fetch User's Groups
        houses.value = await listGroups()

        // 2. Fetch Members for current group
        if (currentHouseId.value) {
            members.value = await listGroupMembers(currentHouseId.value)
        } else if (houses.value.length > 0) {
            // Fallback if no current group selected (though useAuth usually handles this)
            // For now just fetch first
            members.value = await listGroupMembers(houses.value[0].id)
        }
    } catch (error) {
        console.error('Failed to fetch mates data', error)
    } finally {
        isLoading.value = false
    }
}

// Helpers
const getHouseIcon = (house: GroupResponse) => {
    // Deterministic icon based on id or name
    const icons = ['home', 'apartment', 'cabin', 'cottage', 'house']
    return icons[house.id % icons.length]
}

const getHouseColor = (house: GroupResponse) => {
    // Deterministic color
    const colors = ['bg-[#e0f2f1]', 'bg-[#fff9c4]', 'bg-[#ffe0b2]', 'bg-[#d1c4e9]']
    if (house.id === currentHouseId.value) return 'bg-primary'
    return colors[house.id % colors.length]
}

const getAvatarColor = (member: GroupMemberResponse) => {
    if (member.user.id === members.value[0]?.user.id) return 'bg-primary' // Just a guess for "me"
    const colors = ['bg-gray-200', 'bg-[#8E9DB3]', 'bg-gray-100', 'bg-[#A3B18A]']
    // Use user ID for consistent color
    return colors[member.user.id % colors.length]
}
const isCurrentUser = (member: GroupMemberResponse) => {
    // Ideally compare with my user ID, but we need to fetch 'me' first.
    // We can fetch 'me' in fetchData or assume strict equality if we had the ID.
    // For now, let's just leave it false or implement if we fetch user.
    return false // TODO: compare with logged in user
}

onMounted(() => {
    fetchData()
})
</script>

<template>
    <div class="bg-background-light dark:bg-background-dark min-h-screen text-background-dark font-display pb-24">
        <!-- Header -->
        <header
            class="sticky top-0 z-50 bg-background-light border-b-[3px] border-background-dark px-5 h-16 flex items-center justify-between shadow-sm">
            <div class="flex items-center gap-3">
                <NuxtLink to="/"
                    class="flex items-center justify-center size-10 rounded-lg border-[2px] border-transparent hover:border-background-dark hover:bg-black/5 transition-colors">
                    <span class="material-symbols-outlined text-[28px]">arrow_back</span>
                </NuxtLink>
            </div>
            <h1 class="text-xl font-bold tracking-tight uppercase">Manage Houses</h1>
            <div class="size-10 flex items-center justify-end">
                <span class="material-symbols-outlined text-[24px]">add_circle</span>
            </div>
        </header>

        <main class="flex flex-col gap-8 p-5 pb-24 max-w-lg mx-auto w-full">

            <!-- Households Section -->
            <section class="flex flex-col gap-4">
                <div class="flex items-center justify-between border-b-[3px] border-background-dark pb-2 w-full">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined">holiday_village</span>
                        <h2 class="text-lg font-bold uppercase tracking-wide">Your Households</h2>
                    </div>
                    <span class="text-xs font-bold bg-background-dark text-white px-2 py-0.5 rounded">{{ houses.length
                        }} TOTAL</span>
                </div>

                <div v-if="isLoading && houses.length === 0" class="py-10 text-center opacity-50">
                    Loading houses...
                </div>

                <div v-for="house in houses" :key="house.id"
                    class="group relative w-full border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism transition-all cursor-pointer overflow-hidden"
                    :class="house.id === currentHouseId ? 'bg-primary shadow-neobrutalism-lg' : 'bg-white hover:-translate-y-1'">
                    <div v-if="house.id === currentHouseId"
                        class="absolute -right-4 -top-4 size-20 bg-white/20 rounded-full blur-xl">
                    </div>

                    <div v-if="house.id === currentHouseId" class="flex justify-between items-start mb-2">
                        <div
                            class="flex items-center gap-2 bg-background-dark text-white px-3 py-1 rounded-lg border border-background-dark shadow-sm">
                            <span class="material-symbols-outlined text-[16px] text-primary">check_circle</span>
                            <span class="text-xs font-bold uppercase tracking-wider">Active</span>
                        </div>
                        <span class="material-symbols-outlined text-[28px]">more_vert</span>
                    </div>

                    <div class="flex items-center gap-4"
                        :class="{ 'mt-2': house.id === currentHouseId, 'justify-between w-full': house.id !== currentHouseId }">
                        <div class="flex items-center gap-4">
                            <div class="size-12 rounded-full border-[3px] border-background-dark flex items-center justify-center shrink-0"
                                :class="house.id === currentHouseId ? 'bg-white' : getHouseColor(house)">
                                <span class="material-symbols-outlined text-[24px] text-black">{{ getHouseIcon(house)
                                    }}</span>
                            </div>
                            <div>
                                <h3 class="text-xl font-bold leading-none">{{ house.name }}</h3>
                                <p class="text-sm font-medium mt-1"
                                    :class="house.id === currentHouseId ? 'opacity-80' : 'opacity-60'">
                                    {{ house.address || 'No address' }}</p>
                            </div>
                        </div>
                        <button v-if="house.id !== currentHouseId"
                            class="size-10 flex items-center justify-center border-[2px] border-background-dark rounded-lg hover:bg-gray-100">
                            <span class="material-symbols-outlined">arrow_forward</span>
                        </button>
                    </div>
                </div>
            </section>

            <div class="w-full h-1 border-t-[3px] border-dashed border-background-dark/30 my-2"></div>

            <!-- Members Section -->
            <section class="flex flex-col gap-5">
                <div class="flex flex-col gap-1">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined">badge</span>
                        <h2 class="text-lg font-bold uppercase tracking-wide">Role Assignment</h2>
                    </div>
                    <p class="text-sm opacity-70">Managing members.</p>
                </div>

                <div v-if="isLoading && members.length === 0" class="py-10 text-center opacity-50">
                    Loading members...
                </div>

                <div v-for="member in members" :key="member.id"
                    class="flex items-center justify-between bg-white border-[3px] border-background-dark rounded-lg p-3 shadow-neobrutalism">
                    <div class="flex items-center gap-3">
                        <div class="size-10 rounded-full border-[2px] border-background-dark overflow-hidden shrink-0 flex items-center justify-center font-bold text-white text-sm"
                            :class="getAvatarColor(member)">
                            <img v-if="member.user.avatar_url" :src="member.user.avatar_url" alt="User Avatar"
                                class="w-full h-full object-cover" />
                            <span v-else>{{ member.user.name?.[0] || '?' }}</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="font-bold text-lg leading-none">{{ member.user.name }}</span>
                            <span class="text-xs text-gray-500 font-medium">{{ member.nickname || '@' +
                                member.user.email.split('@')[0] }}</span>
                        </div>
                    </div>

                    <!-- Role Badge/Dropdown -->
                    <div v-if="isCurrentUser(member)" class="flex items-center gap-2">
                        <span
                            class="bg-background-dark text-white text-[10px] font-black uppercase px-2 py-1 rounded border border-background-dark shadow-sm">{{
                            member.role }}</span>
                        <span class="material-symbols-outlined text-gray-400">edit</span>
                    </div>
                    <div v-else class="relative group">
                        <button
                            class="flex items-center gap-2 bg-[#A3B18A]/30 hover:bg-[#A3B18A] hover:text-white transition-colors border-[2px] border-background-dark rounded px-3 py-1.5">
                            <span class="text-[10px] font-black uppercase">{{ member.role }}</span>
                            <span class="material-symbols-outlined text-[14px]">expand_more</span>
                        </button>
                    </div>
                </div>

                <button
                    class="mt-2 w-full h-12 border-[3px] border-dashed border-background-dark rounded-lg flex items-center justify-center gap-2 hover:bg-primary/10 transition-colors group">
                    <span class="material-symbols-outlined group-hover:scale-110 transition-transform">person_add</span>
                    <span class="font-bold uppercase tracking-wide">Invite New Roommate</span>
                </button>
            </section>
        </main>
    </div>
</template>

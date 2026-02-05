<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuth } from '~/composables/useAuth'
import type { GroupResponse, UserResponse } from '~/types/auth'

const { listGroups, listGroupMembers, getMe, updateUser } = useAuth()

const house = ref<GroupResponse | null>(null)
const user = ref<UserResponse | null>(null)
const memberCount = ref(0)
const isLoading = ref(true)

// Mock notification state stored in user preferences?
const pushEnabled = ref(false)
const emailEnabled = ref(false)

const fetchData = async () => {
    isLoading.value = true
    try {
        const [groups, userData] = await Promise.all([
            listGroups(),
            getMe()
        ])

        user.value = userData
        // Initialize toggles from preferences or default
        pushEnabled.value = (userData.preferences?.push_notifications as boolean) ?? true
        emailEnabled.value = (userData.preferences?.email_digest as boolean) ?? false

        if (groups.length > 0) {
            house.value = groups[0] // Select first house for now
            const members = await listGroupMembers(house.value.id)
            memberCount.value = members.length
        }
    } catch (e) {
        console.error('Failed to fetch settings data', e)
    } finally {
        isLoading.value = false
    }
}

const updatePreference = async (key: string, value: boolean) => {
    if (!user.value) return
    try {
        const newPrefs = { ...user.value.preferences, [key]: value }
        await updateUser(user.value.id, { preferences: newPrefs })
        // Update local ref
        if (key === 'push_notifications') pushEnabled.value = value
        if (key === 'email_digest') emailEnabled.value = value
    } catch (e) {
        console.error('Failed to update preference', e)
        // Revert toggle
        if (key === 'push_notifications') pushEnabled.value = !value
        if (key === 'email_digest') emailEnabled.value = !value
    }
}

const copyInviteLink = async () => {
    // Generate or fetch invite link (mocking action for now as invite generation needs a separate flow)
    // Real implementation: create invite -> get code -> copy url
    alert('Invite link copied! (Simulated)')
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
                    class="flex items-center justify-center size-10 rounded-lg border-[2px] border-transparent hover:border-background-dark hover:bg-black/5 focus-visible:border-background-dark focus-visible:bg-black/5 focus-visible:outline-none transition-colors">
                    <span class="material-symbols-outlined text-[28px]">arrow_back</span>
                </NuxtLink>
            </div>
            <h1 class="text-xl font-bold tracking-tight uppercase">Settings</h1>
            <div class="size-10"></div>
        </header>

        <main class="flex flex-col gap-8 p-5 max-w-lg mx-auto w-full">
            <div v-if="isLoading" class="text-center py-10 opacity-50">Loading settings...</div>

            <!-- House Title -->
            <div v-if="house" class="flex items-center justify-between">
                <div class="flex flex-col">
                    <h2 class="text-2xl font-bold leading-tight">{{ house.name }}</h2>
                    <span class="text-sm font-medium opacity-60">Global Settings</span>
                </div>
                <div
                    class="size-12 bg-primary border-[3px] border-background-dark rounded-full flex items-center justify-center shadow-neobrutalism-sm">
                    <span class="material-symbols-outlined text-[24px]">home</span>
                </div>
            </div>

            <!-- Settings Sections -->
            <div v-if="!isLoading" class="flex flex-col gap-6">
                <!-- Notifications -->
                <div class="flex flex-col gap-2">
                    <h3 class="text-sm font-bold uppercase text-gray-500 ml-1">Notifications</h3>
                    <div
                        class="flex flex-col gap-0 bg-white border-[3px] border-background-dark rounded-xl overflow-hidden shadow-neobrutalism">

                        <!-- Push Toggle -->
                        <button
                            type="button"
                            role="switch"
                            :aria-checked="pushEnabled"
                            class="w-full text-left flex items-center justify-between p-4 border-b-[2px] border-gray-100 hover:bg-gray-50 focus-visible:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-background-dark transition-colors cursor-pointer group"
                            @click="updatePreference('push_notifications', !pushEnabled)">
                            <div class="flex items-center gap-3">
                                <div
                                    class="size-8 rounded-lg bg-gray-100 flex items-center justify-center text-gray-600 group-hover:bg-primary group-hover:text-background-dark transition-colors">
                                    <span class="material-symbols-outlined text-[20px]">notifications</span>
                                </div>
                                <span class="font-bold text-lg">Push Notifications</span>
                            </div>
                            <div class="w-12 h-6 bg-gray-200 rounded-full border-2 border-background-dark relative transition-colors"
                                :class="{ 'bg-primary': pushEnabled }">
                                <div class="size-4 bg-white border-2 border-background-dark rounded-full absolute top-[2px] left-[2px] transition-transform"
                                    :class="{ 'translate-x-[24px]': pushEnabled }"></div>
                            </div>
                        </button>

                        <!-- Email Toggle -->
                        <button
                            type="button"
                            role="switch"
                            :aria-checked="emailEnabled"
                            class="w-full text-left flex items-center justify-between p-4 hover:bg-gray-50 focus-visible:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-background-dark transition-colors cursor-pointer group"
                            @click="updatePreference('email_digest', !emailEnabled)">
                            <div class="flex items-center gap-3">
                                <div
                                    class="size-8 rounded-lg bg-gray-100 flex items-center justify-center text-gray-600 group-hover:bg-primary group-hover:text-background-dark transition-colors">
                                    <span class="material-symbols-outlined text-[20px]">mail</span>
                                </div>
                                <span class="font-bold text-lg">Email Digest</span>
                            </div>
                            <div class="w-12 h-6 bg-gray-200 rounded-full border-2 border-background-dark relative transition-colors"
                                :class="{ 'bg-primary': emailEnabled }">
                                <div class="size-4 bg-white border-2 border-background-dark rounded-full absolute top-[2px] left-[2px] transition-transform"
                                    :class="{ 'translate-x-[24px]': emailEnabled }"></div>
                            </div>
                        </button>

                    </div>
                </div>

                <!-- Roommates -->
                <div class="flex flex-col gap-2">
                    <h3 class="text-sm font-bold uppercase text-gray-500 ml-1">Roommates</h3>
                    <div
                        class="flex flex-col gap-0 bg-white border-[3px] border-background-dark rounded-xl overflow-hidden shadow-neobrutalism">
                        <!-- Invite -->
                        <button
                            type="button"
                            class="w-full text-left flex items-center justify-between p-4 border-b-[2px] border-gray-100 hover:bg-gray-50 focus-visible:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-background-dark transition-colors cursor-pointer group"
                            @click="copyInviteLink">
                            <div class="flex items-center gap-3">
                                <div
                                    class="size-8 rounded-lg bg-gray-100 flex items-center justify-center text-gray-600 group-hover:bg-primary group-hover:text-background-dark transition-colors">
                                    <span class="material-symbols-outlined text-[20px]">link</span>
                                </div>
                                <span class="font-bold text-lg">Invite Roommate</span>
                            </div>
                            <div class="flex items-center gap-2 text-sm font-bold opacity-60 group-hover:opacity-100">
                                Copy
                                <span class="material-symbols-outlined text-[16px]">content_copy</span>
                            </div>
                        </button>

                        <!-- Manage -->
                        <NuxtLink to="/mates"
                            class="flex items-center justify-between p-4 hover:bg-gray-50 focus-visible:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-background-dark transition-colors cursor-pointer group">
                            <div class="flex items-center gap-3">
                                <div
                                    class="size-8 rounded-lg bg-gray-100 flex items-center justify-center text-gray-600 group-hover:bg-primary group-hover:text-background-dark transition-colors">
                                    <span class="material-symbols-outlined text-[20px]">group</span>
                                </div>
                                <span class="font-bold text-lg">Manage Members</span>
                            </div>
                            <div class="flex items-center gap-2 text-sm font-bold opacity-60 group-hover:opacity-100">
                                {{ memberCount }} Active
                                <span class="material-symbols-outlined text-[16px]">chevron_right</span>
                            </div>
                        </NuxtLink>
                    </div>
                </div>

                <!-- Danger Zone -->
                <div class="flex flex-col gap-2 mt-4">
                    <h3 class="font-bold uppercase tracking-wider text-red-500 ml-1">Danger Zone</h3>
                    <button
                        class="w-full bg-red-100 text-red-600 border-[3px] border-red-500 rounded-xl p-4 font-bold uppercase shadow-[4px_4px_0px_0px_#ef4444] active:shadow-none active:translate-x-1 active:translate-y-1 focus-visible:ring-2 focus-visible:ring-background-dark focus-visible:ring-offset-2 focus-visible:outline-none transition-all flex items-center justify-center gap-2">
                        <span class="material-symbols-outlined">logout</span>
                        Leave House
                    </button>
                </div>
            </div>
        </main>
    </div>
</template>

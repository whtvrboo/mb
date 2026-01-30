<script setup lang="ts">
// Mock Settings Data
const houseName = ref('The Loft')
const settings = [
    {
        section: 'Plan & Billing', items: [
            { label: 'Manage Subscription', icon: 'credit_card', action: 'External Link' },
            { label: 'Payment Methods', icon: 'account_balance_wallet', action: 'Visa ...4242' }
        ]
    },
    {
        section: 'Notifications', items: [
            { label: 'Push Notifications', icon: 'notifications', toggle: true },
            { label: 'Email Digest', icon: 'mail', toggle: false }
        ]
    },
    {
        section: 'Roommates', items: [
            { label: 'Invite Link', icon: 'link', action: 'Copy' },
            { label: 'Manage Members', icon: 'group', action: '4 Active' }
        ]
    }
]
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
            <h1 class="text-xl font-bold tracking-tight uppercase">Settings</h1>
            <div class="size-10"></div>
        </header>

        <main class="flex flex-col gap-8 p-5 max-w-lg mx-auto w-full">
            <!-- House Title -->
            <div class="flex items-center justify-between">
                <div class="flex flex-col">
                    <h2 class="text-2xl font-bold leading-tight">{{ houseName }}</h2>
                    <span class="text-sm font-medium opacity-60">Global Settings</span>
                </div>
                <div
                    class="size-12 bg-primary border-[3px] border-background-dark rounded-full flex items-center justify-center shadow-neobrutalism-sm">
                    <span class="material-symbols-outlined text-[24px]">home</span>
                </div>
            </div>

            <!-- Settings Sections -->
            <div class="flex flex-col gap-6">
                <div v-for="(section, idx) in settings" :key="idx" class="flex flex-col gap-2">
                    <h3 class="text-sm font-bold uppercase text-gray-500 ml-1">{{ section.section }}</h3>
                    <div
                        class="flex flex-col gap-0 bg-white border-[3px] border-background-dark rounded-xl overflow-hidden shadow-neobrutalism">
                        <div v-for="(item, i) in section.items" :key="i"
                            class="flex items-center justify-between p-4 border-b-[2px] border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors cursor-pointer group">
                            <div class="flex items-center gap-3">
                                <div
                                    class="size-8 rounded-lg bg-gray-100 flex items-center justify-center text-gray-600 group-hover:bg-primary group-hover:text-background-dark transition-colors">
                                    <span class="material-symbols-outlined text-[20px]">{{ item.icon }}</span>
                                </div>
                                <span class="font-bold text-lg">{{ item.label }}</span>
                            </div>

                            <!-- Action Types -->
                            <div v-if="item.toggle !== undefined">
                                <div class="w-12 h-6 bg-gray-200 rounded-full border-2 border-background-dark relative transition-colors"
                                    :class="{ 'bg-primary': item.toggle }">
                                    <div class="size-4 bg-white border-2 border-background-dark rounded-full absolute top-[2px] left-[2px] transition-transform"
                                        :class="{ 'translate-x-[24px]': item.toggle }"></div>
                                </div>
                            </div>
                            <div v-else
                                class="flex items-center gap-2 text-sm font-bold opacity-60 group-hover:opacity-100">
                                {{ item.action }}
                                <span class="material-symbols-outlined text-[16px]">chevron_right</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Danger Zone -->
                <div class="flex flex-col gap-2 mt-4">
                    <h3 class="font-bold uppercase tracking-wider text-red-500 ml-1">Danger Zone</h3>
                    <button
                        class="w-full bg-red-100 text-red-600 border-[3px] border-red-500 rounded-xl p-4 font-bold uppercase shadow-[4px_4px_0px_0px_#ef4444] active:shadow-none active:translate-x-1 active:translate-y-1 transition-all flex items-center justify-center gap-2">
                        <span class="material-symbols-outlined">logout</span>
                        Leave House
                    </button>
                </div>
            </div>
        </main>
    </div>
</template>

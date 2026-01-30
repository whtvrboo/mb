<script setup lang="ts">
// Mock Data
const houses = [
    { id: 1, name: 'The Main Pad', members: 4, location: 'Austin, TX', active: true, color: 'bg-primary', icon: 'home' },
    { id: 2, name: 'Lake Cabin', members: 2, location: 'Tahoe', active: false, color: 'bg-[#e0f2f1]', icon: 'cabin', iconColor: 'text-teal-800' },
    { id: 3, name: 'Co-living Space', members: 8, location: 'Brooklyn', active: false, color: 'bg-[#fff9c4]', icon: 'apartment', iconColor: 'text-orange-800' },
]

const members = [
    { name: 'You', handle: '@jess_design', role: 'Admin', avatarColor: 'bg-primary', isCurrentUser: true },
    { name: 'Alex M.', handle: '@alex_cooks', role: 'Member', avatarColor: 'bg-gray-200' },
    { name: 'Sarah', handle: '@sarah_m', role: 'Member', avatarColor: 'bg-[#8E9DB3]', initials: 'SM' },
    { name: 'Guest User', handle: 'Invited via Link', role: 'Guest', avatarColor: 'bg-gray-100', isGuest: true },
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
                    <span class="text-xs font-bold bg-background-dark text-white px-2 py-0.5 rounded">3 TOTAL</span>
                </div>

                <div v-for="house in houses" :key="house.id"
                    class="group relative w-full border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism transition-all cursor-pointer overflow-hidden"
                    :class="house.active ? 'bg-primary shadow-neobrutalism-lg' : 'bg-white hover:-translate-y-1'">
                    <div v-if="house.active" class="absolute -right-4 -top-4 size-20 bg-white/20 rounded-full blur-xl">
                    </div>

                    <div v-if="house.active" class="flex justify-between items-start mb-2">
                        <div
                            class="flex items-center gap-2 bg-background-dark text-white px-3 py-1 rounded-lg border border-background-dark shadow-sm">
                            <span class="material-symbols-outlined text-[16px] text-primary">check_circle</span>
                            <span class="text-xs font-bold uppercase tracking-wider">Active</span>
                        </div>
                        <span class="material-symbols-outlined text-[28px]">more_vert</span>
                    </div>

                    <div class="flex items-center gap-4"
                        :class="{ 'mt-2': house.active, 'justify-between w-full': !house.active }">
                        <div class="flex items-center gap-4">
                            <div class="size-12 rounded-full border-[3px] border-background-dark flex items-center justify-center shrink-0"
                                :class="house.active ? 'bg-white' : house.color">
                                <span class="material-symbols-outlined text-[24px]"
                                    :class="house.iconColor || 'text-black'">{{ house.icon }}</span>
                            </div>
                            <div>
                                <h3 class="text-xl font-bold leading-none">{{ house.name }}</h3>
                                <p class="text-sm font-medium mt-1" :class="house.active ? 'opacity-80' : 'opacity-60'">
                                    {{ house.members }} Members • {{ house.location }}</p>
                            </div>
                        </div>
                        <button v-if="!house.active"
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
                    <p class="text-sm opacity-70">Managing permissions for <span class="font-bold underline">The Main
                            Pad</span>.</p>
                </div>

                <div v-for="(member, idx) in members" :key="idx"
                    class="flex items-center justify-between bg-white border-[3px] border-background-dark rounded-lg p-3 shadow-neobrutalism"
                    :class="{ 'opacity-80': member.isGuest }">
                    <div class="flex items-center gap-3">
                        <div class="size-10 rounded-full border-[2px] border-background-dark overflow-hidden shrink-0 flex items-center justify-center font-bold text-white text-sm"
                            :class="member.avatarColor">
                            <span v-if="member.initials">{{ member.initials }}</span>
                            <span v-else-if="member.isGuest"
                                class="material-symbols-outlined text-gray-400">person</span>
                            <img v-else alt="User Avatar" class="w-full h-full object-cover"
                                src="https://lh3.googleusercontent.com/aida-public/AB6AXuDdIeKSvSw4g0UUcuJweKw7YgtsfrLM5Eld5EIqorAUZk7VenHbkKixdWdj8iw-K0dr1dQoD2vI-tRFaqfrk1PZyA8s4mjhvR8QUAjBaKuWFc1jJ_EsRNXftMEyuwuE2_TbZ0pxpnD1wPv7XiAkmrOUy3vE2ruD7E0-r_QpIIqCmuOcKJgZl4MR2NaJRDy-lIVJYkf-hcPeOZtvr1-pZQzrCO3lxO2S_kcYiA64JDQGy-VbecLGkn7TuHbtZGBUIZdyw9UAj8zg5txZ" />
                        </div>
                        <div class="flex flex-col">
                            <span class="font-bold text-lg leading-none">{{ member.name }}</span>
                            <span class="text-xs text-gray-500 font-medium">{{ member.handle }}</span>
                        </div>
                    </div>

                    <!-- Role Badge/Dropdown -->
                    <div v-if="member.isCurrentUser" class="flex items-center gap-2">
                        <span
                            class="bg-background-dark text-white text-[10px] font-black uppercase px-2 py-1 rounded border border-background-dark shadow-sm">Admin</span>
                        <span class="material-symbols-outlined text-gray-400">edit</span>
                    </div>
                    <div v-else class="relative group">
                        <button
                            class="flex items-center gap-2 bg-[#A3B18A]/30 hover:bg-[#A3B18A] hover:text-white transition-colors border-[2px] border-background-dark rounded px-3 py-1.5"
                            :class="{ 'bg-gray-100 hover:bg-gray-200 text-gray-600': member.isGuest }">
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

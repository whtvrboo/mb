<script setup lang="ts">
// Mock Data
const chores = [
    { title: 'Vacuum Floor', area: 'Living Room', points: 15, assignee: 'You', dueDate: 'Today', status: 'pending', overdue: false, assigneeColor: 'bg-primary' },
    { title: 'Empty Dishwasher', area: 'Kitchen', points: 10, assignee: 'You', dueDate: 'Overdue', status: 'pending', overdue: true, assigneeColor: 'bg-primary' },
    { title: 'Take out Trash', area: 'Garbage', points: 20, assignee: 'You', status: 'completed', completedDate: 'Yesterday', assigneeColor: 'bg-primary' },
    { title: 'Water Plants', area: 'Plants', points: 5, assignee: 'You', status: 'completed', completedDate: 'Today', assigneeColor: 'bg-primary' },
]

const pendingChores = computed(() => chores.filter(c => c.status === 'pending'))
const completedChores = computed(() => chores.filter(c => c.status === 'completed'))
</script>

<template>
    <div class="bg-background-light text-background-dark font-display overflow-x-hidden min-h-screen pb-24">
        <!-- Header -->
        <header
            class="sticky top-0 z-50 bg-background-light border-b-[3px] border-background-dark px-5 h-16 flex items-center justify-between shadow-sm">
            <div class="flex items-center gap-3">
                <NuxtLink to="/"
                    class="flex items-center justify-center size-10 rounded-lg hover:bg-black/5 transition-colors">
                    <span class="material-symbols-outlined text-[28px]">arrow_back</span>
                </NuxtLink>
            </div>
            <h1 class="text-xl font-bold tracking-tight uppercase">Chores</h1>
            <div class="size-10 flex items-center justify-end">
                <button class="flex items-center justify-center size-10 rounded-lg hover:bg-black/5 transition-colors">
                    <span class="material-symbols-outlined text-[24px]">filter_list</span>
                </button>
            </div>
        </header>

        <main class="flex flex-col gap-6 p-5 w-full max-w-lg mx-auto">
            <!-- Toggle Switch -->
            <div class="w-full bg-white border-[3px] border-background-dark rounded-xl p-1.5 flex shadow-neobrutalism">
                <button
                    class="flex-1 py-2.5 rounded-lg bg-primary border-[2px] border-background-dark font-bold text-sm shadow-neobrutalism-sm transition-transform active:translate-y-0.5 active:shadow-none flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-[18px]">person</span>
                    My Tasks
                </button>
                <button
                    class="flex-1 py-2.5 rounded-lg text-background-dark/60 font-bold text-sm hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-[18px]">groups</span>
                    All Chores
                </button>
            </div>

            <!-- Stats -->
            <div class="flex justify-between items-end px-1">
                <div class="flex flex-col">
                    <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Your Effort</span>
                    <span class="text-3xl font-bold">45 <span
                            class="text-lg text-gray-400 font-medium">pts</span></span>
                </div>
                <div class="flex flex-col items-end">
                    <span class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-1">Weekly Goal</span>
                    <div class="flex gap-1">
                        <div class="w-2 h-4 bg-primary border border-background-dark rounded-sm"></div>
                        <div class="w-2 h-4 bg-primary border border-background-dark rounded-sm"></div>
                        <div class="w-2 h-4 bg-primary border border-background-dark rounded-sm"></div>
                        <div class="w-2 h-4 bg-gray-200 border border-background-dark rounded-sm"></div>
                        <div class="w-2 h-4 bg-gray-200 border border-background-dark rounded-sm"></div>
                    </div>
                </div>
            </div>

            <!-- Pending Chores -->
            <div class="flex flex-col gap-5">
                <div v-for="(chore, idx) in pendingChores" :key="idx"
                    class="relative w-full bg-white border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism-lg flex flex-col gap-4 transition-transform active:scale-[0.99]">
                    <div class="flex justify-between items-start">
                        <div class="flex flex-col gap-2">
                            <div class="flex items-center gap-2">
                                <span
                                    class="bg-primary/30 text-xs font-bold px-2 py-0.5 border border-background-dark rounded-md uppercase">{{
                                    chore.area }}</span>
                                <span
                                    class="bg-[#A3B18A] text-white text-xs font-bold px-2 py-0.5 border border-background-dark rounded-md">+{{
                                    chore.points }} pts</span>
                            </div>
                            <h3 class="text-2xl font-bold leading-tight mt-1">{{ chore.title }}</h3>
                        </div>
                        <div
                            class="size-10 rounded-full border-[3px] border-background-dark overflow-hidden bg-gray-200 shrink-0">
                            <div class="w-full h-full bg-gray-300 flex items-center justify-center font-bold">You</div>
                        </div>
                    </div>
                    <div class="h-0.5 w-full bg-black/5"></div>
                    <div class="flex justify-between items-center">
                        <span class="text-xs font-bold uppercase tracking-wide"
                            :class="chore.overdue ? 'text-red-500 flex items-center gap-1' : 'text-gray-400'">
                            <span v-if="chore.overdue"
                                class="material-symbols-outlined text-[14px]">priority_high</span>
                            {{ chore.overdue ? 'Overdue' : 'Due Today' }}
                        </span>
                        <button
                            class="flex items-center gap-2 px-4 py-2.5 bg-white border-[2px] border-background-dark rounded-lg font-bold hover:bg-gray-50 active:translate-y-0.5 active:shadow-none shadow-neobrutalism-sm transition-all text-sm group">
                            <div
                                class="size-4 border-[2px] border-background-dark rounded flex items-center justify-center group-hover:bg-primary transition-colors">
                            </div>
                            Mark Done
                        </button>
                    </div>
                </div>
            </div>

            <!-- Completed Divider -->
            <div class="flex items-center gap-4 mt-4">
                <div class="h-[3px] bg-background-dark flex-1 opacity-10"></div>
                <span class="text-xs font-bold uppercase text-background-dark/40 tracking-widest">Completed</span>
                <div class="h-[3px] bg-background-dark flex-1 opacity-10"></div>
            </div>

            <!-- Completed Chores -->
            <div class="flex flex-col gap-4 opacity-80">
                <div v-for="(chore, idx) in completedChores" :key="idx"
                    class="relative w-full bg-[#f0f0f0] border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism flex flex-col gap-4 overflow-hidden">
                    <!-- Stamp -->
                    <div
                        class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10 rotate-[-12deg] pointer-events-none">
                        <div
                            class="border-[4px] border-green-700 text-green-700 font-black text-2xl uppercase px-3 py-1 rounded-lg opacity-70 mix-blend-multiply flex items-center gap-2 shadow-sm backdrop-blur-[1px]">
                            <span class="material-symbols-outlined text-[28px] font-bold">verified</span>
                            Done
                        </div>
                    </div>

                    <div class="flex justify-between items-start opacity-60">
                        <div class="flex flex-col gap-2">
                            <div class="flex items-center gap-2">
                                <span
                                    class="bg-gray-300 text-xs font-bold px-2 py-0.5 border border-background-dark rounded-md uppercase">{{
                                    chore.area }}</span>
                                <span
                                    class="bg-gray-300 text-xs font-bold px-2 py-0.5 border border-background-dark rounded-md">+{{
                                    chore.points }} pts</span>
                            </div>
                            <h3
                                class="text-2xl font-bold leading-tight decoration-[3px] line-through decoration-background-dark">
                                {{ chore.title }}</h3>
                        </div>
                        <div
                            class="size-10 rounded-full border-[3px] border-background-dark overflow-hidden bg-gray-200 shrink-0 grayscale">
                            <div class="w-full h-full bg-gray-300 flex items-center justify-center font-bold">You</div>
                        </div>
                    </div>
                    <div class="h-0.5 w-full bg-black/5"></div>
                    <div class="flex justify-between items-center opacity-60">
                        <span class="text-xs font-bold text-gray-500 uppercase tracking-wide">{{ chore.completedDate
                            }}</span>
                        <div class="flex items-center gap-2 text-sm font-bold text-green-700">
                            <span class="material-symbols-outlined text-[18px]">check_circle</span> Verified
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

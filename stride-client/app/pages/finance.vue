<script setup lang="ts">
import Button from '~/components/ui/Button.vue'
import Card from '~/components/ui/Card.vue'

// Mock Data
const expenses = [
    { title: 'Friday Pizza Night', date: 'Oct 24 • Split evenly', amount: '-$12.50', status: 'Unpaid', icon: 'local_pizza', color: 'bg-primary/20' },
    { title: 'Cleaning Supplies', date: 'Oct 22 • You owe 50%', amount: '-$8.00', status: 'Unpaid', icon: 'cleaning_services', color: 'bg-sage/30' },
    { title: 'Bottled Water', date: 'Oct 20 • Alex paid', amount: '-$4.00', status: 'Unpaid', icon: 'water_drop', color: 'bg-blue-100' }, // dusty-blue substitute
    { title: 'Internet Bill', date: 'Oct 15 • Paid', amount: '$30.00', status: 'Paid', icon: 'router', color: 'bg-gray-200', paid: true },
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
            <h1 class="text-xl font-bold tracking-tight uppercase">Settlement</h1>
            <div class="size-10 flex items-center justify-end">
                <button class="flex items-center justify-center size-10 rounded-lg hover:bg-black/5 transition-colors">
                    <span class="material-symbols-outlined text-[24px]">more_horiz</span>
                </button>
            </div>
        </header>

        <main class="flex flex-col p-5 max-w-lg mx-auto w-full gap-6">
            <!-- Balance Card -->
            <section
                class="flex flex-col gap-0 w-full bg-white border-[3px] border-background-dark rounded-xl shadow-neobrutalism-lg overflow-hidden">
                <div class="p-6 pb-2 flex flex-col items-center text-center gap-4">
                    <div
                        class="size-20 rounded-full border-[3px] border-background-dark overflow-hidden bg-gray-200 shadow-neobrutalism-sm mb-2">
                        <!-- Avatar Placeholer -->
                        <div class="w-full h-full bg-gray-300 flex items-center justify-center text-2xl font-bold">AL
                        </div>
                    </div>
                    <div class="flex flex-col gap-1">
                        <span class="text-sm font-bold uppercase tracking-wide opacity-60">Balance Due</span>
                        <h2 class="text-4xl font-bold leading-none">You owe Alex</h2>
                        <div class="flex items-baseline justify-center gap-1 mt-1">
                            <span class="text-sm font-bold self-start mt-2">$</span>
                            <span
                                class="text-[56px] font-bold leading-none tracking-tight text-background-dark">24.50</span>
                        </div>
                    </div>
                </div>
                <div class="p-5 pt-4 flex flex-col gap-3">
                    <button
                        class="w-full h-16 bg-[#A3B18A] border-[3px] border-background-dark rounded-xl font-bold text-xl text-white shadow-neobrutalism active:translate-x-1 active:translate-y-1 active:shadow-none transition-all flex items-center justify-center gap-2 hover:brightness-105">
                        <span class="material-symbols-outlined">payments</span>
                        Pay Now
                    </button>
                    <button
                        class="w-full h-16 bg-primary border-[3px] border-background-dark rounded-xl font-bold text-xl text-background-dark shadow-neobrutalism active:translate-x-1 active:translate-y-1 active:shadow-none transition-all flex items-center justify-center gap-2 hover:brightness-105">
                        <span class="material-symbols-outlined">notifications</span>
                        Remind Me
                    </button>
                </div>
            </section>

            <!-- Breakdown -->
            <section class="flex flex-col gap-4 mt-2">
                <div class="flex items-center justify-between border-b-[3px] border-background-dark pb-2 w-full">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined">receipt_long</span>
                        <h2 class="text-xl font-bold uppercase tracking-wide">Breakdown</h2>
                    </div>
                    <span class="text-sm font-bold text-gray-500">3 items</span>
                </div>

                <div class="flex flex-col gap-3">
                    <div v-for="(item, idx) in expenses" :key="idx"
                        class="group relative w-full bg-white border-[3px] border-background-dark rounded-lg p-4 shadow-neobrutalism flex justify-between items-center transition-transform hover:-translate-y-0.5"
                        :class="{ 'bg-gray-100 opacity-70': item.paid }">
                        <div class="flex items-center gap-4">
                            <div class="size-12 border-[2px] border-background-dark rounded-lg flex items-center justify-center shrink-0"
                                :class="[item.color, item.paid ? 'grayscale' : '']">
                                <span class="material-symbols-outlined text-2xl">{{ item.icon }}</span>
                            </div>
                            <div class="flex flex-col">
                                <h3 class="text-lg font-bold leading-tight"
                                    :class="{ 'line-through decoration-2': item.paid }">{{ item.title }}</h3>
                                <span class="text-xs font-bold text-gray-500 uppercase">{{ item.date }}</span>
                            </div>
                        </div>
                        <div class="flex flex-col items-end">
                            <span class="text-lg font-bold"
                                :class="item.paid ? 'text-gray-400 decoration-2 line-through' : 'text-red-600'">{{
                                item.amount }}</span>

                            <span v-if="!item.paid"
                                class="text-xs font-medium bg-gray-100 border border-background-dark px-1.5 rounded">Unpaid</span>
                            <span v-else
                                class="text-xs font-bold text-[#7a8a61] bg-[#A3B18A]/20 border border-[#7a8a61] px-1.5 rounded flex items-center gap-0.5">
                                <span class="material-symbols-outlined text-[10px] font-black">check</span> Paid
                            </span>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useFinance } from '~/composables/useFinance'
import type { GroupBalanceSummaryResponse, ExpenseResponse } from '~/types/finance'

const { getBalances, listExpenses } = useFinance()

const balances = ref<GroupBalanceSummaryResponse | null>(null)
const expenses = ref<ExpenseResponse[]>([])
const isLoading = ref(true)

const fetchData = async () => {
    isLoading.value = true
    try {
        const [balanceData, expenseData] = await Promise.all([
            getBalances(),
            listExpenses({ limit: 5 })
        ])
        balances.value = balanceData
        expenses.value = expenseData
    } catch (e) {
        console.error('Failed to fetch finance data', e)
    } finally {
        isLoading.value = false
    }
}

// Helpers for display
const formatCurrency = (amount: number, currency = 'USD') => { // Mock currency for now if not in response
    return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount)
}

const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// Map category to icon/color (Simple mapping for now as category might be just an ID)
// Real app would fetch categories and map IDs
const getCategoryIcon = (id: number) => 'category' // Placeholder
const getCategoryColor = (id: number) => 'bg-gray-100' // Placeholder

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
            <h1 class="text-xl font-bold tracking-tight uppercase">Settlement</h1>
            <div class="size-10 flex items-center justify-end">
                <button class="flex items-center justify-center size-10 rounded-lg hover:bg-black/5 transition-colors">
                    <span class="material-symbols-outlined text-[24px]">more_horiz</span>
                </button>
            </div>
        </header>

        <main class="flex flex-col p-5 max-w-lg mx-auto w-full gap-6">

            <div v-if="isLoading" class="text-center py-10 opacity-50">Loading finances...</div>

            <!-- Balance Card -->
            <section v-if="!isLoading"
                class="flex flex-col gap-0 w-full bg-white border-[3px] border-background-dark rounded-xl shadow-neobrutalism-lg overflow-hidden">
                <div class="p-6 pb-2 flex flex-col items-center text-center gap-4">
                    <div
                        class="size-20 rounded-full border-[3px] border-background-dark overflow-hidden bg-gray-200 shadow-neobrutalism-sm mb-2">
                        <!-- Avatar Placeholer -->
                        <div class="w-full h-full bg-gray-300 flex items-center justify-center text-2xl font-bold">$$
                        </div>
                    </div>
                    <div class="flex flex-col gap-1">
                        <span class="text-sm font-bold uppercase tracking-wide opacity-60">Total Balance</span>
                        <h2 class="text-4xl font-bold leading-none">
                            <!-- Just showing strict you owe vs you are owed for simplicity. Real app needs breakdown -->
                            {{ 0 }} <!-- Placeholder for computed balance -->
                        </h2>
                        <div class="flex items-baseline justify-center gap-1 mt-1">
                            <span class="text-sm font-bold opacity-70">
                                (Summary placeholder)
                            </span>
                        </div>
                    </div>
                </div>

                <div
                    class="grid grid-cols-2 border-t-[3px] border-background-dark divide-x-[3px] divide-background-dark mt-4 bg-gray-50">
                    <button
                        class="py-4 hover:bg-primary hover:text-background-dark transition-colors flex flex-col items-center gap-1 group">
                        <span
                            class="material-symbols-outlined text-3xl group-hover:scale-110 transition-transform">payments</span>
                        <span class="font-black text-xs uppercase tracking-widest">Pay Now</span>
                    </button>
                    <button
                        class="py-4 hover:bg-[#8E9DB3] hover:text-white transition-colors flex flex-col items-center gap-1 group">
                        <span
                            class="material-symbols-outlined text-3xl group-hover:scale-110 transition-transform">notifications_active</span>
                        <span class="font-black text-xs uppercase tracking-widest">Remind</span>
                    </button>
                </div>
            </section>

            <!-- History / Expenses Section -->
            <section v-if="!isLoading" class="flex flex-col gap-4">
                <div class="flex items-center justify-between px-1">
                    <h3 class="font-bold text-lg uppercase tracking-wide">Recent Expenses</h3>
                    <button
                        class="text-xs font-bold underline decoration-2 underline-offset-2 hover:text-primary transition-colors">See
                        All</button>
                </div>

                <div v-if="expenses.length === 0" class="text-center py-4 opacity-50 font-bold">No expenses yet.</div>

                <div v-for="expense in expenses" :key="expense.id"
                    class="flex items-center justify-between bg-white border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism hover:-translate-y-1 transition-transform cursor-pointer">
                    <div class="flex items-center gap-4">
                        <div class="size-12 rounded-lg border-[2px] border-background-dark flex items-center justify-center text-background-dark"
                            :class="getCategoryColor(expense.category_id)">
                            <span class="material-symbols-outlined">{{ getCategoryIcon(expense.category_id) }}</span>
                        </div>
                        <div class="flex flex-col">
                            <h4 class="font-bold text-lg leading-none">{{ expense.title }}</h4>
                            <span class="text-xs font-bold text-gray-500 mt-1">{{ formatDate(expense.date) }} • {{
                                'Split' }}</span>
                        </div>
                    </div>

                    <div class="flex flex-col items-end gap-1">
                        <span class="font-bold text-lg">{{ formatCurrency(expense.amount) }}</span>
                        <span
                            class="text-[10px] font-black uppercase px-1.5 py-0.5 rounded border border-gray-300 bg-gray-100 text-gray-500">
                            Paid
                        </span>
                    </div>
                </div>
            </section>

        </main>
    </div>
</template>

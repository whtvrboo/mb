<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useGovernance } from '~/composables/useGovernance'
import type { ProposalResponse } from '~/types/governance'

const { listProposals } = useGovernance()

const proposals = ref<ProposalResponse[]>([])
const isLoading = ref(true)

const fetchData = async () => {
    isLoading.value = true
    try {
        proposals.value = await listProposals()
    } catch (e) {
        console.error('Failed to fetch proposals', e)
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchData()
})

const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
        case 'active': return 'bg-green-100 text-green-800 border-green-500'
        case 'passed': return 'bg-primary text-background-dark border-background-dark'
        case 'rejected': return 'bg-red-100 text-red-800 border-red-500'
        default: return 'bg-gray-100 text-gray-800 border-gray-500'
    }
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
            <h1 class="text-xl font-bold tracking-tight uppercase">Governance</h1>
            <div class="size-10 flex items-center justify-end">
                <span class="material-symbols-outlined text-[24px]">how_to_vote</span>
            </div>
        </header>

        <main class="flex flex-col gap-6 p-5 max-w-lg mx-auto w-full">
            <h2 class="text-3xl font-black uppercase leading-none mb-2">House<br />Proposals</h2>

            <div v-if="isLoading" class="text-center py-10 opacity-50">Loading votes...</div>
            <div v-if="!isLoading && proposals.length === 0"
                class="bg-white border-[3px] border-background-dark rounded-xl p-8 text-center opacity-60">
                <span class="material-symbols-outlined text-6xl mb-2"> casilla </span>
                <p class="font-bold text-lg">No active proposals.</p>
            </div>

            <div v-for="proposal in proposals" :key="proposal.id"
                class="bg-white border-[3px] border-background-dark rounded-xl overflow-hidden shadow-neobrutalism">
                <div class="bg-gray-50 border-b-[3px] border-background-dark p-4 flex justify-between items-center">
                    <span class="text-xs font-bold bg-white px-2 py-1 rounded border-[2px]"
                        :class="getStatusColor(proposal.status)">
                        {{ proposal.status }}
                    </span>
                    <span class="text-xs font-bold opacity-60">Vote #{{ proposal.id }}</span>
                </div>
                <div class="p-6">
                    <h3 class="font-bold text-2xl leading-tight mb-2">{{ proposal.title }}</h3>
                    <!-- <p class="text-sm font-medium opacity-80">{{ proposal.description }}</p> -->

                    <div class="mt-4 pt-4 border-t-[2px] border-dashed border-gray-200">
                        <button
                            class="w-full bg-background-dark text-white font-bold uppercase py-3 rounded-lg hover:bg-primary hover:text-background-dark transition-colors border-[2px] border-background-dark">
                            View Ballot
                        </button>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

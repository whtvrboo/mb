<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    currentPage: number
    totalPages: number
    visiblePages?: number
}

const props = withDefaults(defineProps<Props>(), {
    visiblePages: 5
})

const emit = defineEmits(['update:currentPage', 'change'])

const pages = computed(() => {
    const range = []
    const start = Math.max(1, props.currentPage - Math.floor(props.visiblePages / 2))
    const end = Math.min(props.totalPages, start + props.visiblePages - 1)

    if (end - start + 1 < props.visiblePages) {
        const adjustStart = Math.max(1, end - props.visiblePages + 1)
        for (let i = adjustStart; i <= end; i++) range.push(i)
    } else {
        for (let i = start; i <= end; i++) range.push(i)
    }
    return range
})

const goToPage = (page: number) => {
    if (page >= 1 && page <= props.totalPages && page !== props.currentPage) {
        emit('update:currentPage', page)
        emit('change', page)
    }
}
</script>

<template>
    <nav aria-label="Pagination" class="flex items-center justify-center gap-2" v-if="totalPages > 1">
        <!-- Previous Button -->
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1"
            aria-label="Previous page"
            class="flex items-center justify-center size-10 rounded-lg border-[2px] border-background-dark bg-white shadow-[2px_2px_0px_0px_#221f10] active:translate-x-0.5 active:translate-y-0.5 active:shadow-none hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transition-all">
            <span class="material-symbols-outlined">chevron_left</span>
        </button>

        <!-- Page Numbers -->
        <div class="flex items-center gap-1 mx-2">
            <button v-for="page in pages" :key="page" @click="goToPage(page)"
                :aria-label="'Page ' + page"
                :aria-current="page === currentPage ? 'page' : undefined"
                class="flex items-center justify-center size-10 rounded-lg border-[2px] font-bold transition-all"
                :class="page === currentPage
                    ? 'bg-primary border-background-dark shadow-[2px_2px_0px_0px_#221f10] -translate-y-0.5'
                    : 'bg-transparent border-transparent hover:bg-gray-100 text-gray-500'">
                {{ page }}
            </button>
        </div>

        <!-- Next Button -->
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages"
            aria-label="Next page"
            class="flex items-center justify-center size-10 rounded-lg border-[2px] border-background-dark bg-white shadow-[2px_2px_0px_0px_#221f10] active:translate-x-0.5 active:translate-y-0.5 active:shadow-none hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transition-all">
            <span class="material-symbols-outlined">chevron_right</span>
        </button>
    </nav>
</template>

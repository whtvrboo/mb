<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useCalendar } from '~/composables/useCalendar'
import type { CalendarFeedResponse, CalendarEventItem } from '~/types/calendar'

const { getFeed } = useCalendar()

const feed = ref<CalendarEventItem[]>([])
const isLoading = ref(true)
const currentDate = new Date()

const fetchData = async () => {
    isLoading.value = true
    try {
        const today = new Date().toISOString().split('T')[0]
        // Fetch next 30 days? API signature usually defaults or takes range.
        // useCalendar definition: getFeed: (params?: { start_date?: string; end_date?: string })
        const nextMonth = new Date()
        nextMonth.setDate(nextMonth.getDate() + 30)

        const data = await getFeed({
            start_date: today,
            end_date: nextMonth.toISOString().split('T')[0]
        })

        // Ensure data is array (API might return object if mapped by date, types said CalendarEventItem[])
        if (Array.isArray(data)) {
            feed.value = data
        } else {
            console.warn('Calendar API did not return array', data)
            feed.value = []
        }
    } catch (e) {
        console.error('Failed to fetch calendar', e)
    } finally {
        isLoading.value = false
    }
}

const eventsByDate = computed(() => {
    const groups: Record<string, CalendarEventItem[]> = {}
    feed.value.forEach(event => {
        const d = event.event_date
        if (!groups[d]) groups[d] = []
        groups[d].push(event)
    })
    // Sort items within day?
    return Object.fromEntries(
        Object.entries(groups).sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
    )
})

const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    // Check if today
    if (new Date(date).setHours(0, 0, 0, 0) === today.getTime()) return 'Today'

    return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })
}

const getEventIcon = (category?: string) => {
    switch (category?.toLowerCase()) {
        case 'chore': return 'check_box'
        case 'bill': return 'payments'
        case 'event': return 'event'
        default: return 'event_note'
    }
}

const getEventColor = (category?: string) => {
    switch (category?.toLowerCase()) {
        case 'chore': return 'bg-primary border-background-dark'
        case 'bill': return 'bg-red-100 text-red-800 border-red-500'
        default: return 'bg-white border-background-dark'
    }
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
                    class="flex items-center justify-center size-10 rounded-lg border-[2px] border-transparent hover:border-background-dark hover:bg-black/5 transition-colors">
                    <span class="material-symbols-outlined text-[28px]">arrow_back</span>
                </NuxtLink>
            </div>
            <h1 class="text-xl font-bold tracking-tight uppercase">Calendar</h1>
            <div class="size-10 flex items-center justify-end">
                <span class="material-symbols-outlined text-[24px]">calendar_month</span>
            </div>
        </header>

        <main class="flex flex-col gap-6 p-5 max-w-lg mx-auto w-full">
            <div v-if="isLoading" class="text-center py-10 opacity-50">Loading schedule...</div>

            <div v-if="!isLoading && feed.length === 0" class="text-center py-10 opacity-50 font-bold">No upcoming
                events found.</div>

            <div v-for="(items, date) in eventsByDate" :key="date" class="flex flex-col gap-2">
                <h2
                    class="text-sm font-bold uppercase tracking-widest opacity-60 sticky top-20 bg-background-light/95 backdrop-blur py-2 z-10">
                    {{ formatDate(date) }}
                </h2>

                <div v-for="event in items" :key="event.id || event.title"
                    class="flex items-center gap-4 border-[3px] rounded-xl p-4 shadow-sm"
                    :class="getEventColor(event.category)">

                    <div
                        class="size-10 rounded-full border-[2px] border-background-dark flex items-center justify-center bg-white/50 shrink-0">
                        <span class="material-symbols-outlined">{{ getEventIcon(event.category) }}</span>
                    </div>

                    <div class="flex flex-col">
                        <h3 class="font-bold text-lg leading-tight">{{ event.title }}</h3>
                        <div class="flex items-center gap-2 text-xs font-bold opacity-70">
                            <span v-if="!event.is_all_day && event.event_time">{{ event.event_time }}</span>
                            <span v-else>All Day</span>
                            <span v-if="event.description">• {{ event.description }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

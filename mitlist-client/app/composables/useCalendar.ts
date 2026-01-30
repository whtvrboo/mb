import type { CalendarFeedResponse } from '~/types/calendar'

export function useCalendar() {
  return {
    getFeed: (params?: { start_date?: string; end_date?: string }) =>
      useApi<CalendarFeedResponse>('/calendar/feed', { query: params }),
  }
}

/** Calendar module types: Calendar feed events */

export interface CalendarEventItem {
  id?: string
  title: string
  description?: string | null
  event_date: string
  event_time?: string | null
  end_time?: string | null
  is_all_day?: boolean
  category?: string
  source_type?: string
  source_id?: number
  [key: string]: unknown
}

export type CalendarFeedResponse = CalendarEventItem[]

/** Common API types: errors, pagination, and base options */

export interface ApiError {
  code: string
  detail?: string
  message?: string
  status?: number
  details?: Record<string, unknown>
}

export interface PaginationParams {
  limit?: number
  offset?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total_count: number
  has_more: boolean
}

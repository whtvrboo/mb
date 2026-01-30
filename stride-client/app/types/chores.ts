/** Chores module types: Chore, ChoreAssignment, ChoreTemplate, Stats */

export type ChoreFrequencyType = 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'CUSTOM' | 'SEASONAL'
export type ChoreCategory = 'CLEANING' | 'OUTDOOR' | 'MAINTENANCE' | 'ADMIN' | 'OTHER'
export type RotationStrategy = 'ROUND_ROBIN' | 'LEAST_BUSY' | 'RANDOM'
export type ChoreAssignmentStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED'

export interface ChoreResponse {
  id: number
  group_id: number
  name: string
  description: string | null
  frequency_type: ChoreFrequencyType
  interval_value: number
  effort_value: number
  estimated_duration_minutes: number | null
  category: ChoreCategory | null
  is_rotating: boolean
  rotation_strategy: RotationStrategy | null
  required_item_concept_id: number | null
  last_assigned_to_id: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ChoreCreate {
  group_id: number
  name: string
  description?: string | null
  frequency_type: ChoreFrequencyType
  interval_value?: number
  effort_value: number
  estimated_duration_minutes?: number | null
  category?: ChoreCategory | null
  is_rotating?: boolean
  rotation_strategy?: RotationStrategy | null
  required_item_concept_id?: number | null
}

export interface ChoreUpdate {
  name?: string | null
  description?: string | null
  frequency_type?: ChoreFrequencyType | null
  interval_value?: number | null
  effort_value?: number | null
  estimated_duration_minutes?: number | null
  category?: ChoreCategory | null
  is_rotating?: boolean | null
  rotation_strategy?: RotationStrategy | null
  required_item_concept_id?: number | null
  is_active?: boolean | null
}

export interface ChoreAssignmentResponse {
  id: number
  chore_id: number
  assigned_to_id: number
  due_date: string
  status: ChoreAssignmentStatus
  notes: string | null
  completed_at: string | null
  completed_by_id: number | null
  started_at: string | null
  actual_duration_minutes: number | null
  quality_rating: number | null
  rated_by_id: number | null
  created_at: string
  updated_at: string
}

export interface ChoreAssignmentWithChoreResponse extends ChoreAssignmentResponse {
  chore: ChoreResponse
}

export interface ChoreAssignmentCompleteRequest {
  actual_duration_minutes?: number | null
  notes?: string | null
}

export interface ChoreAssignmentReassignRequest {
  assigned_to_id: number
}

export interface ChoreAssignmentRateRequest {
  quality_rating: number
}

export interface ChoreDependencyResponse {
  id: number
  chore_id: number
  depends_on_chore_id: number
  dependency_type: string
  created_at: string
  updated_at: string
}

export interface ChoreDependencyCreate {
  chore_id: number
  depends_on_chore_id: number
  dependency_type: string
}

export interface ChoreTemplateResponse {
  id: number
  name: string
  description: string | null
  frequency_type: ChoreFrequencyType
  interval_value: number
  effort_value: number
  category: ChoreCategory | null
  is_public: boolean
  use_count: number
  created_at: string
  updated_at: string
}

export interface ChoreTemplateCreate {
  name: string
  description?: string | null
  frequency_type: ChoreFrequencyType
  interval_value?: number
  effort_value: number
  category?: ChoreCategory | null
  is_public?: boolean
}

export interface ChoreFromTemplateRequest {
  template_id: number
  group_id: number
  name?: string | null
  frequency_type?: ChoreFrequencyType | null
  interval_value?: number | null
}

export interface ChoreStatisticsResponse {
  total_chores: number
  active_chores: number
  total_assignments: number
  completed_assignments: number
  pending_assignments: number
  overdue_assignments: number
  completion_rate: number
  average_completion_time_minutes: number | null
}

export interface UserChoreStatsResponse {
  user_id: number
  total_assigned: number
  completed: number
  pending: number
  skipped: number
  total_effort_points: number
  average_quality_rating: number | null
  completion_rate: number
}

export interface ChoreLeaderboardResponse {
  group_id: number
  period_start: string
  period_end: string
  rankings: UserChoreStatsResponse[]
}

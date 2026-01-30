/** Audit module types: AuditLog, Report, Tag */

export interface AuditLogResponse {
  id: number
  group_id: number
  user_id: number | null
  action: string
  entity_type: string
  entity_id: number | null
  old_values: Record<string, unknown> | null
  new_values: Record<string, unknown> | null
  ip_address: string | null
  user_agent: string | null
  occurred_at: string
  created_at: string
  updated_at: string
}

export interface AuditLogListResponse {
  logs: AuditLogResponse[]
  total_count: number
  has_more: boolean
}

export interface EntityHistoryResponse {
  entity_type: string
  entity_id: number
  history: AuditLogResponse[]
  total_changes: number
  created_by_user_id: number | null
  created_at: string | null
  last_modified_by_user_id: number | null
  last_modified_at: string | null
}

export interface ReportSnapshotResponse {
  id: number
  group_id: number
  report_type: string
  period_start_date: string | null
  period_end_date: string | null
  data_json: Record<string, unknown> | null
  generated_at: string
  created_at: string
  updated_at: string
}

export interface GenerateReportRequest {
  group_id: number
  report_type: string
  period_start_date?: string | null
  period_end_date?: string | null
}

export interface TagResponse {
  id: number
  group_id: number
  name: string
  color_hex: string | null
  created_at: string
  updated_at: string
}

export interface TagCreate {
  group_id: number
  name: string
  color_hex?: string | null
}

export interface TagUpdate {
  name?: string | null
  color_hex?: string | null
}

export interface TagAssignmentResponse {
  id: number
  tag_id: number
  entity_type: string
  entity_id: number
  created_at: string
  updated_at: string
}

export interface TagAssignmentCreate {
  tag_id: number
  entity_type: string
  entity_id: number
}

export interface EntityTagsResponse {
  entity_type: string
  entity_id: number
  tags: TagResponse[]
}

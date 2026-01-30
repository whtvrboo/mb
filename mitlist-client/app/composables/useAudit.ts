import type {
  AuditLogListResponse,
  EntityHistoryResponse,
  ReportSnapshotResponse,
  GenerateReportRequest,
  TagResponse,
  TagCreate,
  TagUpdate,
  TagAssignmentResponse,
  TagAssignmentCreate,
  EntityTagsResponse,
} from '~/types/audit'

export function useAudit() {
  const $api = useNuxtApp().$api

  return {
    getSystemStats: () => useApi<Record<string, unknown>>('/admin/system-stats'),
    broadcast: (title: string, body: string) =>
      $api<void>('/admin/broadcast', {
        method: 'POST',
        query: { title, body },
      }),

    getAuditTrail: (params?: {
      entity_type?: string
      entity_id?: number
      user_id?: number
      action?: string
      limit?: number
      offset?: number
    }) =>
      useApi<AuditLogListResponse>('/admin/audit-trail', { query: params }),
    getEntityHistory: (params: { entity_type: string; entity_id: number }) =>
      useApi<EntityHistoryResponse>('/admin/audit-trail/entity', {
        query: params,
      }),

    getMaintenanceMode: () =>
      useApi<{ enabled: boolean; message?: string }>('/admin/maintenance-mode'),
    setMaintenanceMode: (enabled: boolean, message?: string) =>
      $api<{ enabled: boolean; message: string }>('/admin/maintenance-mode', {
        method: 'POST',
        query: { enabled, message: message ?? '' },
      }),

    listReports: (params?: { report_type?: string; limit?: number }) =>
      useApi<ReportSnapshotResponse[]>('/admin/reports', { query: params }),
    generateReport: (data: GenerateReportRequest) =>
      $api<ReportSnapshotResponse>('/admin/reports/generate', {
        method: 'POST',
        body: data,
      }),

    listTags: () => useApi<TagResponse[]>('/admin/tags'),
    createTag: (data: TagCreate) =>
      $api<TagResponse>('/admin/tags', { method: 'POST', body: data }),
    updateTag: (tagId: number, data: TagUpdate) =>
      $api<TagResponse>(`/admin/tags/${tagId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteTag: (tagId: number) =>
      $api<void>(`/admin/tags/${tagId}`, { method: 'DELETE' }),
    assignTag: (data: TagAssignmentCreate) =>
      $api<TagAssignmentResponse>('/admin/tags/assign', {
        method: 'POST',
        body: data,
      }),
    getEntityTags: (params: { entity_type: string; entity_id: number }) =>
      useApi<EntityTagsResponse>('/admin/tags/entity', { query: params }),
  }
}

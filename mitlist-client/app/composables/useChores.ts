import type {
  ChoreResponse,
  ChoreCreate,
  ChoreUpdate,
  ChoreAssignmentResponse,
  ChoreAssignmentWithChoreResponse,
  ChoreAssignmentCompleteRequest,
  ChoreAssignmentReassignRequest,
  ChoreAssignmentRateRequest,
  ChoreDependencyResponse,
  ChoreDependencyCreate,
  ChoreTemplateResponse,
  ChoreTemplateCreate,
  ChoreFromTemplateRequest,
  ChoreStatisticsResponse,
  UserChoreStatsResponse,
  ChoreLeaderboardResponse,
} from '~/types/chores'

export function useChores() {
  const $api = useNuxtApp().$api

  return {
    listChores: (params?: { active_only?: boolean }) =>
      useApi<ChoreResponse[]>('/chores', { query: params }),
    getChore: (choreId: number) =>
      useApi<ChoreResponse>(`/chores/${choreId}`),
    createChore: (data: ChoreCreate) =>
      $api<ChoreResponse>('/chores', { method: 'POST', body: data }),
    updateChore: (choreId: number, data: ChoreUpdate) =>
      $api<ChoreResponse>(`/chores/${choreId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteChore: (choreId: number) =>
      $api<void>(`/chores/${choreId}`, { method: 'DELETE' }),

    listAssignments: (params?: {
      due_date?: string
      status_filter?: string
    }) =>
      useApi<ChoreAssignmentWithChoreResponse[]>('/chores/assignments', {
        query: params,
      }),
    completeAssignment: (
      assignmentId: number,
      data: ChoreAssignmentCompleteRequest,
    ) =>
      $api<ChoreAssignmentResponse>(
        `/chores/assignments/${assignmentId}/complete`,
        { method: 'PATCH', body: data },
      ),
    skipAssignment: (assignmentId: number) =>
      $api<ChoreAssignmentResponse>(
        `/chores/assignments/${assignmentId}/skip`,
        { method: 'PATCH' },
      ),
    reassignAssignment: (
      assignmentId: number,
      data: ChoreAssignmentReassignRequest,
    ) =>
      $api<ChoreAssignmentResponse>(
        `/chores/assignments/${assignmentId}/reassign`,
        { method: 'PATCH', body: data },
      ),
    startAssignment: (assignmentId: number) =>
      $api<ChoreAssignmentResponse>(
        `/chores/assignments/${assignmentId}/start`,
        { method: 'PATCH' },
      ),
    rateAssignment: (
      assignmentId: number,
      data: ChoreAssignmentRateRequest,
    ) =>
      $api<ChoreAssignmentResponse>(
        `/chores/assignments/${assignmentId}/rate`,
        { method: 'POST', body: data },
      ),

    listHistory: (params?: { limit?: number; offset?: number }) =>
      useApi<ChoreAssignmentWithChoreResponse[]>('/chores/history', {
        query: params,
      }),

    getStats: () => useApi<ChoreStatisticsResponse>('/chores/stats'),
    getMyStats: () => useApi<UserChoreStatsResponse>('/chores/stats/me'),
    getLeaderboard: () =>
      useApi<ChoreLeaderboardResponse>('/chores/leaderboard'),

    listDependencies: (choreId: number) =>
      useApi<ChoreDependencyResponse[]>(`/chores/${choreId}/dependencies`),
    addDependency: (choreId: number, data: ChoreDependencyCreate) =>
      $api<ChoreDependencyResponse>(`/chores/${choreId}/dependencies`, {
        method: 'POST',
        body: data,
      }),
    removeDependency: (dependencyId: number) =>
      $api<void>(`/chores/dependencies/${dependencyId}`, {
        method: 'DELETE',
      }),

    listTemplates: (params?: { include_public?: boolean }) =>
      useApi<ChoreTemplateResponse[]>('/chores/templates', { query: params }),
    createTemplate: (data: ChoreTemplateCreate) =>
      $api<ChoreTemplateResponse>('/chores/templates', {
        method: 'POST',
        body: data,
      }),
    createChoreFromTemplate: (
      templateId: number,
      data: ChoreFromTemplateRequest,
    ) =>
      $api<ChoreResponse>(`/chores/templates/${templateId}/instantiate`, {
        method: 'POST',
        body: data,
      }),
  }
}

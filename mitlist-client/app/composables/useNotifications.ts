import type {
  NotificationListResponse,
  NotificationResponse,
  NotificationMarkAllReadRequest,
  NotificationPreferenceResponse,
  NotificationPreferenceCreate,
  CommentWithReactionsResponse,
  CommentResponse,
  CommentCreate,
  CommentUpdate,
  ReactionResponse,
  ReactionToggleRequest,
  ReactionToggleResponse,
} from '~/types/notifications'

export function useNotifications() {
  const $api = useNuxtApp().$api

  return {
    listNotifications: (params?: {
      unread_only?: boolean
      limit?: number
      offset?: number
    }) =>
      useApi<NotificationListResponse>('/notifications', { query: params }),
    markRead: (notificationId: number) =>
      $api<NotificationResponse>(
        `/notifications/${notificationId}/read`,
        { method: 'PATCH' },
      ),
    markAllRead: (data?: NotificationMarkAllReadRequest) =>
      $api<void>('/notifications/clear', {
        method: 'POST',
        body: data ?? {},
      }),
    getUnreadCount: () =>
      useApi<{ unread_count: number }>('/notifications/count'),

    listPreferences: () =>
      useApi<NotificationPreferenceResponse[]>('/notifications/preferences'),
    updatePreference: (data: NotificationPreferenceCreate) =>
      $api<NotificationPreferenceResponse>('/notifications/preferences', {
        method: 'PATCH',
        body: data,
      }),

    listComments: (params: {
      parent_type: string
      parent_id: number
      limit?: number
      offset?: number
    }) =>
      useApi<CommentWithReactionsResponse[]>('/comments', {
        query: params,
      }),
    createComment: (data: CommentCreate) =>
      $api<CommentResponse>('/comments', {
        method: 'POST',
        body: data,
      }),
    updateComment: (commentId: number, data: CommentUpdate) =>
      $api<CommentResponse>(`/comments/${commentId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteComment: (commentId: number) =>
      $api<void>(`/comments/${commentId}`, {
        method: 'DELETE',
      }),

    toggleReaction: (data: ReactionToggleRequest) =>
      $api<ReactionToggleResponse>('/reactions/toggle', {
        method: 'POST',
        body: data,
      }),
    listReactions: (params: { target_type: string; target_id: number }) =>
      useApi<ReactionResponse[]>('/reactions', {
        query: params,
      }),
  }
}

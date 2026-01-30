/** Notifications module types: Notification, Comment, Reaction, Preferences */

export interface NotificationResponse {
  id: number
  user_id: number
  group_id: number | null
  type: string
  title: string
  body: string | null
  link_url: string | null
  priority: string
  is_read: boolean
  read_at: string | null
  delivered_at: string | null
  created_at: string
  updated_at: string
}

export interface NotificationListResponse {
  notifications: NotificationResponse[]
  total_count: number
  unread_count: number
  has_more: boolean
}

export interface NotificationMarkAllReadRequest {
  group_id?: number | null
}

export interface MentionResponse {
  id: number
  comment_id: number
  mentioned_user_id: number
  is_read: boolean
  created_at: string
  updated_at: string
}

export interface ReactionResponse {
  id: number
  user_id: number
  target_type: string
  target_id: number
  emoji_code: string
  comment_id: number | null
  created_at: string
  updated_at: string
}

export interface CommentResponse {
  id: number
  author_id: number
  parent_type: string
  parent_id: number
  content: string
  is_edited: boolean
  edited_at: string | null
  deleted_at: string | null
  created_at: string
  updated_at: string
  mentions?: MentionResponse[]
}

export interface CommentWithReactionsResponse extends CommentResponse {
  mentions: MentionResponse[]
  reactions: ReactionResponse[]
  reaction_counts: Record<string, number>
}

export interface CommentCreate {
  parent_type: string
  parent_id: number
  content: string
  mentioned_user_ids?: number[]
}

export interface CommentUpdate {
  content: string
}

export interface ReactionToggleRequest {
  target_type: string
  target_id: number
  emoji_code: string
}

export interface ReactionToggleResponse {
  action: 'added' | 'removed'
  reaction: ReactionResponse | null
}

export interface NotificationPreferenceResponse {
  id: number
  user_id: number
  event_type: string
  channel: string
  enabled: boolean
  advance_notice_hours: number | null
  quiet_hours_start: string | null
  created_at: string
  updated_at: string
}

export interface NotificationPreferenceCreate {
  event_type: string
  channel: string
  enabled: boolean
  advance_notice_hours?: number | null
}

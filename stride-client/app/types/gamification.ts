/** Gamification module types: Points, Achievement, Streak, Leaderboard */

export interface UserPointsResponse {
  id: number
  user_id: number
  group_id: number
  total_points: number
  monthly_points: number
  last_reset_at: string | null
  rank_position: number | null
  created_at: string
  updated_at: string
}

export interface AwardPointsRequest {
  user_id: number
  group_id: number
  points: number
  reason?: string | null
}

export interface AwardPointsResponse {
  user_id: number
  points_awarded: number
  new_total: number
  new_monthly: number
  reason: string | null
}

export interface AchievementResponse {
  id: number
  name: string
  description: string | null
  badge_icon_url: string | null
  category: string | null
  requirement_type: string | null
  requirement_value: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserAchievementWithDetailsResponse {
  id: number
  user_id: number
  achievement_id: number
  progress_percentage: number
  earned_at: string
  created_at: string
  updated_at: string
  achievement: AchievementResponse
}

export interface StreakResponse {
  id: number
  user_id: number
  group_id: number
  activity_type: string
  current_streak_days: number
  longest_streak_days: number
  last_activity_date: string | null
  created_at: string
  updated_at: string
}

export interface StreakRecordActivityRequest {
  activity_type: string
  group_id: number
}

export interface StreakRecordActivityResponse {
  streak: StreakResponse
  streak_extended: boolean
  is_new_record: boolean
}

export interface LeaderboardEntryResponse {
  rank: number
  user_id: number
  user_name: string
  avatar_url: string | null
  value: number
  change_from_previous: number | null
}

export interface LeaderboardWithEntriesResponse {
  id: number
  group_id: number
  period_type: string
  metric: string
  period_start_date: string
  period_end_date: string | null
  created_at: string
  updated_at: string
  entries: LeaderboardEntryResponse[]
  total_participants: number
  current_user_rank: number | null
}

export interface UserGamificationSummaryResponse {
  user_id: number
  group_id: number
  total_points: number
  monthly_points: number
  rank_position: number | null
  achievements_earned: number
  total_achievements: number
  active_streaks: number
  longest_streak_ever: number
  recent_achievements: AchievementResponse[]
}

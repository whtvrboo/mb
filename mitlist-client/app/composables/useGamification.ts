import type {
  UserPointsResponse,
  AwardPointsRequest,
  AwardPointsResponse,
  AchievementResponse,
  UserAchievementWithDetailsResponse,
  StreakResponse,
  StreakRecordActivityRequest,
  StreakRecordActivityResponse,
  LeaderboardWithEntriesResponse,
  UserGamificationSummaryResponse,
} from '~/types/gamification'

export function useGamification() {
  const $api = useNuxtApp().$api

  return {
    getPoints: () => useApi<UserPointsResponse>('/gamification/points'),
    awardPoints: (data: AwardPointsRequest) =>
      $api<AwardPointsResponse>('/gamification/points/award', {
        method: 'POST',
        body: data,
      }),

    listAchievements: (params?: { category?: string }) =>
      useApi<AchievementResponse[]>('/gamification/achievements', {
        query: params,
      }),
    getMyAchievements: () =>
      useApi<UserAchievementWithDetailsResponse[]>('/gamification/achievements/me'),
    checkAchievements: () =>
      $api<AchievementResponse[]>('/gamification/achievements/check', {
        method: 'POST',
      }),

    getStreaks: () => useApi<StreakResponse[]>('/gamification/streaks'),
    recordActivity: (data: StreakRecordActivityRequest) =>
      $api<StreakRecordActivityResponse>('/gamification/streaks/record', {
        method: 'POST',
        body: data,
      }),

    getLeaderboard: (params?: {
      period_type?: string
      metric?: string
    }) =>
      useApi<LeaderboardWithEntriesResponse>('/gamification/leaderboard', {
        query: params,
      }),

    getSummary: () =>
      useApi<UserGamificationSummaryResponse>('/gamification/summary'),
  }
}

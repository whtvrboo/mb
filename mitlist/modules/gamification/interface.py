"""
Gamification module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
Never import models or service directly from other modules.
"""

from mitlist.modules.gamification import schemas, service

__all__ = [
    "schemas",
    # Points
    "get_user_points",
    "get_or_create_user_points",
    "award_points",
    "reset_monthly_points",
    # Achievements
    "list_achievements",
    "get_achievement_by_id",
    "get_user_achievements",
    "award_achievement",
    "check_and_award_achievements",
    # Streaks
    "get_user_streaks",
    "get_streak",
    "record_activity",
    # Leaderboard
    "get_leaderboard",
    "get_user_gamification_summary",
]

get_user_points = service.get_user_points
get_or_create_user_points = service.get_or_create_user_points
award_points = service.award_points
reset_monthly_points = service.reset_monthly_points

list_achievements = service.list_achievements
get_achievement_by_id = service.get_achievement_by_id
get_user_achievements = service.get_user_achievements
award_achievement = service.award_achievement
check_and_award_achievements = service.check_and_award_achievements

get_user_streaks = service.get_user_streaks
get_streak = service.get_streak
record_activity = service.record_activity

get_leaderboard = service.get_leaderboard
get_user_gamification_summary = service.get_user_gamification_summary

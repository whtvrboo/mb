"""Gamification module Pydantic schemas for request/response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ====================
# UserPoints Schemas
# ====================
class UserPointsBase(BaseModel):
    """Base user points schema."""

    total_points: int = Field(0, ge=0)
    monthly_points: int = Field(0, ge=0)


class UserPointsCreate(UserPointsBase):
    """Schema for creating user points record."""

    user_id: int
    group_id: int


class UserPointsUpdate(BaseModel):
    """Schema for updating user points."""

    total_points: Optional[int] = Field(None, ge=0)
    monthly_points: Optional[int] = Field(None, ge=0)


class UserPointsResponse(UserPointsBase):
    """Schema for user points response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    group_id: int
    last_reset_at: Optional[datetime] = None
    rank_position: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class AwardPointsRequest(BaseModel):
    """Schema for awarding points to a user."""

    user_id: int
    group_id: int
    points: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1, max_length=255)


class AwardPointsResponse(BaseModel):
    """Schema for award points response."""

    user_id: int
    points_awarded: int
    new_total: int
    new_monthly: int
    reason: str


# ====================
# Achievement Schemas
# ====================
class AchievementBase(BaseModel):
    """Base achievement schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=500)
    badge_icon_url: Optional[str] = Field(None, max_length=500)
    category: str = Field(..., pattern="^(CHORES|FINANCE|PLANTS|PETS)$")
    requirement_type: str = Field(..., pattern="^(POINTS|COUNT|STREAK)$")
    requirement_value: int = Field(..., ge=1)


class AchievementCreate(AchievementBase):
    """Schema for creating an achievement."""

    is_active: bool = True


class AchievementUpdate(BaseModel):
    """Schema for updating an achievement."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    badge_icon_url: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, pattern="^(CHORES|FINANCE|PLANTS|PETS)$")
    requirement_type: Optional[str] = Field(None, pattern="^(POINTS|COUNT|STREAK)$")
    requirement_value: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class AchievementResponse(AchievementBase):
    """Schema for achievement response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ====================
# UserAchievement Schemas
# ====================
class UserAchievementBase(BaseModel):
    """Base user achievement schema."""

    progress_percentage: int = Field(0, ge=0, le=100)


class UserAchievementCreate(UserAchievementBase):
    """Schema for creating a user achievement."""

    user_id: int
    achievement_id: int
    earned_at: datetime


class UserAchievementResponse(UserAchievementBase):
    """Schema for user achievement response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    achievement_id: int
    earned_at: datetime
    created_at: datetime
    updated_at: datetime


class UserAchievementWithDetailsResponse(UserAchievementResponse):
    """Schema for user achievement with achievement details."""

    achievement: AchievementResponse


class AchievementProgressResponse(BaseModel):
    """Schema for achievement progress."""

    achievement: AchievementResponse
    current_progress: int
    required_value: int
    progress_percentage: float
    is_earned: bool
    earned_at: Optional[datetime] = None


# ====================
# Streak Schemas
# ====================
class StreakBase(BaseModel):
    """Base streak schema."""

    activity_type: str = Field(..., pattern="^(CHORES|PLANT_CARE|PET_CARE)$")
    current_streak_days: int = Field(0, ge=0)
    longest_streak_days: int = Field(0, ge=0)


class StreakCreate(StreakBase):
    """Schema for creating a streak."""

    user_id: int
    group_id: int


class StreakUpdate(BaseModel):
    """Schema for updating a streak."""

    current_streak_days: Optional[int] = Field(None, ge=0)
    longest_streak_days: Optional[int] = Field(None, ge=0)


class StreakResponse(StreakBase):
    """Schema for streak response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    group_id: int
    last_activity_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class StreakRecordActivityRequest(BaseModel):
    """Schema for recording activity to update streak."""

    activity_type: str = Field(..., pattern="^(CHORES|PLANT_CARE|PET_CARE)$")
    group_id: int


class StreakRecordActivityResponse(BaseModel):
    """Schema for streak record activity response."""

    streak: StreakResponse
    streak_extended: bool
    is_new_record: bool


# ====================
# Leaderboard Schemas
# ====================
class LeaderboardBase(BaseModel):
    """Base leaderboard schema."""

    period_type: str = Field(..., pattern="^(WEEKLY|MONTHLY|ALL_TIME)$")
    metric: str = Field(..., pattern="^(POINTS|CHORES_COMPLETED|EXPENSES_ADDED)$")
    period_start_date: datetime
    period_end_date: Optional[datetime] = None


class LeaderboardCreate(LeaderboardBase):
    """Schema for creating a leaderboard."""

    group_id: int


class LeaderboardResponse(LeaderboardBase):
    """Schema for leaderboard response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime


class LeaderboardEntryResponse(BaseModel):
    """Schema for leaderboard entry."""

    rank: int
    user_id: int
    user_name: str
    avatar_url: Optional[str] = None
    value: int  # Points, chores completed, etc.
    change_from_previous: Optional[int] = None  # Rank change


class LeaderboardWithEntriesResponse(LeaderboardResponse):
    """Schema for leaderboard with entries."""

    entries: list[LeaderboardEntryResponse]
    total_participants: int
    current_user_rank: Optional[int] = None


# ====================
# Aggregation/Summary Schemas
# ====================
class UserGamificationSummaryResponse(BaseModel):
    """Schema for user gamification summary."""

    user_id: int
    group_id: int
    total_points: int
    monthly_points: int
    rank_position: Optional[int] = None
    achievements_earned: int
    total_achievements: int
    active_streaks: list[StreakResponse]
    longest_streak_ever: int
    recent_achievements: list[UserAchievementWithDetailsResponse]


class GroupGamificationSummaryResponse(BaseModel):
    """Schema for group gamification summary."""

    group_id: int
    total_points_this_month: int
    most_active_user_id: Optional[int] = None
    most_active_user_points: int
    achievements_earned_this_month: int
    active_streaks_count: int
    leaderboard_leaders: dict[str, int]  # metric -> user_id


class PointsHistoryResponse(BaseModel):
    """Schema for points history."""

    user_id: int
    group_id: int
    history: list[dict]  # date, points_earned, reason
    total_earned: int
    period_start: datetime
    period_end: datetime


class AchievementUnlockedNotification(BaseModel):
    """Schema for achievement unlocked notification data."""

    user_id: int
    achievement: AchievementResponse
    earned_at: datetime
    message: str

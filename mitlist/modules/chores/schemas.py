"""Chores module Pydantic schemas for request/response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ====================
# Chore Schemas
# ====================
class ChoreBase(BaseModel):
    """Base chore schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    frequency_type: str = Field(..., pattern="^(DAILY|WEEKLY|MONTHLY|CUSTOM|SEASONAL)$")
    interval_value: int = Field(1, ge=1)
    effort_value: int = Field(..., ge=1, le=10)
    estimated_duration_minutes: int | None = Field(None, ge=1)
    category: str | None = Field(None, pattern="^(CLEANING|OUTDOOR|MAINTENANCE|ADMIN|OTHER)$")
    is_rotating: bool = False
    rotation_strategy: str | None = Field(None, pattern="^(ROUND_ROBIN|LEAST_BUSY|RANDOM)$")


class ChoreCreate(ChoreBase):
    """Schema for creating a chore."""

    group_id: int
    required_item_concept_id: int | None = None


class ChoreUpdate(BaseModel):
    """Schema for updating a chore."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    frequency_type: str | None = Field(None, pattern="^(DAILY|WEEKLY|MONTHLY|CUSTOM|SEASONAL)$")
    interval_value: int | None = Field(None, ge=1)
    effort_value: int | None = Field(None, ge=1, le=10)
    estimated_duration_minutes: int | None = Field(None, ge=1)
    category: str | None = Field(None, pattern="^(CLEANING|OUTDOOR|MAINTENANCE|ADMIN|OTHER)$")
    is_rotating: bool | None = None
    rotation_strategy: str | None = Field(None, pattern="^(ROUND_ROBIN|LEAST_BUSY|RANDOM)$")
    required_item_concept_id: int | None = None
    is_active: bool | None = None


class ChoreResponse(ChoreBase):
    """Schema for chore response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    required_item_concept_id: int | None = None
    last_assigned_to_id: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ====================
# ChoreAssignment Schemas
# ====================
class ChoreAssignmentBase(BaseModel):
    """Base chore assignment schema."""

    due_date: datetime
    notes: str | None = None


class ChoreAssignmentCreate(ChoreAssignmentBase):
    """Schema for creating a chore assignment."""

    chore_id: int
    assigned_to_id: int


class ChoreAssignmentUpdate(BaseModel):
    """Schema for updating a chore assignment."""

    due_date: datetime | None = None
    status: str | None = Field(None, pattern="^(PENDING|IN_PROGRESS|COMPLETED|SKIPPED)$")
    notes: str | None = None


class ChoreAssignmentStartRequest(BaseModel):
    """Schema for starting a chore assignment."""

    pass  # No input needed, just marks as in_progress


class ChoreAssignmentCompleteRequest(BaseModel):
    """Schema for completing a chore assignment."""

    actual_duration_minutes: int | None = Field(None, ge=1)
    notes: str | None = None


class ChoreAssignmentRateRequest(BaseModel):
    """Schema for rating a completed chore assignment."""

    quality_rating: int = Field(..., ge=1, le=5)


class ChoreAssignmentReassignRequest(BaseModel):
    """Schema for reassigning a chore to another member."""

    assigned_to_id: int


class ChoreAssignmentResponse(ChoreAssignmentBase):
    """Schema for chore assignment response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    chore_id: int
    assigned_to_id: int
    completed_at: datetime | None = None
    completed_by_id: int | None = None
    status: str
    started_at: datetime | None = None
    actual_duration_minutes: int | None = None
    quality_rating: int | None = None
    rated_by_id: int | None = None
    attachment_id: int | None = None
    created_at: datetime
    updated_at: datetime


class ChoreAssignmentWithChoreResponse(ChoreAssignmentResponse):
    """Schema for chore assignment with embedded chore details."""

    chore: ChoreResponse


# ====================
# ChoreDependency Schemas
# ====================
class ChoreDependencyBase(BaseModel):
    """Base chore dependency schema."""

    dependency_type: str = Field(..., pattern="^(BLOCKING|SUGGESTED)$")


class ChoreDependencyCreate(ChoreDependencyBase):
    """Schema for creating a chore dependency."""

    chore_id: int
    depends_on_chore_id: int


class ChoreDependencyResponse(ChoreDependencyBase):
    """Schema for chore dependency response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    chore_id: int
    depends_on_chore_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# ChoreTemplate Schemas
# ====================
class ChoreTemplateBase(BaseModel):
    """Base chore template schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    frequency_type: str = Field(..., pattern="^(DAILY|WEEKLY|MONTHLY|CUSTOM|SEASONAL)$")
    interval_value: int = Field(1, ge=1)
    effort_value: int = Field(..., ge=1, le=10)
    category: str | None = Field(None, pattern="^(CLEANING|OUTDOOR|MAINTENANCE|ADMIN|OTHER)$")
    is_public: bool = False


class ChoreTemplateCreate(ChoreTemplateBase):
    """Schema for creating a chore template."""

    pass


class ChoreTemplateUpdate(BaseModel):
    """Schema for updating a chore template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    frequency_type: str | None = Field(None, pattern="^(DAILY|WEEKLY|MONTHLY|CUSTOM|SEASONAL)$")
    interval_value: int | None = Field(None, ge=1)
    effort_value: int | None = Field(None, ge=1, le=10)
    category: str | None = Field(None, pattern="^(CLEANING|OUTDOOR|MAINTENANCE|ADMIN|OTHER)$")
    is_public: bool | None = None


class ChoreTemplateResponse(ChoreTemplateBase):
    """Schema for chore template response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    use_count: int
    created_at: datetime
    updated_at: datetime


class ChoreFromTemplateRequest(BaseModel):
    """Schema for creating a chore from a template."""

    template_id: int
    group_id: int
    # Override template defaults
    name: str | None = Field(None, min_length=1, max_length=255)
    frequency_type: str | None = Field(None, pattern="^(DAILY|WEEKLY|MONTHLY|CUSTOM|SEASONAL)$")
    interval_value: int | None = Field(None, ge=1)


# ====================
# Aggregation/Summary Schemas
# ====================
class ChoreStatisticsResponse(BaseModel):
    """Schema for chore statistics."""

    total_chores: int
    active_chores: int
    total_assignments: int
    completed_assignments: int
    pending_assignments: int
    overdue_assignments: int
    completion_rate: float
    average_completion_time_minutes: float | None = None


class UserChoreStatsResponse(BaseModel):
    """Schema for user chore statistics."""

    user_id: int
    total_assigned: int
    completed: int
    pending: int
    skipped: int
    total_effort_points: int
    average_quality_rating: float | None = None
    completion_rate: float


class ChoreLeaderboardResponse(BaseModel):
    """Schema for chore leaderboard."""

    group_id: int
    period_start: datetime
    period_end: datetime
    rankings: list[UserChoreStatsResponse]

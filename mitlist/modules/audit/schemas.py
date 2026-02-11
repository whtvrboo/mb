"""Audit module Pydantic schemas for request/response models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ====================
# AuditLog Schemas
# ====================
class AuditLogBase(BaseModel):
    """Base audit log schema."""

    action: str = Field(
        ...,
        pattern="^(CREATED|UPDATED|DELETED|VIEWED|APPROVED|REJECTED)$",
    )
    entity_type: str = Field(..., max_length=50)
    entity_id: int
    old_values: Optional[dict[str, Any]] = None
    new_values: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = Field(None, max_length=500)
    occurred_at: datetime


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log entry."""

    group_id: Optional[int] = None
    user_id: Optional[int] = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class AuditLogQueryRequest(BaseModel):
    """Schema for querying audit logs."""

    group_id: Optional[int] = None
    user_id: Optional[int] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    action: Optional[str] = Field(
        None,
        pattern="^(CREATED|UPDATED|DELETED|VIEWED|APPROVED|REJECTED)$",
    )
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class AuditLogListResponse(BaseModel):
    """Schema for audit log list response."""

    logs: list[AuditLogResponse]
    total_count: int
    has_more: bool


# ====================
# ReportSnapshot Schemas
# ====================
class ReportSnapshotBase(BaseModel):
    """Base report snapshot schema."""

    report_type: str = Field(
        ...,
        pattern="^(MONTHLY_EXPENSES|CHORE_COMPLETION|BUDGET_STATUS)$",
    )
    period_start_date: datetime
    period_end_date: datetime
    data_json: dict[str, Any]
    generated_at: datetime


class ReportSnapshotCreate(ReportSnapshotBase):
    """Schema for creating a report snapshot."""

    group_id: int


class ReportSnapshotResponse(ReportSnapshotBase):
    """Schema for report snapshot response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime


class GenerateReportRequest(BaseModel):
    """Schema for generating a report."""

    group_id: int
    report_type: str = Field(
        ...,
        pattern="^(MONTHLY_EXPENSES|CHORE_COMPLETION|BUDGET_STATUS)$",
    )
    period_start_date: datetime
    period_end_date: datetime


class ReportQueryRequest(BaseModel):
    """Schema for querying report snapshots."""

    group_id: int
    report_type: Optional[str] = Field(
        None,
        pattern="^(MONTHLY_EXPENSES|CHORE_COMPLETION|BUDGET_STATUS)$",
    )
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(10, ge=1, le=100)


# ====================
# Tag Schemas
# ====================
class TagBase(BaseModel):
    """Base tag schema."""

    name: str = Field(..., min_length=1, max_length=100)
    color_hex: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")


class TagCreate(TagBase):
    """Schema for creating a tag."""

    group_id: int


class TagUpdate(BaseModel):
    """Schema for updating a tag."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color_hex: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")


class TagResponse(TagBase):
    """Schema for tag response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# TagAssignment Schemas
# ====================
class TagAssignmentBase(BaseModel):
    """Base tag assignment schema."""

    entity_type: str = Field(..., max_length=50)
    entity_id: int


class TagAssignmentCreate(TagAssignmentBase):
    """Schema for creating a tag assignment."""

    tag_id: int


class TagAssignmentResponse(TagAssignmentBase):
    """Schema for tag assignment response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tag_id: int
    created_at: datetime
    updated_at: datetime


class TagAssignmentWithTagResponse(TagAssignmentResponse):
    """Schema for tag assignment with tag details."""

    tag: TagResponse


class BulkTagAssignmentRequest(BaseModel):
    """Schema for bulk tag assignment."""

    tag_ids: list[int] = Field(..., min_length=1)
    entity_type: str = Field(..., max_length=50)
    entity_id: int


class BulkTagAssignmentResponse(BaseModel):
    """Schema for bulk tag assignment response."""

    assigned: list[TagAssignmentResponse]
    already_assigned: list[int]  # Tag IDs that were already assigned


# ====================
# Aggregation/Summary Schemas
# ====================
class EntityTagsResponse(BaseModel):
    """Schema for tags on an entity."""

    entity_type: str
    entity_id: int
    tags: list[TagResponse]


class TagUsageResponse(BaseModel):
    """Schema for tag usage statistics."""

    tag: TagResponse
    usage_count: int
    entities_by_type: dict[str, int]  # entity_type -> count


class GroupTagsResponse(BaseModel):
    """Schema for all tags in a group."""

    group_id: int
    tags: list[TagUsageResponse]
    total_tags: int


class AuditSummaryResponse(BaseModel):
    """Schema for audit summary."""

    group_id: int
    total_logs: int
    logs_by_action: dict[str, int]
    logs_by_entity_type: dict[str, int]
    most_active_users: list[dict]  # user_id, action_count
    period_start: datetime
    period_end: datetime


class EntityHistoryResponse(BaseModel):
    """Schema for entity change history."""

    entity_type: str
    entity_id: int
    history: list[AuditLogResponse]
    total_changes: int
    created_by_user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_modified_by_user_id: Optional[int] = None
    last_modified_at: Optional[datetime] = None


class ReportComparisonRequest(BaseModel):
    """Schema for comparing two reports."""

    group_id: int
    report_type: str = Field(
        ...,
        pattern="^(MONTHLY_EXPENSES|CHORE_COMPLETION|BUDGET_STATUS)$",
    )
    period_1_start: datetime
    period_1_end: datetime
    period_2_start: datetime
    period_2_end: datetime


class ReportComparisonResponse(BaseModel):
    """Schema for report comparison response."""

    report_type: str
    period_1: ReportSnapshotResponse
    period_2: ReportSnapshotResponse
    differences: dict[str, Any]
    percentage_changes: dict[str, float]

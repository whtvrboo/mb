"""Audit & admin module FastAPI router."""


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import (
    get_current_group_id,
    get_current_user,
    get_db,
    require_group_admin,
    require_introspection_user,
)
from mitlist.core.errors import NotFoundError, ValidationError
from mitlist.modules.audit import schemas
from mitlist.modules.audit.interface import (
    assign_tag,
    broadcast_notification,
    create_tag,
    delete_tag,
    generate_report,
    get_entity_history,
    get_entity_tags,
    get_system_stats,
    get_tag_by_id,
    list_audit_logs,
    list_reports,
    list_tags,
    update_tag,
)
from mitlist.modules.auth.models import User

router = APIRouter(prefix="/admin", tags=["audit", "admin"])


@router.get("/system-stats")
async def get_admin_system_stats(
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get system-wide statistics."""
    stats = await get_system_stats(db)
    return stats


@router.post("/broadcast", status_code=status.HTTP_204_NO_CONTENT)
async def post_admin_broadcast(
    title: str,
    body: str,
    group_id: int = Depends(get_current_group_id),
    _user: User = Depends(require_introspection_user),
    _admin: int = Depends(require_group_admin),
    db: AsyncSession = Depends(get_db),
):
    """Broadcast a notification to all group members."""
    await broadcast_notification(db, group_id, title, body)


@router.get("/audit-trail", response_model=schemas.AuditLogListResponse)
async def get_admin_audit_trail(
    entity_type: str | None = None,
    entity_id: int | None = None,
    user_id: int | None = None,
    action: str | None = None,
    limit: int = 100,
    offset: int = 0,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Query audit logs for the group."""
    logs = await list_audit_logs(
        db,
        group_id=group_id,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        limit=limit,
        offset=offset,
    )
    return schemas.AuditLogListResponse(
        logs=logs,
        total_count=len(logs),
        has_more=len(logs) == limit,
    )


@router.get("/audit-trail/entity", response_model=schemas.EntityHistoryResponse)
async def get_entity_audit_history(
    entity_type: str,
    entity_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get audit history for a specific entity (scoped to current group)."""
    history = await get_entity_history(db, entity_type, entity_id, group_id=group_id)

    # Find created_by and last_modified_by
    created_by = None
    created_at = None
    last_modified_by = None
    last_modified_at = None

    for log in reversed(history):  # Oldest first
        if log.action == "CREATED":
            created_by = log.user_id
            created_at = log.occurred_at
        if log.action in ("CREATED", "UPDATED"):
            last_modified_by = log.user_id
            last_modified_at = log.occurred_at

    return schemas.EntityHistoryResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        history=history,
        total_changes=len(history),
        created_by_user_id=created_by,
        created_at=created_at,
        last_modified_by_user_id=last_modified_by,
        last_modified_at=last_modified_at,
    )


@router.post("/maintenance-mode")
async def post_admin_maintenance_mode(
    enabled: bool,
    message: str = "",
    _user: User = Depends(require_introspection_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle maintenance mode."""
    from mitlist.modules.audit.service import set_maintenance_mode

    result = set_maintenance_mode(enabled=enabled, message=message, enabled_by=_user.id)
    return result


@router.get("/maintenance-mode")
async def get_admin_maintenance_mode():
    """Get current maintenance mode status."""
    from mitlist.modules.audit.service import get_maintenance_mode

    return get_maintenance_mode()


# ---------- Reports ----------
@router.get("/reports", response_model=list[schemas.ReportSnapshotResponse])
async def get_reports(
    report_type: str | None = None,
    limit: int = 10,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """List generated reports."""
    reports = await list_reports(db, group_id, report_type=report_type, limit=limit)
    return reports


@router.post(
    "/reports/generate",
    response_model=schemas.ReportSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_generate_report(
    data: schemas.GenerateReportRequest,
    group_id: int = Depends(get_current_group_id),
    _admin: int = Depends(require_group_admin),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new report."""
    if data.group_id != group_id:
        raise ValidationError(
            code="GROUP_MISMATCH", detail="group_id in body must match current group"
        )
    report = await generate_report(
        db,
        group_id=data.group_id,
        report_type=data.report_type,
        period_start_date=data.period_start_date,
        period_end_date=data.period_end_date,
    )
    return report


# ---------- Tags ----------
@router.get("/tags", response_model=list[schemas.TagResponse])
async def get_tags(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """List group tags."""
    tags = await list_tags(db, group_id)
    return tags


@router.post("/tags", response_model=schemas.TagResponse, status_code=status.HTTP_201_CREATED)
async def post_tag(
    data: schemas.TagCreate,
    group_id: int = Depends(get_current_group_id),
    _admin: int = Depends(require_group_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tag."""
    if data.group_id != group_id:
        raise ValidationError(
            code="GROUP_MISMATCH", detail="group_id in body must match current group"
        )
    tag = await create_tag(db, data.group_id, data.name, data.color_hex)
    return tag


@router.patch("/tags/{tag_id}", response_model=schemas.TagResponse)
async def patch_tag(
    tag_id: int,
    data: schemas.TagUpdate,
    group_id: int = Depends(get_current_group_id),
    _admin: int = Depends(require_group_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a tag."""
    tag = await get_tag_by_id(db, tag_id)
    if not tag or tag.group_id != group_id:
        raise NotFoundError(code="TAG_NOT_FOUND", detail=f"Tag {tag_id} not found")
    tag = await update_tag(db, tag_id, name=data.name, color_hex=data.color_hex)
    return tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag_endpoint(
    tag_id: int,
    group_id: int = Depends(get_current_group_id),
    _admin: int = Depends(require_group_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a tag."""
    tag = await get_tag_by_id(db, tag_id)
    if not tag or tag.group_id != group_id:
        raise NotFoundError(code="TAG_NOT_FOUND", detail=f"Tag {tag_id} not found")
    await delete_tag(db, tag_id)


@router.post(
    "/tags/assign",
    response_model=schemas.TagAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_assign_tag(
    data: schemas.TagAssignmentCreate,
    group_id: int = Depends(get_current_group_id),
    _admin: int = Depends(require_group_admin),
    db: AsyncSession = Depends(get_db),
):
    """Assign a tag to an entity."""
    tag = await get_tag_by_id(db, data.tag_id)
    if not tag or tag.group_id != group_id:
        raise NotFoundError(code="TAG_NOT_FOUND", detail=f"Tag {data.tag_id} not found")
    assignment = await assign_tag(db, data.tag_id, data.entity_type, data.entity_id)
    return assignment


@router.get("/tags/entity", response_model=schemas.EntityTagsResponse)
async def get_entity_tags_endpoint(
    entity_type: str,
    entity_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get tags for an entity (only tags belonging to current group)."""
    tags = await get_entity_tags(db, entity_type, entity_id)
    tags = [t for t in tags if t.group_id == group_id]
    return schemas.EntityTagsResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        tags=tags,
    )

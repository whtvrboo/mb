"""Audit module service layer. PRIVATE - other modules import from interface.py."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.core.errors import NotFoundError
from mitlist.modules.audit.models import AuditLog, ReportSnapshot, Tag, TagAssignment


# ---------- Audit Logs ----------
async def log_action(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: int,
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    old_values: Optional[dict[str, Any]] = None,
    new_values: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Log an action in the audit trail."""
    log = AuditLog(
        group_id=group_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        occurred_at=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def list_audit_logs(
    db: AsyncSession,
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditLog]:
    """List audit logs with optional filters."""
    q = select(AuditLog)

    if group_id is not None:
        q = q.where(AuditLog.group_id == group_id)
    if user_id is not None:
        q = q.where(AuditLog.user_id == user_id)
    if entity_type is not None:
        q = q.where(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        q = q.where(AuditLog.entity_id == entity_id)
    if action is not None:
        q = q.where(AuditLog.action == action)
    if start_date is not None:
        q = q.where(AuditLog.occurred_at >= start_date)
    if end_date is not None:
        q = q.where(AuditLog.occurred_at <= end_date)

    q = q.order_by(AuditLog.occurred_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_entity_history(
    db: AsyncSession,
    entity_type: str,
    entity_id: int,
    group_id: Optional[int] = None,
    limit: int = 100,
) -> list[AuditLog]:
    """Get audit history for a specific entity, optionally scoped to a group."""
    q = (
        select(AuditLog)
        .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.occurred_at.desc())
        .limit(limit)
    )
    if group_id is not None:
        q = q.where(AuditLog.group_id == group_id)
    result = await db.execute(q)
    return list(result.scalars().all())


# ---------- Reports ----------
async def generate_report(
    db: AsyncSession,
    group_id: int,
    report_type: str,
    period_start_date: datetime,
    period_end_date: datetime,
) -> ReportSnapshot:
    """Generate a report snapshot."""
    # Build report data based on type
    data_json: dict[str, Any] = {}

    if report_type == "MONTHLY_EXPENSES":
        from mitlist.modules.finance.models import Expense

        result = await db.execute(
            select(
                func.count(Expense.id).label("count"),
                func.sum(Expense.amount).label("total"),
            ).where(
                Expense.group_id == group_id,
                Expense.expense_date >= period_start_date,
                Expense.expense_date <= period_end_date,
                Expense.deleted_at.is_(None),
            )
        )
        row = result.one()
        data_json = {
            "expense_count": row.count or 0,
            "total_amount": float(row.total or 0),
        }

    elif report_type == "CHORE_COMPLETION":
        from mitlist.modules.chores.models import ChoreAssignment

        result = await db.execute(
            select(
                func.count(ChoreAssignment.id).label("total"),
                func.sum(func.cast(ChoreAssignment.status == "COMPLETED", Integer)).label("completed"),  # noqa: F821
            ).where(
                ChoreAssignment.due_date >= period_start_date,
                ChoreAssignment.due_date <= period_end_date,
            )
        )
        row = result.one()
        completed = row.completed or 0
        total = row.total or 0
        completion_rate = (completed / total * 100) if total > 0 else 0
        data_json = {
            "total_assignments": total,
            "completed_assignments": completed,
            "completion_rate": completion_rate,
        }

    elif report_type == "BUDGET_STATUS":
        from mitlist.modules.finance.models import Budget, Expense

        budgets_result = await db.execute(
            select(Budget).where(Budget.group_id == group_id)
        )
        budgets = budgets_result.scalars().all()
        budget_data = []
        for budget in budgets:
            spent_result = await db.execute(
                select(func.sum(Expense.amount)).where(
                    Expense.group_id == group_id,
                    Expense.category_id == budget.category_id,
                    Expense.expense_date >= period_start_date,
                    Expense.expense_date <= period_end_date,
                    Expense.deleted_at.is_(None),
                )
            )
            spent = spent_result.scalar_one() or 0
            budget_data.append({
                "budget_id": budget.id,
                "category_id": budget.category_id,
                "limit": float(budget.amount_limit),
                "spent": float(spent),
                "remaining": float(budget.amount_limit - spent),
            })
        data_json = {"budgets": budget_data}

    report = ReportSnapshot(
        group_id=group_id,
        report_type=report_type,
        period_start_date=period_start_date,
        period_end_date=period_end_date,
        data_json=data_json,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return report


async def list_reports(
    db: AsyncSession,
    group_id: int,
    report_type: Optional[str] = None,
    limit: int = 10,
) -> list[ReportSnapshot]:
    """List report snapshots."""
    q = select(ReportSnapshot).where(ReportSnapshot.group_id == group_id)
    if report_type:
        q = q.where(ReportSnapshot.report_type == report_type)
    q = q.order_by(ReportSnapshot.generated_at.desc()).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_report_by_id(db: AsyncSession, report_id: int) -> Optional[ReportSnapshot]:
    """Get report by ID."""
    result = await db.execute(
        select(ReportSnapshot).where(ReportSnapshot.id == report_id)
    )
    return result.scalar_one_or_none()


# ---------- Tags ----------
async def list_tags(db: AsyncSession, group_id: int) -> list[Tag]:
    """List tags for a group."""
    result = await db.execute(
        select(Tag).where(Tag.group_id == group_id).order_by(Tag.name)
    )
    return list(result.scalars().all())


async def get_tag_by_id(db: AsyncSession, tag_id: int) -> Optional[Tag]:
    """Get tag by ID."""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalar_one_or_none()


async def create_tag(
    db: AsyncSession,
    group_id: int,
    name: str,
    color_hex: Optional[str] = None,
) -> Tag:
    """Create a new tag."""
    tag = Tag(
        group_id=group_id,
        name=name,
        color_hex=color_hex,
    )
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


async def update_tag(
    db: AsyncSession,
    tag_id: int,
    name: Optional[str] = None,
    color_hex: Optional[str] = None,
) -> Tag:
    """Update a tag."""
    tag = await get_tag_by_id(db, tag_id)
    if not tag:
        raise NotFoundError(code="TAG_NOT_FOUND", detail=f"Tag {tag_id} not found")

    if name is not None:
        tag.name = name
    if color_hex is not None:
        tag.color_hex = color_hex

    await db.flush()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, tag_id: int) -> None:
    """Delete a tag and its assignments."""
    tag = await get_tag_by_id(db, tag_id)
    if not tag:
        raise NotFoundError(code="TAG_NOT_FOUND", detail=f"Tag {tag_id} not found")

    # Delete assignments first
    await db.execute(delete(TagAssignment).where(TagAssignment.tag_id == tag_id))
    await db.delete(tag)
    await db.flush()


# ---------- Tag Assignments ----------
async def assign_tag(
    db: AsyncSession,
    tag_id: int,
    entity_type: str,
    entity_id: int,
) -> TagAssignment:
    """Assign a tag to an entity."""
    # Check if already assigned
    result = await db.execute(
        select(TagAssignment).where(
            TagAssignment.tag_id == tag_id,
            TagAssignment.entity_type == entity_type,
            TagAssignment.entity_id == entity_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    assignment = TagAssignment(
        tag_id=tag_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment


async def remove_tag_assignment(db: AsyncSession, assignment_id: int) -> None:
    """Remove a tag assignment."""
    result = await db.execute(
        select(TagAssignment).where(TagAssignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if assignment:
        await db.delete(assignment)
        await db.flush()


async def get_entity_tags(
    db: AsyncSession,
    entity_type: str,
    entity_id: int,
) -> list[Tag]:
    """Get all tags for an entity."""
    result = await db.execute(
        select(Tag)
        .join(TagAssignment, TagAssignment.tag_id == Tag.id)
        .where(
            TagAssignment.entity_type == entity_type,
            TagAssignment.entity_id == entity_id,
        )
    )
    return list(result.scalars().all())


# ---------- Maintenance Mode ----------
# In-memory state (in production, use Redis or a settings table)
_maintenance_state = {
    "enabled": False,
    "message": "",
    "enabled_at": None,
    "enabled_by": None,
}


def get_maintenance_mode() -> dict[str, Any]:
    """Get current maintenance mode status."""
    return _maintenance_state.copy()


def set_maintenance_mode(
    enabled: bool,
    message: str = "",
    enabled_by: Optional[int] = None,
) -> dict[str, Any]:
    """Toggle maintenance mode."""
    global _maintenance_state
    _maintenance_state = {
        "enabled": enabled,
        "message": message,
        "enabled_at": datetime.now(timezone.utc).isoformat() if enabled else None,
        "enabled_by": enabled_by,
    }
    return _maintenance_state.copy()


# ---------- Admin ----------
async def get_system_stats(db: AsyncSession) -> dict[str, Any]:
    """Get system-wide statistics."""
    from mitlist.modules.auth.models import Group, User

    users_result = await db.execute(select(func.count(User.id)))
    groups_result = await db.execute(select(func.count(Group.id)))

    return {
        "total_users": users_result.scalar_one() or 0,
        "total_groups": groups_result.scalar_one() or 0,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


async def broadcast_notification(
    db: AsyncSession,
    group_id: int,
    title: str,
    body: str,
) -> int:
    """Broadcast a notification to all group members. Returns count sent."""
    from mitlist.modules.auth.models import UserGroup
    from mitlist.modules.notifications.interface import create_notification

    result = await db.execute(
        select(UserGroup.user_id).where(UserGroup.group_id == group_id)
    )
    user_ids = result.scalars().all()

    count = 0
    for user_id in user_ids:
        await create_notification(
            db,
            user_id=user_id,
            type="BROADCAST",
            title=title,
            body=body,
            group_id=group_id,
            priority="HIGH",
        )
        count += 1

    return count

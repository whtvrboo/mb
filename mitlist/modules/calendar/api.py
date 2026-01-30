"""Calendar module FastAPI router."""

from datetime import date
from typing import Any, List as ListType

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_group_id, get_current_user, get_db
from mitlist.modules.auth.interface import require_member
from mitlist.modules.auth.models import User
from mitlist.modules.calendar import service

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/feed", response_model=ListType[dict[str, Any]])
async def get_calendar_feed(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: date | None = Query(None, description="Start date for calendar feed"),
    end_date: date | None = Query(None, description="End date for calendar feed"),
):
    """
    Unified calendar feed: bills, chore deadlines, meal plans, pet vaccines, birthdays, lease expiry.

    Returns a list of calendar events sorted by date.
    """
    await require_member(db, group_id, user.id)
    events = await service.get_calendar_feed(
        db,
        group_id,
        start_date=start_date,
        end_date=end_date,
    )
    return events

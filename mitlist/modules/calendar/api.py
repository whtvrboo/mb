"""Calendar module FastAPI router."""

from typing import Any, List as ListType

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError

router = APIRouter(prefix="/calendar", tags=["calendar"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/feed", response_model=ListType[dict[str, Any]])
async def get_calendar_feed(group_id: int, db: AsyncSession = Depends(get_db)):
    """Unified calendar feed: bills, chore deadlines, meal plans, pet vaccines, birthdays, lease expiry."""
    _stub("GET /calendar/feed is not yet implemented")

"""Notifications module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.notifications import schemas

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("", response_model=ListType[schemas.NotificationResponse])
async def get_notifications(db: AsyncSession = Depends(get_db)):
    _stub("GET /notifications is not yet implemented")


@router.post("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def post_notifications_clear(db: AsyncSession = Depends(get_db)):
    _stub("POST /notifications/clear is not yet implemented")


@router.patch("/{notification_id}/read", response_model=schemas.NotificationResponse)
async def patch_notification_read(notification_id: int, db: AsyncSession = Depends(get_db)):
    _stub("PATCH /notifications/{id}/read is not yet implemented")

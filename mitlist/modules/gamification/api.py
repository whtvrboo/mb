"""Gamification & Social module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.gamification import schemas
from mitlist.modules.notifications import schemas as notif_schemas

router = APIRouter(tags=["gamification", "social"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/leaderboard", response_model=schemas.LeaderboardWithEntriesResponse)
async def get_leaderboard(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /leaderboard is not yet implemented")


@router.get("/achievements", response_model=ListType[schemas.UserAchievementWithDetailsResponse])
async def get_achievements(db: AsyncSession = Depends(get_db)):
    _stub("GET /achievements is not yet implemented")


@router.post("/comments", response_model=notif_schemas.CommentResponse)
async def post_comments(data: notif_schemas.CommentCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /comments is not yet implemented")


@router.get("/comments", response_model=ListType[notif_schemas.CommentResponse])
async def get_comments(parent_type: str, parent_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /comments is not yet implemented")

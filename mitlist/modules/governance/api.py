"""Governance (voting) module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.governance import schemas

router = APIRouter(prefix="/proposals", tags=["governance"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("", response_model=ListType[schemas.ProposalResponse])
async def get_proposals(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /proposals is not yet implemented")


@router.post("", response_model=schemas.ProposalResponse, status_code=status.HTTP_201_CREATED)
async def post_proposals(data: schemas.ProposalCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /proposals is not yet implemented")


@router.get("/{proposal_id}/options", response_model=ListType[schemas.BallotOptionResponse])
async def get_proposal_options(proposal_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /proposals/{id}/options is not yet implemented")


@router.post("/{proposal_id}/vote", response_model=schemas.VoteResponse)
async def post_proposal_vote(proposal_id: int, data: schemas.VoteCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /proposals/{id}/vote is not yet implemented")


@router.post("/{proposal_id}/close", response_model=schemas.ProposalResponse)
async def post_proposal_close(proposal_id: int, db: AsyncSession = Depends(get_db)):
    _stub("POST /proposals/{id}/close is not yet implemented")

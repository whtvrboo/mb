"""Governance (voting) module FastAPI router."""


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_group_id, get_current_user, get_db
from mitlist.core.errors import NotFoundError
from mitlist.modules.auth.interface import require_member
from mitlist.modules.auth.models import User
from mitlist.modules.governance import schemas
from mitlist.modules.governance.interface import (
    cancel_proposal,
    cast_ranked_votes,
    cast_vote,
    close_proposal,
    create_proposal,
    execute_proposal,
    get_proposal_by_id,
    get_user_vote,
    list_proposals,
    open_proposal,
    update_proposal,
)

router = APIRouter(prefix="/proposals", tags=["governance"])


@router.get("", response_model=list[schemas.ProposalResponse])
async def get_proposals(
    status_filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """List proposals for the current group."""
    proposals = await list_proposals(
        db, group_id, status_filter=status_filter, limit=limit, offset=offset
    )
    return proposals


@router.post("", response_model=schemas.ProposalResponse, status_code=status.HTTP_201_CREATED)
async def post_proposals(
    data: schemas.ProposalCreate,
    user: User = Depends(get_current_user),
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new proposal."""
    ballot_options = [
        {
            "text": opt.text,
            "display_order": opt.display_order,
            "option_metadata": opt.option_metadata,
        }
        for opt in data.ballot_options
    ]
    proposal = await create_proposal(
        db=db,
        group_id=group_id,
        created_by_id=user.id,
        title=data.title,
        type=data.type,
        strategy=data.strategy,
        description=data.description,
        deadline_at=data.deadline_at,
        min_quorum_percentage=data.min_quorum_percentage,
        ballot_options=ballot_options,
        linked_expense_id=data.linked_expense_id,
        linked_chore_id=data.linked_chore_id,
        linked_pet_id=data.linked_pet_id,
    )
    return proposal


@router.get("/{proposal_id}", response_model=schemas.ProposalResponse)
async def get_proposal(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a proposal by ID with ballot options and vote counts."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")
    await require_member(db, proposal.group_id, user.id)
    return proposal


@router.patch("/{proposal_id}", response_model=schemas.ProposalResponse)
async def patch_proposal(
    proposal_id: int,
    data: schemas.ProposalUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a draft proposal."""
    proposal = await update_proposal(
        db=db,
        proposal_id=proposal_id,
        user_id=user.id,
        title=data.title,
        description=data.description,
        deadline_at=data.deadline_at,
        min_quorum_percentage=data.min_quorum_percentage,
    )
    return proposal


@router.delete("/{proposal_id}", response_model=schemas.ProposalResponse)
async def delete_proposal(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a proposal."""
    proposal = await cancel_proposal(db, proposal_id, user.id)
    return proposal


@router.post("/{proposal_id}/open", response_model=schemas.ProposalResponse)
async def post_proposal_open(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Open a proposal for voting (change status from DRAFT to OPEN)."""
    proposal = await open_proposal(db, proposal_id, user.id)
    return proposal


@router.get("/{proposal_id}/options", response_model=list[schemas.BallotOptionResponse])
async def get_proposal_options(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ballot options for a proposal."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")
    await require_member(db, proposal.group_id, user.id)
    return proposal.ballot_options


@router.post("/{proposal_id}/vote", response_model=schemas.VoteResponse)
async def post_proposal_vote(
    proposal_id: int,
    data: schemas.VoteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cast a vote for a proposal."""
    vote = await cast_vote(
        db=db,
        proposal_id=proposal_id,
        user_id=user.id,
        ballot_option_id=data.ballot_option_id,
        weight=data.weight,
        is_anonymous=data.is_anonymous,
    )
    return vote


@router.post("/{proposal_id}/vote/ranked", response_model=list[schemas.VoteResponse])
async def post_proposal_vote_ranked(
    proposal_id: int,
    data: schemas.RankedVoteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cast ranked choice votes for a proposal."""
    ranked_choices = [
        {"ballot_option_id": choice.ballot_option_id, "rank": choice.rank}
        for choice in data.ranked_choices
    ]
    votes = await cast_ranked_votes(
        db=db,
        proposal_id=proposal_id,
        user_id=user.id,
        ranked_choices=ranked_choices,
        is_anonymous=data.is_anonymous,
    )
    return votes


@router.get("/{proposal_id}/vote/me", response_model=schemas.VoteResponse | None)
async def get_proposal_vote_me(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's vote for a proposal."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")
    await require_member(db, proposal.group_id, user.id)
    vote = await get_user_vote(db, proposal_id, user.id)
    return vote


@router.post("/{proposal_id}/close", response_model=schemas.ProposalResponse)
async def post_proposal_close(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Close a proposal and tally votes."""
    proposal = await close_proposal(db, proposal_id, user.id)
    return proposal


@router.post("/{proposal_id}/execute", response_model=schemas.ProposalResponse)
async def post_proposal_execute(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a passed proposal."""
    proposal = await execute_proposal(db, proposal_id, user.id)
    return proposal


@router.get("/{proposal_id}/results", response_model=schemas.ProposalResultResponse)
async def get_proposal_results(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get voting results summary for a proposal."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")
    await require_member(db, proposal.group_id, user.id)

    # Get vote counts per option
    from sqlalchemy import func, select

    from mitlist.modules.governance.models import BallotOption, VoteRecord

    result = await db.execute(
        select(
            BallotOption.id,
            BallotOption.text,
            func.count(VoteRecord.id).label("vote_count"),
        )
        .outerjoin(VoteRecord, VoteRecord.ballot_option_id == BallotOption.id)
        .where(BallotOption.proposal_id == proposal_id)
        .group_by(BallotOption.id, BallotOption.text)
        .order_by(func.count(VoteRecord.id).desc())
    )
    option_results = result.all()

    total_votes = sum(count for _, _, count in option_results)
    results = []
    for option_id, option_text, vote_count in option_results:
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0.0
        results.append(
            {
                "option_id": option_id,
                "option_text": option_text,
                "vote_count": vote_count,
                "percentage": round(percentage, 2),
            }
        )

    # Check quorum
    from mitlist.modules.auth.models import UserGroup

    group_size_result = await db.execute(
        select(func.count(UserGroup.user_id)).where(UserGroup.group_id == proposal.group_id)
    )
    group_size = group_size_result.scalar_one() or 1
    quorum_reached = True
    required_quorum = None
    if proposal.min_quorum_percentage:
        required_quorum = int(group_size * proposal.min_quorum_percentage / 100)
        quorum_reached = total_votes >= required_quorum

    execution_result = proposal.execution_result or {}
    winner_option_id = execution_result.get("winner_option_id")
    winner_option_text = execution_result.get("winner_option_text")

    return schemas.ProposalResultResponse(
        proposal_id=proposal_id,
        status=proposal.status,
        total_votes=total_votes,
        quorum_reached=quorum_reached,
        required_quorum=required_quorum,
        results=results,
        winner_option_id=winner_option_id,
        winner_option_text=winner_option_text,
    )

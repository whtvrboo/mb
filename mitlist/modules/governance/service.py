"""Governance module service layer. PRIVATE - other modules import from interface.py."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from mitlist.modules.auth.interface import require_member
from mitlist.modules.governance.models import (
    BallotOption,
    Proposal,
    ProposalStatus,
    ProposalType,
    VoteDelegation,
    VoteRecord,
    VotingStrategy,
)


async def list_proposals(
    db: AsyncSession,
    group_id: int,
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Proposal]:
    """List proposals for a group, optionally filtered by status."""
    q = (
        select(Proposal)
        .where(Proposal.group_id == group_id)
        .options(selectinload(Proposal.ballot_options))
        .order_by(Proposal.created_at.desc())
    )
    if status_filter:
        q = q.where(Proposal.status == status_filter)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_proposal_by_id(db: AsyncSession, proposal_id: int) -> Optional[Proposal]:
    """Get proposal by ID with ballot options and votes loaded."""
    result = await db.execute(
        select(Proposal)
        .where(Proposal.id == proposal_id)
        .options(selectinload(Proposal.ballot_options), selectinload(Proposal.votes))
    )
    return result.scalar_one_or_none()


async def create_proposal(
    db: AsyncSession,
    group_id: int,
    created_by_id: int,
    title: str,
    type: str,
    strategy: str,
    description: Optional[str] = None,
    deadline_at: Optional[datetime] = None,
    min_quorum_percentage: Optional[int] = None,
    ballot_options: Optional[list[dict]] = None,
    linked_expense_id: Optional[int] = None,
    linked_chore_id: Optional[int] = None,
    linked_pet_id: Optional[int] = None,
) -> Proposal:
    """Create a new proposal with ballot options."""
    # Ensure user is a group member
    await require_member(db, group_id, created_by_id)

    # Validate ballot options
    if not ballot_options or len(ballot_options) < 2:
        raise ValidationError(
            code="INSUFFICIENT_OPTIONS", detail="Proposal must have at least 2 ballot options"
        )

    proposal = Proposal(
        group_id=group_id,
        created_by_id=created_by_id,
        title=title,
        description=description,
        type=type,
        strategy=strategy,
        status=ProposalStatus.DRAFT,
        deadline_at=deadline_at,
        min_quorum_percentage=min_quorum_percentage,
        linked_expense_id=linked_expense_id,
        linked_chore_id=linked_chore_id,
        linked_pet_id=linked_pet_id,
    )
    db.add(proposal)
    await db.flush()
    await db.refresh(proposal)

    # Create ballot options
    for idx, opt in enumerate(ballot_options):
        ballot_option = BallotOption(
            proposal_id=proposal.id,
            text=opt["text"],
            display_order=opt.get("display_order", idx),
            option_metadata=opt.get("option_metadata"),
        )
        db.add(ballot_option)

    await db.flush()
    # Re-load with ballot_options for async-safe serialization (no lazy load)
    result = await db.execute(
        select(Proposal)
        .where(Proposal.id == proposal.id)
        .options(selectinload(Proposal.ballot_options))
    )
    return result.scalar_one()


async def update_proposal(
    db: AsyncSession,
    proposal_id: int,
    user_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    deadline_at: Optional[datetime] = None,
    min_quorum_percentage: Optional[int] = None,
) -> Proposal:
    """Update a proposal (only allowed for DRAFT status)."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")

    # Only creator can update, and only when DRAFT
    if proposal.created_by_id != user_id:
        raise ForbiddenError(code="NOT_CREATOR", detail="Only the proposal creator can update it")

    if proposal.status != ProposalStatus.DRAFT:
        raise ConflictError(
            code="PROPOSAL_NOT_DRAFT",
            detail=f"Cannot update proposal with status {proposal.status}",
        )

    if title is not None:
        proposal.title = title
    if description is not None:
        proposal.description = description
    if deadline_at is not None:
        proposal.deadline_at = deadline_at
    if min_quorum_percentage is not None:
        proposal.min_quorum_percentage = min_quorum_percentage

    await db.flush()
    await db.refresh(proposal)
    return proposal


async def open_proposal(db: AsyncSession, proposal_id: int, user_id: int) -> Proposal:
    """Open a proposal for voting (change status from DRAFT to OPEN)."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")

    if proposal.created_by_id != user_id:
        raise ForbiddenError(code="NOT_CREATOR", detail="Only the proposal creator can open it")

    if proposal.status != ProposalStatus.DRAFT:
        raise ConflictError(
            code="PROPOSAL_NOT_DRAFT",
            detail=f"Cannot open proposal with status {proposal.status}",
        )

    if not proposal.ballot_options or len(proposal.ballot_options) < 2:
        raise ValidationError(
            code="INSUFFICIENT_OPTIONS", detail="Proposal must have at least 2 ballot options"
        )

    proposal.status = ProposalStatus.OPEN
    await db.flush()
    await db.refresh(proposal)
    return proposal


async def cancel_proposal(db: AsyncSession, proposal_id: int, user_id: int) -> Proposal:
    """Cancel a proposal (set status to CANCELLED)."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")

    # Creator or admin can cancel
    await require_member(db, proposal.group_id, user_id)
    if proposal.created_by_id != user_id:
        from mitlist.modules.auth.interface import require_admin

        await require_admin(db, proposal.group_id, user_id)

    if proposal.status in (ProposalStatus.PASSED, ProposalStatus.EXECUTED):
        raise ConflictError(
            code="PROPOSAL_ALREADY_PASSED",
            detail="Cannot cancel a proposal that has already passed",
        )

    proposal.status = ProposalStatus.CANCELLED
    await db.flush()
    await db.refresh(proposal)
    return proposal


async def get_user_vote(db: AsyncSession, proposal_id: int, user_id: int) -> Optional[VoteRecord]:
    """Get a user's vote for a proposal."""
    result = await db.execute(
        select(VoteRecord).where(VoteRecord.proposal_id == proposal_id, VoteRecord.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def cast_vote(
    db: AsyncSession,
    proposal_id: int,
    user_id: int,
    ballot_option_id: int,
    weight: int = 1,
    is_anonymous: bool = False,
) -> VoteRecord:
    """Cast a vote for a proposal."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")

    if proposal.status != ProposalStatus.OPEN:
        raise ConflictError(
            code="PROPOSAL_NOT_OPEN", detail=f"Cannot vote on proposal with status {proposal.status}"
        )

    # Check deadline
    if proposal.deadline_at and proposal.deadline_at < datetime.now(timezone.utc):
        raise ConflictError(code="PROPOSAL_EXPIRED", detail="Proposal deadline has passed")

    # Ensure user is a group member
    await require_member(db, proposal.group_id, user_id)

    # Validate ballot option belongs to this proposal
    result = await db.execute(
        select(BallotOption).where(
            BallotOption.id == ballot_option_id, BallotOption.proposal_id == proposal_id
        )
    )
    ballot_option = result.scalar_one_or_none()
    if not ballot_option:
        raise NotFoundError(
            code="BALLOT_OPTION_NOT_FOUND",
            detail=f"Ballot option {ballot_option_id} not found for this proposal",
        )

    # Check for existing vote
    existing_vote = await get_user_vote(db, proposal_id, user_id)
    if existing_vote:
        # Update existing vote
        existing_vote.ballot_option_id = ballot_option_id
        existing_vote.weight = weight
        existing_vote.is_anonymous = is_anonymous
        existing_vote.voted_at = datetime.now(timezone.utc)

        # Update vote counts
        old_option_result = await db.execute(
            select(BallotOption).where(BallotOption.id == existing_vote.ballot_option_id)
        )
        old_option = old_option_result.scalar_one_or_none()
        if old_option and old_option.id != ballot_option_id:
            old_option.vote_count = max(0, old_option.vote_count - existing_vote.weight)
            ballot_option.vote_count += weight
        elif old_option and old_option.id == ballot_option_id:
            # Same option, just update weight difference
            weight_diff = weight - existing_vote.weight
            ballot_option.vote_count += weight_diff

        await db.flush()
        await db.refresh(existing_vote)
        return existing_vote

    # Create new vote
    vote = VoteRecord(
        proposal_id=proposal_id,
        user_id=user_id,
        ballot_option_id=ballot_option_id,
        weight=weight,
        is_anonymous=is_anonymous,
        voted_at=datetime.now(timezone.utc),
    )
    db.add(vote)

    # Update vote count
    ballot_option.vote_count += weight

    await db.flush()
    await db.refresh(vote)
    return vote


async def cast_ranked_votes(
    db: AsyncSession,
    proposal_id: int,
    user_id: int,
    ranked_choices: list[dict],
    is_anonymous: bool = False,
) -> list[VoteRecord]:
    """Cast ranked choice votes for a proposal."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")

    if proposal.strategy != VotingStrategy.RANKED_CHOICE:
        raise ValidationError(
            code="INVALID_STRATEGY",
            detail="Ranked choice voting only available for RANKED_CHOICE strategy",
        )

    if proposal.status != ProposalStatus.OPEN:
        raise ConflictError(
            code="PROPOSAL_NOT_OPEN", detail=f"Cannot vote on proposal with status {proposal.status}"
        )

    if proposal.deadline_at and proposal.deadline_at < datetime.now(timezone.utc):
        raise ConflictError(code="PROPOSAL_EXPIRED", detail="Proposal deadline has passed")

    await require_member(db, proposal.group_id, user_id)

    # Validate all ballot options belong to this proposal
    ballot_option_ids = {opt["ballot_option_id"] for opt in ranked_choices}
    result = await db.execute(
        select(BallotOption).where(
            BallotOption.id.in_(ballot_option_ids), BallotOption.proposal_id == proposal_id
        )
    )
    found_options = {opt.id for opt in result.scalars().all()}
    if found_options != ballot_option_ids:
        raise ValidationError(
            code="INVALID_BALLOT_OPTIONS",
            detail="Some ballot options do not belong to this proposal",
        )

    # Check for existing votes and delete them
    existing_votes_result = await db.execute(
        select(VoteRecord).where(VoteRecord.proposal_id == proposal_id, VoteRecord.user_id == user_id)
    )
    existing_votes = existing_votes_result.scalars().all()
    for vote in existing_votes:
        # Decrement vote count
        opt_result = await db.execute(
            select(BallotOption).where(BallotOption.id == vote.ballot_option_id)
        )
        opt = opt_result.scalar_one_or_none()
        if opt:
            opt.vote_count = max(0, opt.vote_count - vote.weight)
        await db.delete(vote)

    # Create new ranked votes
    votes = []
    for choice in ranked_choices:
        vote = VoteRecord(
            proposal_id=proposal_id,
            user_id=user_id,
            ballot_option_id=choice["ballot_option_id"],
            rank_order=choice.get("rank"),
            weight=1,  # Ranked choice uses weight=1
            is_anonymous=is_anonymous,
            voted_at=datetime.now(timezone.utc),
        )
        db.add(vote)
        votes.append(vote)

        # Update vote count (for first choice only in ranked choice)
        if choice.get("rank") == 1:
            opt_result = await db.execute(
                select(BallotOption).where(BallotOption.id == choice["ballot_option_id"])
            )
            opt = opt_result.scalar_one_or_none()
            if opt:
                opt.vote_count += 1

    await db.flush()
    for vote in votes:
        await db.refresh(vote)
    return votes


async def _tally_simple_majority(
    db: AsyncSession, proposal: Proposal, total_votes: int, group_size: int
) -> tuple[Optional[int], str]:
    """Tally votes for SIMPLE_MAJORITY strategy."""
    if total_votes == 0:
        return None, "REJECTED"

    # Get vote counts per option
    result = await db.execute(
        select(BallotOption.id, BallotOption.vote_count)
        .where(BallotOption.proposal_id == proposal.id)
        .order_by(BallotOption.vote_count.desc())
    )
    option_counts = result.all()

    if not option_counts:
        return None, "REJECTED"

    winner_id, winner_count = option_counts[0]

    # Check if winner has >50% of votes
    if winner_count > total_votes / 2:
        return winner_id, "PASSED"
    return None, "REJECTED"


async def _tally_unanimous(
    db: AsyncSession, proposal: Proposal, total_votes: int, group_size: int
) -> tuple[Optional[int], str]:
    """Tally votes for UNANIMOUS strategy."""
    if total_votes == 0:
        return None, "REJECTED"

    # Get vote counts per option
    result = await db.execute(
        select(BallotOption.id, BallotOption.vote_count)
        .where(BallotOption.proposal_id == proposal.id)
        .order_by(BallotOption.vote_count.desc())
    )
    option_counts = result.all()

    if not option_counts:
        return None, "REJECTED"

    winner_id, winner_count = option_counts[0]

    # All votes must be for the same option
    if winner_count == total_votes and len(option_counts) == 1:
        return winner_id, "PASSED"
    return None, "REJECTED"


async def _tally_ranked_choice(
    db: AsyncSession, proposal: Proposal, total_votes: int, group_size: int
) -> tuple[Optional[int], str]:
    """Tally votes for RANKED_CHOICE strategy using instant-runoff."""
    if total_votes == 0:
        return None, "REJECTED"

    # Get all votes with rankings
    votes_result = await db.execute(
        select(VoteRecord)
        .where(VoteRecord.proposal_id == proposal.id)
        .order_by(VoteRecord.user_id, VoteRecord.rank_order)
    )
    all_votes = votes_result.scalars().all()

    # Group votes by user
    user_votes: dict[int, list[VoteRecord]] = {}
    for vote in all_votes:
        if vote.user_id not in user_votes:
            user_votes[vote.user_id] = []
        user_votes[vote.user_id].append(vote)

    # Get all ballot options
    options_result = await db.execute(
        select(BallotOption).where(BallotOption.proposal_id == proposal.id)
    )
    all_options = {opt.id for opt in options_result.scalars().all()}
    eliminated = set()

    # Instant-runoff elimination rounds
    while len(all_options - eliminated) > 1:
        # Count first-choice votes
        first_choice_counts: dict[int, int] = {}
        for user_id, votes in user_votes.items():
            # Find first non-eliminated choice
            sorted_votes = sorted(votes, key=lambda v: v.rank_order or 999)
            for vote in sorted_votes:
                if vote.ballot_option_id not in eliminated:
                    first_choice_counts[vote.ballot_option_id] = (
                        first_choice_counts.get(vote.ballot_option_id, 0) + 1
                    )
                    break

        if not first_choice_counts:
            return None, "REJECTED"

        # Check for majority
        total_first_choice = sum(first_choice_counts.values())
        for option_id, count in first_choice_counts.items():
            if count > total_first_choice / 2:
                return option_id, "PASSED"

        # Eliminate option with fewest votes
        min_count = min(first_choice_counts.values())
        for option_id, count in first_choice_counts.items():
            if count == min_count:
                eliminated.add(option_id)
                break

    # Final two options
    remaining = all_options - eliminated
    if len(remaining) == 1:
        return remaining.pop(), "PASSED"
    return None, "REJECTED"


async def _tally_weighted(
    db: AsyncSession, proposal: Proposal, total_votes: int, group_size: int
) -> tuple[Optional[int], str]:
    """Tally votes for WEIGHTED strategy."""
    if total_votes == 0:
        return None, "REJECTED"

    # Sum weighted votes per option
    result = await db.execute(
        select(BallotOption.id, func.sum(VoteRecord.weight).label("total_weight"))
        .join(VoteRecord, VoteRecord.ballot_option_id == BallotOption.id)
        .where(BallotOption.proposal_id == proposal.id)
        .group_by(BallotOption.id)
        .order_by(func.sum(VoteRecord.weight).desc())
    )
    weighted_counts = result.all()

    if not weighted_counts:
        return None, "REJECTED"

    winner_id, winner_weight = weighted_counts[0]

    # Check if winner has >50% of weighted votes
    total_weight = sum(weight for _, weight in weighted_counts)
    if winner_weight > total_weight / 2:
        return winner_id, "PASSED"
    return None, "REJECTED"


async def close_proposal(db: AsyncSession, proposal_id: int, closed_by_id: int) -> Proposal:
    """Close a proposal and tally votes."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")

    if proposal.status != ProposalStatus.OPEN:
        raise ConflictError(
            code="PROPOSAL_NOT_OPEN",
            detail=f"Cannot close proposal with status {proposal.status}",
        )

    # Ensure user is a group member (and ideally admin or creator)
    await require_member(db, proposal.group_id, closed_by_id)

    # Get group size for quorum calculation
    from mitlist.modules.auth.models import UserGroup

    group_size_result = await db.execute(
        select(func.count(UserGroup.user_id)).where(UserGroup.group_id == proposal.group_id)
    )
    group_size = group_size_result.scalar_one() or 1

    # Get total votes cast
    votes_result = await db.execute(
        select(func.count(VoteRecord.id)).where(VoteRecord.proposal_id == proposal.id)
    )
    total_votes = votes_result.scalar_one() or 0

    # Check quorum
    quorum_met = True
    if proposal.min_quorum_percentage:
        required_votes = int(group_size * proposal.min_quorum_percentage / 100)
        quorum_met = total_votes >= required_votes

    # Tally votes based on strategy
    winner_option_id = None
    final_status = ProposalStatus.REJECTED

    if quorum_met:
        if proposal.strategy == VotingStrategy.SIMPLE_MAJORITY:
            winner_option_id, status_str = await _tally_simple_majority(
                db, proposal, total_votes, group_size
            )
            final_status = ProposalStatus(status_str)
        elif proposal.strategy == VotingStrategy.UNANIMOUS:
            winner_option_id, status_str = await _tally_unanimous(
                db, proposal, total_votes, group_size
            )
            final_status = ProposalStatus(status_str)
        elif proposal.strategy == VotingStrategy.RANKED_CHOICE:
            winner_option_id, status_str = await _tally_ranked_choice(
                db, proposal, total_votes, group_size
            )
            final_status = ProposalStatus(status_str)
        elif proposal.strategy == VotingStrategy.WEIGHTED:
            winner_option_id, status_str = await _tally_weighted(db, proposal, total_votes, group_size)
            final_status = ProposalStatus(status_str)

    # Get winner option text
    winner_option_text = None
    if winner_option_id:
        opt_result = await db.execute(
            select(BallotOption).where(BallotOption.id == winner_option_id)
        )
        winner_option = opt_result.scalar_one_or_none()
        if winner_option:
            winner_option_text = winner_option.text

    # Update proposal status
    proposal.status = final_status
    proposal.execution_result = {
        "winner_option_id": winner_option_id,
        "winner_option_text": winner_option_text,
        "total_votes": total_votes,
        "quorum_met": quorum_met,
        "group_size": group_size,
    }

    await db.flush()
    await db.refresh(proposal)
    return proposal


async def execute_proposal(db: AsyncSession, proposal_id: int, executed_by_id: int) -> Proposal:
    """Execute a passed proposal (create linked resources)."""
    proposal = await get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise NotFoundError(code="PROPOSAL_NOT_FOUND", detail=f"Proposal {proposal_id} not found")

    if proposal.status != ProposalStatus.PASSED:
        raise ConflictError(
            code="PROPOSAL_NOT_PASSED",
            detail=f"Cannot execute proposal with status {proposal.status}",
        )

    if proposal.executed_at:
        raise ConflictError(code="ALREADY_EXECUTED", detail="Proposal has already been executed")

    await require_member(db, proposal.group_id, executed_by_id)

    execution_result = proposal.execution_result or {}
    winner_option_id = execution_result.get("winner_option_id")

    if not winner_option_id:
        raise ValidationError(code="NO_WINNER", detail="Proposal has no winning option")

    # Execute based on proposal type
    if proposal.type == ProposalType.EXPENSE_REQUEST:
        # For expense requests, mark the linked expense as approved/executed
        if proposal.linked_expense_id:
            from mitlist.modules.finance.models import Expense
            expense_result = await db.execute(
                select(Expense).where(Expense.id == proposal.linked_expense_id)
            )
            expense = expense_result.scalar_one_or_none()
            if expense:
                expense.is_approved = True
                execution_result["expense_approved"] = True
    elif proposal.type == ProposalType.CHORE_ASSIGNMENT:
        # For chore assignments, mark the assignment as approved
        if proposal.linked_chore_id:
            from mitlist.modules.chores.models import ChoreAssignment
            assignment_result = await db.execute(
                select(ChoreAssignment).where(ChoreAssignment.chore_id == proposal.linked_chore_id)
                .order_by(ChoreAssignment.created_at.desc())
                .limit(1)
            )
            assignment = assignment_result.scalar_one_or_none()
            if assignment:
                assignment.status = "APPROVED"
                execution_result["chore_assignment_approved"] = True
    elif proposal.type == ProposalType.KICK_USER:
        # Extract user_id from winner option metadata
        winner_opt_result = await db.execute(
            select(BallotOption).where(BallotOption.id == winner_option_id)
        )
        winner_opt = winner_opt_result.scalar_one_or_none()
        if winner_opt and winner_opt.option_metadata and "user_id" in winner_opt.option_metadata:
            user_to_kick = winner_opt.option_metadata["user_id"]
            from mitlist.modules.auth.interface import remove_member
            await remove_member(db, proposal.group_id, user_to_kick)
            execution_result["user_kicked"] = user_to_kick

    # Update the execution result with any new data
    proposal.execution_result = execution_result
    proposal.executed_at = datetime.now(timezone.utc)
    proposal.status = ProposalStatus.EXECUTED

    await db.flush()
    await db.refresh(proposal)
    return proposal

"""Governance module Pydantic schemas for request/response models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ====================
# Proposal Schemas
# ====================
class BallotOptionInput(BaseModel):
    """Input schema for ballot option when creating a proposal."""

    text: str = Field(..., min_length=1, max_length=500)
    display_order: int = Field(0, ge=0)
    option_metadata: Optional[dict[str, Any]] = None


class ProposalBase(BaseModel):
    """Base proposal schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = Field(
        ...,
        pattern="^(GENERAL|EXPENSE_REQUEST|POLICY_CHANGE|KICK_USER|CHORE_ASSIGNMENT|PET_ADOPTION)$",
    )
    strategy: str = Field(..., pattern="^(SIMPLE_MAJORITY|UNANIMOUS|RANKED_CHOICE|WEIGHTED)$")
    deadline_at: Optional[datetime] = None
    min_quorum_percentage: Optional[int] = Field(None, ge=0, le=100)


class ProposalCreate(ProposalBase):
    """Schema for creating a proposal."""

    group_id: int
    ballot_options: list[BallotOptionInput] = Field(default_factory=list)
    linked_expense_id: Optional[int] = None
    linked_chore_id: Optional[int] = None
    linked_pet_id: Optional[int] = None


class ProposalUpdate(BaseModel):
    """Schema for updating a proposal."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    deadline_at: Optional[datetime] = None
    min_quorum_percentage: Optional[int] = Field(None, ge=0, le=100)


class ProposalStatusUpdate(BaseModel):
    """Schema for updating proposal status."""

    status: str = Field(..., pattern="^(DRAFT|OPEN|PASSED|REJECTED|EXECUTED|CANCELLED)$")


class BallotOptionResponse(BaseModel):
    """Schema for ballot option response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    text: str
    display_order: int
    option_metadata: Optional[dict[str, Any]] = None
    vote_count: int
    created_at: datetime
    updated_at: datetime


class ProposalResponse(ProposalBase):
    """Schema for proposal response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_by_id: int
    status: str
    linked_expense_id: Optional[int] = None
    linked_chore_id: Optional[int] = None
    linked_pet_id: Optional[int] = None
    execution_result: Optional[dict[str, Any]] = None
    executed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    ballot_options: list[BallotOptionResponse] = Field(default_factory=list)


# ====================
# VoteRecord Schemas
# ====================
class VoteBase(BaseModel):
    """Base vote schema."""

    ballot_option_id: int
    rank_order: Optional[int] = Field(None, ge=1)  # For ranked choice
    weight: int = Field(1, ge=1)
    is_anonymous: bool = False


class VoteCreate(VoteBase):
    """Schema for creating a vote."""

    proposal_id: int


class RankedVoteInput(BaseModel):
    """Input for ranked choice voting."""

    ballot_option_id: int
    rank: int = Field(..., ge=1)


class RankedVoteCreate(BaseModel):
    """Schema for creating ranked choice votes."""

    proposal_id: int
    ranked_choices: list[RankedVoteInput] = Field(..., min_length=1)
    is_anonymous: bool = False


class VoteResponse(VoteBase):
    """Schema for vote response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    user_id: int
    voted_at: datetime
    created_at: datetime
    updated_at: datetime


class VoteWithOptionResponse(VoteResponse):
    """Schema for vote with ballot option details."""

    option_text: str


# ====================
# VoteDelegation Schemas
# ====================
class VoteDelegationBase(BaseModel):
    """Base vote delegation schema."""

    topic_category: str = Field(
        ..., pattern="^(ALL|FINANCE|CHORES|PETS|PLANTS|ASSETS|RECIPES|OTHER)$"
    )
    start_date: datetime
    end_date: Optional[datetime] = None


class VoteDelegationCreate(VoteDelegationBase):
    """Schema for creating a vote delegation."""

    group_id: int
    delegate_id: int  # User receiving the delegation


class VoteDelegationUpdate(BaseModel):
    """Schema for updating a vote delegation."""

    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class VoteDelegationResponse(VoteDelegationBase):
    """Schema for vote delegation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    delegator_id: int
    delegate_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ====================
# BallotOption Management Schemas
# ====================
class BallotOptionCreate(BaseModel):
    """Schema for adding a ballot option to existing proposal."""

    proposal_id: int
    text: str = Field(..., min_length=1, max_length=500)
    display_order: int = Field(0, ge=0)
    option_metadata: Optional[dict[str, Any]] = None


class BallotOptionUpdate(BaseModel):
    """Schema for updating a ballot option."""

    text: Optional[str] = Field(None, min_length=1, max_length=500)
    display_order: Optional[int] = Field(None, ge=0)
    option_metadata: Optional[dict[str, Any]] = None


# ====================
# Aggregation/Summary Schemas
# ====================
class ProposalResultResponse(BaseModel):
    """Schema for proposal voting results."""

    proposal_id: int
    status: str
    total_votes: int
    quorum_reached: bool
    required_quorum: Optional[int] = None
    results: list[dict[str, Any]]  # Option ID, text, vote count, percentage
    winner_option_id: Optional[int] = None
    winner_option_text: Optional[str] = None


class VotingSummaryResponse(BaseModel):
    """Schema for voting summary."""

    proposal_id: int
    eligible_voters: int
    total_votes: int
    participation_rate: float
    votes_by_option: dict[int, int]  # Option ID -> vote count
    is_concluded: bool
    deadline_remaining_seconds: Optional[int] = None


class UserVotingHistoryResponse(BaseModel):
    """Schema for user voting history."""

    user_id: int
    total_votes_cast: int
    proposals_participated: int
    delegations_given: int
    delegations_received: int


class ActiveProposalsResponse(BaseModel):
    """Schema for list of active proposals."""

    group_id: int
    proposals: list[ProposalResponse]
    total_count: int

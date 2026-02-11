"""Governance module ORM models - voting and proposals."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import Base, BaseModel, TimestampMixin


class ProposalType(str):
    """Proposal types."""

    GENERAL = "GENERAL"
    EXPENSE_REQUEST = "EXPENSE_REQUEST"
    POLICY_CHANGE = "POLICY_CHANGE"
    KICK_USER = "KICK_USER"
    CHORE_ASSIGNMENT = "CHORE_ASSIGNMENT"
    PET_ADOPTION = "PET_ADOPTION"


class VotingStrategy(str):
    """Voting strategies."""

    SIMPLE_MAJORITY = "SIMPLE_MAJORITY"
    UNANIMOUS = "UNANIMOUS"
    RANKED_CHOICE = "RANKED_CHOICE"
    WEIGHTED = "WEIGHTED"


class ProposalStatus(str):
    """Proposal status."""

    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"


class Proposal(BaseModel, TimestampMixin):
    """Proposal - voting item."""

    __tablename__ = "proposals"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    strategy: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    deadline_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    min_quorum_percentage: Mapped[Optional[int]] = mapped_column(nullable=True)
    linked_expense_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # FK to expenses
    linked_chore_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # FK to chores
    linked_pet_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # FK to pets
    execution_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    ballot_options: Mapped[list["BallotOption"]] = relationship(
        "BallotOption", back_populates="proposal", cascade="all, delete-orphan"
    )
    votes: Mapped[list["VoteRecord"]] = relationship(
        "VoteRecord", back_populates="proposal", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "min_quorum_percentage IS NULL OR (min_quorum_percentage >= 0 AND min_quorum_percentage <= 100)",
            name="ck_proposal_quorum",
        ),
    )


class BallotOption(BaseModel, TimestampMixin):
    """Ballot option - voting choice."""

    __tablename__ = "ballot_options"

    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposals.id"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    option_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    vote_count: Mapped[int] = mapped_column(
        default=0, nullable=False
    )  # Denormalized for performance

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="ballot_options")


class VoteRecord(BaseModel, TimestampMixin):
    """Vote record - individual vote."""

    __tablename__ = "vote_records"

    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposals.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    ballot_option_id: Mapped[int] = mapped_column(ForeignKey("ballot_options.id"), nullable=False)
    rank_order: Mapped[Optional[int]] = mapped_column(nullable=True)  # For ranked choice
    weight: Mapped[int] = mapped_column(default=1, nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(default=False, nullable=False)
    voted_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="votes")

    __table_args__ = (CheckConstraint("weight > 0", name="ck_vote_weight_positive"),)


class VoteDelegation(BaseModel, TimestampMixin):
    """Vote delegation - proxy voting."""

    __tablename__ = "vote_delegations"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    delegator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    delegate_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    topic_category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ALL, FINANCE, CHORES, etc.
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

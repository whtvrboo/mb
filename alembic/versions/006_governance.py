"""Governance module: proposals, ballot options, votes, delegations

Revision ID: 006_governance
Revises: 005_chores
Create Date: 2026-01-29 17:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006_governance"
down_revision: Union[str, None] = "005_chores"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create proposals table
    op.create_table(
        "proposals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("strategy", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="DRAFT"),
        sa.Column("deadline_at", sa.DateTime(), nullable=True),
        sa.Column("min_quorum_percentage", sa.Integer(), nullable=True),
        sa.Column("linked_expense_id", sa.Integer(), nullable=True),
        sa.Column("linked_chore_id", sa.Integer(), nullable=True),
        sa.Column("linked_pet_id", sa.Integer(), nullable=True),
        sa.Column("execution_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("executed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["linked_chore_id"],
            ["chores.id"],
        ),
        sa.ForeignKeyConstraint(
            ["linked_expense_id"],
            ["expenses.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "min_quorum_percentage IS NULL OR (min_quorum_percentage >= 0 AND min_quorum_percentage <= 100)",
            name="ck_proposal_quorum",
        ),
    )
    op.create_index(op.f("ix_proposals_group_id"), "proposals", ["group_id"], unique=False)

    # Create ballot_options table
    op.create_table(
        "ballot_options",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("proposal_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("option_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("vote_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["proposals.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ballot_options_proposal_id"), "ballot_options", ["proposal_id"], unique=False
    )

    # Create vote_records table
    op.create_table(
        "vote_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("proposal_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ballot_option_id", sa.Integer(), nullable=False),
        sa.Column("rank_order", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("voted_at", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ballot_option_id"],
            ["ballot_options.id"],
        ),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["proposals.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("weight > 0", name="ck_vote_weight_positive"),
    )
    op.create_index(
        op.f("ix_vote_records_proposal_id"), "vote_records", ["proposal_id"], unique=False
    )

    # Create vote_delegations table
    op.create_table(
        "vote_delegations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("delegator_id", sa.Integer(), nullable=False),
        sa.Column("delegate_id", sa.Integer(), nullable=False),
        sa.Column("topic_category", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["delegate_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["delegator_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_vote_delegations_group_id"), "vote_delegations", ["group_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_vote_delegations_group_id"), table_name="vote_delegations")
    op.drop_table("vote_delegations")
    op.drop_index(op.f("ix_vote_records_proposal_id"), table_name="vote_records")
    op.drop_table("vote_records")
    op.drop_index(op.f("ix_ballot_options_proposal_id"), table_name="ballot_options")
    op.drop_table("ballot_options")
    op.drop_index(op.f("ix_proposals_group_id"), table_name="proposals")
    op.drop_table("proposals")

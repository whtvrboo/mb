"""Chores module: chores, assignments, dependencies, templates

Revision ID: 005_chores
Revises: 004_documents
Create Date: 2026-01-29 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "005_chores"
down_revision: Union[str, None] = "004_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chores table
    op.create_table(
        "chores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("frequency_type", sa.String(length=20), nullable=False),
        sa.Column("interval_value", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("effort_value", sa.Integer(), nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=20), nullable=True),
        sa.Column("required_item_concept_id", sa.Integer(), nullable=True),
        sa.Column("is_rotating", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("rotation_strategy", sa.String(length=20), nullable=True),
        sa.Column("last_assigned_to_id", sa.Integer(), nullable=True),
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
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["last_assigned_to_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["required_item_concept_id"],
            ["common_item_concepts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chores_group_id"), "chores", ["group_id"], unique=False)

    # Create chore_assignments table
    op.create_table(
        "chore_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chore_id", sa.Integer(), nullable=False),
        sa.Column("assigned_to_id", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("completed_by_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("actual_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("quality_rating", sa.Integer(), nullable=True),
        sa.Column("rated_by_id", sa.Integer(), nullable=True),
        sa.Column("attachment_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
            ["assigned_to_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["attachment_id"],
            ["documents.id"],
        ),
        sa.ForeignKeyConstraint(
            ["chore_id"],
            ["chores.id"],
        ),
        sa.ForeignKeyConstraint(
            ["completed_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["rated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "quality_rating IS NULL OR (quality_rating >= 1 AND quality_rating <= 5)",
            name="ck_chore_rating",
        ),
    )
    op.create_index(
        op.f("ix_chore_assignments_chore_id"), "chore_assignments", ["chore_id"], unique=False
    )

    # Create chore_dependencies table
    op.create_table(
        "chore_dependencies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chore_id", sa.Integer(), nullable=False),
        sa.Column("depends_on_chore_id", sa.Integer(), nullable=False),
        sa.Column("dependency_type", sa.String(length=20), nullable=False),
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
            ["chore_id"],
            ["chores.id"],
        ),
        sa.ForeignKeyConstraint(
            ["depends_on_chore_id"],
            ["chores.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create chore_templates table
    op.create_table(
        "chore_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("frequency_type", sa.String(length=20), nullable=False),
        sa.Column("interval_value", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("effort_value", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
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
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("chore_templates")
    op.drop_table("chore_dependencies")
    op.drop_index(op.f("ix_chore_assignments_chore_id"), table_name="chore_assignments")
    op.drop_table("chore_assignments")
    op.drop_index(op.f("ix_chores_group_id"), table_name="chores")
    op.drop_table("chores")

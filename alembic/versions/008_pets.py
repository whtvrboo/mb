"""Pets module: pets, medical records, logs, schedules

Revision ID: 008_pets
Revises: 007_plants
Create Date: 2026-01-29 19:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008_pets"
down_revision: str | None = "007_plants"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create pets table
    op.create_table(
        "pets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("species", sa.String(length=20), nullable=False),
        sa.Column("breed", sa.String(length=255), nullable=True),
        sa.Column("sex", sa.String(length=20), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("adoption_date", sa.DateTime(), nullable=True),
        sa.Column("chip_id", sa.String(length=100), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("color_markings", sa.String(length=500), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("vet_contact_id", sa.Integer(), nullable=True),
        sa.Column("insurance_policy_number", sa.String(length=100), nullable=True),
        sa.Column("insurance_provider", sa.String(length=255), nullable=True),
        sa.Column("diet_instructions", sa.Text(), nullable=True),
        sa.Column("medication_schedule", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("special_needs", sa.Text(), nullable=True),
        sa.Column("is_alive", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("died_at", sa.DateTime(), nullable=True),
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
            ["vet_contact_id"],
            ["service_contacts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pets_group_id"), "pets", ["group_id"], unique=False)

    # Create pet_medical_records table
    op.create_table(
        "pet_medical_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pet_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("performed_at", sa.DateTime(), nullable=False),
        sa.Column("performed_by", sa.String(length=255), nullable=True),
        sa.Column("cost_expense_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("reminder_days_before", sa.Integer(), nullable=True),
        sa.Column("document_id", sa.Integer(), nullable=True),
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
            ["cost_expense_id"],
            ["expenses.id"],
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pet_id"],
            ["pets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pet_medical_records_pet_id"), "pet_medical_records", ["pet_id"], unique=False
    )

    # Create pet_logs table
    op.create_table(
        "pet_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pet_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("value_amount", sa.Float(), nullable=True),
        sa.Column("value_unit", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
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
            ["pet_id"],
            ["pets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pet_logs_pet_id"), "pet_logs", ["pet_id"], unique=False)

    # Create pet_schedules table
    op.create_table(
        "pet_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pet_id", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("frequency_type", sa.String(length=20), nullable=False),
        sa.Column("time_of_day", sa.DateTime(), nullable=True),
        sa.Column("assigned_to_id", sa.Integer(), nullable=True),
        sa.Column("is_rotating", sa.Boolean(), nullable=False, server_default="false"),
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
            ["assigned_to_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pet_id"],
            ["pets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pet_schedules_pet_id"), "pet_schedules", ["pet_id"], unique=False)

    # Add FK from proposals.linked_pet_id to pets
    op.create_foreign_key("fk_proposals_linked_pet", "proposals", "pets", ["linked_pet_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_proposals_linked_pet", "proposals", type_="foreignkey")
    op.drop_index(op.f("ix_pet_schedules_pet_id"), table_name="pet_schedules")
    op.drop_table("pet_schedules")
    op.drop_index(op.f("ix_pet_logs_pet_id"), table_name="pet_logs")
    op.drop_table("pet_logs")
    op.drop_index(op.f("ix_pet_medical_records_pet_id"), table_name="pet_medical_records")
    op.drop_table("pet_medical_records")
    op.drop_index(op.f("ix_pets_group_id"), table_name="pets")
    op.drop_table("pets")

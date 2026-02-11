"""Plants module: species, plants, logs, schedules

Revision ID: 007_plants
Revises: 006_governance
Create Date: 2026-01-29 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "007_plants"
down_revision: Union[str, None] = "006_governance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create plant_species table
    op.create_table(
        "plant_species",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scientific_name", sa.String(length=255), nullable=False),
        sa.Column("common_name", sa.String(length=255), nullable=True),
        sa.Column("toxicity", sa.String(length=20), nullable=False),
        sa.Column("light_needs", sa.String(length=20), nullable=False),
        sa.Column("water_interval_summer", sa.Integer(), nullable=True),
        sa.Column("water_interval_winter", sa.Integer(), nullable=True),
        sa.Column("humidity_preference", sa.String(length=20), nullable=True),
        sa.Column("fertilize_frequency_weeks", sa.Integer(), nullable=True),
        sa.Column("growth_rate", sa.String(length=20), nullable=True),
        sa.Column("mature_height_cm", sa.Integer(), nullable=True),
        sa.Column("propagation_method", sa.String(length=20), nullable=True),
        sa.Column("care_difficulty", sa.String(length=20), nullable=True),
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
        sa.UniqueConstraint("scientific_name"),
    )

    # Create plants table
    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("species_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=True),
        sa.Column("nickname", sa.String(length=255), nullable=True),
        sa.Column("acquired_at", sa.DateTime(), nullable=True),
        sa.Column("acquired_from", sa.String(length=20), nullable=True),
        sa.Column("parent_plant_id", sa.Integer(), nullable=True),
        sa.Column("pot_size_cm", sa.Integer(), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("is_alive", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("died_at", sa.DateTime(), nullable=True),
        sa.Column("death_reason", sa.Text(), nullable=True),
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
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_plant_id"],
            ["plants.id"],
        ),
        sa.ForeignKeyConstraint(
            ["species_id"],
            ["plant_species.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plants_group_id"), "plants", ["group_id"], unique=False)

    # Create plant_logs table
    op.create_table(
        "plant_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("quantity_value", sa.Float(), nullable=True),
        sa.Column("quantity_unit", sa.String(length=50), nullable=True),
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
            ["plant_id"],
            ["plants.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plant_logs_plant_id"), "plant_logs", ["plant_id"], unique=False)

    # Create plant_schedules table
    op.create_table(
        "plant_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("next_due_date", sa.DateTime(), nullable=False),
        sa.Column("frequency_days", sa.Integer(), nullable=False),
        sa.Column("assigned_to_id", sa.Integer(), nullable=True),
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
            ["plant_id"],
            ["plants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_plant_schedules_plant_id"), "plant_schedules", ["plant_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_plant_schedules_plant_id"), table_name="plant_schedules")
    op.drop_table("plant_schedules")
    op.drop_index(op.f("ix_plant_logs_plant_id"), table_name="plant_logs")
    op.drop_table("plant_logs")
    op.drop_index(op.f("ix_plants_group_id"), table_name="plants")
    op.drop_table("plants")
    op.drop_table("plant_species")

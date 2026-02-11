"""Calendar module: events, attendees, reminders

Revision ID: 013_calendar
Revises: 012_gamification
Create Date: 2026-01-30 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "013_calendar"
down_revision: str | None = "012_gamification"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create calendar_events table
    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_date", sa.DateTime(), nullable=False),
        sa.Column("event_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("is_all_day", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("recurrence_rule", sa.String(length=500), nullable=True),
        sa.Column("reminder_minutes_before", sa.Integer(), nullable=True),
        sa.Column("location_text", sa.String(length=500), nullable=True),
        sa.Column("linked_user_id", sa.Integer(), nullable=True),
        sa.Column("linked_asset_id", sa.Integer(), nullable=True),
        sa.Column("linked_pet_id", sa.Integer(), nullable=True),
        sa.Column("is_cancelled", sa.Boolean(), nullable=False, server_default="false"),
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
            ["linked_asset_id"],
            ["home_assets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["linked_pet_id"],
            ["pets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["linked_user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_calendar_events_group_id"), "calendar_events", ["group_id"], unique=False
    )

    # Create event_attendees table
    op.create_table(
        "event_attendees",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rsvp_status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("rsvp_at", sa.DateTime(), nullable=True),
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
            ["event_id"],
            ["calendar_events.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_event_attendees_event_id"), "event_attendees", ["event_id"], unique=False
    )

    # Create reminders table
    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
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
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reminders_group_id"), "reminders", ["group_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reminders_group_id"), table_name="reminders")
    op.drop_table("reminders")
    op.drop_index(op.f("ix_event_attendees_event_id"), table_name="event_attendees")
    op.drop_table("event_attendees")
    op.drop_index(op.f("ix_calendar_events_group_id"), table_name="calendar_events")
    op.drop_table("calendar_events")

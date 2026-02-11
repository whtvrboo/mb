"""Assets module: home assets, maintenance tasks, logs, insurance

Revision ID: 009_assets
Revises: 008_pets
Create Date: 2026-01-29 20:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009_assets"
down_revision: str | None = "008_pets"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create home_assets table
    op.create_table(
        "home_assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("brand", sa.String(length=255), nullable=True),
        sa.Column("model_number", sa.String(length=100), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("purchase_date", sa.DateTime(), nullable=True),
        sa.Column("purchase_price", sa.Float(), nullable=True),
        sa.Column("purchase_store", sa.String(length=255), nullable=True),
        sa.Column("warranty_end_date", sa.DateTime(), nullable=True),
        sa.Column("warranty_type", sa.String(length=20), nullable=True),
        sa.Column("energy_rating", sa.String(length=10), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("manual_document_id", sa.Integer(), nullable=True),
        sa.Column("receipt_document_id", sa.Integer(), nullable=True),
        sa.Column("service_contact_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("disposed_at", sa.DateTime(), nullable=True),
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
            ["manual_document_id"],
            ["documents.id"],
        ),
        sa.ForeignKeyConstraint(
            ["receipt_document_id"],
            ["documents.id"],
        ),
        sa.ForeignKeyConstraint(
            ["service_contact_id"],
            ["service_contacts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_home_assets_group_id"), "home_assets", ["group_id"], unique=False)

    # Create maintenance_tasks table
    op.create_table(
        "maintenance_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("frequency_days", sa.Integer(), nullable=False),
        sa.Column("last_completed_at", sa.DateTime(), nullable=True),
        sa.Column("next_due_date", sa.DateTime(), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("estimated_cost", sa.Float(), nullable=True),
        sa.Column("required_item_concept_id", sa.Integer(), nullable=True),
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
            ["asset_id"],
            ["home_assets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["required_item_concept_id"],
            ["common_item_concepts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_maintenance_tasks_asset_id"), "maintenance_tasks", ["asset_id"], unique=False
    )

    # Create maintenance_logs table
    op.create_table(
        "maintenance_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.Column("actual_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("cost_expense_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("quality_rating", sa.Integer(), nullable=True),
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
            ["task_id"],
            ["maintenance_tasks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "quality_rating IS NULL OR (quality_rating >= 1 AND quality_rating <= 5)",
            name="ck_maintenance_rating",
        ),
    )
    op.create_index(
        op.f("ix_maintenance_logs_task_id"), "maintenance_logs", ["task_id"], unique=False
    )

    # Create asset_insurances table
    op.create_table(
        "asset_insurances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("policy_number", sa.String(length=100), nullable=False),
        sa.Column("provider_name", sa.String(length=255), nullable=False),
        sa.Column("coverage_type", sa.String(length=50), nullable=False),
        sa.Column("premium_amount", sa.Float(), nullable=False),
        sa.Column("premium_frequency", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("deductible_amount", sa.Float(), nullable=True),
        sa.Column("document_id", sa.Integer(), nullable=True),
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
            ["document_id"],
            ["documents.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("premium_amount >= 0", name="ck_insurance_premium_non_negative"),
    )
    op.create_index(
        op.f("ix_asset_insurances_group_id"), "asset_insurances", ["group_id"], unique=False
    )

    # Add FK from expenses.linked_maintenance_log_id to maintenance_logs
    op.create_foreign_key(
        "fk_expenses_linked_maintenance_log",
        "expenses",
        "maintenance_logs",
        ["linked_maintenance_log_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_expenses_linked_maintenance_log", "expenses", type_="foreignkey")
    op.drop_index(op.f("ix_asset_insurances_group_id"), table_name="asset_insurances")
    op.drop_table("asset_insurances")
    op.drop_index(op.f("ix_maintenance_logs_task_id"), table_name="maintenance_logs")
    op.drop_table("maintenance_logs")
    op.drop_index(op.f("ix_maintenance_tasks_asset_id"), table_name="maintenance_tasks")
    op.drop_table("maintenance_tasks")
    op.drop_index(op.f("ix_home_assets_group_id"), table_name="home_assets")
    op.drop_table("home_assets")

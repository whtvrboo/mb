"""Finance module: categories, expenses, splits, budgets, etc.

Revision ID: 003_finance
Revises: 002_auth_core_ext
Create Date: 2026-01-29 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_finance"
down_revision: Union[str, None] = "002_auth_core_ext"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("icon_emoji", sa.String(length=10), nullable=True),
        sa.Column("color_hex", sa.String(length=7), nullable=True),
        sa.Column("parent_category_id", sa.Integer(), nullable=True),
        sa.Column("is_income", sa.Boolean(), nullable=False, server_default="false"),
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
            ["parent_category_id"],
            ["categories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_group_id"), "categories", ["group_id"], unique=False)

    # Create split_presets table (needed before recurring_expenses)
    op.create_table(
        "split_presets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("method", sa.String(length=20), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_split_presets_group_id"), "split_presets", ["group_id"], unique=False)

    # Create split_preset_members table
    op.create_table(
        "split_preset_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("preset_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("fixed_amount", sa.Numeric(precision=10, scale=2), nullable=True),
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
            ["preset_id"],
            ["split_presets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("preset_id", "user_id", name="uq_split_preset_member"),
    )
    op.create_index(
        op.f("ix_split_preset_members_preset_id"),
        "split_preset_members",
        ["preset_id"],
        unique=False,
    )

    # Create recurring_expenses table
    op.create_table(
        "recurring_expenses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("paid_by_user_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("frequency_type", sa.String(length=20), nullable=False),
        sa.Column("interval_value", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("next_due_date", sa.DateTime(), nullable=True),
        sa.Column("auto_create_expense", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("split_preset_id", sa.Integer(), nullable=True),
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
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["paid_by_user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["split_preset_id"],
            ["split_presets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recurring_expenses_group_id"), "recurring_expenses", ["group_id"], unique=False
    )

    # Create expenses table (with version_id for optimistic locking)
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("paid_by_user_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("exchange_rate", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("receipt_img_url", sa.String(length=500), nullable=True),
        sa.Column("expense_date", sa.DateTime(), nullable=False),
        sa.Column("payment_method", sa.String(length=20), nullable=True),
        sa.Column("vendor_name", sa.String(length=255), nullable=True),
        sa.Column("is_reimbursable", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_recurring_generated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("linked_proposal_id", sa.Integer(), nullable=True),
        sa.Column("linked_pet_medical_id", sa.Integer(), nullable=True),
        sa.Column("linked_maintenance_log_id", sa.Integer(), nullable=True),
        sa.Column("linked_recurring_expense_id", sa.Integer(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("version_id", sa.Integer(), nullable=False, server_default="1"),
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
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["linked_recurring_expense_id"],
            ["recurring_expenses.id"],
        ),
        sa.ForeignKeyConstraint(
            ["paid_by_user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("amount > 0", name="ck_expense_amount_positive"),
    )
    op.create_index(op.f("ix_expenses_group_id"), "expenses", ["group_id"], unique=False)

    # Create expense_splits table
    op.create_table(
        "expense_splits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("expense_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("owed_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("is_paid", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("manual_override", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
            ["expense_id"],
            ["expenses.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("owed_amount >= 0", name="ck_expense_split_amount_non_negative"),
    )
    op.create_index(
        op.f("ix_expense_splits_expense_id"), "expense_splits", ["expense_id"], unique=False
    )

    # Create settlements table
    op.create_table(
        "settlements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("payer_id", sa.Integer(), nullable=False),
        sa.Column("payee_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.Column("settled_at", sa.DateTime(), nullable=False),
        sa.Column("confirmation_code", sa.String(length=100), nullable=True),
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
            ["payee_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["payer_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("amount > 0", name="ck_settlement_amount_positive"),
    )
    op.create_index(op.f("ix_settlements_group_id"), "settlements", ["group_id"], unique=False)

    # Create budgets table
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("amount_limit", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("period_type", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("alert_threshold_percentage", sa.Integer(), nullable=False, server_default="80"),
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
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("amount_limit > 0", name="ck_budget_amount_positive"),
        sa.CheckConstraint(
            "alert_threshold_percentage BETWEEN 0 AND 100", name="ck_budget_threshold"
        ),
    )
    op.create_index(op.f("ix_budgets_group_id"), "budgets", ["group_id"], unique=False)

    # Create balance_snapshots table
    op.create_table(
        "balance_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("balance_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("snapshot_date", sa.DateTime(), nullable=False),
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
        sa.UniqueConstraint("group_id", "user_id", "snapshot_date", name="uq_balance_snapshot"),
    )
    op.create_index(
        op.f("ix_balance_snapshots_group_id"), "balance_snapshots", ["group_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_balance_snapshots_group_id"), table_name="balance_snapshots")
    op.drop_table("balance_snapshots")
    op.drop_index(op.f("ix_budgets_group_id"), table_name="budgets")
    op.drop_table("budgets")
    op.drop_index(op.f("ix_settlements_group_id"), table_name="settlements")
    op.drop_table("settlements")
    op.drop_index(op.f("ix_expense_splits_expense_id"), table_name="expense_splits")
    op.drop_table("expense_splits")
    op.drop_index(op.f("ix_expenses_group_id"), table_name="expenses")
    op.drop_table("expenses")
    op.drop_index(op.f("ix_recurring_expenses_group_id"), table_name="recurring_expenses")
    op.drop_table("recurring_expenses")
    op.drop_index(op.f("ix_split_preset_members_preset_id"), table_name="split_preset_members")
    op.drop_table("split_preset_members")
    op.drop_index(op.f("ix_split_presets_group_id"), table_name="split_presets")
    op.drop_table("split_presets")
    op.drop_index(op.f("ix_categories_group_id"), table_name="categories")
    op.drop_table("categories")

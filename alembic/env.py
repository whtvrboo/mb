"""Alembic environment configuration."""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from mitlist.core.config import settings
from mitlist.db.base import Base
from mitlist.modules.assets.models import (  # noqa: F401
    AssetInsurance,
    HomeAsset,
    MaintenanceLog,
    MaintenanceTask,
)
from mitlist.modules.audit.models import AuditLog, ReportSnapshot, Tag, TagAssignment  # noqa: F401

# Import all models so Alembic can detect them
from mitlist.modules.auth.models import (  # noqa: F401
    CommonItemConcept,
    Group,
    Invite,
    Location,
    ServiceContact,
    User,
    UserGroup,
)
from mitlist.modules.calendar.models import CalendarEvent, EventAttendee, Reminder  # noqa: F401
from mitlist.modules.chores.models import (  # noqa: F401
    Chore,
    ChoreAssignment,
    ChoreDependency,
    ChoreTemplate,
)
from mitlist.modules.documents.models import Document, DocumentShare, SharedCredential  # noqa: F401
from mitlist.modules.finance.models import (  # noqa: F401
    BalanceSnapshot,
    Budget,
    Category,
    Expense,
    ExpenseSplit,
    RecurringExpense,
    Settlement,
    SplitPreset,
    SplitPresetMember,
)
from mitlist.modules.gamification.models import (  # noqa: F401
    Achievement,
    Leaderboard,
    Streak,
    UserAchievement,
    UserPoints,
)
from mitlist.modules.governance.models import (  # noqa: F401
    BallotOption,
    Proposal,
    VoteDelegation,
    VoteRecord,
)
from mitlist.modules.lists.models import InventoryItem, Item, List, ListShare  # noqa: F401
from mitlist.modules.notifications.models import (  # noqa: F401
    Comment,
    Mention,
    Notification,
    NotificationPreference,
    Reaction,
)
from mitlist.modules.pets.models import Pet, PetLog, PetMedicalRecord, PetSchedule  # noqa: F401
from mitlist.modules.plants.models import Plant, PlantLog, PlantSchedule, PlantSpecies  # noqa: F401
from mitlist.modules.recipes.models import (  # noqa: F401
    MealPlan,
    MealPlanShoppingSync,
    Recipe,
    RecipeIngredient,
    RecipeStep,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLAlchemy URL from settings
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

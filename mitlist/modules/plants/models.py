"""Plants module ORM models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import Base, BaseModel, TimestampMixin


class ToxicityLevel(str):
    """Plant toxicity levels."""

    SAFE = "SAFE"
    TOXIC_CATS = "TOXIC_CATS"
    TOXIC_DOGS = "TOXIC_DOGS"
    TOXIC_ALL = "TOXIC_ALL"


class LightNeeds(str):
    """Light needs."""

    LOW = "LOW"
    INDIRECT = "INDIRECT"
    DIRECT = "DIRECT"


class HumidityPreference(str):
    """Humidity preferences."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class GrowthRate(str):
    """Growth rate."""

    SLOW = "SLOW"
    MEDIUM = "MEDIUM"
    FAST = "FAST"


class PropagationMethod(str):
    """Propagation methods."""

    SEED = "SEED"
    CUTTING = "CUTTING"
    DIVISION = "DIVISION"


class CareDifficulty(str):
    """Care difficulty."""

    EASY = "EASY"
    MODERATE = "MODERATE"
    HARD = "HARD"


class AcquiredFrom(str):
    """Acquisition source."""

    STORE = "STORE"
    GIFT = "GIFT"
    PROPAGATION = "PROPAGATION"


class PlantAction(str):
    """Plant log actions."""

    WATER = "WATER"
    FERTILIZE = "FERTILIZE"
    PRUNE = "PRUNE"
    REPOT = "REPOT"
    PEST_CONTROL = "PEST_CONTROL"
    ROTATE = "ROTATE"
    PROPAGATE = "PROPAGATE"


class PlantSpecies(BaseModel, TimestampMixin):
    """Plant species - reference data."""

    __tablename__ = "plant_species"

    scientific_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    common_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    toxicity: Mapped[str] = mapped_column(String(20), nullable=False)
    light_needs: Mapped[str] = mapped_column(String(20), nullable=False)
    water_interval_summer: Mapped[Optional[int]] = mapped_column(nullable=True)  # days
    water_interval_winter: Mapped[Optional[int]] = mapped_column(nullable=True)  # days
    humidity_preference: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    fertilize_frequency_weeks: Mapped[Optional[int]] = mapped_column(nullable=True)
    growth_rate: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mature_height_cm: Mapped[Optional[int]] = mapped_column(nullable=True)
    propagation_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    care_difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class Plant(BaseModel, TimestampMixin):
    """Plant - individual plant instance."""

    __tablename__ = "plants"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("plant_species.id"), nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    acquired_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    acquired_from: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    parent_plant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("plants.id"), nullable=True)
    pot_size_cm: Mapped[Optional[int]] = mapped_column(nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_alive: Mapped[bool] = mapped_column(default=True, nullable=False)
    died_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    death_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PlantLog(BaseModel, TimestampMixin):
    """Plant log - care activity record."""

    __tablename__ = "plant_logs"

    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    quantity_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(nullable=False)


class PlantSchedule(BaseModel, TimestampMixin):
    """Plant schedule - next care actions."""

    __tablename__ = "plant_schedules"

    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    next_due_date: Mapped[datetime] = mapped_column(nullable=False)
    frequency_days: Mapped[int] = mapped_column(nullable=False)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

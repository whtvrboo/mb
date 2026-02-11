"""Plants module Pydantic schemas for request/response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ====================
# PlantSpecies Schemas
# ====================
class PlantSpeciesBase(BaseModel):
    """Base plant species schema."""

    scientific_name: str = Field(..., min_length=1, max_length=255)
    common_name: str | None = Field(None, max_length=255)
    toxicity: str = Field(..., pattern="^(SAFE|TOXIC_CATS|TOXIC_DOGS|TOXIC_ALL)$")
    light_needs: str = Field(..., pattern="^(LOW|INDIRECT|DIRECT)$")
    water_interval_summer: int | None = Field(None, ge=1)  # days
    water_interval_winter: int | None = Field(None, ge=1)  # days
    humidity_preference: str | None = Field(None, pattern="^(LOW|MEDIUM|HIGH)$")
    fertilize_frequency_weeks: int | None = Field(None, ge=1)
    growth_rate: str | None = Field(None, pattern="^(SLOW|MEDIUM|FAST)$")
    mature_height_cm: int | None = Field(None, ge=1)
    propagation_method: str | None = Field(None, pattern="^(SEED|CUTTING|DIVISION)$")
    care_difficulty: str | None = Field(None, pattern="^(EASY|MODERATE|HARD)$")


class PlantSpeciesCreate(PlantSpeciesBase):
    """Schema for creating a plant species."""

    pass


class PlantSpeciesUpdate(BaseModel):
    """Schema for updating a plant species."""

    scientific_name: str | None = Field(None, min_length=1, max_length=255)
    common_name: str | None = Field(None, max_length=255)
    toxicity: str | None = Field(None, pattern="^(SAFE|TOXIC_CATS|TOXIC_DOGS|TOXIC_ALL)$")
    light_needs: str | None = Field(None, pattern="^(LOW|INDIRECT|DIRECT)$")
    water_interval_summer: int | None = Field(None, ge=1)
    water_interval_winter: int | None = Field(None, ge=1)
    humidity_preference: str | None = Field(None, pattern="^(LOW|MEDIUM|HIGH)$")
    fertilize_frequency_weeks: int | None = Field(None, ge=1)
    growth_rate: str | None = Field(None, pattern="^(SLOW|MEDIUM|FAST)$")
    mature_height_cm: int | None = Field(None, ge=1)
    propagation_method: str | None = Field(None, pattern="^(SEED|CUTTING|DIVISION)$")
    care_difficulty: str | None = Field(None, pattern="^(EASY|MODERATE|HARD)$")


class PlantSpeciesResponse(PlantSpeciesBase):
    """Schema for plant species response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ====================
# Plant Schemas
# ====================
class PlantBase(BaseModel):
    """Base plant schema."""

    species_id: int
    location_id: int | None = None
    nickname: str | None = Field(None, max_length=255)
    acquired_at: datetime | None = None
    acquired_from: str | None = Field(None, pattern="^(STORE|GIFT|PROPAGATION)$")
    pot_size_cm: int | None = Field(None, ge=1)
    photo_url: str | None = Field(None, max_length=500)
    notes: str | None = None


class PlantCreate(PlantBase):
    """Schema for creating a plant."""

    group_id: int
    parent_plant_id: int | None = None  # For propagated plants


class PlantUpdate(BaseModel):
    """Schema for updating a plant."""

    location_id: int | None = None
    nickname: str | None = Field(None, max_length=255)
    pot_size_cm: int | None = Field(None, ge=1)
    photo_url: str | None = Field(None, max_length=500)
    notes: str | None = None


class PlantMarkDeadRequest(BaseModel):
    """Schema for marking a plant as dead."""

    death_reason: str | None = None


class PlantResponse(PlantBase):
    """Schema for plant response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    parent_plant_id: int | None = None
    is_alive: bool
    died_at: datetime | None = None
    death_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class PlantWithSpeciesResponse(PlantResponse):
    """Schema for plant with embedded species details."""

    species: PlantSpeciesResponse


# ====================
# PlantLog Schemas
# ====================
class PlantLogBase(BaseModel):
    """Base plant log schema."""

    action: str = Field(
        ...,
        pattern="^(WATER|FERTILIZE|PRUNE|REPOT|PEST_CONTROL|ROTATE|PROPAGATE)$",
    )
    quantity_value: float | None = Field(None, ge=0)
    quantity_unit: str | None = Field(None, max_length=50)
    notes: str | None = None
    photo_url: str | None = Field(None, max_length=500)
    occurred_at: datetime


class PlantLogCreate(PlantLogBase):
    """Schema for creating a plant log."""

    plant_id: int


class PlantLogResponse(PlantLogBase):
    """Schema for plant log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# PlantSchedule Schemas
# ====================
class PlantScheduleBase(BaseModel):
    """Base plant schedule schema."""

    action_type: str = Field(
        ...,
        pattern="^(WATER|FERTILIZE|PRUNE|REPOT|PEST_CONTROL|ROTATE|PROPAGATE)$",
    )
    next_due_date: datetime
    frequency_days: int = Field(..., ge=1)
    assigned_to_id: int | None = None


class PlantScheduleCreate(PlantScheduleBase):
    """Schema for creating a plant schedule."""

    plant_id: int


class PlantScheduleUpdate(BaseModel):
    """Schema for updating a plant schedule."""

    next_due_date: datetime | None = None
    frequency_days: int | None = Field(None, ge=1)
    assigned_to_id: int | None = None


class PlantScheduleResponse(PlantScheduleBase):
    """Schema for plant schedule response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: int
    created_at: datetime
    updated_at: datetime


class PlantScheduleMarkDoneRequest(BaseModel):
    """Schema for marking a scheduled action as done."""

    notes: str | None = None
    quantity_value: float | None = Field(None, ge=0)
    quantity_unit: str | None = Field(None, max_length=50)


# ====================
# Aggregation/Summary Schemas
# ====================
class PlantCareStatusResponse(BaseModel):
    """Schema for plant care status."""

    plant_id: int
    nickname: str | None = None
    species_name: str
    is_alive: bool
    overdue_actions: list[str]
    upcoming_actions: list[dict]  # action_type, due_date
    last_watered_at: datetime | None = None
    last_fertilized_at: datetime | None = None
    days_since_last_care: int | None = None


class GroupPlantSummaryResponse(BaseModel):
    """Schema for group plant summary."""

    group_id: int
    total_plants: int
    alive_plants: int
    dead_plants: int
    plants_needing_care_today: int
    plants_overdue: int
    total_care_actions_this_week: int


class ToxicityWarningResponse(BaseModel):
    """Schema for toxicity warning (when pets are in same group)."""

    plant_id: int
    plant_nickname: str | None = None
    species_name: str
    toxicity_level: str
    affected_pets: list[dict]  # pet_id, pet_name, pet_species


class PlantCareHistoryResponse(BaseModel):
    """Schema for plant care history."""

    plant_id: int
    care_logs: list[PlantLogResponse]
    total_waterings: int
    total_fertilizations: int
    average_days_between_waterings: float | None = None

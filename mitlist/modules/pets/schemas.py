"""Pets module Pydantic schemas for request/response models."""

from datetime import datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ====================
# Pet Schemas
# ====================
class PetBase(BaseModel):
    """Base pet schema."""

    name: str = Field(..., min_length=1, max_length=255)
    species: str = Field(..., pattern="^(DOG|CAT|BIRD|REPTILE|FISH|RODENT|OTHER)$")
    breed: str | None = Field(None, max_length=255)
    sex: str | None = Field(None, pattern="^(MALE|FEMALE|UNKNOWN)$")
    date_of_birth: datetime | None = None
    adoption_date: datetime | None = None
    chip_id: str | None = Field(None, max_length=100)
    weight_kg: float | None = Field(None, gt=0)
    color_markings: str | None = Field(None, max_length=500)
    photo_url: str | None = Field(None, max_length=500)
    diet_instructions: str | None = None
    special_needs: str | None = None


class PetCreate(PetBase):
    """Schema for creating a pet."""

    group_id: int
    vet_contact_id: int | None = None
    insurance_policy_number: str | None = Field(None, max_length=100)
    insurance_provider: str | None = Field(None, max_length=255)
    medication_schedule: dict[str, Any] | None = None


class PetUpdate(BaseModel):
    """Schema for updating a pet."""

    name: str | None = Field(None, min_length=1, max_length=255)
    breed: str | None = Field(None, max_length=255)
    sex: str | None = Field(None, pattern="^(MALE|FEMALE|UNKNOWN)$")
    date_of_birth: datetime | None = None
    chip_id: str | None = Field(None, max_length=100)
    weight_kg: float | None = Field(None, gt=0)
    color_markings: str | None = Field(None, max_length=500)
    photo_url: str | None = Field(None, max_length=500)
    vet_contact_id: int | None = None
    insurance_policy_number: str | None = Field(None, max_length=100)
    insurance_provider: str | None = Field(None, max_length=255)
    diet_instructions: str | None = None
    medication_schedule: dict[str, Any] | None = None
    special_needs: str | None = None


class PetMarkDeceasedRequest(BaseModel):
    """Schema for marking a pet as deceased."""

    died_at: datetime = Field(default_factory=datetime.utcnow)


class PetResponse(PetBase):
    """Schema for pet response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    vet_contact_id: int | None = None
    insurance_policy_number: str | None = None
    insurance_provider: str | None = None
    medication_schedule: dict[str, Any] | None = None
    is_alive: bool
    died_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# ====================
# PetMedicalRecord Schemas
# ====================
class PetMedicalRecordBase(BaseModel):
    """Base pet medical record schema."""

    type: str = Field(..., pattern="^(VACCINE|SURGERY|CHECKUP|MEDICATION|INJURY|ALLERGY)$")
    description: str = Field(..., min_length=1)
    performed_at: datetime
    performed_by: str | None = Field(None, max_length=255)
    expires_at: datetime | None = None
    reminder_days_before: int | None = Field(None, ge=1)
    notes: str | None = None


class PetMedicalRecordCreate(PetMedicalRecordBase):
    """Schema for creating a pet medical record."""

    pet_id: int
    cost_expense_id: int | None = None
    document_id: int | None = None


class PetMedicalRecordUpdate(BaseModel):
    """Schema for updating a pet medical record."""

    description: str | None = Field(None, min_length=1)
    performed_by: str | None = Field(None, max_length=255)
    expires_at: datetime | None = None
    reminder_days_before: int | None = Field(None, ge=1)
    notes: str | None = None
    cost_expense_id: int | None = None
    document_id: int | None = None


class PetMedicalRecordResponse(PetMedicalRecordBase):
    """Schema for pet medical record response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    cost_expense_id: int | None = None
    document_id: int | None = None
    created_at: datetime
    updated_at: datetime


# ====================
# PetLog Schemas
# ====================
class PetLogBase(BaseModel):
    """Base pet log schema."""

    action: str = Field(..., pattern="^(WALK|FEED|MEDICINE|GROOM|PLAY|VET_VISIT)$")
    value_amount: float | None = Field(None, ge=0)
    value_unit: str | None = Field(None, max_length=50)
    notes: str | None = None
    photo_url: str | None = Field(None, max_length=500)
    occurred_at: datetime


class PetLogCreate(PetLogBase):
    """Schema for creating a pet log."""

    pet_id: int


class PetLogResponse(PetLogBase):
    """Schema for pet log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# PetSchedule Schemas
# ====================
class PetScheduleBase(BaseModel):
    """Base pet schedule schema."""

    action_type: str = Field(..., pattern="^(WALK|FEED|MEDICINE|GROOM|PLAY|VET_VISIT)$")
    frequency_type: str = Field(..., pattern="^(DAILY|WEEKLY)$")
    time_of_day: time | None = None
    assigned_to_id: int | None = None
    is_rotating: bool = False


class PetScheduleCreate(PetScheduleBase):
    """Schema for creating a pet schedule."""

    pet_id: int


class PetScheduleUpdate(BaseModel):
    """Schema for updating a pet schedule."""

    frequency_type: str | None = Field(None, pattern="^(DAILY|WEEKLY)$")
    time_of_day: time | None = None
    assigned_to_id: int | None = None
    is_rotating: bool | None = None
    is_active: bool | None = None


class PetScheduleResponse(PetScheduleBase):
    """Schema for pet schedule response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("time_of_day", mode="before")
    @classmethod
    def time_of_day_from_datetime(cls, v: time | datetime | None) -> time | None:
        """Accept datetime from DB (SQLite stores time as datetime) and normalize to time."""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.time()
        return v


class PetScheduleMarkDoneRequest(BaseModel):
    """Schema for marking a scheduled action as done."""

    notes: str | None = None
    value_amount: float | None = Field(None, ge=0)
    value_unit: str | None = Field(None, max_length=50)


# ====================
# Aggregation/Summary Schemas
# ====================
class PetCareStatusResponse(BaseModel):
    """Schema for pet care status."""

    pet_id: int
    pet_name: str
    species: str
    is_alive: bool
    age_years: float | None = None
    overdue_actions: list[str]
    upcoming_vaccinations: list[dict]  # vaccine type, due_date
    last_fed_at: datetime | None = None
    last_walked_at: datetime | None = None
    last_vet_visit_at: datetime | None = None


class GroupPetSummaryResponse(BaseModel):
    """Schema for group pet summary."""

    group_id: int
    total_pets: int
    alive_pets: int
    pets_by_species: dict[str, int]
    pets_needing_care_today: int
    upcoming_vet_appointments: int
    expiring_vaccinations: int


class VaccineReminderResponse(BaseModel):
    """Schema for vaccine reminder."""

    pet_id: int
    pet_name: str
    vaccine_type: str
    last_administered_at: datetime | None = None
    expires_at: datetime
    days_until_expiry: int
    is_expired: bool


class PetCareHistoryResponse(BaseModel):
    """Schema for pet care history."""

    pet_id: int
    care_logs: list[PetLogResponse]
    total_walks: int
    total_feedings: int
    total_vet_visits: int
    medical_records: list[PetMedicalRecordResponse]


class PetMedicationReminderResponse(BaseModel):
    """Schema for medication reminder."""

    pet_id: int
    pet_name: str
    medication_name: str
    dosage: str | None = None
    next_dose_at: datetime | None = None
    frequency: str

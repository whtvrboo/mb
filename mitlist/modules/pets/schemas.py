"""Pets module Pydantic schemas for request/response models."""

from datetime import datetime, time
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ====================
# Pet Schemas
# ====================
class PetBase(BaseModel):
    """Base pet schema."""

    name: str = Field(..., min_length=1, max_length=255)
    species: str = Field(
        ..., pattern="^(DOG|CAT|BIRD|REPTILE|FISH|RODENT|OTHER)$"
    )
    breed: Optional[str] = Field(None, max_length=255)
    sex: Optional[str] = Field(None, pattern="^(MALE|FEMALE|UNKNOWN)$")
    date_of_birth: Optional[datetime] = None
    adoption_date: Optional[datetime] = None
    chip_id: Optional[str] = Field(None, max_length=100)
    weight_kg: Optional[float] = Field(None, gt=0)
    color_markings: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = Field(None, max_length=500)
    diet_instructions: Optional[str] = None
    special_needs: Optional[str] = None


class PetCreate(PetBase):
    """Schema for creating a pet."""

    group_id: int
    vet_contact_id: Optional[int] = None
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_provider: Optional[str] = Field(None, max_length=255)
    medication_schedule: Optional[dict[str, Any]] = None


class PetUpdate(BaseModel):
    """Schema for updating a pet."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    breed: Optional[str] = Field(None, max_length=255)
    sex: Optional[str] = Field(None, pattern="^(MALE|FEMALE|UNKNOWN)$")
    date_of_birth: Optional[datetime] = None
    chip_id: Optional[str] = Field(None, max_length=100)
    weight_kg: Optional[float] = Field(None, gt=0)
    color_markings: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = Field(None, max_length=500)
    vet_contact_id: Optional[int] = None
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_provider: Optional[str] = Field(None, max_length=255)
    diet_instructions: Optional[str] = None
    medication_schedule: Optional[dict[str, Any]] = None
    special_needs: Optional[str] = None


class PetMarkDeceasedRequest(BaseModel):
    """Schema for marking a pet as deceased."""

    died_at: datetime = Field(default_factory=datetime.utcnow)


class PetResponse(PetBase):
    """Schema for pet response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    vet_contact_id: Optional[int] = None
    insurance_policy_number: Optional[str] = None
    insurance_provider: Optional[str] = None
    medication_schedule: Optional[dict[str, Any]] = None
    is_alive: bool
    died_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ====================
# PetMedicalRecord Schemas
# ====================
class PetMedicalRecordBase(BaseModel):
    """Base pet medical record schema."""

    type: str = Field(
        ..., pattern="^(VACCINE|SURGERY|CHECKUP|MEDICATION|INJURY|ALLERGY)$"
    )
    description: str = Field(..., min_length=1)
    performed_at: datetime
    performed_by: Optional[str] = Field(None, max_length=255)
    expires_at: Optional[datetime] = None
    reminder_days_before: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None


class PetMedicalRecordCreate(PetMedicalRecordBase):
    """Schema for creating a pet medical record."""

    pet_id: int
    cost_expense_id: Optional[int] = None
    document_id: Optional[int] = None


class PetMedicalRecordUpdate(BaseModel):
    """Schema for updating a pet medical record."""

    description: Optional[str] = Field(None, min_length=1)
    performed_by: Optional[str] = Field(None, max_length=255)
    expires_at: Optional[datetime] = None
    reminder_days_before: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    cost_expense_id: Optional[int] = None
    document_id: Optional[int] = None


class PetMedicalRecordResponse(PetMedicalRecordBase):
    """Schema for pet medical record response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    cost_expense_id: Optional[int] = None
    document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# ====================
# PetLog Schemas
# ====================
class PetLogBase(BaseModel):
    """Base pet log schema."""

    action: str = Field(
        ..., pattern="^(WALK|FEED|MEDICINE|GROOM|PLAY|VET_VISIT)$"
    )
    value_amount: Optional[float] = Field(None, ge=0)
    value_unit: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)
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

    action_type: str = Field(
        ..., pattern="^(WALK|FEED|MEDICINE|GROOM|PLAY|VET_VISIT)$"
    )
    frequency_type: str = Field(..., pattern="^(DAILY|WEEKLY)$")
    time_of_day: Optional[time] = None
    assigned_to_id: Optional[int] = None
    is_rotating: bool = False


class PetScheduleCreate(PetScheduleBase):
    """Schema for creating a pet schedule."""

    pet_id: int


class PetScheduleUpdate(BaseModel):
    """Schema for updating a pet schedule."""

    frequency_type: Optional[str] = Field(None, pattern="^(DAILY|WEEKLY)$")
    time_of_day: Optional[time] = None
    assigned_to_id: Optional[int] = None
    is_rotating: Optional[bool] = None
    is_active: Optional[bool] = None


class PetScheduleResponse(PetScheduleBase):
    """Schema for pet schedule response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PetScheduleMarkDoneRequest(BaseModel):
    """Schema for marking a scheduled action as done."""

    notes: Optional[str] = None
    value_amount: Optional[float] = Field(None, ge=0)
    value_unit: Optional[str] = Field(None, max_length=50)


# ====================
# Aggregation/Summary Schemas
# ====================
class PetCareStatusResponse(BaseModel):
    """Schema for pet care status."""

    pet_id: int
    pet_name: str
    species: str
    is_alive: bool
    age_years: Optional[float] = None
    overdue_actions: list[str]
    upcoming_vaccinations: list[dict]  # vaccine type, due_date
    last_fed_at: Optional[datetime] = None
    last_walked_at: Optional[datetime] = None
    last_vet_visit_at: Optional[datetime] = None


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
    last_administered_at: Optional[datetime] = None
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
    dosage: Optional[str] = None
    next_dose_at: Optional[datetime] = None
    frequency: str

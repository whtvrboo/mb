"""Pets module ORM models."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import BaseModel, TimestampMixin


class PetSpecies(str):
    """Pet species."""

    DOG = "DOG"
    CAT = "CAT"
    BIRD = "BIRD"
    REPTILE = "REPTILE"
    FISH = "FISH"
    RODENT = "RODENT"
    OTHER = "OTHER"


class Sex(str):
    """Sex."""

    MALE = "MALE"
    FEMALE = "FEMALE"
    UNKNOWN = "UNKNOWN"


class MedicalRecordType(str):
    """Medical record types."""

    VACCINE = "VACCINE"
    SURGERY = "SURGERY"
    CHECKUP = "CHECKUP"
    MEDICATION = "MEDICATION"
    INJURY = "INJURY"
    ALLERGY = "ALLERGY"


class PetAction(str):
    """Pet log actions."""

    WALK = "WALK"
    FEED = "FEED"
    MEDICINE = "MEDICINE"
    GROOM = "GROOM"
    PLAY = "PLAY"
    VET_VISIT = "VET_VISIT"


class ScheduleFrequency(str):
    """Schedule frequency."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class Pet(BaseModel, TimestampMixin):
    """Pet - individual pet."""

    __tablename__ = "pets"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    species: Mapped[str] = mapped_column(String(20), nullable=False)
    breed: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sex: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(nullable=True)
    adoption_date: Mapped[datetime | None] = mapped_column(nullable=True)
    chip_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    color_markings: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vet_contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_contacts.id"), nullable=True
    )
    insurance_policy_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    insurance_provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    diet_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    medication_schedule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    special_needs: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_alive: Mapped[bool] = mapped_column(default=True, nullable=False)
    died_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    medical_records: Mapped[list["PetMedicalRecord"]] = relationship(
        "PetMedicalRecord", back_populates="pet", cascade="all, delete-orphan"
    )
    logs: Mapped[list["PetLog"]] = relationship(
        "PetLog", back_populates="pet", cascade="all, delete-orphan"
    )
    schedules: Mapped[list["PetSchedule"]] = relationship(
        "PetSchedule", back_populates="pet", cascade="all, delete-orphan"
    )


class PetMedicalRecord(BaseModel, TimestampMixin):
    """Pet medical record - vet visits, vaccines, etc."""

    __tablename__ = "pet_medical_records"

    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_at: Mapped[datetime] = mapped_column(nullable=False)
    performed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cost_expense_id: Mapped[int | None] = mapped_column(nullable=True)  # FK to expenses
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    reminder_days_before: Mapped[int | None] = mapped_column(nullable=True)
    document_id: Mapped[int | None] = mapped_column(nullable=True)  # FK to documents
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    pet: Mapped["Pet"] = relationship("Pet", back_populates="medical_records")


class PetLog(BaseModel, TimestampMixin):
    """Pet log - daily care activities."""

    __tablename__ = "pet_logs"

    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    value_amount: Mapped[float | None] = mapped_column(nullable=True)
    value_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    pet: Mapped["Pet"] = relationship("Pet", back_populates="logs")


class PetSchedule(BaseModel, TimestampMixin):
    """Pet schedule - recurring care tasks."""

    __tablename__ = "pet_schedules"

    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    frequency_type: Mapped[str] = mapped_column(String(20), nullable=False)
    time_of_day: Mapped[datetime | None] = mapped_column(nullable=True)  # TIME type
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_rotating: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    pet: Mapped["Pet"] = relationship("Pet", back_populates="schedules")

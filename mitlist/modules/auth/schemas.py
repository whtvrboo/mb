"""Auth module Pydantic schemas for request/response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field


# ====================
# User Schemas
# ====================
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    phone_number: str | None = Field(None, max_length=50)
    birth_date: datetime | None = None
    avatar_url: str | None = Field(None, max_length=500)
    language_code: str = Field("en", max_length=10)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: str | None = Field(None, min_length=1, max_length=255)
    phone_number: str | None = Field(None, max_length=50)
    birth_date: datetime | None = None
    avatar_url: str | None = Field(None, max_length=500)
    language_code: str | None = Field(None, max_length=10)
    preferences: dict[str, Any] | None = None


class UserResponse(UserBase):
    """Schema for user response - returned directly, no envelope."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_superuser: bool
    is_active: bool
    preferences: dict[str, Any] | None = None
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserLoginRequest(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(..., max_length=128)


class UserLoginResponse(BaseModel):
    """Schema for login response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ====================
# Group Schemas
# ====================
class GroupBase(BaseModel):
    """Base group schema."""

    name: str = Field(..., min_length=1, max_length=255)
    default_currency: str = Field("USD", max_length=3, pattern="^[A-Z]{3}$")
    timezone: str = Field("UTC", max_length=50)
    description: str | None = None
    avatar_url: str | None = Field(None, max_length=500)
    address: str | None = None


class GroupCreate(GroupBase):
    """Schema for creating a group."""

    lease_start_date: datetime | None = None
    lease_end_date: datetime | None = None


class GroupUpdate(BaseModel):
    """Schema for updating a group."""

    name: str | None = Field(None, min_length=1, max_length=255)
    default_currency: str | None = Field(None, max_length=3, pattern="^[A-Z]{3}$")
    timezone: str | None = Field(None, max_length=50)
    description: str | None = None
    avatar_url: str | None = Field(None, max_length=500)
    address: str | None = None
    lease_start_date: datetime | None = None
    lease_end_date: datetime | None = None
    landlord_contact_id: int | None = None


class GroupResponse(GroupBase):
    """Schema for group response - returned directly, no envelope."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: int
    lease_start_date: datetime | None = None
    lease_end_date: datetime | None = None
    landlord_contact_id: int | None = None
    created_at: datetime
    updated_at: datetime


# ====================
# UserGroup (Membership) Schemas
# ====================
class UserGroupBase(BaseModel):
    """Base user-group membership schema."""

    role: str = Field(..., pattern="^(ADMIN|MEMBER|GUEST|CHILD)$")
    nickname: str | None = Field(None, max_length=255)


class UserGroupCreate(UserGroupBase):
    """Schema for creating a user-group membership."""

    user_id: int
    group_id: int


class UserGroupCreate(BaseModel):
    """Schema for creating a user-group membership."""

    user_id: int
    role: str = Field("MEMBER", pattern="^(ADMIN|MEMBER|GUEST|CHILD)$")


class UserGroupUpdate(BaseModel):
    """Schema for updating a user-group membership."""

    role: str | None = Field(None, pattern="^(ADMIN|MEMBER|GUEST|CHILD)$")
    nickname: str | None = Field(None, max_length=255)


class UserGroupResponse(UserGroupBase):
    """Schema for user-group membership response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    group_id: int
    joined_at: datetime
    left_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class GroupMemberResponse(BaseModel):
    """Schema for group member with user details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role: str
    nickname: str | None = None
    joined_at: datetime
    user: UserResponse


# ====================
# Invite Schemas
# ====================
class InviteBase(BaseModel):
    """Base invite schema."""

    email_hint: str | None = Field(None, max_length=255)
    role: str = Field("MEMBER", pattern="^(ADMIN|MEMBER|GUEST|CHILD)$")
    max_uses: int = Field(1, ge=1)


class InviteCreate(InviteBase):
    """Schema for creating an invite."""

    group_id: int
    expires_at: datetime | None = None


class InviteCreateRequest(InviteBase):
    """Schema for creating an invite (group_id comes from path)."""

    expires_at: datetime | None = None


class InviteResponse(InviteBase):
    """Schema for invite response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_by_id: int
    code: str
    use_count: int
    expires_at: datetime | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def email(self) -> str | None:
        """Alias for email_hint."""
        return self.email_hint

    @computed_field
    @property
    def invite_code(self) -> str:
        """Alias for code."""
        return self.code

    @computed_field
    @property
    def status(self) -> str:
        """Status string."""
        return "PENDING" if self.is_active else "REVOKED"


class InviteAcceptRequest(BaseModel):
    """Schema for accepting an invite."""

    code: str = Field(..., max_length=100)


# ====================
# Location Schemas
# ====================
class LocationBase(BaseModel):
    """Base location schema."""

    name: str = Field(..., min_length=1, max_length=255)
    floor_level: int | None = None
    sunlight_direction: str | None = Field(None, pattern="^(NORTH|SOUTH|EAST|WEST)$")
    humidity_level: str | None = Field(None, pattern="^(LOW|MEDIUM|HIGH)$")
    temperature_avg_celsius: float | None = None
    notes: str | None = Field(None, max_length=1000)


class LocationCreate(LocationBase):
    """Schema for creating a location."""

    group_id: int


class LocationUpdate(BaseModel):
    """Schema for updating a location."""

    name: str | None = Field(None, min_length=1, max_length=255)
    floor_level: int | None = None
    sunlight_direction: str | None = Field(None, pattern="^(NORTH|SOUTH|EAST|WEST)$")
    humidity_level: str | None = Field(None, pattern="^(LOW|MEDIUM|HIGH)$")
    temperature_avg_celsius: float | None = None
    notes: str | None = Field(None, max_length=1000)


class LocationResponse(LocationBase):
    """Schema for location response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# ServiceContact Schemas
# ====================
class ServiceContactBase(BaseModel):
    """Base service contact schema."""

    name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(
        ...,
        pattern="^(VET|PLUMBER|ELECTRICIAN|DOCTOR|LANDLORD|CLEANER|HANDYMAN|OTHER)$",
    )
    company_name: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=500)
    website_url: str | None = Field(None, max_length=500)
    emergency_contact: bool = False
    notes: str | None = Field(None, max_length=1000)


class ServiceContactCreate(ServiceContactBase):
    """Schema for creating a service contact."""

    group_id: int


class ServiceContactUpdate(BaseModel):
    """Schema for updating a service contact."""

    name: str | None = Field(None, min_length=1, max_length=255)
    job_title: str | None = Field(
        None,
        pattern="^(VET|PLUMBER|ELECTRICIAN|DOCTOR|LANDLORD|CLEANER|HANDYMAN|OTHER)$",
    )
    company_name: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=500)
    website_url: str | None = Field(None, max_length=500)
    emergency_contact: bool | None = None
    notes: str | None = Field(None, max_length=1000)


class ServiceContactResponse(ServiceContactBase):
    """Schema for service contact response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# CommonItemConcept Schemas
# ====================
class CommonItemConceptBase(BaseModel):
    """Base common item concept schema."""

    name: str = Field(..., min_length=1, max_length=255)
    default_category_id: int | None = None
    barcode: str | None = Field(None, max_length=100)
    average_price: float | None = Field(None, ge=0)
    image_url: str | None = Field(None, max_length=500)


class CommonItemConceptCreate(CommonItemConceptBase):
    """Schema for creating a common item concept."""

    pass


class CommonItemConceptUpdate(BaseModel):
    """Schema for updating a common item concept."""

    name: str | None = Field(None, min_length=1, max_length=255)
    default_category_id: int | None = None
    barcode: str | None = Field(None, max_length=100)
    average_price: float | None = Field(None, ge=0)
    image_url: str | None = Field(None, max_length=500)


class CommonItemConceptResponse(CommonItemConceptBase):
    """Schema for common item concept response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

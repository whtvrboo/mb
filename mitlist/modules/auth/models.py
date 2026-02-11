"""Auth module - User, Group, and related identity models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, String, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import Base, BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    """User model with full identity fields."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    memberships: Mapped[list["UserGroup"]] = relationship(
        "UserGroup",
        primaryjoin="User.id==foreign(UserGroup.user_id)",
        viewonly=True,
    )


class Group(BaseModel, TimestampMixin):
    """Group model - household/roommate group."""

    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by_id: Mapped[int] = mapped_column(nullable=False)
    default_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lease_start_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    lease_end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    landlord_contact_id: Mapped[Optional[int]] = mapped_column(
        nullable=True
    )  # FK to service_contacts
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)


class UserGroup(BaseModel, TimestampMixin):
    """User-Group association with role and membership history."""

    __tablename__ = "user_groups"

    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    group_id: Mapped[int] = mapped_column(nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # ADMIN, MEMBER, GUEST, CHILD
    nickname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(nullable=False)
    left_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_user_group_active"),
        CheckConstraint("role IN ('ADMIN', 'MEMBER', 'GUEST', 'CHILD')", name="ck_user_group_role"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        primaryjoin="User.id==foreign(UserGroup.user_id)",
        viewonly=True,
    )


class Invite(BaseModel, TimestampMixin):
    """Group invitation with code and usage tracking."""

    __tablename__ = "invites"

    group_id: Mapped[int] = mapped_column(nullable=False, index=True)
    created_by_id: Mapped[int] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email_hint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="MEMBER", nullable=False)
    max_uses: Mapped[int] = mapped_column(default=1, nullable=False)
    use_count: Mapped[int] = mapped_column(default=0, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Location(BaseModel, TimestampMixin):
    """Location within a group (room, area) for plants/assets."""

    __tablename__ = "locations"

    group_id: Mapped[int] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    floor_level: Mapped[Optional[int]] = mapped_column(nullable=True)
    sunlight_direction: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # NORTH, SOUTH, etc.
    humidity_level: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # LOW, MEDIUM, HIGH
    temperature_avg_celsius: Mapped[Optional[float]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ServiceContact(BaseModel, TimestampMixin):
    """Service contact (vet, plumber, landlord, etc.)."""

    __tablename__ = "service_contacts"

    group_id: Mapped[int] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # VET, PLUMBER, LANDLORD, etc.
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    emergency_contact: Mapped[bool] = mapped_column(default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CommonItemConcept(BaseModel, TimestampMixin):
    """Common item concept - shared item definitions across groups."""

    __tablename__ = "common_item_concepts"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    default_category_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # FK to categories
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    average_price: Mapped[Optional[float]] = mapped_column(nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

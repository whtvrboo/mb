"""Auth module service layer - business logic. PRIVATE - other modules import from interface.py."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import ForbiddenError, NotFoundError, ValidationError
from mitlist.modules.auth.models import Group, Invite, Location, ServiceContact, User, UserGroup


def _now() -> datetime:
    return datetime.now(timezone.utc)()


# ---------- Users ----------
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession,
    user_id: int,
    name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    phone_number: Optional[str] = None,
    language_code: Optional[str] = None,
    preferences: Optional[dict] = None,
) -> User:
    """Update user profile."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(code="USER_NOT_FOUND", detail=f"User {user_id} not found")

    if name is not None:
        user.name = name
    if avatar_url is not None:
        user.avatar_url = avatar_url
    if phone_number is not None:
        user.phone_number = phone_number
    if language_code is not None:
        user.language_code = language_code
    if preferences is not None:
        user.preferences = preferences

    await db.flush()
    await db.refresh(user)
    return user


async def soft_delete_user(db: AsyncSession, user_id: int) -> None:
    """Soft delete a user account."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(code="USER_NOT_FOUND", detail=f"User {user_id} not found")

    user.deleted_at = _now()
    user.is_active = False
    # Anonymize email to allow re-registration
    user.email = f"deleted_{user_id}_{user.email}"
    await db.flush()


def _generate_invite_code() -> str:
    # urlsafe, short-ish; collisions extremely unlikely but still checked
    return secrets.token_urlsafe(18)


# ---------- Membership / authorization helpers ----------
async def get_membership(db: AsyncSession, group_id: int, user_id: int) -> Optional[UserGroup]:
    result = await db.execute(
        select(UserGroup).where(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def require_member(db: AsyncSession, group_id: int, user_id: int) -> UserGroup:
    ug = await get_membership(db, group_id, user_id)
    if not ug:
        raise ForbiddenError(code="NOT_A_MEMBER", detail="User is not a member of this group")
    return ug


async def require_admin(db: AsyncSession, group_id: int, user_id: int) -> UserGroup:
    ug = await require_member(db, group_id, user_id)
    if ug.role != "ADMIN":
        raise ForbiddenError(code="ADMIN_REQUIRED", detail="Admin role required for this action")
    return ug


# ---------- Groups ----------
async def list_groups_for_user(db: AsyncSession, user_id: int) -> list[Group]:
    result = await db.execute(
        select(Group)
        .join(UserGroup, UserGroup.group_id == Group.id)
        .where(UserGroup.user_id == user_id, Group.deleted_at.is_(None))
        .order_by(Group.id)
    )
    return list(result.scalars().all())


async def create_group(
    db: AsyncSession,
    created_by_id: int,
    name: str,
    default_currency: str = "USD",
    timezone: str = "UTC",
    description: Optional[str] = None,
    avatar_url: Optional[str] = None,
    address: Optional[str] = None,
    lease_start_date: Optional[datetime] = None,
    lease_end_date: Optional[datetime] = None,
) -> Group:
    group = Group(
        name=name,
        created_by_id=created_by_id,
        default_currency=default_currency,
        timezone=timezone,
        description=description,
        avatar_url=avatar_url,
        address=address,
        lease_start_date=lease_start_date,
        lease_end_date=lease_end_date,
    )
    db.add(group)
    await db.flush()
    await db.refresh(group)

    membership = UserGroup(
        user_id=created_by_id,
        group_id=group.id,
        role="ADMIN",
        nickname=None,
        joined_at=_now(),
        left_at=None,
    )
    db.add(membership)
    await db.flush()
    return group


async def get_group_by_id(db: AsyncSession, group_id: int) -> Optional[Group]:
    result = await db.execute(select(Group).where(Group.id == group_id, Group.deleted_at.is_(None)))
    return result.scalar_one_or_none()


async def update_group(
    db: AsyncSession,
    group_id: int,
    name: Optional[str] = None,
    default_currency: Optional[str] = None,
    timezone: Optional[str] = None,
    description: Optional[str] = None,
    avatar_url: Optional[str] = None,
    address: Optional[str] = None,
    lease_start_date: Optional[datetime] = None,
    lease_end_date: Optional[datetime] = None,
    landlord_contact_id: Optional[int] = None,
) -> Group:
    result = await db.execute(select(Group).where(Group.id == group_id, Group.deleted_at.is_(None)))
    group = result.scalar_one_or_none()
    if not group:
        raise NotFoundError(code="GROUP_NOT_FOUND", detail=f"Group {group_id} not found")

    if name is not None:
        group.name = name
    if default_currency is not None:
        group.default_currency = default_currency
    if timezone is not None:
        group.timezone = timezone
    if description is not None:
        group.description = description
    if avatar_url is not None:
        group.avatar_url = avatar_url
    if address is not None:
        group.address = address
    if lease_start_date is not None:
        group.lease_start_date = lease_start_date
    if lease_end_date is not None:
        group.lease_end_date = lease_end_date
    if landlord_contact_id is not None:
        group.landlord_contact_id = landlord_contact_id

    await db.flush()
    await db.refresh(group)
    return group


async def soft_delete_group(db: AsyncSession, group_id: int) -> None:
    result = await db.execute(select(Group).where(Group.id == group_id, Group.deleted_at.is_(None)))
    group = result.scalar_one_or_none()
    if not group:
        raise NotFoundError(code="GROUP_NOT_FOUND", detail=f"Group {group_id} not found")
    group.deleted_at = _now()
    await db.flush()


async def list_group_members(db: AsyncSession, group_id: int) -> list[UserGroup]:
    # Load membership + embedded user for API response
    result = await db.execute(
        select(UserGroup)
        .options(selectinload(UserGroup.user))
        .where(UserGroup.group_id == group_id)
        .order_by(UserGroup.id)
    )
    return list(result.scalars().all())


async def update_member(
    db: AsyncSession,
    group_id: int,
    user_id: int,
    role: Optional[str] = None,
    nickname: Optional[str] = None,
) -> UserGroup:
    result = await db.execute(
        select(UserGroup).where(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )
    ug = result.scalar_one_or_none()
    if not ug:
        raise NotFoundError(code="MEMBER_NOT_FOUND", detail="Membership not found")
    if role is not None:
        ug.role = role
    if nickname is not None:
        ug.nickname = nickname
    await db.flush()
    await db.refresh(ug)
    return ug


async def remove_member(db: AsyncSession, group_id: int, user_id: int) -> None:
    result = await db.execute(
        select(UserGroup).where(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )
    ug = result.scalar_one_or_none()
    if not ug:
        raise NotFoundError(code="MEMBER_NOT_FOUND", detail="Membership not found")
    await db.delete(ug)
    await db.flush()


async def leave_group(db: AsyncSession, group_id: int, user_id: int) -> None:
    # Delete membership row (unique constraint does not allow historical duplicates)
    await remove_member(db, group_id, user_id)


# ---------- Invites ----------
async def create_invite(
    db: AsyncSession,
    group_id: int,
    created_by_id: int,
    role: str = "MEMBER",
    email_hint: Optional[str] = None,
    max_uses: int = 1,
    expires_at: Optional[datetime] = None,
) -> Invite:
    if max_uses < 1:
        raise ValidationError(code="INVALID_MAX_USES", detail="max_uses must be >= 1")

    # Ensure unique code
    for _ in range(5):
        code = _generate_invite_code()
        existing = await db.execute(select(Invite).where(Invite.code == code))
        if existing.scalar_one_or_none() is None:
            invite = Invite(
                group_id=group_id,
                created_by_id=created_by_id,
                code=code,
                email_hint=email_hint,
                role=role,
                max_uses=max_uses,
                use_count=0,
                expires_at=expires_at,
                is_active=True,
            )
            db.add(invite)
            await db.flush()
            await db.refresh(invite)
            return invite

    raise ValidationError(code="INVITE_CODE_GENERATION_FAILED", detail="Could not generate invite code")


def _invite_is_valid(invite: Invite) -> bool:
    if not invite.is_active:
        return False
    if invite.expires_at is not None and invite.expires_at <= _now():
        return False
    if invite.use_count >= invite.max_uses:
        return False
    return True


async def get_invite_by_code(db: AsyncSession, code: str) -> Optional[Invite]:
    result = await db.execute(select(Invite).where(Invite.code == code))
    return result.scalar_one_or_none()

async def get_invite_by_id(db: AsyncSession, invite_id: int) -> Optional[Invite]:
    result = await db.execute(select(Invite).where(Invite.id == invite_id))
    return result.scalar_one_or_none()


async def require_valid_invite(db: AsyncSession, code: str) -> Invite:
    invite = await get_invite_by_code(db, code)
    if not invite or not _invite_is_valid(invite):
        raise NotFoundError(code="INVITE_INVALID", detail="Invite code is invalid or expired")
    return invite


async def accept_invite(db: AsyncSession, code: str, user_id: int) -> UserGroup:
    invite = await require_valid_invite(db, code)

    # Ensure not already a member
    existing = await get_membership(db, invite.group_id, user_id)
    if existing:
        return existing

    ug = UserGroup(
        user_id=user_id,
        group_id=invite.group_id,
        role=invite.role,
        nickname=None,
        joined_at=_now(),
        left_at=None,
    )
    db.add(ug)

    invite.use_count += 1
    if invite.use_count >= invite.max_uses:
        invite.is_active = False
    await db.flush()
    await db.refresh(ug)
    return ug


async def revoke_invite(db: AsyncSession, invite_id: int) -> Invite:
    result = await db.execute(select(Invite).where(Invite.id == invite_id))
    invite = result.scalar_one_or_none()
    if not invite:
        raise NotFoundError(code="INVITE_NOT_FOUND", detail=f"Invite {invite_id} not found")
    invite.is_active = False
    await db.flush()
    await db.refresh(invite)
    return invite


async def list_invites_for_group(db: AsyncSession, group_id: int) -> list[Invite]:
    """List invites for a group."""
    result = await db.execute(
        select(Invite)
        .where(Invite.group_id == group_id)
        .order_by(Invite.created_at.desc())
    )
    return list(result.scalars().all())


async def add_member(
    db: AsyncSession,
    group_id: int,
    user_id: int,
    role: str = "MEMBER",
) -> UserGroup:
    """Add a member to a group directly (without invite)."""
    # Check if already a member
    existing = await get_membership(db, group_id, user_id)
    if existing:
        raise ValidationError(code="ALREADY_MEMBER", detail="User is already a member of this group")
    
    ug = UserGroup(
        user_id=user_id,
        group_id=group_id,
        role=role,
        nickname=None,
        joined_at=_now(),
        left_at=None,
    )
    db.add(ug)
    await db.flush()
    await db.refresh(ug)
    return ug


# ---------- Locations ----------
async def list_locations(db: AsyncSession, group_id: int) -> list[Location]:
    """List locations for a group."""
    result = await db.execute(
        select(Location).where(Location.group_id == group_id).order_by(Location.name)
    )
    return list(result.scalars().all())


async def get_location_by_id(db: AsyncSession, location_id: int) -> Optional[Location]:
    """Get location by ID."""
    result = await db.execute(select(Location).where(Location.id == location_id))
    return result.scalar_one_or_none()


async def create_location(
    db: AsyncSession,
    group_id: int,
    name: str,
    floor_level: Optional[int] = None,
    sunlight_direction: Optional[str] = None,
    humidity_level: Optional[str] = None,
    temperature_avg_celsius: Optional[float] = None,
    notes: Optional[str] = None,
) -> Location:
    """Create a new location."""
    location = Location(
        group_id=group_id,
        name=name,
        floor_level=floor_level,
        sunlight_direction=sunlight_direction,
        humidity_level=humidity_level,
        temperature_avg_celsius=temperature_avg_celsius,
        notes=notes,
    )
    db.add(location)
    await db.flush()
    await db.refresh(location)
    return location


async def update_location(
    db: AsyncSession,
    location_id: int,
    name: Optional[str] = None,
    floor_level: Optional[int] = None,
    sunlight_direction: Optional[str] = None,
    humidity_level: Optional[str] = None,
    temperature_avg_celsius: Optional[float] = None,
    notes: Optional[str] = None,
) -> Location:
    """Update a location."""
    location = await get_location_by_id(db, location_id)
    if not location:
        raise NotFoundError(code="LOCATION_NOT_FOUND", detail=f"Location {location_id} not found")

    if name is not None:
        location.name = name
    if floor_level is not None:
        location.floor_level = floor_level
    if sunlight_direction is not None:
        location.sunlight_direction = sunlight_direction
    if humidity_level is not None:
        location.humidity_level = humidity_level
    if temperature_avg_celsius is not None:
        location.temperature_avg_celsius = temperature_avg_celsius
    if notes is not None:
        location.notes = notes

    await db.flush()
    await db.refresh(location)
    return location


async def delete_location(db: AsyncSession, location_id: int) -> None:
    """Delete a location."""
    location = await get_location_by_id(db, location_id)
    if not location:
        raise NotFoundError(code="LOCATION_NOT_FOUND", detail=f"Location {location_id} not found")
    await db.delete(location)
    await db.flush()


# ---------- Service Contacts ----------
async def list_service_contacts(db: AsyncSession, group_id: int) -> list[ServiceContact]:
    """List service contacts for a group."""
    result = await db.execute(
        select(ServiceContact).where(ServiceContact.group_id == group_id).order_by(ServiceContact.name)
    )
    return list(result.scalars().all())


async def get_service_contact_by_id(db: AsyncSession, contact_id: int) -> Optional[ServiceContact]:
    """Get service contact by ID."""
    result = await db.execute(select(ServiceContact).where(ServiceContact.id == contact_id))
    return result.scalar_one_or_none()


async def create_service_contact(
    db: AsyncSession,
    group_id: int,
    name: str,
    job_title: str,
    company_name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
    website_url: Optional[str] = None,
    emergency_contact: bool = False,
    notes: Optional[str] = None,
) -> ServiceContact:
    """Create a new service contact."""
    contact = ServiceContact(
        group_id=group_id,
        name=name,
        job_title=job_title,
        company_name=company_name,
        phone=phone,
        email=email,
        address=address,
        website_url=website_url,
        emergency_contact=emergency_contact,
        notes=notes,
    )
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    return contact


async def update_service_contact(
    db: AsyncSession,
    contact_id: int,
    name: Optional[str] = None,
    job_title: Optional[str] = None,
    company_name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
    website_url: Optional[str] = None,
    emergency_contact: Optional[bool] = None,
    notes: Optional[str] = None,
) -> ServiceContact:
    """Update a service contact."""
    contact = await get_service_contact_by_id(db, contact_id)
    if not contact:
        raise NotFoundError(code="SERVICE_CONTACT_NOT_FOUND", detail=f"Service contact {contact_id} not found")

    if name is not None:
        contact.name = name
    if job_title is not None:
        contact.job_title = job_title
    if company_name is not None:
        contact.company_name = company_name
    if phone is not None:
        contact.phone = phone
    if email is not None:
        contact.email = email
    if address is not None:
        contact.address = address
    if website_url is not None:
        contact.website_url = website_url
    if emergency_contact is not None:
        contact.emergency_contact = emergency_contact
    if notes is not None:
        contact.notes = notes

    await db.flush()
    await db.refresh(contact)
    return contact


async def delete_service_contact(db: AsyncSession, contact_id: int) -> None:
    """Delete a service contact."""
    contact = await get_service_contact_by_id(db, contact_id)
    if not contact:
        raise NotFoundError(code="SERVICE_CONTACT_NOT_FOUND", detail=f"Service contact {contact_id} not found")
    await db.delete(contact)
    await db.flush()

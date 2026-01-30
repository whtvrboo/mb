"""Auth & Identity module FastAPI router. Handles /auth, /users, /groups, /invites."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.api.deps import get_current_user
from mitlist.api.deps import require_introspection_user
from mitlist.core.errors import GoneError, NotFoundError
from mitlist.modules.auth import interface, schemas

router = APIRouter(tags=["auth", "users", "groups", "invites"])


def _gone(msg: str):
    raise GoneError(code="USE_ZITADEL_OIDC", detail=msg)


# ---------- Auth ----------
@router.post("/auth/register")
async def auth_register(data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    _gone("Local auth is disabled. Use Zitadel OIDC to obtain an access token.")


@router.post("/auth/login", response_model=schemas.UserLoginResponse)
async def auth_login(data: schemas.UserLoginRequest, db: AsyncSession = Depends(get_db)):
    _gone("Local auth is disabled. Use Zitadel OIDC to obtain an access token.")


@router.post("/auth/refresh")
async def auth_refresh(db: AsyncSession = Depends(get_db)):
    _gone("Local auth is disabled. Use Zitadel OIDC refresh flow in your client.")


@router.post("/auth/logout")
async def auth_logout(db: AsyncSession = Depends(get_db)):
    _gone("Local auth is disabled. Use Zitadel logout/end-session flow in your client.")


@router.post("/auth/password-reset-request")
async def auth_password_reset_request(db: AsyncSession = Depends(get_db)):
    _gone("Local auth is disabled. Use Zitadel password reset flows.")


@router.post("/auth/password-reset-confirm")
async def auth_password_reset_confirm(db: AsyncSession = Depends(get_db)):
    _gone("Local auth is disabled. Use Zitadel password reset flows.")


# ---------- Users ----------
@router.get("/users/me", response_model=schemas.UserResponse)
async def get_users_me(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.UserResponse:
    return schemas.UserResponse.model_validate(user)


@router.patch("/users/me", response_model=schemas.UserResponse)
async def patch_users_me(
    data: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.UserResponse:
    """Update the current user's profile."""
    updated_user = await interface.update_user(
        db,
        user_id=user.id,
        name=data.name,
        avatar_url=data.avatar_url,
        phone_number=data.phone_number,
        language_code=data.language_code,
        preferences=data.preferences,
    )
    return schemas.UserResponse.model_validate(updated_user)


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_introspection_user),
):
    """Delete (soft) the current user's account. Requires re-authentication."""
    await interface.soft_delete_user(db, user.id)


# ---------- Groups ----------
@router.get("/groups", response_model=list[schemas.GroupResponse])
async def get_groups(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[schemas.GroupResponse]:
    groups = await interface.list_groups_for_user(db, user.id)
    return [schemas.GroupResponse.model_validate(g) for g in groups]


@router.post("/groups", response_model=schemas.GroupResponse, status_code=status.HTTP_201_CREATED)
async def post_groups(
    data: schemas.GroupCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.GroupResponse:
    group = await interface.create_group(
        db,
        created_by_id=user.id,
        name=data.name,
        default_currency=data.default_currency,
        timezone=data.timezone,
        description=data.description,
        avatar_url=data.avatar_url,
        address=data.address,
        lease_start_date=data.lease_start_date,
        lease_end_date=data.lease_end_date,
    )
    return schemas.GroupResponse.model_validate(group)


@router.get("/groups/{group_id}", response_model=schemas.GroupResponse)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.GroupResponse:
    await interface.require_member(db, group_id, user.id)
    group = await interface.get_group_by_id(db, group_id)
    if not group:
        raise NotFoundError(code="GROUP_NOT_FOUND", detail=f"Group {group_id} not found")
    return schemas.GroupResponse.model_validate(group)


@router.patch("/groups/{group_id}", response_model=schemas.GroupResponse)
async def patch_group(
    group_id: int,
    data: schemas.GroupUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.GroupResponse:
    await interface.require_admin(db, group_id, user.id)
    group = await interface.update_group(
        db,
        group_id=group_id,
        name=data.name,
        default_currency=data.default_currency,
        timezone=data.timezone,
        description=data.description,
        avatar_url=data.avatar_url,
        address=data.address,
        lease_start_date=data.lease_start_date,
        lease_end_date=data.lease_end_date,
        landlord_contact_id=data.landlord_contact_id,
    )
    return schemas.GroupResponse.model_validate(group)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_introspection_user),
):
    await interface.require_admin(db, group_id, _user.id)
    await interface.soft_delete_group(db, group_id)


@router.get("/groups/{group_id}/members", response_model=list[schemas.GroupMemberResponse])
async def get_group_members(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[schemas.GroupMemberResponse]:
    await interface.require_member(db, group_id, user.id)
    members = await interface.list_group_members(db, group_id)
    return [schemas.GroupMemberResponse.model_validate(m) for m in members]


@router.patch("/groups/{group_id}/members/{user_id}", response_model=schemas.UserGroupResponse)
async def patch_group_member(
    group_id: int,
    user_id: int,
    data: schemas.UserGroupUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.UserGroupResponse:
    await interface.require_admin(db, group_id, user.id)
    ug = await interface.update_member(db, group_id, user_id, role=data.role, nickname=data.nickname)
    return schemas.UserGroupResponse.model_validate(ug)


@router.delete("/groups/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_member(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    await interface.require_admin(db, group_id, user.id)
    await interface.remove_member(db, group_id, user_id)


@router.post("/groups/{group_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def post_groups_leave(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    await interface.leave_group(db, group_id, user.id)


# ---------- Invites ----------
@router.post("/invites", response_model=schemas.InviteResponse, status_code=status.HTTP_201_CREATED)
async def post_invites(
    data: schemas.InviteCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.InviteResponse:
    await interface.require_admin(db, data.group_id, user.id)
    invite = await interface.create_invite(
        db,
        group_id=data.group_id,
        created_by_id=user.id,
        role=data.role,
        email_hint=data.email_hint,
        max_uses=data.max_uses,
        expires_at=data.expires_at,
    )
    return schemas.InviteResponse.model_validate(invite)


@router.get("/invites/{code}", response_model=schemas.InviteResponse)
async def get_invites_code(code: str, db: AsyncSession = Depends(get_db)):
    # Note: this endpoint is intentionally public to allow clients to check codes
    invite = await interface.require_valid_invite(db, code)
    return schemas.InviteResponse.model_validate(invite)


@router.post("/invites/join")
async def post_invites_join(
    data: schemas.InviteAcceptRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> schemas.UserGroupResponse:
    ug = await interface.accept_invite(db, data.code, user.id)
    return schemas.UserGroupResponse.model_validate(ug)


@router.delete("/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite(
    invite_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    invite = await interface.get_invite_by_id(db, invite_id)
    if not invite:
        raise NotFoundError(code="INVITE_NOT_FOUND", detail=f"Invite {invite_id} not found")
    # only admins of that invite's group can revoke it
    await interface.require_admin(db, invite.group_id, user.id)
    await interface.revoke_invite(db, invite_id)


# ---------- Locations (System & Ops) ----------
@router.get("/locations", response_model=list[schemas.LocationResponse])
async def get_locations(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """List locations for a group."""
    await interface.require_member(db, group_id, user.id)
    locations = await interface.list_locations(db, group_id)
    return [schemas.LocationResponse.model_validate(loc) for loc in locations]


@router.post("/locations", response_model=schemas.LocationResponse, status_code=status.HTTP_201_CREATED)
async def post_locations(
    data: schemas.LocationCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a new location."""
    await interface.require_member(db, data.group_id, user.id)
    location = await interface.create_location(
        db,
        group_id=data.group_id,
        name=data.name,
        floor_level=data.floor_level,
        sunlight_direction=data.sunlight_direction,
        humidity_level=data.humidity_level,
        temperature_avg_celsius=data.temperature_avg_celsius,
        notes=data.notes,
    )
    return schemas.LocationResponse.model_validate(location)


@router.get("/locations/{location_id}", response_model=schemas.LocationResponse)
async def get_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get a location by ID."""
    location = await interface.get_location_by_id(db, location_id)
    if not location:
        raise NotFoundError(code="LOCATION_NOT_FOUND", detail=f"Location {location_id} not found")
    await interface.require_member(db, location.group_id, user.id)
    return schemas.LocationResponse.model_validate(location)


@router.patch("/locations/{location_id}", response_model=schemas.LocationResponse)
async def patch_location(
    location_id: int,
    data: schemas.LocationUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Update a location."""
    location = await interface.get_location_by_id(db, location_id)
    if not location:
        raise NotFoundError(code="LOCATION_NOT_FOUND", detail=f"Location {location_id} not found")
    await interface.require_member(db, location.group_id, user.id)
    location = await interface.update_location(
        db,
        location_id=location_id,
        name=data.name,
        floor_level=data.floor_level,
        sunlight_direction=data.sunlight_direction,
        humidity_level=data.humidity_level,
        temperature_avg_celsius=data.temperature_avg_celsius,
        notes=data.notes,
    )
    return schemas.LocationResponse.model_validate(location)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Delete a location."""
    location = await interface.get_location_by_id(db, location_id)
    if not location:
        raise NotFoundError(code="LOCATION_NOT_FOUND", detail=f"Location {location_id} not found")
    await interface.require_admin(db, location.group_id, user.id)
    await interface.delete_location(db, location_id)


# ---------- Service contacts ----------
@router.get("/service-contacts", response_model=list[schemas.ServiceContactResponse])
async def get_service_contacts(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """List service contacts for a group."""
    await interface.require_member(db, group_id, user.id)
    contacts = await interface.list_service_contacts(db, group_id)
    return [schemas.ServiceContactResponse.model_validate(c) for c in contacts]


@router.post("/service-contacts", response_model=schemas.ServiceContactResponse, status_code=status.HTTP_201_CREATED)
async def post_service_contacts(
    data: schemas.ServiceContactCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a new service contact."""
    await interface.require_member(db, data.group_id, user.id)
    contact = await interface.create_service_contact(
        db,
        group_id=data.group_id,
        name=data.name,
        job_title=data.job_title,
        company_name=data.company_name,
        phone=data.phone,
        email=data.email,
        address=data.address,
        website_url=data.website_url,
        emergency_contact=data.emergency_contact,
        notes=data.notes,
    )
    return schemas.ServiceContactResponse.model_validate(contact)


@router.get("/service-contacts/{contact_id}", response_model=schemas.ServiceContactResponse)
async def get_service_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get a service contact by ID."""
    contact = await interface.get_service_contact_by_id(db, contact_id)
    if not contact:
        raise NotFoundError(code="SERVICE_CONTACT_NOT_FOUND", detail=f"Service contact {contact_id} not found")
    await interface.require_member(db, contact.group_id, user.id)
    return schemas.ServiceContactResponse.model_validate(contact)


@router.patch("/service-contacts/{contact_id}", response_model=schemas.ServiceContactResponse)
async def patch_service_contact(
    contact_id: int,
    data: schemas.ServiceContactUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Update a service contact."""
    contact = await interface.get_service_contact_by_id(db, contact_id)
    if not contact:
        raise NotFoundError(code="SERVICE_CONTACT_NOT_FOUND", detail=f"Service contact {contact_id} not found")
    await interface.require_member(db, contact.group_id, user.id)
    contact = await interface.update_service_contact(
        db,
        contact_id=contact_id,
        name=data.name,
        job_title=data.job_title,
        company_name=data.company_name,
        phone=data.phone,
        email=data.email,
        address=data.address,
        website_url=data.website_url,
        emergency_contact=data.emergency_contact,
        notes=data.notes,
    )
    return schemas.ServiceContactResponse.model_validate(contact)


@router.delete("/service-contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Delete a service contact."""
    contact = await interface.get_service_contact_by_id(db, contact_id)
    if not contact:
        raise NotFoundError(code="SERVICE_CONTACT_NOT_FOUND", detail=f"Service contact {contact_id} not found")
    await interface.require_admin(db, contact.group_id, user.id)
    await interface.delete_service_contact(db, contact_id)

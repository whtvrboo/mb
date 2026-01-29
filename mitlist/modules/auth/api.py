"""Auth & Identity module FastAPI router. Handles /auth, /users, /groups, /invites."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.api.deps import require_introspection_user
from mitlist.core.errors import GoneError, NotImplementedAppError
from mitlist.modules.auth import schemas

router = APIRouter(tags=["auth", "users", "groups", "invites"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)

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
async def get_users_me(db: AsyncSession = Depends(get_db)):
    _stub("GET /users/me is not yet implemented")


@router.patch("/users/me", response_model=schemas.UserResponse)
async def patch_users_me(data: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    _stub("PATCH /users/me is not yet implemented")


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me(
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_introspection_user),
):
    _stub("DELETE /users/me is not yet implemented")


# ---------- Groups ----------
@router.get("/groups", response_model=list[schemas.GroupResponse])
async def get_groups(db: AsyncSession = Depends(get_db)):
    _stub("GET /groups is not yet implemented")


@router.post("/groups", response_model=schemas.GroupResponse, status_code=status.HTTP_201_CREATED)
async def post_groups(data: schemas.GroupCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /groups is not yet implemented")


@router.get("/groups/{group_id}", response_model=schemas.GroupResponse)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /groups/{id} is not yet implemented")


@router.patch("/groups/{group_id}", response_model=schemas.GroupResponse)
async def patch_group(group_id: int, data: schemas.GroupUpdate, db: AsyncSession = Depends(get_db)):
    _stub("PATCH /groups/{id} is not yet implemented")


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_introspection_user),
):
    _stub("DELETE /groups/{id} is not yet implemented")


@router.get("/groups/{group_id}/members", response_model=list[schemas.GroupMemberResponse])
async def get_group_members(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /groups/{id}/members is not yet implemented")


@router.patch("/groups/{group_id}/members/{user_id}", response_model=schemas.UserGroupResponse)
async def patch_group_member(group_id: int, user_id: int, data: schemas.UserGroupUpdate, db: AsyncSession = Depends(get_db)):
    _stub("PATCH /groups/{id}/members/{user_id} is not yet implemented")


@router.delete("/groups/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_member(group_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    _stub("DELETE /groups/{id}/members/{user_id} is not yet implemented")


@router.post("/groups/{group_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def post_groups_leave(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("POST /groups/{id}/leave is not yet implemented")


# ---------- Invites ----------
@router.post("/invites", response_model=schemas.InviteResponse, status_code=status.HTTP_201_CREATED)
async def post_invites(data: schemas.InviteCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /invites is not yet implemented")


@router.get("/invites/{code}", response_model=schemas.InviteResponse)
async def get_invites_code(code: str, db: AsyncSession = Depends(get_db)):
    _stub("GET /invites/{code} is not yet implemented")


@router.post("/invites/join")
async def post_invites_join(data: schemas.InviteAcceptRequest, db: AsyncSession = Depends(get_db)):
    _stub("POST /invites/join is not yet implemented")


@router.delete("/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite(invite_id: int, db: AsyncSession = Depends(get_db)):
    _stub("DELETE /invites/{id} is not yet implemented")


# ---------- Locations (System & Ops) ----------
@router.get("/locations", response_model=list[schemas.LocationResponse])
async def get_locations(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /locations is not yet implemented")


@router.post("/locations", response_model=schemas.LocationResponse, status_code=status.HTTP_201_CREATED)
async def post_locations(data: schemas.LocationCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /locations is not yet implemented")


# ---------- Service contacts ----------
@router.get("/service-contacts", response_model=list[schemas.ServiceContactResponse])
async def get_service_contacts(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /service-contacts is not yet implemented")


@router.post("/service-contacts", response_model=schemas.ServiceContactResponse, status_code=status.HTTP_201_CREATED)
async def post_service_contacts(data: schemas.ServiceContactCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /service-contacts is not yet implemented")

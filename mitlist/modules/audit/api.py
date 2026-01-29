"""Audit & admin module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.api.deps import require_introspection_user
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.audit import schemas

router = APIRouter(prefix="/admin", tags=["audit", "admin"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/system-stats")
async def get_admin_system_stats(db: AsyncSession = Depends(get_db)):
    _stub("GET /admin/system-stats is not yet implemented")


@router.post("/broadcast", status_code=status.HTTP_204_NO_CONTENT)
async def post_admin_broadcast(
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_introspection_user),
):
    _stub("POST /admin/broadcast is not yet implemented")


@router.get("/audit-trail", response_model=ListType[schemas.AuditLogResponse])
async def get_admin_audit_trail(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /admin/audit-trail is not yet implemented")


@router.post("/maintenance-mode", status_code=status.HTTP_204_NO_CONTENT)
async def post_admin_maintenance_mode(
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_introspection_user),
):
    _stub("POST /admin/maintenance-mode is not yet implemented")

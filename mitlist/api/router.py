"""Main API router aggregator."""

from fastapi import APIRouter, Depends

from mitlist.api import health, system
from mitlist.api.deps import get_current_user
from mitlist.modules.assets import api as assets_api
from mitlist.modules.audit import api as audit_api
from mitlist.modules.auth import api as auth_api
from mitlist.modules.calendar import api as calendar_api
from mitlist.modules.chores import api as chores_api
from mitlist.modules.documents import api as documents_api
from mitlist.modules.finance import api as finance_api
from mitlist.modules.gamification import api as gamification_api
from mitlist.modules.governance import api as governance_api
from mitlist.modules.lists import api as lists_api
from mitlist.modules.notifications import api as notifications_api
from mitlist.modules.pets import api as pets_api
from mitlist.modules.plants import api as plants_api
from mitlist.modules.recipes import api as recipes_api

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include health check routes (no version prefix)
health_router = APIRouter()
health_router.include_router(health.router, prefix="/health")

# Include module routers
api_router.include_router(auth_api.router)
api_router.include_router(system.router, dependencies=[Depends(get_current_user)])
api_router.include_router(assets_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(audit_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(calendar_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(chores_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(documents_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(finance_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(gamification_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(governance_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(lists_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(lists_api.inventory_router, dependencies=[Depends(get_current_user)])
api_router.include_router(notifications_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(notifications_api.comments_router, dependencies=[Depends(get_current_user)])
api_router.include_router(notifications_api.reactions_router, dependencies=[Depends(get_current_user)])
api_router.include_router(pets_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(plants_api.router, dependencies=[Depends(get_current_user)])
api_router.include_router(recipes_api.router, dependencies=[Depends(get_current_user)])

__all__ = ["api_router", "health_router"]

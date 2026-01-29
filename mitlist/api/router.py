"""Main API router aggregator."""

from fastapi import APIRouter

from mitlist.api import health
from mitlist.modules.lists import api as lists_api

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include health check routes (no version prefix)
health_router = APIRouter()
health_router.include_router(health.router, prefix="/health")

# Include module routers
api_router.include_router(lists_api.router)

__all__ = ["api_router", "health_router"]

"""
API routes for the Hospital Operations Platform
"""

from fastapi import APIRouter
from .endpoints import agents, beds, equipment, staff, supplies, health

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["agents"]
)

api_router.include_router(
    beds.router,
    prefix="/beds",
    tags=["bed-management"]
)

api_router.include_router(
    equipment.router,
    prefix="/equipment",
    tags=["equipment-tracking"]
)

api_router.include_router(
    staff.router,
    prefix="/staff",
    tags=["staff-allocation"]
)

api_router.include_router(
    supplies.router,
    prefix="/supplies",
    tags=["supply-inventory"]
)

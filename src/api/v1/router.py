"""
Main router for API v1.

Combines all v1 API routes under a single router.
"""

from fastapi import APIRouter

from src.api.v1.auth import router as auth_router
from src.api.v1.contact import admin_router as contact_admin_router
from src.api.v1.contact import public_router as contact_public_router
from src.api.v1.content import admin_router as content_admin_router
from src.api.v1.content import public_router as content_public_router
from src.api.v1.game import router as game_router
from src.api.v1.health import router as health_router
from src.api.v1.quests import router as quests_router
from src.api.v1.users import router as users_router

api_v1_router = APIRouter()

# Include all routers
api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users_router, prefix="/users", tags=["Users"])
api_v1_router.include_router(game_router, prefix="/game", tags=["Game"])
api_v1_router.include_router(quests_router, prefix="/quests", tags=["Quests"])
api_v1_router.include_router(content_admin_router, prefix="/admin/content", tags=["Content Admin"])
api_v1_router.include_router(content_public_router, prefix="/content", tags=["Content"])
api_v1_router.include_router(contact_public_router, tags=["Contact"])
api_v1_router.include_router(contact_admin_router, tags=["Contact Admin"])

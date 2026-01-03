"""Content API endpoints package."""

from src.api.v1.content.admin import router as admin_router
from src.api.v1.content.public import router as public_router

__all__ = ["admin_router", "public_router"]

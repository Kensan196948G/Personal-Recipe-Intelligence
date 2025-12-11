"""
API Routers Package
"""

from backend.api.routers.recipes import router as recipes_router
from backend.api.routers.tags import router as tags_router

__all__ = ["recipes_router", "tags_router"]

"""
API Routers Package
"""

from backend.api.routers.ocr import router as ocr_router
from backend.api.routers.recipes import router as recipes_router
from backend.api.routers.scraper import router as scraper_router
from backend.api.routers.search import router as search_router
from backend.api.routers.tags import router as tags_router
from backend.api.routers.translation import router as translation_router

__all__ = [
    "recipes_router",
    "tags_router",
    "scraper_router",
    "ocr_router",
    "translation_router",
    "search_router",
]

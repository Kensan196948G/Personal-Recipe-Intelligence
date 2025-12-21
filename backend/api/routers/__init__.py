"""
API Routers Package
"""

from .cache import router as cache_router
from .nutrition import router as nutrition_router
from .ocr import router as ocr_router
from .recipes import router as recipes_router
from .scraper import router as scraper_router
from .search import router as search_router
from .shopping_list import router as shopping_list_router
from .tags import router as tags_router
from .translation import router as translation_router

__all__ = [
    "recipes_router",
    "tags_router",
    "scraper_router",
    "ocr_router",
    "translation_router",
    "search_router",
    "cache_router",
    "nutrition_router",
    "shopping_list_router",
]

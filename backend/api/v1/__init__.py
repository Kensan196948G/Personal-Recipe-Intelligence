"""
API v1 Package

All v1 API routers with rate limiting.
"""

from .ocr import router as ocr_router
from .video import router as video_router
from .scraper import router as scraper_router
from .recipes import router as recipes_router

__all__ = [
  "ocr_router",
  "video_router",
  "scraper_router",
  "recipes_router",
]

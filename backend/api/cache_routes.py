"""
Cache management API routes.

This module provides endpoints for cache monitoring and management.
"""

from typing import Dict, Any
from backend.core.cache import get_cache_stats, clear_all_cache, invalidate_cache


def register_cache_routes(app):
  """
  Register cache-related routes to the application.

  Args:
    app: FastAPI or Flask application instance

  Note:
    This is a framework-agnostic implementation.
    Adapt based on your chosen framework (FastAPI/Flask).
  """

  # Example for FastAPI:
  # @app.get("/api/v1/cache/stats")
  # async def cache_stats():

  # Example for Flask:
  # @app.route("/api/v1/cache/stats", methods=["GET"])
  # def cache_stats():

  pass


def get_cache_stats_handler() -> Dict[str, Any]:
  """
  Get cache statistics.

  Returns:
    Dictionary containing cache statistics
  """
  stats = get_cache_stats()

  return {
    "status": "ok",
    "data": stats,
    "error": None,
  }


def clear_cache_handler() -> Dict[str, Any]:
  """
  Clear all cache entries.

  Returns:
    Success response
  """
  clear_all_cache()

  return {
    "status": "ok",
    "data": {"message": "Cache cleared successfully"},
    "error": None,
  }


def invalidate_cache_handler(pattern: str) -> Dict[str, Any]:
  """
  Invalidate cache entries matching a pattern.

  Args:
    pattern: Pattern to match

  Returns:
    Response with number of invalidated entries
  """
  count = invalidate_cache(pattern)

  return {
    "status": "ok",
    "data": {
      "message": f"Invalidated {count} cache entries",
      "count": count,
    },
    "error": None,
  }


# FastAPI example implementation
"""
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/cache", tags=["cache"])

@router.get("/stats")
async def get_stats():
  return get_cache_stats_handler()

@router.post("/clear")
async def clear_cache():
  return clear_cache_handler()

@router.post("/invalidate")
async def invalidate(pattern: str = Query(..., description="Pattern to match")):
  return invalidate_cache_handler(pattern)
"""

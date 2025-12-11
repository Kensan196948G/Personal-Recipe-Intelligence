"""
Cache configuration for Personal Recipe Intelligence.

This module defines cache TTL settings and policies for different
operation types.
"""

from typing import Dict


class CacheConfig:
  """Cache configuration settings."""

  # Default TTL values in seconds
  DEFAULT_TTL = 60

  # TTL for different operation types
  TTL_RECIPE_LIST = 60  # Recipe list queries
  TTL_RECIPE_DETAIL = 120  # Individual recipe details
  TTL_SEARCH = 30  # Search results
  TTL_NUTRITION = 300  # Nutrition calculations (expensive)
  TTL_TAGS = 300  # Tag lists (stable)
  TTL_STATS = 600  # Statistics and aggregations (very expensive)
  TTL_USER_PREFS = 60  # User preferences

  # Cache key prefixes
  PREFIX_RECIPES = "recipes"
  PREFIX_SEARCH = "search"
  PREFIX_NUTRITION = "nutrition"
  PREFIX_TAGS = "tags"
  PREFIX_STATS = "stats"
  PREFIX_USER = "user"

  # Performance settings
  MAX_CACHE_SIZE = 10000  # Maximum number of entries
  CLEANUP_INTERVAL = 300  # Cleanup expired entries every 5 minutes

  # Monitoring settings
  ENABLE_STATS = True  # Enable cache statistics
  LOG_HIT_RATE_THRESHOLD = 50.0  # Log warning if hit rate below this

  @classmethod
  def get_ttl_for_operation(cls, operation_type: str) -> int:
    """
    Get TTL for a specific operation type.

    Args:
      operation_type: Type of operation (e.g., 'recipe_list', 'search')

    Returns:
      TTL in seconds
    """
    ttl_mapping: Dict[str, int] = {
      "recipe_list": cls.TTL_RECIPE_LIST,
      "recipe_detail": cls.TTL_RECIPE_DETAIL,
      "search": cls.TTL_SEARCH,
      "nutrition": cls.TTL_NUTRITION,
      "tags": cls.TTL_TAGS,
      "stats": cls.TTL_STATS,
      "user_prefs": cls.TTL_USER_PREFS,
    }

    return ttl_mapping.get(operation_type, cls.DEFAULT_TTL)

  @classmethod
  def get_prefix_for_operation(cls, operation_type: str) -> str:
    """
    Get cache key prefix for a specific operation type.

    Args:
      operation_type: Type of operation

    Returns:
      Cache key prefix
    """
    prefix_mapping: Dict[str, str] = {
      "recipe_list": cls.PREFIX_RECIPES,
      "recipe_detail": cls.PREFIX_RECIPES,
      "search": cls.PREFIX_SEARCH,
      "nutrition": cls.PREFIX_NUTRITION,
      "tags": cls.PREFIX_TAGS,
      "stats": cls.PREFIX_STATS,
      "user_prefs": cls.PREFIX_USER,
    }

    return prefix_mapping.get(operation_type, "default")

  @classmethod
  def should_cache_operation(cls, operation_type: str) -> bool:
    """
    Determine if an operation should be cached.

    Args:
      operation_type: Type of operation

    Returns:
      True if operation should be cached
    """
    # Don't cache sensitive or user-specific operations with long TTL
    no_cache_operations = [
      "login",
      "logout",
      "private_data",
    ]

    return operation_type not in no_cache_operations


# Environment-specific overrides
# You can override these values via environment variables or .env file

def load_cache_config_from_env():
  """
  Load cache configuration from environment variables.

  This allows overriding default values without code changes.
  """
  import os

  config_overrides = {}

  # Check for TTL overrides
  ttl_vars = {
    "CACHE_TTL_RECIPE_LIST": "TTL_RECIPE_LIST",
    "CACHE_TTL_SEARCH": "TTL_SEARCH",
    "CACHE_TTL_NUTRITION": "TTL_NUTRITION",
    "CACHE_TTL_TAGS": "TTL_TAGS",
  }

  for env_var, config_attr in ttl_vars.items():
    value = os.getenv(env_var)
    if value:
      try:
        config_overrides[config_attr] = int(value)
      except ValueError:
        pass  # Ignore invalid values

  # Apply overrides
  for attr, value in config_overrides.items():
    setattr(CacheConfig, attr, value)

  return config_overrides


# Usage example with decorator
"""
from backend.core.cache import cached
from config.cache_config import CacheConfig

@cached(
  ttl=CacheConfig.TTL_RECIPE_LIST,
  key_prefix=CacheConfig.PREFIX_RECIPES
)
def get_recipes(limit: int = 50) -> list:
  return database.query_recipes(limit)
"""

# Dynamic configuration based on operation type
"""
from backend.core.cache import cached
from config.cache_config import CacheConfig

def cache_for_operation(operation_type: str):
  return cached(
    ttl=CacheConfig.get_ttl_for_operation(operation_type),
    key_prefix=CacheConfig.get_prefix_for_operation(operation_type)
  )

@cache_for_operation("recipe_list")
def get_recipes(limit: int = 50) -> list:
  return database.query_recipes(limit)
"""

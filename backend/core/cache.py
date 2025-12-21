"""
Lightweight in-memory TTL cache implementation for Personal Recipe Intelligence.

This module provides a simple TTL-based cache without external dependencies
like Redis, suitable for personal use.
"""

import time
import functools
import hashlib
import json
from typing import Any, Callable, Dict, Optional, Tuple
from datetime import datetime
from threading import Lock


class CacheEntry:
  """Represents a single cache entry with TTL."""

  def __init__(self, value: Any, ttl: int):
    """
    Initialize cache entry.

    Args:
      value: The cached value
      ttl: Time to live in seconds
    """
    self.value = value
    self.created_at = time.time()
    self.ttl = ttl
    self.hits = 0

  def is_expired(self) -> bool:
    """Check if the cache entry has expired."""
    return time.time() - self.created_at > self.ttl

  def get_age(self) -> float:
    """Get the age of the cache entry in seconds."""
    return time.time() - self.created_at


class TTLCache:
  """Thread-safe in-memory TTL cache."""

  def __init__(self):
    """Initialize the cache."""
    self._cache: Dict[str, CacheEntry] = {}
    self._lock = Lock()
    self._stats = {
      "hits": 0,
      "misses": 0,
      "evictions": 0,
      "sets": 0,
    }

  def _generate_key(self, key: Any) -> str:
    """
    Generate a cache key from any hashable input.

    Args:
      key: The key to hash

    Returns:
      Hash string
    """
    if isinstance(key, str):
      return key

    # Convert to JSON and hash for complex objects
    key_str = json.dumps(key, sort_keys=True, default=str)
    return hashlib.sha256(key_str.encode()).hexdigest()

  def get(self, key: Any) -> Optional[Any]:
    """
    Get a value from the cache.

    Args:
      key: Cache key

    Returns:
      Cached value or None if not found or expired
    """
    cache_key = self._generate_key(key)

    with self._lock:
      if cache_key not in self._cache:
        self._stats["misses"] += 1
        return None

      entry = self._cache[cache_key]

      if entry.is_expired():
        del self._cache[cache_key]
        self._stats["misses"] += 1
        self._stats["evictions"] += 1
        return None

      entry.hits += 1
      self._stats["hits"] += 1
      return entry.value

  def set(self, key: Any, value: Any, ttl: int = 60) -> None:
    """
    Set a value in the cache with TTL.

    Args:
      key: Cache key
      value: Value to cache
      ttl: Time to live in seconds (default: 60)
    """
    cache_key = self._generate_key(key)

    with self._lock:
      self._cache[cache_key] = CacheEntry(value, ttl)
      self._stats["sets"] += 1

  def delete(self, key: Any) -> bool:
    """
    Delete a specific key from the cache.

    Args:
      key: Cache key

    Returns:
      True if key was deleted, False if not found
    """
    cache_key = self._generate_key(key)

    with self._lock:
      if cache_key in self._cache:
        del self._cache[cache_key]
        self._stats["evictions"] += 1
        return True
      return False

  def clear(self) -> None:
    """Clear all cache entries."""
    with self._lock:
      count = len(self._cache)
      self._cache.clear()
      self._stats["evictions"] += count

  def invalidate_pattern(self, pattern: str) -> int:
    """
    Invalidate all keys matching a pattern.

    Args:
      pattern: String pattern to match (simple substring match)

    Returns:
      Number of keys invalidated
    """
    with self._lock:
      keys_to_delete = [
        key for key in self._cache.keys()
        if pattern in key
      ]

      for key in keys_to_delete:
        del self._cache[key]
        self._stats["evictions"] += 1

      return len(keys_to_delete)

  def cleanup_expired(self) -> int:
    """
    Remove all expired entries from the cache.

    Returns:
      Number of entries removed
    """
    with self._lock:
      expired_keys = [
        key for key, entry in self._cache.items()
        if entry.is_expired()
      ]

      for key in expired_keys:
        del self._cache[key]
        self._stats["evictions"] += 1

      return len(expired_keys)

  def get_stats(self) -> Dict[str, Any]:
    """
    Get cache statistics.

    Returns:
      Dictionary containing cache stats
    """
    with self._lock:
      total_requests = self._stats["hits"] + self._stats["misses"]
      hit_rate = (
        self._stats["hits"] / total_requests * 100
        if total_requests > 0
        else 0
      )

      entries_info = []
      for key, entry in self._cache.items():
        entries_info.append({
          "key": key[:16] + "..." if len(key) > 16 else key,
          "age": round(entry.get_age(), 2),
          "ttl": entry.ttl,
          "hits": entry.hits,
        })

      return {
        "total_entries": len(self._cache),
        "hits": self._stats["hits"],
        "misses": self._stats["misses"],
        "evictions": self._stats["evictions"],
        "sets": self._stats["sets"],
        "hit_rate": round(hit_rate, 2),
        "entries": sorted(entries_info, key=lambda x: x["hits"], reverse=True)[:10],
      }

  def get_size(self) -> int:
    """Get the current number of entries in the cache."""
    with self._lock:
      return len(self._cache)


# Global cache instance
_global_cache = TTLCache()


def get_cache() -> TTLCache:
  """
  Get the global cache instance.

  Returns:
    Global TTLCache instance
  """
  return _global_cache


def cached(ttl: int = 60, key_prefix: str = ""):
  """
  Decorator to cache function results with TTL.

  Args:
    ttl: Time to live in seconds (default: 60)
    key_prefix: Optional prefix for cache keys

  Returns:
    Decorated function

  Example:
    @cached(ttl=300, key_prefix="nutrition")
    def calculate_nutrition(recipe_id: int) -> dict:
      # expensive calculation
      return result
  """
  def decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
      # Generate cache key from function name and arguments
      key_parts = [key_prefix, func.__name__]

      # Add args to key
      if args:
        key_parts.extend([str(arg) for arg in args])

      # Add kwargs to key
      if kwargs:
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])

      cache_key = ":".join(filter(None, key_parts))

      # Try to get from cache
      cache = get_cache()
      cached_value = cache.get(cache_key)

      if cached_value is not None:
        return cached_value

      # Execute function and cache result
      result = func(*args, **kwargs)
      cache.set(cache_key, result, ttl)

      return result

    # Add cache management methods to the wrapper
    wrapper.cache_clear = lambda: get_cache().invalidate_pattern(f"{key_prefix}:{func.__name__}")
    wrapper.cache_key_prefix = f"{key_prefix}:{func.__name__}"

    return wrapper

  return decorator


def invalidate_cache(pattern: str) -> int:
  """
  Invalidate cache entries matching a pattern.

  Args:
    pattern: Pattern to match

  Returns:
    Number of invalidated entries
  """
  return get_cache().invalidate_pattern(pattern)


def clear_all_cache() -> None:
  """Clear all cache entries."""
  get_cache().clear()


def get_cache_stats() -> Dict[str, Any]:
  """
  Get cache statistics.

  Returns:
    Cache statistics dictionary
  """
  return get_cache().get_stats()

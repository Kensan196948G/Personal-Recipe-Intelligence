"""
Lightweight caching implementation for Personal Recipe Intelligence
Per CLAUDE.md Section 12.2: Lightweight cache only
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Tuple, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class TTLCache:
    """
    Time-To-Live cache with automatic expiration.
    Lightweight in-memory cache suitable for personal use.
    """

    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Initialize TTL cache.

        Args:
            ttl_seconds: Time to live for cached items (default: 5 minutes)
            max_size: Maximum number of items to cache
        """
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        if key in self._cache:
            value, timestamp = self._cache[key]

            # Check if expired
            if datetime.now() - timestamp < timedelta(seconds=self._ttl):
                self._hits += 1
                logger.debug(f"Cache HIT: {key}")
                return value
            else:
                # Remove expired entry
                del self._cache[key]
                logger.debug(f"Cache EXPIRED: {key}")

        self._misses += 1
        logger.debug(f"Cache MISS: {key}")
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Set cached value with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Enforce max size by removing oldest entry
        if len(self._cache) >= self._max_size and key not in self._cache:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug(f"Cache EVICT: {oldest_key} (max size reached)")

        self._cache[key] = (value, datetime.now())
        logger.debug(f"Cache SET: {key}")

    def invalidate(self, key: str) -> None:
        """
        Remove specific key from cache.

        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache INVALIDATE: {key}")

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.

        Args:
            pattern: String pattern to match (simple substring match)

        Returns:
            Number of keys invalidated
        """
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            logger.info(f"Cache INVALIDATE PATTERN: {pattern} ({len(keys_to_remove)} keys)")

        return len(keys_to_remove)

    def clear(self) -> None:
        """Clear all cached items."""
        count = len(self._cache)
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info(f"Cache CLEAR: {count} items removed")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with hits, misses, hit_rate, size
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "size": len(self._cache),
            "max_size": self._max_size,
        }


def cached(ttl_seconds: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results with TTL.

    Args:
        ttl_seconds: Time to live for cached results
        key_func: Optional function to generate cache key from args

    Example:
        @cached(ttl_seconds=300)
        async def get_recipe(recipe_id: int):
            return await fetch_recipe_from_db(recipe_id)

        @cached(ttl_seconds=60, key_func=lambda url: f"scrape:{url}")
        async def scrape_recipe(url: str):
            return await fetch_recipe_from_url(url)
    """
    cache = TTLCache(ttl_seconds=ttl_seconds)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Simple key from function name and first arg
                cache_key = f"{func.__name__}:{args[0] if args else 'no_args'}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{args[0] if args else 'no_args'}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result)

            return result

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Global cache instances for common use cases
recipe_cache = TTLCache(ttl_seconds=300, max_size=500)  # 5 minutes, 500 recipes
ingredient_cache = TTLCache(ttl_seconds=600, max_size=1000)  # 10 minutes, 1000 ingredients
scraping_cache = TTLCache(ttl_seconds=3600, max_size=100)  # 1 hour, 100 URLs


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics for all global caches.

    Returns:
        Dict with stats for each cache
    """
    return {
        "recipe_cache": recipe_cache.get_stats(),
        "ingredient_cache": ingredient_cache.get_stats(),
        "scraping_cache": scraping_cache.get_stats(),
    }

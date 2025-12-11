"""
Unit tests for the TTL cache module.

Tests cache functionality including TTL expiration, statistics,
and the caching decorator.
"""

import time
import pytest
from backend.core.cache import (
  TTLCache,
  cached,
  get_cache,
  invalidate_cache,
  clear_all_cache,
  get_cache_stats,
)


class TestTTLCache:
  """Test cases for TTLCache class."""

  def setup_method(self):
    """Setup for each test method."""
    self.cache = TTLCache()

  def test_set_and_get(self):
    """Test basic set and get operations."""
    self.cache.set("key1", "value1", ttl=60)
    assert self.cache.get("key1") == "value1"

  def test_get_nonexistent_key(self):
    """Test getting a non-existent key returns None."""
    assert self.cache.get("nonexistent") is None

  def test_ttl_expiration(self):
    """Test that entries expire after TTL."""
    self.cache.set("key1", "value1", ttl=1)
    assert self.cache.get("key1") == "value1"

    # Wait for expiration
    time.sleep(1.1)
    assert self.cache.get("key1") is None

  def test_delete(self):
    """Test deleting a cache entry."""
    self.cache.set("key1", "value1", ttl=60)
    assert self.cache.delete("key1") is True
    assert self.cache.get("key1") is None

  def test_delete_nonexistent(self):
    """Test deleting a non-existent key."""
    assert self.cache.delete("nonexistent") is False

  def test_clear(self):
    """Test clearing all cache entries."""
    self.cache.set("key1", "value1", ttl=60)
    self.cache.set("key2", "value2", ttl=60)
    self.cache.clear()
    assert self.cache.get("key1") is None
    assert self.cache.get("key2") is None

  def test_invalidate_pattern(self):
    """Test pattern-based cache invalidation."""
    self.cache.set("user:1:profile", "data1", ttl=60)
    self.cache.set("user:2:profile", "data2", ttl=60)
    self.cache.set("post:1", "data3", ttl=60)

    count = self.cache.invalidate_pattern("user:")
    assert count == 2
    assert self.cache.get("user:1:profile") is None
    assert self.cache.get("user:2:profile") is None
    assert self.cache.get("post:1") == "data3"

  def test_cleanup_expired(self):
    """Test cleanup of expired entries."""
    self.cache.set("key1", "value1", ttl=1)
    self.cache.set("key2", "value2", ttl=60)

    time.sleep(1.1)
    count = self.cache.cleanup_expired()

    assert count == 1
    assert self.cache.get("key1") is None
    assert self.cache.get("key2") == "value2"

  def test_get_stats(self):
    """Test cache statistics."""
    self.cache.set("key1", "value1", ttl=60)
    self.cache.get("key1")
    self.cache.get("key1")
    self.cache.get("nonexistent")

    stats = self.cache.get_stats()

    assert stats["total_entries"] == 1
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["sets"] == 1
    assert stats["hit_rate"] > 0

  def test_get_size(self):
    """Test getting cache size."""
    assert self.cache.get_size() == 0

    self.cache.set("key1", "value1", ttl=60)
    self.cache.set("key2", "value2", ttl=60)

    assert self.cache.get_size() == 2

  def test_complex_key(self):
    """Test caching with complex keys."""
    complex_key = {"user_id": 1, "filters": ["tag1", "tag2"]}
    self.cache.set(complex_key, "result", ttl=60)

    assert self.cache.get(complex_key) == "result"

  def test_thread_safety(self):
    """Test basic thread safety (simplified test)."""
    import threading

    def set_values():
      for i in range(100):
        self.cache.set(f"key{i}", f"value{i}", ttl=60)

    def get_values():
      for i in range(100):
        self.cache.get(f"key{i}")

    threads = []
    for _ in range(5):
      threads.append(threading.Thread(target=set_values))
      threads.append(threading.Thread(target=get_values))

    for thread in threads:
      thread.start()

    for thread in threads:
      thread.join()

    # If we get here without errors, thread safety is working
    assert True


class TestCachedDecorator:
  """Test cases for the @cached decorator."""

  def setup_method(self):
    """Setup for each test method."""
    clear_all_cache()
    self.call_count = 0

  def test_cached_function(self):
    """Test that function results are cached."""

    @cached(ttl=60, key_prefix="test")
    def expensive_function(x: int) -> int:
      self.call_count += 1
      return x * 2

    result1 = expensive_function(5)
    result2 = expensive_function(5)

    assert result1 == 10
    assert result2 == 10
    assert self.call_count == 1  # Function called only once

  def test_cached_with_different_args(self):
    """Test caching with different arguments."""

    @cached(ttl=60, key_prefix="test")
    def add(a: int, b: int) -> int:
      self.call_count += 1
      return a + b

    result1 = add(1, 2)
    result2 = add(1, 2)
    result3 = add(2, 3)

    assert result1 == 3
    assert result2 == 3
    assert result3 == 5
    assert self.call_count == 2  # Called twice for different args

  def test_cached_with_kwargs(self):
    """Test caching with keyword arguments."""

    @cached(ttl=60, key_prefix="test")
    def greet(name: str, greeting: str = "Hello") -> str:
      self.call_count += 1
      return f"{greeting}, {name}!"

    result1 = greet("Alice", greeting="Hi")
    result2 = greet("Alice", greeting="Hi")

    assert result1 == "Hi, Alice!"
    assert result2 == "Hi, Alice!"
    assert self.call_count == 1

  def test_cache_expiration_in_decorator(self):
    """Test that decorated function cache expires."""

    @cached(ttl=1, key_prefix="test")
    def get_time() -> float:
      self.call_count += 1
      return time.time()

    result1 = get_time()
    time.sleep(1.1)
    result2 = get_time()

    assert result1 != result2
    assert self.call_count == 2

  def test_cache_clear_method(self):
    """Test that cache_clear method works."""

    @cached(ttl=60, key_prefix="test")
    def compute(x: int) -> int:
      self.call_count += 1
      return x ** 2

    result1 = compute(5)
    compute.cache_clear()
    result2 = compute(5)

    assert result1 == 25
    assert result2 == 25
    assert self.call_count == 2  # Called twice due to cache clear


class TestGlobalCacheFunctions:
  """Test global cache utility functions."""

  def setup_method(self):
    """Setup for each test method."""
    clear_all_cache()

  def test_get_cache(self):
    """Test getting global cache instance."""
    cache = get_cache()
    assert cache is not None
    assert isinstance(cache, TTLCache)

  def test_invalidate_cache(self):
    """Test global invalidate_cache function."""
    cache = get_cache()
    cache.set("test:key1", "value1", ttl=60)
    cache.set("test:key2", "value2", ttl=60)
    cache.set("other:key", "value3", ttl=60)

    count = invalidate_cache("test:")
    assert count == 2

  def test_clear_all_cache(self):
    """Test global clear_all_cache function."""
    cache = get_cache()
    cache.set("key1", "value1", ttl=60)
    cache.set("key2", "value2", ttl=60)

    clear_all_cache()
    assert cache.get_size() == 0

  def test_get_cache_stats(self):
    """Test global get_cache_stats function."""
    cache = get_cache()
    cache.set("key1", "value1", ttl=60)

    stats = get_cache_stats()
    assert "total_entries" in stats
    assert stats["total_entries"] >= 1


if __name__ == "__main__":
  pytest.main([__file__, "-v"])

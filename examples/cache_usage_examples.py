"""
Cache Usage Examples for Personal Recipe Intelligence.

This file demonstrates various caching patterns and best practices
for the PRI project.
"""

from typing import List, Dict, Any, Optional
from backend.core.cache import cached, get_cache, invalidate_cache


# Example 1: Simple Function Caching
# ===================================

@cached(ttl=60, key_prefix="recipes")
def get_all_recipes() -> List[Dict[str, Any]]:
  """
  Get all recipes with 60-second cache.

  This is the simplest caching pattern - just add the decorator.
  """
  print("Executing expensive database query...")
  # Simulated database query
  return [
    {"id": 1, "title": "Recipe 1"},
    {"id": 2, "title": "Recipe 2"},
  ]


# Example 2: Caching with Parameters
# ===================================

@cached(ttl=30, key_prefix="search")
def search_by_tag(tag: str, limit: int = 10) -> List[Dict[str, Any]]:
  """
  Search recipes by tag with parameter-based cache keys.

  Each unique combination of (tag, limit) creates a separate cache entry.
  """
  print(f"Searching for tag: {tag}, limit: {limit}")
  # Simulated search
  return []


# Example 3: Expensive Computation Caching
# =========================================

@cached(ttl=300, key_prefix="nutrition")
def calculate_recipe_nutrition(recipe_id: int) -> Dict[str, float]:
  """
  Calculate nutrition info with long TTL (5 minutes).

  Use longer TTL for expensive computations that rarely change.
  """
  print(f"Calculating nutrition for recipe {recipe_id}...")
  # Simulated expensive calculation
  return {
    "calories": 450.0,
    "protein": 25.0,
    "carbs": 55.0,
    "fat": 12.0,
  }


# Example 4: Manual Cache Control
# ================================

def get_recipe_with_manual_cache(recipe_id: int) -> Optional[Dict[str, Any]]:
  """
  Demonstrate manual cache control for complex scenarios.

  Use this when you need fine-grained control over caching logic.
  """
  cache = get_cache()
  cache_key = f"recipe:{recipe_id}"

  # Try to get from cache
  cached_recipe = cache.get(cache_key)
  if cached_recipe is not None:
    print(f"Cache hit for recipe {recipe_id}")
    return cached_recipe

  print(f"Cache miss for recipe {recipe_id}, fetching from database...")

  # Simulated database fetch
  recipe = {
    "id": recipe_id,
    "title": f"Recipe {recipe_id}",
    "ingredients": ["ingredient1", "ingredient2"],
  }

  # Store in cache with custom TTL
  cache.set(cache_key, recipe, ttl=120)

  return recipe


# Example 5: Cache Invalidation on Write
# =======================================

def create_recipe(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
  """
  Create recipe and invalidate affected caches.

  Always invalidate caches when data changes to prevent stale data.
  """
  print("Creating recipe in database...")

  # Simulated database insert
  new_recipe = {
    "id": 999,
    **recipe_data,
    "created_at": "2025-12-11T12:00:00Z",
  }

  # Invalidate all recipe list caches
  invalidate_cache("recipes:get_all_recipes")

  # If recipe has tags, invalidate search caches
  if "tags" in recipe_data:
    invalidate_cache("search:search_by_tag")

  print(f"Invalidated caches after creating recipe {new_recipe['id']}")

  return new_recipe


def update_recipe(recipe_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
  """
  Update recipe and invalidate specific caches.

  Be surgical with invalidation - only clear what's affected.
  """
  print(f"Updating recipe {recipe_id}...")

  # Simulated database update
  updated_recipe = {"id": recipe_id, **updates}

  # Invalidate specific recipe cache
  cache = get_cache()
  cache.delete(f"recipe:{recipe_id}")

  # Invalidate nutrition cache if ingredients changed
  if "ingredients" in updates:
    invalidate_cache(f"nutrition:calculate_recipe_nutrition:{recipe_id}")

  # Invalidate list caches
  invalidate_cache("recipes:get_all_recipes")

  # Invalidate search if tags changed
  if "tags" in updates:
    invalidate_cache("search:search_by_tag")

  print(f"Invalidated caches after updating recipe {recipe_id}")

  return updated_recipe


# Example 6: Conditional Caching
# ===============================

def get_user_recipes(user_id: int, include_private: bool = False) -> List[Dict[str, Any]]:
  """
  Demonstrate conditional caching based on parameters.

  Don't cache sensitive or user-specific data with long TTL.
  """
  cache = get_cache()

  # Only cache public recipe lists
  if not include_private:
    cache_key = f"user_recipes:{user_id}:public"
    cached_recipes = cache.get(cache_key)

    if cached_recipes is not None:
      return cached_recipes

    # Fetch public recipes
    recipes = []  # Simulated query

    # Cache for 60 seconds
    cache.set(cache_key, recipes, ttl=60)
    return recipes

  else:
    # Don't cache private data - fetch fresh every time
    print(f"Fetching private recipes for user {user_id} (no cache)")
    return []  # Simulated query


# Example 7: Cache Warming
# =========================

def warm_common_caches():
  """
  Pre-populate cache with commonly accessed data.

  Call this on application startup or after cache clear.
  """
  print("Warming caches with common data...")

  # Pre-fetch common queries
  get_all_recipes()

  # Pre-calculate nutrition for popular recipes
  for recipe_id in [1, 2, 3, 4, 5]:
    calculate_recipe_nutrition(recipe_id)

  # Pre-fetch common searches
  for tag in ["quick", "healthy", "japanese"]:
    search_by_tag(tag)

  print("Cache warming complete")


# Example 8: Monitoring Cache Performance
# ========================================

def print_cache_performance():
  """
  Display cache performance metrics.

  Call this periodically or expose via admin endpoint.
  """
  from backend.core.cache import get_cache_stats

  stats = get_cache_stats()

  print("\n=== Cache Performance ===")
  print(f"Total Entries: {stats['total_entries']}")
  print(f"Hit Rate: {stats['hit_rate']:.2f}%")
  print(f"Hits: {stats['hits']}")
  print(f"Misses: {stats['misses']}")
  print(f"Evictions: {stats['evictions']}")

  print("\nTop Cached Items:")
  for entry in stats['entries'][:5]:
    print(f"  {entry['key']}: {entry['hits']} hits, {entry['age']:.1f}s old")


# Example 9: Bulk Operations with Cache
# ======================================

def get_multiple_recipes(recipe_ids: List[int]) -> List[Dict[str, Any]]:
  """
  Efficiently fetch multiple recipes using cache.

  Check cache first, then batch-fetch missing items.
  """
  cache = get_cache()
  results = []
  missing_ids = []

  # Check cache for each recipe
  for recipe_id in recipe_ids:
    cache_key = f"recipe:{recipe_id}"
    cached_recipe = cache.get(cache_key)

    if cached_recipe is not None:
      results.append(cached_recipe)
    else:
      missing_ids.append(recipe_id)

  # Batch fetch missing recipes
  if missing_ids:
    print(f"Fetching {len(missing_ids)} recipes from database...")
    # Simulated batch query
    fetched_recipes = [
      {"id": rid, "title": f"Recipe {rid}"}
      for rid in missing_ids
    ]

    # Cache the fetched recipes
    for recipe in fetched_recipes:
      cache_key = f"recipe:{recipe['id']}"
      cache.set(cache_key, recipe, ttl=120)

    results.extend(fetched_recipes)

  return results


# Example 10: Testing with Cache
# ===============================

def example_test_with_cache():
  """
  Demonstrate how to test code that uses caching.

  Always clear cache before tests to ensure isolation.
  """
  from backend.core.cache import clear_all_cache

  # Clear cache before test
  clear_all_cache()

  # Test cache miss (first call)
  result1 = get_all_recipes()
  assert len(result1) > 0

  # Test cache hit (second call)
  result2 = get_all_recipes()
  assert result1 == result2

  # Test cache invalidation
  create_recipe({"title": "New Recipe"})

  # After invalidation, should fetch fresh data
  result3 = get_all_recipes()

  print("All cache tests passed!")


# Main demonstration
# ==================

if __name__ == "__main__":
  print("=== Cache Usage Examples ===\n")

  # Example 1: Basic caching
  print("1. Basic function caching:")
  recipes1 = get_all_recipes()  # Cache miss
  recipes2 = get_all_recipes()  # Cache hit
  print()

  # Example 2: Parameter-based caching
  print("2. Parameter-based caching:")
  search_by_tag("italian", limit=5)  # Cache miss
  search_by_tag("italian", limit=5)  # Cache hit
  search_by_tag("japanese", limit=5)  # Different params = cache miss
  print()

  # Example 3: Expensive computation
  print("3. Expensive computation caching:")
  nutrition1 = calculate_recipe_nutrition(1)  # Cache miss
  nutrition2 = calculate_recipe_nutrition(1)  # Cache hit
  print()

  # Example 4: Manual cache control
  print("4. Manual cache control:")
  recipe1 = get_recipe_with_manual_cache(1)  # Cache miss
  recipe2 = get_recipe_with_manual_cache(1)  # Cache hit
  print()

  # Example 5: Cache invalidation
  print("5. Cache invalidation on write:")
  new_recipe = create_recipe({"title": "Pasta", "tags": ["italian"]})
  print()

  # Example 8: Performance monitoring
  print_cache_performance()

  print("\n=== Examples Complete ===")

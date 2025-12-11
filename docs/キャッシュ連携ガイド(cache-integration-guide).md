# Cache Integration Guide

## Quick Start

This guide helps you integrate the TTL cache into existing Personal Recipe Intelligence code.

## Installation

No external dependencies required - the cache is pure Python.

## Step 1: Import the Cache

```python
from backend.core.cache import cached, invalidate_cache, get_cache
```

## Step 2: Add Caching to Functions

### Option A: Using the @cached Decorator (Recommended)

```python
from backend.core.cache import cached

@cached(ttl=60, key_prefix="recipes")
def get_recipes(limit: int = 50) -> List[dict]:
  # Your existing code here
  return database.query_recipes(limit)
```

### Option B: Manual Cache Control

```python
from backend.core.cache import get_cache

def get_recipe(recipe_id: int) -> dict:
  cache = get_cache()
  cache_key = f"recipe:{recipe_id}"

  # Check cache
  cached_value = cache.get(cache_key)
  if cached_value:
    return cached_value

  # Fetch from database
  recipe = database.get_recipe(recipe_id)

  # Store in cache
  cache.set(cache_key, recipe, ttl=120)

  return recipe
```

## Step 3: Invalidate Cache on Data Changes

```python
from backend.core.cache import invalidate_cache

def update_recipe(recipe_id: int, data: dict) -> dict:
  # Update database
  recipe = database.update_recipe(recipe_id, data)

  # Invalidate affected caches
  invalidate_cache("recipes:get_recipes")
  invalidate_cache(f"recipe:{recipe_id}")

  return recipe
```

## Integration Checklist

### For Read Operations (GET endpoints)

- [ ] Identify slow database queries (> 100ms)
- [ ] Add @cached decorator with appropriate TTL
- [ ] Choose TTL based on data freshness requirements
- [ ] Test cache hit/miss behavior

### For Write Operations (POST/PUT/DELETE endpoints)

- [ ] Identify which caches are affected
- [ ] Add invalidate_cache() calls after data changes
- [ ] Use pattern matching for related caches
- [ ] Verify cache invalidation works correctly

### For API Endpoints

- [ ] Add cache stats endpoint for monitoring
- [ ] Consider adding cache clear endpoint (admin only)
- [ ] Document cache behavior in API docs

## Recommended TTL Values

| Data Type | TTL | Reasoning |
|-----------|-----|-----------|
| Recipe lists | 60s | Balance between freshness and performance |
| Individual recipes | 120s | Updated less frequently |
| Search results | 30s | Users expect fresh results |
| Nutrition calculations | 300s | Expensive, rarely changes |
| Tag lists | 300s | Very stable data |
| User preferences | 60s | Personal data, moderate TTL |
| Statistics/aggregations | 600s | Expensive queries, can be slightly stale |

## Common Patterns

### Pattern 1: List Endpoints with Pagination

```python
@cached(ttl=60, key_prefix="recipes")
def get_recipe_list(limit: int, offset: int, sort_by: str) -> List[dict]:
  # Cache automatically includes all parameters in the key
  return database.get_recipes(limit=limit, offset=offset, sort_by=sort_by)
```

### Pattern 2: Search Endpoints

```python
@cached(ttl=30, key_prefix="search")
def search_recipes(query: str, filters: dict) -> List[dict]:
  return database.search(query, filters)

# Invalidate on any recipe change
def on_recipe_change():
  invalidate_cache("search:search_recipes")
```

### Pattern 3: Expensive Calculations

```python
@cached(ttl=300, key_prefix="nutrition")
def calculate_nutrition(recipe_id: int) -> dict:
  # Expensive calculation
  ingredients = get_recipe_ingredients(recipe_id)
  return nutrition_calculator.calculate(ingredients)

# Invalidate only when recipe ingredients change
def update_recipe_ingredients(recipe_id: int, ingredients: List[dict]):
  database.update_ingredients(recipe_id, ingredients)
  invalidate_cache(f"nutrition:calculate_nutrition:{recipe_id}")
```

### Pattern 4: Hierarchical Data

```python
# Cache parent and children separately
@cached(ttl=120, key_prefix="category")
def get_category(category_id: int) -> dict:
  return database.get_category(category_id)

@cached(ttl=60, key_prefix="category_recipes")
def get_category_recipes(category_id: int) -> List[dict]:
  return database.get_recipes_by_category(category_id)

# Invalidate hierarchy correctly
def update_category(category_id: int, data: dict):
  database.update_category(category_id, data)
  invalidate_cache(f"category:get_category:{category_id}")
  invalidate_cache(f"category_recipes:get_category_recipes:{category_id}")
```

## Testing Cache Integration

### Test 1: Verify Caching Works

```python
def test_caching():
  from backend.core.cache import clear_all_cache

  clear_all_cache()

  # First call should be cache miss
  start = time.time()
  result1 = get_recipes(limit=10)
  time1 = time.time() - start

  # Second call should be cache hit (much faster)
  start = time.time()
  result2 = get_recipes(limit=10)
  time2 = time.time() - start

  assert result1 == result2
  assert time2 < time1 / 10  # Should be at least 10x faster
```

### Test 2: Verify Cache Invalidation

```python
def test_cache_invalidation():
  from backend.core.cache import clear_all_cache

  clear_all_cache()

  # Cache initial data
  recipes1 = get_recipes(limit=10)

  # Modify data
  create_recipe({"title": "New Recipe"})

  # Should get fresh data after invalidation
  recipes2 = get_recipes(limit=10)

  assert len(recipes2) == len(recipes1) + 1
```

## Monitoring

### Add Cache Stats to Health Check

```python
from backend.core.cache import get_cache_stats

def health_check() -> dict:
  cache_stats = get_cache_stats()

  return {
    "status": "ok",
    "cache": {
      "hit_rate": cache_stats["hit_rate"],
      "entries": cache_stats["total_entries"],
    }
  }
```

### Log Cache Performance

```python
import logging
from backend.core.cache import get_cache_stats

logger = logging.getLogger(__name__)

def log_cache_stats():
  stats = get_cache_stats()

  if stats["hit_rate"] < 50:
    logger.warning(f"Low cache hit rate: {stats['hit_rate']}%")
  else:
    logger.info(f"Cache performing well: {stats['hit_rate']}% hit rate")
```

## Troubleshooting

### Problem: Cache Not Working

**Check:**
- Function is decorated with @cached
- Function is being called (not just defined)
- Parameters are hashable (no mutable defaults)

**Solution:**
```python
# Bad - mutable default
@cached(ttl=60)
def search(filters: dict = {}):  # Don't do this!
  pass

# Good - immutable default
@cached(ttl=60)
def search(filters: dict = None):
  filters = filters or {}
  pass
```

### Problem: Stale Data

**Check:**
- TTL is appropriate for data freshness
- Cache invalidation is working
- Invalidation patterns are correct

**Solution:**
- Reduce TTL for affected operations
- Add missing invalidation calls
- Use pattern matching for bulk invalidation

### Problem: Memory Growth

**Check:**
- Cache size with `get_cache_stats()`
- TTL values are reasonable
- No memory leaks in cached functions

**Solution:**
```python
from backend.core.cache import get_cache

cache = get_cache()
cache.cleanup_expired()  # Remove expired entries

# Or schedule periodic cleanup
import schedule
schedule.every(5).minutes.do(cache.cleanup_expired)
```

## Migration Guide

### Migrating Existing Code

1. **Identify slow operations:**
   ```bash
   # Profile your application
   python -m cProfile -o profile.stats your_app.py
   ```

2. **Add caching incrementally:**
   - Start with read-heavy operations
   - Test each change
   - Monitor cache hit rates

3. **Update write operations:**
   - Add invalidation after testing reads
   - Verify data consistency

4. **Monitor and tune:**
   - Adjust TTL values based on hit rates
   - Optimize invalidation patterns

## Best Practices Summary

1. **Cache read operations, invalidate on writes**
2. **Use appropriate TTL for each data type**
3. **Always clear cache in tests**
4. **Monitor hit rates and adjust as needed**
5. **Use pattern matching for related caches**
6. **Don't cache user-specific or sensitive data with long TTL**
7. **Document cache behavior in API docs**
8. **Test cache invalidation thoroughly**

## Next Steps

1. Review `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/examples/cache_usage_examples.py`
2. Read `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/docs/cache-implementation.md`
3. Run tests: `pytest tests/test_cache.py -v`
4. Integrate caching into your services
5. Monitor cache performance via stats endpoint

## Support

For issues or questions:
- Review test suite: `tests/test_cache.py`
- Check examples: `examples/cache_usage_examples.py`
- Read implementation: `backend/core/cache.py`

---

**Version**: 1.0.0
**Last Updated**: 2025-12-11

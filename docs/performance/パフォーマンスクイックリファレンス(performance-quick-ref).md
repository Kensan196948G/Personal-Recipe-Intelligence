# Performance Optimization - Quick Reference Card

**Personal Recipe Intelligence - At-a-Glance Guide**

---

## Target Performance

- API Response: **< 200ms** (per CLAUDE.md Section 12.1)
- Database Query: **< 100ms**
- Cache Hit Rate: **> 70%**

---

## Files Created

### Documentation
- `パフォーマンス索引(performance-index).md` - Complete overview
- `パフォーマンスサマリー(performance-summary).md` - Executive summary
- `パフォーマンス統合(performance-integration).md` - Integration guide
- `パフォーマンス調査結果(performance-findings).md` - Detailed analysis
- `パフォーマンスチェックリスト(performance-checklist).md` - Quick fixes
- `パフォーマンスクイックリファレンス(performance-quick-ref).md` - This file

### Implementation (Ready to Use)
- `backend/middleware.py` - Performance tracking
- `backend/cache.py` - Lightweight caching
- `backend/monitoring.py` - System monitoring
- `backend/async_helpers.py` - Async utilities
- `backend/database_optimized.py` - SQLite optimization

### Tools
- `scripts/performance_audit.py` - Code scanner

---

## Quick Commands

```bash
# Run performance audit
python scripts/performance_audit.py

# Save audit report
python scripts/performance_audit.py > audit_report.txt

# Test API response time
curl -i http://localhost:8000/api/v1/recipes/1

# Load test (requires apache2-utils)
ab -n 100 -c 10 http://localhost:8000/api/v1/recipes/1

# Check metrics
curl http://localhost:8000/api/v1/metrics | jq

# Install dependencies
pip install aiohttp aiofiles psutil
```

---

## Common Fixes

### Fix 1: N+1 Query
```python
# BEFORE
recipes = session.query(Recipe).all()
for recipe in recipes:
    ingredients = session.query(Ingredient).filter_by(recipe_id=recipe.id).all()

# AFTER
from sqlalchemy.orm import joinedload
recipes = session.query(Recipe).options(joinedload(Recipe.ingredients)).all()
```

### Fix 2: Blocking HTTP
```python
# BEFORE
import requests
response = requests.get(url)

# AFTER
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.text()
```

### Fix 3: Blocking File I/O
```python
# BEFORE
with open(path) as f:
    data = json.load(f)

# AFTER
from backend.async_helpers import AsyncFileHandler
data = await AsyncFileHandler.read_json(path)
```

### Fix 4: CPU-Bound in Async
```python
# BEFORE
async def process():
    text = pytesseract.image_to_string(img)

# AFTER
from backend.async_helpers import run_cpu_bound
async def process():
    text = await run_cpu_bound(pytesseract.image_to_string, img)
```

### Fix 5: Resource Leak
```python
# BEFORE
f = open(path)
data = f.read()

# AFTER
with open(path) as f:
    data = f.read()
```

---

## Quick Integration (30 min)

### Step 1: Add Middleware (5 min)
```python
from backend.middleware import PerformanceMiddleware
app.add_middleware(PerformanceMiddleware)
```

### Step 2: Use Optimized DB (5 min)
```python
from backend.database_optimized import OptimizedDatabase
db = OptimizedDatabase("data/recipes.db")
```

### Step 3: Add Caching (10 min)
```python
from backend.cache import recipe_cache

# In your endpoint
cached = recipe_cache.get(f"recipe:{id}")
if cached:
    return cached

result = await fetch_from_db(id)
recipe_cache.set(f"recipe:{id}", result)
return result
```

### Step 4: Fix Async Operations (10 min)
```python
# Replace requests with aiohttp
import aiohttp

# Move OCR to thread pool
from backend.async_helpers import run_cpu_bound
```

---

## Verification Checks

```python
# Check middleware active
print(app.middleware)

# Check cache stats
from backend.cache import get_cache_stats
print(get_cache_stats())

# Check database stats
print(db.get_database_stats())

# Check memory
from backend.monitoring import MemoryMonitor
MemoryMonitor.log_memory_usage("checkpoint")
```

---

## Common Issues

### Issue: SQLite database locked
```python
# Solution: Enable WAL mode
import sqlite3
conn = sqlite3.connect('data/recipes.db')
conn.execute("PRAGMA journal_mode=WAL")
```

### Issue: Cache not working
```python
# Solution: Check TTL and clear if needed
from backend.cache import recipe_cache
print(recipe_cache.get_stats())
recipe_cache.clear()
```

### Issue: Import errors
```bash
# Solution: Add to Python path
export PYTHONPATH=/mnt/Linux-ExHDD/Personal-Recipe-Intelligence:$PYTHONPATH
```

### Issue: Slow requests not logged
```python
# Solution: Enable logging
import logging
logging.basicConfig(level=logging.INFO)
```

---

## Performance Patterns

### Pattern: Cache with Invalidation
```python
from backend.cache import recipe_cache

class RecipeService:
    async def get(self, id):
        cached = recipe_cache.get(f"recipe:{id}")
        if cached:
            return cached
        result = await self.fetch(id)
        recipe_cache.set(f"recipe:{id}", result)
        return result

    async def update(self, id, data):
        await self.save(id, data)
        recipe_cache.invalidate(f"recipe:{id}")
```

### Pattern: Batch Loading
```python
from backend.database_optimized import OptimizedDatabase

db = OptimizedDatabase("data/recipes.db")
recipes = db.get_recipes_batch([1, 2, 3, 4, 5])
```

### Pattern: OCR with Memory Tracking
```python
from backend.monitoring import MemoryMonitor
from backend.async_helpers import run_cpu_bound

async def process_images(paths):
    with MemoryMonitor.track_memory("OCR batch"):
        results = []
        for path in paths:
            text = await run_cpu_bound(ocr_function, path)
            results.append(text)
        return results
```

### Pattern: Concurrent Scraping
```python
from backend.async_helpers import batch_process, RateLimiter

rate_limiter = RateLimiter(max_requests=3, time_window=1.0)

async def scrape_url(url):
    async with rate_limiter:
        return await fetch(url)

results = await batch_process(urls, scrape_url, max_concurrent=3)
```

---

## Monitoring

### Add Metrics Endpoint
```python
from backend.cache import get_cache_stats
from backend.monitoring import get_all_stats

@app.get("/api/v1/metrics")
async def metrics():
    return {
        "cache": get_cache_stats(),
        "system": get_all_stats()
    }
```

### Add Timing Decorator
```python
from backend.monitoring import PerformanceMonitor

@PerformanceMonitor.timed(threshold_ms=200)
async def expensive_function():
    pass
```

### Track Memory
```python
from backend.monitoring import MemoryMonitor

with MemoryMonitor.track_memory("operation name"):
    # Your code
    pass
```

---

## Testing Performance

### Response Time Test
```bash
# Check header
curl -i http://localhost:8000/api/v1/recipes/1 | grep X-Response-Time

# Benchmark
time curl http://localhost:8000/api/v1/recipes/1
```

### Load Test
```bash
# 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/api/v1/recipes/1

# Check: Time per request < 200ms
```

### Cache Test
```bash
# First request (miss)
time curl http://localhost:8000/api/v1/recipes/1

# Second request (hit) - should be faster
time curl http://localhost:8000/api/v1/recipes/1
```

---

## Priorities

### Critical (Do First)
1. Add middleware
2. Run audit script
3. Fix blocking operations

### High (Week 1)
4. Fix N+1 queries
5. Enable SQLite optimizations
6. Add caching to hot paths

### Medium (Week 2)
7. Move OCR to thread pool
8. Add monitoring
9. Fix file I/O

### Low (Ongoing)
10. Fine-tuning
11. Comprehensive tests
12. Performance profiling

---

## Success Criteria

- [ ] API < 200ms (p90)
- [ ] No blocking in async (audit clean)
- [ ] No N+1 queries
- [ ] Cache hit > 70%
- [ ] Memory stable
- [ ] Monitoring active

---

## Getting Started

1. **Read**: パフォーマンスサマリー(performance-summary).md
2. **Implement**: パフォーマンス統合(performance-integration).md
3. **Reference**: This file
4. **Audit**: `python scripts/performance_audit.py`
5. **Monitor**: Check `/api/v1/metrics`

---

## Key Imports

```python
# Middleware
from backend.middleware import PerformanceMiddleware

# Caching
from backend.cache import recipe_cache, TTLCache, cached

# Monitoring
from backend.monitoring import MemoryMonitor, PerformanceMonitor

# Async helpers
from backend.async_helpers import (
    run_cpu_bound,
    run_in_thread,
    AsyncFileHandler,
    AsyncRetry,
    RateLimiter,
    batch_process
)

# Database
from backend.database_optimized import OptimizedDatabase
```

---

## One-Liner Checks

```bash
# Audit code
python scripts/performance_audit.py | grep "TOTAL ISSUES"

# Test response
curl -w "@-" -o /dev/null -s http://localhost:8000/api/v1/recipes/1 <<< "time_total: %{time_total}s\n"

# Check cache
python -c "from backend.cache import recipe_cache; print(recipe_cache.get_stats())"

# Check memory
python -c "from backend.monitoring import MemoryMonitor; MemoryMonitor.log_memory_usage('check')"

# DB stats
python -c "from backend.database_optimized import OptimizedDatabase; print(OptimizedDatabase('data/recipes.db').get_database_stats())"
```

---

## Contact Points

All files in: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/`

**Start here:** パフォーマンス索引(performance-index).md for complete overview

**Questions?** Check パフォーマンス調査結果(performance-findings).md for detailed explanations

**Integration help?** See パフォーマンス統合(performance-integration).md step-by-step guide

---

**Target: API < 200ms | All code production-ready | CLAUDE.md compliant**

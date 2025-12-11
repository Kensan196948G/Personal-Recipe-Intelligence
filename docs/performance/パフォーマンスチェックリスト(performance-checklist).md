# Performance Optimization Checklist - Personal Recipe Intelligence

**Quick Reference Guide for Identifying and Fixing Performance Issues**

---

## 1. Database Query Optimization Checklist

### Check for N+1 Problems

```bash
# Search for patterns that might indicate N+1 queries
grep -r "for.*in.*:" backend/services/ | grep -A 5 "query\|filter\|get"
```

### Quick Fix Templates

#### Template 1: Eager Loading Relationships
```python
# BEFORE (N+1)
recipes = session.query(Recipe).all()
for recipe in recipes:
    ingredients = session.query(Ingredient).filter_by(recipe_id=recipe.id).all()

# AFTER (Optimized)
from sqlalchemy.orm import joinedload
recipes = session.query(Recipe).options(joinedload(Recipe.ingredients)).all()
```

#### Template 2: Select Specific Columns
```python
# BEFORE (Loads all columns)
recipes = session.query(Recipe).all()

# AFTER (Only needed columns)
recipes = session.query(Recipe.id, Recipe.name, Recipe.created_at).all()
```

#### Template 3: Batch Loading
```python
# BEFORE (Multiple individual queries)
for recipe_id in recipe_ids:
    recipe = session.query(Recipe).get(recipe_id)

# AFTER (Single batch query)
recipes = session.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
```

---

## 2. Async/Await Optimization Checklist

### Search for Blocking Operations

```bash
# Find sync HTTP requests in async code
grep -r "import requests" backend/
grep -r "requests\.get\|requests\.post" backend/

# Find sync file operations in async functions
grep -r "async def" backend/ | grep -A 10 "open("
```

### Quick Fix Templates

#### Template 1: HTTP Requests
```python
# BEFORE (Blocking)
import requests
async def fetch_recipe(url):
    response = requests.get(url)
    return response.text

# AFTER (Non-blocking)
import aiohttp
async def fetch_recipe(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
            return await response.text()
```

#### Template 2: Concurrent Operations
```python
# BEFORE (Sequential - 3x slower)
async def fetch_multiple(urls):
    results = []
    for url in urls:
        result = await fetch_recipe(url)
        results.append(result)
    return results

# AFTER (Concurrent)
import asyncio
async def fetch_multiple(urls):
    tasks = [fetch_recipe(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

#### Template 3: File Operations
```python
# BEFORE (Blocking)
async def save_recipe(recipe_id, data):
    with open(f'data/{recipe_id}.json', 'w') as f:
        json.dump(data, f)

# AFTER (Non-blocking)
import aiofiles
async def save_recipe(recipe_id, data):
    async with aiofiles.open(f'data/{recipe_id}.json', 'w') as f:
        await f.write(json.dumps(data))
```

#### Template 4: CPU-Bound Operations
```python
# BEFORE (Blocks event loop)
async def process_image(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

# AFTER (Runs in thread pool)
import asyncio
async def process_image(image_path):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: pytesseract.image_to_string(Image.open(image_path))
    )
```

---

## 3. Memory Leak Prevention Checklist

### Search for Resource Leaks

```bash
# Find file operations without context managers
grep -r "open(" backend/ | grep -v "with open"

# Find database connections without proper cleanup
grep -r "connect(" backend/ | grep -v "with.*connect"
```

### Quick Fix Templates

#### Template 1: File Handles
```python
# BEFORE (Potential leak)
def read_recipe(path):
    f = open(path)
    data = f.read()
    return data  # File never closed

# AFTER (Safe)
def read_recipe(path):
    with open(path) as f:
        return f.read()
```

#### Template 2: Database Connections
```python
# BEFORE (Potential leak)
def get_recipes():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    return cursor.fetchall()

# AFTER (Safe)
def get_recipes():
    with sqlite3.connect('recipes.db') as conn:
        cursor = conn.cursor()
        return cursor.fetchall()
```

#### Template 3: Browser/MCP Cleanup
```python
# BEFORE (Resource leak)
async def scrape(url):
    browser = await launch_browser()
    page = await browser.new_page()
    content = await page.content()
    return content

# AFTER (Safe)
async def scrape(url):
    browser = await launch_browser()
    try:
        page = await browser.new_page()
        content = await page.content()
        return content
    finally:
        await browser.close()
```

#### Template 4: Image Processing
```python
# BEFORE (Memory not freed)
def process_image(path):
    img = Image.open(path)
    result = do_processing(img)
    return result

# AFTER (Explicit cleanup)
def process_image(path):
    with Image.open(path) as img:
        result = do_processing(img)
    return result
```

---

## 4. Caching Implementation Checklist

### Search for Repeated Computations

```bash
# Find functions that might benefit from caching
grep -r "def get_\|def fetch_\|def load_" backend/services/
```

### Quick Fix Templates

#### Template 1: LRU Cache for Pure Functions
```python
from functools import lru_cache

# BEFORE (Recalculates every time)
def normalize_ingredient(name: str) -> str:
    return name.lower().strip().replace('  ', ' ')

# AFTER (Cached)
@lru_cache(maxsize=1000)
def normalize_ingredient(name: str) -> str:
    return name.lower().strip().replace('  ', ' ')
```

#### Template 2: TTL Cache for API Data
```python
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self._ttl):
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (value, datetime.now())

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

# Usage
recipe_cache = TTLCache(ttl_seconds=300)

async def get_recipe(recipe_id: int):
    cached = recipe_cache.get(f"recipe:{recipe_id}")
    if cached:
        return cached

    recipe = await fetch_recipe_from_db(recipe_id)
    recipe_cache.set(f"recipe:{recipe_id}", recipe)
    return recipe
```

#### Template 3: Cache Invalidation
```python
class RecipeService:
    def __init__(self):
        self.cache = TTLCache(ttl_seconds=300)

    async def get_recipe(self, recipe_id: int):
        cached = self.cache.get(f"recipe:{recipe_id}")
        if cached:
            return cached

        recipe = await self._fetch_from_db(recipe_id)
        self.cache.set(f"recipe:{recipe_id}", recipe)
        return recipe

    async def update_recipe(self, recipe_id: int, data: dict):
        await self._update_in_db(recipe_id, data)
        # Invalidate cache after update
        self.cache.invalidate(f"recipe:{recipe_id}")

    async def delete_recipe(self, recipe_id: int):
        await self._delete_from_db(recipe_id)
        # Invalidate cache after deletion
        self.cache.invalidate(f"recipe:{recipe_id}")
```

---

## 5. File I/O Optimization Checklist

### Search for Blocking File Operations

```bash
# Find sync file operations in async context
grep -r "async def" backend/ -A 20 | grep -B 2 "json.load\|json.dump\|open("
```

### Quick Fix Templates

#### Template 1: Async File Reading
```python
# BEFORE (Blocking)
async def load_recipe_json(recipe_id):
    with open(f'data/recipes/{recipe_id}.json') as f:
        return json.load(f)

# AFTER (Non-blocking)
import aiofiles
import json

async def load_recipe_json(recipe_id):
    async with aiofiles.open(f'data/recipes/{recipe_id}.json') as f:
        content = await f.read()
        return json.loads(content)
```

#### Template 2: Streaming Large Files
```python
# BEFORE (Loads entire file into memory)
def process_log_file(path):
    with open(path) as f:
        lines = f.readlines()  # Memory spike
    for line in lines:
        process(line)

# AFTER (Streams line by line)
def process_log_file(path):
    with open(path) as f:
        for line in f:  # Iterator - low memory
            process(line)
```

#### Template 3: Batch File Operations
```python
# BEFORE (Opens file repeatedly)
def log_operations(operations):
    for op in operations:
        with open('logs/audit.log', 'a') as f:
            f.write(f"{op}\n")

# AFTER (Single file open)
def log_operations(operations):
    with open('logs/audit.log', 'a') as f:
        f.writelines(f"{op}\n" for op in operations)
```

#### Template 4: Buffered Logging
```python
import logging
from logging.handlers import MemoryHandler

# Setup buffered logging
file_handler = logging.FileHandler('logs/app.log')
memory_handler = MemoryHandler(
    capacity=100,  # Buffer 100 records
    flushLevel=logging.ERROR,  # Flush on error
    target=file_handler
)

logger = logging.getLogger(__name__)
logger.addHandler(memory_handler)
```

---

## 6. Blocking Operations Detection Checklist

### Search Commands

```bash
# Find potential blocking operations
grep -r "time.sleep\|sleep(" backend/
grep -r "subprocess.call\|subprocess.run" backend/
grep -r "requests\." backend/
grep -r "pytesseract\|tesseract" backend/
```

### Quick Fix Templates

#### Template 1: Replace time.sleep()
```python
# BEFORE (Blocks event loop)
import time
async def retry_operation():
    for i in range(3):
        try:
            return await operation()
        except Exception:
            time.sleep(1)  # BLOCKS!

# AFTER (Non-blocking)
import asyncio
async def retry_operation():
    for i in range(3):
        try:
            return await operation()
        except Exception:
            await asyncio.sleep(1)  # Non-blocking
```

#### Template 2: OCR in Thread Pool
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import pytesseract

# Create executor at module level
_executor = ThreadPoolExecutor(max_workers=2)

async def ocr_image(image_path: str) -> str:
    """Run OCR in thread pool to avoid blocking event loop"""
    loop = asyncio.get_event_loop()

    def _ocr_sync():
        with Image.open(image_path) as img:
            return pytesseract.image_to_string(img)

    return await loop.run_in_executor(_executor, _ocr_sync)
```

#### Template 3: Complex Parsing in Thread Pool
```python
from bs4 import BeautifulSoup
import asyncio

async def parse_recipe_html(html: str):
    """Parse HTML in thread pool for CPU-intensive operations"""
    loop = asyncio.get_event_loop()

    def _parse_sync():
        soup = BeautifulSoup(html, 'html.parser')
        # CPU-intensive parsing logic
        ingredients = extract_ingredients(soup)
        steps = extract_steps(soup)
        return {'ingredients': ingredients, 'steps': steps}

    return await loop.run_in_executor(None, _parse_sync)
```

---

## 7. Performance Monitoring Setup

### Add Timing Middleware

```python
# backend/api/middleware.py
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        duration_ms = duration * 1000

        # Add header
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        # Log slow requests (>200ms per CLAUDE.md)
        if duration > 0.2:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.url.path} "
                f"took {duration_ms:.2f}ms",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "client": request.client.host if request.client else None
                }
            )

        return response

# Usage in main.py
from fastapi import FastAPI
app = FastAPI()
app.add_middleware(PerformanceMiddleware)
```

### Add Database Query Logging

```python
# backend/database.py
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug(f"Starting query: {statement[:100]}")

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    total_ms = total * 1000

    if total > 0.1:  # Log queries slower than 100ms
        logger.warning(
            f"SLOW QUERY ({total_ms:.2f}ms): {statement[:200]}",
            extra={
                "duration_ms": total_ms,
                "query": statement
            }
        )
```

### Add Memory Monitoring

```python
# backend/monitoring.py
import psutil
import os
import logging

logger = logging.getLogger(__name__)

def log_memory_usage(context: str = ""):
    """Log current memory usage"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()

    logger.info(
        f"Memory usage {context}: "
        f"RSS={mem_info.rss / 1024 / 1024:.2f}MB, "
        f"VMS={mem_info.vms / 1024 / 1024:.2f}MB",
        extra={
            "memory_rss_mb": mem_info.rss / 1024 / 1024,
            "memory_vms_mb": mem_info.vms / 1024 / 1024,
            "context": context
        }
    )

# Usage
async def process_large_recipe_batch(recipes):
    log_memory_usage("before batch processing")
    results = await process_recipes(recipes)
    log_memory_usage("after batch processing")
    return results
```

---

## 8. SQLite Optimization

### Optimal Configuration

```python
# backend/database.py
import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Apply SQLite performance optimizations"""
        with self.get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")

            # Increase cache size (10MB)
            conn.execute("PRAGMA cache_size=-10000")

            # Faster synchronization for personal use
            conn.execute("PRAGMA synchronous=NORMAL")

            # Use memory for temp tables
            conn.execute("PRAGMA temp_store=MEMORY")

            # Optimize for read-heavy workloads
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB

    @contextmanager
    def get_connection(self):
        """Context manager for safe connection handling"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=10.0,
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        conn.row_factory = sqlite3.Row  # Dict-like access
        try:
            yield conn
        finally:
            conn.close()

    def create_indexes(self):
        """Create performance indexes"""
        with self.get_connection() as conn:
            # Index for recipe searches
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_recipes_name "
                "ON recipes(name)"
            )

            # Index for date filtering
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_recipes_created "
                "ON recipes(created_at)"
            )

            # Index for ingredient lookups
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_ingredients_recipe "
                "ON ingredients(recipe_id)"
            )

            # Index for tag searches
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tags_name "
                "ON tags(name)"
            )

# Usage
db = Database("data/recipes.db")
db.create_indexes()
```

---

## 9. Quick Performance Audit Script

```python
# scripts/performance_audit.py
"""
Quick performance audit script
Run: python scripts/performance_audit.py
"""

import os
import re
from pathlib import Path

def audit_async_code():
    """Check for blocking operations in async code"""
    issues = []
    backend_path = Path("backend")

    for py_file in backend_path.rglob("*.py"):
        with open(py_file) as f:
            content = f.read()
            lines = content.split('\n')

            # Check if file has async functions
            if 'async def' not in content:
                continue

            # Look for blocking operations
            for i, line in enumerate(lines, 1):
                if 'import requests' in line:
                    issues.append(f"{py_file}:{i} - Using blocking 'requests' module")

                if re.search(r'(?<!await\s)time\.sleep', line):
                    issues.append(f"{py_file}:{i} - Using blocking time.sleep()")

                if re.search(r'open\(.*\)(?!\s*as)', line) and 'aiofiles' not in content:
                    issues.append(f"{py_file}:{i} - Blocking file operation")

    return issues

def audit_database_queries():
    """Check for potential N+1 queries"""
    issues = []
    backend_path = Path("backend")

    for py_file in backend_path.rglob("*.py"):
        with open(py_file) as f:
            content = f.read()
            lines = content.split('\n')

            in_loop = False
            for i, line in enumerate(lines, 1):
                if re.search(r'for\s+\w+\s+in\s+', line):
                    in_loop = True

                if in_loop and re.search(r'\.query\(|\.filter\(|\.get\(', line):
                    issues.append(f"{py_file}:{i} - Potential N+1 query in loop")

                if not line.strip() or line.strip().startswith('def '):
                    in_loop = False

    return issues

def audit_resource_leaks():
    """Check for potential resource leaks"""
    issues = []
    backend_path = Path("backend")

    for py_file in backend_path.rglob("*.py"):
        with open(py_file) as f:
            content = f.read()
            lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                # File operations without context manager
                if re.search(r'\w+\s*=\s*open\(', line) and 'with' not in line:
                    issues.append(f"{py_file}:{i} - File opened without context manager")

                # Database connections without context manager
                if re.search(r'\w+\s*=\s*.*\.connect\(', line) and 'with' not in line:
                    issues.append(f"{py_file}:{i} - Connection without context manager")

    return issues

if __name__ == "__main__":
    print("=" * 60)
    print("PERFORMANCE AUDIT REPORT")
    print("=" * 60)

    print("\n[1] Async/Await Issues:")
    async_issues = audit_async_code()
    if async_issues:
        for issue in async_issues:
            print(f"  - {issue}")
    else:
        print("  ✓ No issues found")

    print("\n[2] Database Query Issues:")
    db_issues = audit_database_queries()
    if db_issues:
        for issue in db_issues:
            print(f"  - {issue}")
    else:
        print("  ✓ No issues found")

    print("\n[3] Resource Leak Risks:")
    leak_issues = audit_resource_leaks()
    if leak_issues:
        for issue in leak_issues:
            print(f"  - {issue}")
    else:
        print("  ✓ No issues found")

    print("\n" + "=" * 60)
    total_issues = len(async_issues) + len(db_issues) + len(leak_issues)
    print(f"Total issues found: {total_issues}")
    print("=" * 60)
```

---

## 10. Priority Action Items

### Immediate (Day 1)
- [ ] Run performance audit script
- [ ] Add timing middleware
- [ ] Enable SQLite WAL mode
- [ ] Add database query logging

### High Priority (Week 1)
- [ ] Fix any N+1 queries identified
- [ ] Convert blocking HTTP to aiohttp
- [ ] Add context managers for file operations
- [ ] Implement LRU cache for ingredient normalization

### Medium Priority (Week 2)
- [ ] Move OCR to thread pool
- [ ] Implement TTL cache for recipes
- [ ] Convert sync file I/O to async
- [ ] Add memory monitoring

### Low Priority (Month 1)
- [ ] Profile CPU-intensive functions
- [ ] Optimize JSON serialization
- [ ] Implement batch operations
- [ ] Add comprehensive performance tests

---

## Files to Create/Modify

1. `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/api/middleware.py` - Add PerformanceMiddleware
2. `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/monitoring.py` - Add memory monitoring
3. `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/cache.py` - Add TTLCache
4. `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/scripts/performance_audit.py` - Audit script
5. Update `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/database.py` - SQLite optimizations

---

**Last Updated:** 2025-12-11
**Target Performance:** API < 200ms (CLAUDE.md Section 12.1)

# Performance Analysis Findings - Personal Recipe Intelligence

**Analysis Date:** 2025-12-11
**Project:** Personal Recipe Intelligence
**Focus:** backend/services/ and backend/api/

---

## Current Status

**IMPORTANT:** The codebase analysis requires reading actual implementation files. Since I cannot execute bash commands to explore the directory structure in this environment, I will provide:

1. A comprehensive performance analysis framework
2. Common performance anti-patterns to look for
3. Specific recommendations based on the project requirements in CLAUDE.md

---

## Performance Analysis Framework

### 1. Database Query Optimization (N+1 Problem Detection)

#### Common N+1 Patterns in Recipe Applications:

**Anti-Pattern 1: Loop with Individual Queries**
```python
# INEFFICIENT - N+1 Problem
def get_recipes_with_ingredients():
    recipes = session.query(Recipe).all()
    for recipe in recipes:
        # This triggers N additional queries!
        ingredients = session.query(Ingredient).filter_by(
            recipe_id=recipe.id
        ).all()
        recipe.ingredients = ingredients
    return recipes

# OPTIMIZED - Single Query with JOIN
def get_recipes_with_ingredients():
    recipes = session.query(Recipe).options(
        joinedload(Recipe.ingredients)
    ).all()
    return recipes
```

**Anti-Pattern 2: Multiple Relationship Loads**
```python
# INEFFICIENT
def get_recipe_details(recipe_id):
    recipe = session.query(Recipe).get(recipe_id)
    tags = session.query(Tag).filter(Tag.recipe_id == recipe_id).all()
    steps = session.query(Step).filter(Step.recipe_id == recipe_id).all()
    nutrition = session.query(Nutrition).filter(Nutrition.recipe_id == recipe_id).first()
    return recipe, tags, steps, nutrition

# OPTIMIZED
def get_recipe_details(recipe_id):
    recipe = session.query(Recipe).options(
        joinedload(Recipe.tags),
        joinedload(Recipe.steps),
        joinedload(Recipe.nutrition)
    ).filter(Recipe.id == recipe_id).first()
    return recipe
```

**Recommendation:**
- Use `joinedload()` for one-to-many relationships that are always needed
- Use `selectinload()` for large collections to avoid cartesian products
- Use `lazy='dynamic'` for relationships that are rarely accessed

---

### 2. Async/Await Usage Analysis

#### Common Async Anti-Patterns:

**Anti-Pattern 1: Blocking HTTP in Async Context**
```python
# BLOCKS EVENT LOOP
import requests

async def fetch_recipe_from_url(url):
    # This blocks the entire event loop!
    response = requests.get(url)
    return response.text

# CORRECT - Non-blocking
import aiohttp

async def fetch_recipe_from_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

**Anti-Pattern 2: Sequential Awaits**
```python
# INEFFICIENT - Sequential execution (600ms total)
async def fetch_multiple_recipes(urls):
    results = []
    for url in urls:
        result = await fetch_recipe(url)  # 200ms each
        results.append(result)
    return results

# OPTIMIZED - Concurrent execution (200ms total)
async def fetch_multiple_recipes(urls):
    tasks = [fetch_recipe(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

**Anti-Pattern 3: Sync DB Queries in Async Functions**
```python
# BLOCKS EVENT LOOP
async def get_recipe_api(recipe_id: int):
    # SQLAlchemy sync query blocks!
    recipe = session.query(Recipe).get(recipe_id)
    return recipe

# CORRECT - Use async DB driver
from sqlalchemy.ext.asyncio import AsyncSession

async def get_recipe_api(recipe_id: int, session: AsyncSession):
    result = await session.execute(
        select(Recipe).where(Recipe.id == recipe_id)
    )
    return result.scalar_one_or_none()
```

**Recommendations:**
- Use `aiohttp` instead of `requests` for HTTP calls
- Use `asyncio.gather()` for concurrent operations
- Use async SQLAlchemy (`asyncpg` driver) or run sync queries in thread pool
- Use `asyncio.to_thread()` for CPU-bound operations

---

### 3. Memory Leak Risk Assessment

#### Critical Areas for Recipe Application:

**Risk 1: OCR Image Processing**
```python
# MEMORY LEAK RISK
def process_recipe_image(image_path):
    img = Image.open(image_path)
    # Heavy OCR processing
    text = pytesseract.image_to_string(img)
    # Image not explicitly closed!
    return text

# SAFE
def process_recipe_image(image_path):
    with Image.open(image_path) as img:
        text = pytesseract.image_to_string(img)
    # Explicit cleanup of temp files
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return text
```

**Risk 2: Database Connection Leaks**
```python
# LEAK RISK
def get_recipes():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    recipes = cursor.fetchall()
    # Connection never closed!
    return recipes

# SAFE
def get_recipes():
    with sqlite3.connect('recipes.db') as conn:
        cursor = conn.cursor()
        recipes = cursor.fetchall()
    return recipes
```

**Risk 3: Large JSON Loading**
```python
# MEMORY INEFFICIENT
def import_recipes(json_file):
    # Loads entire file into memory
    with open(json_file) as f:
        all_recipes = json.load(f)  # Could be 100MB+
    for recipe in all_recipes:
        save_recipe(recipe)

# MEMORY EFFICIENT
import ijson

def import_recipes(json_file):
    with open(json_file, 'rb') as f:
        # Streams JSON objects one at a time
        for recipe in ijson.items(f, 'item'):
            save_recipe(recipe)
```

**Risk 4: Puppeteer/Browser MCP Resource Leaks**
```python
# LEAK RISK
async def scrape_recipe(url):
    browser = await launch_browser()
    page = await browser.new_page()
    content = await page.content()
    # Browser never closed!
    return content

# SAFE
async def scrape_recipe(url):
    browser = await launch_browser()
    try:
        page = await browser.new_page()
        content = await page.content()
        return content
    finally:
        await browser.close()
```

**Recommendations:**
- Always use context managers (`with` statements)
- Explicitly close file handles and connections
- Use `try/finally` for browser/MCP cleanup
- Monitor memory usage during OCR operations
- Implement timeout for web scraping operations

---

### 4. Caching Implementation Review

#### Optimal Caching Strategy (per CLAUDE.md: lightweight only):

**Good: Simple In-Memory Cache**
```python
from functools import lru_cache
from datetime import datetime, timedelta

# Simple LRU cache for ingredient normalization
@lru_cache(maxsize=1000)
def normalize_ingredient(name: str) -> str:
    return name.lower().strip()

# Time-based cache for recipe metadata
class SimpleCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

    def invalidate(self, key):
        if key in self.cache:
            del self.cache[key]
```

**Anti-Pattern: Unbounded Cache**
```python
# MEMORY LEAK RISK
class RecipeCache:
    def __init__(self):
        self.cache = {}  # No size limit!

    def get_recipe(self, url):
        if url not in self.cache:
            # Cache grows forever!
            self.cache[url] = fetch_recipe(url)
        return self.cache[url]
```

**Recommendations:**
- Use `functools.lru_cache` with `maxsize` parameter
- Implement TTL (time-to-live) for cached data
- Invalidate cache on recipe updates
- Cache only frequently accessed, rarely changed data
- Monitor cache hit/miss ratios

---

### 5. File I/O Operation Optimization

#### Critical File Operations:

**Anti-Pattern 1: Sync File I/O in Async Context**
```python
# BLOCKS EVENT LOOP
async def save_recipe_json(recipe_id, data):
    with open(f'data/recipes/{recipe_id}.json', 'w') as f:
        json.dump(data, f)  # Blocking!

# OPTIMIZED
import aiofiles

async def save_recipe_json(recipe_id, data):
    async with aiofiles.open(f'data/recipes/{recipe_id}.json', 'w') as f:
        await f.write(json.dumps(data))
```

**Anti-Pattern 2: Reading Large Files**
```python
# MEMORY INEFFICIENT
def process_large_log():
    with open('logs/app.log') as f:
        lines = f.readlines()  # Loads entire file
    for line in lines:
        process(line)

# OPTIMIZED
def process_large_log():
    with open('logs/app.log') as f:
        for line in f:  # Streams line by line
            process(line)
```

**Anti-Pattern 3: Repeated File Writes**
```python
# INEFFICIENT - Multiple file opens
def log_operations(operations):
    for op in operations:
        with open('logs/audit.log', 'a') as f:
            f.write(f"{op}\n")

# OPTIMIZED - Single file open
def log_operations(operations):
    with open('logs/audit.log', 'a') as f:
        for op in operations:
            f.write(f"{op}\n")
```

**Recommendations:**
- Use `aiofiles` for async file operations
- Stream large files instead of loading entirely
- Batch file write operations
- Use buffered I/O for logs
- Consider using SQLite instead of JSON files for structured data

---

### 6. Blocking Operations Detection

#### Common Blocking Operations in Recipe Application:

**1. CPU-Intensive OCR Processing**
```python
# BLOCKS EVENT LOOP
async def process_recipe_image(image_path):
    # OCR is CPU-intensive and synchronous
    text = pytesseract.image_to_string(Image.open(image_path))
    return parse_recipe(text)

# OPTIMIZED - Run in thread pool
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

async def process_recipe_image(image_path):
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(
        executor,
        lambda: pytesseract.image_to_string(Image.open(image_path))
    )
    return parse_recipe(text)
```

**2. Complex Recipe Parsing**
```python
# BLOCKS EVENT LOOP
async def parse_complex_recipe(html):
    # Heavy DOM parsing and regex operations
    soup = BeautifulSoup(html, 'html.parser')
    ingredients = extract_ingredients(soup)  # CPU-intensive
    steps = extract_steps(soup)  # CPU-intensive
    return Recipe(ingredients=ingredients, steps=steps)

# OPTIMIZED
async def parse_complex_recipe(html):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,  # Use default executor
        _parse_recipe_sync,
        html
    )

def _parse_recipe_sync(html):
    soup = BeautifulSoup(html, 'html.parser')
    ingredients = extract_ingredients(soup)
    steps = extract_steps(soup)
    return Recipe(ingredients=ingredients, steps=steps)
```

**3. Synchronous Database Queries**
```python
# BLOCKS EVENT LOOP
async def get_all_recipes_api():
    # Sync SQLAlchemy query
    recipes = session.query(Recipe).all()
    return recipes

# OPTIMIZED - Use async session or thread pool
async def get_all_recipes_api():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: session.query(Recipe).all()
    )

# BETTER - Use async SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession

async def get_all_recipes_api(session: AsyncSession):
    result = await session.execute(select(Recipe))
    return result.scalars().all()
```

**Recommendations:**
- Use `asyncio.to_thread()` or `run_in_executor()` for CPU-bound operations
- Limit thread pool size (2-4 workers for personal app)
- Profile code to identify CPU-intensive functions
- Consider caching results of expensive operations

---

## Specific Recommendations for Personal Recipe Intelligence

### Based on CLAUDE.md Requirements:

#### 1. API Response Time Target: <200ms

**Key Optimizations:**
```python
# Recipe API endpoint optimization checklist
async def get_recipe_endpoint(recipe_id: int):
    # 1. Use async database query or thread pool (50ms)
    # 2. Eager load relationships to avoid N+1 (30ms)
    # 3. Cache frequently accessed recipes (10ms)
    # 4. Return only required fields (10ms)
    # Target: ~100ms total

    # Check cache first
    cached = cache.get(f"recipe:{recipe_id}")
    if cached:
        return cached

    # Async DB query with eager loading
    recipe = await session.execute(
        select(Recipe)
        .options(
            joinedload(Recipe.ingredients),
            joinedload(Recipe.steps)
        )
        .where(Recipe.id == recipe_id)
    )
    result = recipe.scalar_one_or_none()

    # Cache for 5 minutes
    cache.set(f"recipe:{recipe_id}", result, ttl=300)
    return result
```

#### 2. Web Scraping Performance (MCP Constraint)

**Per CLAUDE.md: Maximum 1 MCP at a time**
```python
# Efficient scraping with single MCP instance
class RecipeScraper:
    def __init__(self):
        self.browser = None
        self.semaphore = asyncio.Semaphore(1)  # Enforce single use

    async def scrape_recipe(self, url: str):
        async with self.semaphore:
            if not self.browser:
                self.browser = await launch_browser()

            try:
                page = await self.browser.new_page()
                await page.goto(url, timeout=10000)
                content = await page.content()
                return self.parse_content(content)
            finally:
                await page.close()

    async def cleanup(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
```

#### 3. OCR Performance

**Optimize image processing:**
```python
import asyncio
from PIL import Image
import pytesseract

async def process_recipe_image_optimized(image_path: str):
    # 1. Resize image to reduce OCR time
    # 2. Run OCR in thread pool
    # 3. Clean up temp files

    def _process_sync():
        with Image.open(image_path) as img:
            # Resize to max 1000px width for faster OCR
            if img.width > 1000:
                ratio = 1000 / img.width
                new_size = (1000, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # OCR with optimized settings
            text = pytesseract.image_to_string(
                img,
                lang='jpn+eng',  # Support Japanese
                config='--psm 6'  # Assume uniform text block
            )
            return text

    # Run in thread pool
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _process_sync)

    return text
```

#### 4. SQLite Optimization

**Connection pooling and WAL mode:**
```python
import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self.get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            # Increase cache size
            conn.execute("PRAGMA cache_size=10000")
            # Synchronous mode for personal use
            conn.execute("PRAGMA synchronous=NORMAL")

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(
            self.db_path,
            timeout=10.0,
            check_same_thread=False
        )
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
```

---

## Performance Monitoring Recommendations

### 1. Add Request Timing Middleware
```python
import time
from fastapi import Request

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Response-Time"] = f"{duration:.3f}s"

    # Log slow requests
    if duration > 0.2:  # 200ms threshold
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {duration:.3f}s"
        )

    return response
```

### 2. Database Query Logging
```python
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.1:  # Log queries > 100ms
        logger.warning(f"Slow query ({total:.3f}s): {statement}")
```

### 3. Memory Monitoring
```python
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logger.info(
        f"Memory usage: {mem_info.rss / 1024 / 1024:.2f} MB "
        f"(VMS: {mem_info.vms / 1024 / 1024:.2f} MB)"
    )
```

---

## Action Items

### High Priority
1. **Audit database queries for N+1 problems** in recipe listing endpoints
2. **Review async/await usage** in web scraping service
3. **Implement connection pooling** for SQLite with WAL mode
4. **Add timing middleware** to identify slow endpoints

### Medium Priority
5. **Optimize OCR processing** with image resizing and thread pool
6. **Implement lightweight caching** for frequently accessed recipes
7. **Review file I/O** in JSON import/export functions
8. **Add memory monitoring** for image processing

### Low Priority
9. **Profile CPU-intensive parsing** functions
10. **Optimize JSON serialization** for large recipe exports

---

## Conclusion

Without access to the actual codebase files, this report provides:
- Comprehensive framework for identifying performance issues
- Common anti-patterns specific to recipe applications
- Optimized code examples for each category
- Specific recommendations aligned with CLAUDE.md requirements

**Next Steps:**
To complete the performance analysis, please provide access to:
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/*.py`
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/api/**/*.py`
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/models/*.py`

This will enable specific line-by-line analysis and concrete bottleneck identification.

---

**Report Generated:** 2025-12-11
**Performance Target:** API response < 200ms (per CLAUDE.md Section 12.1)
**Environment:** Ubuntu CLI, Python 3.11, SQLite, Async FastAPI

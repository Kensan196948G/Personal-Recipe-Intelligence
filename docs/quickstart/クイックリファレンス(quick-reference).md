# N+1 Query Optimization - Quick Reference Card

## Installation (30 seconds)

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
chmod +x *.sh
./setup-performance-optimization.sh
./create-models-and-schemas.sh
cd backend && pip install sqlalchemy pydantic fastapi
```

## Key Concepts

### The Problem
```python
# BAD: N+1 queries (1 + 100 = 101 queries for 100 recipes)
recipes = db.query(Recipe).all()
for recipe in recipes:
    for ingredient in recipe.ingredients:  # +1 query per recipe
        print(ingredient.name)
```

### The Solution
```python
# GOOD: 2 queries total
recipes = (
    db.query(Recipe)
    .options(selectinload(Recipe.ingredients))
    .all()
)
```

## Repository Methods

### Get Single Recipe
```python
# With relations (4 queries)
recipe = repository.get_by_id_with_relations(123)

# Without relations (1 query)
recipe = repository.get_by_id(123)
```

### Get List
```python
# With pagination and relations (4 queries)
recipes = repository.get_all(skip=0, limit=50, with_relations=True)

# Lightweight without relations (1 query)
recipes = repository.get_all(skip=0, limit=50, with_relations=False)
```

### Filter by Tags
```python
# With eager loading (4 queries)
recipes = repository.get_by_tags(
    tags=["japanese", "quick"],
    skip=0,
    limit=50,
    with_relations=True
)
```

### Search
```python
# Case-insensitive search with eager loading (4 queries)
results = repository.search("curry", with_relations=True)
```

### Count (for pagination)
```python
# Get total count
total = repository.count(tags=["japanese"])
```

## Service Layer

```python
service = RecipeService(db)

# Get recipes with control over relations
recipes = service.get_recipes(
    skip=0,
    limit=50,
    tags=["japanese"],
    with_relations=True  # Default True
)

# Get count for pagination
total = service.get_recipes_count(tags=["japanese"])
```

## API Endpoints

### List with Pagination
```bash
GET /api/v1/recipes/?skip=0&limit=50
```

### Filter by Tags
```bash
GET /api/v1/recipes/?tags=japanese,quick&limit=20
```

### Search
```bash
GET /api/v1/recipes/search/?q=curry
```

### Get Single
```bash
GET /api/v1/recipes/123
```

### Create
```bash
POST /api/v1/recipes/
Content-Type: application/json

{
  "name": "Recipe Name",
  "ingredients": [
    {"name": "たまねぎ", "quantity": "2", "unit": "個"}
  ],
  "steps": ["Step 1", "Step 2"],
  "tags": ["japanese", "dinner"]
}
```

## Performance Rules

### Rule 1: Always Use Eager Loading for Lists
```python
# ✅ GOOD
recipes = repository.get_all(with_relations=True)

# ❌ BAD
recipes = db.query(Recipe).all()
```

### Rule 2: Always Paginate
```python
# ✅ GOOD
recipes = repository.get_all(skip=0, limit=50)

# ❌ BAD
recipes = repository.get_all(limit=10000)
```

### Rule 3: Use Batch Operations
```python
# ✅ GOOD
items = [Ingredient(...) for data in items]
db.bulk_save_objects(items)

# ❌ BAD
for data in items:
    db.add(Ingredient(...))
    db.commit()
```

### Rule 4: Provide Total Count
```python
# ✅ GOOD
recipes = repository.get_all(skip=0, limit=50)
total = repository.count()
return {"items": recipes, "total": total}

# ❌ BAD
recipes = repository.get_all(skip=0, limit=50)
return recipes  # No total count
```

## Testing

### Run All Tests
```bash
pytest tests/test_performance_optimization.py -v
```

### Test Specific Function
```bash
pytest tests/test_performance_optimization.py::test_list_recipes_query_count_optimized -v
```

### Enable Query Logging
```python
from backend.utils.performance import QueryLogger

logger = QueryLogger()
logger.enable()

# Run your code

stats = logger.get_stats()
print(f"Queries: {stats['total_queries']}")
print(f"Time: {stats['total_time']:.3f}s")

logger.disable()
```

## Query Count Targets

| Operation          | Target | Notes                    |
|-------------------|--------|--------------------------|
| List N recipes    | 4      | Regardless of N          |
| Get single recipe | 4      | With all relations       |
| Search N results  | 4      | Regardless of N          |
| Filter by tags    | 4      | Regardless of N          |
| Create recipe     | ≤10    | With bulk inserts        |
| Update recipe     | ≤15    | With bulk updates        |

## Common Issues

### Issue: Too Many Queries
```python
# Check if you're using the right method
# ❌ DON'T
recipes = db.query(Recipe).all()

# ✅ DO
recipes = repository.get_all(with_relations=True)
```

### Issue: Slow Pagination
```python
# Add indexes
CREATE INDEX idx_recipes_created_at ON recipes(created_at DESC);
```

### Issue: Memory Usage High
```python
# Use smaller page size
recipes = repository.get_all(skip=0, limit=50)  # Not 1000
```

## Monitoring in Development

### Enable SQLAlchemy Echo
```python
# In database.py
engine = create_engine(DATABASE_URL, echo=True)
```

### Use Query Logger
```python
from backend.utils.performance import QueryLogger

logger = QueryLogger()
logger.enable()

# Make requests

print(logger.get_stats())
```

## Response Schema

### Paginated Response
```json
{
  "items": [
    {
      "id": 1,
      "name": "Recipe Name",
      "ingredients": [...],
      "steps": [...],
      "tags": [...]
    }
  ],
  "total": 234,
  "skip": 0,
  "limit": 50
}
```

### Single Recipe Response
```json
{
  "id": 1,
  "name": "Japanese Curry",
  "description": "Delicious curry",
  "ingredients": [
    {
      "id": 1,
      "name": "たまねぎ",
      "quantity": "2",
      "unit": "個",
      "normalized_name": "たまねぎ"
    }
  ],
  "steps": [
    {
      "id": 1,
      "step_number": 1,
      "description": "Cut onions"
    }
  ],
  "tags": [
    {"id": 1, "name": "japanese"},
    {"id": 2, "name": "curry"}
  ],
  "prep_time": 15,
  "cook_time": 30,
  "servings": 4,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

## Cheat Sheet

### Eager Loading Options

```python
from sqlalchemy.orm import selectinload, joinedload

# One-to-many (collections) - USE THIS
.options(selectinload(Recipe.ingredients))

# Many-to-one (single) - Rarely needed
.options(joinedload(Ingredient.recipe))
```

### Batch Operations

```python
# Bulk insert
db.bulk_save_objects(items)

# Bulk update
db.bulk_update_mappings(Model, [{"id": 1, "name": "New"}])

# Bulk delete
db.query(Model).filter(...).delete()
```

### Filtering

```python
# Single filter
.filter(Recipe.name.ilike("%curry%"))

# Multiple filters (AND)
.filter(Recipe.name.ilike("%curry%"), Recipe.prep_time < 30)

# OR filters
from sqlalchemy import or_
.filter(or_(Recipe.name.ilike("%curry%"), Recipe.tags.any(name="curry")))

# IN filter
.filter(Recipe.id.in_([1, 2, 3]))
```

## Performance Targets

- API Response: < 200ms
- List 100 recipes: ~ 85ms
- List 50 recipes: ~ 45ms
- Single recipe: ~ 8ms
- Search: ~ 25ms per 20 results

## File Locations

```
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/
├── backend/
│   ├── repositories/recipe_repository.py  # Data access
│   ├── services/recipe_service.py         # Business logic
│   ├── api/routers/recipes.py            # API endpoints
│   ├── models/recipe.py                   # DB models
│   ├── schemas/recipe.py                  # Validation
│   └── database.py                        # DB config
├── tests/
│   └── test_performance_optimization.py   # Tests
└── docs/
    ├── PERFORMANCE_OPTIMIZATION_REPORT.md
    ├── PERFORMANCE_OPTIMIZATION_README.md
    └── OPTIMIZATION_SUMMARY.md
```

## Help Commands

```bash
# Setup
./setup-performance-optimization.sh

# Test
pytest tests/test_performance_optimization.py -v

# Run with query logging
python -c "from backend.database import engine; engine.echo = True; ..."

# Check CLAUDE.md compliance
black backend/ --check
ruff backend/
```

## Key Takeaways

1. Use `selectinload()` for one-to-many relationships
2. Always paginate with `skip` and `limit`
3. Provide total count for pagination
4. Use batch operations for inserts/updates
5. Monitor query counts in development
6. Target 4 queries for list operations
7. Keep responses under 200ms

---

**Need more details?** See PERFORMANCE_OPTIMIZATION_README.md

**Full analysis?** See PERFORMANCE_OPTIMIZATION_REPORT.md

**Summary?** See OPTIMIZATION_SUMMARY.md

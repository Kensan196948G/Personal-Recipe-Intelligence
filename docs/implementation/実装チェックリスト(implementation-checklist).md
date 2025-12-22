# N+1 Query Optimization - Implementation Checklist

## Phase 1: Setup and Installation (Day 1)

### Environment Setup
- [ ] Navigate to project directory
  ```bash
  cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
  ```

- [ ] Make setup scripts executable
  ```bash
  chmod +x setup-performance-optimization.sh
  chmod +x create-models-and-schemas.sh
  ```

- [ ] Run first setup script
  ```bash
  ./setup-performance-optimization.sh
  ```
  - Creates `backend/repositories/recipe_repository.py`
  - Creates `backend/services/recipe_service.py`
  - Creates `backend/api/routers/recipes.py`

- [ ] Run second setup script
  ```bash
  ./create-models-and-schemas.sh
  ```
  - Creates `backend/models/recipe.py`
  - Creates `backend/api/dependencies.py`
  - Creates `backend/database.py`
  - Creates `backend/utils/performance.py`

- [ ] Verify all files created
  ```bash
  ls -la backend/repositories/recipe_repository.py
  ls -la backend/services/recipe_service.py
  ls -la backend/api/routers/recipes.py
  ls -la backend/models/recipe.py
  ls -la backend/schemas/recipe.py
  ```

### Install Dependencies
- [ ] Install Python dependencies
  ```bash
  cd backend
  pip install sqlalchemy pydantic fastapi uvicorn
  ```

- [ ] Install development dependencies
  ```bash
  pip install pytest black ruff
  ```

- [ ] Verify installations
  ```bash
  python -c "import sqlalchemy; print(sqlalchemy.__version__)"
  python -c "import pydantic; print(pydantic.__version__)"
  python -c "import fastapi; print(fastapi.__version__)"
  ```

## Phase 2: Code Review (Day 1-2)

### Repository Layer Review
- [ ] Review `backend/repositories/recipe_repository.py`
  - [ ] Check `get_by_id_with_relations()` uses `selectinload()`
  - [ ] Check `get_all()` supports `with_relations` parameter
  - [ ] Check `get_by_tags()` uses eager loading
  - [ ] Check `search()` uses eager loading
  - [ ] Check `create()` uses `bulk_save_objects()`
  - [ ] Check `update()` uses batch operations
  - [ ] Check `_normalize_ingredient_name()` handles Japanese characters

### Service Layer Review
- [ ] Review `backend/services/recipe_service.py`
  - [ ] Check all methods have `with_relations` parameter
  - [ ] Check `get_recipes_count()` exists
  - [ ] Check proper delegation to repository

### API Layer Review
- [ ] Review `backend/api/routers/recipes.py`
  - [ ] Check pagination parameters (skip, limit)
  - [ ] Check limit max value is 100
  - [ ] Check all endpoints use eager loading
  - [ ] Check error handling (404 responses)
  - [ ] Check response models are correct

### Model Layer Review
- [ ] Review `backend/models/recipe.py`
  - [ ] Check relationships have `cascade="all, delete-orphan"`
  - [ ] Check foreign keys have `ondelete="CASCADE"`
  - [ ] Check indexes on foreign keys
  - [ ] Check `lazy="select"` on relationships

### Schema Layer Review
- [ ] Review `backend/schemas/recipe.py`
  - [ ] Check validation rules
  - [ ] Check `RecipePaginatedResponse` has helper properties
  - [ ] Check tag normalization in validators

## Phase 3: Testing (Day 2-3)

### Unit Tests
- [ ] Run repository tests
  ```bash
  pytest tests/test_performance_optimization.py::test_list_recipes_query_count_optimized -v
  ```

- [ ] Run service layer tests
  ```bash
  pytest tests/test_performance_optimization.py::test_service_layer_query_optimization -v
  ```

- [ ] Run batch operation tests
  ```bash
  pytest tests/test_performance_optimization.py::test_batch_create_performance -v
  pytest tests/test_performance_optimization.py::test_batch_update_performance -v
  ```

- [ ] Run pagination tests
  ```bash
  pytest tests/test_performance_optimization.py::test_pagination_with_count -v
  ```

### Performance Tests
- [ ] Run query count verification
  ```bash
  pytest tests/test_performance_optimization.py::test_list_recipes_query_count_optimized -v
  ```

- [ ] Run large dataset test
  ```bash
  pytest tests/test_performance_optimization.py::test_large_dataset_performance -v
  ```

- [ ] Run N+1 detection test
  ```bash
  pytest tests/test_performance_optimization.py::test_no_n_plus_1_when_accessing_relations -v
  ```

### Integration Tests
- [ ] Test API endpoints manually
  ```bash
  # Start server
  uvicorn backend.main:app --reload

  # In another terminal
  curl http://localhost:8001/api/v1/recipes/?limit=10
  ```

- [ ] Test pagination
  ```bash
  curl http://localhost:8001/api/v1/recipes/?skip=0&limit=10
  curl http://localhost:8001/api/v1/recipes/?skip=10&limit=10
  ```

- [ ] Test tag filtering
  ```bash
  curl http://localhost:8001/api/v1/recipes/?tags=japanese,quick
  ```

- [ ] Test search
  ```bash
  curl http://localhost:8001/api/v1/recipes/search/?q=curry
  ```

## Phase 4: Database Setup (Day 3)

### Database Initialization
- [ ] Create data directory
  ```bash
  mkdir -p data
  ```

- [ ] Initialize database
  ```python
  from backend.database import init_db
  init_db()
  ```

- [ ] Verify tables created
  ```bash
  sqlite3 data/recipes.db ".tables"
  ```

### Create Indexes
- [ ] Add performance indexes
  ```sql
  CREATE INDEX IF NOT EXISTS idx_recipes_created_at ON recipes(created_at DESC);
  CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name);
  CREATE INDEX IF NOT EXISTS idx_ingredients_recipe_id ON ingredients(recipe_id);
  CREATE INDEX IF NOT EXISTS idx_ingredients_normalized ON ingredients(normalized_name);
  CREATE INDEX IF NOT EXISTS idx_steps_recipe_id ON steps(recipe_id);
  CREATE INDEX IF NOT EXISTS idx_recipe_tags_recipe_id ON recipe_tags(recipe_id);
  CREATE INDEX IF NOT EXISTS idx_recipe_tags_name ON recipe_tags(name);
  ```

- [ ] Verify indexes
  ```bash
  sqlite3 data/recipes.db ".indexes"
  ```

### Test Data
- [ ] Create test recipes
  ```bash
  python -c "
  from backend.database import SessionLocal
  from backend.repositories.recipe_repository import RecipeRepository
  from backend.schemas.recipe import RecipeCreate, IngredientCreate

  db = SessionLocal()
  repo = RecipeRepository(db)

  for i in range(10):
      recipe = RecipeCreate(
          name=f'Test Recipe {i}',
          description='Test description',
          ingredients=[
              IngredientCreate(name='たまねぎ', quantity='1', unit='個'),
              IngredientCreate(name='にんじん', quantity='1', unit='本'),
          ],
          steps=['Step 1', 'Step 2'],
          tags=['test', 'quick']
      )
      repo.create(recipe)

  print('Created 10 test recipes')
  "
  ```

- [ ] Verify test data
  ```bash
  sqlite3 data/recipes.db "SELECT COUNT(*) FROM recipes;"
  ```

## Phase 5: Performance Verification (Day 3-4)

### Query Count Verification
- [ ] Enable query logging
  ```python
  from backend.utils.performance import QueryLogger
  from backend.database import SessionLocal
  from backend.repositories.recipe_repository import RecipeRepository

  logger = QueryLogger()
  logger.enable()

  db = SessionLocal()
  repo = RecipeRepository(db)

  # List 50 recipes
  recipes = repo.get_all(skip=0, limit=50, with_relations=True)

  stats = logger.get_stats()
  print(f"Query count: {stats['total_queries']}")  # Should be 4
  print(f"Total time: {stats['total_time']:.3f}s")
  ```

- [ ] Verify query count is 4 for list operations
- [ ] Verify query count is 4 for single recipe fetch
- [ ] Verify query count is 4 for search operations

### Response Time Verification
- [ ] Measure list endpoint
  ```bash
  time curl http://localhost:8001/api/v1/recipes/?limit=50
  ```

- [ ] Measure search endpoint
  ```bash
  time curl http://localhost:8001/api/v1/recipes/search/?q=test
  ```

- [ ] Measure single recipe endpoint
  ```bash
  time curl http://localhost:8001/api/v1/recipes/1
  ```

- [ ] Verify all responses are under 200ms

### Load Testing
- [ ] Install Apache Bench
  ```bash
  sudo apt-get install apache2-utils
  ```

- [ ] Run load test
  ```bash
  ab -n 1000 -c 10 http://localhost:8001/api/v1/recipes/?limit=50
  ```

- [ ] Verify average response time
- [ ] Verify no failed requests

## Phase 6: Code Quality (Day 4)

### Linting
- [ ] Run Black formatter
  ```bash
  black backend/ --check
  ```

- [ ] Run Ruff linter
  ```bash
  ruff backend/
  ```

- [ ] Fix any issues found

### Type Checking
- [ ] Install mypy
  ```bash
  pip install mypy
  ```

- [ ] Run type checking
  ```bash
  mypy backend/
  ```

- [ ] Fix type errors

### Documentation
- [ ] Review all docstrings
- [ ] Verify README is complete
- [ ] Check CLAUDE.md compliance
  - [ ] 2-space indentation
  - [ ] snake_case naming
  - [ ] Type annotations
  - [ ] 120 char line limit

## Phase 7: Integration (Day 5)

### Backup Existing Code
- [ ] Backup current backend files
  ```bash
  mkdir -p backup
  cp -r backend/ backup/backend_$(date +%Y%m%d)/
  ```

### Replace Files
- [ ] Replace repository files
- [ ] Replace service files
- [ ] Replace API router files
- [ ] Add new model files if needed

### Update Imports
- [ ] Update main.py to include new router
  ```python
  from backend.api.routers import recipes
  app.include_router(recipes.router, prefix="/api/v1")
  ```

- [ ] Verify all imports work
  ```bash
  python -c "from backend.repositories.recipe_repository import RecipeRepository"
  ```

### Migrate Database
- [ ] Create migration script if needed
- [ ] Run migrations
- [ ] Verify data integrity

## Phase 8: Monitoring (Day 5+)

### Enable Logging
- [ ] Add query logging in development
  ```python
  # In database.py
  engine = create_engine(DATABASE_URL, echo=True)
  ```

- [ ] Add slow query logging
  ```python
  # In middleware
  from backend.utils.performance import QueryLogger
  ```

- [ ] Set up log rotation

### Performance Monitoring
- [ ] Track average queries per request
- [ ] Track 95th percentile response time
- [ ] Track database connection pool usage
- [ ] Set up alerts for slow queries (>500ms)

### Create Dashboard
- [ ] Add Grafana or similar monitoring
- [ ] Create performance metrics dashboard
- [ ] Set up alerting rules

## Phase 9: Documentation (Ongoing)

### Update Documentation
- [ ] Update API documentation
- [ ] Add performance notes to README
- [ ] Document query optimization patterns
- [ ] Create runbook for common issues

### Team Training
- [ ] Share QUICK_REFERENCE.md with team
- [ ] Conduct code review session
- [ ] Document best practices
- [ ] Create troubleshooting guide

## Phase 10: Maintenance (Ongoing)

### Weekly Tasks
- [ ] Review slow query logs
- [ ] Check for N+1 query regressions
- [ ] Monitor response times
- [ ] Review error rates

### Monthly Tasks
- [ ] Analyze query patterns
- [ ] Optimize frequently used queries
- [ ] Review and update indexes
- [ ] Clean up old test data

### Quarterly Tasks
- [ ] Performance review
- [ ] Database optimization
- [ ] Code quality audit
- [ ] Update dependencies

## Success Criteria

### Must Have
- [ ] Query count for list operations ≤ 4
- [ ] API response time < 200ms
- [ ] All tests passing
- [ ] No N+1 query regressions
- [ ] CLAUDE.md compliant

### Should Have
- [ ] Query logging enabled in dev
- [ ] Performance monitoring set up
- [ ] Documentation complete
- [ ] Team trained on patterns

### Nice to Have
- [ ] Load test results documented
- [ ] Performance dashboard
- [ ] Automated alerts
- [ ] Cache layer implemented

## Rollback Plan

### If Issues Found
- [ ] Restore from backup
  ```bash
  cp -r backup/backend_YYYYMMDD/ backend/
  ```

- [ ] Restart application
- [ ] Verify functionality
- [ ] Document issues found

### If Performance Degrades
- [ ] Check query counts
- [ ] Enable query logging
- [ ] Review recent changes
- [ ] Consult QUICK_REFERENCE.md

## Sign-off

### Development Team
- [ ] Code reviewed by: __________
- [ ] Date: __________

### QA Team
- [ ] Performance verified by: __________
- [ ] Date: __________

### DevOps Team
- [ ] Monitoring configured by: __________
- [ ] Date: __________

### Product Owner
- [ ] Approved by: __________
- [ ] Date: __________

---

## Notes

Use this checklist to track progress through the implementation. Check off items as completed and add notes for any issues encountered.

**Current Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

**Last Updated:** 2024-12-11

**Next Review:** __________

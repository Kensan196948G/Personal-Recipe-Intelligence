# Test Suite Recommendations
## Personal Recipe Intelligence Project

**Date:** 2025-12-11
**Prepared by:** QA Engineer Agent

---

## Overview

This document provides specific, actionable recommendations for building a comprehensive test suite for the Personal Recipe Intelligence (PRI) project, following the guidelines in CLAUDE.md.

---

## 1. Test Infrastructure Setup

### 1.1 Directory Structure

Create the following directory structure:

```
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/
├── tests/                    # Root-level integration and E2E tests
│   ├── __init__.py
│   ├── conftest.py          # Shared pytest fixtures
│   ├── integration/         # Integration tests
│   │   ├── __init__.py
│   │   ├── test_recipe_workflow.py
│   │   └── test_api_integration.py
│   └── e2e/                 # End-to-end tests
│       ├── __init__.py
│       └── test_user_workflows.py
├── backend/tests/           # Backend unit tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_recipe_parser.py
│   ├── test_web_scraper.py
│   ├── test_ocr_service.py
│   ├── test_database.py
│   └── test_api_routes.py
└── frontend/tests/          # Frontend tests
    ├── components/
    │   ├── RecipeCard.test.js
    │   └── SearchBar.test.js
    └── integration/
        └── api-client.test.js
```

### 1.2 Configuration Files

**pytest.ini** (root directory):
```ini
[pytest]
testpaths = tests backend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --strict-markers
    --cov=backend
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=60
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    web: Tests requiring web scraping
    ocr: Tests requiring OCR functionality
```

**package.json** (frontend test scripts):
```json
{
  "scripts": {
    "test": "bun test",
    "test:watch": "bun test --watch",
    "test:coverage": "bun test --coverage"
  }
}
```

---

## 2. Backend Unit Tests

### 2.1 Recipe Parser Tests

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_recipe_parser.py`

**Test Coverage:**
- Parse ingredients from text
- Parse cooking steps
- Handle malformed input
- Normalize ingredient names
- Extract quantities and units
- Handle special characters and Unicode

**Specific Tests:**
```python
def test_parse_ingredients_basic()
def test_parse_ingredients_with_fractions()
def test_parse_ingredients_unicode()
def test_parse_steps_numbered()
def test_parse_steps_bulleted()
def test_normalize_ingredient_names()
def test_extract_quantity_and_unit()
def test_handle_missing_data()
def test_parse_cooking_time()
def test_parse_servings()
```

### 2.2 Web Scraper Tests

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_web_scraper.py`

**Test Coverage:**
- Fetch recipe from URL (mocked)
- Extract recipe data from HTML
- Handle different recipe sites
- Handle network errors
- Rate limiting
- Invalid URLs

**Specific Tests:**
```python
@pytest.mark.web
def test_scrape_recipe_url_success()

@pytest.mark.web
def test_scrape_recipe_invalid_url()

@pytest.mark.web
def test_scrape_recipe_timeout()

def test_extract_recipe_from_html()

def test_extract_recipe_schema_org()

def test_handle_missing_elements()

def test_extract_image_url()
```

**Mock Strategy:**
- Mock HTTP requests using `responses` or `pytest-httpx`
- Use fixture HTML files for different recipe sites
- Mock Puppeteer/Browser MCP responses

### 2.3 OCR Service Tests

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_ocr_service.py`

**Test Coverage:**
- Extract text from image
- Handle different image formats
- Handle corrupted images
- Post-process OCR results
- Clean up temporary files

**Specific Tests:**
```python
@pytest.mark.ocr
def test_extract_text_from_image()

@pytest.mark.ocr
def test_handle_invalid_image()

@pytest.mark.ocr
def test_cleanup_temp_files()

def test_preprocess_image()

def test_postprocess_ocr_text()
```

**Mock Strategy:**
- Mock OCR engine (Tesseract/Cloud API)
- Use sample test images in `tests/fixtures/images/`
- Mock file system operations where appropriate

### 2.4 Database Tests

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_database.py`

**Test Coverage:**
- Create recipe
- Read recipe
- Update recipe
- Delete recipe
- Search recipes
- Filter by tags
- Database migrations
- Backup/restore

**Specific Tests:**
```python
def test_create_recipe()

def test_read_recipe_by_id()

def test_update_recipe()

def test_delete_recipe()

def test_search_recipes_by_name()

def test_filter_recipes_by_tag()

def test_get_all_recipes()

def test_duplicate_recipe_name()

def test_cascade_delete_tags()
```

**Setup:**
- Use in-memory SQLite for tests
- Create fresh database for each test
- Use pytest fixtures for test data

### 2.5 API Routes Tests

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_api_routes.py`

**Test Coverage:**
- GET /api/v1/recipes
- POST /api/v1/recipes
- PUT /api/v1/recipes/{id}
- DELETE /api/v1/recipes/{id}
- GET /api/v1/recipes/search
- POST /api/v1/recipes/from-url
- POST /api/v1/recipes/from-image
- Error responses
- Input validation

**Specific Tests:**
```python
def test_get_recipes_list()

def test_get_recipe_by_id()

def test_create_recipe_success()

def test_create_recipe_invalid_data()

def test_update_recipe()

def test_delete_recipe()

def test_search_recipes()

def test_create_recipe_from_url()

def test_create_recipe_from_image()

def test_authentication_required()

def test_rate_limiting()
```

**Setup:**
- Use FastAPI TestClient or similar
- Mock database operations
- Test response formats match spec

---

## 3. Integration Tests

### 3.1 Recipe Workflow Test

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/integration/test_recipe_workflow.py`

**Test Coverage:**
- Complete workflow: URL → Parser → Database → API
- OCR → Parser → Database → API
- Search and filter workflows
- Tag management workflows

**Specific Tests:**
```python
@pytest.mark.integration
def test_url_to_database_workflow()

@pytest.mark.integration
def test_ocr_to_database_workflow()

@pytest.mark.integration
def test_search_and_filter_workflow()

@pytest.mark.integration
def test_recipe_update_workflow()
```

### 3.2 API Integration Test

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/integration/test_api_integration.py`

**Test Coverage:**
- API server startup
- Database connectivity
- External service integration (mocked)
- Error propagation through layers

**Specific Tests:**
```python
@pytest.mark.integration
def test_api_server_starts()

@pytest.mark.integration
def test_database_connection()

@pytest.mark.integration
def test_end_to_end_recipe_creation()
```

---

## 4. Frontend Tests

### 4.1 Component Tests

**Files:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend/tests/components/*.test.js`

**Components to Test:**
- RecipeCard
- RecipeList
- SearchBar
- FilterPanel
- RecipeForm
- ImageUpload

**Example - RecipeCard.test.js:**
```javascript
import { describe, it, expect } from 'bun:test';
import { render } from '@testing-library/react';
import RecipeCard from '../src/components/RecipeCard';

describe('RecipeCard', () => {
  it('renders recipe name', () => {
    const recipe = { name: 'Test Recipe', ingredients: [] };
    const { getByText } = render(<RecipeCard recipe={recipe} />);
    expect(getByText('Test Recipe')).toBeDefined();
  });

  it('displays ingredients count', () => {
    // Test implementation
  });

  it('handles click event', () => {
    // Test implementation
  });
});
```

### 4.2 API Client Tests

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend/tests/integration/api-client.test.js`

**Test Coverage:**
- Fetch recipes
- Create recipe
- Update recipe
- Delete recipe
- Error handling
- Request timeout

---

## 5. End-to-End Tests

### 5.1 User Workflow Tests

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/e2e/test_user_workflows.py`

**Test Coverage:**
- User adds recipe from URL
- User adds recipe from image
- User searches for recipes
- User updates recipe
- User deletes recipe

**Note:** E2E tests are lower priority for individual use. Focus on unit and integration tests first.

---

## 6. Test Fixtures and Helpers

### 6.1 Shared Fixtures

**File:** `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/conftest.py`

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing"""
    return {
        "name": "Test Recipe",
        "ingredients": [
            {"name": "flour", "quantity": 2, "unit": "cups"},
            {"name": "sugar", "quantity": 1, "unit": "cup"}
        ],
        "steps": [
            "Mix ingredients",
            "Bake at 350F for 30 minutes"
        ],
        "tags": ["dessert", "baking"]
    }

@pytest.fixture
def sample_html_recipe():
    """Load sample HTML recipe from fixtures"""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_recipe.html"
    return fixture_path.read_text()

@pytest.fixture
def temp_database():
    """Create temporary SQLite database for testing"""
    # Implementation
    pass

@pytest.fixture
def mock_web_scraper():
    """Mock web scraper for tests"""
    # Implementation
    pass
```

### 6.2 Test Data Files

Create directory: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/fixtures/`

**Contents:**
- `sample_recipe.html` - Sample recipe HTML
- `sample_recipe.json` - Sample recipe JSON
- `images/sample_recipe.jpg` - Sample recipe image for OCR
- `malformed_data.json` - Test edge cases

---

## 7. Mock Strategy

### 7.1 External Dependencies to Mock

1. **Web Scraping (Browser/Puppeteer MCP)**
   - Mock HTTP responses
   - Use fixture HTML files
   - Simulate network errors

2. **OCR Engine**
   - Mock OCR API calls
   - Return predefined text for test images

3. **File System (where appropriate)**
   - Use temporary directories
   - Clean up after tests

4. **Database (for unit tests)**
   - Use in-memory SQLite
   - Reset between tests

### 7.2 Mock Libraries

- Python: `unittest.mock`, `pytest-mock`, `responses`, `pytest-httpx`
- JavaScript: `jest` mocks (if using Jest) or custom mocks for Bun

---

## 8. Coverage Goals

### 8.1 Target Coverage

Per CLAUDE.md requirements:
- **Minimum: 60% overall coverage**
- **Recommended: 80%+ for critical paths**

### 8.2 Priority Areas

**Must have 80%+ coverage:**
- Recipe parser
- Database operations
- API routes
- Data validation

**Can have lower coverage:**
- UI components (60%+)
- Utility functions (60%+)
- Error handlers (60%+)

---

## 9. Implementation Phases

### Phase 1: Foundation (Week 1)
1. Create test directory structure
2. Set up pytest.ini and test configs
3. Create conftest.py with shared fixtures
4. Add test_database.py with basic CRUD tests
5. Verify tests run successfully

**Success Criteria:**
- Test infrastructure working
- Basic database tests passing
- Coverage reporting enabled

### Phase 2: Core Functionality (Week 2)
1. Add test_recipe_parser.py (complete)
2. Add test_api_routes.py (complete)
3. Add test_web_scraper.py (mocked)
4. Achieve 60%+ coverage

**Success Criteria:**
- All core modules have unit tests
- 60% minimum coverage achieved
- All tests passing

### Phase 3: Integration & Edge Cases (Week 3)
1. Add integration tests
2. Add OCR tests (mocked)
3. Add frontend component tests
4. Test error scenarios
5. Achieve 70%+ coverage

**Success Criteria:**
- Integration tests passing
- Edge cases covered
- 70% coverage achieved

### Phase 4: Enhancement (Week 4)
1. Add performance tests
2. Add security tests (input validation)
3. Improve coverage to 80%+
4. Document test strategy

**Success Criteria:**
- 80% coverage
- All critical paths tested
- Documentation complete

---

## 10. Continuous Testing

### 10.1 Pre-commit Checks

Create `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/test.sh`:

```bash
#!/bin/bash
# Run all tests before commit

echo "Running linters..."
python -m ruff check backend/
python -m black --check backend/

echo "Running tests..."
python -m pytest tests/ backend/tests/ --cov --cov-fail-under=60

echo "Running frontend tests..."
cd frontend && bun test

echo "All checks passed!"
```

### 10.2 Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# Run specific test file
pytest backend/tests/test_recipe_parser.py

# Run tests by marker
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run with verbose output
pytest -v

# Run frontend tests
cd frontend && bun test
```

---

## 11. Common Testing Patterns

### 11.1 Arrange-Act-Assert Pattern

```python
def test_create_recipe():
    # Arrange
    recipe_data = {"name": "Test", "ingredients": []}

    # Act
    result = create_recipe(recipe_data)

    # Assert
    assert result.name == "Test"
    assert len(result.ingredients) == 0
```

### 11.2 Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("1 cup flour", {"quantity": 1, "unit": "cup", "name": "flour"}),
    ("2 tablespoons sugar", {"quantity": 2, "unit": "tablespoons", "name": "sugar"}),
])
def test_parse_ingredient(input, expected):
    result = parse_ingredient(input)
    assert result == expected
```

### 11.3 Exception Testing

```python
def test_invalid_recipe_raises_error():
    with pytest.raises(ValidationError):
        create_recipe({"invalid": "data"})
```

---

## 12. Specific Module Test Requirements

### Recipe Parser Module

**Priority:** CRITICAL
**Target Coverage:** 90%

Required tests:
- [ ] Parse plain text ingredients
- [ ] Parse ingredients with fractions (1/2, ¾)
- [ ] Parse metric and imperial units
- [ ] Normalize ingredient names (onion/onions → onion)
- [ ] Handle Unicode characters (Japanese, Chinese)
- [ ] Parse numbered steps
- [ ] Parse bulleted steps
- [ ] Extract cooking time and temperature
- [ ] Handle malformed input gracefully

### Web Scraper Module

**Priority:** HIGH
**Target Coverage:** 80%

Required tests:
- [ ] Mock successful URL fetch
- [ ] Handle 404 errors
- [ ] Handle timeout errors
- [ ] Extract schema.org recipe data
- [ ] Extract recipe from various HTML structures
- [ ] Respect robots.txt (if implemented)
- [ ] Extract recipe images
- [ ] Handle JavaScript-rendered content

### Database Module

**Priority:** CRITICAL
**Target Coverage:** 90%

Required tests:
- [ ] CRUD operations for recipes
- [ ] CRUD operations for tags
- [ ] Search functionality
- [ ] Filter functionality
- [ ] Relationship integrity (cascades)
- [ ] Transaction handling
- [ ] Migration tests
- [ ] Backup and restore

### API Routes Module

**Priority:** CRITICAL
**Target Coverage:** 85%

Required tests:
- [ ] All GET endpoints
- [ ] All POST endpoints
- [ ] All PUT endpoints
- [ ] All DELETE endpoints
- [ ] Input validation
- [ ] Error responses (400, 404, 500)
- [ ] Authentication (if implemented)
- [ ] Response format validation

### OCR Module

**Priority:** MEDIUM
**Target Coverage:** 70%

Required tests:
- [ ] Mock OCR text extraction
- [ ] Handle different image formats
- [ ] Handle corrupted images
- [ ] Text post-processing
- [ ] Temporary file cleanup

---

## 13. Anti-Patterns to Avoid

1. **Testing Implementation Details**
   - Don't test internal private methods
   - Test public interfaces and behavior

2. **Brittle Tests**
   - Avoid hardcoding dates/times
   - Use fixtures and factories

3. **Dependent Tests**
   - Each test should be independent
   - Don't rely on test execution order

4. **Missing Mocks**
   - Always mock external services
   - Don't make real HTTP requests in tests

5. **Ignoring Edge Cases**
   - Test empty inputs
   - Test maximum values
   - Test special characters

---

## 14. Success Metrics

Track these metrics to measure test suite quality:

- **Coverage Percentage:** Target 60% minimum, 80% ideal
- **Test Execution Time:** < 30 seconds for unit tests
- **Test Reliability:** 0 flaky tests
- **Test Count:** Aim for 100+ meaningful tests
- **Bug Detection Rate:** Tests should catch bugs before production

---

## 15. Resources and Tools

### Testing Libraries

**Python:**
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `pytest-asyncio` - Async test support
- `responses` - HTTP request mocking
- `factory_boy` - Test data factories

**JavaScript:**
- `bun:test` - Built-in test framework
- `@testing-library/react` - Component testing
- Custom mocks for API calls

### Documentation

- pytest documentation: https://docs.pytest.org/
- Bun test docs: https://bun.sh/docs/cli/test
- CLAUDE.md project rules: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/CLAUDE.md`

---

## 16. Next Steps

To implement this test strategy:

1. **Review this document** with the development team
2. **Create test infrastructure** (directories, configs)
3. **Start with Phase 1** (Foundation)
4. **Write tests incrementally** alongside new features
5. **Monitor coverage** and adjust strategy as needed
6. **Iterate and improve** based on findings

---

**Document Version:** 1.0
**Last Updated:** 2025-12-11
**Status:** DRAFT - Ready for Implementation


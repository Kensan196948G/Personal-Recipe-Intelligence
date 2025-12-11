# Testing Guide - Personal Recipe Intelligence

## Overview
This directory contains comprehensive tests for the Personal Recipe Intelligence application, designed to achieve 60%+ test coverage.

## Test Structure

```
backend/tests/
├── conftest.py                              # Basic fixtures
├── conftest_enhanced.py                     # Enhanced fixtures with more test data
├── test_recipe_service_comprehensive.py     # Recipe service CRUD tests (24 tests)
├── test_search_service.py                   # Search functionality tests (23 tests)
├── test_recipes_router.py                   # API endpoint tests (28 tests)
├── test_security.py                         # Security utilities tests (40 tests)
├── test_utils.py                            # Utility functions tests (48 tests)
├── test_database.py                         # Database operations tests (30 tests)
├── test_recipe_parser.py                    # Recipe parsing tests (30 tests)
├── test_integration.py                      # Integration tests (25 tests)
├── pytest.ini                               # Pytest configuration
├── TEST_COVERAGE_SUMMARY.md                 # Detailed coverage documentation
└── README_TESTING.md                        # This file
```

**Total: 248 tests**

---

## Quick Start

### 1. Install Dependencies
```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pip install pytest pytest-cov pytest-mock sqlalchemy fastapi
```

### 2. Run All Tests
```bash
# From project root
python -m pytest backend/tests/ -v

# With coverage report
python -m pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term
```

### 3. View Coverage Report
```bash
# Coverage report will be in htmlcov/index.html
# Open in browser or use CLI to view
cat htmlcov/index.html  # View raw HTML
```

---

## Running Specific Tests

### By Test File
```bash
# Recipe service tests
python -m pytest backend/tests/test_recipe_service_comprehensive.py -v

# Search tests
python -m pytest backend/tests/test_search_service.py -v

# API tests
python -m pytest backend/tests/test_recipes_router.py -v

# Integration tests
python -m pytest backend/tests/test_integration.py -v
```

### By Test Class
```bash
# Run specific test class
python -m pytest backend/tests/test_recipe_service_comprehensive.py::TestRecipeServiceCreate -v
```

### By Test Function
```bash
# Run specific test function
python -m pytest backend/tests/test_recipe_service_comprehensive.py::TestRecipeServiceCreate::test_create_recipe_success -v
```

### By Marker
```bash
# Run unit tests only
python -m pytest -m unit

# Run integration tests only
python -m pytest -m integration

# Run API tests only
python -m pytest -m api
```

---

## Test Categories

### Unit Tests
Focus on individual components in isolation:
- `test_recipe_service_comprehensive.py`
- `test_search_service.py`
- `test_security.py`
- `test_utils.py`
- `test_database.py`
- `test_recipe_parser.py`

### Integration Tests
Test multiple components working together:
- `test_integration.py`

### API Tests
Test HTTP endpoints and request/response handling:
- `test_recipes_router.py`

---

## Coverage Goals

| Component | Target | Tests | Status |
|-----------|--------|-------|--------|
| recipe_service.py | 80%+ | 24 | ✓ Covered |
| search_service.py | 80%+ | 23 | ✓ Covered |
| recipes.py (router) | 70%+ | 28 | ✓ Covered |
| security.py | 60%+ | 40 | ✓ Covered |
| utils.py | 60%+ | 48 | ✓ Covered |
| database.py | 70%+ | 30 | ✓ Covered |
| recipe_parser.py | 60%+ | 30 | ✓ Covered |
| Integration | 50%+ | 25 | ✓ Covered |

**Overall Target: 60%+**

---

## Test Fixtures

### Basic Fixtures (conftest.py)
- `db_session`: In-memory SQLite database session
- `sample_recipe`: Sample recipe object
- `sample_recipe_dict`: Recipe data as dictionary
- `multiple_recipes`: Multiple recipes in database
- `mock_recipe_data`: Mock data for API testing

### Enhanced Fixtures (conftest_enhanced.py)
- `invalid_recipe_data`: For validation testing
- `minimal_recipe_data`: Minimal valid data
- `japanese_recipe_data`: Unicode/multilingual testing
- `recipe_with_all_fields`: Complete data testing
- `search_test_recipes`: Recipes for search testing
- `mock_html_recipe`: HTML content for parser testing
- `large_recipe_set`: Performance testing (100 recipes)
- `reset_database`: Auto-cleanup between tests

---

## Writing New Tests

### Test Template
```python
"""
Brief description of what this test file covers
"""

import pytest
from backend.services.your_service import YourService


class TestYourFeature:
  """Test suite for YourFeature"""

  def test_feature_success(self, db_session):
    """Test successful operation"""
    service = YourService(db_session)

    result = service.your_method()

    assert result is not None
    assert result.expected_field == "expected_value"

  def test_feature_error_case(self, db_session):
    """Test error handling"""
    service = YourService(db_session)

    with pytest.raises(ValueError):
      service.your_method(invalid_input)
```

### Best Practices
1. **One assertion per test**: Focus each test on one behavior
2. **Use descriptive names**: `test_create_recipe_with_empty_title_fails`
3. **Test both paths**: Happy path and error cases
4. **Use fixtures**: Reuse setup code via fixtures
5. **Mock external dependencies**: Database, APIs, file system
6. **Keep tests independent**: Tests should not depend on each other
7. **Add docstrings**: Explain what each test verifies

---

## Common Test Patterns

### Testing CRUD Operations
```python
def test_create_read_update_delete(self, db_session):
  """Test complete CRUD workflow"""
  service = RecipeService(db_session)

  # Create
  recipe = service.create_recipe({"title": "Test", ...})
  assert recipe.id is not None

  # Read
  retrieved = service.get_recipe_by_id(recipe.id)
  assert retrieved.title == "Test"

  # Update
  updated = service.update_recipe(recipe.id, {"title": "Updated"})
  assert updated.title == "Updated"

  # Delete
  deleted = service.delete_recipe(recipe.id)
  assert deleted is True
```

### Testing Validation
```python
def test_validation_error(self, db_session):
  """Test that validation catches invalid data"""
  service = RecipeService(db_session)

  with pytest.raises(ValueError) as exc_info:
    service.create_recipe({"title": ""})

  assert "title cannot be empty" in str(exc_info.value)
```

### Testing Search
```python
def test_search_returns_correct_results(self, db_session):
  """Test search functionality"""
  # Arrange
  service = RecipeService(db_session)
  search = SearchService(db_session)
  service.create_recipe({"title": "Pasta", ...})
  service.create_recipe({"title": "Pizza", ...})

  # Act
  results = search.search_by_title("Pasta")

  # Assert
  assert len(results) == 1
  assert results[0].title == "Pasta"
```

---

## Debugging Tests

### Run with Verbose Output
```bash
python -m pytest backend/tests/ -vv
```

### Show Print Statements
```bash
python -m pytest backend/tests/ -s
```

### Stop at First Failure
```bash
python -m pytest backend/tests/ -x
```

### Run Last Failed Tests
```bash
python -m pytest backend/tests/ --lf
```

### Show Local Variables on Failure
```bash
python -m pytest backend/tests/ -l
```

### Use Debugger
```bash
python -m pytest backend/tests/ --pdb
```

---

## Continuous Integration

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running tests..."
python -m pytest backend/tests/ --cov=backend --cov-fail-under=60

if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
```

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest backend/tests/ --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Performance Testing

### Measure Test Execution Time
```bash
python -m pytest backend/tests/ --durations=10
```

### Run Only Fast Tests
```bash
python -m pytest backend/tests/ -m "not slow"
```

---

## Troubleshooting

### Tests Fail with Database Errors
- Ensure in-memory SQLite is working: `python -c "import sqlite3; print(sqlite3.version)"`
- Check that models are imported correctly
- Verify fixtures are properly set up

### Import Errors
- Ensure `PYTHONPATH` includes project root
- Run from project root directory
- Check `__init__.py` files exist in all packages

### Fixture Not Found
- Ensure `conftest.py` is in the correct location
- Check fixture name spelling
- Verify fixture scope is correct

### Coverage Not Generated
- Install pytest-cov: `pip install pytest-cov`
- Run with coverage flags: `--cov=backend`
- Check .coveragerc configuration

---

## Maintenance Checklist

### Daily
- [ ] Run full test suite before committing
- [ ] Fix any failing tests immediately

### Weekly
- [ ] Check test coverage percentage
- [ ] Review and update flaky tests
- [ ] Clean up obsolete tests

### Monthly
- [ ] Review test execution time
- [ ] Optimize slow tests
- [ ] Update test documentation
- [ ] Add tests for new features

---

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **SQLAlchemy Testing**: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html

---

## Contact

For questions or issues with the test suite, please refer to:
- TEST_COVERAGE_SUMMARY.md for detailed test information
- Project CLAUDE.md for development guidelines
- pytest.ini for test configuration

---

**Last Updated**: 2025-12-11
**Test Count**: 248 tests
**Target Coverage**: 60%+
**Status**: Ready for execution

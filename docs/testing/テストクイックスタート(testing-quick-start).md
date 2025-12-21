# Testing Quick Start Guide
## Personal Recipe Intelligence Project

**Goal:** Get your first tests running in under 30 minutes

---

## Step 1: Install Test Dependencies (5 minutes)

### Backend (Python)
```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# Install pytest and related tools
pip install pytest pytest-cov pytest-asyncio pytest-mock responses

# Verify installation
pytest --version
```

### Frontend (JavaScript)
```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend

# Bun has built-in test support, no installation needed
bun --version
```

---

## Step 2: Create Test Directory Structure (5 minutes)

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# Create backend test directories
mkdir -p backend/tests
touch backend/tests/__init__.py
touch backend/tests/conftest.py

# Create root test directories
mkdir -p tests/fixtures
mkdir -p tests/integration
mkdir -p tests/e2e
touch tests/__init__.py
touch tests/conftest.py

# Create frontend test directories
mkdir -p frontend/tests/components
mkdir -p frontend/tests/integration
```

---

## Step 3: Create pytest.ini (2 minutes)

Create file at `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/pytest.ini`:

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
    --cov-report=term-missing
    --cov-report=html:coverage_html
    --cov-fail-under=60
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    web: Tests requiring web scraping
    ocr: Tests requiring OCR functionality
```

---

## Step 4: Create Your First Test (5 minutes)

### Simple Database Test

Create file at `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_database_basic.py`:

```python
"""
Basic database tests to verify test infrastructure
"""
import pytest


class TestDatabaseBasic:
    """Basic database test suite"""

    def test_simple_assertion(self):
        """Verify test framework is working"""
        assert True

    def test_basic_math(self):
        """Test basic operations"""
        assert 1 + 1 == 2
        assert 2 * 3 == 6

    def test_string_operations(self):
        """Test string handling"""
        recipe_name = "Test Recipe"
        assert recipe_name.lower() == "test recipe"
        assert len(recipe_name) == 11

    @pytest.mark.unit
    def test_list_operations(self):
        """Test list handling"""
        ingredients = ["flour", "sugar", "eggs"]
        assert len(ingredients) == 3
        assert "flour" in ingredients

    @pytest.mark.unit
    def test_dict_operations(self):
        """Test dictionary handling"""
        recipe = {
            "name": "Test",
            "ingredients": [],
            "steps": []
        }
        assert recipe["name"] == "Test"
        assert isinstance(recipe["ingredients"], list)
```

---

## Step 5: Run Your First Tests (2 minutes)

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov

# Run specific test file
pytest backend/tests/test_database_basic.py

# Run tests with specific marker
pytest -m unit
```

### Expected Output:
```
======================== test session starts =========================
collected 5 items

backend/tests/test_database_basic.py .....                     [100%]

========================= 5 passed in 0.02s ==========================
```

---

## Step 6: Add Fixtures (5 minutes)

Update `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/conftest.py`:

```python
"""
Shared test fixtures for Personal Recipe Intelligence
"""
import pytest
from pathlib import Path


@pytest.fixture
def sample_recipe_data():
    """Standard sample recipe for testing"""
    return {
        "name": "Test Recipe",
        "ingredients": [
            {"name": "flour", "quantity": 2, "unit": "cups"},
            {"name": "sugar", "quantity": 1, "unit": "cup"},
            {"name": "eggs", "quantity": 3, "unit": "whole"}
        ],
        "steps": [
            "Preheat oven to 350F",
            "Mix dry ingredients",
            "Add wet ingredients",
            "Bake for 30 minutes"
        ],
        "tags": ["dessert", "baking"],
        "prep_time": 15,
        "cook_time": 30,
        "servings": 8
    }


@pytest.fixture
def sample_ingredients():
    """Sample ingredient list"""
    return [
        "2 cups all-purpose flour",
        "1 cup sugar",
        "3 eggs",
        "1/2 teaspoon salt",
        "1 tablespoon vanilla extract"
    ]


@pytest.fixture
def sample_steps():
    """Sample cooking steps"""
    return [
        "Preheat oven to 350F",
        "Mix flour and sugar",
        "Add eggs one at a time",
        "Pour into greased pan",
        "Bake for 30 minutes"
    ]
```

---

## Step 7: Create Test with Fixtures (5 minutes)

Create file at `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_with_fixtures.py`:

```python
"""
Tests demonstrating fixture usage
"""
import pytest


class TestFixtures:
    """Test suite using fixtures"""

    def test_recipe_data_structure(self, sample_recipe_data):
        """Test recipe data structure is correct"""
        assert "name" in sample_recipe_data
        assert "ingredients" in sample_recipe_data
        assert "steps" in sample_recipe_data

    def test_recipe_has_ingredients(self, sample_recipe_data):
        """Test recipe has ingredients"""
        assert len(sample_recipe_data["ingredients"]) > 0
        first_ingredient = sample_recipe_data["ingredients"][0]
        assert "name" in first_ingredient
        assert "quantity" in first_ingredient
        assert "unit" in first_ingredient

    def test_recipe_has_steps(self, sample_recipe_data):
        """Test recipe has cooking steps"""
        assert len(sample_recipe_data["steps"]) > 0
        assert isinstance(sample_recipe_data["steps"], list)

    def test_ingredients_parsing(self, sample_ingredients):
        """Test ingredient list can be processed"""
        assert len(sample_ingredients) == 5
        assert "flour" in sample_ingredients[0]
        assert "eggs" in sample_ingredients[2]

    @pytest.mark.parametrize("step_number,expected_word", [
        (0, "Preheat"),
        (1, "Mix"),
        (2, "Add"),
        (3, "Pour"),
        (4, "Bake")
    ])
    def test_steps_content(self, sample_steps, step_number, expected_word):
        """Test each step contains expected keyword"""
        assert expected_word in sample_steps[step_number]
```

Run tests:
```bash
pytest backend/tests/test_with_fixtures.py -v
```

---

## Step 8: Create Test Script (3 minutes)

Create `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/test.sh`:

```bash
#!/bin/bash
# Test runner script for Personal Recipe Intelligence

set -e  # Exit on error

echo "================================"
echo "Personal Recipe Intelligence"
echo "Test Suite Runner"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${YELLOW}Running Python tests...${NC}"
python -m pytest tests/ backend/tests/ \
    --verbose \
    --cov=backend \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python tests passed${NC}"
else
    echo -e "${RED}✗ Python tests failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Running frontend tests...${NC}"
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        bun test || echo "No frontend tests found"
        cd ..
    fi
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}All tests completed!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Coverage report generated in: coverage_html/index.html"
```

Make it executable:
```bash
chmod +x /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/test.sh
```

Run all tests:
```bash
./test.sh
```

---

## Step 9: View Coverage Report (2 minutes)

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# Generate coverage report
pytest --cov --cov-report=html

# Coverage report is in: coverage_html/index.html
# Open in browser or view summary in terminal
```

---

## Next Steps: Adding Real Tests

### Option 1: Database Tests

If you have a database module, create `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_database_real.py`:

```python
"""
Real database tests (adapt to your actual database module)
"""
import pytest


class TestDatabase:
    """Database operation tests"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database for testing"""
        # Replace with your actual database initialization
        # Example: db = Database(":memory:")
        # db.create_tables()
        # yield db
        # db.close()
        return {"recipes": {}}  # Placeholder

    def test_database_exists(self, mock_db):
        """Verify database can be created"""
        assert mock_db is not None

    # Add more tests based on your actual database module
```

### Option 2: Parser Tests

Create `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_parser.py`:

```python
"""
Recipe parser tests (adapt to your actual parser module)
"""
import pytest


class TestParser:
    """Recipe parser tests"""

    def test_parse_simple_ingredient(self):
        """Test parsing simple ingredient"""
        # Example: result = parse_ingredient("2 cups flour")
        # assert result["quantity"] == 2
        # assert result["unit"] == "cups"
        # assert result["name"] == "flour"
        pass  # Implement based on your parser

    def test_parse_ingredient_with_fraction(self):
        """Test parsing ingredient with fraction"""
        # Example: result = parse_ingredient("1/2 cup sugar")
        pass  # Implement based on your parser
```

---

## Common Issues & Solutions

### Issue 1: pytest not found
**Solution:**
```bash
pip install pytest
# or
python -m pip install pytest
```

### Issue 2: Module not found errors
**Solution:**
```bash
# Make sure you're in the project root
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
```

### Issue 3: No tests collected
**Solution:**
```bash
# Verify test file naming (must start with test_)
# Verify test functions start with test_
# Check pytest.ini configuration
pytest --collect-only  # See what pytest finds
```

### Issue 4: Import errors in tests
**Solution:**
```python
# Use absolute imports in tests
from backend.module import function

# Or add to conftest.py:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

## Quick Reference Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific file
pytest backend/tests/test_database.py

# Run specific test
pytest backend/tests/test_database.py::TestDatabase::test_create

# Run with markers
pytest -m unit
pytest -m "not slow"

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run tests in parallel (install pytest-xdist first)
pytest -n auto
```

---

## Checklist

- [ ] Test dependencies installed
- [ ] Directory structure created
- [ ] pytest.ini created
- [ ] First test file created
- [ ] Tests run successfully
- [ ] Fixtures added
- [ ] Test script created
- [ ] Coverage report generated
- [ ] Ready to add real tests

---

## What's Next?

1. **Review comprehensive documentation:**
   - `TEST_SUITE_ANALYSIS_SUMMARY.md` - Overview and roadmap
   - `TEST_RECOMMENDATIONS.md` - Detailed specifications
   - `TEST_TEMPLATES.md` - Ready-to-use templates

2. **Start implementing Phase 1:**
   - Add database tests
   - Add API tests
   - Achieve 20% coverage

3. **Gradually increase coverage:**
   - Follow the phase plan
   - Add tests incrementally
   - Target 60% minimum

---

## Success Criteria

You've successfully set up testing when:
- pytest runs without errors
- At least 5 tests pass
- Coverage report generates
- Test script works

---

**Time to Complete:** 30 minutes
**Difficulty:** Beginner
**Status:** Production Ready


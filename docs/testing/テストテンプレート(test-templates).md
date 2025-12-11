# Test Templates
## Personal Recipe Intelligence Project

Ready-to-use test templates following CLAUDE.md guidelines.

---

## Backend Test Templates

### Template 1: Recipe Parser Unit Test

```python
# File: backend/tests/test_recipe_parser.py

import pytest
from backend.services.recipe_parser import RecipeParser

class TestRecipeParser:
    """Test suite for recipe parsing functionality"""

    @pytest.fixture
    def parser(self):
        """Create parser instance for tests"""
        return RecipeParser()

    @pytest.fixture
    def sample_ingredient_text(self):
        """Sample ingredient text for testing"""
        return """
        2 cups all-purpose flour
        1/2 cup sugar
        1 teaspoon vanilla extract
        3 eggs
        """

    def test_parse_ingredients_basic(self, parser, sample_ingredient_text):
        """Test basic ingredient parsing"""
        # Arrange
        expected_count = 4

        # Act
        result = parser.parse_ingredients(sample_ingredient_text)

        # Assert
        assert len(result) == expected_count
        assert result[0]["name"] == "all-purpose flour"
        assert result[0]["quantity"] == 2
        assert result[0]["unit"] == "cups"

    def test_parse_ingredients_with_fractions(self, parser):
        """Test parsing ingredients with fractions"""
        # Arrange
        text = "1/2 cup sugar"

        # Act
        result = parser.parse_ingredients(text)

        # Assert
        assert len(result) == 1
        assert result[0]["quantity"] == 0.5
        assert result[0]["unit"] == "cup"
        assert result[0]["name"] == "sugar"

    def test_parse_ingredients_unicode(self, parser):
        """Test parsing ingredients with Unicode characters"""
        # Arrange
        text = "大さじ2 醤油"  # 2 tablespoons soy sauce in Japanese

        # Act
        result = parser.parse_ingredients(text)

        # Assert
        assert len(result) == 1
        # Add appropriate assertions based on implementation

    def test_normalize_ingredient_names(self, parser):
        """Test ingredient name normalization"""
        # Arrange
        test_cases = [
            ("onions", "onion"),
            ("Tomatoes", "tomato"),
            ("  garlic  ", "garlic")
        ]

        # Act & Assert
        for input_name, expected_name in test_cases:
            result = parser.normalize_ingredient_name(input_name)
            assert result == expected_name

    def test_parse_cooking_steps(self, parser):
        """Test parsing cooking steps"""
        # Arrange
        text = """
        1. Preheat oven to 350F
        2. Mix dry ingredients
        3. Add wet ingredients
        4. Bake for 30 minutes
        """

        # Act
        result = parser.parse_steps(text)

        # Assert
        assert len(result) == 4
        assert "Preheat oven" in result[0]
        assert "Mix dry" in result[1]

    def test_parse_empty_input(self, parser):
        """Test handling of empty input"""
        # Arrange
        text = ""

        # Act
        result = parser.parse_ingredients(text)

        # Assert
        assert result == []

    @pytest.mark.parametrize("input_text,expected_quantity,expected_unit", [
        ("2 cups flour", 2, "cups"),
        ("1/4 teaspoon salt", 0.25, "teaspoon"),
        ("3 tablespoons butter", 3, "tablespoons"),
        ("1.5 kg chicken", 1.5, "kg")
    ])
    def test_quantity_unit_extraction(self, parser, input_text, expected_quantity, expected_unit):
        """Test quantity and unit extraction with various formats"""
        # Act
        result = parser.parse_ingredients(input_text)

        # Assert
        assert result[0]["quantity"] == expected_quantity
        assert result[0]["unit"] == expected_unit
```

---

### Template 2: Database Unit Test

```python
# File: backend/tests/test_database.py

import pytest
from backend.database import Database, Recipe, Tag

@pytest.fixture
def db():
    """Create in-memory database for testing"""
    database = Database(":memory:")
    database.create_tables()
    yield database
    database.close()

@pytest.fixture
def sample_recipe_data():
    """Sample recipe data"""
    return {
        "name": "Test Recipe",
        "ingredients": [
            {"name": "flour", "quantity": 2, "unit": "cups"},
            {"name": "sugar", "quantity": 1, "unit": "cup"}
        ],
        "steps": ["Mix ingredients", "Bake"],
        "tags": ["dessert", "easy"]
    }

class TestDatabase:
    """Test suite for database operations"""

    def test_create_recipe(self, db, sample_recipe_data):
        """Test creating a recipe"""
        # Act
        recipe_id = db.create_recipe(sample_recipe_data)

        # Assert
        assert recipe_id is not None
        recipe = db.get_recipe(recipe_id)
        assert recipe.name == sample_recipe_data["name"]
        assert len(recipe.ingredients) == 2

    def test_read_recipe(self, db, sample_recipe_data):
        """Test reading a recipe"""
        # Arrange
        recipe_id = db.create_recipe(sample_recipe_data)

        # Act
        recipe = db.get_recipe(recipe_id)

        # Assert
        assert recipe is not None
        assert recipe.name == "Test Recipe"
        assert recipe.id == recipe_id

    def test_update_recipe(self, db, sample_recipe_data):
        """Test updating a recipe"""
        # Arrange
        recipe_id = db.create_recipe(sample_recipe_data)
        updated_name = "Updated Recipe Name"

        # Act
        db.update_recipe(recipe_id, {"name": updated_name})
        recipe = db.get_recipe(recipe_id)

        # Assert
        assert recipe.name == updated_name

    def test_delete_recipe(self, db, sample_recipe_data):
        """Test deleting a recipe"""
        # Arrange
        recipe_id = db.create_recipe(sample_recipe_data)

        # Act
        db.delete_recipe(recipe_id)
        recipe = db.get_recipe(recipe_id)

        # Assert
        assert recipe is None

    def test_search_recipes(self, db):
        """Test searching recipes by name"""
        # Arrange
        db.create_recipe({"name": "Chocolate Cake", "ingredients": [], "steps": []})
        db.create_recipe({"name": "Vanilla Cake", "ingredients": [], "steps": []})
        db.create_recipe({"name": "Chocolate Cookies", "ingredients": [], "steps": []})

        # Act
        results = db.search_recipes("Chocolate")

        # Assert
        assert len(results) == 2
        assert all("Chocolate" in r.name for r in results)

    def test_filter_by_tags(self, db):
        """Test filtering recipes by tags"""
        # Arrange
        db.create_recipe({"name": "Recipe 1", "tags": ["dessert", "easy"]})
        db.create_recipe({"name": "Recipe 2", "tags": ["dinner", "hard"]})
        db.create_recipe({"name": "Recipe 3", "tags": ["dessert", "hard"]})

        # Act
        results = db.filter_by_tag("dessert")

        # Assert
        assert len(results) == 2

    def test_duplicate_recipe_name(self, db, sample_recipe_data):
        """Test handling duplicate recipe names"""
        # Arrange
        db.create_recipe(sample_recipe_data)

        # Act & Assert
        with pytest.raises(ValueError):
            db.create_recipe(sample_recipe_data)

    def test_get_nonexistent_recipe(self, db):
        """Test retrieving non-existent recipe"""
        # Act
        recipe = db.get_recipe(99999)

        # Assert
        assert recipe is None
```

---

### Template 3: API Routes Test

```python
# File: backend/tests/test_api_routes.py

import pytest
from fastapi.testclient import TestClient
from backend.api import app
from backend.database import Database

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def mock_db(monkeypatch):
    """Mock database for API tests"""
    db = Database(":memory:")
    db.create_tables()

    # Monkeypatch the database instance
    monkeypatch.setattr("backend.api.db", db)

    yield db
    db.close()

class TestRecipeAPI:
    """Test suite for Recipe API endpoints"""

    def test_get_recipes_empty(self, client, mock_db):
        """Test GET /api/v1/recipes with no recipes"""
        # Act
        response = client.get("/api/v1/recipes")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"] == []

    def test_get_recipes_list(self, client, mock_db):
        """Test GET /api/v1/recipes with recipes"""
        # Arrange
        mock_db.create_recipe({"name": "Recipe 1", "ingredients": [], "steps": []})
        mock_db.create_recipe({"name": "Recipe 2", "ingredients": [], "steps": []})

        # Act
        response = client.get("/api/v1/recipes")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    def test_get_recipe_by_id(self, client, mock_db):
        """Test GET /api/v1/recipes/{id}"""
        # Arrange
        recipe_id = mock_db.create_recipe({
            "name": "Test Recipe",
            "ingredients": [],
            "steps": []
        })

        # Act
        response = client.get(f"/api/v1/recipes/{recipe_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Test Recipe"

    def test_get_recipe_not_found(self, client, mock_db):
        """Test GET /api/v1/recipes/{id} with invalid ID"""
        # Act
        response = client.get("/api/v1/recipes/99999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"

    def test_create_recipe_success(self, client, mock_db):
        """Test POST /api/v1/recipes with valid data"""
        # Arrange
        recipe_data = {
            "name": "New Recipe",
            "ingredients": [
                {"name": "flour", "quantity": 2, "unit": "cups"}
            ],
            "steps": ["Mix", "Bake"]
        }

        # Act
        response = client.post("/api/v1/recipes", json=recipe_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "ok"
        assert "id" in data["data"]

    def test_create_recipe_invalid_data(self, client, mock_db):
        """Test POST /api/v1/recipes with invalid data"""
        # Arrange
        invalid_data = {
            "invalid_field": "value"
        }

        # Act
        response = client.post("/api/v1/recipes", json=invalid_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"

    def test_update_recipe(self, client, mock_db):
        """Test PUT /api/v1/recipes/{id}"""
        # Arrange
        recipe_id = mock_db.create_recipe({
            "name": "Original Name",
            "ingredients": [],
            "steps": []
        })
        update_data = {"name": "Updated Name"}

        # Act
        response = client.put(f"/api/v1/recipes/{recipe_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        updated = mock_db.get_recipe(recipe_id)
        assert updated.name == "Updated Name"

    def test_delete_recipe(self, client, mock_db):
        """Test DELETE /api/v1/recipes/{id}"""
        # Arrange
        recipe_id = mock_db.create_recipe({
            "name": "To Delete",
            "ingredients": [],
            "steps": []
        })

        # Act
        response = client.delete(f"/api/v1/recipes/{recipe_id}")

        # Assert
        assert response.status_code == 200
        assert mock_db.get_recipe(recipe_id) is None

    def test_search_recipes(self, client, mock_db):
        """Test GET /api/v1/recipes/search"""
        # Arrange
        mock_db.create_recipe({"name": "Chocolate Cake", "ingredients": [], "steps": []})
        mock_db.create_recipe({"name": "Vanilla Cake", "ingredients": [], "steps": []})

        # Act
        response = client.get("/api/v1/recipes/search?q=Chocolate")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
```

---

### Template 4: Web Scraper Test (with Mocks)

```python
# File: backend/tests/test_web_scraper.py

import pytest
import responses
from backend.services.web_scraper import WebScraper

@pytest.fixture
def scraper():
    """Create scraper instance"""
    return WebScraper()

@pytest.fixture
def sample_recipe_html():
    """Sample recipe HTML"""
    return """
    <html>
    <head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org/",
            "@type": "Recipe",
            "name": "Test Recipe",
            "recipeIngredient": ["2 cups flour", "1 cup sugar"],
            "recipeInstructions": [
                {"@type": "HowToStep", "text": "Mix ingredients"},
                {"@type": "HowToStep", "text": "Bake"}
            ]
        }
        </script>
    </head>
    <body>
        <h1>Test Recipe</h1>
    </body>
    </html>
    """

class TestWebScraper:
    """Test suite for web scraping functionality"""

    @responses.activate
    @pytest.mark.web
    def test_scrape_recipe_success(self, scraper, sample_recipe_html):
        """Test successful recipe scraping"""
        # Arrange
        url = "https://example.com/recipe"
        responses.add(
            responses.GET,
            url,
            body=sample_recipe_html,
            status=200
        )

        # Act
        result = scraper.scrape_url(url)

        # Assert
        assert result is not None
        assert result["name"] == "Test Recipe"
        assert len(result["ingredients"]) == 2

    @responses.activate
    @pytest.mark.web
    def test_scrape_recipe_404(self, scraper):
        """Test handling of 404 error"""
        # Arrange
        url = "https://example.com/not-found"
        responses.add(responses.GET, url, status=404)

        # Act & Assert
        with pytest.raises(Exception):
            scraper.scrape_url(url)

    @pytest.mark.web
    def test_scrape_invalid_url(self, scraper):
        """Test handling of invalid URL"""
        # Arrange
        url = "not-a-valid-url"

        # Act & Assert
        with pytest.raises(ValueError):
            scraper.scrape_url(url)

    def test_extract_schema_org_recipe(self, scraper, sample_recipe_html):
        """Test extracting recipe from schema.org JSON-LD"""
        # Act
        result = scraper.extract_recipe_from_html(sample_recipe_html)

        # Assert
        assert result["name"] == "Test Recipe"
        assert len(result["ingredients"]) == 2
        assert len(result["steps"]) == 2

    @responses.activate
    @pytest.mark.web
    def test_scrape_with_timeout(self, scraper):
        """Test handling of request timeout"""
        # Arrange
        url = "https://example.com/slow"
        responses.add(
            responses.GET,
            url,
            body=Exception("Timeout")
        )

        # Act & Assert
        with pytest.raises(Exception):
            scraper.scrape_url(url, timeout=1)
```

---

## Frontend Test Templates

### Template 5: React Component Test

```javascript
// File: frontend/tests/components/RecipeCard.test.js

import { describe, it, expect, beforeEach } from 'bun:test';
import { render, screen, fireEvent } from '@testing-library/react';
import RecipeCard from '../../src/components/RecipeCard';

describe('RecipeCard', () => {
  let mockRecipe;
  let mockOnClick;

  beforeEach(() => {
    mockRecipe = {
      id: 1,
      name: 'Test Recipe',
      ingredients: [
        { name: 'flour', quantity: 2, unit: 'cups' },
        { name: 'sugar', quantity: 1, unit: 'cup' }
      ],
      steps: ['Mix', 'Bake'],
      tags: ['dessert', 'easy']
    };

    mockOnClick = jest.fn();
  });

  it('renders recipe name', () => {
    // Arrange & Act
    render(<RecipeCard recipe={mockRecipe} />);

    // Assert
    expect(screen.getByText('Test Recipe')).toBeDefined();
  });

  it('displays ingredient count', () => {
    // Arrange & Act
    render(<RecipeCard recipe={mockRecipe} />);

    // Assert
    expect(screen.getByText(/2 ingredients/i)).toBeDefined();
  });

  it('displays tags', () => {
    // Arrange & Act
    render(<RecipeCard recipe={mockRecipe} />);

    // Assert
    expect(screen.getByText('dessert')).toBeDefined();
    expect(screen.getByText('easy')).toBeDefined();
  });

  it('calls onClick when clicked', () => {
    // Arrange
    render(<RecipeCard recipe={mockRecipe} onClick={mockOnClick} />);
    const card = screen.getByTestId('recipe-card');

    // Act
    fireEvent.click(card);

    // Assert
    expect(mockOnClick).toHaveBeenCalledWith(mockRecipe);
  });

  it('renders without image when not provided', () => {
    // Arrange & Act
    render(<RecipeCard recipe={mockRecipe} />);

    // Assert
    expect(screen.queryByRole('img')).toBeNull();
  });

  it('renders with image when provided', () => {
    // Arrange
    const recipeWithImage = {
      ...mockRecipe,
      image: 'https://example.com/image.jpg'
    };

    // Act
    render(<RecipeCard recipe={recipeWithImage} />);

    // Assert
    expect(screen.getByRole('img')).toBeDefined();
  });
});
```

---

### Template 6: Integration Test

```python
# File: tests/integration/test_recipe_workflow.py

import pytest
from backend.database import Database
from backend.services.recipe_parser import RecipeParser
from backend.services.web_scraper import WebScraper

@pytest.fixture
def full_stack():
    """Set up full stack for integration testing"""
    db = Database(":memory:")
    db.create_tables()
    parser = RecipeParser()
    scraper = WebScraper()

    yield {
        "db": db,
        "parser": parser,
        "scraper": scraper
    }

    db.close()

class TestRecipeWorkflow:
    """Integration tests for complete recipe workflows"""

    @pytest.mark.integration
    def test_url_to_database_workflow(self, full_stack, sample_recipe_html):
        """Test complete workflow: URL -> Scrape -> Parse -> Database"""
        # Arrange
        db = full_stack["db"]
        parser = full_stack["parser"]
        scraper = full_stack["scraper"]

        # Mock the scraper
        recipe_data = scraper.extract_recipe_from_html(sample_recipe_html)

        # Act - Parse and save
        parsed_recipe = parser.parse_recipe(recipe_data)
        recipe_id = db.create_recipe(parsed_recipe)

        # Assert
        assert recipe_id is not None
        saved_recipe = db.get_recipe(recipe_id)
        assert saved_recipe.name == parsed_recipe["name"]
        assert len(saved_recipe.ingredients) > 0

    @pytest.mark.integration
    def test_search_workflow(self, full_stack):
        """Test search workflow"""
        # Arrange
        db = full_stack["db"]
        db.create_recipe({"name": "Chocolate Cake", "ingredients": [], "steps": []})
        db.create_recipe({"name": "Vanilla Cake", "ingredients": [], "steps": []})

        # Act
        results = db.search_recipes("Chocolate")

        # Assert
        assert len(results) == 1
        assert results[0].name == "Chocolate Cake"

    @pytest.mark.integration
    def test_update_workflow(self, full_stack):
        """Test update workflow"""
        # Arrange
        db = full_stack["db"]
        recipe_id = db.create_recipe({
            "name": "Original",
            "ingredients": [],
            "steps": []
        })

        # Act
        db.update_recipe(recipe_id, {"name": "Updated"})
        updated = db.get_recipe(recipe_id)

        # Assert
        assert updated.name == "Updated"
```

---

## Shared Test Configuration

### conftest.py Template

```python
# File: tests/conftest.py

import pytest
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_recipe_data():
    """Standard sample recipe data"""
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
def sample_recipe_html():
    """Load sample recipe HTML from fixtures"""
    html_file = TEST_DATA_DIR / "sample_recipe.html"
    if html_file.exists():
        return html_file.read_text()
    return "<html><body><h1>Test Recipe</h1></body></html>"

@pytest.fixture
def temp_database():
    """Create temporary in-memory database"""
    from backend.database import Database
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()

@pytest.fixture(autouse=True)
def reset_test_environment():
    """Reset environment between tests"""
    # Clean up any test files
    # Reset any global state
    yield
    # Cleanup after test

# Markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "web: Tests requiring web access")
    config.addinivalue_line("markers", "ocr: Tests requiring OCR")
```

---

## Usage Instructions

1. **Copy template to appropriate directory**
2. **Modify imports to match your project structure**
3. **Update fixture paths**
4. **Implement actual test logic**
5. **Run tests:** `pytest backend/tests/test_module.py`
6. **Check coverage:** `pytest --cov=backend`

---

**Templates Version:** 1.0
**Compatible with:** Python 3.11, Bun latest
**Last Updated:** 2025-12-11


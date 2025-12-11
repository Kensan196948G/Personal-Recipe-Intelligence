"""
Enhanced test configuration and fixtures for comprehensive testing.

This file provides reusable fixtures for all test modules including:
- Database session management
- Sample recipe data
- Mock services
- Test clients
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.models.database import Base
from backend.models.recipe import Recipe
from datetime import datetime
from typing import Generator


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
  """
  Create a test database session using in-memory SQLite.

  Yields:
    Session: SQLAlchemy database session
  """
  engine = create_engine("sqlite:///:memory:")
  Base.metadata.create_all(engine)
  SessionLocal = sessionmaker(bind=engine)
  session = SessionLocal()

  yield session

  session.close()
  Base.metadata.drop_all(engine)


@pytest.fixture
def sample_recipe() -> Recipe:
  """
  Create a sample recipe instance for testing (not committed to DB).

  Returns:
    Recipe: A sample recipe object
  """
  return Recipe(
    title="Test Recipe",
    ingredients=["ingredient1", "ingredient2"],
    steps=["step1", "step2"],
    source_url="https://example.com/recipe",
    tags=["tag1", "tag2"],
  )


@pytest.fixture
def sample_recipe_dict() -> dict:
  """
  Create a sample recipe dictionary for testing API endpoints.

  Returns:
    dict: Recipe data as dictionary
  """
  return {
    "title": "Delicious Pasta",
    "ingredients": ["pasta 200g", "tomato sauce 100ml", "garlic 2 cloves"],
    "steps": [
      "Boil water and cook pasta",
      "Heat tomato sauce with garlic",
      "Mix pasta with sauce"
    ],
    "source_url": "https://example.com/pasta",
    "tags": ["italian", "dinner"],
    "cooking_time": 30,
    "servings": 2
  }


@pytest.fixture
def multiple_recipes(db_session: Session) -> list[Recipe]:
  """
  Create multiple recipes in the database for testing list and search operations.

  Args:
    db_session: Database session fixture

  Returns:
    list[Recipe]: List of created recipe objects
  """
  recipes = [
    Recipe(
      title="Spaghetti Carbonara",
      ingredients=["spaghetti 400g", "eggs 4", "bacon 200g", "parmesan 100g"],
      steps=["Cook pasta", "Fry bacon", "Mix with egg mixture"],
      source_url="https://example.com/carbonara",
      tags=["italian", "pasta"],
      cooking_time=25,
      servings=4
    ),
    Recipe(
      title="Caesar Salad",
      ingredients=["romaine lettuce", "croutons", "parmesan", "caesar dressing"],
      steps=["Chop lettuce", "Add croutons and cheese", "Toss with dressing"],
      source_url="https://example.com/caesar",
      tags=["salad", "healthy"],
      cooking_time=10,
      servings=2
    ),
    Recipe(
      title="Tomato Soup",
      ingredients=["tomatoes 1kg", "onion 1", "vegetable stock 500ml", "cream 100ml"],
      steps=["Sauté onion", "Add tomatoes and stock", "Blend and add cream"],
      source_url="https://example.com/soup",
      tags=["soup", "vegetarian"],
      cooking_time=40,
      servings=4
    ),
  ]

  for recipe in recipes:
    db_session.add(recipe)
  db_session.commit()

  for recipe in recipes:
    db_session.refresh(recipe)

  return recipes


@pytest.fixture
def mock_recipe_data() -> dict:
  """
  Mock recipe data for API testing with all fields.

  Returns:
    dict: Complete recipe data dictionary
  """
  return {
    "title": "Mock Recipe",
    "ingredients": ["ingredient A", "ingredient B"],
    "steps": ["step 1", "step 2"],
    "source_url": "https://mock.com/recipe",
    "tags": ["mock", "test"],
    "cooking_time": 20,
    "servings": 3
  }


@pytest.fixture
def invalid_recipe_data() -> dict:
  """
  Invalid recipe data for testing validation.

  Returns:
    dict: Invalid recipe data
  """
  return {
    "title": "",
    "ingredients": [],
    "steps": []
  }


@pytest.fixture
def minimal_recipe_data() -> dict:
  """
  Minimal valid recipe data with only required fields.

  Returns:
    dict: Minimal recipe data
  """
  return {
    "title": "Minimal Recipe",
    "ingredients": ["salt"],
    "steps": ["Add salt"]
  }


@pytest.fixture
def japanese_recipe_data() -> dict:
  """
  Recipe data with Japanese text for unicode testing.

  Returns:
    dict: Japanese recipe data
  """
  return {
    "title": "味噌汁",
    "ingredients": ["味噌", "豆腐", "わかめ"],
    "steps": ["お湯を沸かす", "味噌を溶く", "豆腐とわかめを入れる"],
    "tags": ["和食", "スープ"],
    "cooking_time": 10,
    "servings": 2
  }


@pytest.fixture
def recipe_with_all_fields() -> dict:
  """
  Recipe data with all possible fields populated.

  Returns:
    dict: Complete recipe data
  """
  return {
    "title": "Complete Recipe with All Fields",
    "ingredients": [
      "flour 500g",
      "water 300ml",
      "yeast 7g",
      "salt 10g",
      "olive oil 50ml"
    ],
    "steps": [
      "Mix flour, water, and yeast",
      "Knead for 10 minutes",
      "Let rise for 1 hour",
      "Shape and bake at 220°C for 25 minutes"
    ],
    "source_url": "https://example.com/complete-recipe",
    "tags": ["bread", "baking", "homemade"],
    "cooking_time": 120,
    "servings": 8
  }


@pytest.fixture
def search_test_recipes(db_session: Session) -> list[Recipe]:
  """
  Create recipes specifically for testing search functionality.

  Args:
    db_session: Database session fixture

  Returns:
    list[Recipe]: List of recipes for search testing
  """
  recipes = [
    Recipe(
      title="Italian Pasta Primavera",
      ingredients=["pasta", "vegetables", "olive oil"],
      steps=["Cook pasta", "Sauté vegetables", "Mix together"],
      tags=["italian", "vegetarian", "pasta"]
    ),
    Recipe(
      title="Italian Pizza Margherita",
      ingredients=["dough", "tomatoes", "mozzarella"],
      steps=["Prepare dough", "Add toppings", "Bake"],
      tags=["italian", "pizza"]
    ),
    Recipe(
      title="Japanese Ramen",
      ingredients=["noodles", "broth", "egg"],
      steps=["Prepare broth", "Cook noodles", "Assemble"],
      tags=["japanese", "noodles"]
    ),
    Recipe(
      title="Vegetarian Curry",
      ingredients=["vegetables", "curry paste", "coconut milk"],
      steps=["Sauté vegetables", "Add curry paste", "Simmer"],
      tags=["vegetarian", "curry", "indian"]
    ),
  ]

  for recipe in recipes:
    db_session.add(recipe)
  db_session.commit()

  for recipe in recipes:
    db_session.refresh(recipe)

  return recipes


@pytest.fixture
def mock_html_recipe() -> str:
  """
  Mock HTML content for recipe parsing tests.

  Returns:
    str: HTML content with recipe data
  """
  return """
  <html>
    <head><title>Recipe Page</title></head>
    <body>
      <h1>Chocolate Chip Cookies</h1>
      <ul class="ingredients">
        <li>2 cups flour</li>
        <li>1 cup butter</li>
        <li>1 cup sugar</li>
        <li>2 eggs</li>
        <li>1 tsp vanilla</li>
        <li>1 cup chocolate chips</li>
      </ul>
      <ol class="steps">
        <li>Preheat oven to 350°F</li>
        <li>Mix butter and sugar</li>
        <li>Add eggs and vanilla</li>
        <li>Mix in flour</li>
        <li>Fold in chocolate chips</li>
        <li>Bake for 12 minutes</li>
      </ol>
      <span class="cooking-time">25 minutes</span>
      <span class="servings">Makes 24 cookies</span>
    </body>
  </html>
  """


@pytest.fixture(autouse=True)
def reset_database(db_session: Session):
  """
  Automatically reset database between tests.

  Args:
    db_session: Database session fixture
  """
  yield
  db_session.rollback()
  for table in reversed(Base.metadata.sorted_tables):
    db_session.execute(table.delete())
  db_session.commit()


# Performance testing fixtures

@pytest.fixture
def large_recipe_set(db_session: Session) -> list[Recipe]:
  """
  Create a large set of recipes for performance testing.

  Args:
    db_session: Database session fixture

  Returns:
    list[Recipe]: List of 100 recipes
  """
  recipes = []
  for i in range(100):
    recipe = Recipe(
      title=f"Performance Test Recipe {i}",
      ingredients=[f"ingredient_{j}" for j in range(5)],
      steps=[f"step_{j}" for j in range(3)],
      tags=[f"tag_{i % 10}"],
      cooking_time=30 + (i % 60),
      servings=2 + (i % 6)
    )
    recipes.append(recipe)

  db_session.add_all(recipes)
  db_session.commit()

  return recipes

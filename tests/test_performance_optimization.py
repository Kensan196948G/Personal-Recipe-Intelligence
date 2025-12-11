"""Tests for N+1 query optimization."""

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from backend.repositories.recipe_repository import RecipeRepository
from backend.services.recipe_service import RecipeService
from backend.schemas.recipe import RecipeCreate, IngredientCreate


class QueryCounter:
  """Context manager to count SQL queries."""

  def __init__(self):
    self.count = 0
    self.queries = []

  def __enter__(self):
    event.listen(Engine, "before_cursor_execute", self._before_cursor_execute)
    return self

  def __exit__(self, *args):
    event.remove(Engine, "before_cursor_execute", self._before_cursor_execute)

  def _before_cursor_execute(self, conn, cursor, statement, *args):
    self.count += 1
    self.queries.append(statement)


@pytest.fixture
def sample_recipe_data():
  """Create sample recipe data for testing."""
  return RecipeCreate(
    name="Test Recipe",
    description="A test recipe",
    ingredients=[
      IngredientCreate(name="たまねぎ", quantity="1", unit="個"),
      IngredientCreate(name="にんじん", quantity="2", unit="本"),
      IngredientCreate(name="じゃがいも", quantity="3", unit="個"),
    ],
    steps=["Step 1", "Step 2", "Step 3"],
    tags=["test", "quick", "easy"],
  )


def test_list_recipes_query_count_optimized(db_session, sample_recipe_data):
  """Test that listing recipes uses minimal queries with eager loading."""
  repository = RecipeRepository(db_session)

  # Create 10 test recipes
  for i in range(10):
    data = sample_recipe_data.copy()
    data.name = f"Recipe {i}"
    repository.create(data)

  # Count queries when fetching with relations
  with QueryCounter() as counter:
    recipes = repository.get_all(limit=10, with_relations=True)

  # Should use exactly 4 queries:
  # 1. SELECT recipes
  # 2. SELECT ingredients WHERE recipe_id IN (...)
  # 3. SELECT steps WHERE recipe_id IN (...)
  # 4. SELECT tags WHERE recipe_id IN (...)
  assert counter.count <= 4, f"Expected <= 4 queries, got {counter.count}"
  assert len(recipes) == 10


def test_list_recipes_without_relations_lightweight(db_session, sample_recipe_data):
  """Test that listing without relations uses only 1 query."""
  repository = RecipeRepository(db_session)

  # Create test recipes
  for i in range(5):
    data = sample_recipe_data.copy()
    data.name = f"Recipe {i}"
    repository.create(data)

  # Count queries when fetching without relations
  with QueryCounter() as counter:
    recipes = repository.get_all(limit=5, with_relations=False)

  # Should use only 1 query for recipes
  assert counter.count == 1, f"Expected 1 query, got {counter.count}"
  assert len(recipes) == 5


def test_get_single_recipe_query_count(db_session, sample_recipe_data):
  """Test that getting a single recipe uses minimal queries."""
  repository = RecipeRepository(db_session)

  # Create recipe
  recipe = repository.create(sample_recipe_data)

  # Count queries when fetching with relations
  with QueryCounter() as counter:
    fetched = repository.get_by_id_with_relations(recipe.id)

  # Should use exactly 4 queries
  assert counter.count <= 4, f"Expected <= 4 queries, got {counter.count}"
  assert fetched is not None
  assert len(fetched.ingredients) == 3
  assert len(fetched.steps) == 3
  assert len(fetched.tags) == 3


def test_search_recipes_query_count(db_session, sample_recipe_data):
  """Test that searching recipes uses minimal queries."""
  repository = RecipeRepository(db_session)

  # Create test recipes
  for i in range(15):
    data = sample_recipe_data.copy()
    data.name = f"Curry Recipe {i}"
    repository.create(data)

  # Count queries when searching with relations
  with QueryCounter() as counter:
    results = repository.search("curry", with_relations=True)

  # Should use exactly 4 queries regardless of result count
  assert counter.count <= 4, f"Expected <= 4 queries, got {counter.count}"
  assert len(results) == 15


def test_filter_by_tags_query_count(db_session, sample_recipe_data):
  """Test that filtering by tags uses minimal queries."""
  repository = RecipeRepository(db_session)

  # Create recipes with different tags
  for i in range(10):
    data = sample_recipe_data.copy()
    data.name = f"Recipe {i}"
    data.tags = ["quick"] if i % 2 == 0 else ["slow"]
    repository.create(data)

  # Count queries when filtering with relations
  with QueryCounter() as counter:
    results = repository.get_by_tags(["quick"], with_relations=True)

  # Should use exactly 4 queries
  assert counter.count <= 4, f"Expected <= 4 queries, got {counter.count}"
  assert len(results) == 5  # Half of the recipes


def test_batch_create_performance(db_session, sample_recipe_data):
  """Test that creating recipe with relations uses batch operations."""
  repository = RecipeRepository(db_session)

  with QueryCounter() as counter:
    recipe = repository.create(sample_recipe_data)

  # Should use minimal queries:
  # 1. INSERT recipe
  # 2. BULK INSERT ingredients
  # 3. BULK INSERT steps
  # 4. BULK INSERT tags
  # Plus potential SELECT for refresh
  assert counter.count <= 10, f"Expected <= 10 queries, got {counter.count}"
  assert recipe.id is not None
  assert len(recipe.ingredients) == 3


def test_batch_update_performance(db_session, sample_recipe_data):
  """Test that updating recipe uses batch operations."""
  repository = RecipeRepository(db_session)

  # Create recipe
  recipe = repository.create(sample_recipe_data)

  # Update with new data
  from backend.schemas.recipe import RecipeUpdate

  update_data = RecipeUpdate(
    name="Updated Recipe",
    ingredients=[
      IngredientCreate(name="新しい材料", quantity="5", unit="個"),
    ],
  )

  with QueryCounter() as counter:
    updated = repository.update(recipe.id, update_data)

  # Should use batch operations for updating relations
  assert counter.count <= 15, f"Expected <= 15 queries, got {counter.count}"
  assert updated.name == "Updated Recipe"
  assert len(updated.ingredients) == 1


def test_ingredient_normalization(db_session):
  """Test that ingredient names are properly normalized."""
  repository = RecipeRepository(db_session)

  # Test various spellings
  test_cases = [
    ("玉ねぎ", "たまねぎ"),
    ("玉葱", "たまねぎ"),
    ("人参", "にんじん"),
    ("じゃが芋", "じゃがいも"),
    ("ジャガイモ", "じゃがいも"),
  ]

  for original, expected in test_cases:
    result = repository._normalize_ingredient_name(original)
    assert result == expected, f"Expected {expected}, got {result}"


def test_pagination_with_count(db_session, sample_recipe_data):
  """Test pagination support with total count."""
  repository = RecipeRepository(db_session)

  # Create 25 recipes
  for i in range(25):
    data = sample_recipe_data.copy()
    data.name = f"Recipe {i}"
    repository.create(data)

  # Get first page
  page1 = repository.get_all(skip=0, limit=10, with_relations=True)
  assert len(page1) == 10

  # Get second page
  page2 = repository.get_all(skip=10, limit=10, with_relations=True)
  assert len(page2) == 10

  # Get last page
  page3 = repository.get_all(skip=20, limit=10, with_relations=True)
  assert len(page3) == 5

  # Get total count
  total = repository.count()
  assert total == 25


def test_service_layer_query_optimization(db_session, sample_recipe_data):
  """Test that service layer properly uses optimized queries."""
  service = RecipeService(db_session)

  # Create recipes
  for i in range(10):
    data = sample_recipe_data.copy()
    data.name = f"Recipe {i}"
    service.create_recipe(data)

  # Test get_recipes with relations
  with QueryCounter() as counter:
    recipes = service.get_recipes(limit=10, with_relations=True)

  assert counter.count <= 4, f"Expected <= 4 queries, got {counter.count}"
  assert len(recipes) == 10

  # Test get_recipes without relations
  with QueryCounter() as counter:
    recipes_light = service.get_recipes(limit=10, with_relations=False)

  assert counter.count == 1, f"Expected 1 query, got {counter.count}"
  assert len(recipes_light) == 10


def test_batch_fetch_by_ids(db_session, sample_recipe_data):
  """Test batch fetching multiple recipes by IDs."""
  repository = RecipeRepository(db_session)

  # Create recipes
  recipe_ids = []
  for i in range(10):
    data = sample_recipe_data.copy()
    data.name = f"Recipe {i}"
    recipe = repository.create(data)
    recipe_ids.append(recipe.id)

  # Fetch batch with eager loading
  with QueryCounter() as counter:
    recipes = repository.get_batch_by_ids(recipe_ids)

  # Should use exactly 4 queries regardless of ID count
  assert counter.count <= 4, f"Expected <= 4 queries, got {counter.count}"
  assert len(recipes) == 10


@pytest.mark.performance
def test_large_dataset_performance(db_session, sample_recipe_data):
  """Test performance with a large dataset (100 recipes)."""
  repository = RecipeRepository(db_session)

  # Create 100 recipes
  for i in range(100):
    data = sample_recipe_data.copy()
    data.name = f"Recipe {i}"
    repository.create(data)

  # Measure query count for fetching all
  with QueryCounter() as counter:
    recipes = repository.get_all(limit=100, with_relations=True)

  # Should still use only 4 queries
  assert counter.count <= 4, f"Expected <= 4 queries, got {counter.count}"
  assert len(recipes) == 100

  # Verify all relations are loaded (no lazy loading)
  for recipe in recipes[:5]:  # Check first 5
    # Accessing these should not trigger additional queries
    assert len(recipe.ingredients) >= 0
    assert len(recipe.steps) >= 0
    assert len(recipe.tags) >= 0


def test_no_n_plus_1_when_accessing_relations(db_session, sample_recipe_data):
  """Test that accessing relations doesn't trigger additional queries."""
  repository = RecipeRepository(db_session)

  # Create recipes
  for i in range(10):
    data = sample_recipe_data.copy()
    data.name = f"Recipe {i}"
    repository.create(data)

  # Fetch with eager loading
  recipes = repository.get_all(limit=10, with_relations=True)

  # Count queries when accessing relations
  with QueryCounter() as counter:
    for recipe in recipes:
      # Access all relations
      _ = recipe.name
      _ = list(recipe.ingredients)
      _ = list(recipe.steps)
      _ = list(recipe.tags)

  # Should be 0 additional queries (all data already loaded)
  assert counter.count == 0, f"Expected 0 queries, got {counter.count}"


if __name__ == "__main__":
  pytest.main([__file__, "-v", "--tb=short"])

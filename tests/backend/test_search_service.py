"""
Tests for search service functionality.

Tests fuzzy search, ingredient search, and combined search.
"""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from backend.models.recipe import Recipe, Ingredient
from backend.services.search_service import SearchService, SearchResult


@pytest.fixture(name="session")
def session_fixture():
  """Create test database session."""
  engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
  )
  SQLModel.metadata.create_all(engine)
  with Session(engine) as session:
    yield session


@pytest.fixture(name="sample_recipes")
def sample_recipes_fixture(session: Session):
  """Create sample recipes for testing."""
  # Recipe 1: カレーライス
  recipe1 = Recipe(
    title="カレーライス",
    description="基本的なカレーライスのレシピ",
    tags="和食,簡単",
  )
  session.add(recipe1)
  session.commit()
  session.refresh(recipe1)

  # Add ingredients
  ingredients1 = [
    Ingredient(recipe_id=recipe1.id, name="玉ねぎ", quantity="1個"),
    Ingredient(recipe_id=recipe1.id, name="にんじん", quantity="1本"),
    Ingredient(recipe_id=recipe1.id, name="じゃがいも", quantity="2個"),
    Ingredient(recipe_id=recipe1.id, name="豚肉", quantity="200g"),
    Ingredient(recipe_id=recipe1.id, name="カレールー", quantity="1箱"),
  ]
  for ing in ingredients1:
    session.add(ing)

  # Recipe 2: チキンカレー
  recipe2 = Recipe(
    title="チキンカレー",
    description="鶏肉を使ったカレー",
    tags="洋食,簡単",
  )
  session.add(recipe2)
  session.commit()
  session.refresh(recipe2)

  # Add ingredients
  ingredients2 = [
    Ingredient(recipe_id=recipe2.id, name="鶏肉", quantity="300g"),
    Ingredient(recipe_id=recipe2.id, name="玉ねぎ", quantity="2個"),
    Ingredient(recipe_id=recipe2.id, name="トマト", quantity="2個"),
    Ingredient(recipe_id=recipe2.id, name="カレー粉", quantity="大さじ2"),
  ]
  for ing in ingredients2:
    session.add(ing)

  # Recipe 3: ポテトサラダ
  recipe3 = Recipe(
    title="ポテトサラダ",
    description="定番のポテトサラダ",
    tags="和食,簡単,サラダ",
  )
  session.add(recipe3)
  session.commit()
  session.refresh(recipe3)

  # Add ingredients
  ingredients3 = [
    Ingredient(recipe_id=recipe3.id, name="じゃがいも", quantity="4個"),
    Ingredient(recipe_id=recipe3.id, name="にんじん", quantity="1本"),
    Ingredient(recipe_id=recipe3.id, name="きゅうり", quantity="1本"),
    Ingredient(recipe_id=recipe3.id, name="マヨネーズ", quantity="適量"),
  ]
  for ing in ingredients3:
    session.add(ing)

  session.commit()
  return [recipe1, recipe2, recipe3]


class TestSearchService:
  """Test search service functionality."""

  def test_fuzzy_search_exact_match(
    self, session: Session, sample_recipes: list
  ):
    """Test fuzzy search with exact match."""
    search_service = SearchService(session)
    results = search_service.fuzzy_search("カレーライス")

    assert len(results) > 0
    assert results[0].recipe.title == "カレーライス"
    assert results[0].score == 1.0
    assert results[0].match_type == "title"

  def test_fuzzy_search_partial_match(
    self, session: Session, sample_recipes: list
  ):
    """Test fuzzy search with partial match."""
    search_service = SearchService(session)
    results = search_service.fuzzy_search("カレー")

    assert len(results) >= 2
    # Should find both カレーライス and チキンカレー
    titles = [r.recipe.title for r in results]
    assert "カレーライス" in titles
    assert "チキンカレー" in titles

  def test_fuzzy_search_threshold(
    self, session: Session, sample_recipes: list
  ):
    """Test fuzzy search with custom threshold."""
    search_service = SearchService(session)
    results = search_service.fuzzy_search("カレー", threshold=0.9)

    # With high threshold, only strong matches should be returned
    assert all(r.score >= 0.9 for r in results)

  def test_search_by_ingredients_any(
    self, session: Session, sample_recipes: list
  ):
    """Test ingredient search with ANY match."""
    search_service = SearchService(session)
    results = search_service.search_by_ingredients(
      ["玉ねぎ", "にんじん"], match_all=False
    )

    assert len(results) >= 2
    # Should find カレーライス, チキンカレー, and ポテトサラダ
    assert any(r.recipe.title == "カレーライス" for r in results)
    assert any(r.recipe.title == "ポテトサラダ" for r in results)

  def test_search_by_ingredients_all(
    self, session: Session, sample_recipes: list
  ):
    """Test ingredient search with ALL match."""
    search_service = SearchService(session)
    results = search_service.search_by_ingredients(
      ["玉ねぎ", "にんじん"], match_all=True
    )

    assert len(results) >= 2
    # Only recipes with both ingredients
    for result in results:
      assert result.recipe.title in ["カレーライス", "ポテトサラダ"]

  def test_search_by_ingredients_single(
    self, session: Session, sample_recipes: list
  ):
    """Test ingredient search with single ingredient."""
    search_service = SearchService(session)
    results = search_service.search_by_ingredients(["じゃがいも"])

    assert len(results) >= 2
    # Should find カレーライス and ポテトサラダ
    titles = [r.recipe.title for r in results]
    assert "カレーライス" in titles
    assert "ポテトサラダ" in titles

  def test_combined_search_title_only(
    self, session: Session, sample_recipes: list
  ):
    """Test combined search with title only."""
    search_service = SearchService(session)
    results = search_service.combined_search(title_query="カレー")

    assert len(results) >= 2
    assert any(r.recipe.title == "カレーライス" for r in results)
    assert any(r.recipe.title == "チキンカレー" for r in results)

  def test_combined_search_ingredients_only(
    self, session: Session, sample_recipes: list
  ):
    """Test combined search with ingredients only."""
    search_service = SearchService(session)
    results = search_service.combined_search(
      ingredient_names=["じゃがいも"]
    )

    assert len(results) >= 2
    titles = [r.recipe.title for r in results]
    assert "カレーライス" in titles
    assert "ポテトサラダ" in titles

  def test_combined_search_both(
    self, session: Session, sample_recipes: list
  ):
    """Test combined search with both title and ingredients."""
    search_service = SearchService(session)
    results = search_service.combined_search(
      title_query="カレー", ingredient_names=["じゃがいも"]
    )

    assert len(results) > 0
    # カレーライス should have highest score (matches both)
    assert results[0].recipe.title == "カレーライス"
    assert results[0].match_type == "combined"

  def test_advanced_search_with_tags(
    self, session: Session, sample_recipes: list
  ):
    """Test advanced search with tags."""
    search_service = SearchService(session)
    results = search_service.advanced_search(tags=["和食"])

    assert len(results) >= 2
    # Should find カレーライス and ポテトサラダ
    titles = [r.recipe.title for r in results]
    assert "カレーライス" in titles
    assert "ポテトサラダ" in titles

  def test_advanced_search_combined(
    self, session: Session, sample_recipes: list
  ):
    """Test advanced search with multiple criteria."""
    search_service = SearchService(session)
    results = search_service.advanced_search(
      query="カレー", ingredients=["玉ねぎ"], tags=["簡単"]
    )

    assert len(results) > 0
    # All results should match the criteria
    for result in results:
      assert "カレー" in result.recipe.title or "玉ねぎ" in str(result.matched_terms)

  def test_normalize_text(self, session: Session):
    """Test text normalization."""
    search_service = SearchService(session)

    # Test whitespace normalization
    assert search_service._normalize_text("  test  ") == "test"
    assert search_service._normalize_text("test\n\ntext") == "test text"

    # Test lowercase conversion
    assert search_service._normalize_text("TEST") == "test"

    # Test Japanese text (should remain unchanged)
    assert search_service._normalize_text("カレーライス") == "カレーライス"

  def test_calculate_title_score(self, session: Session):
    """Test title score calculation."""
    search_service = SearchService(session)

    # Exact match
    assert search_service._calculate_title_score("test", "test") == 1.0

    # Partial match (query in title)
    score = search_service._calculate_title_score("test", "test recipe")
    assert score == 0.9

    # No match
    score = search_service._calculate_title_score("test", "xyz")
    assert score < 0.5

  def test_empty_search(self, session: Session, sample_recipes: list):
    """Test search with empty query."""
    search_service = SearchService(session)

    # Empty fuzzy search
    results = search_service.fuzzy_search("")
    assert len(results) == 0

    # Empty ingredient search
    results = search_service.search_by_ingredients([])
    assert len(results) == 0

    # Empty combined search
    results = search_service.combined_search()
    assert len(results) == 0

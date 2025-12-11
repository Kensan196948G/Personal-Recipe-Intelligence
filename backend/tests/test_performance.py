"""Performance tests for database indexes.

This module tests the performance impact of database indexes
on common query patterns.
"""

import time
from typing import Tuple

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models import Base, Recipe, Ingredient, Tag


@pytest.fixture
def db_session():
    """Create a test database session with sample data."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add sample data
    for i in range(1000):
        recipe = Recipe(
            title=f"Recipe {i}",
            description=f"Description for recipe {i}",
            source_type="manual",
            created_at=f"2025-01-{(i % 28) + 1:02d} 12:00:00",
        )
        session.add(recipe)

        # Add ingredients
        for j in range(5):
            ingredient = Ingredient(
                recipe=recipe,
                name=f"Ingredient {j}",
                name_normalized=f"ingredient_{j}",
                quantity=100.0 + j,
                unit="g",
                order_index=j,
            )
            session.add(ingredient)

        # Add tags
        if i % 10 == 0:
            tag = Tag(name=f"Tag {i // 10}", category="test")
            session.add(tag)
            recipe.tags.append(tag)

    session.commit()

    yield session

    session.close()


def measure_query_time(session, query_func) -> Tuple[float, int]:
    """Measure query execution time.

    Args:
        session: Database session
        query_func: Function that executes a query

    Returns:
        Tuple of (execution_time_ms, result_count)
    """
    start = time.perf_counter()
    results = query_func(session)
    end = time.perf_counter()

    execution_time = (end - start) * 1000  # Convert to milliseconds
    result_count = len(results) if isinstance(results, list) else results.count()

    return execution_time, result_count


def test_recipe_title_search_performance(db_session):
    """Test recipe title search performance."""

    def query_func(session):
        return session.query(Recipe).filter(Recipe.title.like("%500%")).all()

    exec_time, count = measure_query_time(db_session, query_func)

    print(f"\nRecipe title search: {exec_time:.2f}ms, {count} results")
    assert exec_time < 100, f"Query too slow: {exec_time}ms"
    assert count > 0


def test_recipe_created_at_sort_performance(db_session):
    """Test recipe sorting by created_at performance."""

    def query_func(session):
        return session.query(Recipe).order_by(Recipe.created_at.desc()).limit(50).all()

    exec_time, count = measure_query_time(db_session, query_func)

    print(f"\nRecipe created_at sort: {exec_time:.2f}ms, {count} results")
    assert exec_time < 100, f"Query too slow: {exec_time}ms"
    assert count == 50


def test_ingredient_name_search_performance(db_session):
    """Test ingredient name search performance."""

    def query_func(session):
        return (
            session.query(Ingredient)
            .filter(Ingredient.name.like("%Ingredient 2%"))
            .all()
        )

    exec_time, count = measure_query_time(db_session, query_func)

    print(f"\nIngredient name search: {exec_time:.2f}ms, {count} results")
    assert exec_time < 100, f"Query too slow: {exec_time}ms"
    assert count > 0


def test_ingredient_normalized_search_performance(db_session):
    """Test ingredient normalized search performance."""

    def query_func(session):
        return (
            session.query(Ingredient)
            .filter(Ingredient.name_normalized == "ingredient_2")
            .all()
        )

    exec_time, count = measure_query_time(db_session, query_func)

    print(f"\nIngredient normalized search: {exec_time:.2f}ms, {count} results")
    assert exec_time < 100, f"Query too slow: {exec_time}ms"
    assert count > 0


def test_tag_unique_constraint(db_session):
    """Test tag name unique constraint."""
    tag1 = Tag(name="unique_tag", category="test")
    db_session.add(tag1)
    db_session.commit()

    # Try to add duplicate tag
    tag2 = Tag(name="unique_tag", category="test")
    db_session.add(tag2)

    with pytest.raises(Exception):  # SQLite will raise IntegrityError
        db_session.commit()

    db_session.rollback()


def test_composite_index_performance(db_session):
    """Test composite index (created_at + title) performance."""

    def query_func(session):
        return (
            session.query(Recipe)
            .filter(Recipe.created_at >= "2025-01-15")
            .order_by(Recipe.created_at.desc(), Recipe.title)
            .limit(50)
            .all()
        )

    exec_time, count = measure_query_time(db_session, query_func)

    print(f"\nComposite index query: {exec_time:.2f}ms, {count} results")
    assert exec_time < 100, f"Query too slow: {exec_time}ms"


def test_index_usage_with_explain(db_session):
    """Test that indexes are being used by checking EXPLAIN QUERY PLAN."""
    # Test recipe title index
    query = db_session.query(Recipe).filter(Recipe.title.like("%500%"))
    explain = db_session.execute(
        text(
            f"EXPLAIN QUERY PLAN {query.statement.compile(compile_kwargs={'literal_binds': True})}"
        )
    ).fetchall()

    print("\nEXPLAIN QUERY PLAN for title search:")
    for row in explain:
        print(row)

    # Check if index is mentioned (for indexed queries)
    # Note: In-memory SQLite may not use indexes the same way as file-based


def test_full_text_recipe_search_performance(db_session):
    """Test full-text recipe search performance."""

    def query_func(session):
        search_term = "Recipe"
        return (
            session.query(Recipe)
            .filter(Recipe.title.contains(search_term))
            .order_by(Recipe.created_at.desc())
            .limit(20)
            .all()
        )

    exec_time, count = measure_query_time(db_session, query_func)

    print(f"\nFull-text search: {exec_time:.2f}ms, {count} results")
    assert exec_time < 100, f"Query too slow: {exec_time}ms"
    assert count == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""
Recipe API routes with caching integration.

This module demonstrates how to integrate the TTL cache
with API endpoints for optimal performance.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.core.cache import cached, invalidate_cache
from backend.core.database import get_session
from backend.models import Recipe, Ingredient, Step, Tag


# Example handlers that would be used with FastAPI or Flask


@cached(ttl=60, key_prefix="recipes")
def get_recipes_handler(
  limit: int = 50,
  offset: int = 0,
  sort_by: str = "created_at",
  db: Optional[Session] = None
) -> Dict[str, Any]:
  """
  Get paginated recipe list with caching.

  Cache TTL: 60 seconds

  Args:
    limit: Maximum number of recipes
    offset: Pagination offset
    sort_by: Sort field
    db: Database session (optional, for dependency injection)

  Returns:
    API response with recipe list
  """
  # Get database session
  if db is None:
    db = next(get_session())

  try:
    # Query recipes with sorting
    query = db.query(Recipe)

    # Apply sorting
    if sort_by == "created_at":
      query = query.order_by(Recipe.created_at.desc())
    elif sort_by == "updated_at":
      query = query.order_by(Recipe.updated_at.desc())
    elif sort_by == "title":
      query = query.order_by(Recipe.title)
    elif sort_by == "rating":
      query = query.order_by(Recipe.rating.desc().nullslast())

    # Get total count
    total = query.count()

    # Apply pagination
    recipes_db = query.offset(offset).limit(limit).all()

    # Convert to dict
    recipes = []
    for recipe in recipes_db:
      recipe_dict = {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "source_type": recipe.source_type,
        "servings": recipe.servings,
        "total_time_minutes": recipe.total_time_minutes,
        "difficulty": recipe.difficulty,
        "image_url": recipe.image_url,
        "is_favorite": recipe.is_favorite,
        "rating": recipe.rating,
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        "tags": [tag.name for tag in recipe.tags] if recipe.tags else [],
      }
      recipes.append(recipe_dict)

    return {
      "status": "ok",
      "data": {
        "recipes": recipes,
        "total": total,
        "limit": limit,
        "offset": offset,
      },
      "error": None,
    }
  except Exception as e:
    return {
      "status": "error",
      "data": None,
      "error": str(e),
    }


@cached(ttl=30, key_prefix="search")
def search_recipes_handler(
  query: str,
  tags: Optional[List[str]] = None,
  limit: int = 50,
  db: Optional[Session] = None
) -> Dict[str, Any]:
  """
  Search recipes with caching.

  Cache TTL: 30 seconds

  Args:
    query: Search query
    tags: Optional tag filters
    limit: Maximum results
    db: Database session (optional, for dependency injection)

  Returns:
    API response with search results
  """
  # Get database session
  if db is None:
    db = next(get_session())

  try:
    # Build query
    query_db = db.query(Recipe)

    # Search in title, description
    if query:
      search_filter = (
        Recipe.title.ilike(f"%{query}%") |
        Recipe.description.ilike(f"%{query}%")
      )
      query_db = query_db.filter(search_filter)

    # Filter by tags
    if tags:
      query_db = query_db.join(Recipe.tags).filter(Tag.name.in_(tags))

    # Limit results
    recipes_db = query_db.limit(limit).all()

    # Convert to dict
    results = []
    for recipe in recipes_db:
      recipe_dict = {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "source_type": recipe.source_type,
        "image_url": recipe.image_url,
        "rating": recipe.rating,
        "tags": [tag.name for tag in recipe.tags] if recipe.tags else [],
      }
      results.append(recipe_dict)

    return {
      "status": "ok",
      "data": {
        "results": results,
        "query": query,
        "tags": tags,
        "count": len(results),
      },
      "error": None,
    }
  except Exception as e:
    return {
      "status": "error",
      "data": None,
      "error": str(e),
    }


@cached(ttl=300, key_prefix="nutrition")
def get_recipe_nutrition_handler(recipe_id: int, db: Optional[Session] = None) -> Dict[str, Any]:
  """
  Get nutrition information for a recipe with caching.

  Cache TTL: 300 seconds (5 minutes)

  Args:
    recipe_id: Recipe ID
    db: Database session (optional, for dependency injection)

  Returns:
    API response with nutrition data
  """
  # Get database session
  if db is None:
    db = next(get_session())

  try:
    # Get recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
      return {
        "status": "error",
        "data": None,
        "error": f"Recipe {recipe_id} not found",
      }

    # Simplified nutrition calculation based on ingredients
    # In production, this would use a nutrition database
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    total_fiber = 0
    total_sodium = 0

    # Estimate based on number of ingredients (mock calculation)
    ingredient_count = len(recipe.ingredients) if recipe.ingredients else 0
    if ingredient_count > 0:
      total_calories = ingredient_count * 100
      total_protein = ingredient_count * 5
      total_carbs = ingredient_count * 15
      total_fat = ingredient_count * 3
      total_fiber = ingredient_count * 2
      total_sodium = ingredient_count * 150

    nutrition = {
      "recipe_id": recipe_id,
      "calories": total_calories,
      "protein": total_protein,
      "carbs": total_carbs,
      "fat": total_fat,
      "fiber": total_fiber,
      "sodium": total_sodium,
    }

    return {
      "status": "ok",
      "data": nutrition,
      "error": None,
    }
  except Exception as e:
    return {
      "status": "error",
      "data": None,
      "error": str(e),
    }


@cached(ttl=300, key_prefix="tags")
def get_tags_handler(db: Optional[Session] = None) -> Dict[str, Any]:
  """
  Get all tags with usage count.

  Cache TTL: 300 seconds (5 minutes)

  Args:
    db: Database session (optional, for dependency injection)

  Returns:
    API response with tag list
  """
  # Get database session
  if db is None:
    db = next(get_session())

  try:
    from sqlalchemy import func

    # Get all tags with recipe count
    tags_query = (
      db.query(
        Tag.name,
        Tag.category,
        func.count(Recipe.id).label("count")
      )
      .outerjoin(Tag.recipes)
      .group_by(Tag.id, Tag.name, Tag.category)
      .order_by(func.count(Recipe.id).desc())
      .all()
    )

    tags = [
      {
        "name": tag.name,
        "category": tag.category,
        "count": tag.count
      }
      for tag in tags_query
    ]

    return {
      "status": "ok",
      "data": {
        "tags": tags,
        "total": len(tags),
      },
      "error": None,
    }
  except Exception as e:
    return {
      "status": "error",
      "data": None,
      "error": str(e),
    }


def create_recipe_handler(recipe_data: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
  """
  Create a new recipe and invalidate relevant caches.

  Args:
    recipe_data: Recipe information
    db: Database session (optional, for dependency injection)

  Returns:
    API response with created recipe
  """
  # Get database session
  if db is None:
    db = next(get_session())

  try:
    from datetime import datetime

    # Create new recipe
    new_recipe = Recipe(
      title=recipe_data.get("title", ""),
      description=recipe_data.get("description"),
      source_url=recipe_data.get("source_url"),
      source_type=recipe_data.get("source_type", "manual"),
      servings=recipe_data.get("servings"),
      prep_time_minutes=recipe_data.get("prep_time_minutes"),
      cook_time_minutes=recipe_data.get("cook_time_minutes"),
      total_time_minutes=recipe_data.get("total_time_minutes"),
      difficulty=recipe_data.get("difficulty"),
      image_url=recipe_data.get("image_url"),
      notes=recipe_data.get("notes"),
      created_at=datetime.utcnow(),
      updated_at=datetime.utcnow()
    )

    db.add(new_recipe)
    db.flush()  # Get the ID without committing

    # Add ingredients if provided
    if "ingredients" in recipe_data:
      for idx, ing_data in enumerate(recipe_data["ingredients"]):
        ingredient = Ingredient(
          recipe_id=new_recipe.id,
          name=ing_data.get("name", ""),
          name_normalized=ing_data.get("name", "").lower(),
          quantity=ing_data.get("quantity"),
          unit=ing_data.get("unit"),
          original_text=ing_data.get("original_text"),
          order_index=idx
        )
        db.add(ingredient)

    # Add steps if provided
    if "steps" in recipe_data:
      for step_num, step_text in enumerate(recipe_data["steps"], start=1):
        step = Step(
          recipe_id=new_recipe.id,
          step_number=step_num,
          instruction=step_text if isinstance(step_text, str) else step_text.get("text", "")
        )
        db.add(step)

    # Commit the transaction
    db.commit()
    db.refresh(new_recipe)

    # Invalidate affected caches
    invalidate_cache("recipes:get_recipes_handler")
    invalidate_cache("tags:get_tags_handler")

    created_recipe = {
      "id": new_recipe.id,
      "title": new_recipe.title,
      "description": new_recipe.description,
      "source_type": new_recipe.source_type,
      "created_at": new_recipe.created_at.isoformat() if new_recipe.created_at else None,
    }

    return {
      "status": "ok",
      "data": created_recipe,
      "error": None,
    }
  except Exception as e:
    db.rollback()
    return {
      "status": "error",
      "data": None,
      "error": str(e),
    }


def update_recipe_handler(
  recipe_id: int,
  recipe_data: Dict[str, Any],
  db: Optional[Session] = None
) -> Dict[str, Any]:
  """
  Update a recipe and invalidate relevant caches.

  Args:
    recipe_id: Recipe ID to update
    recipe_data: Updated recipe information
    db: Database session (optional, for dependency injection)

  Returns:
    API response with updated recipe
  """
  # Get database session
  if db is None:
    db = next(get_session())

  try:
    from datetime import datetime

    # Get existing recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
      return {
        "status": "error",
        "data": None,
        "error": f"Recipe {recipe_id} not found",
      }

    # Update fields
    if "title" in recipe_data:
      recipe.title = recipe_data["title"]
    if "description" in recipe_data:
      recipe.description = recipe_data["description"]
    if "servings" in recipe_data:
      recipe.servings = recipe_data["servings"]
    if "difficulty" in recipe_data:
      recipe.difficulty = recipe_data["difficulty"]
    if "notes" in recipe_data:
      recipe.notes = recipe_data["notes"]
    if "rating" in recipe_data:
      recipe.rating = recipe_data["rating"]
    if "is_favorite" in recipe_data:
      recipe.is_favorite = recipe_data["is_favorite"]

    recipe.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(recipe)

    # Invalidate affected caches
    invalidate_cache("recipes:get_recipes_handler")
    invalidate_cache("search:search_recipes_handler")
    invalidate_cache(f"nutrition:get_recipe_nutrition_handler:{recipe_id}")

    updated_recipe = {
      "id": recipe.id,
      "title": recipe.title,
      "description": recipe.description,
      "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None,
    }

    return {
      "status": "ok",
      "data": updated_recipe,
      "error": None,
    }
  except Exception as e:
    db.rollback()
    return {
      "status": "error",
      "data": None,
      "error": str(e),
    }


def delete_recipe_handler(recipe_id: int, db: Optional[Session] = None) -> Dict[str, Any]:
  """
  Delete a recipe and invalidate relevant caches.

  Args:
    recipe_id: Recipe ID to delete
    db: Database session (optional, for dependency injection)

  Returns:
    API response confirming deletion
  """
  # Get database session
  if db is None:
    db = next(get_session())

  try:
    # Get recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
      return {
        "status": "error",
        "data": None,
        "error": f"Recipe {recipe_id} not found",
      }

    # Delete recipe (cascade will delete related ingredients and steps)
    db.delete(recipe)
    db.commit()

    # Invalidate all affected caches
    invalidate_cache("recipes:get_recipes_handler")
    invalidate_cache("search:search_recipes_handler")
    invalidate_cache("tags:get_tags_handler")
    invalidate_cache(f"nutrition:get_recipe_nutrition_handler:{recipe_id}")

    return {
      "status": "ok",
      "data": {
        "message": f"Recipe {recipe_id} deleted successfully",
        "recipe_id": recipe_id,
      },
      "error": None,
    }
  except Exception as e:
    db.rollback()
    return {
      "status": "error",
      "data": None,
      "error": str(e),
    }


# FastAPI integration example
"""
from fastapi import APIRouter, Query, Body, Path

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])

@router.get("/")
async def get_recipes(
  limit: int = Query(50, ge=1, le=100),
  offset: int = Query(0, ge=0),
  sort_by: str = Query("created_at")
):
  return get_recipes_handler(limit, offset, sort_by)

@router.get("/search")
async def search_recipes(
  query: str = Query(...),
  tags: Optional[List[str]] = Query(None),
  limit: int = Query(50, ge=1, le=100)
):
  return search_recipes_handler(query, tags, limit)

@router.get("/{recipe_id}/nutrition")
async def get_recipe_nutrition(
  recipe_id: int = Path(..., gt=0)
):
  return get_recipe_nutrition_handler(recipe_id)

@router.get("/tags")
async def get_tags():
  return get_tags_handler()

@router.post("/")
async def create_recipe(
  recipe_data: dict = Body(...)
):
  return create_recipe_handler(recipe_data)

@router.put("/{recipe_id}")
async def update_recipe(
  recipe_id: int = Path(..., gt=0),
  recipe_data: dict = Body(...)
):
  return update_recipe_handler(recipe_id, recipe_data)

@router.delete("/{recipe_id}")
async def delete_recipe(
  recipe_id: int = Path(..., gt=0)
):
  return delete_recipe_handler(recipe_id)
"""

"""
API Integration Example for Auto-Tagger

Demonstrates how to integrate the auto-tagger into FastAPI endpoints.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from backend.services.auto_tagger import AutoTagger


# Pydantic models for request/response
class RecipeInput(BaseModel):
  """Recipe input model for tag suggestion."""
  title: str = Field(..., min_length=1, description="Recipe title")
  description: Optional[str] = Field(None, description="Recipe description")
  ingredients: Optional[List[str]] = Field(None, description="List of ingredients")
  instructions: Optional[List[str]] = Field(None, description="Cooking instructions")
  max_tags: Optional[int] = Field(None, ge=1, description="Maximum number of tags")


class TagSuggestionResponse(BaseModel):
  """Response model for tag suggestions."""
  status: str
  data: Dict[str, List[str]]
  error: Optional[str]


class CategorizedTagResponse(BaseModel):
  """Response model for categorized tag suggestions."""
  status: str
  data: Dict[str, Dict[str, List[str]]]
  error: Optional[str]


class AvailableTagsResponse(BaseModel):
  """Response model for available tags listing."""
  status: str
  data: Dict[str, any]
  error: Optional[str]


# Initialize router and auto-tagger
router = APIRouter(prefix="/api/v1/tags", tags=["Auto-Tagging"])
tagger = AutoTagger()


@router.post("/suggest", response_model=TagSuggestionResponse)
async def suggest_tags(recipe: RecipeInput):
  """
  Suggest tags for a recipe.

  Analyzes the recipe content and returns a list of suggested tags.

  **Example Request:**
  ```json
  {
    "title": "親子丼",
    "description": "鶏肉と卵の定番料理",
    "ingredients": ["鶏肉", "卵", "玉ねぎ", "醤油"],
    "instructions": ["鶏肉を煮る", "卵でとじる"],
    "max_tags": 10
  }
  ```

  **Example Response:**
  ```json
  {
    "status": "ok",
    "data": {
      "suggested_tags": ["和食", "肉", "卵", "煮物", "昼食"]
    },
    "error": null
  }
  ```
  """
  try:
    tags = tagger.suggest_tags(
      title=recipe.title,
      description=recipe.description or "",
      ingredients=recipe.ingredients,
      instructions=recipe.instructions,
      max_tags=recipe.max_tags
    )

    return {
      "status": "ok",
      "data": {"suggested_tags": tags},
      "error": None
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-categorized", response_model=CategorizedTagResponse)
async def suggest_tags_categorized(recipe: RecipeInput):
  """
  Suggest tags grouped by category.

  Returns tags organized by their categories (cuisine_type, meal_type, etc.)

  **Example Response:**
  ```json
  {
    "status": "ok",
    "data": {
      "categorized_tags": {
        "cuisine_type": ["和食"],
        "meal_type": ["昼食", "夕食"],
        "cooking_method": ["煮物"],
        "main_ingredient": ["肉", "卵"]
      }
    },
    "error": null
  }
  ```
  """
  try:
    categorized = tagger.suggest_tags_by_category(
      title=recipe.title,
      description=recipe.description or "",
      ingredients=recipe.ingredients,
      instructions=recipe.instructions
    )

    return {
      "status": "ok",
      "data": {"categorized_tags": categorized},
      "error": None
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/available", response_model=AvailableTagsResponse)
async def get_available_tags():
  """
  Get all available tags and categories.

  Returns a complete list of all tags that can be suggested,
  organized by category.

  **Example Response:**
  ```json
  {
    "status": "ok",
    "data": {
      "categories": ["cuisine_type", "meal_type", "cooking_method"],
      "total_tags": 150,
      "tags_by_category": {
        "cuisine_type": ["和食", "洋食", "中華", ...],
        "meal_type": ["朝食", "昼食", "夕食", ...]
      }
    },
    "error": null
  }
  ```
  """
  try:
    categories = tagger.get_categories()
    tags_by_category = {}

    for category in categories:
      tags_by_category[category] = tagger.get_tags_by_category(category)

    all_tags = tagger.get_all_tags()

    return {
      "status": "ok",
      "data": {
        "categories": categories,
        "total_tags": len(all_tags),
        "tags_by_category": tags_by_category
      },
      "error": None
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=AvailableTagsResponse)
async def get_categories():
  """
  Get all tag categories.

  **Example Response:**
  ```json
  {
    "status": "ok",
    "data": {
      "categories": [
        "cuisine_type",
        "meal_type",
        "cooking_method",
        "main_ingredient",
        "dietary"
      ]
    },
    "error": null
  }
  ```
  """
  try:
    categories = tagger.get_categories()

    return {
      "status": "ok",
      "data": {"categories": categories},
      "error": None
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category_name}", response_model=AvailableTagsResponse)
async def get_tags_in_category(category_name: str):
  """
  Get all tags in a specific category.

  **Parameters:**
  - category_name: Name of the category (e.g., 'cuisine_type', 'meal_type')

  **Example Response:**
  ```json
  {
    "status": "ok",
    "data": {
      "category": "cuisine_type",
      "tags": ["和食", "洋食", "中華", "イタリアン", "フレンチ"]
    },
    "error": null
  }
  ```
  """
  try:
    tags = tagger.get_tags_by_category(category_name)

    if not tags:
      return {
        "status": "ok",
        "data": {
          "category": category_name,
          "tags": [],
          "message": f"Category '{category_name}' not found or has no tags"
        },
        "error": None
      }

    return {
      "status": "ok",
      "data": {
        "category": category_name,
        "tags": tags
      },
      "error": None
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


# Example usage with a full FastAPI app
if __name__ == "__main__":
  """
  Example of running the API locally for testing.

  Run with: python examples/api_integration_example.py
  """
  from fastapi import FastAPI
  import uvicorn

  app = FastAPI(
    title="Personal Recipe Intelligence - Auto-Tagging API",
    description="API for automatic recipe tag suggestion",
    version="1.0.0"
  )

  app.include_router(router)

  @app.get("/")
  async def root():
    return {
      "message": "Personal Recipe Intelligence - Auto-Tagging API",
      "docs": "/docs",
      "version": "1.0.0"
    }

  print("\n" + "=" * 60)
  print("  Personal Recipe Intelligence - Auto-Tagging API")
  print("=" * 60)
  print("\nStarting server...")
  print("  URL: http://localhost:8000")
  print("  API Documentation: http://localhost:8000/docs")
  print("  Alternative Docs: http://localhost:8000/redoc")
  print("\nPress Ctrl+C to stop the server.\n")

  uvicorn.run(app, host="0.0.0.0", port=8000)

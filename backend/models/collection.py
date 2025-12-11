"""
Collection data models for Personal Recipe Intelligence.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class CollectionVisibility(str, Enum):
  """Collection visibility types."""

  PUBLIC = "public"
  PRIVATE = "private"


@dataclass
class CollectionItem:
  """Recipe item in a collection."""

  recipe_id: str
  added_at: str  # ISO8601 timestamp
  note: Optional[str] = None
  position: int = 0  # For custom ordering


@dataclass
class Collection:
  """Recipe collection."""

  id: str
  name: str
  description: Optional[str]
  owner_id: str
  visibility: CollectionVisibility
  created_at: str  # ISO8601 timestamp
  updated_at: str  # ISO8601 timestamp
  is_default: bool = False
  recipes: List[CollectionItem] = field(default_factory=list)
  tags: List[str] = field(default_factory=list)
  thumbnail_url: Optional[str] = None

  def to_dict(self) -> dict:
    """Convert to dictionary."""
    return {
      "id": self.id,
      "name": self.name,
      "description": self.description,
      "owner_id": self.owner_id,
      "visibility": self.visibility.value,
      "created_at": self.created_at,
      "updated_at": self.updated_at,
      "is_default": self.is_default,
      "recipes": [
        {
          "recipe_id": item.recipe_id,
          "added_at": item.added_at,
          "note": item.note,
          "position": item.position,
        }
        for item in self.recipes
      ],
      "tags": self.tags,
      "thumbnail_url": self.thumbnail_url,
      "recipe_count": len(self.recipes),
    }

  @classmethod
  def from_dict(cls, data: dict) -> "Collection":
    """Create from dictionary."""
    recipes = [
      CollectionItem(
        recipe_id=item["recipe_id"],
        added_at=item["added_at"],
        note=item.get("note"),
        position=item.get("position", 0),
      )
      for item in data.get("recipes", [])
    ]

    return cls(
      id=data["id"],
      name=data["name"],
      description=data.get("description"),
      owner_id=data["owner_id"],
      visibility=CollectionVisibility(data["visibility"]),
      created_at=data["created_at"],
      updated_at=data["updated_at"],
      is_default=data.get("is_default", False),
      recipes=recipes,
      tags=data.get("tags", []),
      thumbnail_url=data.get("thumbnail_url"),
    )


@dataclass
class CollectionStats:
  """Collection statistics."""

  total_collections: int
  public_collections: int
  private_collections: int
  total_recipes: int
  most_popular_collection_id: Optional[str] = None

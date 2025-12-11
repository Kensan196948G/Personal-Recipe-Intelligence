"""
Collection service for Personal Recipe Intelligence.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from backend.models.collection import (
  Collection,
  CollectionItem,
  CollectionStats,
  CollectionVisibility,
)


class CollectionService:
  """Service for managing recipe collections."""

  MAX_RECIPES_PER_COLLECTION = 100
  DEFAULT_COLLECTIONS = [
    {"name": "お気に入り", "description": "お気に入りのレシピ"},
    {"name": "作りたい", "description": "今度作ってみたいレシピ"},
    {"name": "作った", "description": "実際に作ったレシピ"},
  ]

  def __init__(self, data_dir: str = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/data"):
    """
    Initialize collection service.

    Args:
      data_dir: Directory for storing collection data
    """
    self.data_dir = Path(data_dir)
    self.collections_dir = self.data_dir / "collections"
    self.collections_dir.mkdir(parents=True, exist_ok=True)
    self.collections_file = self.collections_dir / "collections.json"

    # Initialize collections file if not exists
    if not self.collections_file.exists():
      self._save_collections([])

  def _load_collections(self) -> List[Collection]:
    """Load all collections from file."""
    try:
      with open(self.collections_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Collection.from_dict(item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
      return []

  def _save_collections(self, collections: List[Collection]) -> None:
    """Save collections to file."""
    with open(self.collections_file, "w", encoding="utf-8") as f:
      json.dump([c.to_dict() for c in collections], f, ensure_ascii=False, indent=2)

  def _get_collection_by_id(
    self, collection_id: str, collections: List[Collection]
  ) -> Optional[Collection]:
    """Get collection by ID from list."""
    for collection in collections:
      if collection.id == collection_id:
        return collection
    return None

  def create_default_collections(self, owner_id: str) -> List[Collection]:
    """
    Create default collections for a new user.

    Args:
      owner_id: User ID

    Returns:
      List of created collections
    """
    collections = self._load_collections()
    created = []

    now = datetime.utcnow().isoformat()

    for default in self.DEFAULT_COLLECTIONS:
      collection = Collection(
        id=str(uuid.uuid4()),
        name=default["name"],
        description=default["description"],
        owner_id=owner_id,
        visibility=CollectionVisibility.PRIVATE,
        created_at=now,
        updated_at=now,
        is_default=True,
      )
      collections.append(collection)
      created.append(collection)

    self._save_collections(collections)
    return created

  def create_collection(
    self,
    name: str,
    owner_id: str,
    description: Optional[str] = None,
    visibility: CollectionVisibility = CollectionVisibility.PRIVATE,
    tags: Optional[List[str]] = None,
  ) -> Collection:
    """
    Create a new collection.

    Args:
      name: Collection name
      owner_id: Owner user ID
      description: Collection description
      visibility: Public or private
      tags: Collection tags

    Returns:
      Created collection

    Raises:
      ValueError: If name is empty or already exists for user
    """
    if not name or not name.strip():
      raise ValueError("Collection name cannot be empty")

    collections = self._load_collections()

    # Check for duplicate name for same owner
    for collection in collections:
      if collection.owner_id == owner_id and collection.name == name:
        raise ValueError(f"Collection '{name}' already exists")

    now = datetime.utcnow().isoformat()

    collection = Collection(
      id=str(uuid.uuid4()),
      name=name.strip(),
      description=description,
      owner_id=owner_id,
      visibility=visibility,
      created_at=now,
      updated_at=now,
      tags=tags or [],
    )

    collections.append(collection)
    self._save_collections(collections)

    return collection

  def get_collection(self, collection_id: str, user_id: Optional[str] = None) -> Optional[Collection]:
    """
    Get collection by ID.

    Args:
      collection_id: Collection ID
      user_id: Current user ID (for permission check)

    Returns:
      Collection or None if not found/no permission
    """
    collections = self._load_collections()
    collection = self._get_collection_by_id(collection_id, collections)

    if not collection:
      return None

    # Check permissions: owner can see all, others can see public only
    if user_id and collection.owner_id == user_id:
      return collection
    elif collection.visibility == CollectionVisibility.PUBLIC:
      return collection

    return None

  def get_user_collections(self, user_id: str) -> List[Collection]:
    """
    Get all collections for a user.

    Args:
      user_id: User ID

    Returns:
      List of collections
    """
    collections = self._load_collections()
    return [c for c in collections if c.owner_id == user_id]

  def get_public_collections(self, limit: int = 50, offset: int = 0) -> List[Collection]:
    """
    Get public collections.

    Args:
      limit: Maximum number of collections
      offset: Offset for pagination

    Returns:
      List of public collections
    """
    collections = self._load_collections()
    public = [c for c in collections if c.visibility == CollectionVisibility.PUBLIC]

    # Sort by recipe count (descending) then by updated_at
    public.sort(key=lambda c: (len(c.recipes), c.updated_at), reverse=True)

    return public[offset : offset + limit]

  def update_collection(
    self,
    collection_id: str,
    user_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    visibility: Optional[CollectionVisibility] = None,
    tags: Optional[List[str]] = None,
  ) -> Optional[Collection]:
    """
    Update collection.

    Args:
      collection_id: Collection ID
      user_id: User ID (must be owner)
      name: New name
      description: New description
      visibility: New visibility
      tags: New tags

    Returns:
      Updated collection or None if not found/no permission

    Raises:
      ValueError: If name is empty or already exists
    """
    collections = self._load_collections()
    collection = self._get_collection_by_id(collection_id, collections)

    if not collection or collection.owner_id != user_id:
      return None

    # Check for duplicate name
    if name and name != collection.name:
      for c in collections:
        if c.owner_id == user_id and c.name == name and c.id != collection_id:
          raise ValueError(f"Collection '{name}' already exists")

    # Update fields
    if name:
      collection.name = name.strip()
    if description is not None:
      collection.description = description
    if visibility:
      collection.visibility = visibility
    if tags is not None:
      collection.tags = tags

    collection.updated_at = datetime.utcnow().isoformat()

    self._save_collections(collections)
    return collection

  def delete_collection(self, collection_id: str, user_id: str) -> bool:
    """
    Delete collection.

    Args:
      collection_id: Collection ID
      user_id: User ID (must be owner)

    Returns:
      True if deleted, False if not found/no permission
    """
    collections = self._load_collections()
    collection = self._get_collection_by_id(collection_id, collections)

    if not collection or collection.owner_id != user_id:
      return False

    collections = [c for c in collections if c.id != collection_id]
    self._save_collections(collections)
    return True

  def add_recipe(
    self, collection_id: str, recipe_id: str, user_id: str, note: Optional[str] = None
  ) -> Optional[Collection]:
    """
    Add recipe to collection.

    Args:
      collection_id: Collection ID
      recipe_id: Recipe ID
      user_id: User ID (must be owner)
      note: Optional note

    Returns:
      Updated collection or None if not found/no permission

    Raises:
      ValueError: If recipe already in collection or limit exceeded
    """
    collections = self._load_collections()
    collection = self._get_collection_by_id(collection_id, collections)

    if not collection or collection.owner_id != user_id:
      return None

    # Check if recipe already in collection
    for item in collection.recipes:
      if item.recipe_id == recipe_id:
        raise ValueError("Recipe already in collection")

    # Check limit
    if len(collection.recipes) >= self.MAX_RECIPES_PER_COLLECTION:
      raise ValueError(
        f"Collection limit ({self.MAX_RECIPES_PER_COLLECTION}) reached"
      )

    # Add recipe
    item = CollectionItem(
      recipe_id=recipe_id,
      added_at=datetime.utcnow().isoformat(),
      note=note,
      position=len(collection.recipes),
    )
    collection.recipes.append(item)
    collection.updated_at = datetime.utcnow().isoformat()

    self._save_collections(collections)
    return collection

  def remove_recipe(
    self, collection_id: str, recipe_id: str, user_id: str
  ) -> Optional[Collection]:
    """
    Remove recipe from collection.

    Args:
      collection_id: Collection ID
      recipe_id: Recipe ID
      user_id: User ID (must be owner)

    Returns:
      Updated collection or None if not found/no permission
    """
    collections = self._load_collections()
    collection = self._get_collection_by_id(collection_id, collections)

    if not collection or collection.owner_id != user_id:
      return None

    # Remove recipe
    collection.recipes = [r for r in collection.recipes if r.recipe_id != recipe_id]
    collection.updated_at = datetime.utcnow().isoformat()

    # Reorder positions
    for idx, item in enumerate(collection.recipes):
      item.position = idx

    self._save_collections(collections)
    return collection

  def copy_collection(
    self, collection_id: str, user_id: str, new_name: Optional[str] = None
  ) -> Optional[Collection]:
    """
    Copy a collection (must be public or owned by user).

    Args:
      collection_id: Source collection ID
      user_id: New owner user ID
      new_name: Name for copied collection

    Returns:
      Copied collection or None if not found/no permission
    """
    collections = self._load_collections()
    source = self._get_collection_by_id(collection_id, collections)

    if not source:
      return None

    # Check if can copy (public or owned)
    if source.visibility != CollectionVisibility.PUBLIC and source.owner_id != user_id:
      return None

    now = datetime.utcnow().isoformat()

    # Create copy
    copied = Collection(
      id=str(uuid.uuid4()),
      name=new_name or f"{source.name} (コピー)",
      description=source.description,
      owner_id=user_id,
      visibility=CollectionVisibility.PRIVATE,
      created_at=now,
      updated_at=now,
      recipes=[
        CollectionItem(
          recipe_id=item.recipe_id,
          added_at=now,
          note=item.note,
          position=item.position,
        )
        for item in source.recipes
      ],
      tags=source.tags.copy(),
    )

    collections.append(copied)
    self._save_collections(collections)
    return copied

  def get_stats(self) -> CollectionStats:
    """
    Get collection statistics.

    Returns:
      Collection statistics
    """
    collections = self._load_collections()

    total_collections = len(collections)
    public_collections = sum(
      1 for c in collections if c.visibility == CollectionVisibility.PUBLIC
    )
    private_collections = total_collections - public_collections
    total_recipes = sum(len(c.recipes) for c in collections)

    # Find most popular public collection
    public_colls = [
      c for c in collections if c.visibility == CollectionVisibility.PUBLIC
    ]
    most_popular = None
    if public_colls:
      most_popular = max(public_colls, key=lambda c: len(c.recipes)).id

    return CollectionStats(
      total_collections=total_collections,
      public_collections=public_collections,
      private_collections=private_collections,
      total_recipes=total_recipes,
      most_popular_collection_id=most_popular,
    )

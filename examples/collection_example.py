"""
Example usage of collection service for Personal Recipe Intelligence.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.collection import CollectionVisibility
from backend.services.collection_service import CollectionService


def main():
  """Run collection service examples."""
  print("=== Collection Service Example ===\n")

  # Initialize service
  service = CollectionService()

  # Example user ID (in production, this comes from authentication)
  user_id = "user-123"

  # 1. Create default collections
  print("1. Creating default collections...")
  default_collections = service.create_default_collections(user_id)
  for collection in default_collections:
    print(f"  - Created: {collection.name} (ID: {collection.id})")
  print()

  # 2. Create custom collection
  print("2. Creating custom collection...")
  custom_collection = service.create_collection(
    name="週末レシピ",
    owner_id=user_id,
    description="週末に作りたい特別なレシピ",
    visibility=CollectionVisibility.PUBLIC,
    tags=["週末", "特別", "家族"],
  )
  print(f"  - Created: {custom_collection.name}")
  print(f"    ID: {custom_collection.id}")
  print(f"    Visibility: {custom_collection.visibility.value}")
  print()

  # 3. Add recipes to collection
  print("3. Adding recipes to collection...")
  recipe_ids = ["recipe-001", "recipe-002", "recipe-003"]
  for recipe_id in recipe_ids:
    service.add_recipe(
      collection_id=custom_collection.id,
      recipe_id=recipe_id,
      user_id=user_id,
      note=f"Added {recipe_id}",
    )
  print(f"  - Added {len(recipe_ids)} recipes")
  print()

  # 4. Get user collections
  print("4. Getting user collections...")
  collections = service.get_user_collections(user_id)
  print(f"  - Total collections: {len(collections)}")
  for collection in collections:
    print(f"    - {collection.name}: {len(collection.recipes)} recipes")
  print()

  # 5. Update collection
  print("5. Updating collection...")
  updated = service.update_collection(
    collection_id=custom_collection.id,
    user_id=user_id,
    description="週末に家族で楽しむレシピ集（更新版）",
    tags=["週末", "家族", "楽しい"],
  )
  print(f"  - Updated: {updated.name}")
  print(f"    New description: {updated.description}")
  print()

  # 6. Get public collections
  print("6. Getting public collections...")
  public_collections = service.get_public_collections(limit=10)
  print(f"  - Public collections: {len(public_collections)}")
  for collection in public_collections:
    print(f"    - {collection.name}: {len(collection.recipes)} recipes")
  print()

  # 7. Copy collection (simulate another user)
  print("7. Copying collection...")
  other_user_id = "user-456"
  copied = service.copy_collection(
    collection_id=custom_collection.id,
    user_id=other_user_id,
    new_name="コピーした週末レシピ",
  )
  if copied:
    print(f"  - Copied: {copied.name}")
    print(f"    Owner: {copied.owner_id}")
    print(f"    Recipes: {len(copied.recipes)}")
  print()

  # 8. Remove recipe
  print("8. Removing recipe from collection...")
  service.remove_recipe(
    collection_id=custom_collection.id, recipe_id=recipe_ids[0], user_id=user_id
  )
  updated_collection = service.get_collection(custom_collection.id, user_id)
  print(f"  - Removed recipe: {recipe_ids[0]}")
  print(f"    Remaining recipes: {len(updated_collection.recipes)}")
  print()

  # 9. Get statistics
  print("9. Getting collection statistics...")
  stats = service.get_stats()
  print(f"  - Total collections: {stats.total_collections}")
  print(f"  - Public collections: {stats.public_collections}")
  print(f"  - Private collections: {stats.private_collections}")
  print(f"  - Total recipes: {stats.total_recipes}")
  if stats.most_popular_collection_id:
    print(f"  - Most popular: {stats.most_popular_collection_id}")
  print()

  # 10. Delete collection (delete the copied one)
  print("10. Deleting collection...")
  if copied:
    success = service.delete_collection(copied.id, other_user_id)
    if success:
      print(f"  - Deleted: {copied.name}")
  print()

  print("=== Example Complete ===")


if __name__ == "__main__":
  main()

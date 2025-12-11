"""
Tests for collection service.
"""

import tempfile
import uuid

import pytest

from backend.models.collection import CollectionVisibility
from backend.services.collection_service import CollectionService


@pytest.fixture
def temp_data_dir():
  """Create temporary data directory."""
  with tempfile.TemporaryDirectory() as tmpdir:
    yield tmpdir


@pytest.fixture
def service(temp_data_dir):
  """Create collection service with temp directory."""
  return CollectionService(data_dir=temp_data_dir)


@pytest.fixture
def user_id():
  """Generate test user ID."""
  return str(uuid.uuid4())


@pytest.fixture
def other_user_id():
  """Generate another test user ID."""
  return str(uuid.uuid4())


class TestCollectionService:
  """Test collection service."""

  def test_initialization(self, service):
    """Test service initialization."""
    assert service.collections_dir.exists()
    assert service.collections_file.exists()

  def test_create_default_collections(self, service, user_id):
    """Test creating default collections."""
    collections = service.create_default_collections(user_id)

    assert len(collections) == 3
    assert all(c.is_default for c in collections)
    assert all(c.owner_id == user_id for c in collections)
    assert all(c.visibility == CollectionVisibility.PRIVATE for c in collections)

    names = [c.name for c in collections]
    assert "お気に入り" in names
    assert "作りたい" in names
    assert "作った" in names

  def test_create_collection(self, service, user_id):
    """Test creating a collection."""
    collection = service.create_collection(
      name="Test Collection",
      owner_id=user_id,
      description="Test description",
      visibility=CollectionVisibility.PUBLIC,
      tags=["test", "demo"],
    )

    assert collection.name == "Test Collection"
    assert collection.owner_id == user_id
    assert collection.description == "Test description"
    assert collection.visibility == CollectionVisibility.PUBLIC
    assert collection.tags == ["test", "demo"]
    assert not collection.is_default
    assert len(collection.recipes) == 0

  def test_create_collection_empty_name(self, service, user_id):
    """Test creating collection with empty name."""
    with pytest.raises(ValueError, match="cannot be empty"):
      service.create_collection(name="", owner_id=user_id)

  def test_create_collection_duplicate_name(self, service, user_id):
    """Test creating collection with duplicate name."""
    service.create_collection(name="Duplicate", owner_id=user_id)

    with pytest.raises(ValueError, match="already exists"):
      service.create_collection(name="Duplicate", owner_id=user_id)

  def test_create_collection_same_name_different_user(
    self, service, user_id, other_user_id
  ):
    """Test same name for different users is allowed."""
    collection1 = service.create_collection(name="Same Name", owner_id=user_id)
    collection2 = service.create_collection(name="Same Name", owner_id=other_user_id)

    assert collection1.name == collection2.name
    assert collection1.owner_id != collection2.owner_id

  def test_get_collection(self, service, user_id):
    """Test getting collection by ID."""
    created = service.create_collection(name="Test", owner_id=user_id)

    collection = service.get_collection(created.id, user_id)

    assert collection is not None
    assert collection.id == created.id
    assert collection.name == "Test"

  def test_get_collection_not_found(self, service, user_id):
    """Test getting non-existent collection."""
    collection = service.get_collection("invalid-id", user_id)
    assert collection is None

  def test_get_collection_permission_owner(self, service, user_id):
    """Test owner can see private collection."""
    created = service.create_collection(
      name="Private", owner_id=user_id, visibility=CollectionVisibility.PRIVATE
    )

    collection = service.get_collection(created.id, user_id)
    assert collection is not None

  def test_get_collection_permission_other_private(
    self, service, user_id, other_user_id
  ):
    """Test other user cannot see private collection."""
    created = service.create_collection(
      name="Private", owner_id=user_id, visibility=CollectionVisibility.PRIVATE
    )

    collection = service.get_collection(created.id, other_user_id)
    assert collection is None

  def test_get_collection_permission_other_public(
    self, service, user_id, other_user_id
  ):
    """Test other user can see public collection."""
    created = service.create_collection(
      name="Public", owner_id=user_id, visibility=CollectionVisibility.PUBLIC
    )

    collection = service.get_collection(created.id, other_user_id)
    assert collection is not None

  def test_get_user_collections(self, service, user_id, other_user_id):
    """Test getting all user collections."""
    service.create_collection(name="User1-1", owner_id=user_id)
    service.create_collection(name="User1-2", owner_id=user_id)
    service.create_collection(name="User2", owner_id=other_user_id)

    collections = service.get_user_collections(user_id)

    assert len(collections) == 2
    assert all(c.owner_id == user_id for c in collections)

  def test_get_public_collections(self, service, user_id, other_user_id):
    """Test getting public collections."""
    service.create_collection(
      name="Public1", owner_id=user_id, visibility=CollectionVisibility.PUBLIC
    )
    service.create_collection(
      name="Public2", owner_id=other_user_id, visibility=CollectionVisibility.PUBLIC
    )
    service.create_collection(
      name="Private", owner_id=user_id, visibility=CollectionVisibility.PRIVATE
    )

    collections = service.get_public_collections()

    assert len(collections) == 2
    assert all(c.visibility == CollectionVisibility.PUBLIC for c in collections)

  def test_get_public_collections_pagination(self, service, user_id):
    """Test public collections pagination."""
    for i in range(5):
      service.create_collection(
        name=f"Public{i}", owner_id=user_id, visibility=CollectionVisibility.PUBLIC
      )

    page1 = service.get_public_collections(limit=2, offset=0)
    page2 = service.get_public_collections(limit=2, offset=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id

  def test_update_collection(self, service, user_id):
    """Test updating collection."""
    created = service.create_collection(
      name="Original", owner_id=user_id, description="Old description"
    )

    updated = service.update_collection(
      collection_id=created.id,
      user_id=user_id,
      name="Updated",
      description="New description",
      visibility=CollectionVisibility.PUBLIC,
      tags=["new", "tags"],
    )

    assert updated is not None
    assert updated.name == "Updated"
    assert updated.description == "New description"
    assert updated.visibility == CollectionVisibility.PUBLIC
    assert updated.tags == ["new", "tags"]

  def test_update_collection_not_owner(self, service, user_id, other_user_id):
    """Test updating collection by non-owner."""
    created = service.create_collection(name="Test", owner_id=user_id)

    updated = service.update_collection(
      collection_id=created.id, user_id=other_user_id, name="Hacked"
    )

    assert updated is None

  def test_update_collection_duplicate_name(self, service, user_id):
    """Test updating to duplicate name."""
    service.create_collection(name="Existing", owner_id=user_id)
    created = service.create_collection(name="Test", owner_id=user_id)

    with pytest.raises(ValueError, match="already exists"):
      service.update_collection(
        collection_id=created.id, user_id=user_id, name="Existing"
      )

  def test_delete_collection(self, service, user_id):
    """Test deleting collection."""
    created = service.create_collection(name="Test", owner_id=user_id)

    success = service.delete_collection(created.id, user_id)
    assert success

    collection = service.get_collection(created.id, user_id)
    assert collection is None

  def test_delete_collection_not_owner(self, service, user_id, other_user_id):
    """Test deleting collection by non-owner."""
    created = service.create_collection(name="Test", owner_id=user_id)

    success = service.delete_collection(created.id, other_user_id)
    assert not success

    collection = service.get_collection(created.id, user_id)
    assert collection is not None

  def test_add_recipe(self, service, user_id):
    """Test adding recipe to collection."""
    collection = service.create_collection(name="Test", owner_id=user_id)
    recipe_id = str(uuid.uuid4())

    updated = service.add_recipe(
      collection_id=collection.id, recipe_id=recipe_id, user_id=user_id, note="Test note"
    )

    assert updated is not None
    assert len(updated.recipes) == 1
    assert updated.recipes[0].recipe_id == recipe_id
    assert updated.recipes[0].note == "Test note"
    assert updated.recipes[0].position == 0

  def test_add_recipe_duplicate(self, service, user_id):
    """Test adding duplicate recipe."""
    collection = service.create_collection(name="Test", owner_id=user_id)
    recipe_id = str(uuid.uuid4())

    service.add_recipe(collection.id, recipe_id, user_id)

    with pytest.raises(ValueError, match="already in collection"):
      service.add_recipe(collection.id, recipe_id, user_id)

  def test_add_recipe_limit(self, service, user_id):
    """Test adding recipes beyond limit."""
    collection = service.create_collection(name="Test", owner_id=user_id)

    # Add recipes up to limit
    for i in range(CollectionService.MAX_RECIPES_PER_COLLECTION):
      service.add_recipe(collection.id, str(uuid.uuid4()), user_id)

    # Try to add one more
    with pytest.raises(ValueError, match="limit.*reached"):
      service.add_recipe(collection.id, str(uuid.uuid4()), user_id)

  def test_remove_recipe(self, service, user_id):
    """Test removing recipe from collection."""
    collection = service.create_collection(name="Test", owner_id=user_id)
    recipe_id = str(uuid.uuid4())

    service.add_recipe(collection.id, recipe_id, user_id)
    updated = service.remove_recipe(collection.id, recipe_id, user_id)

    assert updated is not None
    assert len(updated.recipes) == 0

  def test_remove_recipe_reorder(self, service, user_id):
    """Test positions are reordered after removal."""
    collection = service.create_collection(name="Test", owner_id=user_id)

    recipe1 = str(uuid.uuid4())
    recipe2 = str(uuid.uuid4())
    recipe3 = str(uuid.uuid4())

    service.add_recipe(collection.id, recipe1, user_id)
    service.add_recipe(collection.id, recipe2, user_id)
    service.add_recipe(collection.id, recipe3, user_id)

    updated = service.remove_recipe(collection.id, recipe2, user_id)

    assert len(updated.recipes) == 2
    assert updated.recipes[0].position == 0
    assert updated.recipes[1].position == 1

  def test_copy_collection(self, service, user_id, other_user_id):
    """Test copying public collection."""
    # Create public collection with recipes
    original = service.create_collection(
      name="Original",
      owner_id=user_id,
      description="Original description",
      visibility=CollectionVisibility.PUBLIC,
      tags=["tag1", "tag2"],
    )

    recipe1 = str(uuid.uuid4())
    recipe2 = str(uuid.uuid4())
    service.add_recipe(original.id, recipe1, user_id, note="Note 1")
    service.add_recipe(original.id, recipe2, user_id, note="Note 2")

    # Copy by another user
    copied = service.copy_collection(original.id, other_user_id, "Copied")

    assert copied is not None
    assert copied.name == "Copied"
    assert copied.owner_id == other_user_id
    assert copied.visibility == CollectionVisibility.PRIVATE
    assert copied.description == original.description
    assert copied.tags == original.tags
    assert len(copied.recipes) == 2

  def test_copy_collection_private(self, service, user_id, other_user_id):
    """Test cannot copy private collection of another user."""
    original = service.create_collection(
      name="Private",
      owner_id=user_id,
      visibility=CollectionVisibility.PRIVATE,
    )

    copied = service.copy_collection(original.id, other_user_id)
    assert copied is None

  def test_copy_collection_own_private(self, service, user_id):
    """Test can copy own private collection."""
    original = service.create_collection(
      name="Private",
      owner_id=user_id,
      visibility=CollectionVisibility.PRIVATE,
    )

    copied = service.copy_collection(original.id, user_id)
    assert copied is not None
    assert copied.owner_id == user_id

  def test_get_stats(self, service, user_id, other_user_id):
    """Test getting collection statistics."""
    # Create collections
    pub1 = service.create_collection(
      name="Public1", owner_id=user_id, visibility=CollectionVisibility.PUBLIC
    )
    pub2 = service.create_collection(
      name="Public2", owner_id=other_user_id, visibility=CollectionVisibility.PUBLIC
    )
    service.create_collection(
      name="Private", owner_id=user_id, visibility=CollectionVisibility.PRIVATE
    )

    # Add recipes
    service.add_recipe(pub1.id, str(uuid.uuid4()), user_id)
    service.add_recipe(pub1.id, str(uuid.uuid4()), user_id)
    service.add_recipe(pub1.id, str(uuid.uuid4()), user_id)
    service.add_recipe(pub2.id, str(uuid.uuid4()), other_user_id)

    stats = service.get_stats()

    assert stats.total_collections == 3
    assert stats.public_collections == 2
    assert stats.private_collections == 1
    assert stats.total_recipes == 4
    assert stats.most_popular_collection_id == pub1.id

  def test_persistence(self, temp_data_dir, user_id):
    """Test collections are persisted across service instances."""
    service1 = CollectionService(data_dir=temp_data_dir)
    created = service1.create_collection(name="Persisted", owner_id=user_id)

    # Create new service instance
    service2 = CollectionService(data_dir=temp_data_dir)
    loaded = service2.get_collection(created.id, user_id)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.name == "Persisted"

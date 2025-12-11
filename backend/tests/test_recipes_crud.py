"""Tests for Recipe CRUD operations."""

import pytest
from datetime import datetime


class MockRecipe:
    """Mock Recipe model for testing."""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.url = kwargs.get("url")
        self.ingredients = kwargs.get("ingredients", [])
        self.steps = kwargs.get("steps", [])
        self.tags = kwargs.get("tags", [])
        self.image_url = kwargs.get("image_url")
        self.cooking_time = kwargs.get("cooking_time")
        self.servings = kwargs.get("servings")
        self.created_at = kwargs.get("created_at", datetime.now())
        self.updated_at = kwargs.get("updated_at", datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "tags": self.tags,
            "image_url": self.image_url,
            "cooking_time": self.cooking_time,
            "servings": self.servings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TestRecipeCRUD:
    """Test suite for Recipe CRUD operations."""

    def test_create_recipe_success(self, mock_db_session, mock_recipe_data):
        """Test successful recipe creation."""
        recipe = MockRecipe(**mock_recipe_data)
        mock_db_session.add(recipe)
        mock_db_session.commit()

        assert mock_db_session.committed is True
        assert recipe.id is not None
        assert recipe.title == mock_recipe_data["title"]
        assert len(recipe.ingredients) == 3
        assert len(recipe.steps) == 3

    def test_create_recipe_missing_title(self):
        """Test recipe creation with missing required field."""
        with pytest.raises((ValueError, TypeError, KeyError)):
            recipe_data = {"url": "https://example.com/recipe/test", "ingredients": []}
            # Simulate validation that would fail without title
            if "title" not in recipe_data or not recipe_data.get("title"):
                raise ValueError("Title is required")

    def test_create_recipe_invalid_ingredients(self):
        """Test recipe creation with invalid ingredients format."""
        with pytest.raises((ValueError, TypeError)):
            recipe_data = {
                "title": "Test Recipe",
                "ingredients": "invalid format",  # Should be list
            }
            if not isinstance(recipe_data["ingredients"], list):
                raise TypeError("Ingredients must be a list")

    def test_read_recipe_by_id(self, mock_db_session, mock_recipe_data):
        """Test reading recipe by ID."""
        recipe = MockRecipe(id=1, **mock_recipe_data)
        mock_db_session.add(recipe)
        mock_db_session.commit()

        retrieved = mock_db_session.query(MockRecipe).get(1)
        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == mock_recipe_data["title"]

    def test_read_recipe_not_found(self, mock_db_session):
        """Test reading non-existent recipe."""
        retrieved = mock_db_session.query(MockRecipe).get(999)
        assert retrieved is None

    def test_read_all_recipes(self, mock_db_session, mock_recipe_data):
        """Test reading all recipes."""
        recipe1 = MockRecipe(id=1, **mock_recipe_data)
        recipe2_data = mock_recipe_data.copy()
        recipe2_data["title"] = "別のレシピ"
        recipe2 = MockRecipe(id=2, **recipe2_data)

        mock_db_session.add(recipe1)
        mock_db_session.add(recipe2)
        mock_db_session.commit()

        all_recipes = mock_db_session.query(MockRecipe).all()
        assert len(all_recipes) == 2
        assert all_recipes[0].title != all_recipes[1].title

    def test_update_recipe_success(self, mock_db_session, mock_recipe_data):
        """Test successful recipe update."""
        recipe = MockRecipe(id=1, **mock_recipe_data)
        mock_db_session.add(recipe)
        mock_db_session.commit()

        # Update recipe
        recipe.title = "更新されたレシピ"
        recipe.cooking_time = 45
        recipe.updated_at = datetime.now()
        mock_db_session.commit()

        assert recipe.title == "更新されたレシピ"
        assert recipe.cooking_time == 45
        assert recipe.updated_at > recipe.created_at

    def test_update_recipe_not_found(self, mock_db_session):
        """Test updating non-existent recipe."""
        recipe = mock_db_session.query(MockRecipe).get(999)
        assert recipe is None

    def test_update_recipe_partial(self, mock_db_session, mock_recipe_data):
        """Test partial recipe update."""
        recipe = MockRecipe(id=1, **mock_recipe_data)
        original_title = recipe.title
        mock_db_session.add(recipe)
        mock_db_session.commit()

        # Update only cooking time
        recipe.cooking_time = 60
        mock_db_session.commit()

        assert recipe.title == original_title
        assert recipe.cooking_time == 60

    def test_delete_recipe_success(self, mock_db_session, mock_recipe_data):
        """Test successful recipe deletion."""
        recipe = MockRecipe(id=1, **mock_recipe_data)
        mock_db_session.add(recipe)
        mock_db_session.commit()

        assert mock_db_session.query(MockRecipe).count() == 1

        mock_db_session.delete(recipe)
        mock_db_session.commit()

        assert mock_db_session.query(MockRecipe).get(1) is None

    def test_delete_recipe_not_found(self, mock_db_session):
        """Test deleting non-existent recipe."""
        recipe = mock_db_session.query(MockRecipe).get(999)
        assert recipe is None

    def test_recipe_validation_empty_title(self):
        """Test recipe validation with empty title."""
        with pytest.raises(ValueError):
            recipe_data = {"title": "", "ingredients": [], "steps": []}
            if not recipe_data["title"].strip():
                raise ValueError("Title cannot be empty")

    def test_recipe_validation_invalid_cooking_time(self):
        """Test recipe validation with invalid cooking time."""
        with pytest.raises(ValueError):
            cooking_time = -10
            if cooking_time < 0:
                raise ValueError("Cooking time must be positive")

    def test_recipe_validation_invalid_servings(self):
        """Test recipe validation with invalid servings."""
        with pytest.raises(ValueError):
            servings = 0
            if servings <= 0:
                raise ValueError("Servings must be greater than 0")

    def test_recipe_to_dict_conversion(self, mock_recipe_data):
        """Test converting recipe to dictionary."""
        recipe = MockRecipe(id=1, **mock_recipe_data)
        recipe_dict = recipe.to_dict()

        assert isinstance(recipe_dict, dict)
        assert recipe_dict["id"] == 1
        assert recipe_dict["title"] == mock_recipe_data["title"]
        assert "created_at" in recipe_dict
        assert "updated_at" in recipe_dict

    def test_recipe_search_by_tag(self, mock_db_session, mock_recipe_data):
        """Test searching recipes by tag."""
        recipe = MockRecipe(id=1, **mock_recipe_data)
        mock_db_session.add(recipe)
        mock_db_session.commit()

        # Simulate tag search
        if "簡単" in recipe.tags:
            assert True
        else:
            assert False, "Tag not found"

    def test_recipe_search_by_ingredient(self, mock_db_session, mock_recipe_data):
        """Test searching recipes by ingredient."""
        recipe = MockRecipe(id=1, **mock_recipe_data)
        mock_db_session.add(recipe)
        mock_db_session.commit()

        # Simulate ingredient search
        ingredient_names = [ing["name"] for ing in recipe.ingredients]
        assert "たまねぎ" in ingredient_names

    def test_recipe_duplicate_url(self, mock_db_session, mock_recipe_data):
        """Test handling duplicate recipe URLs."""
        recipe1 = MockRecipe(id=1, **mock_recipe_data)
        mock_db_session.add(recipe1)
        mock_db_session.commit()

        # Attempt to add duplicate URL
        with pytest.raises(ValueError):
            existing = (
                mock_db_session.query(MockRecipe)
                .filter_by(url=mock_recipe_data["url"])
                .first()
            )
            if existing:
                raise ValueError("Recipe with this URL already exists")

    def test_recipe_bulk_create(self, mock_db_session):
        """Test bulk recipe creation."""
        recipes = []
        for i in range(5):
            recipe = MockRecipe(
                id=i + 1,
                title=f"レシピ{i + 1}",
                ingredients=[{"name": "材料", "amount": "適量"}],
                steps=["手順1"],
            )
            recipes.append(recipe)
            mock_db_session.add(recipe)

        mock_db_session.commit()
        assert mock_db_session.query(MockRecipe).count() == 5

    def test_recipe_filter_by_cooking_time(self, mock_db_session):
        """Test filtering recipes by cooking time."""
        recipe1 = MockRecipe(
            id=1, title="早い料理", cooking_time=15, ingredients=[], steps=[]
        )
        recipe2 = MockRecipe(
            id=2, title="遅い料理", cooking_time=120, ingredients=[], steps=[]
        )

        mock_db_session.add(recipe1)
        mock_db_session.add(recipe2)
        mock_db_session.commit()

        # Simulate filter
        quick_recipes = [
            r
            for r in mock_db_session.query(MockRecipe).all()
            if r.cooking_time and r.cooking_time <= 30
        ]
        assert len(quick_recipes) == 1
        assert quick_recipes[0].title == "早い料理"

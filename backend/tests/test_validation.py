"""Tests for data validation functionality."""

import pytest
from typing import Any, Dict


class RecipeValidator:
    """Validator for recipe data."""

    @staticmethod
    def validate_title(title: str) -> bool:
        """Validate recipe title."""
        if not isinstance(title, str):
            raise TypeError("Title must be a string")
        if not title.strip():
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title is too long (max 200 characters)")
        return True

    @staticmethod
    def validate_ingredients(ingredients: list) -> bool:
        """Validate ingredients list."""
        if not isinstance(ingredients, list):
            raise TypeError("Ingredients must be a list")

        for ingredient in ingredients:
            if not isinstance(ingredient, dict):
                raise TypeError("Each ingredient must be a dict")
            if "name" not in ingredient:
                raise ValueError("Ingredient must have 'name' field")
            if not isinstance(ingredient["name"], str):
                raise TypeError("Ingredient name must be a string")
            if not ingredient["name"].strip():
                raise ValueError("Ingredient name cannot be empty")

        return True

    @staticmethod
    def validate_steps(steps: list) -> bool:
        """Validate cooking steps."""
        if not isinstance(steps, list):
            raise TypeError("Steps must be a list")

        if len(steps) == 0:
            raise ValueError("Recipe must have at least one step")

        for i, step in enumerate(steps):
            if not isinstance(step, str):
                raise TypeError(f"Step {i+1} must be a string")
            if not step.strip():
                raise ValueError(f"Step {i+1} cannot be empty")

        return True

    @staticmethod
    def validate_cooking_time(cooking_time: Any) -> bool:
        """Validate cooking time."""
        if cooking_time is None:
            return True  # Optional field

        if not isinstance(cooking_time, (int, float)):
            raise TypeError("Cooking time must be a number")

        if cooking_time <= 0:
            raise ValueError("Cooking time must be positive")

        if cooking_time > 10080:  # 7 days in minutes
            raise ValueError("Cooking time is unreasonably long")

        return True

    @staticmethod
    def validate_servings(servings: Any) -> bool:
        """Validate servings count."""
        if servings is None:
            return True  # Optional field

        if not isinstance(servings, int):
            raise TypeError("Servings must be an integer")

        if servings <= 0:
            raise ValueError("Servings must be positive")

        if servings > 100:
            raise ValueError("Servings count is unreasonably high")

        return True

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate recipe URL."""
        if url is None:
            return True  # Optional field

        if not isinstance(url, str):
            raise TypeError("URL must be a string")

        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        return True

    @staticmethod
    def validate_tags(tags: list) -> bool:
        """Validate tags list."""
        if tags is None or tags == []:
            return True  # Optional field

        if not isinstance(tags, list):
            raise TypeError("Tags must be a list")

        for tag in tags:
            if not isinstance(tag, str):
                raise TypeError("Each tag must be a string")
            if not tag.strip():
                raise ValueError("Tag cannot be empty")

        return True

    @classmethod
    def validate_recipe(cls, recipe_data: Dict) -> bool:
        """Validate complete recipe data."""
        if not isinstance(recipe_data, dict):
            raise TypeError("Recipe data must be a dictionary")

        # Required fields
        if "title" not in recipe_data:
            raise ValueError("Recipe must have a title")
        cls.validate_title(recipe_data["title"])

        if "ingredients" not in recipe_data:
            raise ValueError("Recipe must have ingredients")
        cls.validate_ingredients(recipe_data["ingredients"])

        if "steps" not in recipe_data:
            raise ValueError("Recipe must have steps")
        cls.validate_steps(recipe_data["steps"])

        # Optional fields
        if "cooking_time" in recipe_data:
            cls.validate_cooking_time(recipe_data["cooking_time"])

        if "servings" in recipe_data:
            cls.validate_servings(recipe_data["servings"])

        if "url" in recipe_data:
            cls.validate_url(recipe_data["url"])

        if "tags" in recipe_data:
            cls.validate_tags(recipe_data["tags"])

        return True


class TestRecipeValidation:
    """Test suite for recipe validation."""

    def test_validate_title_valid(self):
        """Test valid title validation."""
        assert RecipeValidator.validate_title("美味しいカレー") is True
        assert RecipeValidator.validate_title("Simple Recipe") is True

    def test_validate_title_empty(self):
        """Test empty title validation."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            RecipeValidator.validate_title("")

    def test_validate_title_whitespace(self):
        """Test whitespace-only title validation."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            RecipeValidator.validate_title("   ")

    def test_validate_title_too_long(self):
        """Test too long title validation."""
        long_title = "あ" * 201
        with pytest.raises(ValueError, match="Title is too long"):
            RecipeValidator.validate_title(long_title)

    def test_validate_title_not_string(self):
        """Test non-string title validation."""
        with pytest.raises(TypeError, match="Title must be a string"):
            RecipeValidator.validate_title(123)

    def test_validate_ingredients_valid(self):
        """Test valid ingredients validation."""
        ingredients = [
            {"name": "たまねぎ", "amount": "1個"},
            {"name": "にんじん", "amount": "2本"},
        ]
        assert RecipeValidator.validate_ingredients(ingredients) is True

    def test_validate_ingredients_empty_list(self):
        """Test empty ingredients list validation."""
        assert RecipeValidator.validate_ingredients([]) is True

    def test_validate_ingredients_not_list(self):
        """Test non-list ingredients validation."""
        with pytest.raises(TypeError, match="Ingredients must be a list"):
            RecipeValidator.validate_ingredients("not a list")

    def test_validate_ingredients_missing_name(self):
        """Test ingredient missing name field."""
        ingredients = [{"amount": "1個"}]
        with pytest.raises(ValueError, match="must have 'name' field"):
            RecipeValidator.validate_ingredients(ingredients)

    def test_validate_ingredients_empty_name(self):
        """Test ingredient with empty name."""
        ingredients = [{"name": "", "amount": "1個"}]
        with pytest.raises(ValueError, match="name cannot be empty"):
            RecipeValidator.validate_ingredients(ingredients)

    def test_validate_steps_valid(self):
        """Test valid steps validation."""
        steps = ["野菜を洗う", "野菜を切る", "煮込む"]
        assert RecipeValidator.validate_steps(steps) is True

    def test_validate_steps_empty(self):
        """Test empty steps validation."""
        with pytest.raises(ValueError, match="must have at least one step"):
            RecipeValidator.validate_steps([])

    def test_validate_steps_not_list(self):
        """Test non-list steps validation."""
        with pytest.raises(TypeError, match="Steps must be a list"):
            RecipeValidator.validate_steps("not a list")

    def test_validate_steps_empty_step(self):
        """Test empty step in steps."""
        steps = ["野菜を洗う", "", "煮込む"]
        with pytest.raises(ValueError, match="cannot be empty"):
            RecipeValidator.validate_steps(steps)

    def test_validate_cooking_time_valid(self):
        """Test valid cooking time validation."""
        assert RecipeValidator.validate_cooking_time(30) is True
        assert RecipeValidator.validate_cooking_time(120.5) is True
        assert RecipeValidator.validate_cooking_time(None) is True

    def test_validate_cooking_time_negative(self):
        """Test negative cooking time validation."""
        with pytest.raises(ValueError, match="must be positive"):
            RecipeValidator.validate_cooking_time(-10)

    def test_validate_cooking_time_zero(self):
        """Test zero cooking time validation."""
        with pytest.raises(ValueError, match="must be positive"):
            RecipeValidator.validate_cooking_time(0)

    def test_validate_cooking_time_too_long(self):
        """Test unreasonably long cooking time."""
        with pytest.raises(ValueError, match="unreasonably long"):
            RecipeValidator.validate_cooking_time(20000)

    def test_validate_cooking_time_not_number(self):
        """Test non-number cooking time validation."""
        with pytest.raises(TypeError, match="must be a number"):
            RecipeValidator.validate_cooking_time("30 minutes")

    def test_validate_servings_valid(self):
        """Test valid servings validation."""
        assert RecipeValidator.validate_servings(4) is True
        assert RecipeValidator.validate_servings(1) is True
        assert RecipeValidator.validate_servings(None) is True

    def test_validate_servings_negative(self):
        """Test negative servings validation."""
        with pytest.raises(ValueError, match="must be positive"):
            RecipeValidator.validate_servings(-1)

    def test_validate_servings_zero(self):
        """Test zero servings validation."""
        with pytest.raises(ValueError, match="must be positive"):
            RecipeValidator.validate_servings(0)

    def test_validate_servings_too_high(self):
        """Test unreasonably high servings."""
        with pytest.raises(ValueError, match="unreasonably high"):
            RecipeValidator.validate_servings(150)

    def test_validate_servings_not_int(self):
        """Test non-integer servings validation."""
        with pytest.raises(TypeError, match="must be an integer"):
            RecipeValidator.validate_servings(4.5)

    def test_validate_url_valid(self):
        """Test valid URL validation."""
        assert RecipeValidator.validate_url("https://example.com/recipe") is True
        assert RecipeValidator.validate_url("http://example.com") is True
        assert RecipeValidator.validate_url(None) is True

    def test_validate_url_invalid_protocol(self):
        """Test invalid URL protocol."""
        with pytest.raises(ValueError, match="must start with http"):
            RecipeValidator.validate_url("ftp://example.com")

    def test_validate_url_not_string(self):
        """Test non-string URL validation."""
        with pytest.raises(TypeError, match="URL must be a string"):
            RecipeValidator.validate_url(123)

    def test_validate_tags_valid(self):
        """Test valid tags validation."""
        assert RecipeValidator.validate_tags(["簡単", "野菜料理"]) is True
        assert RecipeValidator.validate_tags([]) is True
        assert RecipeValidator.validate_tags(None) is True

    def test_validate_tags_not_list(self):
        """Test non-list tags validation."""
        with pytest.raises(TypeError, match="Tags must be a list"):
            RecipeValidator.validate_tags("not a list")

    def test_validate_tags_empty_tag(self):
        """Test empty tag in tags."""
        with pytest.raises(ValueError, match="Tag cannot be empty"):
            RecipeValidator.validate_tags(["簡単", "", "野菜"])

    def test_validate_recipe_complete_valid(self):
        """Test complete valid recipe validation."""
        recipe = {
            "title": "カレーライス",
            "ingredients": [{"name": "たまねぎ", "amount": "1個"}],
            "steps": ["切る", "煮る"],
            "cooking_time": 30,
            "servings": 4,
            "url": "https://example.com",
            "tags": ["簡単"],
        }
        assert RecipeValidator.validate_recipe(recipe) is True

    def test_validate_recipe_minimal_valid(self):
        """Test minimal valid recipe validation."""
        recipe = {
            "title": "簡単レシピ",
            "ingredients": [{"name": "塩"}],
            "steps": ["混ぜる"],
        }
        assert RecipeValidator.validate_recipe(recipe) is True

    def test_validate_recipe_missing_title(self):
        """Test recipe missing title."""
        recipe = {"ingredients": [{"name": "塩"}], "steps": ["混ぜる"]}
        with pytest.raises(ValueError, match="must have a title"):
            RecipeValidator.validate_recipe(recipe)

    def test_validate_recipe_missing_ingredients(self):
        """Test recipe missing ingredients."""
        recipe = {"title": "テスト", "steps": ["混ぜる"]}
        with pytest.raises(ValueError, match="must have ingredients"):
            RecipeValidator.validate_recipe(recipe)

    def test_validate_recipe_missing_steps(self):
        """Test recipe missing steps."""
        recipe = {"title": "テスト", "ingredients": [{"name": "塩"}]}
        with pytest.raises(ValueError, match="must have steps"):
            RecipeValidator.validate_recipe(recipe)

    def test_validate_recipe_not_dict(self):
        """Test non-dict recipe validation."""
        with pytest.raises(TypeError, match="must be a dictionary"):
            RecipeValidator.validate_recipe("not a dict")

    def test_validate_recipe_invalid_nested_field(self):
        """Test recipe with invalid nested field."""
        recipe = {
            "title": "テスト",
            "ingredients": [{"name": "塩"}],
            "steps": ["混ぜる"],
            "cooking_time": -10,
        }
        with pytest.raises(ValueError, match="must be positive"):
            RecipeValidator.validate_recipe(recipe)

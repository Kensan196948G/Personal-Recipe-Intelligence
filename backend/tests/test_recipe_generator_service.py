"""
レシピ自動生成サービスのテスト
"""

import pytest
from backend.services.recipe_generator_service import RecipeGeneratorService


@pytest.fixture
def generator_service():
    """テスト用のジェネレーターサービス"""
    return RecipeGeneratorService(data_dir="data/test_generator")


class TestRecipeGeneratorService:
    """レシピ自動生成サービスのテスト"""

    def test_generate_recipe_basic(self, generator_service):
        """基本的なレシピ生成のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese"
        )

        assert recipe is not None
        assert "id" in recipe
        assert "name" in recipe
        assert "鶏肉" in recipe["name"]
        assert recipe["category"] == "japanese"
        assert "ingredients" in recipe
        assert "steps" in recipe
        assert len(recipe["steps"]) > 0

    def test_generate_recipe_with_multiple_ingredients(self, generator_service):
        """複数食材でのレシピ生成のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["豚肉", "キャベツ"], category="japanese"
        )

        assert recipe is not None
        assert "豚肉" in recipe["name"]
        ingredient_names = [ing["name"] for ing in recipe["ingredients"]]
        assert "豚肉" in ingredient_names
        assert "キャベツ" in ingredient_names

    def test_generate_recipe_with_cooking_time(self, generator_service):
        """調理時間指定でのレシピ生成のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese", cooking_time=15
        )

        assert recipe is not None
        assert recipe["cooking_time"] <= 15

    def test_generate_recipe_with_difficulty(self, generator_service):
        """難易度指定でのレシピ生成のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese", difficulty="easy"
        )

        assert recipe is not None
        assert recipe["difficulty"] == "easy"

    def test_generate_recipe_western(self, generator_service):
        """洋食レシピ生成のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="western"
        )

        assert recipe is not None
        assert recipe["category"] == "western"

    def test_generate_recipe_chinese(self, generator_service):
        """中華レシピ生成のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["豚肉"], category="chinese"
        )

        assert recipe is not None
        assert recipe["category"] == "chinese"

    def test_generate_recipe_with_seasonal(self, generator_service):
        """季節食材を使ったレシピ生成のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese", use_seasonal=True
        )

        assert recipe is not None
        # 季節の食材が含まれている可能性がある
        assert len(recipe["ingredients"]) > 0

    def test_generate_recipe_without_seasonal(self, generator_service):
        """季節食材なしでのレシピ生成のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["鶏肉", "玉ねぎ"], category="japanese", use_seasonal=False
        )

        assert recipe is not None

    def test_generate_recipe_no_ingredients(self, generator_service):
        """食材なしでのレシピ生成（エラーケース）"""
        with pytest.raises(ValueError, match="食材を最低1つ指定してください"):
            generator_service.generate_recipe(ingredients=[], category="japanese")

    def test_generate_recipe_invalid_category(self, generator_service):
        """無効なカテゴリでのレシピ生成（エラーケース）"""
        with pytest.raises(ValueError, match="無効なカテゴリ"):
            generator_service.generate_recipe(
                ingredients=["鶏肉"], category="invalid_category"
            )

    def test_generate_variations(self, generator_service):
        """バリエーション生成のテスト"""
        base_recipe = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese"
        )

        variations = generator_service.generate_variations(
            base_recipe=base_recipe, count=3
        )

        assert variations is not None
        assert len(variations) > 0
        assert len(variations) <= 3

        for variation in variations:
            assert "id" in variation
            assert "name" in variation
            assert variation["category"] == base_recipe["category"]
            assert "based_on" in variation

    def test_generate_variations_limited_count(self, generator_service):
        """制限された数でのバリエーション生成のテスト"""
        base_recipe = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese"
        )

        variations = generator_service.generate_variations(
            base_recipe=base_recipe, count=1
        )

        assert len(variations) == 1

    def test_suggest_ingredient_combinations(self, generator_service):
        """食材組み合わせ提案のテスト"""
        suggestions = generator_service.suggest_ingredient_combinations(
            main_ingredient="鶏肉", count=5
        )

        assert suggestions is not None
        assert len(suggestions) > 0
        assert len(suggestions) <= 5

        for suggestion in suggestions:
            assert "main" in suggestion
            assert "sub" in suggestion
            assert suggestion["main"] == "鶏肉"
            assert "compatibility_score" in suggestion
            assert "seasonal" in suggestion
            assert "recommended_categories" in suggestion

    def test_suggest_ingredient_combinations_unknown_ingredient(
        self, generator_service
    ):
        """未知の食材での組み合わせ提案のテスト"""
        suggestions = generator_service.suggest_ingredient_combinations(
            main_ingredient="未知の食材", count=5
        )

        # 未知の食材でも提案が返される
        assert suggestions is not None
        assert len(suggestions) > 0

    def test_improve_recipe_taste(self, generator_service):
        """レシピ改善（味）のテスト"""
        original = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese"
        )

        improved = generator_service.improve_recipe(recipe=original, focus="taste")

        assert improved is not None
        assert "improved_at" in improved
        assert improved["improvement_focus"] == "taste"
        assert "味改善版" in improved["tags"]

    def test_improve_recipe_health(self, generator_service):
        """レシピ改善（健康）のテスト"""
        original = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese"
        )

        improved = generator_service.improve_recipe(recipe=original, focus="health")

        assert improved is not None
        assert improved["improvement_focus"] == "health"
        assert "ヘルシー版" in improved["tags"]

    def test_improve_recipe_speed(self, generator_service):
        """レシピ改善（時短）のテスト"""
        original = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese"
        )

        improved = generator_service.improve_recipe(recipe=original, focus="speed")

        assert improved is not None
        assert improved["improvement_focus"] == "speed"
        assert "時短版" in improved["tags"]
        assert improved["cooking_time"] < original["cooking_time"]

    def test_improve_recipe_cost(self, generator_service):
        """レシピ改善（コスト）のテスト"""
        original = generator_service.generate_recipe(
            ingredients=["鶏肉"], category="japanese"
        )

        improved = generator_service.improve_recipe(recipe=original, focus="cost")

        assert improved is not None
        assert improved["improvement_focus"] == "cost"
        assert "節約版" in improved["tags"]

    def test_get_nutrition_estimate(self, generator_service):
        """栄養情報取得のテスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["鶏肉", "玉ねぎ"], category="japanese"
        )

        nutrition = generator_service.get_nutrition_estimate(recipe)

        assert nutrition is not None
        assert "has_protein" in nutrition
        assert "has_vegetable" in nutrition
        assert "has_carbohydrate" in nutrition
        assert "balance_score" in nutrition
        assert "recommendation" in nutrition
        assert 0 <= nutrition["balance_score"] <= 100

    def test_get_nutrition_estimate_with_protein(self, generator_service):
        """たんぱく質を含むレシピの栄養情報テスト"""
        recipe = {
            "ingredients": [
                {"name": "鶏肉", "amount": "200g", "unit": ""},
                {"name": "玉ねぎ", "amount": "1個", "unit": ""},
            ]
        }

        nutrition = generator_service.get_nutrition_estimate(recipe)

        assert nutrition["has_protein"] is True
        assert nutrition["has_vegetable"] is True

    def test_get_nutrition_estimate_no_protein(self, generator_service):
        """たんぱく質なしのレシピの栄養情報テスト"""
        recipe = {"ingredients": [{"name": "玉ねぎ", "amount": "1個", "unit": ""}]}

        nutrition = generator_service.get_nutrition_estimate(recipe)

        assert nutrition["has_protein"] is False
        assert nutrition["has_vegetable"] is True

    def test_recipe_structure(self, generator_service):
        """生成されるレシピの構造テスト"""
        recipe = generator_service.generate_recipe(
            ingredients=["鶏肉", "玉ねぎ"], category="japanese"
        )

        # 必須フィールドの確認
        required_fields = [
            "id",
            "name",
            "category",
            "cooking_time",
            "difficulty",
            "ingredients",
            "steps",
            "servings",
            "tags",
            "generated_at",
        ]

        for field in required_fields:
            assert field in recipe, f"フィールド '{field}' が存在しません"

        # 材料構造の確認
        for ingredient in recipe["ingredients"]:
            assert "name" in ingredient
            assert "amount" in ingredient
            assert "unit" in ingredient

    def test_seasonal_ingredients(self, generator_service):
        """季節食材の取得テスト"""
        season = generator_service._get_current_season()
        assert season in ["spring", "summer", "autumn", "winter"]

        seasonal_ingredients = generator_service.seasonal_ingredients[season]
        assert len(seasonal_ingredients) > 0

    def test_ingredient_compatibility(self, generator_service):
        """食材相性データのテスト"""
        assert "鶏肉" in generator_service.ingredient_compatibility
        assert len(generator_service.ingredient_compatibility["鶏肉"]) > 0

    def test_cooking_methods(self, generator_service):
        """調理方法データのテスト"""
        assert "japanese" in generator_service.cooking_methods
        assert "western" in generator_service.cooking_methods
        assert "chinese" in generator_service.cooking_methods

        for category, methods in generator_service.cooking_methods.items():
            assert len(methods) > 0
            for method in methods:
                assert method in generator_service.templates[category]

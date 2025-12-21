"""
栄養計算サービスのテスト
"""

import pytest
from backend.services.nutrition_service import NutritionService


@pytest.fixture
def nutrition_service():
    """NutritionService のフィクスチャ"""
    return NutritionService()


class TestParseAmount:
    """分量パース機能のテスト"""

    def test_parse_gram(self, nutrition_service):
        """グラム単位のパース"""
        assert nutrition_service.parse_amount("200g") == 200.0
        assert nutrition_service.parse_amount("1.5g") == 1.5

    def test_parse_kilogram(self, nutrition_service):
        """キログラム単位のパース"""
        assert nutrition_service.parse_amount("1kg") == 1000.0
        assert nutrition_service.parse_amount("0.5kg") == 500.0

    def test_parse_milliliter(self, nutrition_service):
        """ミリリットル単位のパース"""
        assert nutrition_service.parse_amount("100ml") == 100.0
        assert nutrition_service.parse_amount("50cc") == 50.0

    def test_parse_tablespoon(self, nutrition_service):
        """大さじのパース"""
        assert nutrition_service.parse_amount("大さじ1") == 15.0
        assert nutrition_service.parse_amount("大さじ2") == 30.0

    def test_parse_teaspoon(self, nutrition_service):
        """小さじのパース"""
        assert nutrition_service.parse_amount("小さじ1") == 5.0
        assert nutrition_service.parse_amount("小さじ3") == 15.0

    def test_parse_cup(self, nutrition_service):
        """カップのパース"""
        assert nutrition_service.parse_amount("1カップ") == 200.0
        assert nutrition_service.parse_amount("2cup") == 400.0

    def test_parse_piece(self, nutrition_service):
        """個数のパース"""
        assert nutrition_service.parse_amount("2個") == 200.0
        assert nutrition_service.parse_amount("3枚") == 300.0

    def test_parse_empty(self, nutrition_service):
        """空文字列のパース"""
        assert nutrition_service.parse_amount("") == 0.0
        assert nutrition_service.parse_amount(None) == 0.0


class TestCalculateIngredientNutrition:
    """材料栄養計算のテスト"""

    def test_calculate_chicken(self, nutrition_service):
        """鶏肉の栄養計算"""
        result = nutrition_service.calculate_ingredient_nutrition("鶏もも肉", "200g")

        assert result["found"] is True
        assert result["ingredient"] == "鶏もも肉"
        assert result["amount"] == "200g"
        assert result["amount_g"] == 200.0
        assert result["calories"] == 400.0  # 200 * 2
        assert result["protein"] == 32.4  # 16.2 * 2

    def test_calculate_unknown_ingredient(self, nutrition_service):
        """未知の材料の栄養計算"""
        result = nutrition_service.calculate_ingredient_nutrition("未知の材料", "100g")

        assert result["found"] is False
        assert result["calories"] == 0
        assert result["protein"] == 0

    def test_calculate_with_tablespoon(self, nutrition_service):
        """大さじ単位での計算"""
        result = nutrition_service.calculate_ingredient_nutrition("醤油", "大さじ1")

        assert result["found"] is True
        # 大さじ1 = 15ml → 15gとして計算
        # 醤油100mlあたり71kcal → 15mlで約10.65kcal
        assert result["calories"] > 0


class TestCalculateRecipeNutrition:
    """レシピ栄養計算のテスト"""

    def test_simple_recipe(self, nutrition_service):
        """シンプルなレシピの計算"""
        ingredients = [
            {"name": "白米", "amount": "200g"},
            {"name": "鶏もも肉", "amount": "100g"},
        ]

        result = nutrition_service.calculate_recipe_nutrition(ingredients, servings=1)

        assert result["servings"] == 1
        assert result["total_ingredients"] == 2
        assert result["found_ingredients"] == 2

        # 白米200g: 168*2 = 336kcal
        # 鶏もも肉100g: 200kcal
        # 合計: 536kcal
        total_calories = result["total"]["calories"]
        assert 530 <= total_calories <= 540

        # 1人前なので total と per_serving は同じ
        assert result["per_serving"]["calories"] == result["total"]["calories"]

    def test_multi_serving_recipe(self, nutrition_service):
        """複数人前のレシピ計算"""
        ingredients = [
            {"name": "白米", "amount": "400g"},
            {"name": "鶏もも肉", "amount": "200g"},
        ]

        result = nutrition_service.calculate_recipe_nutrition(ingredients, servings=2)

        assert result["servings"] == 2
        # 1人前は合計の半分
        assert result["per_serving"]["calories"] == result["total"]["calories"] / 2

    def test_recipe_with_unknown_ingredient(self, nutrition_service):
        """未知の材料を含むレシピ"""
        ingredients = [
            {"name": "白米", "amount": "200g"},
            {"name": "未知の材料", "amount": "100g"},
        ]

        result = nutrition_service.calculate_recipe_nutrition(ingredients, servings=1)

        assert result["total_ingredients"] == 2
        assert result["found_ingredients"] == 1  # 白米のみ


class TestGetNutritionSummary:
    """栄養サマリー生成のテスト"""

    def test_summary_generation(self, nutrition_service):
        """サマリー生成"""
        ingredients = [
            {"name": "白米", "amount": "200g"},
            {"name": "鶏むね肉", "amount": "100g"},
        ]

        nutrition_data = nutrition_service.calculate_recipe_nutrition(
            ingredients, servings=1
        )
        summary = nutrition_service.get_nutrition_summary(nutrition_data)

        assert "calorie_level" in summary
        assert "pfc_balance" in summary
        assert "protein_ratio" in summary
        assert "fat_ratio" in summary
        assert "carb_ratio" in summary

        # PFCバランスの合計は100%に近い
        total_ratio = (
            summary["protein_ratio"] + summary["fat_ratio"] + summary["carb_ratio"]
        )
        assert 99 <= total_ratio <= 101

    def test_calorie_level_low(self, nutrition_service):
        """低カロリー判定"""
        ingredients = [{"name": "レタス", "amount": "200g"}]

        nutrition_data = nutrition_service.calculate_recipe_nutrition(
            ingredients, servings=1
        )
        summary = nutrition_service.get_nutrition_summary(nutrition_data)

        assert summary["calorie_level"] == "低カロリー"

    def test_calorie_level_high(self, nutrition_service):
        """高カロリー判定"""
        ingredients = [{"name": "豚バラ肉", "amount": "300g"}]

        nutrition_data = nutrition_service.calculate_recipe_nutrition(
            ingredients, servings=1
        )
        summary = nutrition_service.get_nutrition_summary(nutrition_data)

        assert summary["calorie_level"] == "高カロリー"


class TestSearchIngredients:
    """材料検索のテスト"""

    def test_search_chicken(self, nutrition_service):
        """鶏肉の検索"""
        results = nutrition_service.search_ingredients("鶏")

        assert len(results) >= 2  # 鶏もも肉、鶏むね肉
        assert any("鶏" in r["name"] for r in results)

    def test_search_partial_match(self, nutrition_service):
        """部分一致検索"""
        results = nutrition_service.search_ingredients("たま")

        # たまねぎ、玉ねぎ が含まれる
        assert len(results) >= 1

    def test_search_no_match(self, nutrition_service):
        """マッチなし検索"""
        results = nutrition_service.search_ingredients("存在しない材料xyz")

        assert len(results) == 0

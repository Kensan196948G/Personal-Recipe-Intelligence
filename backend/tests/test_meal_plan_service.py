"""
献立計画サービスのテスト
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import json
import tempfile
import shutil

from backend.services.meal_plan_service import (
    MealPlanService,
    NutritionInfo,
    RecipeIngredient,
    ShoppingListItem,
    WeeklyNutrition,
)


@pytest.fixture
def temp_data_dir():
    """一時データディレクトリを作成"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def meal_plan_service(temp_data_dir):
    """テスト用献立計画サービス"""
    return MealPlanService(data_dir=temp_data_dir)


@pytest.fixture
def sample_recipes(temp_data_dir):
    """サンプルレシピデータを作成"""
    recipes = [
        {
            "id": 1,
            "name": "カレーライス",
            "servings": 4,
            "ingredients": [
                {"name": "玉ねぎ", "quantity": 2, "unit": "個", "category": "野菜"},
                {"name": "じゃがいも", "quantity": 3, "unit": "個", "category": "野菜"},
                {"name": "豚肉", "quantity": 300, "unit": "g", "category": "肉"},
                {
                    "name": "カレールー",
                    "quantity": 1,
                    "unit": "箱",
                    "category": "調味料",
                },
            ],
            "nutrition": {"calories": 800, "protein": 30, "fat": 25, "carbs": 100},
        },
        {
            "id": 2,
            "name": "ハンバーグ",
            "servings": 2,
            "ingredients": [
                {"name": "牛ひき肉", "quantity": 300, "unit": "g", "category": "肉"},
                {"name": "玉ねぎ", "quantity": 1, "unit": "個", "category": "野菜"},
                {"name": "卵", "quantity": 1, "unit": "個", "category": "卵"},
            ],
            "nutrition": {"calories": 600, "protein": 40, "fat": 35, "carbs": 20},
        },
        {
            "id": 3,
            "name": "サラダ",
            "servings": 2,
            "ingredients": [
                {"name": "レタス", "quantity": 1, "unit": "個", "category": "野菜"},
                {"name": "トマト", "quantity": 2, "unit": "個", "category": "野菜"},
            ],
            "nutrition": {"calories": 50, "protein": 2, "fat": 0.5, "carbs": 10},
        },
    ]

    recipes_file = Path(temp_data_dir) / "recipes.json"
    recipes_file.write_text(json.dumps(recipes, ensure_ascii=False, indent=2))

    return recipes


class TestNutritionInfo:
    """NutritionInfo モデルのテスト"""

    def test_nutrition_info_creation(self):
        """栄養情報の作成"""
        nutrition = NutritionInfo(calories=500, protein=25, fat=15, carbs=60)

        assert nutrition.calories == 500
        assert nutrition.protein == 25
        assert nutrition.fat == 15
        assert nutrition.carbs == 60


class TestRecipeIngredient:
    """RecipeIngredient モデルのテスト"""

    def test_recipe_ingredient_creation(self):
        """レシピ材料の作成"""
        ingredient = RecipeIngredient(
            name="玉ねぎ", quantity=2, unit="個", category="野菜"
        )

        assert ingredient.name == "玉ねぎ"
        assert ingredient.quantity == 2
        assert ingredient.unit == "個"
        assert ingredient.category == "野菜"


class TestMealPlanService:
    """MealPlanService のテスト"""

    def test_service_initialization(self, meal_plan_service, temp_data_dir):
        """サービスの初期化"""
        assert meal_plan_service.data_dir == Path(temp_data_dir)
        assert meal_plan_service.recipes_file == Path(temp_data_dir) / "recipes.json"

    def test_load_recipes_no_file(self, meal_plan_service):
        """レシピファイルが存在しない場合"""
        recipes = meal_plan_service._load_recipes()
        assert recipes == []

    def test_load_recipes_with_data(self, meal_plan_service, sample_recipes):
        """レシピデータの読み込み"""
        recipes = meal_plan_service._load_recipes()
        assert len(recipes) == 3
        assert recipes[0]["name"] == "カレーライス"

    def test_get_recipe_by_id(self, meal_plan_service, sample_recipes):
        """レシピIDからレシピ詳細を取得"""
        recipe = meal_plan_service.get_recipe_by_id(1)

        assert recipe is not None
        assert recipe.id == 1
        assert recipe.name == "カレーライス"
        assert recipe.servings == 4
        assert len(recipe.ingredients) == 4
        assert recipe.nutrition is not None
        assert recipe.nutrition.calories == 800

    def test_get_recipe_by_nonexistent_id(self, meal_plan_service, sample_recipes):
        """存在しないレシピIDの取得"""
        recipe = meal_plan_service.get_recipe_by_id(999)
        assert recipe is None

    def test_generate_shopping_list_single_recipe(
        self, meal_plan_service, sample_recipes
    ):
        """単一レシピの買い物リスト生成"""
        meal_plans = [
            {
                "date": "2025-12-15",
                "meal_type": "昼食",
                "recipe_id": 1,
                "recipe_name": "カレーライス",
                "servings": 4,
            }
        ]

        shopping_list = meal_plan_service.generate_shopping_list(
            meal_plans, date(2025, 12, 15), date(2025, 12, 15)
        )

        assert len(shopping_list) == 4
        ingredient_names = [item.ingredient for item in shopping_list]
        assert "玉ねぎ" in ingredient_names
        assert "じゃがいも" in ingredient_names
        assert "豚肉" in ingredient_names

    def test_generate_shopping_list_multiple_recipes(
        self, meal_plan_service, sample_recipes
    ):
        """複数レシピの買い物リスト生成（材料集約）"""
        meal_plans = [
            {
                "date": "2025-12-15",
                "meal_type": "昼食",
                "recipe_id": 1,
                "recipe_name": "カレーライス",
                "servings": 4,
            },
            {
                "date": "2025-12-16",
                "meal_type": "夕食",
                "recipe_id": 2,
                "recipe_name": "ハンバーグ",
                "servings": 2,
            },
        ]

        shopping_list = meal_plan_service.generate_shopping_list(
            meal_plans, date(2025, 12, 15), date(2025, 12, 16)
        )

        # 玉ねぎは2つのレシピで使用されるため集約される
        onion_item = next(
            (item for item in shopping_list if item.ingredient == "玉ねぎ"), None
        )
        assert onion_item is not None
        assert onion_item.total_quantity == 3.0  # カレー2個 + ハンバーグ1個
        assert len(onion_item.recipes) == 2

    def test_generate_shopping_list_with_servings_adjustment(
        self, meal_plan_service, sample_recipes
    ):
        """人数調整付き買い物リスト生成"""
        # カレーライスは4人分のレシピだが、2人分で作る
        meal_plans = [
            {
                "date": "2025-12-15",
                "meal_type": "昼食",
                "recipe_id": 1,
                "recipe_name": "カレーライス",
                "servings": 2,  # 2人分に調整
            }
        ]

        shopping_list = meal_plan_service.generate_shopping_list(
            meal_plans, date(2025, 12, 15), date(2025, 12, 15)
        )

        # 材料が半分になっているか確認
        onion_item = next(
            (item for item in shopping_list if item.ingredient == "玉ねぎ"), None
        )
        assert onion_item is not None
        assert onion_item.total_quantity == 1.0  # 2個 * (2/4) = 1個

    def test_generate_shopping_list_date_filter(
        self, meal_plan_service, sample_recipes
    ):
        """日付範囲フィルタ付き買い物リスト生成"""
        meal_plans = [
            {"date": "2025-12-14", "recipe_id": 1, "servings": 4},
            {"date": "2025-12-15", "recipe_id": 2, "servings": 2},
            {"date": "2025-12-16", "recipe_id": 3, "servings": 2},
            {"date": "2025-12-17", "recipe_id": 1, "servings": 4},
        ]

        shopping_list = meal_plan_service.generate_shopping_list(
            meal_plans, date(2025, 12, 15), date(2025, 12, 16)
        )

        # 12/15と12/16のレシピのみが含まれる
        all_ingredients = [item.ingredient for item in shopping_list]
        assert "牛ひき肉" in all_ingredients  # ハンバーグ（12/15）
        assert "レタス" in all_ingredients  # サラダ（12/16）

    def test_calculate_nutrition_balance(self, meal_plan_service, sample_recipes):
        """栄養バランス計算"""
        meal_plans = [
            {"date": "2025-12-15", "recipe_id": 1, "servings": 4},
            {"date": "2025-12-16", "recipe_id": 2, "servings": 2},
        ]

        nutrition = meal_plan_service.calculate_nutrition_balance(
            meal_plans, date(2025, 12, 15), date(2025, 12, 16)
        )

        assert nutrition.days_planned == 2
        assert nutrition.total_calories == 1400  # 800 + 600
        assert nutrition.avg_daily_calories == 700  # 1400 / 2
        assert nutrition.total_protein == 70  # 30 + 40
        assert nutrition.total_fat == 60  # 25 + 35
        assert nutrition.total_carbs == 120  # 100 + 20

    def test_calculate_nutrition_balance_with_servings_adjustment(
        self, meal_plan_service, sample_recipes
    ):
        """人数調整付き栄養バランス計算"""
        # カレーライスは4人分のレシピだが、2人分で作る
        meal_plans = [{"date": "2025-12-15", "recipe_id": 1, "servings": 2}]

        nutrition = meal_plan_service.calculate_nutrition_balance(
            meal_plans, date(2025, 12, 15), date(2025, 12, 15)
        )

        # 栄養素が半分になっているか確認
        assert nutrition.total_calories == 400  # 800 * (2/4)
        assert nutrition.total_protein == 15  # 30 * (2/4)

    def test_calculate_nutrition_balance_no_nutrition_data(
        self, meal_plan_service, temp_data_dir
    ):
        """栄養データなしのレシピの栄養計算"""
        # 栄養データなしのレシピを作成
        recipes = [
            {
                "id": 1,
                "name": "不明なレシピ",
                "servings": 2,
                "ingredients": [],
                "nutrition": None,
            }
        ]

        recipes_file = Path(temp_data_dir) / "recipes.json"
        recipes_file.write_text(json.dumps(recipes))

        meal_plans = [{"date": "2025-12-15", "recipe_id": 1, "servings": 2}]

        nutrition = meal_plan_service.calculate_nutrition_balance(
            meal_plans, date(2025, 12, 15), date(2025, 12, 15)
        )

        # 栄養データがないため全て0
        assert nutrition.total_calories == 0
        assert nutrition.total_protein == 0

    def test_get_weekly_summary(self, meal_plan_service, sample_recipes):
        """週間サマリーの取得"""
        # 2025年12月15日（月曜日）を含む週のデータを作成
        target_date = date(2025, 12, 15)

        meal_plans = []
        for i in range(7):
            plan_date = target_date + timedelta(days=i)
            meal_plans.append(
                {
                    "date": plan_date.isoformat(),
                    "recipe_id": (i % 3) + 1,  # レシピID: 1, 2, 3をローテーション
                    "servings": 2,
                }
            )

        summary = meal_plan_service.get_weekly_summary(meal_plans, target_date)

        assert summary["week_start"] == "2025-12-15"
        assert summary["week_end"] == "2025-12-21"
        assert "nutrition" in summary
        assert "shopping_list" in summary
        assert summary["total_meals"] == 7

    def test_suggest_meal_plan(self, meal_plan_service, sample_recipes):
        """献立計画の自動提案"""
        suggestions = meal_plan_service.suggest_meal_plan(days=3)

        # 3日 × 3食 = 9件の提案
        assert len(suggestions) == 9

        # 各提案に必要なフィールドが含まれているか確認
        for suggestion in suggestions:
            assert "date" in suggestion
            assert "meal_type" in suggestion
            assert "recipe_id" in suggestion
            assert "recipe_name" in suggestion

    def test_suggest_meal_plan_no_recipes(self, meal_plan_service):
        """レシピがない場合の献立提案"""
        suggestions = meal_plan_service.suggest_meal_plan(days=3)
        assert suggestions == []


class TestShoppingListItem:
    """ShoppingListItem モデルのテスト"""

    def test_shopping_list_item_creation(self):
        """買い物リストアイテムの作成"""
        item = ShoppingListItem(
            ingredient="玉ねぎ",
            total_quantity=3.0,
            unit="個",
            category="野菜",
            recipes=["カレーライス", "ハンバーグ"],
        )

        assert item.ingredient == "玉ねぎ"
        assert item.total_quantity == 3.0
        assert item.unit == "個"
        assert len(item.recipes) == 2


class TestWeeklyNutrition:
    """WeeklyNutrition モデルのテスト"""

    def test_weekly_nutrition_creation(self):
        """週間栄養サマリーの作成"""
        nutrition = WeeklyNutrition(
            total_calories=10000,
            avg_daily_calories=1428.57,
            total_protein=350,
            total_fat=280,
            total_carbs=1200,
            days_planned=7,
        )

        assert nutrition.total_calories == 10000
        assert nutrition.days_planned == 7


class TestMealPlanServiceEdgeCases:
    """エッジケースのテスト"""

    def test_empty_meal_plans(self, meal_plan_service, sample_recipes):
        """空の献立計画"""
        shopping_list = meal_plan_service.generate_shopping_list(
            [], date(2025, 12, 15), date(2025, 12, 16)
        )
        assert shopping_list == []

        nutrition = meal_plan_service.calculate_nutrition_balance(
            [], date(2025, 12, 15), date(2025, 12, 16)
        )
        assert nutrition.total_calories == 0
        assert nutrition.days_planned == 0

    def test_meal_plan_without_recipe_id(self, meal_plan_service, sample_recipes):
        """レシピIDなしの献立計画"""
        meal_plans = [
            {"date": "2025-12-15", "recipe_name": "不明なレシピ", "servings": 2}
        ]

        shopping_list = meal_plan_service.generate_shopping_list(
            meal_plans, date(2025, 12, 15), date(2025, 12, 15)
        )
        assert shopping_list == []

    def test_recipe_with_empty_ingredients(self, meal_plan_service, temp_data_dir):
        """材料なしのレシピ"""
        recipes = [
            {"id": 1, "name": "シンプルレシピ", "servings": 2, "ingredients": []}
        ]

        recipes_file = Path(temp_data_dir) / "recipes.json"
        recipes_file.write_text(json.dumps(recipes))

        meal_plans = [{"date": "2025-12-15", "recipe_id": 1, "servings": 2}]

        shopping_list = meal_plan_service.generate_shopping_list(
            meal_plans, date(2025, 12, 15), date(2025, 12, 15)
        )
        assert shopping_list == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

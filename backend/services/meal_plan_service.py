"""
献立計画サービス - 週間/月間献立作成、買い物リスト自動生成、栄養バランス計算
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from pydantic import BaseModel, Field
import json
from pathlib import Path


class NutritionInfo(BaseModel):
    """栄養情報"""

    calories: Optional[float] = None
    protein: Optional[float] = None  # タンパク質 (g)
    fat: Optional[float] = None  # 脂質 (g)
    carbs: Optional[float] = None  # 炭水化物 (g)
    fiber: Optional[float] = None  # 食物繊維 (g)
    salt: Optional[float] = None  # 塩分 (g)


class RecipeIngredient(BaseModel):
    """レシピの材料"""

    name: str
    quantity: float
    unit: str
    category: Optional[str] = None  # 野菜/肉/魚/調味料など


class RecipeDetail(BaseModel):
    """レシピ詳細情報"""

    id: int
    name: str
    ingredients: List[RecipeIngredient] = Field(default_factory=list)
    nutrition: Optional[NutritionInfo] = None
    servings: int = 1


class ShoppingListItem(BaseModel):
    """買い物リストアイテム"""

    ingredient: str
    total_quantity: float
    unit: str
    category: Optional[str] = None
    recipes: List[str] = Field(default_factory=list)


class WeeklyNutrition(BaseModel):
    """週間栄養バランスサマリー"""

    total_calories: float = 0
    avg_daily_calories: float = 0
    total_protein: float = 0
    total_fat: float = 0
    total_carbs: float = 0
    days_planned: int = 0


class MealPlanService:
    """献立計画サービス - 買い物リスト生成と栄養計算"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.recipes_file = self.data_dir / "recipes.json"

    def _load_recipes(self) -> List[Dict[str, Any]]:
        """レシピデータを読み込み"""
        if not self.recipes_file.exists():
            return []

        try:
            data = json.loads(self.recipes_file.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error loading recipes: {e}")
            return []

    def get_recipe_by_id(self, recipe_id: int) -> Optional[RecipeDetail]:
        """レシピIDからレシピ詳細を取得"""
        recipes = self._load_recipes()

        for recipe in recipes:
            if recipe.get("id") == recipe_id:
                # 材料データを正規化
                ingredients = []
                recipe_ingredients = recipe.get("ingredients", [])

                if isinstance(recipe_ingredients, list):
                    for ing in recipe_ingredients:
                        if isinstance(ing, dict):
                            ingredients.append(
                                RecipeIngredient(
                                    name=ing.get("name", ""),
                                    quantity=float(ing.get("quantity", 0)),
                                    unit=ing.get("unit", ""),
                                    category=ing.get("category"),
                                )
                            )

                # 栄養情報を正規化
                nutrition = None
                if "nutrition" in recipe and recipe["nutrition"]:
                    nutrition = NutritionInfo(**recipe["nutrition"])

                return RecipeDetail(
                    id=recipe.get("id", recipe_id),
                    name=recipe.get("name", "不明なレシピ"),
                    ingredients=ingredients,
                    nutrition=nutrition,
                    servings=recipe.get("servings", 1),
                )

        return None

    def generate_shopping_list(
        self, meal_plans: List[Dict[str, Any]], start_date: date, end_date: date
    ) -> List[ShoppingListItem]:
        """
        指定期間の献立計画から買い物リストを自動生成

        Args:
          meal_plans: 献立計画のリスト
          start_date: 開始日
          end_date: 終了日

        Returns:
          買い物リストアイテムのリスト
        """
        # 材料を集約
        ingredient_map: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"total_quantity": 0.0, "unit": "", "category": None, "recipes": []}
        )

        for plan in meal_plans:
            plan_date = date.fromisoformat(plan["date"])

            # 日付範囲チェック
            if not (start_date <= plan_date <= end_date):
                continue

            recipe_id = plan.get("recipe_id")
            if not recipe_id:
                continue

            recipe = self.get_recipe_by_id(recipe_id)
            if not recipe:
                continue

            # 人数による調整
            servings_multiplier = plan.get("servings", 1) / recipe.servings

            # 材料を集約
            for ingredient in recipe.ingredients:
                key = f"{ingredient.name}_{ingredient.unit}"

                ingredient_map[key]["total_quantity"] += (
                    ingredient.quantity * servings_multiplier
                )
                ingredient_map[key]["unit"] = ingredient.unit
                ingredient_map[key]["category"] = ingredient.category

                if recipe.name not in ingredient_map[key]["recipes"]:
                    ingredient_map[key]["recipes"].append(recipe.name)

        # ShoppingListItem に変換
        shopping_list = []
        for key, data in ingredient_map.items():
            ingredient_name = key.rsplit("_", 1)[0]

            shopping_list.append(
                ShoppingListItem(
                    ingredient=ingredient_name,
                    total_quantity=round(data["total_quantity"], 2),
                    unit=data["unit"],
                    category=data["category"],
                    recipes=data["recipes"],
                )
            )

        # カテゴリと名前でソート
        shopping_list.sort(
            key=lambda item: (item.category or "その他", item.ingredient)
        )

        return shopping_list

    def calculate_nutrition_balance(
        self, meal_plans: List[Dict[str, Any]], start_date: date, end_date: date
    ) -> WeeklyNutrition:
        """
        指定期間の栄養バランスを計算

        Args:
          meal_plans: 献立計画のリスト
          start_date: 開始日
          end_date: 終了日

        Returns:
          週間栄養サマリー
        """
        total_calories = 0.0
        total_protein = 0.0
        total_fat = 0.0
        total_carbs = 0.0
        planned_dates = set()

        for plan in meal_plans:
            plan_date = date.fromisoformat(plan["date"])

            # 日付範囲チェック
            if not (start_date <= plan_date <= end_date):
                continue

            planned_dates.add(plan_date)

            recipe_id = plan.get("recipe_id")
            if not recipe_id:
                continue

            recipe = self.get_recipe_by_id(recipe_id)
            if not recipe or not recipe.nutrition:
                continue

            # 人数による調整
            servings_multiplier = plan.get("servings", 1) / recipe.servings

            # 栄養素を集計
            if recipe.nutrition.calories:
                total_calories += recipe.nutrition.calories * servings_multiplier
            if recipe.nutrition.protein:
                total_protein += recipe.nutrition.protein * servings_multiplier
            if recipe.nutrition.fat:
                total_fat += recipe.nutrition.fat * servings_multiplier
            if recipe.nutrition.carbs:
                total_carbs += recipe.nutrition.carbs * servings_multiplier

        days_planned = len(planned_dates)
        avg_daily_calories = total_calories / days_planned if days_planned > 0 else 0

        return WeeklyNutrition(
            total_calories=round(total_calories, 2),
            avg_daily_calories=round(avg_daily_calories, 2),
            total_protein=round(total_protein, 2),
            total_fat=round(total_fat, 2),
            total_carbs=round(total_carbs, 2),
            days_planned=days_planned,
        )

    def suggest_meal_plan(
        self, days: int = 7, preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        献立計画を自動提案（シンプルなロジック）

        Args:
          days: 提案する日数
          preferences: ユーザーの好み（未実装）

        Returns:
          提案された献立計画のリスト
        """
        recipes = self._load_recipes()
        if not recipes:
            return []

        suggestions = []
        meal_types = ["朝食", "昼食", "夕食"]
        start_date = date.today()

        for day_offset in range(days):
            target_date = start_date + timedelta(days=day_offset)

            for meal_type in meal_types:
                # ランダムにレシピを選択（実際にはもっと賢いロジックが必要）
                import random

                recipe = random.choice(recipes)

                suggestions.append(
                    {
                        "date": target_date.isoformat(),
                        "meal_type": meal_type,
                        "recipe_id": recipe.get("id"),
                        "recipe_name": recipe.get("name", "不明"),
                        "servings": 2,
                        "notes": "自動提案",
                    }
                )

        return suggestions

    def get_weekly_summary(
        self, meal_plans: List[Dict[str, Any]], target_date: date
    ) -> Dict[str, Any]:
        """
        週間サマリーを取得（栄養バランス + 買い物リスト）

        Args:
          meal_plans: 献立計画のリスト
          target_date: 対象週を含む日付

        Returns:
          週間サマリー辞書
        """
        # 週の開始日（月曜日）を計算
        start_of_week = target_date - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # 栄養バランス計算
        nutrition = self.calculate_nutrition_balance(
            meal_plans, start_of_week, end_of_week
        )

        # 買い物リスト生成
        shopping_list = self.generate_shopping_list(
            meal_plans, start_of_week, end_of_week
        )

        return {
            "week_start": start_of_week.isoformat(),
            "week_end": end_of_week.isoformat(),
            "nutrition": nutrition.dict(),
            "shopping_list": [item.dict() for item in shopping_list],
            "total_meals": len(
                [
                    p
                    for p in meal_plans
                    if start_of_week <= date.fromisoformat(p["date"]) <= end_of_week
                ]
            ),
        }

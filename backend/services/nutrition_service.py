"""
栄養計算サービス

レシピから栄養価を計算し、分析する機能を提供
"""

import re
from typing import Dict, List, Any
from backend.data.nutrition_database import get_ingredient_nutrition, NUTRITION_DATA


class NutritionService:
    """栄養計算サービスクラス"""

    def __init__(self):
        """初期化"""
        pass

    def parse_amount(self, amount_str: str) -> float:
        """
        分量文字列を数値に変換

        Args:
          amount_str: 分量文字列（例: "200g", "2個", "大さじ1"）

        Returns:
          グラム換算した数値
        """
        if not amount_str:
            return 0.0

        # 数値部分を抽出
        numbers = re.findall(r"[\d.]+", str(amount_str))
        if not numbers:
            return 0.0

        base_amount = float(numbers[0])

        # 単位換算
        amount_lower = str(amount_str).lower()

        # グラム単位
        if "kg" in amount_lower:
            return base_amount * 1000
        elif "g" in amount_lower:
            return base_amount

        # ミリリットル（グラムと同等として扱う）
        elif "l" in amount_lower and "ml" not in amount_lower:
            return base_amount * 1000
        elif "ml" in amount_lower or "cc" in amount_lower:
            return base_amount

        # 大さじ・小さじ
        elif "大さじ" in amount_lower or "tbsp" in amount_lower:
            return base_amount * 15
        elif "小さじ" in amount_lower or "tsp" in amount_lower:
            return base_amount * 5

        # カップ
        elif "カップ" in amount_lower or "cup" in amount_lower:
            return base_amount * 200

        # 個数（平均的な重量で換算）
        elif "個" in amount_lower or "枚" in amount_lower:
            # 卵1個 = 50g、玉ねぎ1個 = 200g など
            # ここでは汎用的に100gとする
            return base_amount * 100

        # 単位がない場合はそのまま
        return base_amount

    def calculate_ingredient_nutrition(
        self, ingredient_name: str, amount: str
    ) -> Dict[str, Any]:
        """
        1つの材料の栄養価を計算

        Args:
          ingredient_name: 材料名
          amount: 分量

        Returns:
          栄養価の辞書
        """
        # 栄養データを取得
        nutrition_data = get_ingredient_nutrition(ingredient_name)

        if not nutrition_data:
            return {
                "ingredient": ingredient_name,
                "amount": amount,
                "found": False,
                "calories": 0,
                "protein": 0,
                "fat": 0,
                "carbohydrates": 0,
                "fiber": 0,
            }

        # 分量をグラムに変換
        amount_g = self.parse_amount(amount)

        # 100gあたりの栄養素を実際の分量に換算
        multiplier = amount_g / 100.0

        return {
            "ingredient": ingredient_name,
            "amount": amount,
            "amount_g": round(amount_g, 1),
            "found": True,
            "calories": round(nutrition_data["calories"] * multiplier, 1),
            "protein": round(nutrition_data["protein"] * multiplier, 1),
            "fat": round(nutrition_data["fat"] * multiplier, 1),
            "carbohydrates": round(nutrition_data["carbs"] * multiplier, 1),
            "fiber": round(nutrition_data["fiber"] * multiplier, 1),
        }

    def calculate_recipe_nutrition(
        self, ingredients: List[Dict[str, str]], servings: int = 1
    ) -> Dict[str, Any]:
        """
        レシピ全体の栄養価を計算

        Args:
          ingredients: 材料リスト [{"name": "鶏肉", "amount": "200g"}, ...]
          servings: 何人前か（デフォルト1）

        Returns:
          栄養価の辞書
        """
        ingredients_breakdown = []
        total_nutrition = {
            "calories": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0,
            "fiber": 0.0,
        }

        # 各材料の栄養価を計算
        for ingredient in ingredients:
            name = ingredient.get("name", "")
            amount = ingredient.get("amount", "")

            nutrition = self.calculate_ingredient_nutrition(name, amount)
            ingredients_breakdown.append(nutrition)

            # 合計に加算
            if nutrition["found"]:
                total_nutrition["calories"] += nutrition["calories"]
                total_nutrition["protein"] += nutrition["protein"]
                total_nutrition["fat"] += nutrition["fat"]
                total_nutrition["carbohydrates"] += nutrition["carbohydrates"]
                total_nutrition["fiber"] += nutrition["fiber"]

        # 1人前あたりの栄養価を計算
        per_serving = {
            "calories": round(total_nutrition["calories"] / servings, 1),
            "protein": round(total_nutrition["protein"] / servings, 1),
            "fat": round(total_nutrition["fat"] / servings, 1),
            "carbohydrates": round(total_nutrition["carbohydrates"] / servings, 1),
            "fiber": round(total_nutrition["fiber"] / servings, 1),
        }

        # 合計を四捨五入
        total_nutrition = {
            key: round(value, 1) for key, value in total_nutrition.items()
        }

        return {
            "servings": servings,
            "per_serving": per_serving,
            "total": total_nutrition,
            "ingredients_breakdown": ingredients_breakdown,
            "found_ingredients": sum(
                1 for item in ingredients_breakdown if item["found"]
            ),
            "total_ingredients": len(ingredients),
        }

    def get_nutrition_summary(self, nutrition_data: Dict[str, Any]) -> Dict[str, str]:
        """
        栄養価のサマリーを生成

        Args:
          nutrition_data: calculate_recipe_nutritionの結果

        Returns:
          サマリー情報
        """
        per_serving = nutrition_data.get("per_serving", {})
        nutrition_data.get("total", {})

        # PFCバランス計算
        protein_cal = per_serving.get("protein", 0) * 4  # タンパク質 1g = 4kcal
        fat_cal = per_serving.get("fat", 0) * 9  # 脂質 1g = 9kcal
        carb_cal = per_serving.get("carbohydrates", 0) * 4  # 炭水化物 1g = 4kcal

        total_cal = protein_cal + fat_cal + carb_cal
        if total_cal > 0:
            protein_ratio = round((protein_cal / total_cal) * 100, 1)
            fat_ratio = round((fat_cal / total_cal) * 100, 1)
            carb_ratio = round((carb_cal / total_cal) * 100, 1)
        else:
            protein_ratio = fat_ratio = carb_ratio = 0.0

        # カロリーレベル判定
        calories = per_serving.get("calories", 0)
        if calories < 300:
            calorie_level = "低カロリー"
        elif calories < 600:
            calorie_level = "中カロリー"
        else:
            calorie_level = "高カロリー"

        return {
            "calorie_level": calorie_level,
            "pfc_balance": f"P:{protein_ratio}% F:{fat_ratio}% C:{carb_ratio}%",
            "protein_ratio": protein_ratio,
            "fat_ratio": fat_ratio,
            "carb_ratio": carb_ratio,
        }

    def search_ingredients(self, query: str) -> List[Dict[str, Any]]:
        """
        材料を検索

        Args:
          query: 検索クエリ

        Returns:
          マッチした材料のリスト
        """
        query_lower = query.lower()
        results = []

        for name, data in NUTRITION_DATA.items():
            if query_lower in name.lower():
                results.append(
                    {
                        "name": name,
                        "calories": data["calories"],
                        "protein": data["protein"],
                        "fat": data["fat"],
                        "carbohydrates": data["carbs"],
                        "fiber": data["fiber"],
                        "unit": data["unit"],
                    }
                )

        return results

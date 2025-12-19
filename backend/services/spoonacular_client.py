"""
Spoonacular API Client - 海外レシピ取得サービス
"""

import os
import logging
import random
from typing import Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


def should_retry_http_error(exception):
    """HTTPエラーのリトライ判定（429と5xxエラーのみ）"""
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code == 429 or exception.response.status_code >= 500
    return False


class SpoonacularClient:
    """Spoonacular APIクライアント"""

    BASE_URL = "https://api.spoonacular.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SPOONACULAR_API_KEY")
        if not self.api_key:
            raise ValueError("SPOONACULAR_API_KEY is required")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(httpx.HTTPStatusError) & retry(should_retry_http_error),
        reraise=True,
    )
    def _request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """API リクエストを送信"""
        params = params or {}
        params["apiKey"] = self.api_key

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(f"{self.BASE_URL}{endpoint}", params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Spoonacular API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Spoonacular request error: {e}")
            raise

    def get_random_recipes(self, number: int = 5, tags: Optional[str] = None) -> list[dict]:
        """ランダムなレシピを取得

        Args:
            number: 取得するレシピ数（最大100）
            tags: カンマ区切りのタグ（例: "vegetarian,dessert"）
        """
        params = {"number": min(number, 100)}
        if tags:
            params["tags"] = tags

        result = self._request("/recipes/random", params)
        return result.get("recipes", [])

    def get_recipe_information(self, recipe_id: int) -> dict:
        """レシピの詳細情報を取得"""
        return self._request(f"/recipes/{recipe_id}/information")

    def search_recipes(
        self,
        query: str,
        number: int = 10,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        type_: Optional[str] = None,
    ) -> list[dict]:
        """レシピを検索

        Args:
            query: 検索クエリ
            number: 取得数
            cuisine: 料理ジャンル（例: "italian", "japanese"）
            diet: 食事制限（例: "vegetarian", "vegan"）
            type_: 料理タイプ（例: "main course", "dessert"）
        """
        params = {
            "query": query,
            "number": min(number, 100),
            "addRecipeInformation": True,
        }
        if cuisine:
            params["cuisine"] = cuisine
        if diet:
            params["diet"] = diet
        if type_:
            params["type"] = type_

        result = self._request("/recipes/complexSearch", params)
        return result.get("results", [])

    def get_recipe_by_ingredients(
        self,
        ingredients: list[str],
        number: int = 5,
    ) -> list[dict]:
        """材料からレシピを検索"""
        params = {
            "ingredients": ",".join(ingredients),
            "number": min(number, 100),
            "ranking": 1,  # 最大化: 使用材料数
        }
        return self._request("/recipes/findByIngredients", params)

    def extract_recipe_data(self, raw_recipe: dict) -> dict:
        """Spoonacular形式のレシピデータを正規化用の形式に変換"""
        # 材料を抽出
        ingredients = []
        for ing in raw_recipe.get("extendedIngredients", []):
            ingredients.append({
                "name": ing.get("name", ""),
                "original_text": ing.get("original", ""),
                "amount": ing.get("amount"),
                "unit": ing.get("unit", ""),
                "measures": {
                    "us": ing.get("measures", {}).get("us", {}),
                    "metric": ing.get("measures", {}).get("metric", {}),
                },
            })

        # 手順を抽出
        steps = []
        for instruction in raw_recipe.get("analyzedInstructions", []):
            for step in instruction.get("steps", []):
                steps.append({
                    "number": step.get("number", len(steps) + 1),
                    "description": step.get("step", ""),
                    "equipment": [e.get("name") for e in step.get("equipment", [])],
                    "ingredients_used": [i.get("name") for i in step.get("ingredients", [])],
                })

        # 手順がanalyzedInstructionsにない場合はinstructionsから取得
        if not steps and raw_recipe.get("instructions"):
            # HTMLタグを除去して分割
            instructions_text = raw_recipe["instructions"]
            # <li>や<p>タグで分割
            import re
            clean_text = re.sub(r"<[^>]+>", "\n", instructions_text)
            step_texts = [s.strip() for s in clean_text.split("\n") if s.strip()]
            for i, text in enumerate(step_texts, 1):
                steps.append({
                    "number": i,
                    "description": text,
                    "equipment": [],
                    "ingredients_used": [],
                })

        return {
            "source_id": raw_recipe.get("id"),
            "source_type": "spoonacular",
            "source_url": raw_recipe.get("sourceUrl", ""),
            "original_data": {
                "title": raw_recipe.get("title", ""),
                "summary": raw_recipe.get("summary", ""),
                "servings": raw_recipe.get("servings"),
                "ready_in_minutes": raw_recipe.get("readyInMinutes"),
                "prep_time_minutes": raw_recipe.get("preparationMinutes"),
                "cook_time_minutes": raw_recipe.get("cookingMinutes"),
                "image": raw_recipe.get("image", ""),
                "image_type": raw_recipe.get("imageType", ""),
                "cuisines": raw_recipe.get("cuisines", []),
                "dish_types": raw_recipe.get("dishTypes", []),
                "diets": raw_recipe.get("diets", []),
            },
            "ingredients": ingredients,
            "steps": steps,
            "nutrition": raw_recipe.get("nutrition", {}),
        }

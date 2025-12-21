"""
栄養計算API ルーター

レシピの栄養価計算・材料の栄養情報取得を提供
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.core.cache import get_cache
from backend.core.database import get_session
from backend.services.nutrition_service import NutritionService
from backend.services.recipe_service import RecipeService
from backend.data.nutrition_database import (
    get_ingredient_nutrition,
    list_all_ingredients,
)
from config.cache_config import CacheConfig


# Pydantic モデル定義
class IngredientInput(BaseModel):
    """材料入力モデル"""

    name: str = Field(..., description="材料名", example="鶏もも肉")
    amount: str = Field(..., description="分量", example="200g")


class NutritionCalculateRequest(BaseModel):
    """栄養計算リクエストモデル"""

    ingredients: List[IngredientInput] = Field(..., description="材料リスト")
    servings: int = Field(default=1, ge=1, description="人数", example=2)


class NutritionResponse(BaseModel):
    """栄養計算レスポンスモデル"""

    status: str = "ok"
    data: Dict[str, Any]
    error: None = None


class IngredientNutritionResponse(BaseModel):
    """材料栄養情報レスポンスモデル"""

    status: str = "ok"
    data: Dict[str, Any] | None
    error: None = None


class IngredientsListResponse(BaseModel):
    """材料リストレスポンスモデル"""

    status: str = "ok"
    data: List[str]
    error: None = None


# ルーター初期化
router = APIRouter(prefix="/api/v1/nutrition", tags=["nutrition"])

# サービス初期化
nutrition_service = NutritionService()


def _format_amount(amount: Optional[float], unit: Optional[str]) -> str:
    if amount is None:
        return ""
    if unit:
        return f"{amount}{unit}"
    return str(amount)


def _recipe_nutrition_cache_key(recipe_id: int) -> str:
    return f"{CacheConfig.PREFIX_NUTRITION}:recipe:{recipe_id}"


@router.post("/calculate", response_model=NutritionResponse)
async def calculate_nutrition(request: NutritionCalculateRequest):
    """
    材料リストから栄養価を計算

    Args:
      request: 材料リストと人数

    Returns:
      栄養計算結果
    """
    try:
        # Pydantic モデルを辞書に変換
        ingredients_list = [
            {"name": ing.name, "amount": ing.amount} for ing in request.ingredients
        ]

        # 栄養計算
        result = nutrition_service.calculate_recipe_nutrition(
            ingredients_list, request.servings
        )

        # サマリー追加
        summary = nutrition_service.get_nutrition_summary(result)
        result["summary"] = summary

        return NutritionResponse(status="ok", data=result, error=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"栄養計算エラー: {str(e)}")


@router.get("/ingredient/{name}", response_model=IngredientNutritionResponse)
async def get_ingredient_info(name: str):
    """
    材料の栄養情報を取得

    Args:
      name: 材料名

    Returns:
      材料の栄養情報（100gあたり）
    """
    try:
        nutrition_data = get_ingredient_nutrition(name)

        if not nutrition_data:
            return IngredientNutritionResponse(
                status="ok",
                data=None,
                error=None,
            )

        # レスポンス用に整形
        response_data = {
            "name": name,
            "calories": nutrition_data["calories"],
            "protein": nutrition_data["protein"],
            "fat": nutrition_data["fat"],
            "carbohydrates": nutrition_data["carbs"],
            "fiber": nutrition_data["fiber"],
            "unit": nutrition_data["unit"],
        }

        return IngredientNutritionResponse(status="ok", data=response_data, error=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"材料情報取得エラー: {str(e)}")


@router.get("/ingredients", response_model=IngredientsListResponse)
async def list_ingredients():
    """
    登録されている全材料名を取得

    Returns:
      材料名のリスト
    """
    try:
        ingredients = list_all_ingredients()
        return IngredientsListResponse(status="ok", data=ingredients, error=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"材料リスト取得エラー: {str(e)}")


@router.get("/search")
async def search_ingredients(
    q: str = Query(..., description="検索クエリ", min_length=1),
):
    """
    材料を検索

    Args:
      q: 検索クエリ

    Returns:
      マッチした材料のリスト
    """
    try:
        results = nutrition_service.search_ingredients(q)

        return {
            "status": "ok",
            "data": {
                "query": q,
                "results": results,
                "count": len(results),
            },
            "error": None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"材料検索エラー: {str(e)}")


@router.get("/recipe/{recipe_id}")
async def get_recipe_nutrition(
    recipe_id: int,
    session=Depends(get_session),
):
    """
    レシピIDから栄養価を取得

    Args:
      recipe_id: レシピID

    Returns:
      レシピの栄養情報

    Note:
      この機能は Recipe サービスとの統合が必要です
      現在はプレースホルダー実装
    """
    cache = get_cache()
    cache_key = _recipe_nutrition_cache_key(recipe_id)
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        return cached_response

    recipe_service = RecipeService(session)
    recipe = recipe_service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    ingredients_list = []
    for ing in recipe.ingredients:
        ingredients_list.append(
            {"name": ing.name, "amount": _format_amount(ing.amount, ing.unit)}
        )

    servings = recipe.servings or 1
    result = nutrition_service.calculate_recipe_nutrition(
        ingredients_list, servings
    )
    result["summary"] = nutrition_service.get_nutrition_summary(result)
    response_payload = {
        "status": "ok",
        "data": {
            "recipe_id": recipe.id,
            "title": recipe.title,
            "servings": servings,
            "nutrition": result,
        },
        "error": None,
    }

    cache.set(cache_key, response_payload, CacheConfig.TTL_NUTRITION)
    return response_payload

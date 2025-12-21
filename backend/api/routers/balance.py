"""
食事バランス評価 API ルーター

PFCバランス、栄養バランス評価、スコア算出エンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Any, Optional
from datetime import date

from backend.services.balance_service import BalanceService


router = APIRouter(prefix="/api/v1/balance", tags=["balance"])


# Request Models
class NutritionInput(BaseModel):
    """栄養素データ入力モデル"""

    calories: float = Field(ge=0, description="カロリー (kcal)")
    protein: float = Field(ge=0, description="タンパク質 (g)")
    fat: float = Field(ge=0, description="脂質 (g)")
    carbs: float = Field(ge=0, description="炭水化物 (g)")
    fiber: float = Field(default=0, ge=0, description="食物繊維 (g)")
    salt: float = Field(default=0, ge=0, description="塩分 (g)")


class DailyBalanceRequest(BaseModel):
    """1日の食事バランス評価リクエスト"""

    meals: List[NutritionInput] = Field(description="1日の食事データリスト")
    target_date: Optional[str] = Field(
        default=None, description="対象日付 (YYYY-MM-DD)"
    )


class BalanceScoreRequest(BaseModel):
    """バランススコア計算リクエスト"""

    nutrition: NutritionInput = Field(description="栄養素データ")


# Response Models
class APIResponse(BaseModel):
    """標準APIレスポンス"""

    status: str = Field(default="ok", description="ステータス")
    data: Optional[Any] = Field(default=None, description="レスポンスデータ")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")


# Endpoints
# NOTE: 静的パスは動的パス（/{recipe_id}）より先に定義する必要がある


@router.get("/reference", response_model=APIResponse)
async def get_daily_reference():
    """
    日本人の食事摂取基準データ取得

    Returns:
      食事摂取基準とPFC理想比率
    """
    try:
        from backend.services.balance_service import DAILY_REFERENCE, PFC_IDEAL_RATIO

        return APIResponse(
            status="ok",
            data={
                "daily_reference": DAILY_REFERENCE,
                "pfc_ideal_ratio": PFC_IDEAL_RATIO,
                "description": "日本人の食事摂取基準（成人平均）",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"基準値取得エラー: {str(e)}",
        )


@router.get("/{recipe_id}", response_model=APIResponse)
async def get_recipe_balance(recipe_id: int):
    """
    レシピのバランス評価取得

    Args:
      recipe_id: レシピID

    Returns:
      レシピのバランス評価データ
    """
    try:
        from backend.core.database import get_session
        from backend.models import Recipe

        # Get recipe from database
        db = next(get_session())
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {recipe_id} not found"
            )

        # Calculate nutrition based on ingredients
        # Note: This is a simplified calculation
        # In production, use nutrition database for accurate values
        ingredient_count = len(recipe.ingredients) if recipe.ingredients else 0

        # Mock calculation based on ingredient count
        mock_nutrition = {
            "calories": ingredient_count * 100,
            "protein": ingredient_count * 5,
            "fat": ingredient_count * 3,
            "carbs": ingredient_count * 15,
            "fiber": ingredient_count * 2,
            "salt": ingredient_count * 0.5,
        }

        evaluation = BalanceService.get_recipe_balance_evaluation(mock_nutrition)

        return APIResponse(
            status="ok", data={"recipe_id": recipe_id, "evaluation": evaluation}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"バランス評価取得エラー: {str(e)}",
        )


@router.post("/daily", response_model=APIResponse)
async def evaluate_daily_balance(request: DailyBalanceRequest):
    """
    1日の食事バランス評価

    Args:
      request: 1日の食事データ

    Returns:
      1日のバランス評価データ
    """
    try:
        if not request.meals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="食事データが空です"
            )

        # NutritionInput を dict に変換
        meals_data = [meal.dict() for meal in request.meals]

        evaluation = BalanceService.evaluate_daily_balance(meals_data)

        return APIResponse(
            status="ok",
            data={
                "target_date": request.target_date or str(date.today()),
                "meal_count": len(request.meals),
                "evaluation": evaluation,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"1日のバランス評価エラー: {str(e)}",
        )


@router.get("/pfc/{recipe_id}", response_model=APIResponse)
async def get_pfc_balance(recipe_id: int):
    """
    PFCバランス取得

    Args:
      recipe_id: レシピID

    Returns:
      PFCバランスデータ
    """
    try:
        from backend.core.database import get_session
        from backend.models import Recipe

        # Get recipe from database
        db = next(get_session())
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {recipe_id} not found"
            )

        # Calculate nutrition based on ingredients (simplified)
        ingredient_count = len(recipe.ingredients) if recipe.ingredients else 0

        mock_nutrition = {
            "calories": ingredient_count * 100,
            "protein": ingredient_count * 5,
            "fat": ingredient_count * 3,
            "carbs": ingredient_count * 15,
            "fiber": ingredient_count * 2,
            "salt": ingredient_count * 0.5,
        }

        pfc_balance = BalanceService.calculate_pfc_balance(mock_nutrition)

        return APIResponse(
            status="ok", data={"recipe_id": recipe_id, "pfc_balance": pfc_balance}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PFCバランス取得エラー: {str(e)}",
        )


@router.post("/score", response_model=APIResponse)
async def calculate_balance_score(request: BalanceScoreRequest):
    """
    バランススコア計算

    Args:
      request: 栄養素データ

    Returns:
      バランススコア詳細
    """
    try:
        nutrition_data = request.nutrition.dict()

        score = BalanceService.calculate_nutrition_score(nutrition_data)

        return APIResponse(
            status="ok", data={"nutrition": nutrition_data, "score": score}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"スコア計算エラー: {str(e)}",
        )


@router.post("/compare", response_model=APIResponse)
async def compare_recipes(nutrition_list: List[NutritionInput]):
    """
    複数レシピのバランス比較

    Args:
      nutrition_list: 比較する栄養素データのリスト

    Returns:
      比較データ
    """
    try:
        if not nutrition_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="比較データが空です"
            )

        comparisons = []
        for idx, nutrition in enumerate(nutrition_list):
            nutrition_data = nutrition.dict()
            score = BalanceService.calculate_nutrition_score(nutrition_data)
            pfc_balance = BalanceService.calculate_pfc_balance(nutrition_data)

            comparisons.append(
                {
                    "index": idx,
                    "nutrition": nutrition_data,
                    "overall_score": score["overall_score"],
                    "pfc_score": pfc_balance["balance_score"],
                    "evaluation": score["evaluation"],
                }
            )

        # スコア順にソート
        comparisons.sort(key=lambda x: x["overall_score"], reverse=True)

        return APIResponse(
            status="ok",
            data={
                "count": len(comparisons),
                "comparisons": comparisons,
                "best_index": comparisons[0]["index"] if comparisons else None,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"レシピ比較エラー: {str(e)}",
        )

"""
レシピ推薦 API ルーター

材料ベースのレシピ推薦エンドポイントを提供する。
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
from backend.services.recommendation_service import (
    RecommendationService,
    RecommendationResult,
)


# リクエスト/レスポンスモデル
class IngredientRequest(BaseModel):
    """材料指定リクエスト"""

    ingredients: List[str] = Field(
        ...,
        description="材料リスト",
        min_items=1,
        example=["たまねぎ", "にんじん", "じゃがいも", "肉"],
    )
    min_score: Optional[float] = Field(
        0.5, ge=0.0, le=1.0, description="最小マッチスコア"
    )
    max_results: Optional[int] = Field(10, ge=1, le=50, description="最大結果数")


class WhatCanIMakeRequest(BaseModel):
    """手持ち材料リクエスト"""

    ingredients: List[str] = Field(
        ...,
        description="手持ち材料リスト",
        min_items=1,
        example=["たまねぎ", "にんじん", "じゃがいも"],
    )
    allow_missing: Optional[int] = Field(
        2, ge=0, le=10, description="許容する不足材料数"
    )


class RecommendationItem(BaseModel):
    """推薦アイテム"""

    recipe: dict = Field(..., description="レシピデータ")
    match_score: float = Field(..., description="マッチスコア (0.0〜1.0)")
    matched_ingredients: List[str] = Field(..., description="一致した材料")
    missing_ingredients: List[str] = Field(..., description="不足している材料")
    match_percentage: float = Field(..., description="一致率 (%)")


class RecommendationResponse(BaseModel):
    """推薦レスポンス"""

    status: str = "ok"
    data: dict
    error: Optional[str] = None


# ルーター作成
router = APIRouter(prefix="/api/v1/recommend", tags=["recommendation"])


# モックレシピデータ（実際にはDBから取得）
MOCK_RECIPES = [
    {
        "id": "recipe_001",
        "name": "カレーライス",
        "ingredients": [
            {"name": "たまねぎ", "amount": "2個"},
            {"name": "にんじん", "amount": "1本"},
            {"name": "じゃがいも", "amount": "3個"},
            {"name": "豚肉", "amount": "300g"},
            {"name": "カレールー", "amount": "1箱"},
            {"name": "サラダ油", "amount": "大さじ1"},
        ],
        "steps": ["材料を切る", "炒める", "煮込む", "ルーを入れる"],
        "tags": ["洋食", "定番"],
    },
    {
        "id": "recipe_002",
        "name": "肉じゃが",
        "ingredients": [
            {"name": "じゃがいも", "amount": "4個"},
            {"name": "たまねぎ", "amount": "1個"},
            {"name": "にんじん", "amount": "1本"},
            {"name": "牛肉", "amount": "200g"},
            {"name": "醤油", "amount": "大さじ3"},
            {"name": "砂糖", "amount": "大さじ2"},
            {"name": "みりん", "amount": "大さじ2"},
        ],
        "steps": ["材料を切る", "炒める", "調味料を加える", "煮る"],
        "tags": ["和食", "定番"],
    },
    {
        "id": "recipe_003",
        "name": "野菜炒め",
        "ingredients": [
            {"name": "キャベツ", "amount": "1/4個"},
            {"name": "にんじん", "amount": "1/2本"},
            {"name": "豚肉", "amount": "150g"},
            {"name": "塩", "amount": "少々"},
            {"name": "こしょう", "amount": "少々"},
            {"name": "ごま油", "amount": "大さじ1"},
        ],
        "steps": ["材料を切る", "炒める", "調味料で味付け"],
        "tags": ["中華", "簡単"],
    },
    {
        "id": "recipe_004",
        "name": "ポテトサラダ",
        "ingredients": [
            {"name": "じゃがいも", "amount": "3個"},
            {"name": "きゅうり", "amount": "1本"},
            {"name": "にんじん", "amount": "1/2本"},
            {"name": "ハム", "amount": "4枚"},
            {"name": "マヨネーズ", "amount": "大さじ4"},
            {"name": "塩", "amount": "少々"},
            {"name": "こしょう", "amount": "少々"},
        ],
        "steps": ["じゃがいもを茹でる", "野菜を切る", "混ぜる", "調味料で味付け"],
        "tags": ["洋食", "サラダ"],
    },
    {
        "id": "recipe_005",
        "name": "オニオンスープ",
        "ingredients": [
            {"name": "たまねぎ", "amount": "3個"},
            {"name": "バター", "amount": "30g"},
            {"name": "コンソメ", "amount": "2個"},
            {"name": "塩", "amount": "少々"},
            {"name": "こしょう", "amount": "少々"},
        ],
        "steps": [
            "たまねぎを薄切り",
            "バターで炒める",
            "水とコンソメを加える",
            "煮込む",
        ],
        "tags": ["洋食", "スープ"],
    },
]


def _convert_to_response_item(result: RecommendationResult) -> dict:
    """RecommendationResultをレスポンス形式に変換"""
    return {
        "recipe": result.recipe,
        "match_score": result.match_score,
        "matched_ingredients": result.matched_ingredients,
        "missing_ingredients": result.missing_ingredients,
        "match_percentage": result.match_percentage,
    }


@router.post(
    "/by-ingredients",
    response_model=RecommendationResponse,
    summary="材料からレシピ推薦",
    description="指定した材料から作れるレシピを推薦します",
)
async def recommend_by_ingredients(request: IngredientRequest) -> dict:
    """
    材料からレシピを推薦

    Args:
      request: 材料指定リクエスト

    Returns:
      推薦結果
    """
    try:
        # サービス初期化
        service = RecommendationService(recipes=MOCK_RECIPES)

        # 推薦実行
        results = service.recommend_by_ingredients(
            available_ingredients=request.ingredients,
            min_score=request.min_score,
            max_results=request.max_results,
        )

        # レスポンス作成
        recommendations = [_convert_to_response_item(r) for r in results]

        return {
            "status": "ok",
            "data": {
                "recommendations": recommendations,
                "total": len(recommendations),
                "query_ingredients": request.ingredients,
            },
            "error": None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"推薦処理でエラーが発生しました: {str(e)}"
        )


@router.get(
    "/similar/{recipe_id}",
    response_model=RecommendationResponse,
    summary="類似レシピ推薦",
    description="指定したレシピに類似するレシピを推薦します",
)
async def recommend_similar(
    recipe_id: str = Path(..., description="レシピID"),
    max_results: int = Query(5, ge=1, le=20, description="最大結果数"),
) -> dict:
    """
    類似レシピを推薦

    Args:
      recipe_id: レシピID
      max_results: 最大結果数

    Returns:
      推薦結果
    """
    try:
        # サービス初期化
        service = RecommendationService(recipes=MOCK_RECIPES)

        # 推薦実行
        results = service.recommend_similar(
            target_recipe_id=recipe_id, max_results=max_results
        )

        if not results:
            # レシピが見つからない場合
            return {
                "status": "ok",
                "data": {
                    "recommendations": [],
                    "total": 0,
                    "message": f"レシピID '{recipe_id}' が見つかりません",
                },
                "error": None,
            }

        # レスポンス作成
        recommendations = [_convert_to_response_item(r) for r in results]

        return {
            "status": "ok",
            "data": {
                "recommendations": recommendations,
                "total": len(recommendations),
                "target_recipe_id": recipe_id,
            },
            "error": None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"推薦処理でエラーが発生しました: {str(e)}"
        )


@router.post(
    "/what-can-i-make",
    response_model=RecommendationResponse,
    summary="手持ち材料で作れるレシピ検索",
    description="手持ちの材料で作れるレシピを検索します（不足材料も表示）",
)
async def what_can_i_make(request: WhatCanIMakeRequest) -> dict:
    """
    手持ち材料で作れるレシピを検索

    Args:
      request: 手持ち材料リクエスト

    Returns:
      推薦結果
    """
    try:
        # サービス初期化
        service = RecommendationService(recipes=MOCK_RECIPES)

        # 推薦実行
        results = service.what_can_i_make(
            available_ingredients=request.ingredients,
            allow_missing=request.allow_missing,
        )

        # レスポンス作成
        recommendations = [_convert_to_response_item(r) for r in results]

        return {
            "status": "ok",
            "data": {
                "recommendations": recommendations,
                "total": len(recommendations),
                "query_ingredients": request.ingredients,
                "allow_missing": request.allow_missing,
            },
            "error": None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"推薦処理でエラーが発生しました: {str(e)}"
        )

"""
レシピ推薦AI APIルーター
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.recommendation_ai_service import RecommendationAIService

router = APIRouter(prefix="/api/v1/ai", tags=["AI Recommendation"])

# サービスインスタンス
recommendation_service = RecommendationAIService(data_dir="data")


# === Pydantic Models ===


class RecommendationRequest(BaseModel):
    """推薦リクエスト"""

    user_id: str = Field(..., description="ユーザーID")
    limit: int = Field(10, ge=1, le=50, description="取得件数")


class SimilarRecipeRequest(BaseModel):
    """類似レシピリクエスト"""

    limit: int = Field(5, ge=1, le=20, description="取得件数")


class FeedbackRequest(BaseModel):
    """フィードバックリクエスト"""

    user_id: str = Field(..., description="ユーザーID")
    recipe_id: str = Field(..., description="レシピID")
    feedback_type: str = Field(
        ...,
        description="フィードバックタイプ: interested, not_interested, favorited, cooked",
    )
    metadata: Optional[dict] = Field(None, description="追加メタデータ")


class ActivityRequest(BaseModel):
    """行動記録リクエスト"""

    user_id: str = Field(..., description="ユーザーID")
    recipe_id: str = Field(..., description="レシピID")
    activity_type: str = Field(
        ...,
        description="行動タイプ: viewed, cooked, rated, favorited, dismissed",
    )
    metadata: Optional[dict] = Field(None, description="追加メタデータ")


class RecommendationResponse(BaseModel):
    """推薦レスポンス"""

    recipe: dict
    score: float
    reason: str
    match_percentage: int


class SimilarRecipeResponse(BaseModel):
    """類似レシピレスポンス"""

    recipe: dict
    similarity: float
    match_percentage: int


class PreferencesResponse(BaseModel):
    """ユーザー嗜好レスポンス"""

    user_id: str
    total_activities: int
    favorite_ingredients: List[dict]
    favorite_categories: List[dict]
    favorite_tags: List[dict]
    cooking_frequency: int
    average_cooking_time: int
    preferred_difficulty: str


class StandardResponse(BaseModel):
    """標準レスポンス"""

    status: str
    data: Optional[dict] = None
    error: Optional[str] = None


# === Endpoints ===


@router.get(
    "/recommend",
    response_model=StandardResponse,
    summary="パーソナライズ推薦",
    description="ユーザーの行動履歴に基づいたパーソナライズ推薦を取得",
)
async def get_personalized_recommendations(
    user_id: str = Query(..., description="ユーザーID"),
    limit: int = Query(10, ge=1, le=50, description="取得件数"),
):
    """パーソナライズ推薦を取得"""
    try:
        # ダミーレシピデータ（実際はDBから取得）
        recipes = _get_dummy_recipes()

        recommendations = recommendation_service.get_personalized_recommendations(
            user_id=user_id, recipes=recipes, limit=limit
        )

        return StandardResponse(
            status="ok",
            data={
                "user_id": user_id,
                "recommendations": recommendations,
                "total": len(recommendations),
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推薦生成エラー: {str(e)}")


@router.get(
    "/recommend/similar/{recipe_id}",
    response_model=StandardResponse,
    summary="類似レシピ取得",
    description="指定レシピに類似したレシピを取得",
)
async def get_similar_recipes(
    recipe_id: str,
    limit: int = Query(5, ge=1, le=20, description="取得件数"),
):
    """類似レシピを取得"""
    try:
        recipes = _get_dummy_recipes()

        # レシピが存在するかチェック
        if not any(r.get("id") == recipe_id for r in recipes):
            raise HTTPException(status_code=404, detail="レシピが見つかりません")

        similar_recipes = recommendation_service.get_similar_recipes(
            recipe_id=recipe_id, recipes=recipes, limit=limit
        )

        return StandardResponse(
            status="ok",
            data={
                "recipe_id": recipe_id,
                "similar_recipes": similar_recipes,
                "total": len(similar_recipes),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"類似レシピ取得エラー: {str(e)}")


@router.get(
    "/recommend/trending",
    response_model=StandardResponse,
    summary="トレンドレシピ取得",
    description="最近人気のレシピを取得",
)
async def get_trending_recipes(
    limit: int = Query(10, ge=1, le=50, description="取得件数"),
):
    """トレンドレシピを取得"""
    try:
        recipes = _get_dummy_recipes()

        trending_recipes = recommendation_service.get_trending_recommendations(
            recipes=recipes, limit=limit
        )

        return StandardResponse(
            status="ok",
            data={
                "trending_recipes": trending_recipes,
                "total": len(trending_recipes),
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"トレンドレシピ取得エラー: {str(e)}"
        )


@router.post(
    "/feedback",
    response_model=StandardResponse,
    summary="推薦フィードバック",
    description="推薦結果に対するユーザーフィードバックを記録",
)
async def submit_feedback(request: FeedbackRequest):
    """推薦フィードバックを記録"""
    try:
        # フィードバックタイプのバリデーション
        valid_types = ["interested", "not_interested", "favorited", "cooked"]
        if request.feedback_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"無効なフィードバックタイプ: {request.feedback_type}",
            )

        recommendation_service.submit_feedback(
            user_id=request.user_id,
            recipe_id=request.recipe_id,
            feedback_type=request.feedback_type,
            metadata=request.metadata,
        )

        return StandardResponse(
            status="ok",
            data={
                "message": "フィードバックを記録しました",
                "user_id": request.user_id,
                "recipe_id": request.recipe_id,
                "feedback_type": request.feedback_type,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"フィードバック記録エラー: {str(e)}"
        )


@router.post(
    "/activity",
    response_model=StandardResponse,
    summary="ユーザー行動記録",
    description="ユーザーの行動を記録（推薦アルゴリズム学習用）",
)
async def record_activity(request: ActivityRequest):
    """ユーザー行動を記録"""
    try:
        # 行動タイプのバリデーション
        valid_types = ["viewed", "cooked", "rated", "favorited", "dismissed"]
        if request.activity_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"無効な行動タイプ: {request.activity_type}",
            )

        recommendation_service.record_activity(
            user_id=request.user_id,
            recipe_id=request.recipe_id,
            activity_type=request.activity_type,
            metadata=request.metadata,
        )

        return StandardResponse(
            status="ok",
            data={
                "message": "行動を記録しました",
                "user_id": request.user_id,
                "recipe_id": request.recipe_id,
                "activity_type": request.activity_type,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"行動記録エラー: {str(e)}")


@router.get(
    "/preferences",
    response_model=StandardResponse,
    summary="ユーザー嗜好分析",
    description="ユーザーの嗜好を分析した結果を取得",
)
async def get_user_preferences(user_id: str = Query(..., description="ユーザーID")):
    """ユーザー嗜好分析結果を取得"""
    try:
        recipes = _get_dummy_recipes()

        preferences = recommendation_service.get_user_preferences(
            user_id=user_id, recipes=recipes
        )

        return StandardResponse(status="ok", data=preferences)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"嗜好分析エラー: {str(e)}")


# === Helper Functions ===


def _get_dummy_recipes() -> List[dict]:
    """ダミーレシピデータ（実際はDBから取得）"""
    return [
        {
            "id": "recipe_001",
            "title": "カレーライス",
            "category": "主菜",
            "tags": ["簡単", "人気", "定番"],
            "ingredients": [
                {"name": "じゃがいも", "amount": "2個"},
                {"name": "にんじん", "amount": "1本"},
                {"name": "玉ねぎ", "amount": "1個"},
                {"name": "豚肉", "amount": "200g"},
            ],
            "cooking_time": 30,
            "difficulty": "easy",
        },
        {
            "id": "recipe_002",
            "title": "肉じゃが",
            "category": "主菜",
            "tags": ["和食", "定番", "煮物"],
            "ingredients": [
                {"name": "じゃがいも", "amount": "3個"},
                {"name": "にんじん", "amount": "1本"},
                {"name": "玉ねぎ", "amount": "1個"},
                {"name": "牛肉", "amount": "200g"},
            ],
            "cooking_time": 40,
            "difficulty": "medium",
        },
        {
            "id": "recipe_003",
            "title": "サラダチキン",
            "category": "副菜",
            "tags": ["ヘルシー", "時短", "簡単"],
            "ingredients": [
                {"name": "鶏むね肉", "amount": "1枚"},
                {"name": "塩", "amount": "小さじ1"},
            ],
            "cooking_time": 15,
            "difficulty": "easy",
        },
        {
            "id": "recipe_004",
            "title": "ハンバーグ",
            "category": "主菜",
            "tags": ["洋食", "人気", "子供向け"],
            "ingredients": [
                {"name": "牛ひき肉", "amount": "300g"},
                {"name": "玉ねぎ", "amount": "1個"},
                {"name": "卵", "amount": "1個"},
                {"name": "パン粉", "amount": "大さじ3"},
            ],
            "cooking_time": 35,
            "difficulty": "medium",
        },
        {
            "id": "recipe_005",
            "title": "ペペロンチーノ",
            "category": "主食",
            "tags": ["イタリアン", "時短", "簡単"],
            "ingredients": [
                {"name": "パスタ", "amount": "200g"},
                {"name": "にんにく", "amount": "2片"},
                {"name": "唐辛子", "amount": "1本"},
                {"name": "オリーブオイル", "amount": "大さじ2"},
            ],
            "cooking_time": 20,
            "difficulty": "easy",
        },
        {
            "id": "recipe_006",
            "title": "麻婆豆腐",
            "category": "主菜",
            "tags": ["中華", "辛い", "人気"],
            "ingredients": [
                {"name": "豆腐", "amount": "1丁"},
                {"name": "豚ひき肉", "amount": "100g"},
                {"name": "長ねぎ", "amount": "1本"},
                {"name": "豆板醤", "amount": "大さじ1"},
            ],
            "cooking_time": 25,
            "difficulty": "medium",
        },
        {
            "id": "recipe_007",
            "title": "オムライス",
            "category": "主食",
            "tags": ["洋食", "子供向け", "人気"],
            "ingredients": [
                {"name": "ご飯", "amount": "1杯"},
                {"name": "卵", "amount": "2個"},
                {"name": "鶏肉", "amount": "100g"},
                {"name": "玉ねぎ", "amount": "1/2個"},
            ],
            "cooking_time": 30,
            "difficulty": "medium",
        },
        {
            "id": "recipe_008",
            "title": "味噌汁",
            "category": "汁物",
            "tags": ["和食", "簡単", "定番"],
            "ingredients": [
                {"name": "豆腐", "amount": "1/2丁"},
                {"name": "わかめ", "amount": "適量"},
                {"name": "味噌", "amount": "大さじ2"},
            ],
            "cooking_time": 10,
            "difficulty": "easy",
        },
        {
            "id": "recipe_009",
            "title": "チャーハン",
            "category": "主食",
            "tags": ["中華", "時短", "簡単"],
            "ingredients": [
                {"name": "ご飯", "amount": "1杯"},
                {"name": "卵", "amount": "1個"},
                {"name": "長ねぎ", "amount": "1/2本"},
                {"name": "チャーシュー", "amount": "50g"},
            ],
            "cooking_time": 15,
            "difficulty": "easy",
        },
        {
            "id": "recipe_010",
            "title": "親子丼",
            "category": "主食",
            "tags": ["和食", "簡単", "人気"],
            "ingredients": [
                {"name": "鶏もも肉", "amount": "150g"},
                {"name": "卵", "amount": "2個"},
                {"name": "玉ねぎ", "amount": "1/2個"},
                {"name": "ご飯", "amount": "1杯"},
            ],
            "cooking_time": 20,
            "difficulty": "easy",
        },
    ]

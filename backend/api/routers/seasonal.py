"""
季節・時間帯別レシピ推薦APIルーター

エンドポイント:
- GET /api/v1/seasonal/now - 今の季節のおすすめ
- GET /api/v1/seasonal/meal-time - 時間帯別おすすめ
- GET /api/v1/seasonal/ingredients - 旬の食材レシピ
- GET /api/v1/seasonal/temperature - 気温に応じたおすすめ
- GET /api/v1/seasonal/comprehensive - 総合的なおすすめ
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from backend.services.seasonal_service import (
    SeasonalService,
    Season,
    MealTime,
)


# レスポンスモデル
class StandardResponse(BaseModel):
    """標準レスポンス形式"""

    status: str = Field(default="ok", description="ステータス")
    data: Optional[Any] = Field(default=None, description="データ")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")


class SeasonalRecommendationResponse(BaseModel):
    """季節推薦レスポンス"""

    season: str = Field(..., description="季節")
    season_name_ja: str = Field(..., description="季節名（日本語）")
    recommendations: List[Dict] = Field(..., description="推薦レシピリスト")
    count: int = Field(..., description="推薦件数")


class MealTimeRecommendationResponse(BaseModel):
    """時間帯推薦レスポンス"""

    meal_time: str = Field(..., description="食事時間")
    meal_time_name_ja: str = Field(..., description="食事時間名（日本語）")
    current_time: str = Field(..., description="現在時刻")
    recommendations: List[Dict] = Field(..., description="推薦レシピリスト")
    count: int = Field(..., description="推薦件数")


class IngredientsResponse(BaseModel):
    """旬の食材レスポンス"""

    season: str = Field(..., description="季節")
    season_name_ja: str = Field(..., description="季節名（日本語）")
    ingredients: List[str] = Field(..., description="旬の食材リスト")
    recipes: List[Dict] = Field(..., description="食材を使ったレシピ")
    count: int = Field(..., description="レシピ件数")


class TemperatureRecommendationResponse(BaseModel):
    """気温推薦レスポンス"""

    temperature: float = Field(..., description="気温（摂氏）")
    category: str = Field(..., description="推薦カテゴリ")
    recommendations: List[Dict] = Field(..., description="推薦レシピリスト")
    count: int = Field(..., description="推薦件数")


class ComprehensiveRecommendationResponse(BaseModel):
    """総合推薦レスポンス"""

    season: str = Field(..., description="季節")
    meal_time: str = Field(..., description="食事時間")
    temperature: Optional[float] = Field(None, description="気温（摂氏）")
    recommendations: List[Dict] = Field(..., description="推薦レシピリスト")
    count: int = Field(..., description="推薦件数")


# ルーター作成
router = APIRouter(prefix="/api/v1/seasonal", tags=["seasonal"])

# 季節名の日本語マッピング
SEASON_NAMES_JA = {
    "spring": "春",
    "summer": "夏",
    "autumn": "秋",
    "winter": "冬",
}

# 食事時間名の日本語マッピング
MEAL_TIME_NAMES_JA = {
    "breakfast": "朝食",
    "lunch": "昼食",
    "dinner": "夕食",
    "late_night": "夜食",
}


# サンプルレシピデータ（実際にはDBから取得）
SAMPLE_RECIPES = [
    {
        "id": 1,
        "title": "たけのこご飯",
        "description": "春の味覚、たけのこを使った炊き込みご飯",
        "ingredients": [
            {"name": "たけのこ", "amount": "200g"},
            {"name": "米", "amount": "2合"},
            {"name": "油揚げ", "amount": "1枚"},
        ],
        "tags": ["和食", "ご飯", "春", "昼食", "夕食"],
    },
    {
        "id": 2,
        "title": "冷やし中華",
        "description": "夏にぴったりの冷たい麺料理",
        "ingredients": [
            {"name": "中華麺", "amount": "2玉"},
            {"name": "きゅうり", "amount": "1本"},
            {"name": "トマト", "amount": "1個"},
        ],
        "tags": ["中華", "麺類", "冷たい", "夏", "昼食"],
    },
    {
        "id": 3,
        "title": "さつまいもの煮物",
        "description": "ほっこり甘い秋の味覚",
        "ingredients": [
            {"name": "さつまいも", "amount": "2本"},
            {"name": "砂糖", "amount": "大さじ2"},
            {"name": "醤油", "amount": "大さじ1"},
        ],
        "tags": ["和食", "煮物", "温かい", "秋", "夕食"],
    },
    {
        "id": 4,
        "title": "白菜と豚肉の鍋",
        "description": "冬の定番、体が温まる鍋料理",
        "ingredients": [
            {"name": "白菜", "amount": "1/4個"},
            {"name": "豚肉", "amount": "200g"},
            {"name": "豆腐", "amount": "1丁"},
        ],
        "tags": ["和食", "鍋", "温かい", "冬", "夕食"],
    },
    {
        "id": 5,
        "title": "卵かけご飯",
        "description": "シンプルで美味しい朝食の定番",
        "ingredients": [
            {"name": "ご飯", "amount": "1膳"},
            {"name": "卵", "amount": "1個"},
            {"name": "醤油", "amount": "適量"},
        ],
        "tags": ["和食", "ご飯", "朝食", "簡単", "時短"],
    },
]


def get_seasonal_service() -> SeasonalService:
    """
    SeasonalServiceのインスタンスを取得

    Returns:
        SeasonalService: サービスインスタンス
    """
    # 実際にはDBから取得したレシピデータを使用
    return SeasonalService(recipe_data=SAMPLE_RECIPES)


@router.get("/now", response_model=StandardResponse)
async def get_seasonal_recommendations(
    limit: int = Query(default=10, ge=1, le=100, description="取得件数"),
) -> StandardResponse:
    """
    現在の季節に合ったレシピを推薦

    Args:
        limit: 取得する最大件数

    Returns:
        StandardResponse: 季節推薦レスポンス
    """
    try:
        service = get_seasonal_service()
        current_season = service.get_current_season()
        recommendations = service.recommend_by_season(
            season=current_season, limit=limit
        )

        response_data = SeasonalRecommendationResponse(
            season=current_season.value,
            season_name_ja=SEASON_NAMES_JA.get(
                current_season.value, current_season.value
            ),
            recommendations=recommendations,
            count=len(recommendations),
        )

        return StandardResponse(status="ok", data=response_data.dict(), error=None)

    except Exception as e:
        return StandardResponse(status="error", data=None, error=str(e))


@router.get("/meal-time", response_model=StandardResponse)
async def get_meal_time_recommendations(
    limit: int = Query(default=10, ge=1, le=100, description="取得件数"),
) -> StandardResponse:
    """
    現在の時間帯に合ったレシピを推薦

    Args:
        limit: 取得する最大件数

    Returns:
        StandardResponse: 時間帯推薦レスポンス
    """
    try:
        service = get_seasonal_service()
        current_meal_time = service.get_current_meal_time()
        recommendations = service.recommend_by_meal_time(
            meal_time=current_meal_time, limit=limit
        )

        response_data = MealTimeRecommendationResponse(
            meal_time=current_meal_time.value,
            meal_time_name_ja=MEAL_TIME_NAMES_JA.get(
                current_meal_time.value, current_meal_time.value
            ),
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            recommendations=recommendations,
            count=len(recommendations),
        )

        return StandardResponse(status="ok", data=response_data.dict(), error=None)

    except Exception as e:
        return StandardResponse(status="error", data=None, error=str(e))


@router.get("/ingredients", response_model=StandardResponse)
async def get_seasonal_ingredients_recipes(
    season: Optional[str] = Query(
        default=None, description="季節（spring/summer/autumn/winter）"
    ),
    limit: int = Query(default=10, ge=1, le=100, description="取得件数"),
) -> StandardResponse:
    """
    旬の食材を使ったレシピを推薦

    Args:
        season: 季節（Noneの場合は現在の季節）
        limit: 取得する最大件数

    Returns:
        StandardResponse: 旬の食材レシピレスポンス
    """
    try:
        service = get_seasonal_service()

        # 季節の指定がある場合はバリデーション
        target_season = None
        if season:
            try:
                target_season = Season(season)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid season: {season}. Must be one of: spring, summer, autumn, winter",
                )
        else:
            target_season = service.get_current_season()

        # 旬の食材を取得
        ingredients = service.get_seasonal_ingredients(season=target_season)

        # レシピ推薦
        recommendations = service.recommend_by_season(season=target_season, limit=limit)

        response_data = IngredientsResponse(
            season=target_season.value,
            season_name_ja=SEASON_NAMES_JA.get(
                target_season.value, target_season.value
            ),
            ingredients=ingredients,
            recipes=recommendations,
            count=len(recommendations),
        )

        return StandardResponse(status="ok", data=response_data.dict(), error=None)

    except HTTPException:
        raise
    except Exception as e:
        return StandardResponse(status="error", data=None, error=str(e))


@router.get("/temperature", response_model=StandardResponse)
async def get_temperature_recommendations(
    temperature: float = Query(..., description="気温（摂氏）"),
    limit: int = Query(default=10, ge=1, le=100, description="取得件数"),
) -> StandardResponse:
    """
    気温に応じたレシピを推薦

    Args:
        temperature: 気温（摂氏）
        limit: 取得する最大件数

    Returns:
        StandardResponse: 気温推薦レスポンス
    """
    try:
        service = get_seasonal_service()
        recommendations = service.recommend_by_temperature(
            temperature=temperature, limit=limit
        )

        category = "hot" if temperature >= 25 else "warm"
        category_ja = "冷たい料理" if temperature >= 25 else "温かい料理"

        response_data = TemperatureRecommendationResponse(
            temperature=temperature,
            category=f"{category} ({category_ja})",
            recommendations=recommendations,
            count=len(recommendations),
        )

        return StandardResponse(status="ok", data=response_data.dict(), error=None)

    except Exception as e:
        return StandardResponse(status="error", data=None, error=str(e))


@router.get("/comprehensive", response_model=StandardResponse)
async def get_comprehensive_recommendations(
    season: Optional[str] = Query(
        default=None, description="季節（spring/summer/autumn/winter）"
    ),
    meal_time: Optional[str] = Query(
        default=None, description="食事時間（breakfast/lunch/dinner/late_night）"
    ),
    temperature: Optional[float] = Query(default=None, description="気温（摂氏）"),
    limit: int = Query(default=10, ge=1, le=100, description="取得件数"),
) -> StandardResponse:
    """
    総合的なレシピ推薦（季節・時間帯・気温を考慮）

    Args:
        season: 季節（Noneの場合は現在の季節）
        meal_time: 食事時間（Noneの場合は現在の時間帯）
        temperature: 気温（Noneの場合は考慮しない）
        limit: 取得する最大件数

    Returns:
        StandardResponse: 総合推薦レスポンス
    """
    try:
        service = get_seasonal_service()

        # 季節のバリデーション
        target_season = None
        if season:
            try:
                target_season = Season(season)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid season: {season}. Must be one of: spring, summer, autumn, winter",
                )

        # 食事時間のバリデーション
        target_meal_time = None
        if meal_time:
            try:
                target_meal_time = MealTime(meal_time)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid meal_time: {meal_time}. Must be one of: breakfast, lunch, dinner, late_night",
                )

        # 総合推薦
        recommendations = service.recommend_comprehensive(
            season=target_season,
            meal_time=target_meal_time,
            temperature=temperature,
            limit=limit,
        )

        # 実際に使用された値を取得
        used_season = target_season or service.get_current_season()
        used_meal_time = target_meal_time or service.get_current_meal_time()

        response_data = ComprehensiveRecommendationResponse(
            season=f"{used_season.value} ({SEASON_NAMES_JA.get(used_season.value, used_season.value)})",
            meal_time=f"{used_meal_time.value} ({MEAL_TIME_NAMES_JA.get(used_meal_time.value, used_meal_time.value)})",
            temperature=temperature,
            recommendations=recommendations,
            count=len(recommendations),
        )

        return StandardResponse(status="ok", data=response_data.dict(), error=None)

    except HTTPException:
        raise
    except Exception as e:
        return StandardResponse(status="error", data=None, error=str(e))


@router.get("/info", response_model=StandardResponse)
async def get_seasonal_info() -> StandardResponse:
    """
    季節推薦機能の情報を取得

    Returns:
        StandardResponse: 機能情報
    """
    try:
        service = get_seasonal_service()
        current_season = service.get_current_season()
        current_meal_time = service.get_current_meal_time()

        info = {
            "current_season": {
                "value": current_season.value,
                "name_ja": SEASON_NAMES_JA.get(
                    current_season.value, current_season.value
                ),
                "ingredients": service.get_seasonal_ingredients(season=current_season),
            },
            "current_meal_time": {
                "value": current_meal_time.value,
                "name_ja": MEAL_TIME_NAMES_JA.get(
                    current_meal_time.value, current_meal_time.value
                ),
            },
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "available_seasons": [s.value for s in Season],
            "available_meal_times": [m.value for m in MealTime],
        }

        return StandardResponse(status="ok", data=info, error=None)

    except Exception as e:
        return StandardResponse(status="error", data=None, error=str(e))

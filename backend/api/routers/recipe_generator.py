"""
レシピ自動生成 API ルーター
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.services.recipe_generator_service import RecipeGeneratorService


router = APIRouter(prefix="/api/v1/ai", tags=["recipe_generator"])

# サービスインスタンス
generator_service = RecipeGeneratorService()


# リクエスト/レスポンスモデル
class GenerateRecipeRequest(BaseModel):
    """レシピ生成リクエスト"""

    ingredients: List[str] = Field(..., min_items=1, description="使用する食材リスト")
    category: str = Field(
        default="japanese", description="料理カテゴリ (japanese/western/chinese)"
    )
    cooking_time: Optional[int] = Field(
        default=None, ge=5, le=120, description="調理時間（分）"
    )
    difficulty: Optional[str] = Field(
        default=None, description="難易度 (easy/medium/hard)"
    )
    use_seasonal: bool = Field(default=True, description="季節の食材を活用するか")


class GenerateVariationsRequest(BaseModel):
    """バリエーション生成リクエスト"""

    base_recipe: dict = Field(..., description="元となるレシピ")
    count: int = Field(default=3, ge=1, le=10, description="生成する数")


class SuggestCombinationsRequest(BaseModel):
    """食材組み合わせ提案リクエスト"""

    main_ingredient: str = Field(..., description="メイン食材")
    count: int = Field(default=5, ge=1, le=10, description="提案数")


class ImproveRecipeRequest(BaseModel):
    """レシピ改善リクエスト"""

    recipe: dict = Field(..., description="改善対象のレシピ")
    focus: str = Field(
        default="taste", description="改善の焦点 (taste/health/speed/cost)"
    )


class RecipeResponse(BaseModel):
    """レシピレスポンス"""

    status: str
    data: dict
    error: Optional[str] = None


class RecipeListResponse(BaseModel):
    """レシピリストレスポンス"""

    status: str
    data: List[dict]
    error: Optional[str] = None


class SuggestionResponse(BaseModel):
    """提案レスポンス"""

    status: str
    data: List[dict]
    error: Optional[str] = None


@router.post("/generate", response_model=RecipeResponse)
async def generate_recipe(request: GenerateRecipeRequest):
    """
    レシピを自動生成

    指定された食材とオプションからレシピを生成します。
    """
    try:
        recipe = generator_service.generate_recipe(
            ingredients=request.ingredients,
            category=request.category,
            cooking_time=request.cooking_time,
            difficulty=request.difficulty,
            use_seasonal=request.use_seasonal,
        )

        # 栄養情報を追加
        nutrition = generator_service.get_nutrition_estimate(recipe)
        recipe["nutrition"] = nutrition

        return RecipeResponse(status="ok", data=recipe)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"レシピ生成エラー: {str(e)}",
        )


@router.post("/generate/variations", response_model=RecipeListResponse)
async def generate_variations(request: GenerateVariationsRequest):
    """
    レシピのバリエーションを生成

    既存のレシピを元に、異なる調理方法のバリエーションを生成します。
    """
    try:
        variations = generator_service.generate_variations(
            base_recipe=request.base_recipe, count=request.count
        )

        # 各バリエーションに栄養情報を追加
        for variation in variations:
            nutrition = generator_service.get_nutrition_estimate(variation)
            variation["nutrition"] = nutrition

        return RecipeListResponse(status="ok", data=variations)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"バリエーション生成エラー: {str(e)}",
        )


@router.get("/generate/suggestions", response_model=SuggestionResponse)
async def get_suggestions(main_ingredient: str, count: int = 5):
    """
    食材の組み合わせを提案

    メイン食材に相性の良い食材の組み合わせを提案します。
    """
    try:
        if not main_ingredient:
            raise ValueError("メイン食材を指定してください")

        suggestions = generator_service.suggest_ingredient_combinations(
            main_ingredient=main_ingredient, count=count
        )

        return SuggestionResponse(status="ok", data=suggestions)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提案生成エラー: {str(e)}",
        )


@router.post("/generate/improve", response_model=RecipeResponse)
async def improve_recipe(request: ImproveRecipeRequest):
    """
    既存レシピを改善

    指定された焦点に基づいてレシピを改善します。
    - taste: 味を改善
    - health: ヘルシーに改善
    - speed: 調理時間を短縮
    - cost: コストを削減
    """
    try:
        valid_focuses = ["taste", "health", "speed", "cost"]
        if request.focus not in valid_focuses:
            raise ValueError(
                f"無効な改善焦点: {request.focus}。{valid_focuses} から選択してください。"
            )

        improved = generator_service.improve_recipe(
            recipe=request.recipe, focus=request.focus
        )

        # 栄養情報を追加
        nutrition = generator_service.get_nutrition_estimate(improved)
        improved["nutrition"] = nutrition

        return RecipeResponse(status="ok", data=improved)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"レシピ改善エラー: {str(e)}",
        )


@router.get("/categories")
async def get_categories():
    """
    利用可能な料理カテゴリを取得
    """
    return {
        "status": "ok",
        "data": {
            "categories": ["japanese", "western", "chinese"],
            "difficulties": ["easy", "medium", "hard"],
            "improvement_focuses": ["taste", "health", "speed", "cost"],
        },
    }


@router.get("/ingredients")
async def get_ingredients():
    """
    利用可能な食材リストを取得
    """
    return {
        "status": "ok",
        "data": {
            "meat": ["鶏肉", "豚肉", "牛肉", "ひき肉"],
            "seafood": ["鮭", "エビ", "イカ", "タラ", "サバ"],
            "vegetable": [
                "玉ねぎ",
                "にんじん",
                "キャベツ",
                "ピーマン",
                "なす",
                "トマト",
                "ほうれん草",
                "ブロッコリー",
            ],
            "mushroom": ["しめじ", "えのき", "しいたけ", "エリンギ"],
            "tofu": ["豆腐", "厚揚げ", "油揚げ"],
        },
    }

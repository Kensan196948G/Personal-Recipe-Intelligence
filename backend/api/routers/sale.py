"""
特売情報APIルーター

特売情報の取得、チラシアップロード、レシピ推薦などのエンドポイントを提供。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field

from ...services.sale_service import (
    SaleService,
    SaleCategory,
)
from ...services.flyer_parser import FlyerParser


router = APIRouter(prefix="/api/v1/sales", tags=["sales"])

# サービスインスタンス（実運用ではDI使用）
sale_service = SaleService()
flyer_parser = FlyerParser()


# Request/Response Models
class SaleItemResponse(BaseModel):
    """特売商品レスポンス"""

    id: str
    store_name: str
    product_name: str
    price: float
    original_price: Optional[float] = None
    unit: str
    category: str
    valid_from: str
    valid_until: str
    discount_rate: Optional[float] = None
    image_url: Optional[str] = None


class SaleListResponse(BaseModel):
    """特売一覧レスポンス"""

    status: str = "ok"
    data: List[SaleItemResponse]
    total: int
    error: Optional[str] = None


class PriceComparisonItem(BaseModel):
    """価格比較アイテム"""

    store_name: str
    product_name: str
    price: float
    unit: str
    discount_rate: Optional[float] = None
    valid_until: str


class PriceComparisonResponse(BaseModel):
    """価格比較レスポンス"""

    status: str = "ok"
    data: List[PriceComparisonItem]
    product_name: str
    cheapest_store: Optional[str] = None
    price_range: Optional[Dict[str, float]] = None
    error: Optional[str] = None


class RecipeRecommendation(BaseModel):
    """レシピ推薦"""

    recipe_id: Optional[str] = None
    recipe_name: str
    matching_ingredients: List[str]
    estimated_cost: float
    savings: Optional[float] = None
    available_sale_items: List[SaleItemResponse]


class RecommendationResponse(BaseModel):
    """レシピ推薦レスポンス"""

    status: str = "ok"
    data: List[RecipeRecommendation]
    total_recommendations: int
    error: Optional[str] = None


class UploadFlyerRequest(BaseModel):
    """チラシアップロードリクエスト"""

    store_name: Optional[str] = None
    valid_days: int = Field(default=3, ge=1, le=30)
    ocr_text: Optional[str] = None


class UploadFlyerResponse(BaseModel):
    """チラシアップロードレスポンス"""

    status: str = "ok"
    data: Dict[str, Any]
    error: Optional[str] = None


class StatisticsResponse(BaseModel):
    """統計レスポンス"""

    status: str = "ok"
    data: Dict[str, Any]
    error: Optional[str] = None


class CostEstimateRequest(BaseModel):
    """材料費見積もりリクエスト"""

    ingredients: List[str]


class CostEstimateResponse(BaseModel):
    """材料費見積もりレスポンス"""

    status: str = "ok"
    data: Dict[str, Any]
    error: Optional[str] = None


# Endpoints
@router.get("", response_model=SaleListResponse)
async def get_sales(
    store_name: Optional[str] = Query(None, description="店舗名フィルタ"),
    category: Optional[str] = Query(None, description="カテゴリフィルタ"),
    min_discount: Optional[float] = Query(
        None, ge=0, le=100, description="最小割引率（%）"
    ),
) -> SaleListResponse:
    """
    特売情報一覧を取得

    Args:
      store_name: 店舗名（任意）
      category: カテゴリ（任意）
      min_discount: 最小割引率（任意）

    Returns:
      特売情報一覧
    """
    try:
        # カテゴリ変換
        category_enum = None
        if category:
            try:
                category_enum = SaleCategory[category.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f"無効なカテゴリ: {category}"
                )

        # 特売情報取得
        sales = sale_service.get_active_sales(
            store_name=store_name,
            category=category_enum,
            min_discount=min_discount,
        )

        # レスポンス変換
        sale_responses = [
            SaleItemResponse(
                id=sale.id,
                store_name=sale.store_name,
                product_name=sale.product_name,
                price=sale.price,
                original_price=sale.original_price,
                unit=sale.unit,
                category=sale.category.value,
                valid_from=sale.valid_from.isoformat(),
                valid_until=sale.valid_until.isoformat(),
                discount_rate=sale.discount_rate,
                image_url=sale.image_url,
            )
            for sale in sales
        ]

        return SaleListResponse(
            status="ok",
            data=sale_responses,
            total=len(sale_responses),
        )

    except HTTPException:
        raise
    except Exception as e:
        return SaleListResponse(
            status="error",
            data=[],
            total=0,
            error=str(e),
        )


@router.post("/upload", response_model=UploadFlyerResponse)
async def upload_flyer(
    file: UploadFile = File(...),
    store_name: Optional[str] = Query(None, description="店舗名"),
    valid_days: int = Query(3, ge=1, le=30, description="有効日数"),
) -> UploadFlyerResponse:
    """
    チラシ画像をアップロードして特売情報を抽出

    Args:
      file: チラシ画像ファイル
      store_name: 店舗名（任意、自動検出も可能）
      valid_days: 有効日数

    Returns:
      抽出された特売情報
    """
    try:
        # ファイルタイプチェック
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="画像ファイルをアップロードしてください"
            )

        # OCR processing
        # Note: In production, integrate with OCR service (e.g., Tesseract, Google Vision API)
        # For now, using mock OCR text for demonstration
        ocr_text = """
    イオン 今週の特売
    たまねぎ 98円
    にんじん 3本 158円
    豚バラ肉 100g 198円
    牛乳 1L 168円
    キャベツ 1玉 128円
    """
        # TODO: Integrate actual OCR processing
        # from backend.ocr.service import OCRService
        # ocr_service = OCRService()
        # ocr_text = await ocr_service.extract_text_from_image(file)

        # 店舗名自動検出
        if not store_name:
            store_name = flyer_parser.extract_store_name(ocr_text)

        # 商品情報抽出
        parsed_products = flyer_parser.parse_ocr_result(ocr_text, store_name)

        # 検証
        validated_products = flyer_parser.validate_parsed_products(parsed_products)

        # SaleItem生成
        sale_items = flyer_parser.create_sale_items(
            validated_products, store_name, valid_days
        )

        # サービスに追加
        for item in sale_items:
            sale_service.add_sale_item(item)

        return UploadFlyerResponse(
            status="ok",
            data={
                "store_name": store_name,
                "items_count": len(sale_items),
                "valid_until": (
                    datetime.now() + timedelta(days=valid_days)
                ).isoformat(),
                "items": [item.to_dict() for item in sale_items],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        return UploadFlyerResponse(
            status="error",
            data={},
            error=str(e),
        )


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    recipe_ids: Optional[List[str]] = Query(None, description="レシピIDリスト"),
    max_results: int = Query(10, ge=1, le=50, description="最大結果数"),
) -> RecommendationResponse:
    """
    特売食材を使ったレシピ推薦

    Args:
      recipe_ids: 対象レシピIDリスト（任意）
      max_results: 最大結果数

    Returns:
      レシピ推薦リスト
    """
    try:
        # TODO: 実際のレシピデータベースと連携
        # 仮のレシピデータ
        sample_recipes = [
            {
                "id": "recipe-001",
                "name": "肉じゃが",
                "ingredients": ["じゃがいも", "たまねぎ", "にんじん", "豚肉"],
            },
            {
                "id": "recipe-002",
                "name": "野菜炒め",
                "ingredients": ["キャベツ", "にんじん", "豚肉"],
            },
            {
                "id": "recipe-003",
                "name": "カレー",
                "ingredients": ["じゃがいも", "たまねぎ", "にんじん", "牛肉"],
            },
        ]

        recommendations = []

        for recipe in sample_recipes:
            # 材料費見積もり
            cost_estimate = sale_service.get_recipe_cost_estimate(recipe["ingredients"])

            # 特売マッチング
            matching_sales = sale_service.get_ingredient_recommendations(
                recipe["ingredients"]
            )

            if matching_sales:
                matching_ingredient_names = [
                    sale_service.normalize_ingredient_name(sale.product_name)
                    for sale in matching_sales
                ]

                recommendations.append(
                    RecipeRecommendation(
                        recipe_id=recipe["id"],
                        recipe_name=recipe["name"],
                        matching_ingredients=matching_ingredient_names,
                        estimated_cost=cost_estimate["total_cost"],
                        available_sale_items=[
                            SaleItemResponse(
                                id=sale.id,
                                store_name=sale.store_name,
                                product_name=sale.product_name,
                                price=sale.price,
                                original_price=sale.original_price,
                                unit=sale.unit,
                                category=sale.category.value,
                                valid_from=sale.valid_from.isoformat(),
                                valid_until=sale.valid_until.isoformat(),
                                discount_rate=sale.discount_rate,
                                image_url=sale.image_url,
                            )
                            for sale in matching_sales
                        ],
                    )
                )

        # マッチング数でソート
        recommendations.sort(key=lambda x: len(x.matching_ingredients), reverse=True)

        return RecommendationResponse(
            status="ok",
            data=recommendations[:max_results],
            total_recommendations=len(recommendations),
        )

    except Exception as e:
        return RecommendationResponse(
            status="error",
            data=[],
            total_recommendations=0,
            error=str(e),
        )


@router.get("/price-compare", response_model=PriceComparisonResponse)
async def compare_prices(
    product_name: str = Query(..., description="商品名（部分一致）"),
) -> PriceComparisonResponse:
    """
    商品の価格比較

    Args:
      product_name: 商品名

    Returns:
      価格比較結果
    """
    try:
        comparison_data = sale_service.compare_prices(product_name)

        if not comparison_data:
            return PriceComparisonResponse(
                status="ok",
                data=[],
                product_name=product_name,
                error="該当する商品が見つかりませんでした",
            )

        comparison_items = [PriceComparisonItem(**item) for item in comparison_data]

        # 最安値店舗
        cheapest_store = comparison_items[0].store_name if comparison_items else None

        # 価格範囲
        prices = [item.price for item in comparison_items]
        price_range = {
            "min": min(prices),
            "max": max(prices),
            "avg": round(sum(prices) / len(prices), 2),
        }

        return PriceComparisonResponse(
            status="ok",
            data=comparison_items,
            product_name=product_name,
            cheapest_store=cheapest_store,
            price_range=price_range,
        )

    except Exception as e:
        return PriceComparisonResponse(
            status="error",
            data=[],
            product_name=product_name,
            error=str(e),
        )


@router.post("/cost-estimate", response_model=CostEstimateResponse)
async def estimate_cost(request: CostEstimateRequest) -> CostEstimateResponse:
    """
    レシピの材料費見積もり

    Args:
      request: 材料リスト

    Returns:
      材料費見積もり
    """
    try:
        estimate = sale_service.get_recipe_cost_estimate(request.ingredients)

        return CostEstimateResponse(
            status="ok",
            data=estimate,
        )

    except Exception as e:
        return CostEstimateResponse(
            status="error",
            data={},
            error=str(e),
        )


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics() -> StatisticsResponse:
    """
    特売情報統計を取得

    Returns:
      統計情報
    """
    try:
        stats = sale_service.get_statistics()

        return StatisticsResponse(
            status="ok",
            data=stats,
        )

    except Exception as e:
        return StatisticsResponse(
            status="error",
            data={},
            error=str(e),
        )


@router.delete("/expired")
async def clear_expired() -> Dict[str, Any]:
    """
    期限切れ特売情報を削除

    Returns:
      削除件数
    """
    try:
        deleted_count = sale_service.clear_expired_sales()

        return {
            "status": "ok",
            "data": {"deleted_count": deleted_count},
            "error": None,
        }

    except Exception as e:
        return {
            "status": "error",
            "data": {"deleted_count": 0},
            "error": str(e),
        }

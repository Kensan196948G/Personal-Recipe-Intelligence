"""
宅配サービス連携APIルーター
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.delivery_service import (
  DeliveryService,
  DeliveryServiceType
)


router = APIRouter(prefix="/api/v1/delivery", tags=["delivery"])
delivery_service = DeliveryService()


class ProductSearchRequest(BaseModel):
  """商品検索リクエスト"""
  ingredient_name: str = Field(..., description="食材名")
  services: Optional[List[DeliveryServiceType]] = Field(
    None,
    description="検索対象サービス（未指定時は全サービス）"
  )
  max_results: int = Field(20, ge=1, le=100, description="最大取得件数")


class AddToCartRequest(BaseModel):
  """カート追加リクエスト"""
  service: DeliveryServiceType = Field(..., description="サービス")
  product_id: str = Field(..., description="商品ID")
  quantity: int = Field(1, ge=1, le=99, description="数量")


class RemoveFromCartRequest(BaseModel):
  """カート削除リクエスト"""
  service: DeliveryServiceType = Field(..., description="サービス")
  product_id: str = Field(..., description="商品ID")


@router.get("/services")
async def get_services():
  """
  対応サービス一覧取得

  Returns:
    対応している宅配サービスの一覧
  """
  try:
    services = delivery_service.get_available_services()
    return {
      "status": "ok",
      "data": {
        "services": services,
        "count": len(services)
      }
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_products(request: ProductSearchRequest):
  """
  商品検索

  Args:
    request: 検索リクエスト

  Returns:
    マッチした商品リスト
  """
  try:
    products = delivery_service.search_products(
      ingredient_name=request.ingredient_name,
      services=request.services,
      max_results=request.max_results
    )

    return {
      "status": "ok",
      "data": {
        "products": [
          delivery_service._product_to_dict(p) for p in products
        ],
        "count": len(products),
        "query": {
          "ingredient_name": request.ingredient_name,
          "services": request.services,
          "max_results": request.max_results
        }
      }
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/cart")
async def add_to_cart(request: AddToCartRequest):
  """
  カートに追加

  Args:
    request: カート追加リクエスト

  Returns:
    更新後のカート内容
  """
  try:
    result = delivery_service.add_to_cart(
      service=request.service,
      product_id=request.product_id,
      quantity=request.quantity
    )
    return {
      "status": "ok",
      "data": result
    }
  except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/cart")
async def get_cart(
  service: DeliveryServiceType = Query(..., description="サービス")
):
  """
  カート内容取得

  Args:
    service: サービス種別

  Returns:
    カート内容
  """
  try:
    cart = delivery_service.get_cart(service)
    return {
      "status": "ok",
      "data": cart
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cart")
async def remove_from_cart(request: RemoveFromCartRequest):
  """
  カートから削除

  Args:
    request: カート削除リクエスト

  Returns:
    更新後のカート内容
  """
  try:
    result = delivery_service.remove_from_cart(
      service=request.service,
      product_id=request.product_id
    )
    return {
      "status": "ok",
      "data": result
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cart/clear")
async def clear_cart(
  service: DeliveryServiceType = Query(..., description="サービス")
):
  """
  カートクリア

  Args:
    service: サービス種別

  Returns:
    クリア結果
  """
  try:
    result = delivery_service.clear_cart(service)
    return {
      "status": "ok",
      "data": result
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout-url")
async def generate_checkout_url(
  service: DeliveryServiceType = Query(..., description="サービス")
):
  """
  注文ページURL生成

  Args:
    service: サービス種別

  Returns:
    注文ページURL
  """
  try:
    url = delivery_service.generate_checkout_url(service)
    return {
      "status": "ok",
      "data": {
        "service": service,
        "checkout_url": url,
        "message": "注文ページを開いてください"
      }
    }
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/price-compare")
async def compare_prices(
  ingredient_name: str = Query(..., description="食材名")
):
  """
  価格比較

  Args:
    ingredient_name: 食材名

  Returns:
    各サービスの価格比較結果
  """
  try:
    result = delivery_service.compare_prices(ingredient_name)
    return {
      "status": "ok",
      "data": result
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

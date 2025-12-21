"""
Shopping List API Router
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.core.database import get_session
from backend.services.shopping_list_service import ShoppingListService
from backend.models.shopping_list import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListRead,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListItemRead,
)
from backend.api.schemas import ApiResponse


router = APIRouter(prefix="/api/v1/shopping-lists", tags=["shopping-lists"])


def get_shopping_list_service(session: Session = Depends(get_session)):
    return ShoppingListService(session)


# ===========================================
# Shopping List Endpoints
# ===========================================
@router.get("", response_model=ApiResponse)
async def get_shopping_lists(
    include_completed: bool = False,
    page: int = 1,
    per_page: int = 20,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """買い物リスト一覧取得"""
    lists, total = service.get_lists(
        include_completed=include_completed,
        page=page,
        per_page=per_page,
    )

    return ApiResponse(
        status="ok",
        data={
            "items": [
                {
                    "id": sl.id,
                    "name": sl.name,
                    "notes": sl.notes,
                    "is_completed": sl.is_completed,
                    "created_at": sl.created_at.isoformat() if sl.created_at else None,
                    "updated_at": sl.updated_at.isoformat() if sl.updated_at else None,
                    "item_count": len(sl.items),
                    "checked_count": sum(1 for item in sl.items if item.is_checked),
                }
                for sl in lists
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    )


@router.get("/{list_id}", response_model=ApiResponse)
async def get_shopping_list(
    list_id: int,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """買い物リスト詳細取得"""
    shopping_list = service.get_list(list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    return ApiResponse(
        status="ok",
        data={
            "id": shopping_list.id,
            "name": shopping_list.name,
            "notes": shopping_list.notes,
            "is_completed": shopping_list.is_completed,
            "created_at": shopping_list.created_at.isoformat() if shopping_list.created_at else None,
            "updated_at": shopping_list.updated_at.isoformat() if shopping_list.updated_at else None,
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "amount": item.amount,
                    "unit": item.unit,
                    "category": item.category,
                    "note": item.note,
                    "is_checked": item.is_checked,
                    "recipe_id": item.recipe_id,
                    "recipe_name": item.recipe_name,  # レシピ名
                    "order": item.order,
                }
                for item in sorted(shopping_list.items, key=lambda x: x.order)
            ],
        },
    )


@router.post("", response_model=ApiResponse)
async def create_shopping_list(
    data: ShoppingListCreate,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """買い物リスト作成"""
    shopping_list = service.create_list(data)

    return ApiResponse(
        status="ok",
        data={
            "id": shopping_list.id,
            "name": shopping_list.name,
            "notes": shopping_list.notes,
            "is_completed": shopping_list.is_completed,
            "created_at": shopping_list.created_at.isoformat() if shopping_list.created_at else None,
        },
    )


@router.put("/{list_id}", response_model=ApiResponse)
async def update_shopping_list(
    list_id: int,
    data: ShoppingListUpdate,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """買い物リスト更新"""
    shopping_list = service.update_list(list_id, data)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    return ApiResponse(
        status="ok",
        data={
            "id": shopping_list.id,
            "name": shopping_list.name,
            "notes": shopping_list.notes,
            "is_completed": shopping_list.is_completed,
            "updated_at": shopping_list.updated_at.isoformat() if shopping_list.updated_at else None,
        },
    )


@router.delete("/{list_id}", response_model=ApiResponse)
async def delete_shopping_list(
    list_id: int,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """買い物リスト削除"""
    if not service.delete_list(list_id):
        raise HTTPException(status_code=404, detail="Shopping list not found")

    return ApiResponse(status="ok", data={"deleted": True})


# ===========================================
# Shopping List Item Endpoints
# ===========================================
@router.post("/{list_id}/items", response_model=ApiResponse)
async def add_item(
    list_id: int,
    data: ShoppingListItemCreate,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """アイテム追加"""
    item = service.add_item(list_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    return ApiResponse(
        status="ok",
        data={
            "id": item.id,
            "name": item.name,
            "amount": item.amount,
            "unit": item.unit,
            "category": item.category,
            "note": item.note,
            "is_checked": item.is_checked,
            "order": item.order,
        },
    )


@router.put("/{list_id}/items/{item_id}", response_model=ApiResponse)
async def update_item(
    list_id: int,
    item_id: int,
    data: ShoppingListItemUpdate,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """アイテム更新"""
    item = service.update_item(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return ApiResponse(
        status="ok",
        data={
            "id": item.id,
            "name": item.name,
            "amount": item.amount,
            "unit": item.unit,
            "category": item.category,
            "note": item.note,
            "is_checked": item.is_checked,
        },
    )


@router.post("/{list_id}/items/{item_id}/toggle", response_model=ApiResponse)
async def toggle_item(
    list_id: int,
    item_id: int,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """アイテムのチェック状態を切り替え"""
    item = service.toggle_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return ApiResponse(
        status="ok",
        data={
            "id": item.id,
            "is_checked": item.is_checked,
        },
    )


@router.delete("/{list_id}/items/{item_id}", response_model=ApiResponse)
async def delete_item(
    list_id: int,
    item_id: int,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """アイテム削除"""
    if not service.delete_item(item_id):
        raise HTTPException(status_code=404, detail="Item not found")

    return ApiResponse(status="ok", data={"deleted": True})


# ===========================================
# Recipe Integration Endpoints
# ===========================================
@router.post("/{list_id}/add-recipe/{recipe_id}", response_model=ApiResponse)
async def add_recipe_to_list(
    list_id: int,
    recipe_id: int,
    multiplier: float = 1.0,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """レシピの材料を買い物リストに追加"""
    items = service.add_recipe_ingredients(list_id, recipe_id, multiplier)

    return ApiResponse(
        status="ok",
        data={
            "added_count": len(items),
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "amount": item.amount,
                    "unit": item.unit,
                }
                for item in items
            ],
        },
    )


@router.post("/{list_id}/clear-checked", response_model=ApiResponse)
async def clear_checked_items(
    list_id: int,
    service: ShoppingListService = Depends(get_shopping_list_service),
):
    """チェック済みアイテムをクリア"""
    count = service.clear_checked_items(list_id)

    return ApiResponse(
        status="ok",
        data={"cleared_count": count},
    )

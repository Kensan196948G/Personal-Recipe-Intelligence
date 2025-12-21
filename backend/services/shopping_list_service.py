"""
Shopping List Service - Business logic for shopping list operations
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from backend.models.shopping_list import (
    ShoppingList,
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListItem,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
)
from backend.models.recipe import Recipe, Ingredient


class ShoppingListService:
    """買い物リストサービス"""

    def __init__(self, session: Session):
        self.session = session

    # ===========================================
    # Shopping List CRUD
    # ===========================================
    def get_lists(
        self,
        include_completed: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[List[ShoppingList], int]:
        """買い物リスト一覧取得"""
        query = select(ShoppingList)

        if not include_completed:
            query = query.where(ShoppingList.is_completed == False)

        # 総数取得
        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.exec(count_query).one()

        # ページネーション + 関連データの事前読み込み
        offset = (page - 1) * per_page
        query = (
            query
            .options(selectinload(ShoppingList.items))
            .order_by(ShoppingList.updated_at.desc())
            .offset(offset)
            .limit(per_page)
        )

        lists = self.session.exec(query).all()
        return list(lists), total

    def get_list(self, list_id: int) -> Optional[ShoppingList]:
        """買い物リスト詳細取得"""
        query = (
            select(ShoppingList)
            .where(ShoppingList.id == list_id)
            .options(selectinload(ShoppingList.items))
        )
        return self.session.exec(query).first()

    def create_list(self, data: ShoppingListCreate) -> ShoppingList:
        """買い物リスト作成"""
        shopping_list = ShoppingList(
            name=data.name,
            notes=data.notes,
        )
        self.session.add(shopping_list)
        self.session.commit()
        self.session.refresh(shopping_list)
        return shopping_list

    def update_list(self, list_id: int, data: ShoppingListUpdate) -> Optional[ShoppingList]:
        """買い物リスト更新"""
        shopping_list = self.get_list(list_id)
        if not shopping_list:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(shopping_list, key, value)

        shopping_list.updated_at = datetime.now()
        self.session.add(shopping_list)
        self.session.commit()
        self.session.refresh(shopping_list)
        return shopping_list

    def delete_list(self, list_id: int) -> bool:
        """買い物リスト削除"""
        shopping_list = self.session.get(ShoppingList, list_id)
        if not shopping_list:
            return False

        # アイテムも一緒に削除
        for item in shopping_list.items:
            self.session.delete(item)

        self.session.delete(shopping_list)
        self.session.commit()
        return True

    # ===========================================
    # Shopping List Item CRUD
    # ===========================================
    def add_item(self, list_id: int, data: ShoppingListItemCreate) -> Optional[ShoppingListItem]:
        """買い物リストにアイテム追加"""
        shopping_list = self.session.get(ShoppingList, list_id)
        if not shopping_list:
            return None

        # 最大order取得
        max_order_query = select(func.max(ShoppingListItem.order)).where(
            ShoppingListItem.shopping_list_id == list_id
        )
        max_order = self.session.exec(max_order_query).one() or 0

        item = ShoppingListItem(
            shopping_list_id=list_id,
            name=data.name,
            amount=data.amount,
            unit=data.unit,
            category=data.category,
            note=data.note,
            recipe_id=data.recipe_id,
            order=max_order + 1,
        )
        self.session.add(item)

        # リストの更新日時も更新
        shopping_list.updated_at = datetime.now()
        self.session.add(shopping_list)

        self.session.commit()
        self.session.refresh(item)
        return item

    def update_item(self, item_id: int, data: ShoppingListItemUpdate) -> Optional[ShoppingListItem]:
        """アイテム更新"""
        item = self.session.get(ShoppingListItem, item_id)
        if not item:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def toggle_item(self, item_id: int) -> Optional[ShoppingListItem]:
        """アイテムのチェック状態を切り替え"""
        item = self.session.get(ShoppingListItem, item_id)
        if not item:
            return None

        item.is_checked = not item.is_checked
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete_item(self, item_id: int) -> bool:
        """アイテム削除"""
        item = self.session.get(ShoppingListItem, item_id)
        if not item:
            return False

        self.session.delete(item)
        self.session.commit()
        return True

    # ===========================================
    # Recipe Integration
    # ===========================================
    def add_recipe_ingredients(
        self,
        list_id: int,
        recipe_id: int,
        multiplier: float = 1.0,
    ) -> List[ShoppingListItem]:
        """レシピの材料を買い物リストに追加"""
        shopping_list = self.session.get(ShoppingList, list_id)
        if not shopping_list:
            return []

        # レシピと材料を取得
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe:
            return []

        # 材料を取得
        ingredients_query = select(Ingredient).where(Ingredient.recipe_id == recipe_id)
        ingredients = self.session.exec(ingredients_query).all()

        # 最大order取得
        max_order_query = select(func.max(ShoppingListItem.order)).where(
            ShoppingListItem.shopping_list_id == list_id
        )
        max_order = self.session.exec(max_order_query).one() or 0

        added_items = []
        recipe_name = recipe.title  # レシピ名を取得
        for i, ingredient in enumerate(ingredients):
            amount = ingredient.amount * multiplier if ingredient.amount else None

            item = ShoppingListItem(
                shopping_list_id=list_id,
                name=ingredient.name,
                amount=amount,
                unit=ingredient.unit,
                note=ingredient.note,
                recipe_id=recipe_id,
                recipe_name=recipe_name,  # レシピ名を保存
                order=max_order + i + 1,
            )
            self.session.add(item)
            added_items.append(item)

        # リストの更新日時も更新
        shopping_list.updated_at = datetime.now()
        self.session.add(shopping_list)

        self.session.commit()

        for item in added_items:
            self.session.refresh(item)

        return added_items

    def clear_checked_items(self, list_id: int) -> int:
        """チェック済みアイテムをクリア"""
        query = select(ShoppingListItem).where(
            ShoppingListItem.shopping_list_id == list_id,
            ShoppingListItem.is_checked == True,
        )
        items = self.session.exec(query).all()

        count = len(items)
        for item in items:
            self.session.delete(item)

        self.session.commit()
        return count

    def get_item_count(self, list_id: int) -> dict:
        """アイテム数を取得（総数とチェック済み数）"""
        total_query = select(func.count()).where(
            ShoppingListItem.shopping_list_id == list_id
        )
        checked_query = select(func.count()).where(
            ShoppingListItem.shopping_list_id == list_id,
            ShoppingListItem.is_checked == True,
        )

        total = self.session.exec(total_query).one()
        checked = self.session.exec(checked_query).one()

        return {"total": total, "checked": checked}

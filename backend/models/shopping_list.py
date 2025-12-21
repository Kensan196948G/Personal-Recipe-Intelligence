"""
Shopping List Models - SQLModel definitions
"""

from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, Relationship, SQLModel


class ShoppingListBase(SQLModel):
    """買い物リスト基本情報"""

    name: str = Field(default="買い物リスト")
    notes: Optional[str] = None


class ShoppingList(ShoppingListBase, table=True):
    """買い物リストテーブル"""

    __tablename__ = "shopping_list"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_completed: bool = Field(default=False)

    items: List["ShoppingListItem"] = Relationship(back_populates="shopping_list")


class ShoppingListCreate(ShoppingListBase):
    """買い物リスト作成用"""

    pass


class ShoppingListUpdate(SQLModel):
    """買い物リスト更新用"""

    name: Optional[str] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = None


class ShoppingListItemBase(SQLModel):
    """買い物リストアイテム基本情報"""

    name: str = Field(index=True)
    amount: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None  # 野菜, 肉, 調味料 etc.
    note: Optional[str] = None


class ShoppingListItem(ShoppingListItemBase, table=True):
    """買い物リストアイテムテーブル"""

    __tablename__ = "shopping_list_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    shopping_list_id: int = Field(foreign_key="shopping_list.id")
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id")
    recipe_name: Optional[str] = Field(default=None)  # レシピ名（表示用）
    is_checked: bool = Field(default=False)
    order: int = Field(default=0)

    shopping_list: ShoppingList = Relationship(back_populates="items")


class ShoppingListItemCreate(ShoppingListItemBase):
    """買い物リストアイテム作成用"""

    recipe_id: Optional[int] = None
    recipe_name: Optional[str] = None


class ShoppingListItemUpdate(SQLModel):
    """買い物リストアイテム更新用"""

    name: Optional[str] = None
    amount: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    note: Optional[str] = None
    is_checked: Optional[bool] = None


# Response models
class ShoppingListItemRead(ShoppingListItemBase):
    """買い物リストアイテム読み取り用"""

    id: int
    shopping_list_id: int
    recipe_id: Optional[int]
    recipe_name: Optional[str]  # レシピ名
    is_checked: bool
    order: int


class ShoppingListRead(ShoppingListBase):
    """買い物リスト読み取り用"""

    id: int
    created_at: datetime
    updated_at: datetime
    is_completed: bool
    items: List[ShoppingListItemRead] = []

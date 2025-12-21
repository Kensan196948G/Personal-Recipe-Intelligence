"""
API Schemas - Pydantic models for request/response
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ===========================================
# Response Wrapper
# ===========================================
class ApiResponse(BaseModel):
    """標準APIレスポンス"""

    status: str = "ok"
    data: Optional[dict | list] = None
    error: Optional[dict] = None


class ErrorDetail(BaseModel):
    """エラー詳細"""

    code: str
    message: str
    details: Optional[dict] = None


# ===========================================
# Ingredient Schemas
# ===========================================
class IngredientCreate(BaseModel):
    """材料作成用"""

    name: str = Field(..., min_length=1, max_length=200)
    name_normalized: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    note: Optional[str] = Field(None, max_length=500)
    order: int = Field(default=0, ge=0)


class IngredientRead(BaseModel):
    """材料読み取り用"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_normalized: str
    amount: Optional[float]
    unit: Optional[str]
    note: Optional[str]
    order: int


class IngredientUpdate(BaseModel):
    """材料更新用"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    name_normalized: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    note: Optional[str] = Field(None, max_length=500)
    order: Optional[int] = Field(None, ge=0)


# ===========================================
# Step Schemas
# ===========================================
class StepCreate(BaseModel):
    """調理手順作成用"""

    description: str = Field(..., min_length=1, max_length=2000)
    order: int = Field(..., ge=1)


class StepRead(BaseModel):
    """調理手順読み取り用"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    order: int


class StepUpdate(BaseModel):
    """調理手順更新用"""

    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    order: Optional[int] = Field(None, ge=1)


# ===========================================
# Tag Schemas
# ===========================================
class TagCreate(BaseModel):
    """タグ作成用"""

    name: str = Field(..., min_length=1, max_length=100)


class TagRead(BaseModel):
    """タグ読み取り用"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# ===========================================
# Recipe Schemas
# ===========================================
class RecipeCreate(BaseModel):
    """レシピ作成用"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    servings: Optional[int] = Field(None, ge=1, le=100)
    prep_time_minutes: Optional[int] = Field(None, ge=0, le=1440)
    cook_time_minutes: Optional[int] = Field(None, ge=0, le=1440)
    source_url: Optional[str] = Field(None, max_length=2000)
    source_type: str = Field(default="manual", pattern="^(manual|web|ocr)$")
    image_url: Optional[str] = Field(None, max_length=2000)  # 画像URL
    ingredients: list[IngredientCreate] = Field(default_factory=list)
    steps: list[StepCreate] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)


class RecipeRead(BaseModel):
    """レシピ読み取り用"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    servings: Optional[int]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    source_url: Optional[str]
    source_type: str
    image_url: Optional[str]  # 画像URL
    image_path: Optional[str]  # ローカル保存パス
    image_status: Optional[str] = None  # 画像取得状態: "ok", "画像ソースなし", "API制限到達。後日再取得"
    created_at: datetime
    updated_at: datetime
    ingredients: list[IngredientRead] = Field(default_factory=list)
    steps: list[StepRead] = Field(default_factory=list)
    tags: list[TagRead] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    """レシピ更新用"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    servings: Optional[int] = Field(None, ge=1, le=100)
    prep_time_minutes: Optional[int] = Field(None, ge=0, le=1440)
    cook_time_minutes: Optional[int] = Field(None, ge=0, le=1440)
    source_url: Optional[str] = Field(None, max_length=2000)
    source_type: Optional[str] = Field(None, pattern="^(manual|web|ocr)$")
    image_url: Optional[str] = Field(None, max_length=2000)  # 画像URL


class RecipeListItem(BaseModel):
    """レシピ一覧アイテム"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    servings: Optional[int]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    source_type: str
    image_url: Optional[str]  # 画像URL
    image_path: Optional[str]  # ローカル保存パス
    image_status: Optional[str] = None  # 画像取得状態: "ok", "画像ソースなし", "API制限到達。後日再取得"
    created_at: datetime
    tag_count: int = 0
    ingredient_count: int = 0


# ===========================================
# Pagination
# ===========================================
class PaginationParams(BaseModel):
    """ページネーションパラメータ"""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """ページネーション付きレスポンス"""

    items: list
    total: int
    page: int
    per_page: int
    total_pages: int

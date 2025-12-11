"""
Recipe Models - SQLModel definitions
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class RecipeBase(SQLModel):
    """レシピ基本情報"""

    title: str = Field(index=True)
    description: Optional[str] = None
    servings: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    source_url: Optional[str] = None
    source_type: str = Field(default="manual")  # manual, web, ocr


class Recipe(RecipeBase, table=True):
    """レシピテーブル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    ingredients: list["Ingredient"] = Relationship(back_populates="recipe")
    steps: list["Step"] = Relationship(back_populates="recipe")
    tags: list["RecipeTag"] = Relationship(back_populates="recipe")


class RecipeCreate(RecipeBase):
    """レシピ作成用"""

    pass


class RecipeRead(RecipeBase):
    """レシピ読み取り用"""

    id: int
    created_at: datetime
    updated_at: datetime


class IngredientBase(SQLModel):
    """材料基本情報"""

    name: str = Field(index=True)
    name_normalized: str = Field(index=True)
    amount: Optional[float] = None
    unit: Optional[str] = None
    note: Optional[str] = None


class Ingredient(IngredientBase, table=True):
    """材料テーブル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id")
    order: int = Field(default=0)

    recipe: Recipe = Relationship(back_populates="ingredients")


class StepBase(SQLModel):
    """調理手順基本情報"""

    description: str
    order: int


class Step(StepBase, table=True):
    """調理手順テーブル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id")

    recipe: Recipe = Relationship(back_populates="steps")


class Tag(SQLModel, table=True):
    """タグテーブル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)


class RecipeTag(SQLModel, table=True):
    """レシピ-タグ関連テーブル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id")
    tag_id: int = Field(foreign_key="tag.id")

    recipe: Recipe = Relationship(back_populates="tags")


class Source(SQLModel, table=True):
    """取得元情報テーブル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    url_pattern: Optional[str] = None
    scraper_config: Optional[str] = None  # JSON string

# モデル定義 (Model Definitions)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) の SQLModel モデル定義を記述する。

## 2. モデル一覧

| モデル | テーブル名 | 説明 |
|--------|-----------|------|
| Recipe | recipe | レシピ |
| Ingredient | ingredient | 材料マスタ |
| RecipeIngredient | recipe_ingredient | レシピ材料 |
| RecipeStep | recipe_step | 調理手順 |
| Tag | tag | タグ |
| RecipeTag | recipe_tag | レシピタグ |
| RecipeSource | recipe_source | レシピソース |
| TranslationCache | translation_cache | 翻訳キャッシュ |

## 3. モデル詳細

### 3.1 Recipe

```python
# models/recipe.py
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class RecipeBase(SQLModel):
    title: str = Field(max_length=200, index=True)
    title_original: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    servings: Optional[int] = Field(default=None, ge=1, le=100)
    prep_time_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    cook_time_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    image_path: Optional[str] = Field(default=None, max_length=500)
    language: str = Field(default="ja", max_length=10)

class Recipe(RecipeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = Field(default=False, index=True)

    # リレーション
    ingredients: List["RecipeIngredient"] = Relationship(back_populates="recipe")
    steps: List["RecipeStep"] = Relationship(back_populates="recipe")
    tags: List["Tag"] = Relationship(back_populates="recipes", link_model=RecipeTag)
    source: Optional["RecipeSource"] = Relationship(back_populates="recipe")

class RecipeCreate(RecipeBase):
    ingredients: List["RecipeIngredientCreate"]
    steps: List["RecipeStepCreate"]
    tag_ids: Optional[List[int]] = []

class RecipeUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    servings: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None

class RecipeRead(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    ingredients: List["RecipeIngredientRead"] = []
    steps: List["RecipeStepRead"] = []
    tags: List["TagRead"] = []
```

### 3.2 Ingredient

```python
# models/ingredient.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class IngredientBase(SQLModel):
    name: str = Field(max_length=100)
    name_normalized: str = Field(max_length=100, index=True, unique=True)
    category: Optional[str] = Field(default=None, max_length=50)

class Ingredient(IngredientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.3 RecipeIngredient

```python
# models/recipe.py (続き)
class RecipeIngredientBase(SQLModel):
    name: str = Field(max_length=100)
    amount: Optional[float] = None
    unit: Optional[str] = Field(default=None, max_length=20)
    note: Optional[str] = Field(default=None, max_length=200)
    order_index: int = Field(default=0)

class RecipeIngredient(RecipeIngredientBase, table=True):
    __tablename__ = "recipe_ingredient"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id", index=True)
    ingredient_id: Optional[int] = Field(default=None, foreign_key="ingredient.id")

    # リレーション
    recipe: Optional["Recipe"] = Relationship(back_populates="ingredients")

class RecipeIngredientCreate(RecipeIngredientBase):
    pass

class RecipeIngredientRead(RecipeIngredientBase):
    id: int
```

### 3.4 RecipeStep

```python
# models/recipe.py (続き)
class RecipeStepBase(SQLModel):
    step_number: int = Field(ge=1)
    description: str = Field(max_length=1000)
    image_path: Optional[str] = Field(default=None, max_length=500)

class RecipeStep(RecipeStepBase, table=True):
    __tablename__ = "recipe_step"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id", index=True)

    # リレーション
    recipe: Optional["Recipe"] = Relationship(back_populates="steps")

class RecipeStepCreate(SQLModel):
    description: str

class RecipeStepRead(RecipeStepBase):
    id: int
```

### 3.5 Tag

```python
# models/tag.py
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class TagBase(SQLModel):
    name: str = Field(max_length=50, index=True, unique=True)
    category: Optional[str] = Field(default=None, max_length=50)
    color: str = Field(default="#808080", max_length=7)

class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # リレーション
    recipes: List["Recipe"] = Relationship(back_populates="tags", link_model=RecipeTag)

class TagCreate(TagBase):
    pass

class TagRead(TagBase):
    id: int
```

### 3.6 RecipeTag

```python
# models/recipe.py (続き)
class RecipeTag(SQLModel, table=True):
    __tablename__ = "recipe_tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id", index=True)
    tag_id: int = Field(foreign_key="tag.id", index=True)
```

### 3.7 RecipeSource

```python
# models/source.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class SourceType(str, Enum):
    MANUAL = "manual"
    SCRAPE = "scrape"
    OCR = "ocr"

class RecipeSourceBase(SQLModel):
    source_type: SourceType
    source_url: Optional[str] = Field(default=None, max_length=2000)
    source_site: Optional[str] = Field(default=None, max_length=100)

class RecipeSource(RecipeSourceBase, table=True):
    __tablename__ = "recipe_source"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id", unique=True)
    scraped_at: Optional[datetime] = None

    # リレーション
    recipe: Optional["Recipe"] = Relationship(back_populates="source")
```

### 3.8 TranslationCache

```python
# models/translation_cache.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class TranslationCache(SQLModel, table=True):
    __tablename__ = "translation_cache"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_text_hash: str = Field(max_length=64, index=True)
    source_text: str
    translated_text: str
    source_lang: str = Field(max_length=10)
    target_lang: str = Field(max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
```

## 4. データベース接続

```python
# core/database.py
from sqlmodel import SQLModel, create_engine, Session
from backend.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False}  # SQLite用
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## 5. モデルの使用例

### 5.1 レシピ作成

```python
from sqlmodel import Session
from backend.models.recipe import Recipe, RecipeIngredient, RecipeStep

def create_recipe(session: Session):
    recipe = Recipe(
        title="カレーライス",
        description="家庭の定番料理",
        servings=4,
        cook_time_minutes=30
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    # 材料追加
    ingredient = RecipeIngredient(
        recipe_id=recipe.id,
        name="たまねぎ",
        amount=2,
        unit="個",
        order_index=1
    )
    session.add(ingredient)

    # 手順追加
    step = RecipeStep(
        recipe_id=recipe.id,
        step_number=1,
        description="たまねぎを薄切りにする"
    )
    session.add(step)

    session.commit()
    return recipe
```

### 5.2 レシピ検索

```python
from sqlmodel import Session, select
from backend.models.recipe import Recipe

def search_recipes(session: Session, keyword: str):
    statement = select(Recipe).where(
        Recipe.is_deleted == False,
        Recipe.title.contains(keyword)
    )
    return session.exec(statement).all()
```

## 6. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

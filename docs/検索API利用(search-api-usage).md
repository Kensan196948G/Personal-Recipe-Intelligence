# Search API Usage Guide

Personal Recipe Intelligence の検索機能の使用方法を説明します。

## 概要

検索機能は以下の種類をサポートしています:

1. **Fuzzy Search (あいまい検索)** - レシピタイトルの類似検索
2. **Ingredient Search (材料検索)** - 材料名による検索
3. **Combined Search (複合検索)** - タイトルと材料の組み合わせ検索
4. **Advanced Search (高度な検索)** - タグも含めた多条件検索

## 基本的な使い方

### 1. Fuzzy Search (あいまい検索)

レシピタイトルをあいまいに検索します。日本語にも対応しています。

```python
from sqlmodel import Session
from backend.services.recipe_service import RecipeService

# セッションの取得
session = Session(engine)
service = RecipeService(session)

# あいまい検索
results = service.fuzzy_search("カレー", limit=10)

for result in results:
  print(f"タイトル: {result.recipe.title}")
  print(f"スコア: {result.score}")
  print(f"マッチタイプ: {result.match_type}")
  print("---")
```

#### スコアリング

- **1.0**: 完全一致
- **0.9**: タイトルにクエリが含まれる
- **0.85**: クエリにタイトルが含まれる
- **0.6~0.85**: 類似度に基づくスコア

#### カスタム閾値

```python
# スコア 0.8 以上のみを返す
results = service.fuzzy_search("カレー", threshold=0.8)
```

### 2. Ingredient Search (材料検索)

材料名で検索します。部分一致もサポートしています。

```python
# いずれかの材料を含むレシピを検索 (OR検索)
results = service.search_by_ingredients(
  ingredient_names=["玉ねぎ", "にんじん"],
  match_all=False
)

# すべての材料を含むレシピを検索 (AND検索)
results = service.search_by_ingredients(
  ingredient_names=["玉ねぎ", "にんじん"],
  match_all=True
)

for result in results:
  print(f"タイトル: {result.recipe.title}")
  print(f"マッチした材料: {', '.join(result.matched_terms)}")
  print(f"スコア: {result.score}")
  print("---")
```

#### スコアリング

- **match_all=True**: すべてマッチした場合 1.0、そうでない場合は結果に含まれない
- **match_all=False**: マッチした材料数 ÷ 検索材料数

### 3. Combined Search (複合検索)

タイトルと材料の両方で検索します。

```python
# タイトルと材料の複合検索
results = service.combined_search(
  title_query="カレー",
  ingredient_names=["じゃがいも", "にんじん"],
  limit=20
)

for result in results:
  print(f"タイトル: {result.recipe.title}")
  print(f"スコア: {result.score}")
  print(f"マッチ項目: {', '.join(result.matched_terms)}")
  print("---")
```

#### スコアリング

複合スコアは以下の重み付けで計算されます:
- **タイトルマッチ**: 60%
- **材料マッチ**: 40%

### 4. Advanced Search (高度な検索)

タイトル、材料、タグを組み合わせた検索が可能です。

```python
# 多条件検索
results = service.advanced_search(
  query="カレー",
  ingredients=["じゃがいも"],
  tags=["和食", "簡単"],
  limit=20
)

for result in results:
  print(f"タイトル: {result.recipe.title}")
  print(f"スコア: {result.score}")
  print(f"タグ: {result.recipe.tags}")
  print("---")
```

#### スコアリング

- **タイトル + 材料**: 上記の複合検索と同じ
- **タグマッチ**: 30% の追加スコア

## API エンドポイント例

FastAPI を使用した実装例:

```python
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.services.recipe_service import RecipeService
from backend.database import get_session

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/fuzzy")
def fuzzy_search(
  query: str = Query(..., description="検索クエリ"),
  limit: int = Query(20, ge=1, le=100),
  threshold: float = Query(0.6, ge=0.0, le=1.0),
  session: Session = Depends(get_session),
):
  """レシピタイトルのあいまい検索"""
  service = RecipeService(session)
  results = service.fuzzy_search(query, limit, threshold)

  return {
    "status": "ok",
    "data": [
      {
        "recipe": result.recipe,
        "score": result.score,
        "match_type": result.match_type,
      }
      for result in results
    ],
    "error": None,
  }


@router.get("/ingredients")
def search_by_ingredients(
  ingredients: list[str] = Query(..., description="材料名リスト"),
  match_all: bool = Query(False, description="すべての材料を含む"),
  limit: int = Query(20, ge=1, le=100),
  session: Session = Depends(get_session),
):
  """材料による検索"""
  service = RecipeService(session)
  results = service.search_by_ingredients(ingredients, match_all, limit)

  return {
    "status": "ok",
    "data": [
      {
        "recipe": result.recipe,
        "score": result.score,
        "matched_ingredients": result.matched_terms,
      }
      for result in results
    ],
    "error": None,
  }


@router.get("/combined")
def combined_search(
  title: str = Query(None, description="タイトル検索クエリ"),
  ingredients: list[str] = Query(None, description="材料名リスト"),
  limit: int = Query(20, ge=1, le=100),
  session: Session = Depends(get_session),
):
  """タイトルと材料の複合検索"""
  service = RecipeService(session)
  results = service.combined_search(title, ingredients, limit)

  return {
    "status": "ok",
    "data": [
      {
        "recipe": result.recipe,
        "score": result.score,
        "matched_terms": result.matched_terms,
      }
      for result in results
    ],
    "error": None,
  }


@router.get("/advanced")
def advanced_search(
  query: str = Query(None, description="検索クエリ"),
  ingredients: list[str] = Query(None, description="材料名リスト"),
  tags: list[str] = Query(None, description="タグリスト"),
  limit: int = Query(20, ge=1, le=100),
  session: Session = Depends(get_session),
):
  """高度な多条件検索"""
  service = RecipeService(session)
  results = service.advanced_search(query, ingredients, tags, limit)

  return {
    "status": "ok",
    "data": [
      {
        "recipe": result.recipe,
        "score": result.score,
        "matched_terms": result.matched_terms,
        "match_type": result.match_type,
      }
      for result in results
    ],
    "error": None,
  }
```

## 使用例

### cURL

```bash
# あいまい検索
curl "http://localhost:8000/api/v1/search/fuzzy?query=カレー&limit=10"

# 材料検索 (OR)
curl "http://localhost:8000/api/v1/search/ingredients?ingredients=玉ねぎ&ingredients=にんじん&match_all=false"

# 材料検索 (AND)
curl "http://localhost:8000/api/v1/search/ingredients?ingredients=玉ねぎ&ingredients=にんじん&match_all=true"

# 複合検索
curl "http://localhost:8000/api/v1/search/combined?title=カレー&ingredients=じゃがいも"

# 高度な検索
curl "http://localhost:8000/api/v1/search/advanced?query=カレー&ingredients=じゃがいも&tags=簡単"
```

### JavaScript (fetch)

```javascript
// あいまい検索
async function fuzzySearch(query) {
  const response = await fetch(
    `/api/v1/search/fuzzy?query=${encodeURIComponent(query)}&limit=20`
  );
  const data = await response.json();
  return data.data;
}

// 材料検索
async function searchByIngredients(ingredients, matchAll = false) {
  const params = new URLSearchParams();
  ingredients.forEach(ing => params.append('ingredients', ing));
  params.append('match_all', matchAll);

  const response = await fetch(`/api/v1/search/ingredients?${params}`);
  const data = await response.json();
  return data.data;
}

// 複合検索
async function combinedSearch(title, ingredients) {
  const params = new URLSearchParams();
  if (title) params.append('title', title);
  if (ingredients) {
    ingredients.forEach(ing => params.append('ingredients', ing));
  }

  const response = await fetch(`/api/v1/search/combined?${params}`);
  const data = await response.json();
  return data.data;
}

// 使用例
const results = await fuzzySearch('カレー');
console.log(results);
```

## パフォーマンス最適化

### インデックスの追加

検索パフォーマンスを向上させるため、以下のインデックスを推奨します:

```python
# models/recipe.py
from sqlmodel import Field, SQLModel

class Recipe(SQLModel, table=True):
  id: int = Field(primary_key=True)
  title: str = Field(index=True)  # タイトルにインデックス
  tags: str = Field(index=True, nullable=True)  # タグにインデックス
  # ...

class Ingredient(SQLModel, table=True):
  id: int = Field(primary_key=True)
  recipe_id: int = Field(foreign_key="recipe.id", index=True)
  name: str = Field(index=True)  # 材料名にインデックス
  # ...
```

### キャッシュの活用

頻繁に検索される内容はキャッシュすることを推奨します:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_fuzzy_search(query: str, limit: int = 20):
  # キャッシュされた検索
  pass
```

## トラブルシューティング

### 日本語検索が正しく動作しない

- データベースの文字コードが UTF-8 であることを確認してください
- SQLite の場合、`PRAGMA encoding = "UTF-8";` を設定してください

### 検索結果が多すぎる

- `threshold` パラメータを高く設定してください (例: 0.8)
- `limit` パラメータを調整してください

### 検索結果が少なすぎる

- `threshold` パラメータを低く設定してください (例: 0.5)
- 部分一致を利用してください

## まとめ

Personal Recipe Intelligence の検索機能は、柔軟で高性能な検索を提供します。
用途に応じて適切な検索メソッドを選択し、スコアリングやフィルタリングを活用してください。

# Backend Services

Personal Recipe Intelligence のバックエンドサービス層

## 概要

このディレクトリには、ビジネスロジックと検索機能を提供するサービスクラスが含まれています。

## ファイル構成

```
backend/services/
├── __init__.py              # サービスモジュールのエクスポート
├── recipe_service.py        # レシピCRUD操作と検索インターフェース
├── search_service.py        # 検索エンジンの実装
└── README.md               # このファイル
```

## サービス一覧

### RecipeService

レシピの CRUD 操作と検索機能を提供します。

**主な機能:**
- レシピの作成、取得、更新、削除
- 材料の管理
- 各種検索メソッドのインターフェース

**使用例:**

```python
from sqlmodel import Session
from backend.services import RecipeService

session = Session(engine)
service = RecipeService(session)

# レシピ作成
recipe = service.create_recipe({
  "title": "カレーライス",
  "description": "基本的なカレーのレシピ",
  "tags": "和食,簡単"
})

# あいまい検索
results = service.fuzzy_search("カレー")

# 材料検索
results = service.search_by_ingredients(["玉ねぎ", "にんじん"])
```

### SearchService

高度な検索機能を提供します。

**主な機能:**
- Fuzzy Search (あいまい検索)
- Ingredient Search (材料検索)
- Combined Search (複合検索)
- Advanced Search (高度な検索)

**使用例:**

```python
from sqlmodel import Session
from backend.services import SearchService

session = Session(engine)
search_service = SearchService(session)

# あいまい検索
results = search_service.fuzzy_search("カレー", limit=10, threshold=0.7)

# 材料検索 (AND条件)
results = search_service.search_by_ingredients(
  ["玉ねぎ", "にんじん"],
  match_all=True
)

# 複合検索
results = search_service.combined_search(
  title_query="カレー",
  ingredient_names=["じゃがいも"]
)

# 高度な検索
results = search_service.advanced_search(
  query="カレー",
  ingredients=["じゃがいも"],
  tags=["簡単"]
)
```

## SearchResult データクラス

検索結果は `SearchResult` データクラスで返されます:

```python
@dataclass
class SearchResult:
  recipe: Recipe              # レシピオブジェクト
  score: float               # 関連度スコア (0.0 ~ 1.0)
  match_type: str            # マッチタイプ ('title', 'ingredient', 'combined')
  matched_terms: List[str]   # マッチした検索語句
```

## 検索アルゴリズム

### Fuzzy Search

1. **正規化**: クエリとタイトルを正規化 (小文字化、空白除去)
2. **スコアリング**:
   - 完全一致: 1.0
   - タイトルにクエリ含む: 0.9
   - クエリにタイトル含む: 0.85
   - 類似度 (SequenceMatcher): 0.0 ~ 1.0

### Ingredient Search

1. **正規化**: 材料名を正規化
2. **マッチング**: 完全一致または部分一致
3. **スコアリング**:
   - match_all=True: すべてマッチで 1.0
   - match_all=False: マッチ数 ÷ 検索材料数

### Combined Search

1. タイトル検索と材料検索を並行実行
2. スコアを重み付けして合算:
   - タイトル: 60%
   - 材料: 40%
3. 合算スコアでソート

### Advanced Search

1. タイトルと材料の複合検索を実行
2. タグでフィルタリング
3. タグマッチのスコアを追加 (30%)
4. 最終スコアでソート

## パフォーマンス考慮事項

### データベースクエリ

現在の実装では、全レシピを取得してメモリ内で検索しています。
レシピ数が多い場合は、以下の最適化を検討してください:

1. **データベースレベルの検索**
   - Full-Text Search (FTS) の使用
   - LIKE クエリの活用

2. **インデックス最適化**
   - `recipe.title` にインデックス
   - `ingredient.name` にインデックス

3. **キャッシュ**
   - 検索結果のキャッシュ
   - 頻繁に検索される内容の事前計算

### 推奨される改善

**SQLite FTS5 の使用:**

```python
# FTS5 仮想テーブルの作成
CREATE VIRTUAL TABLE recipe_fts USING fts5(
  title,
  content=recipe,
  content_rowid=id
);

# FTS5 を使用した検索
SELECT * FROM recipe_fts WHERE recipe_fts MATCH '検索語';
```

**PostgreSQL の場合:**

```python
# tsvector と GIN インデックスの使用
CREATE INDEX recipe_title_idx ON recipe USING GIN(to_tsvector('japanese', title));

# 全文検索
SELECT * FROM recipe WHERE to_tsvector('japanese', title) @@ to_tsquery('japanese', '検索語');
```

## テスト

テストは `/tests/backend/test_search_service.py` にあります:

```bash
# テスト実行
pytest tests/backend/test_search_service.py

# カバレッジ付き実行
pytest --cov=backend.services tests/backend/test_search_service.py
```

## エラーハンドリング

サービス層では、以下のエラーハンドリングを行います:

1. **空のクエリ**: 空の結果リストを返す
2. **存在しないレシピ**: `None` を返す (get系) または `False` を返す (delete系)
3. **データベースエラー**: 例外を上位レイヤーに伝播

## ロギング

今後の実装で、以下のログを追加予定:

```python
import logging

logger = logging.getLogger(__name__)

def fuzzy_search(self, query: str, ...):
  logger.info(f"Fuzzy search: query='{query}', limit={limit}")
  results = ...
  logger.info(f"Found {len(results)} results")
  return results
```

## セキュリティ

- **入力検証**: すべての入力は Pydantic でバリデーション
- **SQLインジェクション対策**: SQLModel の ORM を使用
- **機密データマスキング**: ログに機密データを出力しない

## 今後の拡張

1. **全文検索エンジンの統合**
   - Elasticsearch
   - MeiliSearch

2. **機械学習ベースの検索**
   - 埋め込みベクトルによる類似検索
   - BERT などの言語モデル活用

3. **検索履歴と学習**
   - ユーザーの検索履歴を記録
   - 人気のレシピをスコアリングに反映

4. **多言語対応**
   - 英語・日本語以外の言語サポート
   - 言語ごとの正規化処理

## ライセンス

MIT License

## 貢献

バグ報告や機能追加の提案は Issue にてお願いします。

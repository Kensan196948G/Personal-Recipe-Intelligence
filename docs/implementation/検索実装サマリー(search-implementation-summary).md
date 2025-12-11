# Search Implementation Summary

Personal Recipe Intelligence の検索機能実装の完全ガイド

## 実装ファイル一覧

### コアファイル

1. **backend/services/search_service.py**
   - 検索エンジンのコア実装
   - Fuzzy search, ingredient search, combined search, advanced search
   - スコアリングアルゴリズム
   - 日本語テキスト対応

2. **backend/services/recipe_service_new.py**
   - RecipeService の拡張版
   - CRUD 操作 + 検索メソッド
   - search_by_ingredients(), fuzzy_search() の実装

### ドキュメント

3. **docs/search-api-usage.md**
   - 検索 API の使用方法
   - API エンドポイント例
   - cURL, JavaScript の使用例

4. **backend/services/README.md**
   - サービス層の説明
   - アーキテクチャ解説
   - パフォーマンス最適化のヒント

### テスト・デモ

5. **tests/backend/test_search_service.py**
   - 包括的なテストスイート
   - 15+ テストケース
   - すべての検索機能をカバー

6. **examples/search_demo.py**
   - インタラクティブなデモスクリプト
   - サンプルデータ付き
   - すぐに実行可能

## 主な機能

### 1. Fuzzy Search (あいまい検索)

```python
service.fuzzy_search("カレー", limit=10, threshold=0.7)
```

- 完全一致、部分一致、類似検索
- 日本語テキスト完全対応
- スコアリング: 0.0 ~ 1.0
- カスタマイズ可能な閾値

### 2. Ingredient Search (材料検索)

```python
# OR 検索
service.search_by_ingredients(["玉ねぎ", "にんじん"], match_all=False)

# AND 検索
service.search_by_ingredients(["玉ねぎ", "にんじん"], match_all=True)
```

- 複数材料の AND/OR 検索
- 部分一致サポート
- マッチした材料のリストを返す

### 3. Combined Search (複合検索)

```python
service.combined_search(
  title_query="カレー",
  ingredient_names=["じゃがいも"]
)
```

- タイトル + 材料の複合検索
- 重み付けスコアリング (title: 60%, ingredients: 40%)
- 高精度な検索結果

### 4. Advanced Search (高度な検索)

```python
service.advanced_search(
  query="カレー",
  ingredients=["じゃがいも"],
  tags=["簡単"]
)
```

- 多条件検索 (タイトル + 材料 + タグ)
- タグフィルタリング
- 総合スコアリング

## スコアリングアルゴリズム

### Fuzzy Search

| 条件 | スコア |
|------|--------|
| 完全一致 | 1.0 |
| タイトルにクエリ含む | 0.9 |
| クエリにタイトル含む | 0.85 |
| SequenceMatcher 類似度 | 0.0 ~ 1.0 |

### Ingredient Search

| 条件 | スコア |
|------|--------|
| match_all=True (すべてマッチ) | 1.0 |
| match_all=False | マッチ数 ÷ 検索材料数 |

### Combined Search

```
総合スコア = タイトルスコア × 0.6 + 材料スコア × 0.4
```

### Advanced Search

```
総合スコア = Combined スコア + タグスコア × 0.3
```

## データ構造

### SearchResult

```python
@dataclass
class SearchResult:
  recipe: Recipe              # レシピオブジェクト
  score: float               # 関連度スコア (0.0 ~ 1.0)
  match_type: str            # 'title', 'ingredient', 'combined', 'tag'
  matched_terms: List[str]   # マッチした語句
```

## 使用例

### Python

```python
from sqlmodel import Session
from backend.services import RecipeService

session = Session(engine)
service = RecipeService(session)

# あいまい検索
results = service.fuzzy_search("カレー")
for result in results:
    print(f"{result.recipe.title}: {result.score}")

# 材料検索
results = service.search_by_ingredients(["玉ねぎ", "にんじん"])
for result in results:
    print(f"{result.recipe.title}: {result.matched_terms}")
```

### FastAPI エンドポイント

```python
@router.get("/search/fuzzy")
def fuzzy_search(
  query: str,
  limit: int = 20,
  session: Session = Depends(get_session)
):
  service = RecipeService(session)
  results = service.fuzzy_search(query, limit)
  return {"status": "ok", "data": results}
```

### cURL

```bash
curl "http://localhost:8000/api/v1/search/fuzzy?query=カレー&limit=10"
```

## テスト実行

```bash
# 全テスト実行
pytest tests/backend/test_search_service.py

# カバレッジ付き
pytest --cov=backend.services tests/backend/test_search_service.py

# デモスクリプト実行
python examples/search_demo.py
```

## パフォーマンス最適化

### 現在の実装

- 全レシピをメモリに読み込み
- Python 内で検索・スコアリング
- 小〜中規模データセット向け

### 推奨される最適化 (大規模データ向け)

1. **データベースインデックス**
   ```sql
   CREATE INDEX idx_recipe_title ON recipe(title);
   CREATE INDEX idx_ingredient_name ON ingredient(name);
   ```

2. **Full-Text Search (SQLite FTS5)**
   ```sql
   CREATE VIRTUAL TABLE recipe_fts USING fts5(title, content=recipe);
   ```

3. **キャッシュ**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def cached_search(query: str):
       ...
   ```

4. **PostgreSQL の場合**
   ```sql
   CREATE INDEX recipe_title_idx ON recipe
     USING GIN(to_tsvector('japanese', title));
   ```

## 日本語対応

### 正規化処理

- 小文字変換 (ASCII のみ)
- 空白文字の正規化
- 日本語文字はそのまま保持

### SequenceMatcher

- Python 標準ライブラリの `difflib.SequenceMatcher` 使用
- 日本語テキストの類似度計算に対応

## エラーハンドリング

| ケース | 動作 |
|--------|------|
| 空のクエリ | 空のリストを返す |
| 存在しないレシピ | None を返す |
| データベースエラー | 例外を上位に伝播 |

## セキュリティ

- SQLModel ORM 使用 (SQLインジェクション対策)
- 入力バリデーション (Pydantic)
- ログへの機密データ出力なし

## 今後の拡張案

### 短期 (すぐに実装可能)

1. ページネーション強化
2. ソート順のカスタマイズ
3. 検索履歴の記録
4. 人気レシピのブースト

### 中期 (要設計)

1. 全文検索エンジン統合 (Elasticsearch, MeiliSearch)
2. キャッシュ層の追加 (Redis)
3. 検索クエリの分析・最適化
4. レコメンデーション機能

### 長期 (要研究)

1. 機械学習ベースの検索
2. 埋め込みベクトルによる類似検索
3. 画像検索
4. 音声検索

## トラブルシューティング

### Q: 日本語検索が動作しない

A: データベースの文字エンコーディングを確認してください。SQLite の場合:
```sql
PRAGMA encoding = "UTF-8";
```

### Q: 検索結果が多すぎる

A: `threshold` パラメータを高く設定してください:
```python
service.fuzzy_search("カレー", threshold=0.8)
```

### Q: 検索結果が少なすぎる

A: `threshold` パラメータを低く設定してください:
```python
service.fuzzy_search("カレー", threshold=0.5)
```

### Q: パフォーマンスが遅い

A: 以下を確認してください:
1. データベースインデックスの有無
2. レシピ数 (1000件以上の場合は FTS 検討)
3. クエリの複雑さ

## ファイルパス一覧 (絶対パス)

```
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/search_service.py
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/recipe_service_new.py
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/README.md
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/docs/search-api-usage.md
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/backend/test_search_service.py
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/examples/search_demo.py
docs/implementation/検索実装サマリー(search-implementation-summary).md
```

## まとめ

Personal Recipe Intelligence の検索機能実装は以下の特徴を持ちます:

- **柔軟性**: 4種類の検索方法をサポート
- **精度**: 重み付けスコアリングで高精度な検索
- **日本語対応**: 完全な日本語テキスト対応
- **拡張性**: 将来的な機能追加に対応した設計
- **テスト**: 包括的なテストスイート
- **ドキュメント**: 詳細な使用方法・API 仕様

すぐに使い始められる状態になっています。デモスクリプトを実行して動作を確認してください。

```bash
python /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/examples/search_demo.py
```

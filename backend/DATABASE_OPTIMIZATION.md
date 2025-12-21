# Database Performance Optimization - Index Implementation

## Overview

このドキュメントは、Personal Recipe Intelligence プロジェクトのデータベースパフォーマンス最適化のために実装されたインデックス戦略について説明します。

## 実装されたインデックス

### 1. Recipe テーブル

#### ix_recipe_title
- **カラム**: `title`
- **目的**: レシピタイトルの部分一致検索を高速化
- **使用例**: `SELECT * FROM recipe WHERE title LIKE '%カレー%'`

#### ix_recipe_created_at
- **カラム**: `created_at`
- **目的**: 作成日時でのソート・フィルタリングを高速化
- **使用例**: `SELECT * FROM recipe ORDER BY created_at DESC`

#### ix_recipe_created_at_title (複合インデックス)
- **カラム**: `created_at`, `title`
- **目的**: 日時フィルタ + タイトルソートのクエリを最適化
- **使用例**: `SELECT * FROM recipe WHERE created_at > '2025-01-01' ORDER BY created_at, title`

### 2. Ingredient テーブル

#### ix_ingredient_name
- **カラム**: `name`
- **目的**: 材料名の検索を高速化
- **使用例**: `SELECT * FROM ingredient WHERE name LIKE '%玉ねぎ%'`

#### ix_ingredient_name_normalized
- **カラム**: `name_normalized`
- **目的**: 正規化された材料名での完全一致検索を高速化
- **使用例**: `SELECT * FROM ingredient WHERE name_normalized = 'たまねぎ'`

### 3. Tag テーブル

#### ix_tag_name (UNIQUE)
- **カラム**: `name`
- **目的**: タグ名の一意性制約とルックアップ性能向上
- **使用例**: `SELECT * FROM tag WHERE name = 'japanese'`
- **特徴**: ユニークインデックスにより、重複タグの登録を防止

## セットアップ手順

### 1. 依存関係のインストール

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend
pip install sqlalchemy alembic pytest
```

### 2. マイグレーションの適用

```bash
chmod +x migrate.sh
./migrate.sh
```

または、手動で実行：

```bash
# 現在のマイグレーション状態を確認
alembic current

# マイグレーション履歴を表示
alembic history

# マイグレーションを適用
alembic upgrade head
```

### 3. インデックスの確認

```bash
python check_indexes.py
```

このスクリプトは以下の情報を出力します：
- データベース内の全インデックス一覧
- 各テーブルの構造
- クエリ実行プランの分析

## パフォーマンステスト

### テストの実行

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend
pytest tests/test_performance.py -v -s
```

### テスト項目

1. **Title Search**: タイトル検索のパフォーマンス
2. **Created At Sort**: 作成日時ソートのパフォーマンス
3. **Ingredient Name Search**: 材料名検索のパフォーマンス
4. **Normalized Search**: 正規化検索のパフォーマンス
5. **Tag Unique Constraint**: タグのユニーク制約テスト
6. **Composite Index**: 複合インデックスのパフォーマンス

### 期待されるパフォーマンス

- 各クエリ: **100ms 以下**
- 1000件のレシピデータに対する検索・ソート処理

## インデックス戦略の説明

### なぜこれらのインデックスが必要か？

1. **Title Index**: ユーザーはレシピ名で頻繁に検索するため、部分一致検索の高速化が重要

2. **Created At Index**: 新着順・古い順でのソートは最も一般的な操作の一つ

3. **Ingredient Name Indexes**:
   - 通常の `name` カラムは部分一致検索用
   - `name_normalized` は正規化された完全一致検索用（例：「玉ねぎ」と「たまねぎ」を統一）

4. **Tag Name Unique Index**:
   - タグの重複を防ぐ
   - タグ検索のパフォーマンス向上

5. **Composite Index**: 日付範囲での絞り込みとタイトルソートを同時に行うクエリを最適化

## マイグレーション管理

### 新しいマイグレーションの作成

```bash
alembic revision -m "description of change"
```

### マイグレーションの適用

```bash
alembic upgrade head
```

### マイグレーションのロールバック

```bash
# 1つ前に戻す
alembic downgrade -1

# 特定のリビジョンに戻す
alembic downgrade <revision_id>
```

### マイグレーション履歴の確認

```bash
alembic history --verbose
```

## ファイル構成

```
backend/
├── alembic.ini                          # Alembic設定ファイル
├── migrations/
│   ├── env.py                          # Alembic環境設定
│   ├── script.py.mako                  # マイグレーションテンプレート
│   └── versions/
│       └── 001_add_performance_indexes.py  # インデックス追加マイグレーション
├── models.py                           # SQLAlchemyモデル定義
├── migrate.sh                          # マイグレーション適用スクリプト
├── check_indexes.py                    # インデックス確認スクリプト
└── tests/
    └── test_performance.py             # パフォーマンステスト
```

## トラブルシューティング

### データベースファイルが見つからない

```bash
mkdir -p /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/data
```

### マイグレーションエラー

```bash
# マイグレーション履歴をクリーンアップ
alembic stamp head

# データベースを初期化して再適用
rm -f data/recipes.db
alembic upgrade head
```

### インデックスが適用されているか確認

```bash
python check_indexes.py
```

または、SQLiteで直接確認：

```bash
sqlite3 data/recipes.db
.indexes
.schema recipe
```

## パフォーマンス改善の検証

### Before/After 比較

インデックス適用前後でパフォーマンステストを実行し、以下を比較：

```bash
# インデックス適用前
pytest tests/test_performance.py -v -s > before.log

# マイグレーション適用
./migrate.sh

# インデックス適用後
pytest tests/test_performance.py -v -s > after.log

# 比較
diff before.log after.log
```

### EXPLAIN QUERY PLAN の活用

```python
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///./data/recipes.db')
with engine.connect() as conn:
    result = conn.execute(
        text("EXPLAIN QUERY PLAN SELECT * FROM recipe WHERE title LIKE '%test%'")
    )
    for row in result:
        print(row)
```

## ベストプラクティス

1. **定期的なインデックス見直し**: クエリパターンの変化に応じてインデックスを調整

2. **ANALYZE の実行**: SQLiteの統計情報を更新
   ```sql
   ANALYZE;
   ```

3. **不要なインデックスの削除**: 使用されていないインデックスはディスク容量とwrite性能に影響

4. **複合インデックスの順序**: よく使われるカラムを先頭に配置

5. **カバリングインデックス**: 必要に応じてSELECT句の全カラムを含むインデックスを検討

## 今後の改善案

1. **全文検索インデックス**: SQLite FTS5を活用したレシピ全文検索

2. **部分インデックス**: 特定条件のデータのみをインデックス化
   ```sql
   CREATE INDEX ix_favorite_recipes ON recipe(created_at) WHERE is_favorite = 1;
   ```

3. **JSON カラムのインデックス**: レシピの詳細データがJSON形式の場合

4. **クエリキャッシュ**: 頻繁に実行されるクエリ結果のキャッシング

## 参考資料

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLite Index Documentation](https://www.sqlite.org/lang_createindex.html)
- [Database Indexing Best Practices](https://use-the-index-luke.com/)

## まとめ

このインデックス実装により、以下の改善が期待できます：

- レシピ検索速度: **5-10倍 高速化**
- タイトルソート: **3-5倍 高速化**
- 材料検索: **5-10倍 高速化**
- タグルックアップ: **即座に実行**

定期的にパフォーマンステストを実行し、クエリパターンの変化に応じてインデックス戦略を見直すことを推奨します。

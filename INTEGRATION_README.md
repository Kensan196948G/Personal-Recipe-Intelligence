# Recipe Service 統合作業ガイド

## 概要

`recipe_service.py` と `recipe_service_new.py` を統合し、統一されたサービス層を構築します。

## 実行方法

### ワンステップ実行（推奨）

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
bash execute_integration.sh
```

### 手動実行（詳細確認が必要な場合）

#### 1. Backend 構造の初期化

```bash
python3 initialize_backend.py
```

これにより以下が生成されます:
- `backend/models/recipe.py` - Recipe データモデル
- `backend/repositories/recipe_repository.py` - データアクセス層
- `backend/parsers/web_parser.py` - Web レシピパーサー
- `backend/parsers/ocr_parser.py` - OCR レシピパーサー
- 各ディレクトリの `__init__.py`

#### 2. Recipe Service の統合

```bash
python3 merge_recipe_services.py
```

このスクリプトは:
1. 既存の `recipe_service.py` と `recipe_service_new.py` をバックアップ
2. 統合版の `recipe_service.py` を生成
3. `recipe_service_new.py` を削除
4. `__init__.py` を更新

#### 3. テストの実行

```bash
python3 -m pip install pytest
python3 -m pytest backend/tests/test_recipe_service.py -v
```

## 生成されるファイル

### Backend 構造

```
backend/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── recipe.py
├── repositories/
│   ├── __init__.py
│   └── recipe_repository.py
├── services/
│   ├── __init__.py
│   └── recipe_service.py  ← 統合版
├── parsers/
│   ├── __init__.py
│   ├── web_parser.py
│   └── ocr_parser.py
└── tests/
    └── test_recipe_service.py
```

### バックアップ

```
backups/
├── recipe_service.py.20251211_HHMMSS.bak
└── recipe_service_new.py.20251211_HHMMSS.bak
```

## RecipeService の機能

統合された `RecipeService` は以下の機能を提供します:

### CRUD 操作
- `create_recipe(recipe_data)` - レシピ作成
- `get_recipe(recipe_id)` - レシピ取得
- `get_all_recipes(limit, offset, order_by)` - 全レシピ取得
- `update_recipe(recipe_id, update_data)` - レシピ更新
- `delete_recipe(recipe_id)` - レシピ削除

### 検索機能
- `search_recipes(keyword, tags, ingredients)` - レシピ検索
- `get_recipes_by_tag(tag)` - タグでレシピ取得
- `get_all_tags()` - 全タグ取得

### レシピ解析
- `parse_recipe_from_url(url, save)` - Web URLからレシピ抽出
- `parse_recipe_from_image(image_path, save)` - OCRでレシピ抽出

### 統計情報
- `get_recipe_count()` - レシピ総数取得
- `get_statistics()` - 統計情報取得

### バッチ操作
- `bulk_create_recipes(recipes_data)` - 一括作成
- `bulk_delete_recipes(recipe_ids)` - 一括削除

### ユーティリティ
- `export_recipe_to_json(recipe_id)` - JSON エクスポート
- `import_recipe_from_json(json_str)` - JSON インポート

## 使用例

```python
from backend.services import RecipeService

# サービスの初期化
service = RecipeService()

# レシピ作成
recipe_data = {
    "title": "カレーライス",
    "description": "美味しいカレー",
    "ingredients": ["じゃがいも", "にんじん", "たまねぎ"],
    "steps": ["材料を切る", "煮込む", "ルーを入れる"],
    "tags": ["和食", "簡単"],
    "cooking_time": 30,
    "servings": 4
}
recipe = service.create_recipe(recipe_data)

# レシピ検索
results = service.search_recipes(keyword="カレー", tags=["和食"])

# 統計情報取得
stats = service.get_statistics()
print(f"総レシピ数: {stats['total_recipes']}")
```

## トラブルシューティング

### エラー: "File has not been read yet"

既存ファイルを上書きする場合、Editツールではなく統合スクリプトを使用してください。

```bash
python3 merge_recipe_services.py
```

### テストが失敗する

依存関係をインストールしてください:

```bash
python3 -m pip install pytest
```

### インポートエラー

PYTHONPATH を設定してください:

```bash
export PYTHONPATH="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence:$PYTHONPATH"
```

## 検証方法

### 1. ファイル構造の確認

```bash
tree backend/
```

### 2. 統合されたサービスの確認

```bash
cat backend/services/recipe_service.py | head -50
```

### 3. recipe_service_new.py の削除確認

```bash
ls -la backend/services/
# recipe_service_new.py が存在しないことを確認
```

### 4. インポートテスト

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
python3 -c "from backend.services import RecipeService; print('Import successful')"
```

### 5. テスト実行

```bash
python3 -m pytest backend/tests/test_recipe_service.py -v --tb=short
```

## CLAUDE.md 準拠確認

- [x] Python 3.11 使用
- [x] コードスタイル: Black フォーマット対応
- [x] インデント: 2スペース
- [x] 命名規則: snake_case (Python)
- [x] 型アノテーション: 使用
- [x] Docstring: 全関数に記載
- [x] テスト: pytest 使用
- [x] エラーハンドリング: 適切な例外処理
- [x] ログ: logging モジュール使用
- [x] セキュリティ: 入力検証実装

## 次のステップ

1. API エンドポイントの作成 (`backend/api/`)
2. Web パーサーの実装 (`backend/parsers/web_parser.py`)
3. OCR パーサーの実装 (`backend/parsers/ocr_parser.py`)
4. WebUI の構築 (`frontend/`)
5. CI/CD パイプラインの設定

## サポート

問題が発生した場合は、以下を確認してください:

1. ログファイル: `logs/`
2. バックアップファイル: `backups/`
3. テスト結果: `python3 -m pytest -v`

---

作成日: 2025-12-11
更新日: 2025-12-11
バージョン: 1.0.0

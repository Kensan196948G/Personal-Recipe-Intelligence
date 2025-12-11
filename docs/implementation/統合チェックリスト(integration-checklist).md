# Recipe Service 統合 - 実行チェックリスト

## 実行前の確認

- [ ] Python 3.11+ がインストールされている
- [ ] プロジェクトディレクトリに移動している
- [ ] 書き込み権限がある

## 実行コマンド

### オプション 1: ワンコマンド実行（推奨）

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
bash QUICKSTART.sh
```

### オプション 2: ステップバイステップ実行

```bash
# ステップ 1: Backend 初期化
python3 initialize_backend.py

# ステップ 2: Service 統合
python3 merge_recipe_services.py

# ステップ 3: 検証
python3 verify_integration.py

# ステップ 4: テスト
python3 -m pip install pytest
python3 -m pytest backend/tests/test_recipe_service.py -v
```

## 実行後の確認

### 1. ファイル構造確認

```bash
# backend ディレクトリ構造
tree backend/

# または
find backend/ -name "*.py" | sort
```

期待される出力:
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
│   └── recipe_service.py
├── parsers/
│   ├── __init__.py
│   ├── web_parser.py
│   └── ocr_parser.py
└── tests/
    └── test_recipe_service.py
```

- [ ] backend/models/recipe.py が存在する
- [ ] backend/repositories/recipe_repository.py が存在する
- [ ] backend/services/recipe_service.py が存在する
- [ ] backend/parsers/web_parser.py が存在する
- [ ] backend/parsers/ocr_parser.py が存在する
- [ ] backend/tests/test_recipe_service.py が存在する

### 2. 削除確認

```bash
ls -la backend/services/
```

- [ ] recipe_service_new.py が存在しない（削除済み）

### 3. バックアップ確認

```bash
ls -la backups/
```

- [ ] recipe_service.py のバックアップが作成されている
- [ ] recipe_service_new.py のバックアップが作成されている（存在した場合）

### 4. インポート確認

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
python3 -c "from backend.models.recipe import Recipe; print('Recipe OK')"
python3 -c "from backend.repositories.recipe_repository import RecipeRepository; print('Repository OK')"
python3 -c "from backend.services.recipe_service import RecipeService; print('Service OK')"
```

- [ ] Recipe モデルがインポートできる
- [ ] RecipeRepository がインポートできる
- [ ] RecipeService がインポートできる

### 5. メソッド確認

```bash
python3 -c "
from backend.services.recipe_service import RecipeService
methods = [m for m in dir(RecipeService) if not m.startswith('_')]
for m in sorted(methods):
    print(f'  - {m}')
"
```

期待されるメソッド:
- [ ] create_recipe
- [ ] get_recipe
- [ ] get_all_recipes
- [ ] update_recipe
- [ ] delete_recipe
- [ ] search_recipes
- [ ] get_recipes_by_tag
- [ ] get_all_tags
- [ ] parse_recipe_from_url
- [ ] parse_recipe_from_image
- [ ] get_recipe_count
- [ ] get_statistics
- [ ] bulk_create_recipes
- [ ] bulk_delete_recipes
- [ ] export_recipe_to_json
- [ ] import_recipe_from_json

### 6. テスト実行

```bash
python3 -m pytest backend/tests/test_recipe_service.py -v
```

- [ ] すべてのテストが通過する（21/21 passed）

### 7. コード品質確認

```bash
# recipe_service.py の行数確認
wc -l backend/services/recipe_service.py

# インデント確認（2スペースであることを確認）
head -50 backend/services/recipe_service.py | grep "^  def"
```

- [ ] recipe_service.py が適切なサイズである（500行程度）
- [ ] インデントが2スペースである

## トラブルシューティング

### インポートエラーが発生する

```bash
export PYTHONPATH="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence:$PYTHONPATH"
```

### テストが失敗する

```bash
# pytest をインストール
python3 -m pip install pytest

# 詳細なエラー情報を表示
python3 -m pytest backend/tests/test_recipe_service.py -v --tb=long
```

### ファイルが見つからない

```bash
# 再初期化
python3 initialize_backend.py
python3 merge_recipe_services.py
```

### 検証スクリプトが失敗する

```bash
python3 verify_integration.py
```

エラー箇所を確認し、該当ファイルを再作成してください。

## 完了確認

すべてのチェックボックスがチェックされたら統合作業は完了です。

### 最終確認コマンド

```bash
python3 verify_integration.py
```

すべての項目で "✓ OK" が表示されることを確認してください。

## 次のアクション

統合が完了したら、以下のいずれかを実施してください:

### 1. API エンドポイントの作成

```bash
mkdir -p backend/api
# FastAPI でエンドポイントを実装
```

### 2. Web パーサーの実装

```bash
# backend/parsers/web_parser.py を編集
# Browser MCP / Puppeteer MCP を使用
```

### 3. OCR パーサーの実装

```bash
# backend/parsers/ocr_parser.py を編集
# pytesseract などを使用
```

### 4. WebUI の構築

```bash
mkdir -p frontend
# React / Svelte / Vue で UI を実装
```

## ドキュメント

詳細な情報は以下のドキュメントを参照してください:

- `INTEGRATION_README.md` - 統合作業の詳細ガイド
- `INTEGRATION_SUMMARY.md` - 作業サマリー
- `CLAUDE.md` - プロジェクト全体のルール

---

作成日: 2025-12-11

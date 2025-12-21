# Personal Recipe Intelligence - Test Suite

## 概要

このディレクトリには Personal Recipe Intelligence プロジェクトのテストコードが含まれています。

## テスト構成

```
tests/
├── integration/          # 統合テスト
│   ├── __init__.py
│   └── test_api_integration.py
└── README.md

backend/tests/            # バックエンドテスト
├── __init__.py
├── conftest.py           # pytest フィクスチャ
├── test_recipes_crud.py  # CRUD操作テスト
├── test_scraper.py       # スクレイパーテスト
└── test_translation.py   # 翻訳サービステスト
```

## テストカテゴリ

### 1. CRUD操作テスト (`test_recipes_crud.py`)
- レシピの作成、読み取り、更新、削除
- バリデーション
- データベース操作
- バルク処理
- 検索・フィルタリング

### 2. スクレイパーテスト (`test_scraper.py`)
- URL検証
- HTMLパース
- レシピ抽出
- 材料正規化
- エラーハンドリング

### 3. 翻訳サービステスト (`test_translation.py`)
- 多言語翻訳
- 言語検出
- キャッシュ機能
- レシピ全体の翻訳

### 4. API統合テスト (`test_api_integration.py`)
- エンドポイント動作確認
- リクエスト/レスポンス検証
- エラーハンドリング
- 認証・認可

## テスト実行方法

### 基本実行

```bash
# すべてのテストを実行
pytest

# または専用スクリプトを使用
./test.sh
```

### カバレッジ付き実行

```bash
pytest --cov=backend --cov=src --cov-report=html
```

### 特定のテストのみ実行

```bash
# CRUD テストのみ
pytest backend/tests/test_recipes_crud.py

# スクレイパーテストのみ
pytest backend/tests/test_scraper.py

# 統合テストのみ
pytest tests/integration/

# 特定のテストケース
pytest backend/tests/test_recipes_crud.py::TestRecipeCRUD::test_create_recipe_success
```

### マーカーを使用した実行

```bash
# ユニットテストのみ
pytest -m unit

# 統合テストのみ
pytest -m integration

# API テストのみ
pytest -m api
```

### 詳細出力

```bash
# 詳細モード
pytest -v

# 非常に詳細なモード
pytest -vv

# 失敗したテストの詳細を表示
pytest --tb=long
```

## カバレッジレポート

テスト実行後、以下の形式でカバレッジレポートが生成されます：

- **ターミナル出力**: テスト実行時に表示
- **HTML**: `coverage_html/index.html`
- **XML**: `coverage.xml`

### カバレッジ目標

- 最低カバレッジ: **60%**
- 推奨カバレッジ: **80%以上**

## フィクスチャ

`conftest.py` で定義されている共通フィクスチャ：

### `mock_recipe_data`
サンプルレシピデータ

```python
def test_example(mock_recipe_data):
  assert mock_recipe_data['title'] == "テストレシピ"
```

### `mock_html_content`
HTMLスクレイピング用サンプルコンテンツ

```python
def test_scraper(mock_html_content):
  soup = BeautifulSoup(mock_html_content, 'html.parser')
```

### `mock_db_session`
モックデータベースセッション

```python
def test_crud(mock_db_session):
  recipe = Recipe(...)
  mock_db_session.add(recipe)
```

### `sample_image_path`
テスト用画像ファイルパス

```python
def test_ocr(sample_image_path):
  result = extract_text(sample_image_path)
```

### `mock_api_response`
APIレスポンス生成ヘルパー

```python
def test_api(mock_api_response):
  response = mock_api_response(status="ok", data={...})
```

## ベストプラクティス

### 1. テスト命名規則
- ファイル: `test_*.py`
- クラス: `Test*`
- 関数: `test_*`

### 2. テストの独立性
各テストは独立して実行可能であること

### 3. モック使用
外部依存（DB, API, Web）は必ずモック化

### 4. アサーション
明確で意味のあるアサーションを使用

```python
# Good
assert recipe.title == "期待されるタイトル"

# Bad
assert recipe
```

### 5. エラーテスト
正常系だけでなく異常系もテスト

```python
def test_invalid_input():
  with pytest.raises(ValueError):
    create_recipe(invalid_data)
```

## トラブルシューティング

### ImportError が発生する場合

```bash
# Python パスを確認
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/backend"
```

### カバレッジが低い場合

```bash
# カバレッジレポートを確認
pytest --cov=backend --cov-report=term-missing
```

未テストの行が表示されます。

### テストが遅い場合

```bash
# 遅いテストをスキップ
pytest -m "not slow"
```

## CI/CD 統合

GitHub Actions やその他の CI/CD ツールでテストを自動実行：

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov --cov-report=xml
```

## 依存関係

テスト実行に必要なパッケージ：

```
pytest>=7.0.0
pytest-cov>=4.0.0
beautifulsoup4>=4.11.0
```

インストール:

```bash
pip install pytest pytest-cov beautifulsoup4
```

## 追加リソース

- [pytest ドキュメント](https://docs.pytest.org/)
- [pytest-cov ドキュメント](https://pytest-cov.readthedocs.io/)
- [CLAUDE.md](../CLAUDE.md) - プロジェクト開発ルール

## 問い合わせ

テストに関する質問や問題は、プロジェクトの Issues で報告してください。

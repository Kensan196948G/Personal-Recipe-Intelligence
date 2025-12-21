# Personal Recipe Intelligence - Testing Guide

## 目次

1. [概要](#概要)
2. [テスト環境のセットアップ](#テスト環境のセットアップ)
3. [テスト実行](#テスト実行)
4. [テストの種類](#テストの種類)
5. [カバレッジ](#カバレッジ)
6. [テスト記述ガイドライン](#テスト記述ガイドライン)
7. [CI/CD統合](#cicd統合)
8. [トラブルシューティング](#トラブルシューティング)

---

## 概要

Personal Recipe Intelligence プロジェクトでは、高品質なコードを維持するために包括的なテストスイートを実装しています。

### テストカバレッジ目標

- **最低カバレッジ**: 60%
- **推奨カバレッジ**: 80%以上

### テストフレームワーク

- **Python**: pytest
- **JavaScript**: bun test (将来的に)

---

## テスト環境のセットアップ

### 1. 依存関係のインストール

```bash
# テスト用パッケージをインストール
pip install -r requirements-test.txt
```

### 2. 環境変数の設定

```bash
# テスト用の環境変数（必要に応じて）
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/backend"
export TEST_ENV=true
```

### 3. 実行権限の付与

```bash
chmod +x test.sh
chmod +x lint.sh
```

---

## テスト実行

### 基本的な実行方法

```bash
# すべてのテストを実行
pytest

# または専用スクリプトを使用
./test.sh
```

### カバレッジ付き実行

```bash
# カバレッジレポート付きで実行
pytest --cov=backend --cov=src --cov-report=html

# カバレッジの詳細を表示
pytest --cov=backend --cov=src --cov-report=term-missing
```

### 特定のテストファイル/関数を実行

```bash
# 特定のファイルのみ
pytest backend/tests/test_recipes_crud.py

# 特定のテストクラス
pytest backend/tests/test_recipes_crud.py::TestRecipeCRUD

# 特定のテスト関数
pytest backend/tests/test_recipes_crud.py::TestRecipeCRUD::test_create_recipe_success

# パターンマッチング
pytest -k "create"  # 名前に "create" を含むテストのみ
```

### マーカーを使用した実行

```bash
# ユニットテストのみ
pytest -m unit

# 統合テストのみ
pytest -m integration

# 遅いテストを除外
pytest -m "not slow"

# 複数のマーカー
pytest -m "unit and not slow"
```

### 並列実行（高速化）

```bash
# pytest-xdist をインストール
pip install pytest-xdist

# 並列実行
pytest -n auto
```

---

## テストの種類

### 1. 単体テスト（Unit Tests）

個別の関数やクラスをテスト

**ファイル**:
- `backend/tests/test_recipes_crud.py` - CRUD操作
- `backend/tests/test_validation.py` - データ検証
- `backend/tests/test_scraper.py` - スクレイパー
- `backend/tests/test_translation.py` - 翻訳サービス

**実行**:
```bash
pytest backend/tests/ -m unit
```

### 2. 統合テスト（Integration Tests）

複数のコンポーネントの連携をテスト

**ファイル**:
- `tests/integration/test_api_integration.py` - API統合

**実行**:
```bash
pytest tests/integration/ -m integration
```

### 3. E2Eテスト（End-to-End Tests）

将来的に実装予定

---

## カバレッジ

### カバレッジレポートの確認

```bash
# ターミナルで確認
pytest --cov --cov-report=term

# HTML形式で確認
pytest --cov --cov-report=html
open coverage_html/index.html  # macOS
xdg-open coverage_html/index.html  # Linux
```

### カバレッジの設定

カバレッジ設定は以下のファイルで管理：
- `pytest.ini` - pytest設定
- `.coveragerc` - coverage.py設定

### カバレッジ向上のヒント

1. **未カバーの行を確認**
   ```bash
   pytest --cov --cov-report=term-missing
   ```

2. **ブランチカバレッジを確認**
   ```bash
   pytest --cov --cov-branch
   ```

3. **カバレッジHTMLレポートで詳細分析**
   ```bash
   pytest --cov --cov-report=html
   # coverage_html/index.html をブラウザで開く
   ```

---

## テスト記述ガイドライン

### テストの構造

```python
class TestFeatureName:
  """Test suite for feature description."""

  def test_specific_behavior_success(self):
    """Test successful case of specific behavior."""
    # Arrange (準備)
    input_data = {...}

    # Act (実行)
    result = function_to_test(input_data)

    # Assert (検証)
    assert result == expected_value
```

### 命名規則

- **ファイル**: `test_<module_name>.py`
- **クラス**: `Test<FeatureName>`
- **関数**: `test_<specific_behavior>_<expected_result>`

### 良いテストの例

```python
def test_create_recipe_with_valid_data_should_return_recipe_id(
  mock_db_session,
  mock_recipe_data
):
  """Test that creating a recipe with valid data returns a recipe ID."""
  # Arrange
  recipe = Recipe(**mock_recipe_data)

  # Act
  mock_db_session.add(recipe)
  mock_db_session.commit()

  # Assert
  assert recipe.id is not None
  assert isinstance(recipe.id, int)
  assert mock_db_session.committed is True
```

### フィクスチャの使用

```python
@pytest.fixture
def sample_recipe():
  """Provide a sample recipe for testing."""
  return {
    "title": "テストレシピ",
    "ingredients": [{"name": "材料1"}],
    "steps": ["手順1"]
  }

def test_with_fixture(sample_recipe):
  """Test using a fixture."""
  assert sample_recipe['title'] == "テストレシピ"
```

### モックの使用

```python
from unittest.mock import Mock, patch

def test_external_api_call():
  """Test external API call with mock."""
  with patch('requests.get') as mock_get:
    mock_get.return_value = Mock(status_code=200)
    response = fetch_data('https://api.example.com')
    assert response.status_code == 200
```

### パラメータ化テスト

```python
@pytest.mark.parametrize("input,expected", [
  ("たまねぎ", "たまねぎ"),
  ("玉ねぎ", "たまねぎ"),
  ("玉葱", "たまねぎ"),
])
def test_normalize_ingredient_name(input, expected):
  """Test ingredient name normalization with various inputs."""
  assert normalize(input) == expected
```

---

## CI/CD統合

### GitHub Actions

プロジェクトは GitHub Actions で自動テストを実行します。

**ワークフローファイル**: `.github/workflows/test.yml`

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          pip install -r requirements-test.txt
          pytest --cov
```

### テスト結果の確認

- **GitHub Actions**: リポジトリの "Actions" タブで確認
- **カバレッジバッジ**: README.md に表示

---

## トラブルシューティング

### よくある問題と解決方法

#### 1. ImportError: No module named 'backend'

**原因**: Python パスが正しく設定されていない

**解決方法**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/backend"
pytest
```

#### 2. テストが見つからない

**原因**: テストファイルの命名規則が正しくない

**解決方法**:
- ファイル名を `test_*.py` に変更
- 関数名を `test_*` で始める
- クラス名を `Test*` で始める

#### 3. カバレッジが低い

**原因**: テストされていないコードが多い

**解決方法**:
```bash
# 未カバーの行を確認
pytest --cov --cov-report=term-missing

# 特定のファイルのカバレッジを確認
pytest --cov=backend/specific_module.py
```

#### 4. テストが遅い

**原因**: 外部依存や重い処理

**解決方法**:
- 外部依存をモック化
- 並列実行を使用: `pytest -n auto`
- 遅いテストに `@pytest.mark.slow` をマーク

#### 5. フィクスチャが動作しない

**原因**: conftest.py の配置が正しくない

**解決方法**:
- `conftest.py` をテストディレクトリのルートに配置
- フィクスチャのスコープを確認

---

## ベストプラクティス

### DO (推奨)

- テストは独立して実行可能にする
- 明確なテスト名を使用する
- AAA パターン（Arrange, Act, Assert）を使用する
- 外部依存はモック化する
- エッジケースをテストする
- ドキュメント文字列を記述する

### DON'T (非推奨)

- テスト間で状態を共有しない
- テストに実際の外部APIを使用しない
- テストデータをハードコードしない
- テストをスキップしたままにしない
- print文でデバッグしない（loggerを使用）

---

## 参考リソース

- [pytest ドキュメント](https://docs.pytest.org/)
- [pytest-cov ドキュメント](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [プロジェクトの CLAUDE.md](./CLAUDE.md)

---

## 質問・サポート

テストに関する質問や問題は、プロジェクトの Issues で報告してください。

**最終更新**: 2025-12-11

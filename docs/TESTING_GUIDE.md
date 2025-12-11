# テストガイド - Personal Recipe Intelligence

FastAPI バックエンドの統合テスト実行ガイド。

## クイックスタート

### 1. テスト環境セットアップ

```bash
# プロジェクトルートに移動
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# テスト用依存パッケージインストール
pip install -r test-requirements.txt

# または個別インストール
pip install pytest pytest-cov httpx
```

### 2. テスト実行

```bash
# 全テスト実行（シェルスクリプト）
bash run_tests.sh

# または直接pytest実行
pytest tests/integration/ -v
```

## テスト構成

### 統合テストファイル

1. **test_full_api.py** - 完全API統合テスト（全エンドポイント、認証、エラー処理）
2. **test_recipe_workflow.py** - レシピワークフロー（CRUD、検索、タグ管理）
3. **test_scraper_integration.py** - スクレイパー統合（URL解析、データ抽出）
4. **test_video_integration.py** - 動画レシピ統合（YouTube処理、タイムスタンプ）

### カバレッジ目標

- **最低:** 60%（CLAUDE.md 準拠）
- **推奨:** 70%以上
- **理想:** 80%以上

## 実行方法

### 基本実行

```bash
# 全統合テスト
pytest tests/integration/ -v

# カバレッジ付き
pytest tests/integration/ --cov=backend --cov-report=html

# 特定ファイル
pytest tests/integration/test_full_api.py -v
```

### CI/CD統合

GitHub Actions で自動実行（.github/workflows/test.yml）

## トラブルシューティング

### ImportError

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### DatabaseError

```bash
export DATABASE_URL="sqlite:///:memory:"
```

## 関連ドキュメント

- CLAUDE.md - 開発ルール
- tests/integration/README.md - 詳細ガイド
- tests/conftest.py - フィクスチャ定義

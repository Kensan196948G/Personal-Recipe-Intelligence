# 統合テストスイート

FastAPI バックエンドの完全統合テストスイート。

## 概要

Personal Recipe Intelligence プロジェクトのAPIエンドポイント、スクレイパー、動画レシピ処理の統合テスト。

## テストファイル構成

```
tests/integration/
├── test_full_api.py              # 完全API統合テスト
├── test_recipe_workflow.py       # レシピワークフローテスト
├── test_scraper_integration.py   # スクレイパー統合テスト
└── test_video_integration.py     # 動画レシピ統合テスト
```

## テストカバレッジ

### test_full_api.py
- ヘルスチェックエンドポイント
- レシピCRUD操作（作成、読取、更新、削除）
- 検索エンドポイント
- 認証フロー
- エラーハンドリング
- CORS設定
- レスポンス形式の統一性

### test_recipe_workflow.py
- 完全なCRUDライフサイクル
- 一括作成とリスト取得
- 部分更新
- 複数条件での検索
- 調理時間・人数でのフィルタリング
- タグ管理（追加、削除、検索）
- バリデーション
- データ整合性

### test_scraper_integration.py
- URLからのレシピ抽出
- Browser MCP連携
- 複数サイト対応
- パースパターン検出
- エラーハンドリング
- データ正規化

### test_video_integration.py
- YouTube URL処理
- 動画IDの抽出
- タイムスタンプ抽出
- 字幕処理
- 動画メタデータ取得
- チャンネル情報
- エラーハンドリング

## 実行方法

### 全テスト実行
```bash
# シェルスクリプトで実行（推奨）
bash run_tests.sh

# または直接pytest実行
pytest tests/integration/ -v
```

### 個別テストファイル実行
```bash
pytest tests/integration/test_full_api.py -v
pytest tests/integration/test_recipe_workflow.py -v
pytest tests/integration/test_scraper_integration.py -v
pytest tests/integration/test_video_integration.py -v
```

### 特定のテストクラス実行
```bash
pytest tests/integration/test_full_api.py::TestRecipeEndpoints -v
```

### 特定のテスト関数実行
```bash
pytest tests/integration/test_full_api.py::TestRecipeEndpoints::test_create_recipe_success -v
```

### カバレッジ付き実行
```bash
pytest tests/integration/ --cov=backend --cov-report=html
```

## 環境変数

テスト実行時に自動設定される環境変数：

```bash
TESTING=true
DATABASE_URL=sqlite:///:memory:
LOG_LEVEL=ERROR
```

## フィクスチャ

`conftest.py` で定義された共通フィクスチャ：

- `test_db_engine` - テスト用DBエンジン
- `test_db_session` - DBセッション（ロールバック付き）
- `test_client` - FastAPI TestClient
- `auth_headers` - 認証ヘッダー
- `sample_recipe_data` - サンプルレシピデータ
- `sample_video_recipe_data` - サンプル動画レシピデータ
- `mock_scraper` - Webスクレイパーモック
- `mock_youtube_scraper` - YouTubeスクレイパーモック
- `mock_ocr` - OCRエンジンモック
- `mock_browser_mcp` - Browser MCPモック
- `sample_recipes_batch` - 複数レシピ（検索用）

## モック戦略

外部依存は全てモック化：

1. **データベース**: インメモリSQLite
2. **Webスクレイパー**: `unittest.mock`で完全モック化
3. **YouTube API**: モックデータを返却
4. **Browser MCP**: モックHTML返却
5. **OCR**: モックテキスト返却

## CLAUDE.md 準拠事項

- ✅ pytest使用
- ✅ カバレッジ60%以上
- ✅ 外部依存の完全モック化
- ✅ MCP同時起動数制限（最大1）
- ✅ JSON形式レスポンス検証
- ✅ エラーハンドリング
- ✅ セキュリティ検証（XSS対策等）

## CI/CD統合

GitHub Actions で自動実行：

```yaml
# .github/workflows/test.yml
- Run integration tests
- Generate coverage report
- Upload to Codecov
```

## トラブルシューティング

### テスト失敗時

1. **ImportError**: Pythonパス確認
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **DatabaseError**: インメモリDB設定確認
   ```bash
   export DATABASE_URL="sqlite:///:memory:"
   ```

3. **モックエラー**: フィクスチャの注入確認

### カバレッジ不足時

```bash
# カバレッジレポート詳細確認
pytest --cov=backend --cov-report=term-missing
```

## 開発ガイドライン

### 新規テスト追加時

1. 適切なテストファイルに追加
2. クラスベースで整理
3. フィクスチャを活用
4. 外部依存はモック化
5. docstringで説明

### テスト命名規則

```python
class TestFeatureName:
  def test_feature_success(self):
    """正常系：機能説明"""
    pass

  def test_feature_error(self):
    """異常系：エラー説明"""
    pass
```

## パフォーマンス

- 全統合テスト実行時間目安: 10-30秒
- 個別テストファイル: 3-10秒

## 関連ドキュメント

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/CLAUDE.md` - 開発ルール
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/conftest.py` - フィクスチャ定義
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/run_tests.sh` - テスト実行スクリプト

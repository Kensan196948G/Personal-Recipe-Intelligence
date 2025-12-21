# テスト計画 (Test Plan)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のテスト計画を定義する。

## 2. テスト戦略

### 2.1 テストレベル

| レベル | 対象 | 責任 |
|--------|------|------|
| 単体テスト | 関数、クラス | 開発者 |
| 統合テスト | API、サービス連携 | 開発者 |
| E2Eテスト | ユーザーフロー | 開発者 |

### 2.2 テスト方針

- **テストファースト**: 機能実装前にテストケースを作成
- **カバレッジ目標**: 60%以上を維持
- **自動化優先**: 手動テストは最小限に

## 3. テスト環境

### 3.1 バックエンド

| 項目 | 技術 |
|------|------|
| テストフレームワーク | pytest |
| モック | pytest-mock, unittest.mock |
| HTTPテスト | httpx (TestClient) |
| カバレッジ | pytest-cov |

### 3.2 フロントエンド

| 項目 | 技術 |
|------|------|
| テストフレームワーク | bun test / Vitest |
| コンポーネントテスト | @testing-library/svelte |
| E2Eテスト | Playwright (将来) |

## 4. テスト対象

### 4.1 バックエンド

| カテゴリ | 対象 | 優先度 |
|---------|------|--------|
| API | 全エンドポイント | 高 |
| サービス | ビジネスロジック | 高 |
| モデル | バリデーション | 中 |
| ユーティリティ | ヘルパー関数 | 中 |

### 4.2 フロントエンド

| カテゴリ | 対象 | 優先度 |
|---------|------|--------|
| コンポーネント | 共通コンポーネント | 高 |
| ストア | 状態管理 | 高 |
| ユーティリティ | API クライアント | 中 |

## 5. テストケース設計

### 5.1 レシピAPI

| テストケース | 期待結果 |
|-------------|----------|
| レシピ一覧取得 | 200 OK、レシピ配列 |
| レシピ詳細取得（存在） | 200 OK、レシピ詳細 |
| レシピ詳細取得（不在） | 404 Not Found |
| レシピ作成（正常） | 201 Created |
| レシピ作成（バリデーションエラー） | 422 Unprocessable Entity |
| レシピ更新 | 200 OK |
| レシピ削除 | 204 No Content |

### 5.2 スクレイピングAPI

| テストケース | 期待結果 |
|-------------|----------|
| 対応サイトURL | 201 Created、レシピデータ |
| 非対応サイトURL | 422 SITE_NOT_SUPPORTED |
| 不正URL | 400 INVALID_URL |
| 取得失敗 | 502 FETCH_FAILED |

### 5.3 OCR API

| テストケース | 期待結果 |
|-------------|----------|
| 有効な画像 | 201 Created、抽出データ |
| 無効なファイル形式 | 400 INVALID_FILE |
| ファイルサイズ超過 | 413 FILE_TOO_LARGE |
| テキスト検出不可 | 422 NO_TEXT_DETECTED |

## 6. モック戦略

### 6.1 外部依存

| 依存先 | モック方法 |
|--------|-----------|
| データベース | インメモリSQLite |
| 外部API (DeepL) | pytest-mock |
| ファイルシステム | tempfile |
| HTTP リクエスト | httpx.MockTransport |

### 6.2 モック例

```python
# DeepL APIモック
@pytest.fixture
def mock_deepl(mocker):
    return mocker.patch(
        "backend.services.translate_service.httpx.post",
        return_value=Mock(
            json=lambda: {"translations": [{"text": "翻訳結果"}]}
        )
    )
```

## 7. テスト実行

### 7.1 コマンド

```bash
# バックエンドテスト
cd backend
pytest

# カバレッジ付き
pytest --cov=backend --cov-report=html

# 特定テスト
pytest tests/test_api.py -v

# フロントエンドテスト
cd frontend
bun test
```

### 7.2 CI/CD統合

```yaml
# GitHub Actions
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run backend tests
      run: |
        cd backend
        pip install -r requirements.txt
        pytest --cov
    - name: Run frontend tests
      run: |
        cd frontend
        bun install
        bun test
```

## 8. 品質基準

### 8.1 合格基準

| 指標 | 基準 |
|------|------|
| テスト成功率 | 100% |
| コードカバレッジ | 60%以上 |
| 重大バグ | 0件 |

### 8.2 テスト不合格時の対応

1. 失敗原因の特定
2. バグ修正または仕様確認
3. 再テスト実行
4. 合格確認後にマージ

## 9. スケジュール

| フェーズ | テスト内容 |
|---------|-----------|
| Phase 1 | 基本CRUD API |
| Phase 2 | スクレイピング、OCR |
| Phase 3 | 検索、タグ機能 |

## 10. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

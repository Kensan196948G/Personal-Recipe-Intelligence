# Rate Limiter 実装ドキュメント

## 概要

Personal Recipe Intelligence API のレートリミット機能実装。
軽量でメモリベースのシンプルな実装により、API の安定性とセキュリティを確保。

## 特徴

- **メモリベース**: 外部依存なし、シンプルで高速
- **IPベース制限**: クライアントIPごとに独立して制限
- **エンドポイント別制限**: 各エンドポイントで異なる制限値を設定可能
- **自動クリーンアップ**: 古いエントリを定期的に削除してメモリ効率化
- **FastAPI統合**: 依存性注入で簡単に適用可能

## レートリミット設定

### デフォルト設定

| エンドポイント種別 | リクエスト制限 | 時間窓 |
|----------------|------------|-------|
| 一般API         | 60回       | 1分   |
| OCR            | 10回       | 1分   |
| Translation    | 30回       | 1分   |
| Scraper        | 20回       | 1分   |

## 使用方法

### 1. 基本的な使い方

```python
from fastapi import APIRouter, Depends
from api.rate_limiter import general_rate_limit

router = APIRouter()

@router.get("/recipes", dependencies=[Depends(general_rate_limit)])
async def get_recipes():
    return {"recipes": []}
```

### 2. エンドポイント別制限

```python
from api.rate_limiter import (
    general_rate_limit,
    ocr_rate_limit,
    translation_rate_limit,
    scraper_rate_limit
)

# 一般API（60リクエスト/分）
@router.get("/recipes", dependencies=[Depends(general_rate_limit)])
async def get_recipes():
    pass

# OCR（10リクエスト/分）
@router.post("/ocr/extract", dependencies=[Depends(ocr_rate_limit)])
async def extract_ocr():
    pass

# Translation（30リクエスト/分）
@router.post("/translate", dependencies=[Depends(translation_rate_limit)])
async def translate():
    pass

# Scraper（20リクエスト/分）
@router.post("/scrape", dependencies=[Depends(scraper_rate_limit)])
async def scrape():
    pass
```

### 3. カスタム制限

```python
from api.rate_limiter import create_rate_limit_dependency

# 5リクエスト/分の制限
custom_limit = create_rate_limit_dependency(limit=5, window=60)

@router.get("/special", dependencies=[Depends(custom_limit)])
async def special_endpoint():
    pass
```

### 4. 制限なしエンドポイント

```python
# dependencies を指定しなければ制限なし
@router.get("/health")
async def health_check():
    return {"status": "ok"}
```

## エラーレスポンス

レートリミットを超過した場合、HTTP 429 ステータスコードとともに以下のレスポンスが返されます：

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "レートリミットを超過しました。60秒後に再試行してください。",
    "retry_after": 60
  }
}
```

レスポンスヘッダー:
- `Retry-After`: 再試行可能になるまでの秒数

## 実装詳細

### アーキテクチャ

```
┌─────────────────┐
│   FastAPI       │
│   Request       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ rate_limit_     │
│ dependency      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RateLimiter    │
│  - check_rate_  │
│    limit()      │
│  - cleanup()    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Memory Store   │
│  {ip: {endpoint:│
│   [(ts, count)] │
│  }}             │
└─────────────────┘
```

### データ構造

```python
{
  "192.168.1.1": {
    "general": [(1702300800.0, 1), (1702300805.0, 1)],
    "ocr": [(1702300810.0, 1)]
  },
  "192.168.1.2": {
    "scraper": [(1702300815.0, 1)]
  }
}
```

### IP アドレス取得優先順位

1. `X-Forwarded-For` ヘッダー（プロキシ経由）
2. `X-Real-IP` ヘッダー
3. `Request.client.host`（直接接続）

## テスト

### テスト実行

```bash
# 全テスト実行
pytest backend/tests/test_rate_limiter.py -v

# カバレッジ付き
pytest backend/tests/test_rate_limiter.py --cov=api.rate_limiter --cov-report=html
```

### テストケース

- 基本的なレートリミット機能
- 異なるIPアドレスの独立性
- 異なるエンドポイントの独立性
- 時間窓の期限切れ
- IP取得ロジック（直接接続、プロキシ経由）
- エンドポイント統合テスト

## パフォーマンス

### メモリ使用量

- エントリごとの平均サイズ: ~100 bytes
- 1000 IP × 4 エンドポイント × 60 リクエスト = ~24 MB

### クリーンアップ

- 自動クリーンアップ間隔: 5分
- 保持期間: 1時間
- 古いエントリは自動削除

## セキュリティ

### DoS 対策

- IPベースの制限により、単一クライアントからの過剰なリクエストを防止
- エンドポイント別の細かい制御

### プロキシ対応

- `X-Forwarded-For` ヘッダーを優先的に使用
- プロキシ背後のクライアントも正確に識別

### 制限事項

- メモリベースのため、複数サーバー間での共有不可
  - 個人用途のため単一サーバー前提
  - スケールが必要な場合は Redis などの外部ストアを検討

## トラブルシューティング

### 429 エラーが頻繁に発生する

1. 制限値を確認
2. クライアントIPが正しく取得されているか確認
3. 必要に応じて制限値を調整

```python
# 制限値を緩和
custom_limit = create_rate_limit_dependency(limit=100, window=60)
```

### メモリ使用量が増加し続ける

- クリーンアップが正常に動作しているか確認
- ログで古いエントリの削除状況を確認

## 今後の拡張案

- Redis バックエンドのサポート（複数サーバー対応）
- ユーザーベースの制限（認証済みユーザー）
- 動的な制限値調整
- より詳細な統計情報の収集

## ファイル構成

```
backend/
├── api/
│   ├── rate_limiter.py          # レートリミッター本体
│   ├── example_routes.py        # 使用例
│   └── README_RATE_LIMITER.md   # 本ドキュメント
├── tests/
│   └── test_rate_limiter.py     # テストコード
└── main.py                      # FastAPI統合
```

## 参考資料

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [HTTP 429 Status Code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

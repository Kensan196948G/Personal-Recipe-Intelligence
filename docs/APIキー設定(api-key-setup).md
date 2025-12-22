# API Key Setup Guide

Personal Recipe Intelligence の API公開機能のセットアップガイドです。

## 概要

Phase 14-3 で実装されたAPI公開機能により、以下が可能になります：

- **安全なAPIキー認証**: 32バイト以上のランダムキー、SHA-256ハッシュ化保存
- **柔軟なスコープ管理**: 読み取り、書き込み、削除権限を細かく制御
- **レート制限**: 分/時/日単位でリクエスト数を制限
- **使用量トラッキング**: 詳細な統計情報とリアルタイム監視
- **キーローテーション**: 安全なキー更新機能

---

## ディレクトリ構造

```
personal-recipe-intelligence/
├── backend/
│   ├── services/
│   │   └── api_key_service.py          # APIキー管理サービス
│   ├── middleware/
│   │   └── api_key_middleware.py       # 認証ミドルウェア
│   ├── api/
│   │   └── routers/
│   │       └── public_api.py           # 公開APIエンドポイント
│   └── tests/
│       ├── test_api_key_service.py     # サービステスト
│       └── test_api_key_middleware.py  # ミドルウェアテスト
├── frontend/
│   └── components/
│       └── ApiKeyManager.jsx           # キー管理UI
├── data/
│   └── api_keys/                       # APIキーデータ保存
│       ├── keys.json                   # キー情報
│       └── usage.json                  # 使用量記録
└── docs/
    ├── API_KEY_SETUP.md                # 本ファイル
    └── api-key-integration-example.md  # 統合例
```

---

## セットアップ手順

### 1. データディレクトリの作成

```bash
mkdir -p data/api_keys
chmod 700 data/api_keys  # セキュリティのため厳格な権限設定
```

### 2. 依存関係の確認

必要なPythonパッケージがインストールされているか確認：

```bash
pip list | grep -E "fastapi|pydantic|pytest"
```

インストールされていない場合：

```bash
pip install fastapi pydantic pytest httpx
```

### 3. FastAPIアプリケーションへの統合

既存の `backend/main.py` にミドルウェアを追加：

```python
from fastapi import FastAPI
from backend.services.api_key_service import APIKeyService
from backend.middleware.api_key_middleware import APIKeyMiddleware
from backend.api.routers import public_api

app = FastAPI()

# APIキーサービスの初期化
api_key_service = APIKeyService(data_dir="data/api_keys")

# ミドルウェアを追加
api_key_middleware = APIKeyMiddleware(api_key_service)
app.middleware("http")(api_key_middleware)

# ルーターを登録
app.include_router(public_api.router)

# サービスをルーターに渡す
public_api._api_key_service = api_key_service
```

### 4. テストの実行

```bash
# サービステスト
pytest backend/tests/test_api_key_service.py -v

# ミドルウェアテスト
pytest backend/tests/test_api_key_middleware.py -v

# すべてのテスト
pytest backend/tests/test_api_key*.py -v
```

### 5. APIサーバーの起動

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 6. フロントエンドの統合

React アプリケーションに `ApiKeyManager` コンポーネントを追加：

```jsx
import ApiKeyManager from './components/ApiKeyManager';

function App() {
  return (
    <div>
      <h1>Personal Recipe Intelligence</h1>
      <ApiKeyManager />
    </div>
  );
}
```

---

## 初回使用ガイド

### 1. 最初のAPIキーを作成

```bash
curl -X POST http://localhost:8001/api/v1/public/keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin Key",
    "read_recipes": true,
    "write_recipes": true,
    "delete_recipes": true,
    "read_tags": true,
    "write_tags": true,
    "requests_per_minute": 120,
    "requests_per_hour": 5000,
    "requests_per_day": 50000
  }'
```

レスポンスから `api_key` をコピーして保存してください。

### 2. APIキーをテスト

```bash
# 環境変数に設定
export API_KEY="<生成されたAPIキー>"

# レシピ一覧を取得
curl -H "X-API-Key: $API_KEY" http://localhost:8001/api/v1/recipes
```

### 3. 使用量を確認

```bash
curl http://localhost:8001/api/v1/public/usage
```

---

## 設定のカスタマイズ

### デフォルトのレート制限を変更

`backend/services/api_key_service.py` の `RateLimit` クラス：

```python
@dataclass
class RateLimit:
  requests_per_minute: int = 120  # 60 -> 120 に変更
  requests_per_hour: int = 5000   # 1000 -> 5000 に変更
  requests_per_day: int = 50000   # 10000 -> 50000 に変更
```

### 公開エンドポイントの追加

`backend/middleware/api_key_middleware.py` の `public_paths`:

```python
public_paths = [
  "/api/v1/public/keys",
  "/api/v1/public/docs",
  "/docs",
  "/openapi.json",
  "/health",
  "/api/v1/auth/login",  # 追加例
  "/api/v1/auth/register"  # 追加例
]
```

### データ保存場所の変更

環境変数で設定：

```bash
export API_KEY_DATA_DIR="/var/lib/pri/api_keys"
```

```python
import os

api_key_service = APIKeyService(
  data_dir=os.getenv("API_KEY_DATA_DIR", "data/api_keys")
)
```

---

## トラブルシューティング

### 問題: APIキーが保存されない

**原因**: ディレクトリの書き込み権限がない

**解決策**:
```bash
chmod 700 data/api_keys
chown $USER:$USER data/api_keys
```

---

### 問題: レート制限が機能しない

**原因**: システム時刻が同期されていない

**解決策**:
```bash
# NTPで時刻を同期
sudo timedatectl set-ntp true
```

---

### 問題: 401 Unauthorized エラー

**原因**: APIキーが正しく渡されていない

**解決策**:
- ヘッダー名を確認: `X-API-Key` または `Authorization: Bearer <key>`
- キーに余分な空白や改行がないか確認
- キーが有効か確認: `curl http://localhost:8001/api/v1/public/keys`

---

### 問題: 403 Forbidden エラー

**原因**: 必要なスコープがない

**解決策**:
- キーのスコープを確認: `curl http://localhost:8001/api/v1/public/keys/<key_id>`
- 必要なスコープで新しいキーを発行

---

### 問題: 429 Too Many Requests エラー

**原因**: レート制限を超えた

**解決策**:
- レスポンスヘッダーで残りリクエスト数を確認
- リクエスト頻度を下げる
- より高い制限のキーを発行

---

## セキュリティチェックリスト

- [ ] データディレクトリの権限が 700 または 750
- [ ] `.env` ファイルが `.gitignore` に含まれている
- [ ] 本番環境で HTTPS を使用
- [ ] 不要なAPIキーを削除
- [ ] 定期的にキーをローテーション（推奨: 月次）
- [ ] 使用量ログを監視
- [ ] レート制限を適切に設定
- [ ] 最小権限の原則を適用

---

## パフォーマンス最適化

### 1. 使用量記録の自動クリーンアップ

古い記録を定期的に削除：

```python
# backend/services/api_key_service.py に追加

def cleanup_old_usage(self, days: int = 30):
  """
  古い使用量記録を削除

  Args:
    days: 保持期間（日数）
  """
  cutoff = time.time() - (days * 86400)

  for key_id in self.usage.keys():
    self.usage[key_id] = [
      r for r in self.usage[key_id]
      if r.timestamp > cutoff
    ]

  self._save_usage()
```

cronで実行：
```bash
# 毎日午前3時に実行
0 3 * * * python -c "from backend.services.api_key_service import APIKeyService; s = APIKeyService(); s.cleanup_old_usage(30)"
```

### 2. 非同期保存

高トラフィック環境では、使用量記録を非同期で保存：

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)

async def record_usage_async(self, key_id: str, endpoint: str, status_code: int):
  """非同期で使用量を記録"""
  loop = asyncio.get_event_loop()
  await loop.run_in_executor(
    executor,
    self.record_usage,
    key_id,
    endpoint,
    status_code
  )
```

---

## 監視とアラート

### 使用量の監視

Prometheus形式でメトリクスを公開：

```python
from prometheus_client import Counter, Histogram

api_requests = Counter(
  'api_requests_total',
  'Total API requests',
  ['key_id', 'endpoint', 'status']
)

api_latency = Histogram(
  'api_request_duration_seconds',
  'API request latency'
)
```

### アラート設定

レート制限超過時にSlack通知：

```python
import requests

def send_alert(key_id: str, message: str):
  webhook_url = os.getenv("SLACK_WEBHOOK_URL")
  if webhook_url:
    requests.post(webhook_url, json={
      "text": f"⚠️ API Alert: {message} (Key: {key_id})"
    })
```

---

## バックアップとリストア

### バックアップ

```bash
#!/bin/bash
# backup-api-keys.sh

BACKUP_DIR="/var/backups/pri"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# APIキーデータをバックアップ
tar -czf "$BACKUP_DIR/api_keys_$TIMESTAMP.tar.gz" data/api_keys/

# 古いバックアップを削除（30日以上前）
find "$BACKUP_DIR" -name "api_keys_*.tar.gz" -mtime +30 -delete

echo "Backup completed: api_keys_$TIMESTAMP.tar.gz"
```

### リストア

```bash
#!/bin/bash
# restore-api-keys.sh

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

# 現在のデータをバックアップ
mv data/api_keys data/api_keys.old

# リストア
tar -xzf "$BACKUP_FILE" -C .

echo "Restore completed"
```

---

## まとめ

Phase 14-3 のAPI公開機能により、Personal Recipe Intelligence は安全で柔軟なAPI認証システムを備えました。

**実装されたファイル**:
- `backend/services/api_key_service.py` - コアサービス
- `backend/middleware/api_key_middleware.py` - 認証ミドルウェア
- `backend/api/routers/public_api.py` - 管理エンドポイント
- `frontend/components/ApiKeyManager.jsx` - 管理UI
- `backend/tests/test_api_key_service.py` - サービステスト
- `backend/tests/test_api_key_middleware.py` - ミドルウェアテスト

**次のステップ**:
1. 本番環境へのデプロイ
2. HTTPS証明書の設定
3. 監視システムの構築
4. ドキュメントの整備

詳細な使用例は [api-key-integration-example.md](./api-key-integration-example.md) を参照してください。

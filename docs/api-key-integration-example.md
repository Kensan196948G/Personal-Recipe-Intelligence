# API Key Integration Example

Personal Recipe Intelligence の API公開機能の統合例です。

## 目次
- [FastAPI統合](#fastapi統合)
- [使用例](#使用例)
- [セキュリティのベストプラクティス](#セキュリティのベストプラクティス)

---

## FastAPI統合

### 1. メインアプリケーションへの統合

```python
# backend/main.py

from fastapi import FastAPI
from backend.services.api_key_service import APIKeyService
from backend.middleware.api_key_middleware import APIKeyMiddleware
from backend.api.routers import public_api, recipes, tags

app = FastAPI(
  title="Personal Recipe Intelligence API",
  description="個人向けレシピ管理システム",
  version="1.0.0"
)

# APIキーサービスの初期化
api_key_service = APIKeyService(data_dir="data/api_keys")

# ミドルウェアの追加（認証が必要なエンドポイント用）
api_key_middleware = APIKeyMiddleware(api_key_service)
app.middleware("http")(api_key_middleware)

# ルーターの登録
app.include_router(public_api.router)  # 公開API管理
app.include_router(recipes.router)     # レシピAPI（認証必要）
app.include_router(tags.router)        # タグAPI（認証必要）

# 公開API管理サービスをルーターに渡す
public_api._api_key_service = api_key_service

@app.get("/health")
async def health_check():
  """ヘルスチェック（認証不要）"""
  return {"status": "ok", "service": "Personal Recipe Intelligence"}
```

---

## 使用例

### 1. APIキーの発行

```bash
# cURLでAPIキーを発行
curl -X POST http://localhost:8000/api/v1/public/keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Application",
    "read_recipes": true,
    "write_recipes": true,
    "delete_recipes": false,
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "requests_per_day": 10000
  }'
```

レスポンス:
```json
{
  "status": "ok",
  "data": {
    "api_key": "xYz123AbC...",
    "key_info": {
      "key_id": "abc123",
      "name": "My Application",
      "scope": {
        "read_recipes": true,
        "write_recipes": true,
        "delete_recipes": false,
        "read_tags": true,
        "write_tags": false
      },
      "rate_limit": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "requests_per_day": 10000
      },
      "created_at": "2025-12-11T10:00:00",
      "is_active": true
    },
    "message": "API key created successfully. Please save this key securely as it won't be shown again."
  }
}
```

**重要**: APIキー文字列は一度しか表示されません。必ず安全に保存してください。

---

### 2. APIキーを使ったリクエスト

#### X-API-Keyヘッダーを使用

```bash
curl -X GET http://localhost:8000/api/v1/recipes \
  -H "X-API-Key: xYz123AbC..."
```

#### Authorizationヘッダー（Bearer形式）を使用

```bash
curl -X GET http://localhost:8000/api/v1/recipes \
  -H "Authorization: Bearer xYz123AbC..."
```

---

### 3. Pythonでの使用例

```python
import requests

# APIキーを設定
API_KEY = "xYz123AbC..."
BASE_URL = "http://localhost:8000"

# ヘッダーを設定
headers = {
  "X-API-Key": API_KEY
}

# レシピ一覧を取得
response = requests.get(f"{BASE_URL}/api/v1/recipes", headers=headers)

if response.status_code == 200:
  data = response.json()
  print(f"取得したレシピ数: {len(data['data']['recipes'])}")
else:
  print(f"エラー: {response.json()['error']}")

# レシピを作成（書き込み権限が必要）
new_recipe = {
  "title": "カレーライス",
  "ingredients": ["玉ねぎ", "人参", "じゃがいも"],
  "steps": ["材料を切る", "炒める", "煮込む"]
}

response = requests.post(
  f"{BASE_URL}/api/v1/recipes",
  json=new_recipe,
  headers=headers
)

if response.status_code == 200:
  print("レシピを作成しました")
else:
  print(f"エラー: {response.json()['error']}")
```

---

### 4. JavaScriptでの使用例

```javascript
// APIキーを設定
const API_KEY = 'xYz123AbC...';
const BASE_URL = 'http://localhost:8000';

// レシピ一覧を取得
async function getRecipes() {
  try {
    const response = await fetch(`${BASE_URL}/api/v1/recipes`, {
      headers: {
        'X-API-Key': API_KEY
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('取得したレシピ:', data.data.recipes);

    // レート制限情報を確認
    console.log('残りリクエスト数（分）:', response.headers.get('X-RateLimit-Remaining-Minute'));
    console.log('残りリクエスト数（時）:', response.headers.get('X-RateLimit-Remaining-Hour'));

  } catch (error) {
    console.error('エラー:', error);
  }
}

// レシピを作成
async function createRecipe(recipe) {
  try {
    const response = await fetch(`${BASE_URL}/api/v1/recipes`, {
      method: 'POST',
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(recipe)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('レシピを作成しました:', data.data);

  } catch (error) {
    console.error('エラー:', error);
  }
}

// 使用例
getRecipes();

createRecipe({
  title: 'カレーライス',
  ingredients: ['玉ねぎ', '人参', 'じゃがいも'],
  steps: ['材料を切る', '炒める', '煮込む']
});
```

---

### 5. 使用量の確認

```bash
# 特定のAPIキーの使用量を確認
curl -X GET http://localhost:8000/api/v1/public/usage/abc123
```

レスポンス:
```json
{
  "status": "ok",
  "data": {
    "key_id": "abc123",
    "total_requests": 150,
    "last_used_at": "2025-12-11T14:30:00",
    "current_usage": {
      "last_minute": 5,
      "last_hour": 45,
      "last_day": 150
    },
    "rate_limits": {
      "per_minute": 60,
      "per_hour": 1000,
      "per_day": 10000
    },
    "remaining": {
      "per_minute": 55,
      "per_hour": 955,
      "per_day": 9850
    }
  }
}
```

---

### 6. APIキー一覧の取得

```bash
curl -X GET http://localhost:8000/api/v1/public/keys
```

---

### 7. APIキーの削除

```bash
curl -X DELETE http://localhost:8000/api/v1/public/keys/abc123
```

---

### 8. APIキーのローテーション

```bash
# 古いキーを無効化し、新しいキーを発行
curl -X POST http://localhost:8000/api/v1/public/keys/abc123/rotate
```

---

## セキュリティのベストプラクティス

### 1. APIキーの安全な保管

```bash
# 環境変数として保存
export PRI_API_KEY="xYz123AbC..."

# .envファイルで管理（.gitignoreに追加）
echo "PRI_API_KEY=xYz123AbC..." > .env
```

### 2. HTTPSの使用

本番環境では必ずHTTPSを使用してください。

```python
# nginx設定例
server {
  listen 443 ssl;
  server_name api.example.com;

  ssl_certificate /path/to/cert.pem;
  ssl_certificate_key /path/to/key.pem;

  location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

### 3. 最小権限の原則

必要最小限のスコープでAPIキーを発行してください。

```json
{
  "name": "Read Only App",
  "read_recipes": true,
  "write_recipes": false,
  "delete_recipes": false,
  "read_tags": true,
  "write_tags": false
}
```

### 4. レート制限の適切な設定

アプリケーションの用途に応じてレート制限を設定してください。

- **ダッシュボード**: 低い制限（10req/min）
- **一般アプリ**: 標準制限（60req/min）
- **バッチ処理**: 高い制限（120req/min）

### 5. 定期的なキーローテーション

セキュリティのため、定期的にAPIキーをローテーションしてください。

```bash
# 月次でローテーション
curl -X POST http://localhost:8000/api/v1/public/keys/abc123/rotate
```

### 6. 監査ログの確認

使用量統計を定期的に確認し、異常なアクセスがないかチェックしてください。

```bash
curl -X GET http://localhost:8000/api/v1/public/usage
```

---

## エラーハンドリング

### 401 Unauthorized - APIキーが無効

```json
{
  "status": "error",
  "error": "Invalid API key",
  "data": null
}
```

**対処法**: APIキーが正しいか確認してください。

---

### 403 Forbidden - 権限不足

```json
{
  "status": "error",
  "error": "Insufficient permissions",
  "data": null
}
```

**対処法**: 必要なスコープを持つAPIキーを使用してください。

---

### 429 Too Many Requests - レート制限超過

```json
{
  "status": "error",
  "error": "Rate limit exceeded: 60 requests per minute",
  "data": null
}
```

**対処法**:
- リクエスト頻度を下げる
- レスポンスヘッダーの `X-RateLimit-Remaining-*` を確認
- より高い制限のAPIキーを発行

---

## まとめ

Personal Recipe Intelligence API は、安全で柔軟なAPIキー認証システムを提供します。

- **簡単な統合**: 数行のコードで認証を追加
- **柔軟なスコープ**: 細かい権限制御
- **レート制限**: 悪用を防止
- **使用量トラッキング**: 詳細な統計情報

詳細は [API Documentation](http://localhost:8000/docs) を参照してください。

# API Key 認証システム - Personal Recipe Intelligence

## 概要

Personal Recipe Intelligence API は **Bearer Token 形式の API Key 認証** を実装しています。

CLAUDE.md セクション 5（セキュリティ）に準拠した設計です。

---

## セットアップ

### 1. 環境変数設定

プロジェクトルートに `.env` ファイルを作成し、API Key を設定します：

```bash
# .env.example をコピー
cp env.example .env

# セキュアな API Key を生成
openssl rand -hex 32

# .env ファイルを編集
nano .env
```

`.env` の例：

```env
API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
DATABASE_URL=sqlite:///./data/recipes.db
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 2. 依存パッケージインストール

```bash
cd backend
pip install -r requirements.txt
```

### 3. API 起動

```bash
python main.py
```

または

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API 使用方法

### 認証不要エンドポイント

以下のエンドポイントは API Key なしでアクセス可能です：

- `GET /health` - ヘルスチェック
- `GET /` - ルートエンドポイント
- `GET /docs` - Swagger UI（API ドキュメント）
- `GET /redoc` - ReDoc（API ドキュメント）

例：

```bash
curl http://localhost:8000/health
```

レスポンス：

```json
{
  "status": "ok",
  "data": {
    "service": "Personal Recipe Intelligence API",
    "version": "1.0.0",
    "health": "healthy"
  },
  "error": null
}
```

---

### 認証必要エンドポイント

`/api/v1/*` 以下のエンドポイントは **API Key 認証が必須** です。

#### リクエスト方法

**Authorization ヘッダーに Bearer Token を追加**：

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8000/api/v1/recipes
```

例：

```bash
curl -H "Authorization: Bearer a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
  http://localhost:8000/api/v1/recipes
```

成功レスポンス：

```json
{
  "status": "ok",
  "data": {
    "recipes": [],
    "total": 0
  },
  "error": null
}
```

---

### エラーレスポンス

#### 1. API Key がない場合

```bash
curl http://localhost:8000/api/v1/recipes
```

レスポンス（401 Unauthorized）：

```json
{
  "status": "error",
  "data": null,
  "error": "Missing Authorization header"
}
```

#### 2. 無効な認証スキーム

```bash
curl -H "Authorization: Basic dGVzdDp0ZXN0" \
  http://localhost:8000/api/v1/recipes
```

レスポンス（401 Unauthorized）：

```json
{
  "status": "error",
  "data": null,
  "error": "Invalid authentication scheme. Use 'Bearer <token>'"
}
```

#### 3. 無効な API Key

```bash
curl -H "Authorization: Bearer wrong_key" \
  http://localhost:8000/api/v1/recipes
```

レスポンス（401 Unauthorized）：

```json
{
  "status": "error",
  "data": null,
  "error": "Invalid API Key"
}
```

---

## セキュリティ仕様

### 1. Bearer Token 形式

API Key は **Bearer Token** として送信します：

```
Authorization: Bearer <API_KEY>
```

### 2. API Key マスキング

ログに API Key が出力される際は自動的にマスキングされます：

```
Original: a1b2c3d4e5f6g7h8i9j0
Masked:   a1b***j0
```

### 3. 除外パス

以下のパスは認証をバイパスします：

- `/health`
- `/`
- `/docs`
- `/openapi.json`
- `/redoc`

除外パスは `backend/middleware/auth_middleware.py` で定義されています。

### 4. 環境変数管理

- `.env` ファイルは **絶対に Git にコミットしない**
- `.gitignore` に `.env` を追加済み
- `.env.example` で設定例を提供

---

## テスト

### ユニットテスト実行

```bash
cd backend
pytest tests/test_auth.py -v
pytest tests/test_auth_middleware.py -v
```

### カバレッジ測定

```bash
pytest --cov=api --cov=middleware --cov-report=html
```

### すべてのテスト実行

```bash
pytest tests/ -v --cov
```

---

## トラブルシューティング

### 問題: `API_KEY environment variable is not set`

**原因**: `.env` ファイルが存在しないか、`API_KEY` が設定されていない

**解決**:

```bash
# .env ファイルを作成
cp env.example .env

# API Key を生成して設定
openssl rand -hex 32
# → 出力された値を .env の API_KEY に設定
```

### 問題: `Invalid API Key` エラーが発生

**原因**: リクエストの API Key と `.env` の `API_KEY` が一致しない

**解決**:

1. `.env` ファイルの `API_KEY` を確認
2. リクエストの Authorization ヘッダーに正しい API Key を設定

```bash
# 正しい形式
curl -H "Authorization: Bearer $(grep API_KEY .env | cut -d '=' -f2)" \
  http://localhost:8000/api/v1/recipes
```

### 問題: 認証が常にスキップされる

**原因**: エンドポイントが除外パスに含まれている

**解決**: `backend/middleware/auth_middleware.py` の `excluded_paths` を確認

---

## アーキテクチャ

```
┌─────────────────┐
│   Client        │
└────────┬────────┘
         │ Authorization: Bearer <API_KEY>
         ▼
┌─────────────────┐
│  AuthMiddleware │  ← 認証チェック
└────────┬────────┘
         │ 認証成功
         ▼
┌─────────────────┐
│  API Endpoint   │
└─────────────────┘
```

### ファイル構成

```
backend/
├── main.py                    # FastAPI アプリケーション
├── api/
│   ├── __init__.py
│   └── auth.py                # API Key 認証ロジック
├── middleware/
│   ├── __init__.py
│   └── auth_middleware.py     # 認証ミドルウェア
└── tests/
    ├── conftest.py            # pytest 設定
    ├── test_auth.py           # 認証ロジックテスト
    └── test_auth_middleware.py # ミドルウェアテスト
```

---

## 参考

- [CLAUDE.md - セキュリティ要件](/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/CLAUDE.md#5-セキュリティ)
- [FastAPI - Security](https://fastapi.tiangolo.com/tutorial/security/)
- [RFC 6750 - The OAuth 2.0 Authorization Framework: Bearer Token Usage](https://tools.ietf.org/html/rfc6750)

---

## ライセンス

MIT License

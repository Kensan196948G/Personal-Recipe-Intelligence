# バックエンド概要 (Backend Overview)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のバックエンド技術スタックと構成について説明する。

## 2. 技術スタック

### 2.1 主要技術

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.11 | プログラミング言語 |
| FastAPI | 0.104+ | Web フレームワーク |
| SQLModel | 0.0.14+ | ORM |
| SQLite | 3 | データベース |
| Pydantic | 2.x | バリデーション |
| Uvicorn | 0.24+ | ASGI サーバー |

### 2.2 選定理由

**FastAPI**
- 高速なパフォーマンス（Starlette ベース）
- 自動 OpenAPI ドキュメント生成
- Python 型ヒントによるバリデーション
- 非同期処理のネイティブサポート

**SQLModel**
- SQLAlchemy + Pydantic の統合
- 型安全なクエリ
- シンプルな API

**SQLite**
- サーバーレス（設定不要）
- 軽量・ポータブル
- 個人利用に最適

## 3. ディレクトリ構成

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py              # アプリケーションエントリポイント
│   ├── deps.py              # 依存性注入
│   └── routes/
│       ├── __init__.py
│       ├── recipes.py       # レシピ API
│       ├── ingredients.py   # 材料 API
│       ├── tags.py          # タグ API
│       ├── scrape.py        # スクレイピング API
│       └── ocr.py           # OCR API
├── models/
│   ├── __init__.py
│   ├── recipe.py            # レシピモデル
│   ├── ingredient.py        # 材料モデル
│   ├── tag.py               # タグモデル
│   └── source.py            # ソースモデル
├── schemas/
│   ├── __init__.py
│   ├── recipe.py            # レシピスキーマ
│   ├── response.py          # レスポンススキーマ
│   └── common.py            # 共通スキーマ
├── services/
│   ├── __init__.py
│   ├── recipe_service.py    # レシピサービス
│   ├── scraper_service.py   # スクレイピングサービス
│   ├── ocr_service.py       # OCR サービス
│   ├── translate_service.py # 翻訳サービス
│   └── cleaner_service.py   # データ正規化サービス
├── core/
│   ├── __init__.py
│   ├── config.py            # 設定
│   ├── database.py          # DB 接続
│   └── exceptions.py        # 例外定義
├── utils/
│   ├── __init__.py
│   └── helpers.py           # ユーティリティ
├── alembic/                 # マイグレーション
│   ├── env.py
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   └── test_services.py
├── alembic.ini
├── requirements.txt
└── pyproject.toml
```

## 4. アプリケーション構成

### 4.1 main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.core.database import create_db_and_tables
from backend.api.routes import recipes, ingredients, tags, scrape, ocr

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時
    create_db_and_tables()
    yield
    # 終了時

app = FastAPI(
    title="Personal Recipe Intelligence",
    description="レシピ管理 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(recipes.router, prefix="/api/v1/recipes", tags=["recipes"])
app.include_router(ingredients.router, prefix="/api/v1/ingredients", tags=["ingredients"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["tags"])
app.include_router(scrape.router, prefix="/api/v1/scrape", tags=["scrape"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["ocr"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### 4.2 依存性注入

```python
# deps.py
from typing import Generator
from sqlmodel import Session
from backend.core.database import engine

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

## 5. レイヤー設計

### 5.1 レイヤー構成

```
┌─────────────────────────────────────────────┐
│              API Layer (Routes)             │
│  - リクエスト/レスポンス処理                  │
│  - バリデーション                            │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│           Service Layer (Services)          │
│  - ビジネスロジック                          │
│  - トランザクション管理                      │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│            Data Layer (Models)              │
│  - データベースアクセス                       │
│  - ORM マッピング                            │
└─────────────────────────────────────────────┘
```

### 5.2 責務分離

| レイヤー | 責務 | 例 |
|---------|------|-----|
| Routes | HTTP 処理 | パス定義、バリデーション |
| Services | ビジネスロジック | CRUD、変換処理 |
| Models | データ永続化 | SQLModel 定義 |
| Schemas | データ転送 | Pydantic モデル |

## 6. 設定管理

### 6.1 config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # アプリケーション
    app_name: str = "Personal Recipe Intelligence"
    debug: bool = False

    # データベース
    database_url: str = "sqlite:///./data/pri.db"

    # 外部API
    deepl_api_key: str = ""

    # ファイル
    upload_dir: str = "./data/images"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

## 7. 開発環境セットアップ

### 7.1 セットアップ手順

```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env

# マイグレーション実行
alembic upgrade head

# 開発サーバー起動
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 requirements.txt

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
pydantic>=2.0.0
pydantic-settings>=2.0.0
alembic>=1.13.0
python-multipart>=0.0.6
httpx>=0.25.0
beautifulsoup4>=4.12.0
Pillow>=10.0.0
```

## 8. APIドキュメント

### 8.1 Swagger UI

開発サーバー起動後、以下のURLでアクセス可能：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## 9. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

# Personal Recipe Intelligence - システムアーキテクチャ

## 概要

Personal Recipe Intelligence (PRI) は、レシピ収集・管理のための個人向けシステムです。
本ドキュメントはシステム全体のアーキテクチャを定義します。

---

## システム構成図

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Svelte WebUI                            │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │  │
│  │  │ Recipe │ │ Search │ │  Tag   │ │ Import │            │  │
│  │  │  List  │ │  View  │ │Manager │ │  View  │            │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Server                         │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │  │
│  │  │/recipes│ │/scrape │ │  /ocr  │ │ /tags  │            │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Scraper  │ │   OCR    │ │Translator│ │ Cleaner  │          │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      SQLite DB                            │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │  │
│  │  │recipes │ │ingredi-│ │ steps  │ │  tags  │            │  │
│  │  │        │ │  ents  │ │        │ │        │            │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## コンポーネント詳細

### Frontend (Svelte)

```
frontend/
├── src/
│   ├── App.svelte          # メインアプリケーション
│   ├── components/         # 共通コンポーネント
│   │   ├── RecipeCard.svelte
│   │   ├── RecipeList.svelte
│   │   ├── SearchBar.svelte
│   │   └── TagFilter.svelte
│   ├── pages/              # ページコンポーネント
│   │   ├── Home.svelte
│   │   ├── RecipeDetail.svelte
│   │   └── Import.svelte
│   ├── stores/             # 状態管理
│   │   └── recipes.js
│   └── lib/                # ユーティリティ
│       └── api.js
└── tests/
```

### Backend (FastAPI)

```
backend/
├── api/
│   ├── main.py             # FastAPIアプリケーション
│   ├── routes/             # ルート定義
│   │   ├── recipes.py
│   │   ├── scrape.py
│   │   ├── ocr.py
│   │   └── tags.py
│   └── dependencies.py     # 依存性注入
├── models/
│   ├── recipe.py           # データモデル
│   └── schemas.py          # Pydanticスキーマ
├── services/
│   ├── recipe_service.py   # レシピ操作
│   └── search_service.py   # 検索機能
├── scraper/
│   ├── base.py             # 基底クラス
│   ├── cookpad.py          # クックパッド用
│   └── allrecipes.py       # Allrecipes用
├── ocr/
│   └── extractor.py        # OCR処理
├── translation/
│   └── deepl.py            # DeepL連携
└── tests/
```

---

## データフロー

### レシピ取得フロー（Webスクレイピング）

```mermaid
sequenceDiagram
    participant U as User
    participant UI as WebUI
    participant API as FastAPI
    participant SC as Scraper
    participant TR as Translator
    participant CL as Cleaner
    participant DB as SQLite

    U->>UI: URL入力
    UI->>API: POST /api/v1/scrape
    API->>SC: スクレイピング実行
    SC->>SC: HTML解析
    SC-->>API: 生データ

    alt 海外サイト
        API->>TR: 翻訳リクエスト
        TR->>TR: DeepL API呼び出し
        TR-->>API: 翻訳済みデータ
    end

    API->>CL: 正規化リクエスト
    CL->>CL: 材料・手順正規化
    CL-->>API: 正規化データ

    API->>DB: レシピ保存
    DB-->>API: 保存結果
    API-->>UI: レシピデータ
    UI-->>U: 結果表示
```

### レシピ取得フロー（OCR）

```mermaid
sequenceDiagram
    participant U as User
    participant UI as WebUI
    participant API as FastAPI
    participant OCR as OCR Service
    participant CL as Cleaner
    participant DB as SQLite

    U->>UI: 画像アップロード
    UI->>API: POST /api/v1/ocr
    API->>OCR: 画像解析
    OCR->>OCR: Claude Vision処理
    OCR-->>API: 抽出テキスト

    API->>CL: 正規化リクエスト
    CL->>CL: 材料・手順正規化
    CL-->>API: 正規化データ

    API->>DB: レシピ保存
    DB-->>API: 保存結果
    API-->>UI: レシピデータ
    UI-->>U: 結果表示
```

---

## データベース設計

### ER図

```mermaid
erDiagram
    RECIPE ||--o{ INGREDIENT : has
    RECIPE ||--o{ STEP : has
    RECIPE ||--o{ RECIPE_TAG : has
    TAG ||--o{ RECIPE_TAG : has
    SOURCE ||--o{ RECIPE : from

    RECIPE {
        int id PK
        string title
        string description
        int servings
        int prep_time_minutes
        int cook_time_minutes
        string source_url
        string source_type
        datetime created_at
        datetime updated_at
    }

    INGREDIENT {
        int id PK
        int recipe_id FK
        string name
        string name_normalized
        float amount
        string unit
        string note
        int order
    }

    STEP {
        int id PK
        int recipe_id FK
        int order
        string description
    }

    TAG {
        int id PK
        string name UK
    }

    RECIPE_TAG {
        int id PK
        int recipe_id FK
        int tag_id FK
    }

    SOURCE {
        int id PK
        string name
        string url_pattern
        string scraper_config
    }
```

---

## SubAgents アーキテクチャ

### エージェント構成

```
┌─────────────────────────────────────────────────────────────────┐
│                      PlannerAgent                               │
│                    (タスク分解・割当)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ ScraperAgent │     │   OcrAgent   │     │  DevAPI/UI   │
│  (MCP使用)   │     │  (MCP使用)   │     │   Agent      │
└──────────────┘     └──────────────┘     └──────────────┘
        │                     │
        └──────────┬──────────┘
                   ▼
         ┌──────────────┐
         │Translation   │
         │   Agent      │
         └──────────────┘
                   │
                   ▼
         ┌──────────────┐
         │  Cleaner     │
         │   Agent      │
         └──────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌──────────────┐     ┌──────────────┐
│   QaAgent    │     │ WriterAgent  │
└──────────────┘     └──────────────┘
```

### MCP制御

```
┌─────────────────────────────────────────────────────────────────┐
│                       MCP Manager                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Browser MCP ──X── Puppeteer MCP (同時起動禁止)          │  │
│  │       │                   │                               │  │
│  │       └───────┬───────────┘                               │  │
│  │               │                                           │  │
│  │       Filesystem MCP                                      │  │
│  │                                                           │  │
│  │  Max Concurrent: 1                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## セキュリティアーキテクチャ

### 認証・認可

```
┌─────────────────────────────────────────────────────────────────┐
│                      Security Layer                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Key Authentication                                   │  │
│  │  - Header: X-API-Key                                      │  │
│  │  - 個人利用のためシンプルな認証                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Input Validation (Pydantic)                              │  │
│  │  - 全APIエンドポイントでバリデーション                    │  │
│  │  - SQLインジェクション対策                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Logging & Audit                                          │  │
│  │  - 機密データのマスキング                                 │  │
│  │  - 操作ログの記録                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 技術スタック

| レイヤー | 技術 | バージョン |
|---------|------|-----------|
| Frontend | Svelte | 4.x |
| Build Tool | Vite + Bun | 5.x |
| Backend | FastAPI | 0.104+ |
| ORM | SQLModel | 0.0.14+ |
| Database | SQLite | 3.x |
| Migration | Alembic | 1.13+ |
| Testing | pytest / bun test | - |
| Linting | Ruff / ESLint | - |
| Formatting | Black / Prettier | - |

---

## デプロイメント

### ローカル開発環境

```bash
# 起動コマンド
./scripts/dev.sh

# 構成
# - Backend: http://127.0.0.1:8000
# - Frontend: http://127.0.0.1:5173
# - Database: data/db/recipes.db
```

### 本番環境（将来）

- Docker コンテナ化
- リバースプロキシ（Nginx）
- HTTPS対応

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

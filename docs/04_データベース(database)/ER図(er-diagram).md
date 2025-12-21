# ER図 (ER Diagram)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のデータベース構造を ER 図で表現する。

## 2. ER図（全体）

```mermaid
erDiagram
    RECIPE ||--o{ RECIPE_INGREDIENT : has
    RECIPE ||--o{ RECIPE_STEP : has
    RECIPE ||--o{ RECIPE_TAG : has
    RECIPE ||--o| RECIPE_SOURCE : has
    TAG ||--o{ RECIPE_TAG : belongs
    INGREDIENT ||--o{ RECIPE_INGREDIENT : used_in
    TRANSLATION_CACHE ||--o| RECIPE : translates

    RECIPE {
        int id PK
        string title
        string title_original
        text description
        int servings
        int prep_time_minutes
        int cook_time_minutes
        string image_path
        string language
        datetime created_at
        datetime updated_at
        boolean is_deleted
    }

    INGREDIENT {
        int id PK
        string name
        string name_normalized
        string category
        datetime created_at
    }

    RECIPE_INGREDIENT {
        int id PK
        int recipe_id FK
        int ingredient_id FK
        float amount
        string unit
        string note
        int order_index
    }

    RECIPE_STEP {
        int id PK
        int recipe_id FK
        int step_number
        text description
        string image_path
    }

    TAG {
        int id PK
        string name
        string category
        string color
        datetime created_at
    }

    RECIPE_TAG {
        int id PK
        int recipe_id FK
        int tag_id FK
    }

    RECIPE_SOURCE {
        int id PK
        int recipe_id FK
        string source_type
        string source_url
        string source_site
        datetime scraped_at
    }

    TRANSLATION_CACHE {
        int id PK
        string source_text_hash
        string source_text
        string translated_text
        string source_lang
        string target_lang
        datetime created_at
        datetime expires_at
    }
```

## 3. テーブル関連図

```
                    ┌──────────────────┐
                    │     RECIPE       │
                    │──────────────────│
                    │ id (PK)          │
                    │ title            │
                    │ description      │
                    │ servings         │
                    │ prep_time_minutes│
                    │ cook_time_minutes│
                    │ image_path       │
                    │ language         │
                    │ created_at       │
                    │ updated_at       │
                    │ is_deleted       │
                    └──────────────────┘
                           │ 1
                           │
         ┌─────────────────┼─────────────────┬─────────────────┐
         │                 │                 │                 │
         ▼ *               ▼ *               ▼ *               ▼ 0..1
┌─────────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│RECIPE_INGREDIENT│ │ RECIPE_STEP │ │ RECIPE_TAG  │ │  RECIPE_SOURCE  │
│─────────────────│ │─────────────│ │─────────────│ │─────────────────│
│ id (PK)         │ │ id (PK)     │ │ id (PK)     │ │ id (PK)         │
│ recipe_id (FK)  │ │ recipe_id   │ │ recipe_id   │ │ recipe_id (FK)  │
│ ingredient_id   │ │ step_number │ │ tag_id (FK) │ │ source_type     │
│ amount          │ │ description │ └─────────────┘ │ source_url      │
│ unit            │ │ image_path  │        │        │ source_site     │
│ order_index     │ └─────────────┘        │        │ scraped_at      │
└─────────────────┘                        │        └─────────────────┘
         │ *                               │ *
         │                                 │
         ▼ 1                               ▼ 1
┌─────────────────┐                 ┌─────────────┐
│   INGREDIENT    │                 │     TAG     │
│─────────────────│                 │─────────────│
│ id (PK)         │                 │ id (PK)     │
│ name            │                 │ name        │
│ name_normalized │                 │ category    │
│ category        │                 │ color       │
│ created_at      │                 │ created_at  │
└─────────────────┘                 └─────────────┘
```

## 4. カーディナリティ

| 関係 | カーディナリティ | 説明 |
|------|-----------------|------|
| RECIPE - RECIPE_INGREDIENT | 1:N | 1レシピに複数の材料 |
| RECIPE - RECIPE_STEP | 1:N | 1レシピに複数の手順 |
| RECIPE - RECIPE_TAG | 1:N | 1レシピに複数のタグ |
| RECIPE - RECIPE_SOURCE | 1:0..1 | 1レシピに0または1つのソース |
| INGREDIENT - RECIPE_INGREDIENT | 1:N | 1材料が複数レシピで使用 |
| TAG - RECIPE_TAG | 1:N | 1タグが複数レシピに付与 |

## 5. インデックス設計

```sql
-- RECIPE テーブル
CREATE INDEX idx_recipe_title ON recipe(title);
CREATE INDEX idx_recipe_created_at ON recipe(created_at);
CREATE INDEX idx_recipe_is_deleted ON recipe(is_deleted);

-- INGREDIENT テーブル
CREATE UNIQUE INDEX idx_ingredient_name ON ingredient(name_normalized);

-- TAG テーブル
CREATE UNIQUE INDEX idx_tag_name ON tag(name);

-- RECIPE_INGREDIENT テーブル
CREATE INDEX idx_recipe_ingredient_recipe ON recipe_ingredient(recipe_id);
CREATE INDEX idx_recipe_ingredient_ingredient ON recipe_ingredient(ingredient_id);

-- RECIPE_TAG テーブル
CREATE INDEX idx_recipe_tag_recipe ON recipe_tag(recipe_id);
CREATE INDEX idx_recipe_tag_tag ON recipe_tag(tag_id);

-- TRANSLATION_CACHE テーブル
CREATE UNIQUE INDEX idx_translation_hash ON translation_cache(source_text_hash);
```

## 6. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

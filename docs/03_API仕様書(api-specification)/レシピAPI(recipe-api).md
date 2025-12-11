# レシピAPI (Recipe API)

## 1. 概要

レシピの CRUD 操作を提供する API エンドポイントの詳細仕様。

## 2. エンドポイント詳細

### 2.1 レシピ一覧取得

**GET /api/v1/recipes**

レシピの一覧を取得する。

#### リクエスト

**クエリパラメータ**
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|------------|-----|------|-----------|------|
| page | int | No | 1 | ページ番号 |
| per_page | int | No | 20 | 1ページあたりの件数 |
| sort | string | No | created_at | ソート項目 |
| order | string | No | desc | ソート順序 (asc/desc) |

#### レスポンス

**200 OK**
```json
{
  "status": "ok",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "カレーライス",
        "description": "定番の家庭料理",
        "servings": 4,
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "image_path": "/images/curry.jpg",
        "source_url": null,
        "created_at": "2024-12-11T10:00:00Z",
        "updated_at": "2024-12-11T10:00:00Z",
        "tags": [
          {"id": 1, "name": "和食"},
          {"id": 2, "name": "簡単"}
        ]
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20,
    "pages": 3
  }
}
```

---

### 2.2 レシピ詳細取得

**GET /api/v1/recipes/{id}**

特定のレシピの詳細情報を取得する。

#### パスパラメータ
| パラメータ | 型 | 説明 |
|------------|-----|------|
| id | int | レシピID |

#### レスポンス

**200 OK**
```json
{
  "status": "ok",
  "data": {
    "id": 1,
    "title": "カレーライス",
    "description": "定番の家庭料理。スパイスの効いた本格派。",
    "servings": 4,
    "prep_time_minutes": 15,
    "cook_time_minutes": 30,
    "image_path": "/images/curry.jpg",
    "source_url": "https://example.com/recipe/1",
    "created_at": "2024-12-11T10:00:00Z",
    "updated_at": "2024-12-11T10:00:00Z",
    "ingredients": [
      {
        "id": 1,
        "name": "たまねぎ",
        "name_normalized": "たまねぎ",
        "amount": 2,
        "unit": "個",
        "order_index": 1
      },
      {
        "id": 2,
        "name": "にんじん",
        "name_normalized": "にんじん",
        "amount": 1,
        "unit": "本",
        "order_index": 2
      }
    ],
    "steps": [
      {
        "id": 1,
        "step_number": 1,
        "description": "たまねぎを薄切りにする"
      },
      {
        "id": 2,
        "step_number": 2,
        "description": "にんじんを乱切りにする"
      }
    ],
    "tags": [
      {"id": 1, "name": "和食"},
      {"id": 2, "name": "簡単"}
    ]
  }
}
```

**404 Not Found**
```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "レシピが見つかりません"
  }
}
```

---

### 2.3 レシピ作成

**POST /api/v1/recipes**

新しいレシピを作成する。

#### リクエストボディ

```json
{
  "title": "カレーライス",
  "description": "定番の家庭料理",
  "servings": 4,
  "prep_time_minutes": 15,
  "cook_time_minutes": 30,
  "ingredients": [
    {
      "name": "たまねぎ",
      "amount": 2,
      "unit": "個"
    },
    {
      "name": "にんじん",
      "amount": 1,
      "unit": "本"
    }
  ],
  "steps": [
    {
      "description": "たまねぎを薄切りにする"
    },
    {
      "description": "にんじんを乱切りにする"
    }
  ],
  "tag_ids": [1, 2]
}
```

**バリデーションルール**
| フィールド | ルール |
|-----------|--------|
| title | 必須、1-200文字 |
| description | 任意、最大2000文字 |
| servings | 任意、1-100 |
| prep_time_minutes | 任意、0-1440 |
| cook_time_minutes | 任意、0-1440 |
| ingredients | 必須、1件以上 |
| steps | 必須、1件以上 |

#### レスポンス

**201 Created**
```json
{
  "status": "ok",
  "data": {
    "id": 1,
    "title": "カレーライス",
    ...
  }
}
```

**422 Unprocessable Entity**
```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "バリデーションエラー",
    "details": [
      {
        "field": "title",
        "message": "タイトルは必須です"
      }
    ]
  }
}
```

---

### 2.4 レシピ更新

**PUT /api/v1/recipes/{id}**

既存のレシピを更新する。

#### パスパラメータ
| パラメータ | 型 | 説明 |
|------------|-----|------|
| id | int | レシピID |

#### リクエストボディ

```json
{
  "title": "カレーライス（改良版）",
  "description": "スパイスを追加した改良版",
  "servings": 4,
  "prep_time_minutes": 20,
  "cook_time_minutes": 35,
  "ingredients": [
    {
      "id": 1,
      "name": "たまねぎ",
      "amount": 3,
      "unit": "個"
    }
  ],
  "steps": [
    {
      "id": 1,
      "description": "たまねぎをみじん切りにする"
    }
  ],
  "tag_ids": [1, 2, 3]
}
```

#### レスポンス

**200 OK**
```json
{
  "status": "ok",
  "data": {
    "id": 1,
    "title": "カレーライス（改良版）",
    ...
  }
}
```

---

### 2.5 レシピ削除

**DELETE /api/v1/recipes/{id}**

レシピを削除する（論理削除）。

#### パスパラメータ
| パラメータ | 型 | 説明 |
|------------|-----|------|
| id | int | レシピID |

#### レスポンス

**204 No Content**

---

### 2.6 レシピ検索

**GET /api/v1/recipes/search**

レシピを検索する。

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|------------|-----|------|------|
| q | string | No | キーワード検索 |
| tag_ids | array | No | タグIDで絞り込み |
| ingredient | string | No | 材料名で絞り込み |
| min_time | int | No | 最小調理時間 |
| max_time | int | No | 最大調理時間 |

#### レスポンス

**200 OK**
```json
{
  "status": "ok",
  "data": {
    "items": [...],
    "total": 10,
    "query": {
      "q": "カレー",
      "tag_ids": [1],
      "max_time": 30
    }
  }
}
```

## 3. スキーマ定義

### 3.1 Recipe

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "title": {"type": "string", "maxLength": 200},
    "description": {"type": "string", "maxLength": 2000},
    "servings": {"type": "integer", "minimum": 1, "maximum": 100},
    "prep_time_minutes": {"type": "integer", "minimum": 0, "maximum": 1440},
    "cook_time_minutes": {"type": "integer", "minimum": 0, "maximum": 1440},
    "image_path": {"type": "string"},
    "source_url": {"type": "string", "format": "uri"},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "ingredients": {"type": "array", "items": {"$ref": "#/Ingredient"}},
    "steps": {"type": "array", "items": {"$ref": "#/Step"}},
    "tags": {"type": "array", "items": {"$ref": "#/Tag"}}
  },
  "required": ["title", "ingredients", "steps"]
}
```

### 3.2 Ingredient

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string", "maxLength": 100},
    "name_normalized": {"type": "string"},
    "amount": {"type": "number"},
    "unit": {"type": "string", "maxLength": 20},
    "order_index": {"type": "integer"}
  },
  "required": ["name"]
}
```

### 3.3 Step

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "step_number": {"type": "integer"},
    "description": {"type": "string", "maxLength": 1000}
  },
  "required": ["description"]
}
```

## 4. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

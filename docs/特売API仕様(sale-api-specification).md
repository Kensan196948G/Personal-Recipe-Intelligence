# 特売情報API仕様書

## 概要
Personal Recipe Intelligence の特売情報連携機能のAPI仕様書です。

## エンドポイント一覧

### 1. 特売情報一覧取得
**GET** `/api/v1/sales`

スーパーの特売情報一覧を取得します。

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| store_name | string | 任意 | 店舗名でフィルタ |
| category | string | 任意 | カテゴリでフィルタ（vegetable, meat, fish, dairy, etc.） |
| min_discount | float | 任意 | 最小割引率（%） |

#### レスポンス例
```json
{
  "status": "ok",
  "data": [
    {
      "id": "uuid-001",
      "store_name": "イオン",
      "product_name": "たまねぎ",
      "price": 98.0,
      "original_price": 150.0,
      "unit": "個",
      "category": "vegetable",
      "valid_from": "2025-12-11T10:00:00",
      "valid_until": "2025-12-14T23:59:59",
      "discount_rate": 34.7,
      "image_url": null
    }
  ],
  "total": 1,
  "error": null
}
```

---

### 2. チラシアップロード
**POST** `/api/v1/sales/upload`

チラシ画像をアップロードして特売情報を抽出します。

#### リクエスト
- Content-Type: `multipart/form-data`
- Body: 画像ファイル（JPEG, PNG）

#### クエリパラメータ
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| store_name | string | 任意 | 自動検出 | 店舗名 |
| valid_days | int | 任意 | 3 | 有効日数（1-30） |

#### レスポンス例
```json
{
  "status": "ok",
  "data": {
    "store_name": "イオン",
    "items_count": 5,
    "valid_until": "2025-12-14T23:59:59",
    "items": [
      {
        "id": "uuid-002",
        "store_name": "イオン",
        "product_name": "にんじん",
        "price": 158.0,
        "unit": "本",
        "category": "vegetable",
        "valid_from": "2025-12-11T10:00:00",
        "valid_until": "2025-12-14T23:59:59"
      }
    ]
  },
  "error": null
}
```

---

### 3. レシピ推薦
**GET** `/api/v1/sales/recommendations`

特売食材を使ったレシピを推薦します。

#### クエリパラメータ
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| recipe_ids | list[string] | 任意 | - | 対象レシピIDリスト |
| max_results | int | 任意 | 10 | 最大結果数（1-50） |

#### レスポンス例
```json
{
  "status": "ok",
  "data": [
    {
      "recipe_id": "recipe-001",
      "recipe_name": "肉じゃが",
      "matching_ingredients": ["たまねぎ", "にんじん", "豚肉"],
      "estimated_cost": 396.0,
      "savings": null,
      "available_sale_items": [
        {
          "id": "uuid-003",
          "store_name": "イオン",
          "product_name": "たまねぎ",
          "price": 98.0,
          "category": "vegetable"
        }
      ]
    }
  ],
  "total_recommendations": 1,
  "error": null
}
```

---

### 4. 価格比較
**GET** `/api/v1/sales/price-compare`

同じ商品の価格を店舗間で比較します。

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| product_name | string | 必須 | 商品名（部分一致） |

#### レスポンス例
```json
{
  "status": "ok",
  "data": [
    {
      "store_name": "イオン",
      "product_name": "たまねぎ",
      "price": 98.0,
      "unit": "個",
      "discount_rate": 34.7,
      "valid_until": "2025-12-14T23:59:59"
    },
    {
      "store_name": "西友",
      "product_name": "たまねぎ",
      "price": 120.0,
      "unit": "個",
      "discount_rate": 20.0,
      "valid_until": "2025-12-13T23:59:59"
    }
  ],
  "product_name": "たまねぎ",
  "cheapest_store": "イオン",
  "price_range": {
    "min": 98.0,
    "max": 120.0,
    "avg": 109.0
  },
  "error": null
}
```

---

### 5. 材料費見積もり
**POST** `/api/v1/sales/cost-estimate`

レシピの材料費を見積もります。

#### リクエストボディ
```json
{
  "ingredients": ["たまねぎ", "にんじん", "豚肉", "じゃがいも"]
}
```

#### レスポンス例
```json
{
  "status": "ok",
  "data": {
    "total_cost": 454.0,
    "ingredients_count": 4,
    "available_on_sale": 3,
    "coverage_rate": 75.0,
    "items": [
      {
        "ingredient": "たまねぎ",
        "product": "たまねぎ",
        "price": 98.0,
        "store": "イオン",
        "on_sale": true
      },
      {
        "ingredient": "じゃがいも",
        "product": null,
        "price": null,
        "store": null,
        "on_sale": false
      }
    ]
  },
  "error": null
}
```

---

### 6. 統計情報
**GET** `/api/v1/sales/statistics`

特売情報の統計を取得します。

#### レスポンス例
```json
{
  "status": "ok",
  "data": {
    "total_active_sales": 25,
    "total_all_sales": 30,
    "average_discount_rate": 28.5,
    "categories": {
      "vegetable": 10,
      "meat": 8,
      "fish": 4,
      "dairy": 3
    },
    "stores": {
      "イオン": 15,
      "西友": 10
    }
  },
  "error": null
}
```

---

### 7. 期限切れ削除
**DELETE** `/api/v1/sales/expired`

期限切れの特売情報を削除します。

#### レスポンス例
```json
{
  "status": "ok",
  "data": {
    "deleted_count": 5
  },
  "error": null
}
```

---

## エラーレスポンス

全エンドポイント共通のエラーレスポンス形式：

```json
{
  "status": "error",
  "data": {},
  "error": "エラーメッセージ"
}
```

---

## カテゴリ一覧

| カテゴリ値 | 日本語名 |
|-----------|---------|
| vegetable | 野菜 |
| fruit | 果物 |
| meat | 肉類 |
| fish | 魚介類 |
| dairy | 乳製品 |
| grain | 穀物 |
| seasoning | 調味料 |
| other | その他 |

---

## 使用例

### curlでの使用例

#### 特売一覧取得
```bash
curl "http://localhost:8001/api/v1/sales?category=vegetable&min_discount=20"
```

#### チラシアップロード
```bash
curl -X POST "http://localhost:8001/api/v1/sales/upload?store_name=イオン&valid_days=3" \
  -F "file=@flyer.jpg"
```

#### レシピ推薦
```bash
curl "http://localhost:8001/api/v1/sales/recommendations?max_results=5"
```

#### 価格比較
```bash
curl "http://localhost:8001/api/v1/sales/price-compare?product_name=たまねぎ"
```

#### 材料費見積もり
```bash
curl -X POST "http://localhost:8001/api/v1/sales/cost-estimate" \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["たまねぎ", "にんじん", "豚肉"]}'
```

---

## セキュリティ

- 本API は個人用途を想定しているため、認証は実装していません
- 本番環境では適切な認証・認可機構の追加を推奨します

---

## 更新履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025-12-11 | 1.0.0 | 初版作成 |

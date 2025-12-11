# レビュー・評価機能 API ドキュメント

Personal Recipe Intelligence のレビュー・評価機能のAPI仕様書です。

## 概要

レシピに対するユーザーレビュー、星評価、コメント機能を提供します。

## 認証

すべての書き込み操作には認証が必要です。

```
Authorization: Bearer {user_id}
```

## エンドポイント

### 1. レビュー投稿

レシピにレビューを投稿します。

**Endpoint:** `POST /api/v1/review/recipe/{recipe_id}`

**Headers:**
- `Authorization: Bearer {user_id}` (必須)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "rating": 5,
  "comment": "とても美味しかったです！"
}
```

**Response:**
```json
{
  "status": "ok",
  "data": {
    "review": {
      "id": "uuid",
      "recipe_id": "recipe1",
      "user_id": "user1",
      "rating": 5,
      "comment": "とても美味しかったです！",
      "helpful_count": 0,
      "is_helpful": false,
      "created_at": "2025-12-11T10:00:00",
      "updated_at": null
    }
  },
  "error": null
}
```

**Validation:**
- rating: 1-5の整数
- comment: 1-2000文字

---

### 2. レビュー一覧取得

レシピのレビュー一覧と評価サマリーを取得します。

**Endpoint:** `GET /api/v1/review/recipe/{recipe_id}`

**Query Parameters:**
- `sort_by`: ソート方法 (recent/rating/helpful) - デフォルト: recent
- `limit`: 取得件数制限 - 任意

**Headers:**
- `Authorization: Bearer {user_id}` (任意)

**Response:**
```json
{
  "status": "ok",
  "data": {
    "reviews": [
      {
        "id": "uuid",
        "recipe_id": "recipe1",
        "user_id": "user1",
        "rating": 5,
        "comment": "とても美味しかったです！",
        "helpful_count": 10,
        "is_helpful": true,
        "created_at": "2025-12-11T10:00:00",
        "updated_at": null
      }
    ],
    "summary": {
      "recipe_id": "recipe1",
      "average_rating": 4.5,
      "total_reviews": 20,
      "rating_distribution": {
        "1": 0,
        "2": 1,
        "3": 3,
        "4": 6,
        "5": 10
      }
    }
  },
  "error": null
}
```

---

### 3. ユーザーのレビュー一覧

ユーザーが投稿したレビュー一覧を取得します。

**Endpoint:** `GET /api/v1/review/user/{user_id}`

**Headers:**
- `Authorization: Bearer {user_id}` (必須)

**Response:**
```json
{
  "status": "ok",
  "data": {
    "reviews": [...]
  },
  "error": null
}
```

**Note:** 自分のレビューのみ取得可能です。

---

### 4. レビュー編集

投稿済みのレビューを編集します。

**Endpoint:** `PUT /api/v1/review/{review_id}`

**Headers:**
- `Authorization: Bearer {user_id}` (必須)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "rating": 4,
  "comment": "Good but not great"
}
```

**Note:** rating, comment は任意。指定した項目のみ更新されます。

---

### 5. レビュー削除

投稿済みのレビューを削除します。

**Endpoint:** `DELETE /api/v1/review/{review_id}`

**Headers:**
- `Authorization: Bearer {user_id}` (必須)

**Response:**
```json
{
  "status": "ok",
  "data": {
    "message": "Review deleted successfully"
  },
  "error": null
}
```

---

### 6. 役に立ったマーク

レビューを「役に立った」としてマーク/解除します。

**Endpoint:** `POST /api/v1/review/{review_id}/helpful`

**Headers:**
- `Authorization: Bearer {user_id}` (必須)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "helpful": true
}
```

**Parameters:**
- `helpful`: true でマーク、false で解除

**Response:**
```json
{
  "status": "ok",
  "data": {
    "review": {
      "id": "uuid",
      "helpful_count": 11,
      "is_helpful": true,
      ...
    }
  },
  "error": null
}
```

---

### 7. 評価サマリー取得

レシピの評価サマリーのみを取得します。

**Endpoint:** `GET /api/v1/review/recipe/{recipe_id}/summary`

**Response:**
```json
{
  "status": "ok",
  "data": {
    "summary": {
      "recipe_id": "recipe1",
      "average_rating": 4.5,
      "total_reviews": 20,
      "rating_distribution": {
        "1": 0,
        "2": 1,
        "3": 3,
        "4": 6,
        "5": 10
      }
    }
  },
  "error": null
}
```

---

### 8. 人気レビュー取得

役に立った数が多いレビューを取得します。

**Endpoint:** `GET /api/v1/review/recipe/{recipe_id}/popular`

**Query Parameters:**
- `limit`: 取得件数 (デフォルト: 3)

**Response:**
```json
{
  "status": "ok",
  "data": {
    "reviews": [...]
  },
  "error": null
}
```

---

## エラーレスポンス

```json
{
  "status": "error",
  "data": null,
  "error": "エラーメッセージ"
}
```

**Status Codes:**
- 200: 成功
- 400: リクエストエラー
- 401: 認証エラー
- 403: 権限エラー
- 422: バリデーションエラー
- 500: サーバーエラー

---

## セキュリティ

### XSS対策
- コメントは自動的にHTMLエスケープされます
- スクリプトタグなどは無害化されます

### 権限制御
- レビューの編集・削除は投稿者のみ可能
- ユーザーのレビュー一覧は本人のみ取得可能

---

## 使用例

### JavaScript (fetch)

```javascript
// レビュー投稿
const response = await fetch('/api/v1/review/recipe/recipe1', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer user123'
  },
  body: JSON.stringify({
    rating: 5,
    comment: 'とても美味しかったです！'
  })
});

const data = await response.json();
console.log(data.data.review);

// レビュー一覧取得
const listResponse = await fetch('/api/v1/review/recipe/recipe1?sort_by=rating');
const listData = await listResponse.json();
console.log(listData.data.reviews);
console.log(listData.data.summary);
```

### Python (requests)

```python
import requests

# レビュー投稿
response = requests.post(
    'http://localhost:8000/api/v1/review/recipe/recipe1',
    json={'rating': 5, 'comment': 'とても美味しかったです！'},
    headers={'Authorization': 'Bearer user123'}
)

review = response.json()['data']['review']
print(f"Review ID: {review['id']}")

# レビュー一覧取得
response = requests.get(
    'http://localhost:8000/api/v1/review/recipe/recipe1',
    params={'sort_by': 'rating'}
)

data = response.json()['data']
print(f"Average Rating: {data['summary']['average_rating']}")
print(f"Total Reviews: {data['summary']['total_reviews']}")
```

---

## データ永続化

レビューデータは `data/reviews/reviews.json` にJSON形式で保存されます。

## テスト

```bash
# サービスのテスト
pytest backend/tests/test_review_service.py -v

# APIのテスト
pytest backend/tests/test_review_api.py -v

# カバレッジ付き
pytest backend/tests/test_review_*.py --cov=backend.services.review_service --cov=backend.api.routers.review
```

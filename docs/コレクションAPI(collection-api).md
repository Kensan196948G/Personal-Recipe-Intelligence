# Collection API Documentation

## 概要

レシピコレクション機能のAPIドキュメント。
ユーザーがレシピをグループ化し、管理・共有できる機能を提供します。

## エンドポイント一覧

### 1. コレクション作成

**POST** `/api/v1/collection`

新しいコレクションを作成します。

#### リクエスト

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "name": "お気に入りの和食",
  "description": "家族が喜ぶ和食レシピ集",
  "visibility": "private",
  "tags": ["和食", "家庭料理"]
}
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": {
    "id": "uuid",
    "name": "お気に入りの和食",
    "description": "家族が喜ぶ和食レシピ集",
    "owner_id": "user-id",
    "visibility": "private",
    "created_at": "2025-12-11T10:00:00",
    "updated_at": "2025-12-11T10:00:00",
    "is_default": false,
    "recipes": [],
    "tags": ["和食", "家庭料理"],
    "thumbnail_url": null,
    "recipe_count": 0
  },
  "error": null
}
```

---

### 2. 自分のコレクション一覧取得

**GET** `/api/v1/collection`

認証ユーザーのすべてのコレクションを取得します。

#### リクエスト

**Headers:**
```
Authorization: Bearer <token>
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": [
    {
      "id": "uuid",
      "name": "お気に入り",
      "description": "お気に入りのレシピ",
      "owner_id": "user-id",
      "visibility": "private",
      "created_at": "2025-12-11T10:00:00",
      "updated_at": "2025-12-11T10:00:00",
      "is_default": true,
      "recipes": [...],
      "tags": [],
      "thumbnail_url": null,
      "recipe_count": 5
    }
  ],
  "error": null
}
```

---

### 3. コレクション詳細取得

**GET** `/api/v1/collection/{collection_id}`

特定のコレクションの詳細を取得します。

- オーナーはすべてのコレクションにアクセス可能
- 他のユーザーは公開コレクションのみアクセス可能

#### リクエスト

**Headers:**
```
Authorization: Bearer <token> (Optional)
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": {
    "id": "uuid",
    "name": "お気に入りの和食",
    "description": "家族が喜ぶ和食レシピ集",
    "owner_id": "user-id",
    "visibility": "public",
    "created_at": "2025-12-11T10:00:00",
    "updated_at": "2025-12-11T10:30:00",
    "is_default": false,
    "recipes": [
      {
        "recipe_id": "recipe-uuid",
        "added_at": "2025-12-11T10:15:00",
        "note": "週末に作る",
        "position": 0
      }
    ],
    "tags": ["和食", "家庭料理"],
    "thumbnail_url": "https://example.com/thumb.jpg",
    "recipe_count": 1
  },
  "error": null
}
```

**Error (404):**
```json
{
  "detail": "Collection not found"
}
```

---

### 4. コレクション更新

**PUT** `/api/v1/collection/{collection_id}`

コレクション情報を更新します（オーナーのみ可能）。

#### リクエスト

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "name": "お気に入りの和食（更新版）",
  "description": "新しい説明",
  "visibility": "public",
  "tags": ["和食", "簡単"]
}
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": {
    "id": "uuid",
    "name": "お気に入りの和食（更新版）",
    ...
  },
  "error": null
}
```

---

### 5. コレクション削除

**DELETE** `/api/v1/collection/{collection_id}`

コレクションを削除します（オーナーのみ可能）。

#### リクエスト

**Headers:**
```
Authorization: Bearer <token>
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": {
    "message": "Collection deleted successfully"
  },
  "error": null
}
```

---

### 6. レシピ追加

**POST** `/api/v1/collection/{collection_id}/recipes/{recipe_id}`

コレクションにレシピを追加します。

#### リクエスト

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "note": "次回は倍量で作る"
}
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": {
    "id": "uuid",
    "name": "お気に入りの和食",
    "recipes": [
      {
        "recipe_id": "recipe-uuid",
        "added_at": "2025-12-11T10:30:00",
        "note": "次回は倍量で作る",
        "position": 0
      }
    ],
    "recipe_count": 1,
    ...
  },
  "error": null
}
```

**Error (400):**
```json
{
  "detail": "Recipe already in collection"
}
```

```json
{
  "detail": "Collection limit (100) reached"
}
```

---

### 7. レシピ削除

**DELETE** `/api/v1/collection/{collection_id}/recipes/{recipe_id}`

コレクションからレシピを削除します。

#### リクエスト

**Headers:**
```
Authorization: Bearer <token>
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": {
    "id": "uuid",
    "name": "お気に入りの和食",
    "recipes": [],
    "recipe_count": 0,
    ...
  },
  "error": null
}
```

---

### 8. 公開コレクション一覧取得

**GET** `/api/v1/collection/public`

公開設定されているコレクションを取得します。

#### クエリパラメータ

- `limit` (int, optional): 取得件数（デフォルト: 50、最大: 100）
- `offset` (int, optional): オフセット（デフォルト: 0）

#### リクエスト

```
GET /api/v1/collection/public?limit=20&offset=0
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": [
    {
      "id": "uuid",
      "name": "人気の洋食",
      "description": "みんなが作っている洋食レシピ",
      "owner_id": "user-id",
      "visibility": "public",
      "recipe_count": 15,
      ...
    }
  ],
  "error": null
}
```

---

### 9. コレクションコピー

**POST** `/api/v1/collection/{collection_id}/copy`

公開コレクションまたは自分のコレクションをコピーします。

#### リクエスト

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "new_name": "コピーしたコレクション"
}
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": {
    "id": "new-uuid",
    "name": "コピーしたコレクション",
    "description": "元の説明",
    "owner_id": "current-user-id",
    "visibility": "private",
    "recipes": [...],
    ...
  },
  "error": null
}
```

---

### 10. 統計情報取得

**GET** `/api/v1/collection/stats/summary`

コレクション全体の統計情報を取得します。

#### リクエスト

```
GET /api/v1/collection/stats/summary
```

#### レスポンス

**Success (200):**
```json
{
  "status": "ok",
  "data": {
    "total_collections": 150,
    "public_collections": 45,
    "private_collections": 105,
    "total_recipes": 2300,
    "most_popular_collection_id": "uuid"
  },
  "error": null
}
```

---

## データモデル

### Collection

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | string | コレクションID（UUID） |
| name | string | コレクション名（1-100文字） |
| description | string | 説明（最大500文字、省略可） |
| owner_id | string | オーナーのユーザーID |
| visibility | string | 公開設定（"public" or "private"） |
| created_at | string | 作成日時（ISO8601） |
| updated_at | string | 更新日時（ISO8601） |
| is_default | boolean | デフォルトコレクションか |
| recipes | array | レシピリスト |
| tags | array | タグリスト |
| thumbnail_url | string | サムネイルURL（省略可） |
| recipe_count | integer | レシピ数 |

### CollectionItem

| フィールド | 型 | 説明 |
|-----------|-----|------|
| recipe_id | string | レシピID |
| added_at | string | 追加日時（ISO8601） |
| note | string | メモ（最大200文字、省略可） |
| position | integer | 表示順序 |

---

## 制限事項

- 1コレクションあたりの最大レシピ数: **100**
- コレクション名の最大文字数: **100**
- 説明の最大文字数: **500**
- メモの最大文字数: **200**

---

## デフォルトコレクション

新規ユーザー登録時に自動的に以下のコレクションが作成されます：

1. **お気に入り** - お気に入りのレシピ
2. **作りたい** - 今度作ってみたいレシピ
3. **作った** - 実際に作ったレシピ

これらは `is_default: true` で識別でき、削除できません。

---

## エラーコード

| コード | 説明 |
|-------|------|
| 400 | リクエストが不正（バリデーションエラー） |
| 401 | 認証エラー（トークン未提供または無効） |
| 404 | リソースが見つからない |
| 500 | サーバー内部エラー |

---

## 使用例

### Python

```python
import requests

API_URL = "http://localhost:8000"
TOKEN = "your-auth-token"

# コレクション作成
response = requests.post(
    f"{API_URL}/api/v1/collection",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={
        "name": "週末レシピ",
        "description": "週末に作りたいレシピ",
        "visibility": "private",
        "tags": ["週末", "特別"]
    }
)
collection = response.json()["data"]

# レシピ追加
recipe_id = "recipe-uuid-here"
response = requests.post(
    f"{API_URL}/api/v1/collection/{collection['id']}/recipes/{recipe_id}",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"note": "次回は野菜多めで"}
)
```

### JavaScript (Fetch)

```javascript
const API_URL = 'http://localhost:8000';
const TOKEN = 'your-auth-token';

// コレクション作成
const response = await fetch(`${API_URL}/api/v1/collection`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: '週末レシピ',
    description: '週末に作りたいレシピ',
    visibility: 'private',
    tags: ['週末', '特別']
  })
});

const collection = await response.json();

// レシピ追加
const recipeId = 'recipe-uuid-here';
await fetch(
  `${API_URL}/api/v1/collection/${collection.data.id}/recipes/${recipeId}`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      note: '次回は野菜多めで'
    })
  }
);
```

---

## セキュリティ

- すべてのコレクション操作には認証が必要です（公開コレクション閲覧を除く）
- コレクションの編集・削除はオーナーのみ可能です
- 非公開コレクションは他のユーザーから見えません
- APIトークンは環境変数で管理し、ログに出力しないでください

---

## パフォーマンス

- コレクション取得は通常 50ms 以内で完了します
- 大量のレシピを含むコレクションの場合、若干遅くなる可能性があります
- 公開コレクション一覧はレシピ数でソートされます（人気順）

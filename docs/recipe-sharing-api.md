# Recipe Sharing API Documentation

## 概要
Personal Recipe Intelligence のレシピ共有機能API仕様書

## ベースURL
```
/api/v1/sharing
```

---

## エンドポイント一覧

### 1. 共有リンク作成

**POST** `/create-link`

レシピの共有リンクを作成します。

#### リクエスト
```json
{
  "recipe_id": "recipe_001",
  "owner_id": "user_001",
  "permission": "view_only",
  "expires_in_days": 7,
  "shared_with": ["user@example.com", "user_002"]
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| recipe_id | string | ✓ | レシピID |
| owner_id | string | ✓ | オーナーユーザーID |
| permission | string | | 共有権限（`view_only` / `edit`）デフォルト: `view_only` |
| expires_in_days | integer | | 有効期限（日数）0=無期限、デフォルト: 7 |
| shared_with | array[string] | | 共有相手リスト（メールアドレスまたはユーザーID） |

#### レスポンス（201 Created）
```json
{
  "share_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipe_id": "recipe_001",
  "owner_id": "user_001",
  "permission": "view_only",
  "created_at": "2025-12-11T10:00:00",
  "expires_at": "2025-12-18T10:00:00",
  "shared_with": ["user@example.com", "user_002"],
  "share_link": "/shared/550e8400-e29b-41d4-a716-446655440000",
  "is_active": true,
  "access_count": 0,
  "last_accessed": null
}
```

---

### 2. 共有リンクでレシピ取得

**GET** `/link/{share_id}`

共有IDを使用してレシピ情報を取得します。

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|---|------|
| share_id | string | 共有ID（UUID） |

#### レスポンス（200 OK）
```json
{
  "share_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipe_id": "recipe_001",
  "owner_id": "user_001",
  "permission": "view_only",
  "created_at": "2025-12-11T10:00:00",
  "expires_at": "2025-12-18T10:00:00",
  "shared_with": [],
  "share_link": "/shared/550e8400-e29b-41d4-a716-446655440000",
  "is_active": true,
  "access_count": 5,
  "last_accessed": "2025-12-12T15:30:00"
}
```

#### エラーレスポンス（404 Not Found）
```json
{
  "detail": "Share not found or expired"
}
```

---

### 3. レシピの共有情報リスト取得

**GET** `/recipe/{recipe_id}`

指定したレシピの共有情報リストを取得します。

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|---|------|
| recipe_id | string | レシピID |

#### レスポンス（200 OK）
```json
{
  "shares": [
    {
      "share_id": "550e8400-e29b-41d4-a716-446655440000",
      "recipe_id": "recipe_001",
      "owner_id": "user_001",
      "permission": "view_only",
      "created_at": "2025-12-11T10:00:00",
      "expires_at": "2025-12-18T10:00:00",
      "shared_with": [],
      "share_link": "/shared/550e8400-e29b-41d4-a716-446655440000",
      "is_active": true,
      "access_count": 5,
      "last_accessed": "2025-12-12T15:30:00"
    }
  ],
  "total": 1
}
```

---

### 4. 自分が共有したレシピ一覧

**GET** `/my-shares`

自分が作成した共有リンクの一覧を取得します。

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| owner_id | string | ✓ | オーナーユーザーID |

#### レスポンス（200 OK）
```json
{
  "shares": [
    {
      "share_id": "550e8400-e29b-41d4-a716-446655440000",
      "recipe_id": "recipe_001",
      "owner_id": "user_001",
      "permission": "view_only",
      "created_at": "2025-12-11T10:00:00",
      "expires_at": "2025-12-18T10:00:00",
      "shared_with": ["user@example.com"],
      "share_link": "/shared/550e8400-e29b-41d4-a716-446655440000",
      "is_active": true,
      "access_count": 10,
      "last_accessed": "2025-12-12T15:30:00"
    }
  ],
  "total": 1
}
```

---

### 5. 自分に共有されたレシピ一覧

**GET** `/shared-with-me`

自分に共有されたレシピの一覧を取得します。

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| user_id | string | ✓ | ユーザーID（メールアドレスまたはユーザーID） |

#### レスポンス（200 OK）
```json
{
  "shares": [
    {
      "share_id": "550e8400-e29b-41d4-a716-446655440000",
      "recipe_id": "recipe_002",
      "owner_id": "user_002",
      "permission": "view_only",
      "created_at": "2025-12-10T10:00:00",
      "expires_at": "2025-12-17T10:00:00",
      "shared_with": ["user_001", "user@example.com"],
      "share_link": "/shared/550e8400-e29b-41d4-a716-446655440000",
      "is_active": true,
      "access_count": 3,
      "last_accessed": "2025-12-11T12:00:00"
    }
  ],
  "total": 1
}
```

---

### 6. 共有情報更新

**PUT** `/{share_id}`

共有情報を更新します。

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|---|------|
| share_id | string | 共有ID（UUID） |

#### リクエスト
```json
{
  "permission": "edit",
  "expires_in_days": 30,
  "shared_with": ["user@example.com", "new@example.com"]
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| permission | string | | 共有権限（`view_only` / `edit`） |
| expires_in_days | integer | | 有効期限（日数）0=無期限 |
| shared_with | array[string] | | 共有相手リスト |

#### レスポンス（200 OK）
```json
{
  "share_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipe_id": "recipe_001",
  "owner_id": "user_001",
  "permission": "edit",
  "created_at": "2025-12-11T10:00:00",
  "expires_at": "2026-01-10T10:00:00",
  "shared_with": ["user@example.com", "new@example.com"],
  "share_link": "/shared/550e8400-e29b-41d4-a716-446655440000",
  "is_active": true,
  "access_count": 5,
  "last_accessed": "2025-12-12T15:30:00"
}
```

---

### 7. 共有解除

**DELETE** `/{share_id}`

共有を解除します（無効化）。

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|---|------|
| share_id | string | 共有ID（UUID） |

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| user_id | string | ✓ | 実行ユーザーID（オーナーのみ実行可能） |

#### レスポンス（204 No Content）
レスポンスボディなし

#### エラーレスポンス（404 Not Found）
```json
{
  "detail": "Share not found or unauthorized"
}
```

---

### 8. 招待送信

**POST** `/invite`

共有相手に招待を送信します（簡易版、実際のメール送信は含まない）。

#### リクエスト
```json
{
  "share_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipients": ["user@example.com", "another@example.com"],
  "message": "レシピを共有します"
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| share_id | string | ✓ | 共有ID |
| recipients | array[string] | ✓ | 招待先リスト |
| message | string | | メッセージ（現在未使用） |

#### レスポンス（200 OK）
```json
{
  "status": "ok",
  "message": "Invited 2 recipients",
  "share_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipients": ["user@example.com", "another@example.com"]
}
```

---

### 9. 共有統計取得

**GET** `/stats/{owner_id}`

ユーザーの共有統計情報を取得します。

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|---|------|
| owner_id | string | オーナーユーザーID |

#### レスポンス（200 OK）
```json
{
  "total_shares": 10,
  "active_shares": 8,
  "total_accesses": 150,
  "view_only_shares": 6,
  "edit_shares": 2
}
```

---

### 10. 共有履歴取得

**GET** `/history/{share_id}`

共有の履歴（作成、更新、解除など）を取得します。

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|---|------|
| share_id | string | 共有ID（UUID） |

#### レスポンス（200 OK）
```json
{
  "history": [
    {
      "share_id": "550e8400-e29b-41d4-a716-446655440000",
      "action": "created",
      "user_id": "user_001",
      "timestamp": "2025-12-11T10:00:00",
      "details": {
        "recipe_id": "recipe_001",
        "permission": "view_only",
        "expires_at": "2025-12-18T10:00:00"
      }
    },
    {
      "share_id": "550e8400-e29b-41d4-a716-446655440000",
      "action": "updated",
      "user_id": "user_001",
      "timestamp": "2025-12-12T14:00:00",
      "details": {
        "permission": "edit",
        "expires_at": "2026-01-11T14:00:00"
      }
    }
  ],
  "total": 2
}
```

---

### 11. 期限切れ共有クリーンアップ

**POST** `/cleanup`

期限切れの共有を無効化します。

#### レスポンス（200 OK）
```json
{
  "status": "ok",
  "message": "Cleaned up 5 expired shares",
  "count": 5
}
```

---

## データモデル

### RecipeShare

| フィールド | 型 | 説明 |
|-----------|---|------|
| share_id | string | 共有ID（UUID） |
| recipe_id | string | レシピID |
| owner_id | string | オーナーユーザーID |
| permission | string | 共有権限（`view_only` / `edit`） |
| created_at | string | 作成日時（ISO8601） |
| expires_at | string | 有効期限（ISO8601、null=無期限） |
| shared_with | array[string] | 共有相手リスト |
| share_link | string | 共有リンクパス |
| is_active | boolean | アクティブ状態 |
| access_count | integer | アクセス回数 |
| last_accessed | string | 最終アクセス日時（ISO8601、null=未アクセス） |

---

## エラーレスポンス

すべてのエラーは以下の形式で返されます：

```json
{
  "detail": "エラーメッセージ"
}
```

### ステータスコード

| コード | 説明 |
|-------|------|
| 200 | 成功 |
| 201 | 作成成功 |
| 204 | 削除成功（レスポンスボディなし） |
| 404 | リソースが見つからない |
| 500 | サーバーエラー |

---

## 使用例

### 1. 共有リンクを作成してコピー

```bash
# 共有リンク作成
curl -X POST http://localhost:8000/api/v1/sharing/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": "recipe_001",
    "owner_id": "user_001",
    "permission": "view_only",
    "expires_in_days": 7
  }'

# レスポンス例
# {
#   "share_id": "550e8400-e29b-41d4-a716-446655440000",
#   "share_link": "/shared/550e8400-e29b-41d4-a716-446655440000",
#   ...
# }
```

### 2. 共有リンクでレシピにアクセス

```bash
curl http://localhost:8000/api/v1/sharing/link/550e8400-e29b-41d4-a716-446655440000
```

### 3. 自分の共有リスト確認

```bash
curl http://localhost:8000/api/v1/sharing/my-shares?owner_id=user_001
```

### 4. 共有解除

```bash
curl -X DELETE http://localhost:8000/api/v1/sharing/550e8400-e29b-41d4-a716-446655440000?user_id=user_001
```

---

## セキュリティ考慮事項

1. **アクセス制限**
   - 共有IDはUUIDを使用（推測困難）
   - 有効期限設定により自動的に無効化
   - 共有相手リストによる追加制限

2. **権限管理**
   - オーナーのみ共有の更新・解除が可能
   - 閲覧のみ / 編集可能の権限分離

3. **監査ログ**
   - すべての共有操作は履歴に記録
   - アクセス回数と最終アクセス日時を追跡

---

## 今後の拡張予定

- メール招待機能の実装
- SNS連携強化
- 共有レシピのプレビュー機能
- 共有先の閲覧履歴詳細
- 共有リンクのカスタムURL

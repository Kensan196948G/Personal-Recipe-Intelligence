# フォロー機能 仕様書

## 概要

Personal Recipe Intelligence (PRI) のフォロー機能は、ユーザー間の関係を管理し、フォロー中ユーザーのレシピフィードを提供する機能です。

## 機能一覧

### 1. フォロー管理
- ユーザーをフォロー
- ユーザーをアンフォロー
- フォロー状態の確認
- 相互フォロー判定

### 2. フォロー関係取得
- フォロワー一覧取得
- フォロー中ユーザー一覧取得
- フォロワー数/フォロー中数の取得

### 3. フィード機能
- フォロー中ユーザーの新着レシピ表示（最新20件）
- ユーザー情報付きレシピリスト

### 4. おすすめユーザー
- 友達の友達（共通フォロー）に基づく提案
- レシピ数に基づく提案
- 共通の友達数の表示

## データモデル

### Follow (フォロー関係)

```json
{
  "id": "user_1_user_2_1733897600.0",
  "follower_id": "user_1",
  "following_id": "user_2",
  "created_at": "2025-12-11T10:00:00"
}
```

| フィールド | 型 | 説明 |
|-----------|---|------|
| id | string | フォロー関係の一意識別子 |
| follower_id | string | フォローするユーザーID |
| following_id | string | フォローされるユーザーID |
| created_at | string | フォロー開始日時（ISO8601） |

### User (ユーザー)

```json
{
  "id": "user_1",
  "username": "alice",
  "display_name": "Alice",
  "bio": "料理好きです。",
  "avatar_url": null,
  "created_at": "2025-12-01T10:00:00"
}
```

## API エンドポイント

### POST /api/v1/follow/{user_id}
ユーザーをフォロー

**リクエスト**
```bash
POST /api/v1/follow/user_2
```

**レスポンス**
```json
{
  "status": "ok",
  "data": {
    "id": "user_1_user_2_1733897600.0",
    "follower_id": "user_1",
    "following_id": "user_2",
    "created_at": "2025-12-11T10:00:00"
  },
  "error": null
}
```

### DELETE /api/v1/follow/{user_id}
ユーザーをアンフォロー

**リクエスト**
```bash
DELETE /api/v1/follow/user_2
```

**レスポンス**
```json
{
  "status": "ok",
  "data": {
    "message": "アンフォローしました",
    "user_id": "user_2"
  },
  "error": null
}
```

### GET /api/v1/follow/followers
フォロワー一覧を取得

**パラメータ**
- `user_id` (optional): 対象ユーザーID（省略時は現在のユーザー）
- `limit` (optional): 取得件数（デフォルト: 100、最大: 500）
- `offset` (optional): オフセット（デフォルト: 0）

**リクエスト**
```bash
GET /api/v1/follow/followers?limit=20&offset=0
```

**レスポンス**
```json
{
  "status": "ok",
  "data": {
    "followers": [
      {
        "id": "user_2",
        "username": "bob",
        "display_name": "Bob",
        "bio": "パン職人です。",
        "is_mutual": true,
        "is_following": true
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

### GET /api/v1/follow/following
フォロー中ユーザー一覧を取得

**パラメータ**
- `user_id` (optional): 対象ユーザーID（省略時は現在のユーザー）
- `limit` (optional): 取得件数（デフォルト: 100、最大: 500）
- `offset` (optional): オフセット（デフォルト: 0）

**レスポンス**
```json
{
  "status": "ok",
  "data": {
    "following": [
      {
        "id": "user_2",
        "username": "bob",
        "display_name": "Bob",
        "bio": "パン職人です。",
        "is_mutual": true,
        "is_follower": true
      }
    ],
    "total": 1,
    "limit": 100,
    "offset": 0
  },
  "error": null
}
```

### GET /api/v1/follow/feed
フォロー中ユーザーの新着レシピを取得

**パラメータ**
- `limit` (optional): 取得件数（デフォルト: 20、最大: 100）

**リクエスト**
```bash
GET /api/v1/follow/feed?limit=20
```

**レスポンス**
```json
{
  "status": "ok",
  "data": [
    {
      "id": "recipe_3",
      "user_id": "user_3",
      "title": "チョコレートケーキ",
      "description": "濃厚なチョコレートケーキです。",
      "tags": ["ケーキ", "デザート"],
      "created_at": "2025-12-10T14:00:00",
      "user": {
        "id": "user_3",
        "username": "charlie",
        "display_name": "Charlie",
        "avatar_url": null
      }
    }
  ],
  "error": null
}
```

### GET /api/v1/follow/suggestions
おすすめユーザーを取得

**パラメータ**
- `limit` (optional): 取得件数（デフォルト: 10、最大: 50）

**リクエスト**
```bash
GET /api/v1/follow/suggestions?limit=10
```

**レスポンス**
```json
{
  "status": "ok",
  "data": [
    {
      "id": "user_3",
      "username": "charlie",
      "display_name": "Charlie",
      "bio": "デザート専門。",
      "recipe_count": 5,
      "common_friends": 2
    }
  ],
  "error": null
}
```

### GET /api/v1/follow/status/{user_id}
フォロー状態を確認

**リクエスト**
```bash
GET /api/v1/follow/status/user_2
```

**レスポンス**
```json
{
  "status": "ok",
  "data": {
    "is_following": true,
    "is_follower": true,
    "is_mutual": true,
    "follower_count": 10,
    "following_count": 15
  },
  "error": null
}
```

## フロントエンドコンポーネント

### FollowButton
フォロー/アンフォローボタンコンポーネント

**Props**
- `userId` (string): 対象ユーザーID
- `initialStatus` (object, optional): 初期フォロー状態
- `onStatusChange` (function, optional): フォロー状態変更時のコールバック

**使用例**
```jsx
<FollowButton
  userId="user_2"
  onStatusChange={(isFollowing) => console.log('Following:', isFollowing)}
/>
```

### UserList
ユーザーリストコンポーネント

**Props**
- `type` (string): リストタイプ（'followers', 'following', 'suggestions'）
- `userId` (string, optional): 対象ユーザーID
- `limit` (number, optional): 取得件数

**使用例**
```jsx
<UserList type="followers" userId="user_1" limit={20} />
<UserList type="following" />
<UserList type="suggestions" limit={10} />
```

### FollowPage
フォロー管理ページ

**タブ**
- フィード: フォロー中ユーザーの新着レシピ
- フォロワー: フォロワー一覧
- フォロー中: フォロー中ユーザー一覧
- おすすめ: おすすめユーザー一覧

## アルゴリズム

### おすすめユーザー提案

1. **友達の友達（第1優先）**
   - フォロー中ユーザーがフォローしているユーザーを抽出
   - 既にフォロー中または自分自身を除外
   - 共通の友達数でソート

2. **レシピ数（第2優先）**
   - 友達の友達が不足している場合
   - レシピ数が多いユーザーをソート
   - 上位から推薦

### フィード生成

1. フォロー中ユーザーIDリストを取得
2. それらのユーザーが投稿したレシピを抽出
3. 作成日時（created_at）で降順ソート
4. 最新20件を取得
5. ユーザー情報を付加

## データ永続化

### ファイル構成
```
data/
  follows.json     ← フォロー関係データ
  users.json       ← ユーザーデータ
  recipes.json     ← レシピデータ
```

### バックアップ
- 定期的に `data/backups/` にバックアップ
- タイムスタンプ付きファイル名で保存

## テスト

### テストファイル
`backend/tests/test_follow_service.py`

### テストカバレッジ
- フォロー/アンフォロー機能
- フォロワー/フォロー中取得
- フォロー状態確認
- 相互フォロー判定
- フィード取得
- おすすめユーザー提案
- エッジケース（自分自身、存在しないユーザー）

### 実行方法
```bash
pytest backend/tests/test_follow_service.py -v
```

## セキュリティ

### 認証
- 現在は仮実装（`get_current_user_id()`）
- JWT トークン認証への移行予定

### 入力検証
- ユーザーIDの存在確認
- 自分自身へのフォロー防止
- パラメータの範囲チェック

### プライバシー
- フォロワー/フォロー中情報は公開
- 将来的にプライベートアカウント機能を検討

## パフォーマンス最適化

### キャッシュ
- フォロワー数/フォロー中数のキャッシュ（将来実装）
- フィードのキャッシュ（将来実装）

### ページネーション
- フォロワー/フォロー中一覧はページネーション対応
- デフォルト: 100件、最大: 500件

### インデックス
- SQLite 移行時にインデックス作成
  - `follows(follower_id)`
  - `follows(following_id)`
  - `recipes(user_id, created_at)`

## 今後の拡張

### Phase 1
- [x] 基本的なフォロー/アンフォロー機能
- [x] フォロワー/フォロー中一覧
- [x] フィード機能
- [x] おすすめユーザー

### Phase 2（将来）
- [ ] プライベートアカウント
- [ ] ブロック機能
- [ ] 通知機能（新規フォロワー、フォローバック）
- [ ] フォローリクエスト承認/拒否

### Phase 3（将来）
- [ ] アクティビティフィード（いいね、コメント含む）
- [ ] リスト機能（カテゴリ別フォロー管理）
- [ ] ミュート機能
- [ ] フォロー推薦アルゴリズム改善（ML活用）

## トラブルシューティング

### フォローできない
- ユーザーが存在するか確認
- 自分自身をフォローしていないか確認
- ネットワーク接続を確認

### フィードが表示されない
- フォロー中ユーザーがいるか確認
- フォロー中ユーザーがレシピを投稿しているか確認

### おすすめユーザーが表示されない
- 他のユーザーが存在するか確認
- フォロー可能なユーザーが残っているか確認

## 参考リンク

- [API仕様書](./API_SPEC.md)
- [データベース設計](./DATABASE_DESIGN.md)
- [CLAUDE.md](../CLAUDE.md)

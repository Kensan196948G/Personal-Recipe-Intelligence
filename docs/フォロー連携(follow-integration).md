# フォロー機能 統合ガイド

## 概要

このドキュメントは、Personal Recipe Intelligence (PRI) のフォロー機能を既存のアプリケーションに統合する手順を説明します。

## 前提条件

- Python 3.11以上
- Node.js 20以上
- FastAPI実行環境
- React/Next.js フロントエンド環境

## バックエンド統合

### 1. ディレクトリ構成確認

以下のファイルが配置されていることを確認してください：

```
backend/
  services/
    follow_service.py          ← フォローサービス
  api/
    routers/
      follow.py                ← フォローAPI
  tests/
    test_follow_service.py     ← テストコード
```

### 2. FastAPI アプリケーションにルーターを追加

`backend/main.py` または `backend/app.py` に以下を追加：

```python
from fastapi import FastAPI
from backend.api.routers import follow

app = FastAPI(title="Personal Recipe Intelligence")

# フォローAPIルーターを登録
app.include_router(follow.router)
```

### 3. データファイルの配置

以下のJSONファイルを `data/` ディレクトリに配置：

```
data/
  follows.json       ← 空配列 [] で初期化
  users.json         ← ユーザーデータ
  recipes.json       ← レシピデータ
```

初期化コマンド：
```bash
mkdir -p data
echo '[]' > data/follows.json
```

### 4. 依存関係の確認

必要なPythonパッケージがインストールされていることを確認：

```bash
pip install fastapi pydantic
```

### 5. テスト実行

フォロー機能が正しく動作することをテスト：

```bash
pytest backend/tests/test_follow_service.py -v
```

### 6. サーバー起動

FastAPIサーバーを起動：

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 7. API動作確認

以下のエンドポイントが利用可能か確認：

```bash
# フォロー
curl -X POST http://localhost:8001/api/v1/follow/user_2

# フォロワー一覧
curl http://localhost:8001/api/v1/follow/followers

# フォロー中一覧
curl http://localhost:8001/api/v1/follow/following

# フィード取得
curl http://localhost:8001/api/v1/follow/feed

# おすすめユーザー
curl http://localhost:8001/api/v1/follow/suggestions

# フォロー状態確認
curl http://localhost:8001/api/v1/follow/status/user_2
```

## フロントエンド統合

### 1. コンポーネントファイル配置

以下のファイルを `frontend/components/` に配置：

```
frontend/
  components/
    FollowButton.jsx    ← フォローボタン
    UserList.jsx        ← ユーザーリスト
  pages/
    FollowPage.jsx      ← フォローページ
```

### 2. ルーティング設定

Next.js の場合：

```javascript
// pages/follow.js または app/follow/page.js
import FollowPage from '../components/FollowPage';

export default function Follow() {
  return <FollowPage />;
}
```

React Router の場合：

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import FollowPage from './pages/FollowPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/follow" element={<FollowPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### 3. API エンドポイント設定

環境変数で API ベースURLを設定：

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
```

または、コンポーネント内で直接設定：

```javascript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
```

### 4. 既存ページへの統合

#### ユーザープロフィールにフォローボタンを追加

```jsx
import FollowButton from '../components/FollowButton';

function UserProfile({ userId }) {
  return (
    <div>
      <h1>ユーザープロフィール</h1>
      <FollowButton userId={userId} />
    </div>
  );
}
```

#### レシピページにフォロー状態を表示

```jsx
import FollowButton from '../components/FollowButton';

function RecipeDetail({ recipe }) {
  return (
    <div>
      <h1>{recipe.title}</h1>
      <div className="author-info">
        <span>作成者: {recipe.user.display_name}</span>
        <FollowButton
          userId={recipe.user_id}
          onStatusChange={(isFollowing) => {
            console.log('Following status changed:', isFollowing);
          }}
        />
      </div>
    </div>
  );
}
```

#### ナビゲーションメニューに追加

```jsx
function Navigation() {
  return (
    <nav>
      <Link href="/">ホーム</Link>
      <Link href="/recipes">レシピ</Link>
      <Link href="/follow">フォロー</Link>
      <Link href="/profile">プロフィール</Link>
    </nav>
  );
}
```

### 5. スタイリング

CSS-in-JS（styled-jsx）が使用されていますが、必要に応じて以下に置き換え可能：

#### CSS Modules

```jsx
import styles from './FollowButton.module.css';

<button className={styles.followButton}>フォロー</button>
```

#### Tailwind CSS

```jsx
<button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
  フォロー
</button>
```

#### Styled Components

```jsx
import styled from 'styled-components';

const FollowButton = styled.button`
  padding: 8px 16px;
  background-color: #1da1f2;
  color: white;
  border: none;
  border-radius: 6px;
`;
```

## 認証統合

### 現在の実装（仮）

```python
def get_current_user_id() -> str:
  """現在のユーザーIDを取得（仮実装）"""
  return "user_1"
```

### JWT トークン認証への移行

#### バックエンド

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def get_current_user_id(
  credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
  """JWT トークンから現在のユーザーIDを取得"""
  try:
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("user_id")
    if not user_id:
      raise HTTPException(status_code=401, detail="無効なトークン")
    return user_id
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="トークンの有効期限切れ")
  except jwt.InvalidTokenError:
    raise HTTPException(status_code=401, detail="無効なトークン")
```

#### フロントエンド

```javascript
// トークンを保存
localStorage.setItem('authToken', token);

// API リクエストにトークンを含める
const response = await fetch('/api/v1/follow/user_2', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    'Content-Type': 'application/json',
  },
});
```

## データベース移行（SQLite）

JSONファイルからSQLiteへの移行手順：

### 1. マイグレーションスクリプト

```python
import json
import sqlite3

def migrate_to_sqlite():
  # JSONデータを読み込む
  with open('data/follows.json', 'r') as f:
    follows = json.load(f)

  # SQLite接続
  conn = sqlite3.connect('data/pri.db')
  cursor = conn.cursor()

  # テーブル作成
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS follows (
      id TEXT PRIMARY KEY,
      follower_id TEXT NOT NULL,
      following_id TEXT NOT NULL,
      created_at TEXT NOT NULL,
      UNIQUE(follower_id, following_id)
    )
  ''')

  # インデックス作成
  cursor.execute('CREATE INDEX IF NOT EXISTS idx_follower ON follows(follower_id)')
  cursor.execute('CREATE INDEX IF NOT EXISTS idx_following ON follows(following_id)')

  # データ挿入
  for follow in follows:
    cursor.execute(
      'INSERT OR IGNORE INTO follows VALUES (?, ?, ?, ?)',
      (follow['id'], follow['follower_id'], follow['following_id'], follow['created_at'])
    )

  conn.commit()
  conn.close()

if __name__ == '__main__':
  migrate_to_sqlite()
```

### 2. サービス層の修正

```python
import sqlite3

class FollowService:
  def __init__(self, db_path: str = "data/pri.db"):
    self.db_path = db_path

  def _get_connection(self):
    return sqlite3.connect(self.db_path)

  def follow_user(self, follower_id: str, following_id: str) -> Dict:
    conn = self._get_connection()
    cursor = conn.cursor()

    follow_id = f"{follower_id}_{following_id}_{datetime.now().timestamp()}"
    created_at = datetime.now().isoformat()

    cursor.execute(
      'INSERT OR IGNORE INTO follows VALUES (?, ?, ?, ?)',
      (follow_id, follower_id, following_id, created_at)
    )

    conn.commit()
    conn.close()

    return {
      "id": follow_id,
      "follower_id": follower_id,
      "following_id": following_id,
      "created_at": created_at
    }
```

## パフォーマンス最適化

### 1. キャッシュ実装

```python
from functools import lru_cache

class FollowService:
  @lru_cache(maxsize=1000)
  def get_follower_count(self, user_id: str) -> int:
    """フォロワー数をキャッシュ付きで取得"""
    follows = self._load_follows()
    return sum(1 for f in follows if f.get("following_id") == user_id)
```

### 2. ページネーション改善

```python
def get_followers(self, user_id: str, limit: int = 100, offset: int = 0, cursor: str = None):
  """カーソルベースのページネーション"""
  # cursor には最後のフォローIDを使用
  pass
```

### 3. フロントエンドキャッシュ

```javascript
// React Query を使用
import { useQuery } from '@tanstack/react-query';

function useFollowers(userId) {
  return useQuery({
    queryKey: ['followers', userId],
    queryFn: () => fetchFollowers(userId),
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });
}
```

## 監視とログ

### ログ設定

```python
import logging

logger = logging.getLogger(__name__)

class FollowService:
  def follow_user(self, follower_id: str, following_id: str) -> Dict:
    logger.info(f"User {follower_id} followed {following_id}")
    # ... 処理 ...
```

### メトリクス収集

```python
from prometheus_client import Counter

follow_counter = Counter('follow_total', 'Total number of follows')

def follow_user(self, follower_id: str, following_id: str) -> Dict:
  follow_counter.inc()
  # ... 処理 ...
```

## トラブルシューティング

### 問題: フォローAPIが404エラーを返す

**解決策:**
1. ルーターが正しく登録されているか確認
2. FastAPIサーバーが起動しているか確認
3. エンドポイントURLが正しいか確認

```bash
# ルーター確認
curl http://localhost:8001/docs
```

### 問題: フォロー状態が反映されない

**解決策:**
1. JSONファイルの書き込み権限を確認
2. ファイルロックの競合を確認
3. ブラウザキャッシュをクリア

```bash
# ファイル権限確認
ls -la data/follows.json

# 権限修正
chmod 644 data/follows.json
```

### 問題: フロントエンドでCORSエラーが発生

**解決策:**
FastAPIにCORSミドルウェアを追加

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)
```

## デプロイ

### 本番環境設定

```bash
# 環境変数設定
export ENVIRONMENT=production
export DATA_DIR=/var/lib/pri/data
export LOG_LEVEL=INFO

# サービス起動
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Nginx リバースプロキシ設定

```nginx
location /api/v1/follow {
  proxy_pass http://localhost:8001;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
}
```

## まとめ

この統合ガイドに従うことで、フォロー機能を既存のPRIアプリケーションに統合できます。

- バックエンド: FastAPI ルーター登録
- フロントエンド: React コンポーネント配置
- 認証: JWT トークン統合
- データベース: SQLite 移行
- パフォーマンス: キャッシュとページネーション
- 監視: ログとメトリクス

詳細は以下のドキュメントを参照してください：

- [フォロー機能仕様書](./FOLLOW_FEATURE.md)
- [CLAUDE.md](../CLAUDE.md)

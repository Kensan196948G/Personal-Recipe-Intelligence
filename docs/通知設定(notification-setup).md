# プッシュ通知機能セットアップガイド

Personal Recipe Intelligence のプッシュ通知機能（食事時間リマインダー）のセットアップ手順を説明します。

## 目次

1. [概要](#概要)
2. [必要な依存パッケージ](#必要な依存パッケージ)
3. [VAPIDキーの生成](#vapidキーの生成)
4. [環境変数の設定](#環境変数の設定)
5. [バックエンドの統合](#バックエンドの統合)
6. [フロントエンドの統合](#フロントエンドの統合)
7. [動作確認](#動作確認)
8. [トラブルシューティング](#トラブルシューティング)

## 概要

この機能は以下を提供します：

- プッシュ通知の購読/購読解除
- 食事時間リマインダー（朝食/昼食/夕食）
- カスタム通知メッセージ
- 通知スケジューリング

### アーキテクチャ

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend   │─────▶│   Browser   │
│     UI      │      │     API     │      │  Push API   │
└─────────────┘      └─────────────┘      └─────────────┘
      │                     │
      │              ┌──────┴──────┐
      │              │  Scheduler  │
      │              │ (APScheduler)│
      │              └─────────────┘
      │
┌─────┴─────────┐
│ Service Worker│
└───────────────┘
```

## 必要な依存パッケージ

### バックエンド (Python)

```bash
pip install -r backend/requirements-notification.txt
```

主な依存パッケージ：
- `pywebpush` - Web Push プロトコル実装
- `py-vapid` - VAPIDキー生成
- `APScheduler` - スケジューリング

### フロントエンド

通知機能はブラウザのネイティブAPIを使用するため、追加のパッケージは不要です。

## VAPIDキーの生成

VAPIDキーは Web Push の認証に使用されます。

### 1. キー生成スクリプトを実行

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
python scripts/generate_vapid_keys.py
```

### 2. 出力確認

以下のファイルが生成されます：

- `config/vapid_private_key.pem` - 秘密鍵（**絶対に公開しないこと**）
- `config/vapid_public_key.txt` - 公開鍵（フロントエンドで使用）

### 3. .gitignore に追加

```bash
echo "config/vapid_private_key.pem" >> .gitignore
```

## 環境変数の設定

### 1. .env ファイルを作成

```bash
cp .env.notification.example .env
```

### 2. 環境変数を設定

`.env` ファイルを編集：

```env
# VAPID設定
VAPID_PRIVATE_KEY_FILE=config/vapid_private_key.pem
VAPID_PUBLIC_KEY=<生成された公開鍵をここに貼り付け>
VAPID_CLAIM_EMAIL=mailto:your-email@example.com

# 通知サービス設定
NOTIFICATION_ENABLED=true
NOTIFICATION_MAX_RETRIES=3
NOTIFICATION_RETRY_DELAY=5

# デフォルトリマインダー時刻
DEFAULT_BREAKFAST_TIME=07:00
DEFAULT_LUNCH_TIME=12:00
DEFAULT_DINNER_TIME=18:00
```

## バックエンドの統合

### 1. main.pyに通知サービスを統合

```python
# backend/main.py

from fastapi import FastAPI
from backend.api.routers import notification
from backend.api.routers.notification import init_notification_service
import os
from pathlib import Path

app = FastAPI(title="Personal Recipe Intelligence API")

# 環境変数から設定を読み込み
VAPID_PRIVATE_KEY_FILE = os.getenv("VAPID_PRIVATE_KEY_FILE", "config/vapid_private_key.pem")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_CLAIM_EMAIL = os.getenv("VAPID_CLAIM_EMAIL", "mailto:admin@example.com")

# VAPID秘密鍵を読み込み
with open(VAPID_PRIVATE_KEY_FILE, "rb") as f:
  vapid_private_key = f.read()

# 通知サービスを初期化
init_notification_service(
  vapid_private_key=vapid_private_key.decode('utf-8'),
  vapid_public_key=VAPID_PUBLIC_KEY,
  vapid_claims={"sub": VAPID_CLAIM_EMAIL}
)

# ルーターを登録
app.include_router(notification.router)

# 他のルーター...
```

### 2. 起動確認

```bash
cd backend
uvicorn main:app --reload
```

APIドキュメント: http://localhost:8001/docs

## フロントエンドの統合

### 1. HTMLにスクリプトを追加

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>Personal Recipe Intelligence</title>
</head>
<body>
  <div id="app"></div>

  <!-- Notification Manager -->
  <script src="/js/notification-manager.js"></script>

  <!-- React App -->
  <script type="module">
    import React from 'react';
    import ReactDOM from 'react-dom';
    import MealReminderSettings from './components/MealReminderSettings.jsx';

    ReactDOM.render(
      <MealReminderSettings notificationManager={notificationManager} />,
      document.getElementById('app')
    );
  </script>
</body>
</html>
```

### 2. Service Workerを配置

`frontend/service-worker.js` がルートパスで提供されるように設定します。

### 3. manifest.json を作成（オプション）

```json
{
  "name": "Personal Recipe Intelligence",
  "short_name": "PRI",
  "icons": [
    {
      "src": "/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ],
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2196f3"
}
```

## 動作確認

### 1. 通知許可をリクエスト

```javascript
const manager = new NotificationManager();
await manager.requestPermission();
```

### 2. 購読

```javascript
await manager.subscribe();
```

### 3. テスト通知を送信

```javascript
await manager.sendTestNotification('テスト', 'これはテスト通知です');
```

### 4. 食事リマインダーを設定

```javascript
await manager.setMealReminder('breakfast', '07:00', true, 'おはようございます！');
```

### 5. ブラウザコンソールで確認

```javascript
// 購読状態を確認
console.log(await manager.isSubscribed());

// スケジュールを確認
console.log(await manager.getMealSchedules());
```

## API エンドポイント

### 公開鍵取得
```
GET /api/v1/notifications/public-key
```

### 購読
```
POST /api/v1/notifications/subscribe
{
  "user_id": "user123",
  "subscription": { ... }
}
```

### 購読解除
```
DELETE /api/v1/notifications/unsubscribe
{
  "user_id": "user123"
}
```

### 通知送信
```
POST /api/v1/notifications/send
{
  "user_id": "user123",
  "title": "通知タイトル",
  "body": "通知本文"
}
```

### 食事リマインダー設定
```
POST /api/v1/notifications/meal-reminder
{
  "user_id": "user123",
  "meal_type": "breakfast",
  "reminder_time": "07:00",
  "enabled": true,
  "custom_message": "おはようございます！"
}
```

### スケジュール取得
```
GET /api/v1/notifications/schedule?user_id=user123
```

## トラブルシューティング

### 通知が表示されない

1. **ブラウザの通知許可を確認**
   - Chrome: 設定 > プライバシーとセキュリティ > サイトの設定 > 通知
   - Firefox: 設定 > プライバシーとセキュリティ > 権限 > 通知

2. **Service Worker が登録されているか確認**
   ```javascript
   navigator.serviceWorker.getRegistrations().then(console.log);
   ```

3. **コンソールエラーを確認**
   - ブラウザの開発者ツールでエラーメッセージを確認

### VAPIDキーエラー

```
Error: VAPID public key is invalid
```

- 公開鍵が正しく設定されているか確認
- 環境変数が正しく読み込まれているか確認

### スケジューラーが動作しない

```python
# ログレベルをDEBUGに設定
import logging
logging.basicConfig(level=logging.DEBUG)
```

### HTTPSが必要

プッシュ通知は HTTPS が必須です（localhost は例外）。

開発環境で HTTPS を有効にする：

```bash
# 自己署名証明書を生成
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# uvicornでHTTPSを有効化
uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

## セキュリティ考慮事項

1. **秘密鍵の管理**
   - `vapid_private_key.pem` は絶対に公開しない
   - `.gitignore` に追加
   - 本番環境では環境変数または Key Vault で管理

2. **購読情報の保護**
   - データベースに保存する場合は暗号化を検討
   - 定期的に無効な購読を削除

3. **レート制限**
   - 通知送信頻度を制限
   - スパム防止策を実装

## パフォーマンス最適化

1. **バッチ送信**
   - 複数ユーザーへの通知を一括送信

2. **非同期処理**
   - 通知送信を非同期タスクキューで処理

3. **キャッシュ**
   - 購読情報をメモリキャッシュ

## 参考資料

- [Web Push API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [Service Worker API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [VAPID Specification](https://datatracker.ietf.org/doc/html/rfc8292)
- [pywebpush Documentation](https://github.com/web-push-libs/pywebpush)

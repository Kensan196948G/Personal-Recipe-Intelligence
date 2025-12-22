# プッシュ通知機能 - Personal Recipe Intelligence

Personal Recipe Intelligence プロジェクトのプッシュ通知機能（食事時間リマインダー）の実装ドキュメントです。

## 概要

このプロジェクトでは、Web Push API を使用したプッシュ通知機能を実装しました。食事時間（朝食・昼食・夕食）のリマインダー通知を送信し、ユーザーに適切なタイミングで料理を提案します。

## 機能一覧

### バックエンド機能

- **プッシュ通知送信** - Web Push プロトコルでブラウザに通知を送信
- **購読管理** - ユーザーの通知購読/購読解除
- **スケジューリング** - APScheduler による時刻ベースの通知スケジュール管理
- **食事リマインダー** - 朝食/昼食/夕食の3つの時間帯に対応
- **カスタムメッセージ** - 各リマインダーにカスタムメッセージを設定可能

### フロントエンド機能

- **通知許可リクエスト** - ブラウザに通知許可を要求
- **購読処理** - Service Worker 登録とプッシュマネージャーの購読
- **通知表示** - リアルタイムで通知を受信・表示
- **設定UI** - 食事リマインダーの時刻とメッセージを設定

## ファイル構成

```
personal-recipe-intelligence/
├── backend/
│   ├── services/
│   │   └── notification_service.py          # 通知サービス本体
│   ├── api/
│   │   └── routers/
│   │       └── notification.py               # 通知API ルーター
│   └── requirements-notification.txt         # 依存パッケージ
├── frontend/
│   ├── js/
│   │   └── notification-manager.js           # 通知マネージャー（フロントエンド）
│   ├── components/
│   │   └── MealReminderSettings.jsx         # 設定UI（React）
│   ├── service-worker.js                     # Service Worker
│   └── tests/
│       └── notification-manager.test.js      # フロントエンドテスト
├── scripts/
│   ├── generate_vapid_keys.py                # VAPIDキー生成スクリプト
│   └── setup-notification.sh                 # セットアップスクリプト
├── tests/
│   ├── test_notification_service.py          # サービステスト
│   └── test_notification_api.py              # APIテスト
├── examples/
│   ├── notification_integration_example.py   # バックエンド統合例
│   └── notification_frontend_example.html    # フロントエンド使用例
├── docs/
│   └── NOTIFICATION_SETUP.md                 # セットアップガイド
├── config/
│   ├── vapid_private_key.pem                 # VAPID秘密鍵（生成後）
│   └── vapid_public_key.txt                  # VAPID公開鍵（生成後）
└── .env.notification.example                 # 環境変数サンプル
```

## クイックスタート

### 1. セットアップスクリプトを実行

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
chmod +x scripts/setup-notification.sh
./scripts/setup-notification.sh
```

### 2. 環境変数を設定

`.env` ファイルを編集：

```env
VAPID_PRIVATE_KEY_FILE=config/vapid_private_key.pem
VAPID_PUBLIC_KEY=<生成された公開鍵>
VAPID_CLAIM_EMAIL=mailto:your-email@example.com
```

### 3. バックエンドを起動

```bash
cd backend
uvicorn main:app --reload
```

### 4. フロントエンドを開く

ブラウザで以下を開く：

```
http://localhost:8001/examples/notification_frontend_example.html
```

## 使用方法

### バックエンド統合

```python
from fastapi import FastAPI
from backend.api.routers import notification
from backend.api.routers.notification import init_notification_service
import os

app = FastAPI()

# VAPID設定を読み込み
with open("config/vapid_private_key.pem", "rb") as f:
    vapid_private_key = f.read().decode('utf-8')

vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")

# 通知サービスを初期化
init_notification_service(
    vapid_private_key=vapid_private_key,
    vapid_public_key=vapid_public_key,
    vapid_claims={"sub": "mailto:admin@example.com"}
)

# ルーターを登録
app.include_router(notification.router)
```

### フロントエンド使用例

```javascript
// Notification Managerを初期化
const manager = new NotificationManager();

// 通知許可をリクエスト
await manager.requestPermission();

// 購読
await manager.subscribe();

// 食事リマインダーを設定
await manager.setMealReminder('breakfast', '07:00', true, 'おはようございます！');
await manager.setMealReminder('lunch', '12:00', true, '昼食の時間です！');
await manager.setMealReminder('dinner', '18:00', true, '夕食の時間です！');

// テスト通知を送信
await manager.sendTestNotification('テスト', 'これはテスト通知です');

// スケジュールを取得
const schedules = await manager.getMealSchedules();
console.log(schedules);
```

### React コンポーネント

```jsx
import MealReminderSettings from './components/MealReminderSettings.jsx';

function App() {
  const notificationManager = new NotificationManager();

  return (
    <div>
      <MealReminderSettings notificationManager={notificationManager} />
    </div>
  );
}
```

## API エンドポイント

### 公開鍵取得

```
GET /api/v1/notifications/public-key
```

レスポンス：
```json
{
  "status": "ok",
  "data": {
    "public_key": "BN..."
  },
  "error": null
}
```

### 購読

```
POST /api/v1/notifications/subscribe
```

リクエスト：
```json
{
  "user_id": "user123",
  "subscription": {
    "endpoint": "https://fcm.googleapis.com/...",
    "keys": {
      "p256dh": "...",
      "auth": "..."
    }
  }
}
```

### 購読解除

```
DELETE /api/v1/notifications/unsubscribe
```

リクエスト：
```json
{
  "user_id": "user123"
}
```

### 通知送信

```
POST /api/v1/notifications/send
```

リクエスト：
```json
{
  "user_id": "user123",
  "title": "通知タイトル",
  "body": "通知本文",
  "icon": "/icon.png",
  "data": {}
}
```

### 食事リマインダー設定

```
POST /api/v1/notifications/meal-reminder
```

リクエスト：
```json
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

レスポンス：
```json
{
  "status": "ok",
  "data": {
    "breakfast": {
      "time": "07:00",
      "enabled": true,
      "custom_message": "おはようございます！"
    },
    "lunch": {
      "time": "12:00",
      "enabled": true,
      "custom_message": null
    }
  },
  "error": null
}
```

## テスト

### バックエンドテスト

```bash
# サービステスト
pytest tests/test_notification_service.py -v

# APIテスト
pytest tests/test_notification_api.py -v

# カバレッジ付き
pytest tests/ --cov=backend/services/notification_service --cov-report=html
```

### フロントエンドテスト

```bash
cd frontend
bun test tests/notification-manager.test.js
```

## 技術仕様

### 使用技術

- **バックエンド**
  - Python 3.11
  - FastAPI
  - pywebpush (Web Push プロトコル)
  - py-vapid (VAPIDキー生成)
  - APScheduler (スケジューリング)

- **フロントエンド**
  - JavaScript (ES6+)
  - Service Worker API
  - Push API
  - Notification API
  - React (UI コンポーネント)

### セキュリティ

- **VAPID認証** - Web Push の送信元認証
- **HTTPS必須** - 本番環境では HTTPS が必須（localhost は例外）
- **秘密鍵保護** - VAPID秘密鍵は暗号化して保存
- **購読情報の保護** - 購読情報は機密データとして扱う

### パフォーマンス

- **非同期処理** - 通知送信は非同期で実行
- **バッチ送信** - 複数ユーザーへの通知を効率的に送信
- **スケジューラー最適化** - APScheduler で効率的なジョブ管理

## トラブルシューティング

### 通知が表示されない

1. ブラウザの通知許可を確認
2. Service Worker が登録されているか確認（開発者ツール > Application > Service Workers）
3. コンソールエラーを確認

### VAPIDキーエラー

```
Error: VAPID public key is invalid
```

- 公開鍵が正しく設定されているか `.env` を確認
- VAPIDキーを再生成: `python scripts/generate_vapid_keys.py`

### スケジューラーが動作しない

- ログレベルを DEBUG に設定してログを確認
- APScheduler が正しく初期化されているか確認

## 参考資料

- [Web Push API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [Service Worker API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [VAPID Specification (RFC 8292)](https://datatracker.ietf.org/doc/html/rfc8292)
- [pywebpush GitHub](https://github.com/web-push-libs/pywebpush)

## ライセンス

MIT License

## 作成者

Personal Recipe Intelligence Development Team

## 更新履歴

- 2024-12-11: プッシュ通知機能初版リリース
  - バックエンドサービス実装
  - APIルーター実装
  - フロントエンド通知マネージャー実装
  - 食事リマインダー設定UI実装
  - VAPIDキー生成スクリプト実装
  - テスト・ドキュメント整備

"""
Notification Integration Example
プッシュ通知機能の統合サンプル
"""

import os
import asyncio
from pathlib import Path
from fastapi import FastAPI
from backend.api.routers import notification
from backend.api.routers.notification import init_notification_service


def create_app():
  """
  FastAPIアプリケーションを作成し、プッシュ通知機能を統合

  Returns:
    FastAPI app instance
  """
  app = FastAPI(
    title="Personal Recipe Intelligence API",
    description="Recipe management with push notifications",
    version="1.0.0",
  )

  # 環境変数から設定を読み込み
  vapid_private_key_file = os.getenv(
    "VAPID_PRIVATE_KEY_FILE", "config/vapid_private_key.pem"
  )
  vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")
  vapid_claim_email = os.getenv(
    "VAPID_CLAIM_EMAIL", "mailto:admin@example.com"
  )

  # VAPID秘密鍵を読み込み
  try:
    with open(vapid_private_key_file, "rb") as f:
      vapid_private_key = f.read().decode("utf-8")
  except FileNotFoundError:
    print(f"Error: VAPID private key file not found: {vapid_private_key_file}")
    print("Please run: python scripts/generate_vapid_keys.py")
    raise

  # 通知サービスを初期化
  init_notification_service(
    vapid_private_key=vapid_private_key,
    vapid_public_key=vapid_public_key,
    vapid_claims={"sub": vapid_claim_email},
  )

  # 通知ルーターを登録
  app.include_router(notification.router)

  @app.get("/")
  async def root():
    """ルートエンドポイント"""
    return {
      "message": "Personal Recipe Intelligence API",
      "features": ["recipes", "notifications"],
      "docs": "/docs",
    }

  @app.on_event("startup")
  async def startup_event():
    """起動時の処理"""
    print("Starting Personal Recipe Intelligence API...")
    print(f"VAPID Public Key: {vapid_public_key[:20]}...")
    print("Notification service initialized")

  @app.on_event("shutdown")
  async def shutdown_event():
    """シャットダウン時の処理"""
    print("Shutting down notification service...")
    if notification.notification_service:
      notification.notification_service.shutdown()
    print("API shutdown complete")

  return app


async def example_usage():
  """
  プッシュ通知機能の使用例
  """
  print("\n=== Push Notification Usage Example ===\n")

  # サンプル購読情報（実際はブラウザから送信される）
  sample_subscription = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/example",
    "keys": {"p256dh": "sample-p256dh-key", "auth": "sample-auth-key"},
  }

  # 1. ユーザーを購読登録
  print("1. Subscribing user...")
  from backend.api.routers.notification import notification_service

  if notification_service:
    result = notification_service.subscribe("user123", sample_subscription)
    print(f"   Result: {result['status']}")

    # 2. テスト通知を送信
    print("\n2. Sending test notification...")
    result = await notification_service.send_notification(
      user_id="user123",
      title="Welcome to Personal Recipe Intelligence",
      body="Your notification system is working!",
    )
    print(f"   Result: {result['status']}")

    # 3. 食事リマインダーを設定
    print("\n3. Setting meal reminders...")
    meals = {
      "breakfast": ("07:00", "Good morning! Time for breakfast!"),
      "lunch": ("12:00", "Lunch time! What are you having?"),
      "dinner": ("18:00", "Dinner time! Let's cook something delicious!"),
    }

    for meal_type, (time, message) in meals.items():
      result = notification_service.set_meal_reminder(
        user_id="user123",
        meal_type=meal_type,
        reminder_time=time,
        enabled=True,
        custom_message=message,
      )
      print(f"   {meal_type}: {result['status']}")

    # 4. スケジュールを確認
    print("\n4. Getting meal schedules...")
    result = notification_service.get_meal_schedules("user123")
    if result["status"] == "ok":
      schedules = result["data"]
      print("   Configured schedules:")
      for meal_type, config in schedules.items():
        print(
          f"     - {meal_type}: {config['time']} (enabled: {config['enabled']})"
        )

    # 5. 全スケジュールを表示
    print("\n5. All registered schedules:")
    all_schedules = notification_service.get_all_schedules()
    for schedule in all_schedules:
      print(f"   - {schedule['id']}: next run at {schedule['next_run_time']}")

  print("\n=== Example Complete ===\n")


if __name__ == "__main__":
  # アプリケーションを作成
  app = create_app()

  # 使用例を実行
  asyncio.run(example_usage())

  # サーバーを起動する場合は以下をコメント解除
  # import uvicorn
  # uvicorn.run(app, host="0.0.0.0", port=8000)

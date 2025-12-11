"""
Notification Service
プッシュ通知送信・スケジューリング・購読管理を行うサービス
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pywebpush import webpush, WebPushException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class NotificationService:
    """プッシュ通知管理サービス"""

    def __init__(
        self,
        vapid_private_key: str,
        vapid_public_key: str,
        vapid_claims: Dict[str, str],
    ):
        """
        初期化

        Args:
          vapid_private_key: VAPID秘密鍵
          vapid_public_key: VAPID公開鍵
          vapid_claims: VAPIDクレーム（mailto等）
        """
        self.vapid_private_key = vapid_private_key
        self.vapid_public_key = vapid_public_key
        self.vapid_claims = vapid_claims
        self.subscriptions: Dict[str, Dict[str, Any]] = {}
        self.meal_schedules: Dict[str, Dict[str, Any]] = {}
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        logger.info("NotificationService initialized")

    def get_public_key(self) -> str:
        """
        VAPID公開鍵を取得

        Returns:
          VAPID公開鍵
        """
        return self.vapid_public_key

    def subscribe(
        self, user_id: str, subscription_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        プッシュ通知を購読

        Args:
          user_id: ユーザーID
          subscription_info: Push APIのsubscriptionオブジェクト

        Returns:
          購読情報
        """
        try:
            self.subscriptions[user_id] = {
                "subscription": subscription_info,
                "subscribed_at": datetime.now().isoformat(),
            }
            logger.info(f"User {user_id} subscribed to push notifications")
            return {
                "status": "ok",
                "data": {"user_id": user_id, "subscribed": True},
                "error": None,
            }
        except Exception as e:
            logger.error(f"Subscribe error: {e}", exc_info=True)
            return {"status": "error", "data": None, "error": str(e)}

    def unsubscribe(self, user_id: str) -> Dict[str, Any]:
        """
        プッシュ通知を購読解除

        Args:
          user_id: ユーザーID

        Returns:
          購読解除情報
        """
        try:
            if user_id in self.subscriptions:
                del self.subscriptions[user_id]
                logger.info(f"User {user_id} unsubscribed from push notifications")

            # 食事リマインダースケジュールも削除
            if user_id in self.meal_schedules:
                self._remove_meal_schedules(user_id)

            return {
                "status": "ok",
                "data": {"user_id": user_id, "subscribed": False},
                "error": None,
            }
        except Exception as e:
            logger.error(f"Unsubscribe error: {e}", exc_info=True)
            return {"status": "error", "data": None, "error": str(e)}

    async def send_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        icon: Optional[str] = None,
        badge: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        プッシュ通知を送信

        Args:
          user_id: ユーザーID
          title: 通知タイトル
          body: 通知本文
          icon: アイコンURL
          badge: バッジURL
          data: カスタムデータ

        Returns:
          送信結果
        """
        try:
            if user_id not in self.subscriptions:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"User {user_id} is not subscribed",
                }

            subscription_info = self.subscriptions[user_id]["subscription"]

            # 通知ペイロード作成
            payload = {
                "title": title,
                "body": body,
                "icon": icon or "/icon-192x192.png",
                "badge": badge or "/badge-72x72.png",
                "timestamp": datetime.now().isoformat(),
            }

            if data:
                payload["data"] = data

            # プッシュ通知送信
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims,
            )

            logger.info(f"Notification sent to user {user_id}: {title}")
            return {
                "status": "ok",
                "data": {"user_id": user_id, "sent": True, "title": title},
                "error": None,
            }

        except WebPushException as e:
            logger.error(f"WebPush error for user {user_id}: {e}", exc_info=True)

            # 410 Gone の場合は購読を削除
            if e.response and e.response.status_code == 410:
                self.unsubscribe(user_id)

            return {"status": "error", "data": None, "error": str(e)}

        except Exception as e:
            logger.error(f"Send notification error: {e}", exc_info=True)
            return {"status": "error", "data": None, "error": str(e)}

    def set_meal_reminder(
        self,
        user_id: str,
        meal_type: str,
        reminder_time: str,
        enabled: bool = True,
        custom_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        食事リマインダーを設定

        Args:
          user_id: ユーザーID
          meal_type: 食事タイプ（breakfast, lunch, dinner）
          reminder_time: リマインダー時刻（HH:MM形式）
          enabled: 有効/無効
          custom_message: カスタムメッセージ

        Returns:
          設定結果
        """
        try:
            if meal_type not in ["breakfast", "lunch", "dinner"]:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid meal_type. Must be breakfast, lunch, or dinner",
                }

            # 時刻パース
            try:
                hour, minute = map(int, reminder_time.split(":"))
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    raise ValueError("Invalid time range")
            except Exception:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid time format. Use HH:MM",
                }

            # ユーザーの食事スケジュール初期化
            if user_id not in self.meal_schedules:
                self.meal_schedules[user_id] = {}

            # 設定を保存
            self.meal_schedules[user_id][meal_type] = {
                "time": reminder_time,
                "enabled": enabled,
                "custom_message": custom_message,
            }

            # 既存のジョブを削除
            job_id = f"meal_reminder_{user_id}_{meal_type}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # 有効な場合はスケジュールを登録
            if enabled:
                self.scheduler.add_job(
                    self._send_meal_reminder,
                    CronTrigger(hour=hour, minute=minute),
                    id=job_id,
                    args=[user_id, meal_type, custom_message],
                    replace_existing=True,
                )
                logger.info(
                    f"Meal reminder scheduled for user {user_id}: {meal_type} at {reminder_time}"
                )

            return {
                "status": "ok",
                "data": {
                    "user_id": user_id,
                    "meal_type": meal_type,
                    "reminder_time": reminder_time,
                    "enabled": enabled,
                },
                "error": None,
            }

        except Exception as e:
            logger.error(f"Set meal reminder error: {e}", exc_info=True)
            return {"status": "error", "data": None, "error": str(e)}

    async def _send_meal_reminder(
        self, user_id: str, meal_type: str, custom_message: Optional[str] = None
    ):
        """
        食事リマインダーを送信（内部メソッド）

        Args:
          user_id: ユーザーID
          meal_type: 食事タイプ
          custom_message: カスタムメッセージ
        """
        try:
            meal_names = {
                "breakfast": "朝食",
                "lunch": "昼食",
                "dinner": "夕食",
            }

            title = f"{meal_names.get(meal_type, '食事')}の時間です"
            body = (
                custom_message
                or f"今日の{meal_names.get(meal_type, '食事')}は何にしますか？"
            )

            await self.send_notification(
                user_id=user_id,
                title=title,
                body=body,
                data={"type": "meal_reminder", "meal_type": meal_type},
            )

        except Exception as e:
            logger.error(f"Send meal reminder error: {e}", exc_info=True)

    def get_meal_schedules(self, user_id: str) -> Dict[str, Any]:
        """
        食事リマインダースケジュールを取得

        Args:
          user_id: ユーザーID

        Returns:
          スケジュール情報
        """
        try:
            schedules = self.meal_schedules.get(user_id, {})
            return {"status": "ok", "data": schedules, "error": None}
        except Exception as e:
            logger.error(f"Get meal schedules error: {e}", exc_info=True)
            return {"status": "error", "data": None, "error": str(e)}

    def _remove_meal_schedules(self, user_id: str):
        """
        ユーザーの食事リマインダースケジュールを削除

        Args:
          user_id: ユーザーID
        """
        for meal_type in ["breakfast", "lunch", "dinner"]:
            job_id = f"meal_reminder_{user_id}_{meal_type}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

        if user_id in self.meal_schedules:
            del self.meal_schedules[user_id]

        logger.info(f"Removed all meal schedules for user {user_id}")

    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """
        全ての登録済みスケジュールを取得

        Returns:
          スケジュールリスト
        """
        try:
            jobs = self.scheduler.get_jobs()
            schedules = []

            for job in jobs:
                schedules.append(
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run_time": (
                            job.next_run_time.isoformat() if job.next_run_time else None
                        ),
                    }
                )

            return schedules
        except Exception as e:
            logger.error(f"Get all schedules error: {e}", exc_info=True)
            return []

    def shutdown(self):
        """サービスをシャットダウン"""
        try:
            self.scheduler.shutdown()
            logger.info("NotificationService shutdown")
        except Exception as e:
            logger.error(f"Shutdown error: {e}", exc_info=True)

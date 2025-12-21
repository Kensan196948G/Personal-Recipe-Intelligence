"""
Notification API Router
プッシュ通知関連のAPIエンドポイント
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from backend.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

# グローバルなNotificationServiceインスタンス（依存性注入で使用）
notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """
    NotificationServiceの依存性注入

    Returns:
      NotificationService インスタンス

    Raises:
      HTTPException: サービスが初期化されていない場合
    """
    if notification_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notification service is not initialized",
        )
    return notification_service


def init_notification_service(
    vapid_private_key: str, vapid_public_key: str, vapid_claims: Dict[str, str]
):
    """
    NotificationServiceを初期化

    Args:
      vapid_private_key: VAPID秘密鍵
      vapid_public_key: VAPID公開鍵
      vapid_claims: VAPIDクレーム
    """
    global notification_service
    notification_service = NotificationService(
        vapid_private_key=vapid_private_key,
        vapid_public_key=vapid_public_key,
        vapid_claims=vapid_claims,
    )
    logger.info("Notification service initialized in router")


# リクエスト/レスポンスモデル


class SubscribeRequest(BaseModel):
    """購読リクエスト"""

    user_id: str = Field(..., description="ユーザーID")
    subscription: Dict[str, Any] = Field(..., description="Push API subscription情報")


class UnsubscribeRequest(BaseModel):
    """購読解除リクエスト"""

    user_id: str = Field(..., description="ユーザーID")


class SendNotificationRequest(BaseModel):
    """通知送信リクエスト"""

    user_id: str = Field(..., description="ユーザーID")
    title: str = Field(..., description="通知タイトル")
    body: str = Field(..., description="通知本文")
    icon: Optional[str] = Field(None, description="アイコンURL")
    badge: Optional[str] = Field(None, description="バッジURL")
    data: Optional[Dict[str, Any]] = Field(None, description="カスタムデータ")


class MealReminderRequest(BaseModel):
    """食事リマインダー設定リクエスト"""

    user_id: str = Field(..., description="ユーザーID")
    meal_type: str = Field(..., description="食事タイプ (breakfast/lunch/dinner)")
    reminder_time: str = Field(..., description="リマインダー時刻 (HH:MM)")
    enabled: bool = Field(True, description="有効/無効")
    custom_message: Optional[str] = Field(None, description="カスタムメッセージ")


class APIResponse(BaseModel):
    """標準APIレスポンス"""

    status: str
    data: Optional[Any] = None
    error: Optional[str] = None


# エンドポイント


@router.get("/public-key")
async def get_public_key(
    service: NotificationService = Depends(get_notification_service),
) -> APIResponse:
    """
    VAPID公開鍵を取得

    Returns:
      VAPID公開鍵
    """
    try:
        public_key = service.get_public_key()
        return APIResponse(status="ok", data={"public_key": public_key}, error=None)
    except Exception as e:
        logger.error(f"Get public key error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/subscribe")
async def subscribe(
    request: SubscribeRequest,
    service: NotificationService = Depends(get_notification_service),
) -> APIResponse:
    """
    プッシュ通知を購読

    Args:
      request: 購読リクエスト

    Returns:
      購読結果
    """
    try:
        result = service.subscribe(
            user_id=request.user_id, subscription_info=request.subscription
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
            )

        return APIResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscribe error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/unsubscribe")
async def unsubscribe(
    request: UnsubscribeRequest,
    service: NotificationService = Depends(get_notification_service),
) -> APIResponse:
    """
    プッシュ通知を購読解除

    Args:
      request: 購読解除リクエスト

    Returns:
      購読解除結果
    """
    try:
        result = service.unsubscribe(user_id=request.user_id)

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
            )

        return APIResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unsubscribe error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/send")
async def send_notification(
    request: SendNotificationRequest,
    service: NotificationService = Depends(get_notification_service),
) -> APIResponse:
    """
    プッシュ通知を送信

    Args:
      request: 通知送信リクエスト

    Returns:
      送信結果
    """
    try:
        result = await service.send_notification(
            user_id=request.user_id,
            title=request.title,
            body=request.body,
            icon=request.icon,
            badge=request.badge,
            data=request.data,
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
            )

        return APIResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send notification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/schedule")
async def get_schedule(
    user_id: str, service: NotificationService = Depends(get_notification_service)
) -> APIResponse:
    """
    食事リマインダースケジュールを取得

    Args:
      user_id: ユーザーID

    Returns:
      スケジュール情報
    """
    try:
        result = service.get_meal_schedules(user_id=user_id)

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
            )

        return APIResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get schedule error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/meal-reminder")
async def set_meal_reminder(
    request: MealReminderRequest,
    service: NotificationService = Depends(get_notification_service),
) -> APIResponse:
    """
    食事リマインダーを設定

    Args:
      request: 食事リマインダー設定リクエスト

    Returns:
      設定結果
    """
    try:
        result = service.set_meal_reminder(
            user_id=request.user_id,
            meal_type=request.meal_type,
            reminder_time=request.reminder_time,
            enabled=request.enabled,
            custom_message=request.custom_message,
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
            )

        return APIResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set meal reminder error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/schedules/all")
async def get_all_schedules(
    service: NotificationService = Depends(get_notification_service),
) -> APIResponse:
    """
    全ての登録済みスケジュールを取得（管理用）

    Returns:
      スケジュールリスト
    """
    try:
        schedules = service.get_all_schedules()
        return APIResponse(status="ok", data={"schedules": schedules}, error=None)
    except Exception as e:
        logger.error(f"Get all schedules error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

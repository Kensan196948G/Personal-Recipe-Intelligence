"""
Notification Service のテスト

NotificationService の以下の機能をテスト:
- 公開鍵取得
- プッシュ通知購読・購読解除
- プッシュ通知送信
- 食事リマインダー設定
- スケジュール管理
- エラーハンドリング
- WebPush例外処理

目標カバレッジ: 80%
テスト関数数: 30-40
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, MagicMock, patch, AsyncMock, call
from datetime import datetime

from backend.services.notification_service import NotificationService


# ================================================================================
# Fixtures
# ================================================================================

@pytest.fixture
def vapid_keys():
    """VAPID鍵情報"""
    return {
        "private_key": "test_private_key_012345678901234567890123456789",
        "public_key": "test_public_key_012345678901234567890123456789",
        "claims": {"sub": "mailto:test@example.com"},
    }


@pytest.fixture
def notification_service(vapid_keys):
    """NotificationServiceインスタンス"""
    service = NotificationService(
        vapid_private_key=vapid_keys["private_key"],
        vapid_public_key=vapid_keys["public_key"],
        vapid_claims=vapid_keys["claims"],
    )
    yield service
    # クリーンアップ
    service.shutdown()


@pytest.fixture
def sample_subscription():
    """サンプル購読情報"""
    return {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test123",
        "keys": {
            "p256dh": "test_p256dh_key",
            "auth": "test_auth_key",
        },
    }


# ================================================================================
# 初期化テスト (4 tests)
# ================================================================================

def test_init_notification_service(vapid_keys):
    """正常な初期化"""
    service = NotificationService(
        vapid_private_key=vapid_keys["private_key"],
        vapid_public_key=vapid_keys["public_key"],
        vapid_claims=vapid_keys["claims"],
    )

    assert service.vapid_private_key == vapid_keys["private_key"]
    assert service.vapid_public_key == vapid_keys["public_key"]
    assert service.vapid_claims == vapid_keys["claims"]
    assert service.subscriptions == {}
    assert service.meal_schedules == {}
    assert service.scheduler is not None

    service.shutdown()


def test_init_empty_subscriptions(notification_service):
    """購読リストは空で開始"""
    assert len(notification_service.subscriptions) == 0


def test_init_empty_meal_schedules(notification_service):
    """食事スケジュールは空で開始"""
    assert len(notification_service.meal_schedules) == 0


def test_init_scheduler_started(notification_service):
    """スケジューラーが起動している"""
    assert notification_service.scheduler.running


# ================================================================================
# 公開鍵取得テスト (2 tests)
# ================================================================================

def test_get_public_key(notification_service, vapid_keys):
    """公開鍵を取得"""
    public_key = notification_service.get_public_key()

    assert public_key == vapid_keys["public_key"]


def test_get_public_key_returns_string(notification_service):
    """公開鍵が文字列"""
    public_key = notification_service.get_public_key()

    assert isinstance(public_key, str)
    assert len(public_key) > 0


# ================================================================================
# 購読管理テスト (8 tests)
# ================================================================================

def test_subscribe_success(notification_service, sample_subscription):
    """購読成功"""
    result = notification_service.subscribe("user1", sample_subscription)

    assert result["status"] == "ok"
    assert result["data"]["user_id"] == "user1"
    assert result["data"]["subscribed"] is True
    assert result["error"] is None
    assert "user1" in notification_service.subscriptions


def test_subscribe_stores_subscription_info(notification_service, sample_subscription):
    """購読情報が保存される"""
    notification_service.subscribe("user2", sample_subscription)

    subscription = notification_service.subscriptions["user2"]
    assert subscription["subscription"] == sample_subscription
    assert "subscribed_at" in subscription


def test_subscribe_multiple_users(notification_service, sample_subscription):
    """複数ユーザーの購読"""
    notification_service.subscribe("user1", sample_subscription)
    notification_service.subscribe("user2", sample_subscription)
    notification_service.subscribe("user3", sample_subscription)

    assert len(notification_service.subscriptions) == 3
    assert "user1" in notification_service.subscriptions
    assert "user2" in notification_service.subscriptions
    assert "user3" in notification_service.subscriptions


def test_subscribe_overwrites_existing(notification_service, sample_subscription):
    """既存購読を上書き"""
    notification_service.subscribe("user1", sample_subscription)

    new_subscription = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/new456",
        "keys": {"p256dh": "new_p256dh", "auth": "new_auth"},
    }
    notification_service.subscribe("user1", new_subscription)

    assert notification_service.subscriptions["user1"]["subscription"] == new_subscription


def test_unsubscribe_success(notification_service, sample_subscription):
    """購読解除成功"""
    notification_service.subscribe("user1", sample_subscription)

    result = notification_service.unsubscribe("user1")

    assert result["status"] == "ok"
    assert result["data"]["user_id"] == "user1"
    assert result["data"]["subscribed"] is False
    assert result["error"] is None
    assert "user1" not in notification_service.subscriptions


def test_unsubscribe_nonexistent_user(notification_service):
    """存在しないユーザーの購読解除"""
    result = notification_service.unsubscribe("nonexistent_user")

    assert result["status"] == "ok"
    assert result["data"]["subscribed"] is False


def test_unsubscribe_removes_meal_schedules(notification_service, sample_subscription):
    """購読解除で食事スケジュールも削除"""
    notification_service.subscribe("user1", sample_subscription)
    notification_service.set_meal_reminder("user1", "breakfast", "07:00", enabled=True)

    notification_service.unsubscribe("user1")

    assert "user1" not in notification_service.meal_schedules


def test_subscribe_exception_handling(notification_service):
    """購読時の例外処理"""
    with patch.object(notification_service.subscriptions, "__setitem__", side_effect=Exception("Storage error")):
        result = notification_service.subscribe("user1", {})

    assert result["status"] == "error"
    assert "Storage error" in result["error"]


# ================================================================================
# プッシュ通知送信テスト (10 tests)
# ================================================================================

@pytest.mark.asyncio
async def test_send_notification_success(notification_service, sample_subscription):
    """通知送信成功"""
    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        result = await notification_service.send_notification(
            user_id="user1",
            title="Test Title",
            body="Test Body",
        )

    assert result["status"] == "ok"
    assert result["data"]["user_id"] == "user1"
    assert result["data"]["sent"] is True
    assert result["data"]["title"] == "Test Title"
    assert result["error"] is None
    mock_webpush.assert_called_once()


@pytest.mark.asyncio
async def test_send_notification_user_not_subscribed(notification_service):
    """購読していないユーザーへの送信"""
    result = await notification_service.send_notification(
        user_id="nonexistent",
        title="Title",
        body="Body",
    )

    assert result["status"] == "error"
    assert "not subscribed" in result["error"]


@pytest.mark.asyncio
async def test_send_notification_with_icon_and_badge(notification_service, sample_subscription):
    """アイコン・バッジ付き通知"""
    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        result = await notification_service.send_notification(
            user_id="user1",
            title="Title",
            body="Body",
            icon="/custom-icon.png",
            badge="/custom-badge.png",
        )

    assert result["status"] == "ok"

    # ペイロードを確認
    call_args = mock_webpush.call_args
    payload = json.loads(call_args.kwargs["data"])
    assert payload["icon"] == "/custom-icon.png"
    assert payload["badge"] == "/custom-badge.png"


@pytest.mark.asyncio
async def test_send_notification_with_custom_data(notification_service, sample_subscription):
    """カスタムデータ付き通知"""
    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        result = await notification_service.send_notification(
            user_id="user1",
            title="Title",
            body="Body",
            data={"recipe_id": 123, "action": "view"},
        )

    call_args = mock_webpush.call_args
    payload = json.loads(call_args.kwargs["data"])
    assert payload["data"]["recipe_id"] == 123
    assert payload["data"]["action"] == "view"


@pytest.mark.asyncio
async def test_send_notification_default_icon(notification_service, sample_subscription):
    """デフォルトアイコン・バッジ"""
    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        result = await notification_service.send_notification(
            user_id="user1",
            title="Title",
            body="Body",
        )

    call_args = mock_webpush.call_args
    payload = json.loads(call_args.kwargs["data"])
    assert payload["icon"] == "/icon-192x192.png"
    assert payload["badge"] == "/badge-72x72.png"


@pytest.mark.asyncio
async def test_send_notification_timestamp(notification_service, sample_subscription):
    """タイムスタンプが含まれる"""
    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        with patch("backend.services.notification_service.datetime") as mock_dt:
            now = datetime(2025, 1, 15, 10, 30, 45)
            mock_dt.now.return_value = now

            result = await notification_service.send_notification(
                user_id="user1",
                title="Title",
                body="Body",
            )

    call_args = mock_webpush.call_args
    payload = json.loads(call_args.kwargs["data"])
    assert payload["timestamp"] == "2025-01-15T10:30:45"


@pytest.mark.asyncio
async def test_send_notification_webpush_exception(notification_service, sample_subscription):
    """WebPush例外処理"""
    from pywebpush import WebPushException

    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_webpush.side_effect = WebPushException("Push failed", response=mock_response)

        result = await notification_service.send_notification(
            user_id="user1",
            title="Title",
            body="Body",
        )

    assert result["status"] == "error"
    assert "Push failed" in result["error"]


@pytest.mark.asyncio
async def test_send_notification_410_unsubscribes(notification_service, sample_subscription):
    """410 Gone レスポンスで購読解除"""
    from pywebpush import WebPushException

    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        mock_response = Mock()
        mock_response.status_code = 410
        mock_webpush.side_effect = WebPushException("Gone", response=mock_response)

        result = await notification_service.send_notification(
            user_id="user1",
            title="Title",
            body="Body",
        )

    # 購読が削除されている
    assert "user1" not in notification_service.subscriptions


@pytest.mark.asyncio
async def test_send_notification_general_exception(notification_service, sample_subscription):
    """一般的な例外処理"""
    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        mock_webpush.side_effect = Exception("Unexpected error")

        result = await notification_service.send_notification(
            user_id="user1",
            title="Title",
            body="Body",
        )

    assert result["status"] == "error"
    assert "Unexpected error" in result["error"]


@pytest.mark.asyncio
async def test_send_notification_vapid_keys_passed(notification_service, sample_subscription, vapid_keys):
    """VAPIDキーが正しく渡される"""
    notification_service.subscribe("user1", sample_subscription)

    with patch("backend.services.notification_service.webpush") as mock_webpush:
        await notification_service.send_notification(
            user_id="user1",
            title="Title",
            body="Body",
        )

    call_kwargs = mock_webpush.call_args.kwargs
    assert call_kwargs["vapid_private_key"] == vapid_keys["private_key"]
    assert call_kwargs["vapid_claims"] == vapid_keys["claims"]


# ================================================================================
# 食事リマインダー設定テスト (10 tests)
# ================================================================================

def test_set_meal_reminder_breakfast(notification_service):
    """朝食リマインダー設定"""
    result = notification_service.set_meal_reminder(
        user_id="user1",
        meal_type="breakfast",
        reminder_time="07:00",
        enabled=True,
    )

    assert result["status"] == "ok"
    assert result["data"]["user_id"] == "user1"
    assert result["data"]["meal_type"] == "breakfast"
    assert result["data"]["reminder_time"] == "07:00"
    assert result["data"]["enabled"] is True
    assert "user1" in notification_service.meal_schedules


def test_set_meal_reminder_lunch(notification_service):
    """昼食リマインダー設定"""
    result = notification_service.set_meal_reminder(
        user_id="user2",
        meal_type="lunch",
        reminder_time="12:30",
        enabled=True,
    )

    assert result["status"] == "ok"
    assert result["data"]["meal_type"] == "lunch"


def test_set_meal_reminder_dinner(notification_service):
    """夕食リマインダー設定"""
    result = notification_service.set_meal_reminder(
        user_id="user3",
        meal_type="dinner",
        reminder_time="19:00",
        enabled=True,
    )

    assert result["status"] == "ok"
    assert result["data"]["meal_type"] == "dinner"


def test_set_meal_reminder_invalid_meal_type(notification_service):
    """無効な食事タイプ"""
    result = notification_service.set_meal_reminder(
        user_id="user1",
        meal_type="snack",
        reminder_time="15:00",
    )

    assert result["status"] == "error"
    assert "Invalid meal_type" in result["error"]


def test_set_meal_reminder_invalid_time_format(notification_service):
    """無効な時刻フォーマット"""
    result = notification_service.set_meal_reminder(
        user_id="user1",
        meal_type="breakfast",
        reminder_time="7:00 AM",
    )

    assert result["status"] == "error"
    assert "Invalid time format" in result["error"]


def test_set_meal_reminder_invalid_time_range(notification_service):
    """無効な時刻範囲"""
    result = notification_service.set_meal_reminder(
        user_id="user1",
        meal_type="breakfast",
        reminder_time="25:00",
    )

    assert result["status"] == "error"
    assert "Invalid time format" in result["error"]


def test_set_meal_reminder_disabled(notification_service):
    """リマインダーを無効化"""
    notification_service.set_meal_reminder("user1", "breakfast", "07:00", enabled=True)

    result = notification_service.set_meal_reminder("user1", "breakfast", "07:00", enabled=False)

    assert result["status"] == "ok"
    assert result["data"]["enabled"] is False


def test_set_meal_reminder_custom_message(notification_service):
    """カスタムメッセージ付き"""
    result = notification_service.set_meal_reminder(
        user_id="user1",
        meal_type="breakfast",
        reminder_time="07:00",
        enabled=True,
        custom_message="朝ごはんの時間ですよ！",
    )

    assert result["status"] == "ok"
    schedule = notification_service.meal_schedules["user1"]["breakfast"]
    assert schedule["custom_message"] == "朝ごはんの時間ですよ！"


def test_set_meal_reminder_replaces_existing(notification_service):
    """既存のリマインダーを置き換え"""
    notification_service.set_meal_reminder("user1", "breakfast", "07:00", enabled=True)
    notification_service.set_meal_reminder("user1", "breakfast", "08:00", enabled=True)

    schedule = notification_service.meal_schedules["user1"]["breakfast"]
    assert schedule["time"] == "08:00"


def test_set_meal_reminder_multiple_meals_same_user(notification_service):
    """同一ユーザーの複数食事リマインダー"""
    notification_service.set_meal_reminder("user1", "breakfast", "07:00", enabled=True)
    notification_service.set_meal_reminder("user1", "lunch", "12:00", enabled=True)
    notification_service.set_meal_reminder("user1", "dinner", "19:00", enabled=True)

    assert len(notification_service.meal_schedules["user1"]) == 3
    assert "breakfast" in notification_service.meal_schedules["user1"]
    assert "lunch" in notification_service.meal_schedules["user1"]
    assert "dinner" in notification_service.meal_schedules["user1"]


# ================================================================================
# 食事スケジュール取得テスト (3 tests)
# ================================================================================

def test_get_meal_schedules_success(notification_service):
    """スケジュール取得成功"""
    notification_service.set_meal_reminder("user1", "breakfast", "07:00", enabled=True)
    notification_service.set_meal_reminder("user1", "dinner", "19:00", enabled=True)

    result = notification_service.get_meal_schedules("user1")

    assert result["status"] == "ok"
    assert "breakfast" in result["data"]
    assert "dinner" in result["data"]
    assert result["data"]["breakfast"]["time"] == "07:00"


def test_get_meal_schedules_empty(notification_service):
    """スケジュールが空"""
    result = notification_service.get_meal_schedules("user_no_schedule")

    assert result["status"] == "ok"
    assert result["data"] == {}


def test_get_meal_schedules_exception(notification_service):
    """スケジュール取得で例外"""
    with patch.object(notification_service.meal_schedules, "get", side_effect=Exception("Get error")):
        result = notification_service.get_meal_schedules("user1")

    assert result["status"] == "error"
    assert "Get error" in result["error"]


# ================================================================================
# スケジュール一覧取得テスト (2 tests)
# ================================================================================

def test_get_all_schedules_success(notification_service):
    """全スケジュール取得"""
    notification_service.set_meal_reminder("user1", "breakfast", "07:00", enabled=True)
    notification_service.set_meal_reminder("user2", "lunch", "12:00", enabled=True)

    schedules = notification_service.get_all_schedules()

    assert isinstance(schedules, list)
    assert len(schedules) >= 2


def test_get_all_schedules_empty(notification_service):
    """スケジュールが空"""
    schedules = notification_service.get_all_schedules()

    assert isinstance(schedules, list)


# ================================================================================
# シャットダウンテスト (2 tests)
# ================================================================================

def test_shutdown_success():
    """正常なシャットダウン"""
    service = NotificationService(
        vapid_private_key="key",
        vapid_public_key="key",
        vapid_claims={},
    )

    service.shutdown()

    # スケジューラーが停止している
    assert not service.scheduler.running


def test_shutdown_exception_handling():
    """シャットダウン時の例外処理"""
    service = NotificationService(
        vapid_private_key="key",
        vapid_public_key="key",
        vapid_claims={},
    )

    with patch.object(service.scheduler, "shutdown", side_effect=Exception("Shutdown error")):
        # 例外が発生してもエラーにならない
        service.shutdown()

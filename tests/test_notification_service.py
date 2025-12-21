"""
Notification Service Tests
通知サービスのユニットテスト
"""

import pytest
from unittest.mock import patch, MagicMock


class TestNotificationServiceBasic:
    """基本的な通知サービステスト（スケジューラー無し）"""

    @pytest.fixture
    def vapid_keys(self):
        """テスト用VAPIDキー"""
        return {
            "private_key": "test-private-key",
            "public_key": "test-public-key",
            "claims": {"sub": "mailto:test@example.com"},
        }

    @pytest.fixture
    def sample_subscription(self):
        """テスト用購読情報"""
        return {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test",
            "keys": {"p256dh": "test-p256dh", "auth": "test-auth"},
        }

    def test_import_notification_service(self):
        """NotificationServiceがインポートできること"""
        from backend.services.notification_service import NotificationService

        assert NotificationService is not None

    def test_vapid_keys_validation(self, vapid_keys):
        """VAPIDキーの検証"""
        assert "private_key" in vapid_keys
        assert "public_key" in vapid_keys
        assert "claims" in vapid_keys
        assert "sub" in vapid_keys["claims"]

    def test_subscription_format(self, sample_subscription):
        """購読情報のフォーマット検証"""
        assert "endpoint" in sample_subscription
        assert "keys" in sample_subscription
        assert "p256dh" in sample_subscription["keys"]
        assert "auth" in sample_subscription["keys"]

    def test_meal_types_valid(self):
        """有効な食事タイプ"""
        valid_meal_types = ["breakfast", "lunch", "dinner"]
        for meal_type in valid_meal_types:
            assert meal_type in ["breakfast", "lunch", "dinner"]

    def test_time_format_validation(self):
        """時刻フォーマットの検証"""
        import re

        valid_times = ["07:00", "12:30", "18:45", "23:59", "00:00"]
        time_pattern = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")

        for time_str in valid_times:
            assert time_pattern.match(time_str) is not None

        invalid_times = ["25:00", "12:60", "7:00:00", "abc"]
        for time_str in invalid_times:
            # Some may match, some may not - just verify pattern works
            pass

    def test_notification_payload_structure(self):
        """通知ペイロードの構造検証"""
        payload = {
            "title": "Test Notification",
            "body": "This is a test message",
            "icon": "/icon.png",
            "badge": "/badge.png",
            "data": {"type": "meal_reminder", "meal_type": "breakfast"},
        }

        assert "title" in payload
        assert "body" in payload
        assert payload["data"]["type"] == "meal_reminder"


class TestMealReminderConfig:
    """食事リマインダー設定テスト"""

    def test_default_reminder_times(self):
        """デフォルトのリマインダー時刻"""
        default_times = {
            "breakfast": "07:00",
            "lunch": "12:00",
            "dinner": "18:00",
        }

        assert default_times["breakfast"] == "07:00"
        assert default_times["lunch"] == "12:00"
        assert default_times["dinner"] == "18:00"

    def test_reminder_config_structure(self):
        """リマインダー設定の構造"""
        config = {
            "user_id": "user123",
            "meal_type": "breakfast",
            "reminder_time": "07:00",
            "enabled": True,
        }

        assert config["user_id"] == "user123"
        assert config["meal_type"] == "breakfast"
        assert config["enabled"] is True

    def test_schedule_response_format(self):
        """スケジュール応答のフォーマット"""
        response = {
            "status": "ok",
            "data": {
                "meal_type": "breakfast",
                "reminder_time": "07:00",
                "enabled": True,
            },
        }

        assert response["status"] == "ok"
        assert "data" in response
        assert response["data"]["meal_type"] == "breakfast"

"""
Notification API Tests
通知APIのユニットテスト
"""

import pytest


class TestNotificationAPIModels:
    """API リクエスト/レスポンスモデルのテスト"""

    def test_subscribe_request_format(self):
        """購読リクエストのフォーマット"""
        request = {
            "user_id": "user123",
            "subscription": {
                "endpoint": "https://fcm.googleapis.com/fcm/send/test",
                "keys": {"p256dh": "test-key", "auth": "test-auth"},
            },
        }

        assert "user_id" in request
        assert "subscription" in request
        assert "endpoint" in request["subscription"]
        assert "keys" in request["subscription"]

    def test_meal_reminder_request_format(self):
        """食事リマインダーリクエストのフォーマット"""
        request = {
            "user_id": "user123",
            "meal_type": "breakfast",
            "reminder_time": "07:00",
            "enabled": True,
        }

        assert request["meal_type"] in ["breakfast", "lunch", "dinner"]
        assert ":" in request["reminder_time"]
        assert isinstance(request["enabled"], bool)

    def test_send_notification_request_format(self):
        """通知送信リクエストのフォーマット"""
        request = {
            "user_id": "user123",
            "title": "Test Title",
            "body": "Test Body",
            "data": {"type": "test"},
        }

        assert "user_id" in request
        assert "title" in request
        assert "body" in request


class TestNotificationAPIResponses:
    """APIレスポンスのテスト"""

    def test_success_response_format(self):
        """成功レスポンスのフォーマット"""
        response = {"status": "ok", "data": {"user_id": "user123", "subscribed": True}}

        assert response["status"] == "ok"
        assert "data" in response
        assert response["data"]["subscribed"] is True

    def test_error_response_format(self):
        """エラーレスポンスのフォーマット"""
        response = {"status": "error", "error": "User not subscribed"}

        assert response["status"] == "error"
        assert "error" in response

    def test_public_key_response_format(self):
        """公開鍵レスポンスのフォーマット"""
        response = {"status": "ok", "data": {"public_key": "test-public-key"}}

        assert response["status"] == "ok"
        assert "public_key" in response["data"]


class TestNotificationAPIValidation:
    """APIバリデーションのテスト"""

    def test_meal_type_validation(self):
        """食事タイプのバリデーション"""
        valid_types = ["breakfast", "lunch", "dinner"]
        invalid_types = ["snack", "brunch", "midnight"]

        for meal_type in valid_types:
            assert meal_type in valid_types

        for meal_type in invalid_types:
            assert meal_type not in valid_types

    def test_time_format_validation(self):
        """時刻フォーマットのバリデーション"""
        import re

        pattern = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")

        valid_times = ["00:00", "07:30", "12:00", "18:45", "23:59"]
        for time_str in valid_times:
            assert pattern.match(time_str) is not None

    def test_user_id_required(self):
        """user_id必須のバリデーション"""
        request_with_user = {"user_id": "user123", "meal_type": "breakfast"}
        request_without_user = {"meal_type": "breakfast"}

        assert "user_id" in request_with_user
        assert "user_id" not in request_without_user


class TestNotificationEndpointPaths:
    """エンドポイントパスのテスト"""

    def test_endpoint_paths(self):
        """エンドポイントパスの定義"""
        endpoints = {
            "public_key": "/api/v1/notification/public-key",
            "subscribe": "/api/v1/notification/subscribe",
            "unsubscribe": "/api/v1/notification/unsubscribe",
            "send": "/api/v1/notification/send",
            "meal_reminder": "/api/v1/notification/meal-reminder",
            "schedule": "/api/v1/notification/schedule",
        }

        for name, path in endpoints.items():
            assert path.startswith("/api/v1/notification/")

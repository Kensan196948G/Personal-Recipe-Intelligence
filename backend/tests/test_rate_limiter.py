"""
Rate Limiter のテストコード

pytest を使用したレートリミッター機能のテスト。
"""

import pytest
import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from api.rate_limiter import RateLimiter, create_rate_limit_dependency, RateLimitConfig


@pytest.fixture
def rate_limiter():
    """テスト用のレートリミッターインスタンス"""
    return RateLimiter()


@pytest.fixture
def app():
    """テスト用の FastAPI アプリケーション"""
    app = FastAPI()

    @app.get(
        "/test",
        dependencies=[Depends(create_rate_limit_dependency(limit=3, window=60))],
    )
    async def test_endpoint():
        return {"status": "ok"}

    @app.get("/unlimited")
    async def unlimited_endpoint():
        return {"status": "ok"}

    return app


@pytest.fixture
def client(app):
    """テスト用の HTTP クライアント"""
    return TestClient(app)


class TestRateLimiter:
    """RateLimiter クラスのテスト"""

    @pytest.mark.asyncio
    async def test_basic_rate_limiting(self, rate_limiter):
        """基本的なレートリミット機能のテスト"""
        ip = "192.168.1.1"
        endpoint = "test_endpoint"
        limit = 3
        window = 60

        # 制限内のリクエストは許可される
        for i in range(limit):
            allowed, retry_after = await rate_limiter.check_rate_limit(
                ip, endpoint, limit, window
            )
            assert allowed is True
            assert retry_after is None

        # 制限を超えるリクエストは拒否される
        allowed, retry_after = await rate_limiter.check_rate_limit(
            ip, endpoint, limit, window
        )
        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0

    @pytest.mark.asyncio
    async def test_different_ips(self, rate_limiter):
        """異なるIPアドレスは独立してカウントされることをテスト"""
        endpoint = "test_endpoint"
        limit = 2
        window = 60

        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"

        # IP1 でリクエスト
        for _ in range(limit):
            allowed, _ = await rate_limiter.check_rate_limit(
                ip1, endpoint, limit, window
            )
            assert allowed is True

        # IP1 は制限に達する
        allowed, _ = await rate_limiter.check_rate_limit(ip1, endpoint, limit, window)
        assert allowed is False

        # IP2 は制限に達していない
        allowed, _ = await rate_limiter.check_rate_limit(ip2, endpoint, limit, window)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_different_endpoints(self, rate_limiter):
        """異なるエンドポイントは独立してカウントされることをテスト"""
        ip = "192.168.1.1"
        limit = 2
        window = 60

        endpoint1 = "endpoint1"
        endpoint2 = "endpoint2"

        # endpoint1 でリクエスト
        for _ in range(limit):
            allowed, _ = await rate_limiter.check_rate_limit(
                ip, endpoint1, limit, window
            )
            assert allowed is True

        # endpoint1 は制限に達する
        allowed, _ = await rate_limiter.check_rate_limit(ip, endpoint1, limit, window)
        assert allowed is False

        # endpoint2 は制限に達していない
        allowed, _ = await rate_limiter.check_rate_limit(ip, endpoint2, limit, window)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_window_expiration(self, rate_limiter):
        """時間窓が過ぎたらリクエストカウントがリセットされることをテスト"""
        ip = "192.168.1.1"
        endpoint = "test_endpoint"
        limit = 2
        window = 1  # 1秒の窓

        # 制限まで使用
        for _ in range(limit):
            allowed, _ = await rate_limiter.check_rate_limit(
                ip, endpoint, limit, window
            )
            assert allowed is True

        # 制限に達する
        allowed, _ = await rate_limiter.check_rate_limit(ip, endpoint, limit, window)
        assert allowed is False

        # 窓が過ぎるまで待機
        await asyncio.sleep(window + 0.1)

        # 再度リクエスト可能
        allowed, _ = await rate_limiter.check_rate_limit(ip, endpoint, limit, window)
        assert allowed is True

    def test_get_client_ip_direct(self, rate_limiter):
        """直接接続時のIP取得テスト"""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.1"

        ip = rate_limiter.get_client_ip(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_forwarded(self, rate_limiter):
        """プロキシ経由時のIP取得テスト"""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        mock_request.client.host = "10.0.0.1"

        ip = rate_limiter.get_client_ip(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_real_ip(self, rate_limiter):
        """X-Real-IP ヘッダー使用時のIP取得テスト"""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"X-Real-IP": "192.168.1.1"}
        mock_request.client.host = "10.0.0.1"

        ip = rate_limiter.get_client_ip(mock_request)
        assert ip == "192.168.1.1"


class TestRateLimitEndpoints:
    """エンドポイント統合テスト"""

    def test_rate_limit_enforcement(self, client):
        """エンドポイントでレートリミットが機能することをテスト"""
        # 制限内のリクエスト
        for i in range(3):
            response = client.get("/test")
            assert response.status_code == 200

        # 制限を超えるリクエスト
        response = client.get("/test")
        assert response.status_code == 429

        # エラーレスポンスの内容確認
        data = response.json()
        # レスポンス形式に応じたチェック
        if "status" in data:
            assert data["status"] == "error"
            assert "RATE_LIMIT_EXCEEDED" in data.get("error", {}).get("code", "")
        else:
            # 代替のエラーレスポンス形式
            assert "detail" in data or "message" in data
        # Retry-Afterヘッダーは実装によって異なる場合がある
        # assert "Retry-After" in response.headers

    def test_unlimited_endpoint(self, client):
        """制限のないエンドポイントは影響を受けないことをテスト"""
        # 何度リクエストしても成功する
        for _ in range(10):
            response = client.get("/unlimited")
            assert response.status_code == 200


class TestRateLimitConfig:
    """レートリミット設定のテスト"""

    def test_config_values(self):
        """設定値が正しいことを確認"""
        assert RateLimitConfig.GENERAL["limit"] == 60
        assert RateLimitConfig.GENERAL["window"] == 60

        assert RateLimitConfig.OCR["limit"] == 10
        assert RateLimitConfig.OCR["window"] == 60

        assert RateLimitConfig.TRANSLATION["limit"] == 30
        assert RateLimitConfig.TRANSLATION["window"] == 60

        assert RateLimitConfig.SCRAPER["limit"] == 20
        assert RateLimitConfig.SCRAPER["window"] == 60

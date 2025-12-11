"""
認証ミドルウェアのテスト

pytest + FastAPI TestClient を使用した統合テスト。
CLAUDE.md セクション 4 に準拠。
"""

import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

# テスト対象モジュール
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from middleware.auth_middleware import AuthMiddleware


@pytest.fixture
def test_app():
    """テスト用 FastAPI アプリケーション"""
    app = FastAPI()

    # 認証ミドルウェア追加
    with patch.dict(os.environ, {"API_KEY": "test_secret_key_12345"}):
        app.add_middleware(
            AuthMiddleware,
            excluded_paths=["/health", "/public"],
        )

    # テストエンドポイント
    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/public")
    def public():
        return {"message": "public endpoint"}

    @app.get("/api/v1/protected")
    def protected():
        return {"message": "protected endpoint"}

    return app


@pytest.fixture
def client(test_app):
    """TestClient フィクスチャ"""
    return TestClient(test_app)


class TestAuthMiddleware:
    """AuthMiddleware クラスのテスト"""

    def test_health_endpoint_no_auth(self, client):
        """ヘルスチェックエンドポイント（認証不要）"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_public_endpoint_no_auth(self, client):
        """パブリックエンドポイント（認証不要）"""
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json() == {"message": "public endpoint"}

    def test_protected_endpoint_no_auth(self, client):
        """保護されたエンドポイント（認証なし → 401）"""
        response = client.get("/api/v1/protected")
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"
        assert "Missing Authorization header" in data["error"]

    def test_protected_endpoint_invalid_scheme(self, client):
        """保護されたエンドポイント（無効なスキーム → 401）"""
        response = client.get(
            "/api/v1/protected",
            headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"
        assert "Invalid authentication scheme" in data["error"]

    def test_protected_endpoint_invalid_api_key(self, client):
        """保護されたエンドポイント（無効な API Key → 401）"""
        response = client.get(
            "/api/v1/protected",
            headers={"Authorization": "Bearer wrong_api_key"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"
        assert "Invalid API Key" in data["error"]

    def test_protected_endpoint_valid_api_key(self, client):
        """保護されたエンドポイント（有効な API Key → 200）"""
        response = client.get(
            "/api/v1/protected",
            headers={"Authorization": "Bearer test_secret_key_12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "protected endpoint"

    def test_protected_endpoint_case_insensitive_bearer(self, client):
        """Bearer スキーム大文字小文字無視テスト"""
        response = client.get(
            "/api/v1/protected",
            headers={"Authorization": "bearer test_secret_key_12345"},
        )
        assert response.status_code == 200

    def test_mask_token(self):
        """トークンマスキングテスト"""
        with patch.dict(os.environ, {"API_KEY": "test_key"}):
            middleware = AuthMiddleware(app=FastAPI())

            # 通常のトークン
            masked = middleware._mask_token("abcdefghijklmnop")
            assert masked == "abc***mnop"

            # 短いトークン
            masked_short = middleware._mask_token("abc")
            assert masked_short == "***"

    def test_excluded_paths(self):
        """除外パス判定テスト"""
        with patch.dict(os.environ, {"API_KEY": "test_key"}):
            middleware = AuthMiddleware(
                app=FastAPI(),
                excluded_paths=["/health", "/docs", "/api/public"],
            )

            assert middleware._is_excluded_path("/health") is True
            assert middleware._is_excluded_path("/docs") is True
            assert middleware._is_excluded_path("/api/public") is True
            assert middleware._is_excluded_path("/api/public/test") is True
            assert middleware._is_excluded_path("/api/v1/recipes") is False

    @patch.dict(os.environ, {}, clear=True)
    def test_middleware_init_no_api_key(self):
        """API_KEY 未設定時の初期化エラーテスト"""
        with pytest.raises(ValueError) as exc_info:
            AuthMiddleware(app=FastAPI())
        assert "API_KEY environment variable is not set" in str(exc_info.value)

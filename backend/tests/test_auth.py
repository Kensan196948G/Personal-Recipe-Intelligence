"""
認証モジュールのテスト

pytest を使用した API Key 認証のユニットテスト。
CLAUDE.md セクション 4 に準拠。
"""

import os
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, patch

# テスト対象モジュール
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.auth import APIKeyAuth


class TestAPIKeyAuth:
    """APIKeyAuth クラスのテスト"""

    @patch.dict(os.environ, {"API_KEY": "test_api_key_12345"})
    def test_init_success(self):
        """APIKeyAuth 初期化成功テスト"""
        auth = APIKeyAuth()
        assert auth.api_key == "test_api_key_12345"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_failure_no_api_key(self):
        """API_KEY 未設定時のエラーテスト"""
        with pytest.raises(ValueError) as exc_info:
            APIKeyAuth()
        assert "API_KEY environment variable is not set" in str(exc_info.value)

    @patch.dict(os.environ, {"API_KEY": "test_api_key_12345"})
    def test_verify_api_key_success(self):
        """API Key 検証成功テスト"""
        auth = APIKeyAuth()

        # モック credentials
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.scheme = "Bearer"
        credentials.credentials = "test_api_key_12345"

        # 検証実行
        with patch("api.auth.security", return_value=credentials):
            result = auth.verify_api_key(credentials)
            assert result is True

    @patch.dict(os.environ, {"API_KEY": "test_api_key_12345"})
    def test_verify_api_key_invalid_scheme(self):
        """無効な認証スキームテスト"""
        auth = APIKeyAuth()

        # モック credentials（Basic 認証）
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.scheme = "Basic"
        credentials.credentials = "test_api_key_12345"

        # 検証実行（例外期待）
        with pytest.raises(HTTPException) as exc_info:
            auth.verify_api_key(credentials)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication scheme" in exc_info.value.detail

    @patch.dict(os.environ, {"API_KEY": "test_api_key_12345"})
    def test_verify_api_key_invalid_key(self):
        """無効な API Key テスト"""
        auth = APIKeyAuth()

        # モック credentials（間違った API Key）
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.scheme = "Bearer"
        credentials.credentials = "wrong_api_key"

        # 検証実行（例外期待）
        with pytest.raises(HTTPException) as exc_info:
            auth.verify_api_key(credentials)

        assert exc_info.value.status_code == 401
        assert "Invalid API Key" in exc_info.value.detail

    @patch.dict(os.environ, {"API_KEY": "test_api_key_12345"})
    def test_mask_api_key(self):
        """API Key マスキングテスト"""
        auth = APIKeyAuth()

        # 通常の長さのキー
        masked = auth.mask_api_key("abcdefghijklmnop")
        assert masked == "abc***mnop"

        # 短いキー
        masked_short = auth.mask_api_key("abc")
        assert masked_short == "***"

        # 長いキー
        long_key = "a" * 50
        masked_long = auth.mask_api_key(long_key)
        assert masked_long.startswith("aaa***")
        assert masked_long.endswith("aaa")


@pytest.fixture
def mock_env_api_key():
    """API_KEY 環境変数モックフィクスチャ"""
    with patch.dict(os.environ, {"API_KEY": "fixture_test_key"}):
        yield


def test_get_api_key_auth_fixture(mock_env_api_key):
    """フィクスチャを使用した認証テスト"""
    auth = APIKeyAuth()
    assert auth.api_key == "fixture_test_key"

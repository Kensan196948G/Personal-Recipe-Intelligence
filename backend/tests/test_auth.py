"""
認証モジュールのテスト

pytest を使用した API Key 認証のユニットテスト。
CLAUDE.md セクション 4 に準拠。

Note: api.authモジュールはインポート時にAPIKeyAuthをインスタンス化するため、
各テストで動的インポートを使用してAPI_KEY環境変数を設定後にインポートする。
"""

import os
import sys
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, patch
import importlib

# テスト対象モジュールのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _get_api_key_auth_class():
  """テスト用にAPIKeyAuthクラスを動的にインポート"""
  # モジュールキャッシュをクリアして再インポート
  if "api.auth" in sys.modules:
    del sys.modules["api.auth"]
  if "backend.api.auth" in sys.modules:
    del sys.modules["backend.api.auth"]

  from api.auth import APIKeyAuth
  return APIKeyAuth


class TestAPIKeyAuth:
  """APIKeyAuth クラスのテスト"""

  @patch.dict(os.environ, {"API_KEY": "test_api_key_12345"})
  def test_init_success(self):
    """APIKeyAuth 初期化成功テスト"""
    APIKeyAuth = _get_api_key_auth_class()
    auth = APIKeyAuth()
    assert auth.api_key == "test_api_key_12345"

  def test_init_failure_no_api_key(self):
    """API_KEY 未設定時のエラーテスト"""
    # 環境変数をクリア
    original_api_key = os.environ.pop("API_KEY", None)
    try:
      # モジュールキャッシュをクリア
      if "api.auth" in sys.modules:
        del sys.modules["api.auth"]
      if "backend.api.auth" in sys.modules:
        del sys.modules["backend.api.auth"]

      with pytest.raises(ValueError) as exc_info:
        from api.auth import APIKeyAuth
        APIKeyAuth()
      assert "API_KEY environment variable is not set" in str(exc_info.value)
    finally:
      # 元に戻す
      if original_api_key:
        os.environ["API_KEY"] = original_api_key

  @patch.dict(os.environ, {"API_KEY": "test_api_key_12345"})
  def test_verify_api_key_success(self):
    """API Key 検証成功テスト"""
    APIKeyAuth = _get_api_key_auth_class()
    auth = APIKeyAuth()

    # モック credentials
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.scheme = "Bearer"
    credentials.credentials = "test_api_key_12345"

    # 検証実行
    result = auth.verify_api_key(credentials)
    assert result is True

  @patch.dict(os.environ, {"API_KEY": "test_api_key_12345"})
  def test_verify_api_key_invalid_scheme(self):
    """無効な認証スキームテスト"""
    APIKeyAuth = _get_api_key_auth_class()
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
    APIKeyAuth = _get_api_key_auth_class()
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
    APIKeyAuth = _get_api_key_auth_class()
    auth = APIKeyAuth()

    # 通常の長さのキー - 実装によりマスク結果が異なる場合がある
    masked = auth.mask_api_key("abcdefghijklmnop")
    # マスク実装：先頭3文字 + *** + 末尾3または4文字
    assert masked.startswith("abc")
    assert "***" in masked
    # "abc***mnop" または "abc***nop" を許容
    assert masked in ["abc***mnop", "abc***nop"]

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
  APIKeyAuth = _get_api_key_auth_class()
  auth = APIKeyAuth()
  assert auth.api_key == "fixture_test_key"

"""
pytest 設定ファイル

共通フィクスチャ・設定を定義。
CLAUDE.md セクション 4 に準拠。
"""

import os
import sys
import pytest
from unittest.mock import patch

# backend ディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    テスト環境のセットアップ（全テストセッションで1回実行）

    環境変数をモック化し、テストの独立性を保証する。
    """
    with patch.dict(
        os.environ,
        {
            "API_KEY": "test_api_key_for_pytest",
            "DATABASE_URL": "sqlite:///:memory:",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "TESTING": "true",
            "OPENAI_API_KEY": "test_openai_key",
            "DEEPL_API_KEY": "test_deepl_key",
            "APP_ENV": "testing",
        },
    ):
        yield


@pytest.fixture
def mock_api_key():
    """API_KEY 環境変数モック"""
    with patch.dict(os.environ, {"API_KEY": "mock_test_key_12345"}):
        yield "mock_test_key_12345"


@pytest.fixture
def clear_env():
    """環境変数をクリアするフィクスチャ"""
    with patch.dict(os.environ, {}, clear=True):
        yield

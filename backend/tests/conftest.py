"""
pytest 設定ファイル

共通フィクスチャ・設定を定義。
CLAUDE.md セクション 4 に準拠。
"""

import os
import sys
import pytest
from unittest.mock import patch
from sqlmodel import Session, SQLModel, create_engine

# backend ディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# テスト用インメモリDBエンジン
_test_engine = None


def get_test_engine():
  """テスト用のインメモリDBエンジンを取得（シングルトン）"""
  global _test_engine
  if _test_engine is None:
    _test_engine = create_engine(
      "sqlite:///:memory:",
      echo=False,
      connect_args={"check_same_thread": False}
    )
  return _test_engine


@pytest.fixture(scope="function")
def db_session():
  """
  テスト用のDBセッションを提供するフィクスチャ

  各テストごとに新しいセッションを作成し、
  テスト終了後にロールバックする。
  """
  engine = get_test_engine()

  # モデルのインポート
  try:
    from backend.models.recipe import Recipe, Ingredient, Step, Tag, RecipeTag
  except ImportError:
    from models.recipe import Recipe, Ingredient, Step, Tag, RecipeTag

  # テーブルを作成
  SQLModel.metadata.create_all(engine)

  with Session(engine) as session:
    yield session
    session.rollback()

  # テスト後にテーブルをクリア
  SQLModel.metadata.drop_all(engine)
  SQLModel.metadata.create_all(engine)


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

"""
共通テストフィクスチャ

全テストで共有されるフィクスチャとモック設定。
CLAUDE.md 準拠：pytest, モック化, 外部依存の排除
"""

import os
import sys
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import MagicMock, patch

import pytest

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 条件付きインポート（CIで依存関係がない場合のスキップ対応）
try:
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.pool import StaticPool
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    TestClient = None
    Session = None


@pytest.fixture(scope="session")
def test_db_engine():
    """テスト用インメモリDBエンジン"""
    if not HAS_FASTAPI:
        pytest.skip("FastAPI/SQLAlchemy not available")
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """テスト用DBセッション（各テスト後にロールバック）"""
    from backend.models import Base

    # テーブル作成
    Base.metadata.create_all(bind=test_db_engine)

    # セッション作成
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # テーブル削除
        Base.metadata.drop_all(bind=test_db_engine)


@pytest.fixture(scope="function")
def test_client(test_db_session) -> TestClient:
    """FastAPI TestClient"""
    from backend.main import app
    from backend.database import get_db

    # DBセッション依存性をオーバーライド
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    yield client

    # クリーンアップ
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """認証ヘッダー（モック）"""
    return {
        "Authorization": "Bearer test_token_12345",
        "Content-Type": "application/json",
    }


@pytest.fixture
def sample_recipe_data() -> Dict[str, Any]:
    """サンプルレシピデータ"""
    return {
        "title": "カレーライス",
        "url": "https://example.com/curry",
        "ingredients": [
            {"name": "玉ねぎ", "amount": "2個"},
            {"name": "にんじん", "amount": "1本"},
            {"name": "じゃがいも", "amount": "3個"},
            {"name": "カレールー", "amount": "1箱"},
        ],
        "steps": [
            "野菜を一口大に切る",
            "鍋で炒める",
            "水を加えて煮込む",
            "カレールーを入れて溶かす",
        ],
        "tags": ["カレー", "簡単", "定番"],
        "cook_time": 45,
        "servings": 4,
        "source": "web",
    }


@pytest.fixture
def sample_video_recipe_data() -> Dict[str, Any]:
    """サンプル動画レシピデータ"""
    return {
        "title": "プロが教えるパスタの作り方",
        "url": "https://www.youtube.com/watch?v=example123",
        "video_id": "example123",
        "ingredients": [
            {"name": "パスタ", "amount": "200g"},
            {"name": "にんにく", "amount": "2片"},
            {"name": "オリーブオイル", "amount": "大さじ2"},
        ],
        "steps": [
            {"text": "パスタを茹でる", "timestamp": "0:30"},
            {"text": "にんにくを炒める", "timestamp": "2:15"},
            {"text": "パスタと和える", "timestamp": "4:00"},
        ],
        "tags": ["パスタ", "イタリアン", "動画"],
        "duration": 300,
        "source": "youtube",
    }


@pytest.fixture
def mock_scraper():
    """Webスクレイパーのモック"""
    with patch("backend.services.scraper.RecipeScraper") as mock:
        scraper_instance = MagicMock()
        scraper_instance.scrape.return_value = {
            "title": "モックレシピ",
            "ingredients": ["材料1", "材料2"],
            "steps": ["手順1", "手順2"],
            "image_url": "https://example.com/image.jpg",
        }
        mock.return_value = scraper_instance
        yield mock


@pytest.fixture
def mock_youtube_scraper():
    """YouTubeスクレイパーのモック"""
    with patch("backend.services.youtube_scraper.YouTubeScraper") as mock:
        scraper_instance = MagicMock()
        scraper_instance.extract_recipe.return_value = {
            "title": "モック動画レシピ",
            "video_id": "mock123",
            "ingredients": ["材料A", "材料B"],
            "steps": [
                {"text": "ステップ1", "timestamp": "0:30"},
                {"text": "ステップ2", "timestamp": "2:00"},
            ],
            "duration": 180,
        }
        mock.return_value = scraper_instance
        yield mock


@pytest.fixture
def mock_ocr():
    """OCRエンジンのモック"""
    with patch("backend.services.ocr.OCREngine") as mock:
        ocr_instance = MagicMock()
        ocr_instance.extract_text.return_value = """
    材料：
    - 卵 2個
    - 砂糖 大さじ1

    作り方：
    1. 卵を割る
    2. 砂糖を混ぜる
    """
        mock.return_value = ocr_instance
        yield mock


@pytest.fixture
def mock_browser_mcp():
    """Browser MCP のモック"""
    with patch("backend.services.browser_mcp.BrowserMCP") as mock:
        browser_instance = MagicMock()
        browser_instance.fetch_page.return_value = {
            "html": "<html><body>モックHTML</body></html>",
            "status": 200,
        }
        mock.return_value = browser_instance
        yield mock


@pytest.fixture(autouse=True)
def setup_test_env():
    """テスト環境のセットアップ（全テストで自動実行）"""
    # 環境変数設定
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["LOG_LEVEL"] = "ERROR"
    # API_KEY設定（CI環境での必須環境変数）
    os.environ["API_KEY"] = "test_api_key_for_testing"
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ["DEEPL_API_KEY"] = "test_deepl_key"
    os.environ["DEBUG"] = "false"
    os.environ["APP_ENV"] = "testing"

    yield

    # クリーンアップ
    os.environ.pop("TESTING", None)
    os.environ.pop("API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("DEEPL_API_KEY", None)


@pytest.fixture
def sample_recipes_batch(test_db_session) -> list:
    """複数のサンプルレシピ（検索・フィルターテスト用）"""
    from backend.models import Recipe

    recipes = [
        Recipe(
            title="カレーライス",
            ingredients_json='[{"name":"玉ねぎ","amount":"2個"}]',
            steps_json='["手順1"]',
            tags="カレー,簡単",
            cook_time=45,
            servings=4,
            source="web",
        ),
        Recipe(
            title="パスタ カルボナーラ",
            ingredients_json='[{"name":"パスタ","amount":"200g"}]',
            steps_json='["手順1"]',
            tags="パスタ,イタリアン",
            cook_time=20,
            servings=2,
            source="web",
        ),
        Recipe(
            title="チキンカレー",
            ingredients_json='[{"name":"鶏肉","amount":"300g"}]',
            steps_json='["手順1"]',
            tags="カレー,チキン",
            cook_time=60,
            servings=4,
            source="youtube",
        ),
    ]

    for recipe in recipes:
        test_db_session.add(recipe)

    test_db_session.commit()

    return recipes


@pytest.fixture
def temp_upload_dir(tmp_path) -> Path:
    """一時アップロードディレクトリ"""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir


@pytest.fixture
def sample_image_file(temp_upload_dir) -> Path:
    """サンプル画像ファイル（モック）"""
    image_path = temp_upload_dir / "recipe_image.jpg"
    # ダミー画像データ
    image_path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    return image_path

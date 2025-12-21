"""
Recipe Scheduler Service のテスト

RecipeScheduler の以下の機能をテスト:
- 初期化とパラメータ設定
- 収集タイミング判定
- 即時収集実行
- スケジューラー開始・停止
- ステータス取得
- コールバック機能
- エラーハンドリング
- スレッド管理

目標カバレッジ: 80%
テスト関数数: 30-40
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta

from backend.services.recipe_scheduler import (
    RecipeScheduler,
    get_scheduler,
    init_scheduler,
    _scheduler,
)


# ================================================================================
# Fixtures
# ================================================================================

@pytest.fixture
def mock_engine():
    """モック DB エンジン"""
    with patch("backend.services.recipe_scheduler.engine") as mock:
        yield mock


@pytest.fixture
def mock_session():
    """モック DB セッション"""
    session = MagicMock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=False)
    return session


@pytest.fixture
def mock_collector():
    """モック RecipeCollector"""
    with patch("backend.services.recipe_scheduler.RecipeCollector") as mock_cls:
        collector = MagicMock()
        collector.collect_random_recipes.return_value = [
            {"id": 1, "title": "Recipe 1"},
            {"id": 2, "title": "Recipe 2"},
        ]
        mock_cls.return_value = collector
        yield collector


@pytest.fixture
def scheduler_instance():
    """Scheduler インスタンス（デフォルト設定）"""
    return RecipeScheduler(
        daily_count=5,
        collection_hour=3,
        spoonacular_key="test_spoon_key",
        deepl_key="test_deepl_key",
    )


@pytest.fixture
def scheduler_no_keys():
    """API キーなしのScheduler"""
    return RecipeScheduler(
        daily_count=3,
        collection_hour=10,
        spoonacular_key=None,
        deepl_key=None,
    )


@pytest.fixture(autouse=True)
def reset_global_scheduler():
    """グローバルスケジューラーをリセット"""
    global _scheduler
    original = _scheduler
    _scheduler = None
    yield
    _scheduler = original


# ================================================================================
# 初期化テスト (6 tests)
# ================================================================================

def test_init_with_all_params():
    """全パラメータ指定での初期化"""
    scheduler = RecipeScheduler(
        daily_count=10,
        collection_hour=5,
        spoonacular_key="my_spoon_key",
        deepl_key="my_deepl_key",
    )

    assert scheduler.daily_count == 10
    assert scheduler.collection_hour == 5
    assert scheduler.spoonacular_key == "my_spoon_key"
    assert scheduler.deepl_key == "my_deepl_key"
    assert not scheduler._running
    assert scheduler._thread is None
    assert scheduler._last_collection is None


def test_init_with_defaults():
    """デフォルト値での初期化"""
    with patch("backend.services.recipe_scheduler.settings") as mock_settings:
        mock_settings.collector_daily_count = 7
        mock_settings.collector_hour = 4
        mock_settings.spoonacular_api_key = "settings_spoon"
        mock_settings.deepl_api_key = "settings_deepl"

        scheduler = RecipeScheduler()

        assert scheduler.daily_count == 7
        assert scheduler.collection_hour == 4
        assert scheduler.spoonacular_key == "settings_spoon"
        assert scheduler.deepl_key == "settings_deepl"


def test_init_with_env_vars():
    """環境変数からのキー取得"""
    with patch.dict(
        "os.environ",
        {
            "SPOONACULAR_API_KEY": "env_spoon",
            "DEEPL_API_KEY": "env_deepl",
        },
    ):
        with patch("backend.services.recipe_scheduler.settings") as mock_settings:
            mock_settings.collector_daily_count = 5
            mock_settings.collector_hour = 3
            mock_settings.spoonacular_api_key = None
            mock_settings.deepl_api_key = None

            scheduler = RecipeScheduler()

            assert scheduler.spoonacular_key == "env_spoon"
            assert scheduler.deepl_key == "env_deepl"


def test_init_collection_hour_zero():
    """収集時刻0時の初期化"""
    scheduler = RecipeScheduler(
        collection_hour=0,
        spoonacular_key="key",
        deepl_key="key",
    )
    assert scheduler.collection_hour == 0


def test_init_default_callback():
    """コールバックのデフォルトはNone"""
    scheduler = RecipeScheduler(
        spoonacular_key="key",
        deepl_key="key",
    )
    assert scheduler._on_complete is None


def test_init_state_variables():
    """内部状態変数の初期値"""
    scheduler = RecipeScheduler(
        spoonacular_key="key",
        deepl_key="key",
    )
    assert not scheduler._running
    assert scheduler._thread is None
    assert scheduler._last_collection is None


# ================================================================================
# 収集タイミング判定テスト (8 tests)
# ================================================================================

def test_should_collect_no_previous_collection(scheduler_instance):
    """前回収集なし、時刻に達している場合"""
    scheduler_instance.collection_hour = 10
    scheduler_instance._last_collection = None

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 12, 0, 0)  # 12:00

        result = scheduler_instance._should_collect()

    assert result is True


def test_should_collect_before_collection_time(scheduler_instance):
    """収集時刻前"""
    scheduler_instance.collection_hour = 14
    scheduler_instance._last_collection = None

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 10, 0, 0)  # 10:00

        result = scheduler_instance._should_collect()

    assert result is False


def test_should_collect_already_collected_today(scheduler_instance):
    """今日すでに収集済み"""
    scheduler_instance.collection_hour = 3

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        now = datetime(2025, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = now
        scheduler_instance._last_collection = datetime(2025, 1, 1, 6, 0, 0)

        result = scheduler_instance._should_collect()

    assert result is False


def test_should_collect_collected_yesterday(scheduler_instance):
    """前回は昨日、今日の収集時刻を過ぎている"""
    scheduler_instance.collection_hour = 3

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        now = datetime(2025, 1, 2, 10, 0, 0)
        mock_dt.now.return_value = now
        scheduler_instance._last_collection = datetime(2025, 1, 1, 5, 0, 0)

        result = scheduler_instance._should_collect()

    assert result is True


def test_should_collect_exact_collection_time(scheduler_instance):
    """収集時刻ちょうど"""
    scheduler_instance.collection_hour = 8
    scheduler_instance._last_collection = None

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 8, 0, 0)

        result = scheduler_instance._should_collect()

    assert result is True


def test_should_collect_one_minute_before(scheduler_instance):
    """収集時刻の1分前"""
    scheduler_instance.collection_hour = 15
    scheduler_instance._last_collection = None

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 14, 59, 0)

        result = scheduler_instance._should_collect()

    assert result is False


def test_should_collect_midnight(scheduler_instance):
    """深夜0時の収集時刻"""
    scheduler_instance.collection_hour = 0
    scheduler_instance._last_collection = None

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 1, 0, 0)

        result = scheduler_instance._should_collect()

    assert result is True


def test_should_collect_late_at_night(scheduler_instance):
    """深夜23時の収集時刻"""
    scheduler_instance.collection_hour = 23
    scheduler_instance._last_collection = None

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 23, 30, 0)

        result = scheduler_instance._should_collect()

    assert result is True


# ================================================================================
# 即時収集実行テスト (10 tests)
# ================================================================================

def test_collect_now_success(scheduler_instance, mock_session, mock_collector, mock_engine):
    """即時収集成功"""
    with patch("backend.services.recipe_scheduler.Session", return_value=mock_session):
        with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
            now = datetime(2025, 1, 1, 10, 0, 0)
            mock_dt.now.return_value = now

            result = scheduler_instance.collect_now()

    assert result["success"] is True
    assert result["collected"] == 2
    assert len(result["recipes"]) == 2
    assert result["recipes"][0]["title"] == "Recipe 1"
    assert scheduler_instance._last_collection == now


def test_collect_now_custom_count(scheduler_instance, mock_session, mock_collector, mock_engine):
    """カスタム収集数"""
    with patch("backend.services.recipe_scheduler.Session", return_value=mock_session):
        result = scheduler_instance.collect_now(count=10)

    assert result["success"] is True
    mock_collector.collect_random_recipes.assert_called_once()
    args = mock_collector.collect_random_recipes.call_args
    assert args.kwargs["count"] == 10


def test_collect_now_with_tags(scheduler_instance, mock_session, mock_collector, mock_engine):
    """タグ指定で収集"""
    with patch("backend.services.recipe_scheduler.Session", return_value=mock_session):
        result = scheduler_instance.collect_now(tags="vegetarian,dessert")

    assert result["success"] is True
    mock_collector.collect_random_recipes.assert_called_once()
    args = mock_collector.collect_random_recipes.call_args
    assert args.kwargs["tags"] == "vegetarian,dessert"


def test_collect_now_no_spoonacular_key(scheduler_no_keys):
    """Spoonacular キーなし"""
    result = scheduler_no_keys.collect_now()

    assert result["success"] is False
    assert "SPOONACULAR_API_KEY" in result["error"]
    assert result["collected"] == 0


def test_collect_now_no_deepl_key():
    """DeepL キーなし"""
    scheduler = RecipeScheduler(
        spoonacular_key="test_key",
        deepl_key=None,
    )
    result = scheduler.collect_now()

    assert result["success"] is False
    assert "DEEPL_API_KEY" in result["error"]
    assert result["collected"] == 0


def test_collect_now_collector_exception(
    scheduler_instance, mock_session, mock_engine
):
    """Collector で例外発生"""
    with patch("backend.services.recipe_scheduler.RecipeCollector") as mock_cls:
        mock_cls.side_effect = Exception("Collector initialization failed")

        with patch("backend.services.recipe_scheduler.Session", return_value=mock_session):
            result = scheduler_instance.collect_now()

    assert result["success"] is False
    assert "Collector initialization failed" in result["error"]
    assert result["collected"] == 0


def test_collect_now_session_exception(scheduler_instance, mock_engine):
    """Session 取得で例外発生"""
    with patch("backend.services.recipe_scheduler.Session") as mock_session_cls:
        mock_session_cls.side_effect = Exception("Session error")

        result = scheduler_instance.collect_now()

    assert result["success"] is False
    assert "Session error" in result["error"]


def test_collect_now_default_count(scheduler_instance, mock_session, mock_collector, mock_engine):
    """デフォルト収集数を使用"""
    scheduler_instance.daily_count = 7

    with patch("backend.services.recipe_scheduler.Session", return_value=mock_session):
        scheduler_instance.collect_now()

    args = mock_collector.collect_random_recipes.call_args
    assert args.kwargs["count"] == 7


def test_collect_now_timestamp_format(scheduler_instance, mock_session, mock_collector, mock_engine):
    """タイムスタンプがISO形式"""
    with patch("backend.services.recipe_scheduler.Session", return_value=mock_session):
        with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
            now = datetime(2025, 1, 15, 14, 30, 45)
            mock_dt.now.return_value = now

            result = scheduler_instance.collect_now()

    assert "timestamp" in result
    assert result["timestamp"] == "2025-01-15T14:30:45"


def test_collect_now_empty_result(scheduler_instance, mock_session, mock_engine):
    """収集結果が0件"""
    with patch("backend.services.recipe_scheduler.RecipeCollector") as mock_cls:
        collector = MagicMock()
        collector.collect_random_recipes.return_value = []
        mock_cls.return_value = collector

        with patch("backend.services.recipe_scheduler.Session", return_value=mock_session):
            result = scheduler_instance.collect_now()

    assert result["success"] is True
    assert result["collected"] == 0
    assert len(result["recipes"]) == 0


# ================================================================================
# スケジューラー開始・停止テスト (7 tests)
# ================================================================================

def test_start_scheduler(scheduler_instance):
    """スケジューラー開始"""
    scheduler_instance.start()

    assert scheduler_instance._running is True
    assert scheduler_instance._thread is not None
    assert scheduler_instance._thread.daemon is True
    assert scheduler_instance._thread.is_alive()

    # クリーンアップ
    scheduler_instance.stop()


def test_start_with_callback(scheduler_instance):
    """コールバック関数付きで開始"""
    callback = Mock()
    scheduler_instance.start(on_complete=callback)

    assert scheduler_instance._on_complete == callback
    assert scheduler_instance._running is True

    scheduler_instance.stop()


def test_start_already_running(scheduler_instance):
    """既に実行中の場合は警告"""
    scheduler_instance.start()
    assert scheduler_instance._running is True

    # 2回目の start
    scheduler_instance.start()

    # 状態は変わらない
    assert scheduler_instance._running is True

    scheduler_instance.stop()


def test_stop_scheduler(scheduler_instance):
    """スケジューラー停止"""
    scheduler_instance.start()
    assert scheduler_instance._running is True

    scheduler_instance.stop()

    assert scheduler_instance._running is False


def test_stop_not_running(scheduler_instance):
    """実行していないのに stop を呼んでもエラーなし"""
    assert not scheduler_instance._running

    scheduler_instance.stop()

    assert not scheduler_instance._running


def test_stop_waits_for_thread(scheduler_instance):
    """stop() はスレッド終了を待つ"""
    scheduler_instance.start()
    thread = scheduler_instance._thread

    scheduler_instance.stop()

    assert not thread.is_alive()


def test_thread_is_daemon(scheduler_instance):
    """スレッドはデーモンスレッド"""
    scheduler_instance.start()

    assert scheduler_instance._thread.daemon is True

    scheduler_instance.stop()


# ================================================================================
# ステータス取得テスト (6 tests)
# ================================================================================

def test_get_status_not_running(scheduler_instance):
    """実行していない状態"""
    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        now = datetime(2025, 1, 1, 10, 0, 0)
        mock_dt.now.return_value = now

        status = scheduler_instance.get_status()

    assert status["running"] is False
    assert status["daily_count"] == scheduler_instance.daily_count
    assert status["collection_hour"] == scheduler_instance.collection_hour
    assert status["last_collection"] is None
    assert "next_collection" in status
    assert status["api_keys_configured"]["spoonacular"] is True
    assert status["api_keys_configured"]["deepl"] is True


def test_get_status_running(scheduler_instance):
    """実行中の状態"""
    scheduler_instance.start()

    status = scheduler_instance.get_status()

    assert status["running"] is True

    scheduler_instance.stop()


def test_get_status_next_collection_today(scheduler_instance):
    """次回収集が今日（収集時刻前）"""
    scheduler_instance.collection_hour = 15
    scheduler_instance._last_collection = None

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        now = datetime(2025, 1, 1, 10, 0, 0)
        mock_dt.now.return_value = now
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        status = scheduler_instance.get_status()

    next_collection = datetime.fromisoformat(status["next_collection"])
    assert next_collection.date() == now.date()
    assert next_collection.hour == 15


def test_get_status_next_collection_tomorrow_already_collected(scheduler_instance):
    """次回収集が明日（今日すでに収集済み）"""
    scheduler_instance.collection_hour = 3

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        now = datetime(2025, 1, 1, 10, 0, 0)
        mock_dt.now.return_value = now
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        scheduler_instance._last_collection = datetime(2025, 1, 1, 5, 0, 0)

        status = scheduler_instance.get_status()

    next_collection = datetime.fromisoformat(status["next_collection"])
    assert next_collection.date() == (now + timedelta(days=1)).date()


def test_get_status_api_keys_missing(scheduler_no_keys):
    """APIキーなし"""
    status = scheduler_no_keys.get_status()

    assert status["api_keys_configured"]["spoonacular"] is False
    assert status["api_keys_configured"]["deepl"] is False


def test_get_status_last_collection_formatted(scheduler_instance):
    """last_collection がISO形式"""
    scheduler_instance._last_collection = datetime(2025, 1, 1, 5, 30, 15)

    with patch("backend.services.recipe_scheduler.datetime") as mock_dt:
        now = datetime(2025, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = now
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        status = scheduler_instance.get_status()

    assert status["last_collection"] == "2025-01-01T05:30:15"


# ================================================================================
# グローバルスケジューラー管理テスト (3 tests)
# ================================================================================

def test_get_scheduler_creates_instance():
    """get_scheduler() でインスタンス作成"""
    with patch("backend.services.recipe_scheduler.RecipeScheduler") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        scheduler1 = get_scheduler()
        scheduler2 = get_scheduler()

    # 同じインスタンスを返す
    assert scheduler1 == scheduler2
    assert mock_cls.call_count == 1


def test_init_scheduler_with_params():
    """init_scheduler() でカスタム設定"""
    with patch("backend.services.recipe_scheduler.RecipeScheduler") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        scheduler = init_scheduler(daily_count=10, collection_hour=8, auto_start=False)

    mock_cls.assert_called_once_with(daily_count=10, collection_hour=8)
    assert not mock_instance.start.called


def test_init_scheduler_auto_start():
    """init_scheduler() で自動開始"""
    with patch("backend.services.recipe_scheduler.RecipeScheduler") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        scheduler = init_scheduler(auto_start=True)

    mock_instance.start.assert_called_once()

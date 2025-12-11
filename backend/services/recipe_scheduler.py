"""
Recipe Scheduler - 定期レシピ収集スケジューラー
1日5件の海外レシピを自動収集
"""

import os
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Callable

from sqlmodel import Session

from backend.core.database import engine
from backend.core.config import settings
from backend.services.recipe_collector import RecipeCollector

logger = logging.getLogger(__name__)


class RecipeScheduler:
    """レシピ自動収集スケジューラー"""

    def __init__(
        self,
        daily_count: Optional[int] = None,
        collection_hour: Optional[int] = None,
        spoonacular_key: Optional[str] = None,
        deepl_key: Optional[str] = None,
    ):
        self.daily_count = daily_count or settings.collector_daily_count
        self.collection_hour = collection_hour if collection_hour is not None else settings.collector_hour
        self.spoonacular_key = spoonacular_key or settings.spoonacular_api_key or os.getenv("SPOONACULAR_API_KEY")
        self.deepl_key = deepl_key or settings.deepl_api_key or os.getenv("DEEPL_API_KEY")

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_collection: Optional[datetime] = None
        self._on_complete: Optional[Callable] = None

    def _get_session(self) -> Session:
        """DBセッションを取得"""
        return Session(engine)

    def _should_collect(self) -> bool:
        """収集すべきかどうかを判定"""
        now = datetime.now()

        # 今日すでに収集済みかチェック
        if self._last_collection:
            if self._last_collection.date() == now.date():
                return False

        # 収集時刻に達したかチェック
        if now.hour >= self.collection_hour:
            return True

        return False

    def collect_now(self, count: Optional[int] = None, tags: Optional[str] = None) -> dict:
        """今すぐ収集を実行"""
        count = count or self.daily_count

        if not self.spoonacular_key:
            return {
                "success": False,
                "error": "SPOONACULAR_API_KEY is not set",
                "collected": 0,
            }

        if not self.deepl_key:
            return {
                "success": False,
                "error": "DEEPL_API_KEY is not set",
                "collected": 0,
            }

        try:
            collector = RecipeCollector(
                spoonacular_key=self.spoonacular_key,
                deepl_key=self.deepl_key,
            )

            with self._get_session() as session:
                recipes = collector.collect_random_recipes(
                    session=session,
                    count=count,
                    tags=tags,
                )

            self._last_collection = datetime.now()

            return {
                "success": True,
                "collected": len(recipes),
                "recipes": recipes,  # 既に辞書のリスト
                "timestamp": self._last_collection.isoformat(),
            }

        except Exception as e:
            logger.error(f"Collection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "collected": 0,
            }

    def _run_loop(self):
        """スケジューラーのメインループ"""
        logger.info("Recipe scheduler started")

        while self._running:
            try:
                if self._should_collect():
                    logger.info("Starting scheduled collection...")
                    result = self.collect_now()

                    if result["success"]:
                        logger.info(f"Collected {result['collected']} recipes")
                        if self._on_complete:
                            self._on_complete(result)
                    else:
                        logger.error(f"Collection failed: {result.get('error')}")

                # 1時間ごとにチェック
                for _ in range(60):  # 60 x 60秒 = 1時間
                    if not self._running:
                        break
                    time.sleep(60)

            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # エラー時は5分待機

        logger.info("Recipe scheduler stopped")

    def start(self, on_complete: Optional[Callable] = None):
        """スケジューラーを開始"""
        if self._running:
            logger.warning("Scheduler is already running")
            return

        self._running = True
        self._on_complete = on_complete
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started in background")

    def stop(self):
        """スケジューラーを停止"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def get_status(self) -> dict:
        """スケジューラーの状態を取得"""
        now = datetime.now()

        # 次回収集時刻を計算
        if self._last_collection and self._last_collection.date() == now.date():
            # 今日すでに収集済み → 明日の収集時刻
            next_collection = datetime(
                now.year, now.month, now.day, self.collection_hour
            ) + timedelta(days=1)
        elif now.hour >= self.collection_hour:
            # 今日の収集時刻を過ぎている → 明日
            next_collection = datetime(
                now.year, now.month, now.day, self.collection_hour
            ) + timedelta(days=1)
        else:
            # まだ今日の収集時刻前
            next_collection = datetime(
                now.year, now.month, now.day, self.collection_hour
            )

        return {
            "running": self._running,
            "daily_count": self.daily_count,
            "collection_hour": self.collection_hour,
            "last_collection": self._last_collection.isoformat() if self._last_collection else None,
            "next_collection": next_collection.isoformat(),
            "api_keys_configured": {
                "spoonacular": bool(self.spoonacular_key),
                "deepl": bool(self.deepl_key),
            },
        }


# グローバルスケジューラーインスタンス
_scheduler: Optional[RecipeScheduler] = None


def get_scheduler() -> RecipeScheduler:
    """グローバルスケジューラーを取得"""
    global _scheduler
    if _scheduler is None:
        _scheduler = RecipeScheduler()
    return _scheduler


def init_scheduler(
    daily_count: int = 5,
    collection_hour: int = 3,
    auto_start: bool = True,
) -> RecipeScheduler:
    """スケジューラーを初期化"""
    global _scheduler
    _scheduler = RecipeScheduler(
        daily_count=daily_count,
        collection_hour=collection_hour,
    )
    if auto_start:
        _scheduler.start()
    return _scheduler

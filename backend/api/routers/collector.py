"""
Recipe Collector API Router - 海外レシピ収集エンドポイント
"""

import logging
import os
import re
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.recipe_scheduler import get_scheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/collector", tags=["collector"])


class CollectRequest(BaseModel):
    """収集リクエスト"""
    count: int = 5
    tags: Optional[str] = None  # カンマ区切り: "main course,vegetarian"


class CollectResponse(BaseModel):
    """収集レスポンス"""
    success: bool
    collected: int
    recipes: list[dict] = []
    error: Optional[str] = None
    timestamp: Optional[str] = None


class SchedulerStatus(BaseModel):
    """スケジューラー状態"""
    running: bool
    daily_count: int
    collection_hour: int
    last_collection: Optional[str]
    next_collection: str
    api_keys_configured: dict


@router.get("/status", response_model=SchedulerStatus)
def get_collector_status():
    """収集スケジューラーの状態を取得"""
    scheduler = get_scheduler()
    return scheduler.get_status()


def is_japanese(text: str) -> bool:
    """テキストに日本語が含まれるかチェック"""
    if not text:
        return False
    # ひらがな、カタカナ、漢字のいずれかが含まれていれば日本語
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))


def translate_tags_to_english(tags: str) -> str:
    """日本語タグを英語に翻訳（DeepL API使用）"""
    from backend.services.deepl_translator import DeepLTranslator
    from backend.core.config import settings

    deepl_key = settings.deepl_api_key or os.getenv("DEEPL_API_KEY")
    if not deepl_key:
        logger.warning("DeepL API key not configured, using original tags")
        return tags

    try:
        translator = DeepLTranslator(api_key=deepl_key)
        # カンマ区切りで複数タグを処理
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        translated_tags = []

        for tag in tag_list:
            if is_japanese(tag):
                translated = translator.translate(tag, target_lang="EN", source_lang="JA")
                translated_tags.append(translated.lower())
                logger.info(f"Translated tag: {tag} -> {translated}")
            else:
                translated_tags.append(tag.lower())

        return ",".join(translated_tags)
    except Exception as e:
        logger.error(f"Tag translation failed: {e}")
        return tags


@router.post("/collect", response_model=CollectResponse)
def collect_recipes(request: CollectRequest):
    """今すぐレシピを収集

    タグは日本語でも入力可能です。DeepL APIで自動的に英語に翻訳されます。
    例: 「肉料理」→ "meat dish", 「デザート」→ "dessert"
    """
    scheduler = get_scheduler()

    # 日本語タグを英語に翻訳
    tags = request.tags
    if tags and is_japanese(tags):
        tags = translate_tags_to_english(tags)
        logger.info(f"Using translated tags: {tags}")

    result = scheduler.collect_now(count=request.count, tags=tags)
    return CollectResponse(**result)


@router.post("/start")
def start_scheduler():
    """スケジューラーを開始"""
    scheduler = get_scheduler()
    if scheduler._running:
        return {"status": "already_running", "message": "スケジューラーは既に実行中です"}
    scheduler.start()
    return {"status": "started", "message": "スケジューラーを開始しました"}


@router.post("/stop")
def stop_scheduler():
    """スケジューラーを停止"""
    scheduler = get_scheduler()
    if not scheduler._running:
        return {"status": "not_running", "message": "スケジューラーは実行されていません"}
    scheduler.stop()
    return {"status": "stopped", "message": "スケジューラーを停止しました"}

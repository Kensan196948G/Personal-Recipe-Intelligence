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


class QuotaInfoResponse(BaseModel):
    """Spoonacular APIクォータ情報"""
    quota_left: Optional[int] = None  # 残りポイント
    quota_request: Optional[int] = None  # このリクエストで消費したポイント
    is_exceeded: bool = False  # 制限超過フラグ
    reset_time: Optional[str] = None  # リセット予定時刻（ISO8601形式）
    error_code: Optional[int] = None  # HTTPエラーコード
    error_message: Optional[str] = None  # エラーメッセージ


class CollectResponse(BaseModel):
    """収集レスポンス"""
    success: bool
    collected: int
    recipes: list[dict] = []
    error: Optional[str] = None
    timestamp: Optional[str] = None
    quota_exceeded: bool = False  # API制限超過フラグ
    quota_info: Optional[QuotaInfoResponse] = None  # クォータ詳細情報


class ImageBackfillStatus(BaseModel):
    """画像バックフィル状態"""
    pending_count: int
    batch_limit: int


class SchedulerStatus(BaseModel):
    """スケジューラー状態"""
    running: bool
    daily_count: int
    collection_hour: int
    last_collection: Optional[str]
    next_collection: str
    api_keys_configured: dict
    image_backfill: ImageBackfillStatus


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

    Returns:
        CollectResponse: 収集結果。API制限に到達した場合は quota_exceeded=True となり、
        quota_info に詳細情報（リセット予定時刻など）が含まれます。
    """
    scheduler = get_scheduler()

    # 日本語タグを英語に翻訳
    tags = request.tags
    if tags and is_japanese(tags):
        tags = translate_tags_to_english(tags)
        logger.info(f"Using translated tags: {tags}")

    result = scheduler.collect_now(count=request.count, tags=tags)

    # quota_info がある場合は QuotaInfoResponse に変換
    quota_info = None
    if result.get("quota_info"):
        quota_info = QuotaInfoResponse(**result["quota_info"])

    return CollectResponse(
        success=result.get("success", False),
        collected=result.get("collected", 0),
        recipes=result.get("recipes", []),
        error=result.get("error"),
        timestamp=result.get("timestamp"),
        quota_exceeded=result.get("quota_exceeded", False),
        quota_info=quota_info,
    )


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


class BackfillRequest(BaseModel):
    """画像バックフィルリクエスト"""
    limit: Optional[int] = None  # 処理するレシピ数の上限
    dry_run: bool = False  # 実際には変更せず確認のみ


class BackfillResponse(BaseModel):
    """画像バックフィルレスポンス"""
    success: bool
    processed: int
    failed: int
    message: str


@router.post("/backfill-images", response_model=BackfillResponse)
async def backfill_images(request: BackfillRequest):
    """既存レシピに画像を追加（source_urlからスクレイピング）

    画像がないレシピに対して、source_urlページから画像を取得します。
    """
    from backend.scripts.backfill_images import backfill_recipe_images

    try:
        success, failed = await backfill_recipe_images(
            dry_run=request.dry_run,
            limit=request.limit
        )

        mode = "DRY RUN" if request.dry_run else "実行"
        return BackfillResponse(
            success=True,
            processed=success,
            failed=failed,
            message=f"画像バックフィル{mode}完了: 成功 {success}件, 失敗 {failed}件"
        )
    except Exception as e:
        logger.error(f"Backfill failed: {e}")
        return BackfillResponse(
            success=False,
            processed=0,
            failed=0,
            message=f"エラー: {str(e)}"
        )


@router.post("/backfill-spoonacular", response_model=BackfillResponse)
async def backfill_from_spoonacular(request: BackfillRequest):
    """Spoonacular APIから画像を取得

    画像がないSpoonacularレシピに対して、APIから直接画像を取得します。
    タイトルから英語キーワードを抽出して検索します。
    APIレート制限のため、処理には時間がかかります。
    """
    from backend.scripts.backfill_spoonacular_images import backfill_from_spoonacular

    try:
        success, failed = await backfill_from_spoonacular(
            dry_run=request.dry_run,
            limit=request.limit
        )

        mode = "DRY RUN" if request.dry_run else "実行"
        return BackfillResponse(
            success=True,
            processed=success,
            failed=failed,
            message=f"Spoonacular画像バックフィル{mode}完了: 成功 {success}件, 失敗 {failed}件"
        )
    except Exception as e:
        logger.error(f"Spoonacular backfill failed: {e}")
        return BackfillResponse(
            success=False,
            processed=0,
            failed=0,
            message=f"エラー: {str(e)}"
        )

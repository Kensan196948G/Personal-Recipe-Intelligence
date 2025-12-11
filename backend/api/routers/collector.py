"""
Recipe Collector API Router - 海外レシピ収集エンドポイント
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.services.recipe_scheduler import get_scheduler

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


@router.post("/collect", response_model=CollectResponse)
def collect_recipes(request: CollectRequest):
    """今すぐレシピを収集"""
    scheduler = get_scheduler()
    result = scheduler.collect_now(count=request.count, tags=request.tags)
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

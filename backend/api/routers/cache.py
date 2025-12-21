"""
Cache API Router - Cache monitoring and control endpoints
"""

from fastapi import APIRouter, Query

from backend.api.cache_routes import (
    clear_cache_handler,
    get_cache_stats_handler,
    invalidate_cache_handler,
)

router = APIRouter(prefix="/api/v1/cache", tags=["cache"])


@router.get("/stats")
async def get_cache_stats():
    """キャッシュ統計情報取得"""
    return get_cache_stats_handler()


@router.post("/clear")
async def clear_cache():
    """キャッシュ全削除"""
    return clear_cache_handler()


@router.post("/invalidate")
async def invalidate_cache(
    pattern: str = Query(..., description="パターン一致でキャッシュ無効化"),
):
    """パターン一致でキャッシュ無効化"""
    return invalidate_cache_handler(pattern)

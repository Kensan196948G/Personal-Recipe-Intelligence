"""
管理者API ルーター

管理者ダッシュボード用のエンドポイントを提供。
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.services.admin_service import AdminService
from backend.api.auth import get_current_admin_user


router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class SettingsUpdate(BaseModel):
    """システム設定更新リクエスト"""

    site_name: Optional[str] = None
    max_upload_size_mb: Optional[int] = Field(None, ge=1, le=100)
    enable_public_recipes: Optional[bool] = None
    enable_user_registration: Optional[bool] = None
    default_language: Optional[str] = None
    timezone: Optional[str] = None
    pagination_size: Optional[int] = Field(None, ge=10, le=100)
    cache_ttl_seconds: Optional[int] = Field(None, ge=60, le=3600)
    ocr_enabled: Optional[bool] = None
    scraping_enabled: Optional[bool] = None
    max_recipes_per_user: Optional[int] = Field(None, ge=100, le=10000)
    maintenance_mode: Optional[bool] = None


def get_admin_service() -> AdminService:
    """AdminService のインスタンスを取得"""
    return AdminService()


@router.get("/stats")
async def get_system_stats(
    admin_service: AdminService = Depends(get_admin_service),
    _: Dict[str, Any] = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    システム全体の統計情報を取得

    管理者のみアクセス可能。
    """
    try:
        stats = admin_service.get_system_stats()
        return {"status": "ok", "data": stats, "error": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system stats: {str(e)}",
        )


@router.get("/stats/recipes")
async def get_recipe_stats(
    days: int = Query(30, ge=1, le=365, description="集計対象期間（日数）"),
    admin_service: AdminService = Depends(get_admin_service),
    _: Dict[str, Any] = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    レシピ統計を取得

    Args:
      days: 集計対象期間（日数）

    管理者のみアクセス可能。
    """
    try:
        stats = admin_service.get_recipe_stats(days=days)
        return {"status": "ok", "data": stats, "error": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recipe stats: {str(e)}",
        )


@router.get("/stats/users")
async def get_user_stats(
    days: int = Query(30, ge=1, le=365, description="集計対象期間（日数）"),
    admin_service: AdminService = Depends(get_admin_service),
    _: Dict[str, Any] = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    ユーザー統計を取得

    Args:
      days: 集計対象期間（日数）

    管理者のみアクセス可能。
    """
    try:
        stats = admin_service.get_user_stats(days=days)
        return {"status": "ok", "data": stats, "error": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}",
        )


@router.get("/settings")
async def get_settings(
    admin_service: AdminService = Depends(get_admin_service),
    _: Dict[str, Any] = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    システム設定を取得

    管理者のみアクセス可能。
    """
    try:
        settings = admin_service.get_settings()
        return {"status": "ok", "data": settings, "error": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get settings: {str(e)}",
        )


@router.put("/settings")
async def update_settings(
    settings: SettingsUpdate,
    admin_service: AdminService = Depends(get_admin_service),
    _: Dict[str, Any] = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    システム設定を更新

    管理者のみアクセス可能。
    """
    try:
        # None でない項目のみ更新
        update_data = {k: v for k, v in settings.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No settings to update",
            )

        updated_settings = admin_service.update_settings(update_data)
        return {"status": "ok", "data": updated_settings, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}",
        )


@router.get("/logs")
async def get_system_logs(
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
    level: Optional[str] = Query(None, description="ログレベルフィルタ"),
    admin_service: AdminService = Depends(get_admin_service),
    _: Dict[str, Any] = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    システムログを取得

    Args:
      limit: 取得件数
      level: ログレベルフィルタ (ERROR, WARNING, INFO)

    管理者のみアクセス可能。
    """
    try:
        # レベル検証
        if level and level not in ["ERROR", "WARNING", "INFO", "DEBUG"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid log level. Must be ERROR, WARNING, INFO, or DEBUG",
            )

        logs = admin_service.get_system_logs(limit=limit, level=level)
        return {
            "status": "ok",
            "data": {"logs": logs, "count": len(logs)},
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system logs: {str(e)}",
        )


@router.get("/health")
async def health_check(
    admin_service: AdminService = Depends(get_admin_service),
    _: Dict[str, Any] = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    システムヘルスチェック

    管理者のみアクセス可能。
    """
    try:
        health = admin_service.get_health_check()
        return {"status": "ok", "data": health, "error": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform health check: {str(e)}",
        )


@router.post("/cache/clear")
async def clear_cache(
    admin_service: AdminService = Depends(get_admin_service),
    _: Dict[str, Any] = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    統計キャッシュをクリア

    管理者のみアクセス可能。
    """
    try:
        admin_service.clear_stats_cache()
        return {
            "status": "ok",
            "data": {"message": "Cache cleared successfully"},
            "error": None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}",
        )

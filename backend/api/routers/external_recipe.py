"""
外部レシピAPI ルーター

外部レシピサイトからのインポート機能を提供
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
import logging
import httpx

from backend.services.external_recipe_service import ExternalRecipeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/external", tags=["external"])


class ImportRequest(BaseModel):
    """レシピインポートリクエスト"""

    url: HttpUrl


class PreviewRequest(BaseModel):
    """プレビューリクエスト"""

    url: HttpUrl


class ImportResponse(BaseModel):
    """レシピインポートレスポンス"""

    status: str
    data: Dict[str, Any]
    error: str | None = None


class PreviewResponse(BaseModel):
    """プレビューレスポンス"""

    status: str
    data: Dict[str, Any] | None = None
    error: str | None = None


class SupportedSitesResponse(BaseModel):
    """対応サイト一覧レスポンス"""

    status: str
    data: List[Dict[str, str]]
    error: str | None = None


def get_external_recipe_service() -> ExternalRecipeService:
    """外部レシピサービスを取得"""
    return ExternalRecipeService()


async def fetch_html(url: str) -> str:
    """URLからHTMLを取得"""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            )
            response.raise_for_status()
            return response.text
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch URL {url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")


@router.post("/import", response_model=ImportResponse)
async def import_recipe(
    request: ImportRequest,
    service: ExternalRecipeService = Depends(get_external_recipe_service),
):
    """
    URLからレシピをインポート

    Args:
      request: インポートリクエスト

    Returns:
      ImportResponse: インポートされたレシピデータ
    """
    try:
        url = str(request.url)

        # URLの妥当性を検証
        if not service.validate_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # HTMLを取得
        html = await fetch_html(url)

        # レシピをパース
        recipe_data = await service.import_recipe(url, html)

        return ImportResponse(
            status="ok",
            data=recipe_data.to_dict(),
            error=None,
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Failed to parse recipe: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during import: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/preview", response_model=PreviewResponse)
async def preview_recipe(
    request: PreviewRequest,
    service: ExternalRecipeService = Depends(get_external_recipe_service),
):
    """
    URLからレシピのプレビューを取得

    Args:
      request: プレビューリクエスト

    Returns:
      PreviewResponse: レシピのプレビューデータ
    """
    try:
        url = str(request.url)

        # URLの妥当性を検証
        if not service.validate_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # パーサーが対応しているか確認
        parser = service.get_parser(url)
        if not parser:
            return PreviewResponse(
                status="error",
                data=None,
                error="Unsupported site. This URL may not be supported.",
            )

        # HTMLを取得
        html = await fetch_html(url)

        # レシピをパース
        recipe_data = await service.import_recipe(url, html)

        # プレビュー用に一部のデータのみ返す
        preview_data = {
            "title": recipe_data.title,
            "description": recipe_data.description,
            "image_url": recipe_data.image_url,
            "cooking_time": recipe_data.cooking_time,
            "servings": recipe_data.servings,
            "ingredient_count": len(recipe_data.ingredients),
            "step_count": len(recipe_data.steps),
            "source_url": recipe_data.source_url,
            "author": recipe_data.author,
        }

        return PreviewResponse(
            status="ok",
            data=preview_data,
            error=None,
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Failed to preview recipe: {str(e)}")
        return PreviewResponse(
            status="error",
            data=None,
            error=f"Failed to parse recipe: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during preview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/supported-sites", response_model=SupportedSitesResponse)
async def get_supported_sites(
    service: ExternalRecipeService = Depends(get_external_recipe_service),
):
    """
    対応サイト一覧を取得

    Returns:
      SupportedSitesResponse: 対応サイトのリスト
    """
    try:
        sites = service.get_supported_sites()
        return SupportedSitesResponse(
            status="ok",
            data=sites,
            error=None,
        )
    except Exception as e:
        logger.error(f"Failed to get supported sites: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

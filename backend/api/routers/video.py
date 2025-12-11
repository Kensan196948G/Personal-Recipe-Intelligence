"""
動画レシピ抽出APIルーター
"""

import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.video.youtube_extractor import YouTubeExtractor
from backend.video.models import VideoExtractRequest, VideoExtractResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/video", tags=["video"])

# YouTubeExtractorインスタンス
youtube_extractor = YouTubeExtractor()


@router.post("/extract", response_model=VideoExtractResponse)
async def extract_video_recipe(request: VideoExtractRequest):
    """
    YouTube URLからレシピ情報を抽出

    Args:
        request: 動画レシピ抽出リクエスト

    Returns:
        抽出されたレシピデータ

    Raises:
        HTTPException: 抽出失敗時
    """
    try:
        logger.info(f"Extracting recipe from YouTube URL: {request.url}")

        # レシピ抽出
        recipe = youtube_extractor.extract_recipe(
            url=request.url,
            language=request.language,
            extract_from_description=request.extract_from_description,
        )

        if not recipe:
            logger.error(f"Failed to extract recipe from URL: {request.url}")
            return VideoExtractResponse(
                status="error",
                data=None,
                error="Failed to extract recipe from the provided YouTube URL",
            )

        logger.info(
            f"Successfully extracted recipe: {recipe.recipe_name} "
            f"({len(recipe.ingredients)} ingredients, {len(recipe.steps)} steps)"
        )

        return VideoExtractResponse(status="ok", data=recipe, error=None)

    except Exception as e:
        logger.error(f"Error extracting recipe from video: {e}", exc_info=True)

        return VideoExtractResponse(
            status="error", data=None, error=f"Internal error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント

    Returns:
        ステータス情報
    """
    return JSONResponse(
        content={
            "status": "ok",
            "service": "video-recipe-extractor",
            "version": "1.0.0",
        }
    )

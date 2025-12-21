"""
レシピ共有APIルーター

レシピを様々な形式でエクスポートし、共有リンクを生成するAPIエンドポイントを提供する。
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Path as PathParam, Query, Response
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel, Field

from backend.services.share_service import ShareService


router = APIRouter(prefix="/api/v1/share", tags=["share"])
share_service = ShareService()


class ShareLinkResponse(BaseModel):
    """共有リンク生成レスポンス"""

    token: str = Field(..., description="共有トークン")
    expires_at: str = Field(..., description="有効期限（ISO8601形式）")
    share_url: str = Field(..., description="共有URL")


class ShareLinkRequest(BaseModel):
    """共有リンク生成リクエスト"""

    expires_hours: int = Field(24, ge=1, le=168, description="有効期限（時間）")


class APIResponse(BaseModel):
    """API標準レスポンス"""

    status: str = Field(..., description="ステータス")
    data: Optional[dict] = Field(None, description="データ")
    error: Optional[str] = Field(None, description="エラーメッセージ")


# ダミーレシピデータベース（デモ用）
# Note: In production, replace with actual database queries
# TODO: Replace mock data with database integration using backend.models.Recipe
RECIPES_DB = {
    1: {
        "id": 1,
        "name": "カルボナーラ",
        "description": "濃厚でクリーミーなイタリアンパスタ",
        "servings": 2,
        "prep_time": 10,
        "cook_time": 15,
        "ingredients": [
            {"name": "スパゲッティ", "amount": "200", "unit": "g"},
            {"name": "ベーコン", "amount": "100", "unit": "g"},
            {"name": "卵黄", "amount": "3", "unit": "個"},
            {"name": "パルメザンチーズ", "amount": "50", "unit": "g"},
            {"name": "黒こしょう", "amount": "適量", "unit": ""},
        ],
        "steps": [
            {"text": "スパゲッティを茹で始める（塩を加えた熱湯で）"},
            {"text": "ベーコンを細切りにして、フライパンでカリカリに炒める"},
            {"text": "ボウルに卵黄、パルメザンチーズ、黒こしょうを混ぜる"},
            {"text": "茹で上がったパスタをフライパンに入れ、火を止める"},
            {"text": "卵液を加えて素早く混ぜ、余熱で卵を固める"},
            {"text": "皿に盛り付け、黒こしょうとチーズをトッピングして完成"},
        ],
        "tags": ["パスタ", "イタリアン", "簡単", "クリーミー"],
        "source": "Personal Recipe Intelligence",
    }
}


def get_recipe_by_id(recipe_id: int) -> dict:
    """
    レシピIDからレシピデータを取得

    Args:
      recipe_id: レシピID

    Returns:
      レシピデータ

    Raises:
      HTTPException: レシピが見つからない場合
    """
    recipe = RECIPES_DB.get(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("/{recipe_id}/json", response_model=APIResponse)
async def get_recipe_json(
    recipe_id: int = PathParam(..., ge=1, description="レシピID"),
    compact: bool = Query(True, description="コンパクト形式にするか"),
):
    """
    レシピをJSON形式で取得（共有用コンパクト版）

    Args:
      recipe_id: レシピID
      compact: コンパクト形式にするか

    Returns:
      JSON形式のレシピデータ
    """
    try:
        recipe = get_recipe_by_id(recipe_id)
        json_data = share_service.to_json(recipe, compact=compact)

        return {"status": "ok", "data": {"json": json_data}, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export JSON: {str(e)}")


@router.get("/{recipe_id}/markdown", response_class=PlainTextResponse)
async def get_recipe_markdown(
    recipe_id: int = PathParam(..., ge=1, description="レシピID"),
):
    """
    レシピをMarkdown形式で取得（印刷・ブログ用）

    Args:
      recipe_id: レシピID

    Returns:
      Markdown形式のレシピデータ
    """
    try:
        recipe = get_recipe_by_id(recipe_id)
        markdown_data = share_service.to_markdown(recipe)

        return Response(
            content=markdown_data,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="recipe_{recipe_id}.md"'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to export Markdown: {str(e)}"
        )


@router.get("/{recipe_id}/html", response_class=HTMLResponse)
async def get_recipe_html(
    recipe_id: int = PathParam(..., ge=1, description="レシピID"),
):
    """
    レシピをHTML形式で取得（Webページ埋め込み用）

    Args:
      recipe_id: レシピID

    Returns:
      HTML形式のレシピデータ
    """
    try:
        recipe = get_recipe_by_id(recipe_id)
        html_data = share_service.to_html(recipe)

        return HTMLResponse(content=html_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export HTML: {str(e)}")


@router.post("/{recipe_id}/link", response_model=ShareLinkResponse)
async def create_share_link(
    recipe_id: int = PathParam(..., ge=1, description="レシピID"),
    request: ShareLinkRequest = ShareLinkRequest(),
):
    """
    共有リンクを生成（一時的なトークンベース）

    Args:
      recipe_id: レシピID
      request: 共有リンク生成リクエスト

    Returns:
      共有リンク情報
    """
    try:
        # レシピの存在確認
        get_recipe_by_id(recipe_id)

        # 共有リンク生成
        link_data = share_service.generate_share_link(
            recipe_id=recipe_id, expires_hours=request.expires_hours
        )

        return ShareLinkResponse(**link_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create share link: {str(e)}"
        )


@router.get("/link/{token}")
async def access_share_link(
    token: str = PathParam(..., description="共有トークン"),
    format: str = Query("html", regex="^(json|markdown|html)$", description="出力形式"),
):
    """
    共有リンクからレシピにアクセス

    Args:
      token: 共有トークン
      format: 出力形式（json, markdown, html）

    Returns:
      レシピデータ（指定された形式）
    """
    try:
        # トークン検証
        token_data = share_service.verify_share_token(token)
        if not token_data:
            raise HTTPException(status_code=404, detail="Invalid or expired token")

        recipe_id = token_data["recipe_id"]
        recipe = get_recipe_by_id(recipe_id)

        # 形式に応じて出力
        if format == "json":
            json_data = share_service.to_json(recipe, compact=False)
            return Response(
                content=json_data, media_type="application/json; charset=utf-8"
            )
        elif format == "markdown":
            markdown_data = share_service.to_markdown(recipe)
            return Response(
                content=markdown_data, media_type="text/markdown; charset=utf-8"
            )
        else:  # html
            html_data = share_service.to_html(recipe)
            return HTMLResponse(content=html_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to access share link: {str(e)}"
        )


@router.delete("/link/{token}", response_model=APIResponse)
async def revoke_share_link(token: str = PathParam(..., description="共有トークン")):
    """
    共有リンクを無効化

    Args:
      token: 共有トークン

    Returns:
      無効化結果
    """
    try:
        success = share_service.revoke_share_token(token)

        if not success:
            raise HTTPException(status_code=404, detail="Token not found")

        return {
            "status": "ok",
            "data": {"message": "Share link revoked successfully"},
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to revoke share link: {str(e)}"
        )


@router.post("/cleanup", response_model=APIResponse)
async def cleanup_expired_tokens():
    """
    期限切れトークンのクリーンアップ

    Returns:
      クリーンアップ結果
    """
    try:
        deleted_count = share_service.cleanup_expired_tokens()

        return {
            "status": "ok",
            "data": {
                "message": f"Cleaned up {deleted_count} expired tokens",
                "deleted_count": deleted_count,
            },
            "error": None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to cleanup tokens: {str(e)}"
        )

"""
QRCode API Router

レシピ共有用QRコード生成API
"""

from typing import Literal
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse, JSONResponse
import io

from backend.services.qrcode_service import QRCodeService


router = APIRouter(prefix="/api/v1/qrcode", tags=["qrcode"])

# QRCodeサービスインスタンス（シングルトン）
qrcode_service = QRCodeService(
    base_url="http://localhost:8000",
    logo_path=None,  # 必要に応じて設定
)


@router.get("/{recipe_id}", response_class=StreamingResponse)
async def get_recipe_qrcode_png(
    recipe_id: int,
    box_size: int = Query(10, ge=1, le=50, description="QRコードのボックスサイズ"),
    border: int = Query(4, ge=0, le=10, description="QRコードのボーダー幅"),
    fill_color: str = Query("black", description="QRコードの色"),
    back_color: str = Query("white", description="背景色"),
    style: Literal["square", "rounded", "circle"] = Query(
        "square", description="QRコードのスタイル"
    ),
    add_logo: bool = Query(False, description="ロゴを埋め込むかどうか"),
) -> StreamingResponse:
    """
    レシピ共有用QRコード画像を取得（PNG形式）

    Args:
      recipe_id: レシピID
      box_size: QRコードのボックスサイズ（1-50）
      border: QRコードのボーダー幅（0-10）
      fill_color: QRコードの色
      back_color: 背景色
      style: QRコードのスタイル（square/rounded/circle）
      add_logo: ロゴを埋め込むかどうか

    Returns:
      PNG画像
    """
    try:
        png_bytes = qrcode_service.generate_recipe_qrcode_url(
            recipe_id=recipe_id,
            format="png",
            box_size=box_size,
            border=border,
            fill_color=fill_color,
            back_color=back_color,
            style=style,
            add_logo=add_logo,
        )

        return StreamingResponse(
            io.BytesIO(png_bytes),
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=recipe_{recipe_id}_qrcode.png"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QRコード生成エラー: {str(e)}")


@router.get("/{recipe_id}/svg", response_class=Response)
async def get_recipe_qrcode_svg(
    recipe_id: int,
    box_size: int = Query(10, ge=1, le=50, description="QRコードのボックスサイズ"),
    border: int = Query(4, ge=0, le=10, description="QRコードのボーダー幅"),
    fill_color: str = Query("black", description="QRコードの色"),
    back_color: str = Query("white", description="背景色"),
) -> Response:
    """
    レシピ共有用QRコード画像を取得（SVG形式）

    Args:
      recipe_id: レシピID
      box_size: QRコードのボックスサイズ（1-50）
      border: QRコードのボーダー幅（0-10）
      fill_color: QRコードの色
      back_color: 背景色

    Returns:
      SVG画像
    """
    try:
        svg_content = qrcode_service.generate_recipe_qrcode_url(
            recipe_id=recipe_id,
            format="svg",
            box_size=box_size,
            border=border,
            fill_color=fill_color,
            back_color=back_color,
        )

        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f"inline; filename=recipe_{recipe_id}_qrcode.svg"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QRコード生成エラー: {str(e)}")


@router.get("/{recipe_id}/data", response_class=JSONResponse)
async def get_recipe_qrcode_data(
    recipe_id: int,
) -> dict:
    """
    レシピ共有用QRコードデータを取得

    Args:
      recipe_id: レシピID

    Returns:
      QRコードに埋め込まれるデータ
    """
    try:
        # レシピURLを生成
        recipe_url = qrcode_service.generate_recipe_url(recipe_id)

        return {
            "status": "ok",
            "data": {
                "recipe_id": recipe_id,
                "url": recipe_url,
                "qrcode_png_url": f"/api/v1/qrcode/{recipe_id}",
                "qrcode_svg_url": f"/api/v1/qrcode/{recipe_id}/svg",
            },
            "error": None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"QRコードデータ取得エラー: {str(e)}"
        )


@router.post("/{recipe_id}/data-embed", response_model=None)
async def generate_recipe_qrcode_with_data(
    recipe_id: int,
    recipe_data: dict,
    format: Literal["png", "svg"] = Query("png", description="出力形式"),
    box_size: int = Query(10, ge=1, le=50, description="QRコードのボックスサイズ"),
    border: int = Query(4, ge=0, le=10, description="QRコードのボーダー幅"),
    fill_color: str = Query("black", description="QRコードの色"),
    back_color: str = Query("white", description="背景色"),
    style: Literal["square", "rounded", "circle"] = Query(
        "square", description="QRコードのスタイル（PNG時のみ）"
    ),
    add_logo: bool = Query(False, description="ロゴを埋め込むかどうか（PNG時のみ）"),
):
    """
    レシピデータ埋め込み型QRコードを生成（データモード）

    Args:
      recipe_id: レシピID
      recipe_data: レシピデータ（JSON）
      format: 出力形式（png/svg）
      box_size: QRコードのボックスサイズ（1-50）
      border: QRコードのボーダー幅（0-10）
      fill_color: QRコードの色
      back_color: 背景色
      style: QRコードのスタイル（square/rounded/circle）
      add_logo: ロゴを埋め込むかどうか

    Returns:
      PNG画像 または SVG画像
    """
    try:
        result = qrcode_service.generate_recipe_qrcode_data(
            recipe_id=recipe_id,
            recipe_data=recipe_data,
            format=format,
            box_size=box_size,
            border=border,
            fill_color=fill_color,
            back_color=back_color,
            style=style,
            add_logo=add_logo,
        )

        if format == "svg":
            return Response(
                content=result,
                media_type="image/svg+xml",
                headers={
                    "Content-Disposition": f"inline; filename=recipe_{recipe_id}_data_qrcode.svg"
                },
            )
        else:
            return StreamingResponse(
                io.BytesIO(result),
                media_type="image/png",
                headers={
                    "Content-Disposition": f"inline; filename=recipe_{recipe_id}_data_qrcode.png"
                },
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QRコード生成エラー: {str(e)}")

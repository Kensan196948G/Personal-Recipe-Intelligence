"""
OCR API Router - Image-to-recipe extraction endpoints
"""

import base64
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.api.schemas import ApiResponse
from backend.core.database import get_session

router = APIRouter(prefix="/api/v1/ocr", tags=["ocr"])


class OCRResult(BaseModel):
    """OCR結果"""

    raw_text: str
    title: Optional[str] = None
    ingredients: list[dict] = Field(default_factory=list)
    steps: list[dict] = Field(default_factory=list)
    confidence: float = 0.0


class Base64ImageRequest(BaseModel):
    """Base64画像リクエスト"""

    image_data: str = Field(..., description="Base64エンコードされた画像データ")
    save: bool = Field(default=False, description="OCR後に保存するか")


@router.post("/extract", response_model=ApiResponse)
async def extract_from_image(
    file: UploadFile = File(...), save: bool = False, session=Depends(get_session)
):
    """画像からレシピを抽出"""
    try:
        from backend.ocr.service import OCRService

        # ファイルタイプチェック
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="画像ファイルをアップロードしてください"
            )

        # 画像データ読み込み
        image_data = await file.read()

        # OCR実行
        ocr_service = OCRService()
        result = ocr_service.extract_recipe(image_data)

        if not result:
            raise HTTPException(status_code=400, detail="レシピの抽出に失敗しました")

        # 保存オプション
        if save and result.get("title"):
            from backend.services.recipe_service import RecipeService

            service = RecipeService(session)
            recipe = service.create_recipe(
                title=result.get("title", "OCRレシピ"),
                description=result.get("description"),
                source_type="ocr",
                ingredients=result.get("ingredients", []),
                steps=result.get("steps", []),
            )
            return ApiResponse(
                status="ok",
                data={
                    "message": "レシピを保存しました",
                    "recipe_id": recipe.id,
                    "recipe": result,
                },
            )

        return ApiResponse(status="ok", data=result)

    except ImportError:
        raise HTTPException(status_code=501, detail="OCRモジュールが利用できません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-base64", response_model=ApiResponse)
async def extract_from_base64(
    request: Base64ImageRequest, session=Depends(get_session)
):
    """Base64画像からレシピを抽出"""
    try:
        from backend.ocr.service import OCRService

        # Base64デコード
        try:
            image_data = base64.b64decode(request.image_data)
        except Exception:
            raise HTTPException(status_code=400, detail="無効なBase64データです")

        # OCR実行
        ocr_service = OCRService()
        result = ocr_service.extract_recipe(image_data)

        if not result:
            raise HTTPException(status_code=400, detail="レシピの抽出に失敗しました")

        # 保存オプション
        if request.save and result.get("title"):
            from backend.services.recipe_service import RecipeService

            service = RecipeService(session)
            recipe = service.create_recipe(
                title=result.get("title", "OCRレシピ"),
                description=result.get("description"),
                source_type="ocr",
                ingredients=result.get("ingredients", []),
                steps=result.get("steps", []),
            )
            return ApiResponse(
                status="ok",
                data={
                    "message": "レシピを保存しました",
                    "recipe_id": recipe.id,
                    "recipe": result,
                },
            )

        return ApiResponse(status="ok", data=result)

    except ImportError:
        raise HTTPException(status_code=501, detail="OCRモジュールが利用できません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

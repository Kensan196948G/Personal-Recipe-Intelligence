"""
Translation API Router - Recipe translation endpoints
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.schemas import ApiResponse
from backend.core.database import get_session

router = APIRouter(prefix="/api/v1/translation", tags=["translation"])


class TranslateRecipeRequest(BaseModel):
  """レシピ翻訳リクエスト"""

  recipe_id: int = Field(..., description="翻訳するレシピID")
  target_language: str = Field(default="JA", description="翻訳先言語コード")
  save_as_new: bool = Field(default=False, description="新しいレシピとして保存するか")


class TranslateTextRequest(BaseModel):
  """テキスト翻訳リクエスト"""

  text: str = Field(..., description="翻訳するテキスト")
  source_language: Optional[str] = Field(
    None, description="翻訳元言語コード（自動検出）"
  )
  target_language: str = Field(default="JA", description="翻訳先言語コード")


@router.post("/recipe", response_model=ApiResponse)
async def translate_recipe(
  request: TranslateRecipeRequest, session=Depends(get_session)
):
  """レシピ全体を翻訳"""
  try:
    from backend.services.recipe_service import RecipeService
    from backend.translation.service import TranslationService

    # レシピ取得
    recipe_service = RecipeService(session)
    recipe = recipe_service.get_recipe(request.recipe_id)

    if not recipe:
      raise HTTPException(status_code=404, detail="レシピが見つかりません")

    # 翻訳サービス
    translation_service = TranslationService()

    # レシピ全体を翻訳
    translated = translation_service.translate_recipe(
      recipe=recipe, target_lang=request.target_language
    )

    # 新しいレシピとして保存
    if request.save_as_new:
      new_recipe = recipe_service.create_recipe(
        title=translated["title"],
        description=translated.get("description"),
        servings=recipe.servings,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        source_url=recipe.source_url,
        source_type=recipe.source_type,
        ingredients=translated.get("ingredients", []),
        steps=translated.get("steps", []),
      )
      return ApiResponse(
        status="ok",
        data={
          "message": "翻訳したレシピを保存しました",
          "recipe_id": new_recipe.id,
          "translated": translated,
        },
      )

    return ApiResponse(status="ok", data=translated)

  except ImportError:
    raise HTTPException(status_code=501, detail="翻訳モジュールが利用できません")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/text", response_model=ApiResponse)
async def translate_text(request: TranslateTextRequest):
  """テキストを翻訳"""
  try:
    from backend.translation.service import TranslationService

    translation_service = TranslationService()
    result = translation_service.translate_text(
      text=request.text,
      source_lang=request.source_language,
      target_lang=request.target_language,
    )

    return ApiResponse(
      status="ok",
      data={
        "original": request.text,
        "translated": result,
        "target_language": request.target_language,
      },
    )

  except ImportError:
    raise HTTPException(status_code=501, detail="翻訳モジュールが利用できません")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages", response_model=ApiResponse)
async def get_supported_languages():
  """サポートされている言語一覧"""
  languages = [
    {"code": "JA", "name": "日本語"},
    {"code": "EN", "name": "English"},
    {"code": "ZH", "name": "中文"},
    {"code": "KO", "name": "한국어"},
    {"code": "FR", "name": "Français"},
    {"code": "DE", "name": "Deutsch"},
    {"code": "ES", "name": "Español"},
    {"code": "IT", "name": "Italiano"},
  ]
  return ApiResponse(status="ok", data=languages)

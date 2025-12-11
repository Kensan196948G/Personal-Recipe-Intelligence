"""
画像認識APIルーター - 食材画像認識エンドポイント
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.services.image_recognition_service import get_image_recognition_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai/image", tags=["image-recognition"])


# リクエスト・レスポンスモデル
class RecognitionResult(BaseModel):
  """認識結果"""

  ingredient_id: str = Field(..., description="食材ID")
  name: str = Field(..., description="食材名（日本語）")
  name_en: str = Field(..., description="食材名（英語）")
  category: str = Field(..., description="カテゴリ")
  confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度スコア")
  keywords: List[str] = Field(default_factory=list, description="キーワード")


class RecognitionResponse(BaseModel):
  """認識レスポンス"""

  status: str = Field(default="ok")
  data: Optional[List[RecognitionResult]] = None
  error: Optional[str] = None
  meta: Optional[dict] = None


class RecognitionRequest(BaseModel):
  """Base64画像認識リクエスト"""

  image_base64: str = Field(..., description="Base64エンコード画像")
  max_results: int = Field(default=5, ge=1, le=20, description="最大結果数")


class URLRecognitionRequest(BaseModel):
  """URL画像認識リクエスト"""

  image_url: str = Field(..., description="画像URL")
  max_results: int = Field(default=5, ge=1, le=20, description="最大結果数")


class FeedbackRequest(BaseModel):
  """フィードバックリクエスト"""

  image_hash: str = Field(..., description="画像ハッシュ")
  correct_ingredients: List[str] = Field(..., description="正しい食材IDリスト")
  incorrect_ingredients: List[str] = Field(
    default_factory=list, description="誤った食材IDリスト"
  )
  comment: Optional[str] = Field(None, description="コメント")


class RecognitionHistory(BaseModel):
  """認識履歴"""

  id: str
  timestamp: datetime
  image_hash: str
  results: List[RecognitionResult]
  feedback: Optional[dict] = None


# 認識履歴保存（メモリ内、本番環境ではDB使用）
recognition_history: List[RecognitionHistory] = []


@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_image(request: RecognitionRequest):
  """
  Base64画像から食材認識

  Args:
    request: Base64画像データとオプション

  Returns:
    認識結果
  """
  try:
    service = get_image_recognition_service()

    # Base64から認識
    results = service.recognize_from_base64(
      request.image_base64, max_results=request.max_results
    )

    # 認識結果を履歴に保存
    history_entry = RecognitionHistory(
      id=f"rec_{datetime.now().timestamp()}",
      timestamp=datetime.now(),
      image_hash="",  # Base64から計算可能だが省略
      results=[RecognitionResult(**r) for r in results],
    )
    recognition_history.append(history_entry)

    return RecognitionResponse(
      status="ok",
      data=[RecognitionResult(**r) for r in results],
      meta={
        "mode": service.mode,
        "max_results": request.max_results,
        "total_found": len(results),
      },
    )

  except Exception as e:
    logger.error(f"Image recognition failed: {e}")
    return RecognitionResponse(status="error", error=str(e))


@router.post("/recognize-file", response_model=RecognitionResponse)
async def recognize_image_file(
  file: UploadFile = File(...), max_results: int = 5
):
  """
  アップロードファイルから食材認識

  Args:
    file: アップロード画像ファイル
    max_results: 最大結果数

  Returns:
    認識結果
  """
  try:
    # ファイル保存
    upload_dir = Path("data/uploads/images")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{datetime.now().timestamp()}_{file.filename}"
    with open(file_path, "wb") as f:
      content = await file.read()
      f.write(content)

    # 認識実行
    service = get_image_recognition_service()
    results = service.recognize_from_file(file_path, max_results=max_results)

    # 履歴保存
    history_entry = RecognitionHistory(
      id=f"rec_{datetime.now().timestamp()}",
      timestamp=datetime.now(),
      image_hash=str(file_path),
      results=[RecognitionResult(**r) for r in results],
    )
    recognition_history.append(history_entry)

    return RecognitionResponse(
      status="ok",
      data=[RecognitionResult(**r) for r in results],
      meta={
        "mode": service.mode,
        "max_results": max_results,
        "total_found": len(results),
        "file_path": str(file_path),
      },
    )

  except Exception as e:
    logger.error(f"File recognition failed: {e}")
    return RecognitionResponse(status="error", error=str(e))


@router.post("/recognize-url", response_model=RecognitionResponse)
async def recognize_image_url(request: URLRecognitionRequest):
  """
  URL画像から食材認識

  Args:
    request: 画像URLとオプション

  Returns:
    認識結果
  """
  try:
    service = get_image_recognition_service()

    # URL画像認識
    results = service.recognize_from_url(
      request.image_url, max_results=request.max_results
    )

    # 履歴保存
    history_entry = RecognitionHistory(
      id=f"rec_{datetime.now().timestamp()}",
      timestamp=datetime.now(),
      image_hash=request.image_url,
      results=[RecognitionResult(**r) for r in results],
    )
    recognition_history.append(history_entry)

    return RecognitionResponse(
      status="ok",
      data=[RecognitionResult(**r) for r in results],
      meta={
        "mode": service.mode,
        "max_results": request.max_results,
        "total_found": len(results),
        "source_url": request.image_url,
      },
    )

  except Exception as e:
    logger.error(f"URL recognition failed: {e}")
    return RecognitionResponse(status="error", error=str(e))


@router.get("/history", response_model=RecognitionResponse)
async def get_recognition_history(limit: int = 20, offset: int = 0):
  """
  認識履歴取得

  Args:
    limit: 取得件数
    offset: オフセット

  Returns:
    認識履歴リスト
  """
  try:
    # 最新順にソート
    sorted_history = sorted(
      recognition_history, key=lambda x: x.timestamp, reverse=True
    )
    paginated = sorted_history[offset : offset + limit]

    return RecognitionResponse(
      status="ok",
      data=None,  # 履歴はmetaに含める
      meta={
        "history": [h.dict() for h in paginated],
        "total": len(recognition_history),
        "limit": limit,
        "offset": offset,
      },
    )

  except Exception as e:
    logger.error(f"Failed to get history: {e}")
    return RecognitionResponse(status="error", error=str(e))


@router.post("/feedback", response_model=RecognitionResponse)
async def submit_feedback(request: FeedbackRequest):
  """
  認識結果フィードバック送信

  Args:
    request: フィードバックデータ

  Returns:
    処理結果
  """
  try:
    # 該当する履歴を検索
    target_history = None
    for history in recognition_history:
      if history.image_hash == request.image_hash:
        target_history = history
        break

    if not target_history:
      raise HTTPException(status_code=404, detail="Recognition history not found")

    # フィードバック保存
    target_history.feedback = {
      "correct_ingredients": request.correct_ingredients,
      "incorrect_ingredients": request.incorrect_ingredients,
      "comment": request.comment,
      "submitted_at": datetime.now().isoformat(),
    }

    logger.info(f"Feedback submitted for image: {request.image_hash}")

    return RecognitionResponse(
      status="ok",
      data=None,
      meta={"message": "Feedback submitted successfully"},
    )

  except HTTPException:
    raise
  except Exception as e:
    logger.error(f"Failed to submit feedback: {e}")
    return RecognitionResponse(status="error", error=str(e))


@router.get("/ingredients/{ingredient_id}", response_model=RecognitionResponse)
async def get_ingredient_info(ingredient_id: str):
  """
  食材情報取得

  Args:
    ingredient_id: 食材ID

  Returns:
    食材情報
  """
  try:
    service = get_image_recognition_service()
    info = service.get_ingredient_info(ingredient_id)

    if not info:
      raise HTTPException(status_code=404, detail="Ingredient not found")

    return RecognitionResponse(status="ok", data=None, meta={"ingredient": info})

  except HTTPException:
    raise
  except Exception as e:
    logger.error(f"Failed to get ingredient info: {e}")
    return RecognitionResponse(status="error", error=str(e))


@router.get("/ingredients", response_model=RecognitionResponse)
async def search_ingredients(query: str, category: Optional[str] = None):
  """
  食材検索

  Args:
    query: 検索クエリ
    category: カテゴリフィルター

  Returns:
    検索結果
  """
  try:
    service = get_image_recognition_service()
    results = service.search_ingredients(query=query, category=category)

    return RecognitionResponse(
      status="ok",
      data=None,
      meta={
        "ingredients": results,
        "total": len(results),
        "query": query,
        "category": category,
      },
    )

  except Exception as e:
    logger.error(f"Failed to search ingredients: {e}")
    return RecognitionResponse(status="error", error=str(e))


@router.get("/categories", response_model=RecognitionResponse)
async def get_categories():
  """
  カテゴリ一覧取得

  Returns:
    カテゴリリスト
  """
  try:
    service = get_image_recognition_service()
    categories = service.get_categories()

    return RecognitionResponse(
      status="ok", data=None, meta={"categories": categories, "total": len(categories)}
    )

  except Exception as e:
    logger.error(f"Failed to get categories: {e}")
    return RecognitionResponse(status="error", error=str(e))

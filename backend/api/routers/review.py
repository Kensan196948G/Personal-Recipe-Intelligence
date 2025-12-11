"""
Review API router for Personal Recipe Intelligence.
レビュー・評価機能のAPIエンドポイント
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from backend.services.review_service import ReviewService


router = APIRouter(prefix="/api/v1/review", tags=["review"])
review_service = ReviewService()


# Request models
class CreateReviewRequest(BaseModel):
  """レビュー作成リクエスト"""
  rating: int = Field(..., ge=1, le=5, description="評価（1-5）")
  comment: str = Field(..., min_length=1, max_length=2000, description="コメント")


class UpdateReviewRequest(BaseModel):
  """レビュー更新リクエスト"""
  rating: Optional[int] = Field(None, ge=1, le=5, description="評価（1-5）")
  comment: Optional[str] = Field(None, min_length=1, max_length=2000, description="コメント")


class MarkHelpfulRequest(BaseModel):
  """役に立ったマークリクエスト"""
  helpful: bool = Field(..., description="True: マーク、False: マーク解除")


# Response models
class ReviewResponse(BaseModel):
  """レビューレスポンス"""
  id: str
  recipe_id: str
  user_id: str
  rating: int
  comment: str
  helpful_count: int
  is_helpful: bool = False  # 現在のユーザーがマークしているか
  created_at: str
  updated_at: Optional[str]


class RatingSummaryResponse(BaseModel):
  """評価サマリーレスポンス"""
  recipe_id: str
  average_rating: float
  total_reviews: int
  rating_distribution: dict[int, int]


class ApiResponse(BaseModel):
  """API標準レスポンス"""
  status: str
  data: Optional[dict] = None
  error: Optional[str] = None


def get_user_id_from_header(authorization: Optional[str] = Header(None)) -> str:
  """
  ヘッダーからユーザーIDを取得（簡易実装）

  Args:
      authorization: Authorizationヘッダー

  Returns:
      ユーザーID

  Raises:
      HTTPException: 認証情報がない場合
  """
  if not authorization:
    raise HTTPException(status_code=401, detail="Authorization header required")

  # 簡易実装: Bearer {user_id}
  parts = authorization.split()
  if len(parts) != 2 or parts[0].lower() != "bearer":
    raise HTTPException(status_code=401, detail="Invalid authorization format")

  return parts[1]


@router.post("/recipe/{recipe_id}")
async def create_review(
  recipe_id: str,
  request: CreateReviewRequest,
  authorization: Optional[str] = Header(None)
) -> ApiResponse:
  """
  レシピにレビューを投稿

  Args:
      recipe_id: レシピID
      request: レビュー作成リクエスト
      authorization: 認証ヘッダー

  Returns:
      作成されたレビュー
  """
  try:
    user_id = get_user_id_from_header(authorization)
    review = review_service.create_review(
      recipe_id=recipe_id,
      user_id=user_id,
      rating=request.rating,
      comment=request.comment
    )

    return ApiResponse(
      status="ok",
      data={
        "review": {
          "id": review.id,
          "recipe_id": review.recipe_id,
          "user_id": review.user_id,
          "rating": review.rating,
          "comment": review.comment,
          "helpful_count": review.helpful_count,
          "is_helpful": False,
          "created_at": review.created_at.isoformat(),
          "updated_at": review.updated_at.isoformat() if review.updated_at else None
        }
      }
    )
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")


@router.get("/recipe/{recipe_id}")
async def get_recipe_reviews(
  recipe_id: str,
  sort_by: str = "recent",
  limit: Optional[int] = None,
  authorization: Optional[str] = Header(None)
) -> ApiResponse:
  """
  レシピのレビュー一覧を取得

  Args:
      recipe_id: レシピID
      sort_by: ソート方法（recent/rating/helpful）
      limit: 取得件数制限
      authorization: 認証ヘッダー（オプション）

  Returns:
      レビュー一覧と評価サマリー
  """
  try:
    # ユーザーIDを取得（認証オプション）
    current_user_id = None
    if authorization:
      try:
        current_user_id = get_user_id_from_header(authorization)
      except HTTPException:
        pass

    # レビュー一覧取得
    reviews = review_service.get_recipe_reviews(recipe_id, sort_by, limit)

    # 評価サマリー取得
    summary = review_service.get_recipe_rating_summary(recipe_id)

    # レスポンス構築
    review_list = []
    for review in reviews:
      is_helpful = current_user_id in review.helpful_users if current_user_id else False
      review_list.append({
        "id": review.id,
        "recipe_id": review.recipe_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "helpful_count": review.helpful_count,
        "is_helpful": is_helpful,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat() if review.updated_at else None
      })

    return ApiResponse(
      status="ok",
      data={
        "reviews": review_list,
        "summary": summary.to_dict()
      }
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get reviews: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_reviews(
  user_id: str,
  authorization: Optional[str] = Header(None)
) -> ApiResponse:
  """
  ユーザーのレビュー一覧を取得

  Args:
      user_id: ユーザーID
      authorization: 認証ヘッダー

  Returns:
      レビュー一覧
  """
  try:
    # 認証チェック（自分のレビューのみ取得可能）
    current_user_id = get_user_id_from_header(authorization)
    if current_user_id != user_id:
      raise HTTPException(status_code=403, detail="Permission denied")

    reviews = review_service.get_user_reviews(user_id)

    review_list = []
    for review in reviews:
      review_list.append({
        "id": review.id,
        "recipe_id": review.recipe_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "helpful_count": review.helpful_count,
        "is_helpful": False,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat() if review.updated_at else None
      })

    return ApiResponse(
      status="ok",
      data={"reviews": review_list}
    )
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get user reviews: {str(e)}")


@router.put("/{review_id}")
async def update_review(
  review_id: str,
  request: UpdateReviewRequest,
  authorization: Optional[str] = Header(None)
) -> ApiResponse:
  """
  レビューを編集

  Args:
      review_id: レビューID
      request: レビュー更新リクエスト
      authorization: 認証ヘッダー

  Returns:
      更新されたレビュー
  """
  try:
    user_id = get_user_id_from_header(authorization)

    review = review_service.update_review(
      review_id=review_id,
      user_id=user_id,
      rating=request.rating,
      comment=request.comment
    )

    return ApiResponse(
      status="ok",
      data={
        "review": {
          "id": review.id,
          "recipe_id": review.recipe_id,
          "user_id": review.user_id,
          "rating": review.rating,
          "comment": review.comment,
          "helpful_count": review.helpful_count,
          "is_helpful": user_id in review.helpful_users,
          "created_at": review.created_at.isoformat(),
          "updated_at": review.updated_at.isoformat() if review.updated_at else None
        }
      }
    )
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to update review: {str(e)}")


@router.delete("/{review_id}")
async def delete_review(
  review_id: str,
  authorization: Optional[str] = Header(None)
) -> ApiResponse:
  """
  レビューを削除

  Args:
      review_id: レビューID
      authorization: 認証ヘッダー

  Returns:
      削除成功メッセージ
  """
  try:
    user_id = get_user_id_from_header(authorization)
    review_service.delete_review(review_id, user_id)

    return ApiResponse(
      status="ok",
      data={"message": "Review deleted successfully"}
    )
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to delete review: {str(e)}")


@router.post("/{review_id}/helpful")
async def mark_helpful(
  review_id: str,
  request: MarkHelpfulRequest,
  authorization: Optional[str] = Header(None)
) -> ApiResponse:
  """
  レビューを「役に立った」としてマーク/解除

  Args:
      review_id: レビューID
      request: マークリクエスト
      authorization: 認証ヘッダー

  Returns:
      更新されたレビュー
  """
  try:
    user_id = get_user_id_from_header(authorization)

    if request.helpful:
      review = review_service.mark_helpful(review_id, user_id)
    else:
      review = review_service.unmark_helpful(review_id, user_id)

    return ApiResponse(
      status="ok",
      data={
        "review": {
          "id": review.id,
          "recipe_id": review.recipe_id,
          "user_id": review.user_id,
          "rating": review.rating,
          "comment": review.comment,
          "helpful_count": review.helpful_count,
          "is_helpful": user_id in review.helpful_users,
          "created_at": review.created_at.isoformat(),
          "updated_at": review.updated_at.isoformat() if review.updated_at else None
        }
      }
    )
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to mark helpful: {str(e)}")


@router.get("/recipe/{recipe_id}/summary")
async def get_rating_summary(recipe_id: str) -> ApiResponse:
  """
  レシピの評価サマリーを取得

  Args:
      recipe_id: レシピID

  Returns:
      評価サマリー
  """
  try:
    summary = review_service.get_recipe_rating_summary(recipe_id)

    return ApiResponse(
      status="ok",
      data={"summary": summary.to_dict()}
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get rating summary: {str(e)}")


@router.get("/recipe/{recipe_id}/popular")
async def get_popular_reviews(
  recipe_id: str,
  limit: int = 3
) -> ApiResponse:
  """
  人気レビューを取得

  Args:
      recipe_id: レシピID
      limit: 取得件数

  Returns:
      人気レビューリスト
  """
  try:
    reviews = review_service.get_popular_reviews(recipe_id, limit)

    review_list = []
    for review in reviews:
      review_list.append({
        "id": review.id,
        "recipe_id": review.recipe_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "helpful_count": review.helpful_count,
        "is_helpful": False,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat() if review.updated_at else None
      })

    return ApiResponse(
      status="ok",
      data={"reviews": review_list}
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get popular reviews: {str(e)}")

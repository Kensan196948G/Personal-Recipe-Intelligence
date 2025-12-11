"""
Review service for Personal Recipe Intelligence.
レビュー・評価機能のビジネスロジック
"""

import json
import html
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from backend.models.review import Review, RecipeRatingSummary


class ReviewService:
  """レビュー管理サービス"""

  def __init__(self, data_dir: str = "data/reviews"):
    """
    初期化

    Args:
        data_dir: レビューデータ保存ディレクトリ
    """
    self.data_dir = Path(data_dir)
    self.data_dir.mkdir(parents=True, exist_ok=True)
    self.reviews_file = self.data_dir / "reviews.json"
    self._ensure_data_file()

  def _ensure_data_file(self) -> None:
    """データファイルが存在しない場合は作成"""
    if not self.reviews_file.exists():
      self._save_reviews([])

  def _load_reviews(self) -> list[Review]:
    """レビューをファイルから読み込み"""
    try:
      with open(self.reviews_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Review.from_dict(item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
      return []

  def _save_reviews(self, reviews: list[Review]) -> None:
    """レビューをファイルに保存"""
    with open(self.reviews_file, "w", encoding="utf-8") as f:
      json.dump(
        [review.to_dict() for review in reviews],
        f,
        ensure_ascii=False,
        indent=2
      )

  def _sanitize_comment(self, comment: str) -> str:
    """
    コメントをサニタイズ（XSS対策）

    Args:
        comment: 元のコメント

    Returns:
        サニタイズされたコメント
    """
    # HTMLエスケープ
    sanitized = html.escape(comment)
    # 改行は許可
    sanitized = sanitized.replace("&#x0A;", "\n")
    # 最大文字数制限
    max_length = 2000
    if len(sanitized) > max_length:
      sanitized = sanitized[:max_length]
    return sanitized.strip()

  def create_review(
    self,
    recipe_id: str,
    user_id: str,
    rating: int,
    comment: str
  ) -> Review:
    """
    レビューを投稿

    Args:
        recipe_id: レシピID
        user_id: ユーザーID
        rating: 評価（1-5）
        comment: コメント

    Returns:
        作成されたレビュー

    Raises:
        ValueError: 評価が範囲外、または既にレビュー済みの場合
    """
    if not (1 <= rating <= 5):
      raise ValueError("Rating must be between 1 and 5")

    reviews = self._load_reviews()

    # 既にレビュー済みかチェック
    existing = next(
      (r for r in reviews if r.recipe_id == recipe_id and r.user_id == user_id),
      None
    )
    if existing:
      raise ValueError("User has already reviewed this recipe")

    # サニタイズ
    sanitized_comment = self._sanitize_comment(comment)

    # 新規レビュー作成
    review = Review(
      id=str(uuid4()),
      recipe_id=recipe_id,
      user_id=user_id,
      rating=rating,
      comment=sanitized_comment,
      helpful_count=0,
      helpful_users=[],
      created_at=datetime.now(),
      updated_at=None
    )

    reviews.append(review)
    self._save_reviews(reviews)

    return review

  def get_recipe_reviews(
    self,
    recipe_id: str,
    sort_by: str = "recent",
    limit: Optional[int] = None
  ) -> list[Review]:
    """
    レシピのレビュー一覧を取得

    Args:
        recipe_id: レシピID
        sort_by: ソート方法（recent/rating/helpful）
        limit: 取得件数制限

    Returns:
        レビューリスト
    """
    reviews = self._load_reviews()
    recipe_reviews = [r for r in reviews if r.recipe_id == recipe_id]

    # ソート
    if sort_by == "rating":
      recipe_reviews.sort(key=lambda x: (-x.rating, -x.created_at.timestamp()))
    elif sort_by == "helpful":
      recipe_reviews.sort(key=lambda x: (-x.helpful_count, -x.created_at.timestamp()))
    else:  # recent
      recipe_reviews.sort(key=lambda x: -x.created_at.timestamp())

    # 制限
    if limit:
      recipe_reviews = recipe_reviews[:limit]

    return recipe_reviews

  def get_user_reviews(self, user_id: str) -> list[Review]:
    """
    ユーザーのレビュー一覧を取得

    Args:
        user_id: ユーザーID

    Returns:
        レビューリスト
    """
    reviews = self._load_reviews()
    user_reviews = [r for r in reviews if r.user_id == user_id]
    user_reviews.sort(key=lambda x: -x.created_at.timestamp())
    return user_reviews

  def update_review(
    self,
    review_id: str,
    user_id: str,
    rating: Optional[int] = None,
    comment: Optional[str] = None
  ) -> Review:
    """
    レビューを編集

    Args:
        review_id: レビューID
        user_id: ユーザーID（権限確認用）
        rating: 新しい評価
        comment: 新しいコメント

    Returns:
        更新されたレビュー

    Raises:
        ValueError: レビューが見つからない、または権限がない場合
    """
    reviews = self._load_reviews()
    review = next((r for r in reviews if r.id == review_id), None)

    if not review:
      raise ValueError("Review not found")

    if review.user_id != user_id:
      raise ValueError("Permission denied")

    # 更新
    if rating is not None:
      if not (1 <= rating <= 5):
        raise ValueError("Rating must be between 1 and 5")
      review.rating = rating

    if comment is not None:
      review.comment = self._sanitize_comment(comment)

    review.updated_at = datetime.now()

    self._save_reviews(reviews)
    return review

  def delete_review(self, review_id: str, user_id: str) -> bool:
    """
    レビューを削除

    Args:
        review_id: レビューID
        user_id: ユーザーID（権限確認用）

    Returns:
        削除成功したかどうか

    Raises:
        ValueError: レビューが見つからない、または権限がない場合
    """
    reviews = self._load_reviews()
    review = next((r for r in reviews if r.id == review_id), None)

    if not review:
      raise ValueError("Review not found")

    if review.user_id != user_id:
      raise ValueError("Permission denied")

    reviews = [r for r in reviews if r.id != review_id]
    self._save_reviews(reviews)
    return True

  def mark_helpful(self, review_id: str, user_id: str) -> Review:
    """
    レビューを「役に立った」としてマーク

    Args:
        review_id: レビューID
        user_id: ユーザーID

    Returns:
        更新されたレビュー

    Raises:
        ValueError: レビューが見つからない、または既にマーク済みの場合
    """
    reviews = self._load_reviews()
    review = next((r for r in reviews if r.id == review_id), None)

    if not review:
      raise ValueError("Review not found")

    if user_id in review.helpful_users:
      raise ValueError("User has already marked this review as helpful")

    review.helpful_users.append(user_id)
    review.helpful_count = len(review.helpful_users)

    self._save_reviews(reviews)
    return review

  def unmark_helpful(self, review_id: str, user_id: str) -> Review:
    """
    レビューの「役に立った」マークを解除

    Args:
        review_id: レビューID
        user_id: ユーザーID

    Returns:
        更新されたレビュー

    Raises:
        ValueError: レビューが見つからない、またはマークされていない場合
    """
    reviews = self._load_reviews()
    review = next((r for r in reviews if r.id == review_id), None)

    if not review:
      raise ValueError("Review not found")

    if user_id not in review.helpful_users:
      raise ValueError("User has not marked this review as helpful")

    review.helpful_users.remove(user_id)
    review.helpful_count = len(review.helpful_users)

    self._save_reviews(reviews)
    return review

  def get_recipe_rating_summary(self, recipe_id: str) -> RecipeRatingSummary:
    """
    レシピの評価サマリーを取得

    Args:
        recipe_id: レシピID

    Returns:
        評価サマリー
    """
    reviews = self.get_recipe_reviews(recipe_id)

    if not reviews:
      return RecipeRatingSummary(
        recipe_id=recipe_id,
        average_rating=0.0,
        total_reviews=0,
        rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
      )

    # 平均評価計算
    total_rating = sum(r.rating for r in reviews)
    average_rating = total_rating / len(reviews)

    # 評価分布
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
      rating_distribution[review.rating] += 1

    return RecipeRatingSummary(
      recipe_id=recipe_id,
      average_rating=round(average_rating, 1),
      total_reviews=len(reviews),
      rating_distribution=rating_distribution
    )

  def get_popular_reviews(self, recipe_id: str, limit: int = 3) -> list[Review]:
    """
    人気レビューを取得（役に立った順）

    Args:
        recipe_id: レシピID
        limit: 取得件数

    Returns:
        人気レビューリスト
    """
    return self.get_recipe_reviews(recipe_id, sort_by="helpful", limit=limit)

"""
Tests for review service
レビューサービスのテスト
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from backend.services.review_service import ReviewService
from backend.models.review import Review


@pytest.fixture
def temp_data_dir():
  """一時データディレクトリを作成"""
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)


@pytest.fixture
def review_service(temp_data_dir):
  """テスト用レビューサービスを作成"""
  return ReviewService(data_dir=temp_data_dir)


class TestReviewService:
  """レビューサービスのテストクラス"""

  def test_create_review(self, review_service):
    """レビュー作成のテスト"""
    review = review_service.create_review(
      recipe_id="recipe1",
      user_id="user1",
      rating=5,
      comment="とても美味しかったです！"
    )

    assert review.recipe_id == "recipe1"
    assert review.user_id == "user1"
    assert review.rating == 5
    assert review.comment == "とても美味しかったです！"
    assert review.helpful_count == 0
    assert len(review.helpful_users) == 0
    assert review.id is not None

  def test_create_review_invalid_rating(self, review_service):
    """無効な評価でのレビュー作成テスト"""
    with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
      review_service.create_review(
        recipe_id="recipe1",
        user_id="user1",
        rating=6,
        comment="Test"
      )

    with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
      review_service.create_review(
        recipe_id="recipe1",
        user_id="user1",
        rating=0,
        comment="Test"
      )

  def test_create_duplicate_review(self, review_service):
    """重複レビュー作成のテスト"""
    review_service.create_review(
      recipe_id="recipe1",
      user_id="user1",
      rating=5,
      comment="First review"
    )

    with pytest.raises(ValueError, match="already reviewed"):
      review_service.create_review(
        recipe_id="recipe1",
        user_id="user1",
        rating=4,
        comment="Second review"
      )

  def test_sanitize_comment(self, review_service):
    """コメントサニタイズのテスト"""
    review = review_service.create_review(
      recipe_id="recipe1",
      user_id="user1",
      rating=5,
      comment="<script>alert('XSS')</script>美味しい"
    )

    assert "<script>" not in review.comment
    assert "&lt;script&gt;" in review.comment

  def test_get_recipe_reviews(self, review_service):
    """レシピのレビュー一覧取得テスト"""
    # 複数のレビューを作成
    review_service.create_review("recipe1", "user1", 5, "Great!")
    review_service.create_review("recipe1", "user2", 4, "Good")
    review_service.create_review("recipe1", "user3", 3, "OK")
    review_service.create_review("recipe2", "user1", 5, "Other recipe")

    reviews = review_service.get_recipe_reviews("recipe1")
    assert len(reviews) == 3

    # recipe2のレビューは含まれていないことを確認
    recipe_ids = [r.recipe_id for r in reviews]
    assert all(rid == "recipe1" for rid in recipe_ids)

  def test_get_recipe_reviews_sort_by_rating(self, review_service):
    """評価順ソートのテスト"""
    review_service.create_review("recipe1", "user1", 3, "OK")
    review_service.create_review("recipe1", "user2", 5, "Great!")
    review_service.create_review("recipe1", "user3", 4, "Good")

    reviews = review_service.get_recipe_reviews("recipe1", sort_by="rating")
    ratings = [r.rating for r in reviews]
    assert ratings == [5, 4, 3]

  def test_get_recipe_reviews_with_limit(self, review_service):
    """取得件数制限のテスト"""
    for i in range(10):
      review_service.create_review("recipe1", f"user{i}", 5, f"Comment {i}")

    reviews = review_service.get_recipe_reviews("recipe1", limit=3)
    assert len(reviews) == 3

  def test_get_user_reviews(self, review_service):
    """ユーザーのレビュー一覧取得テスト"""
    review_service.create_review("recipe1", "user1", 5, "Great!")
    review_service.create_review("recipe2", "user1", 4, "Good")
    review_service.create_review("recipe3", "user2", 5, "Other user")

    reviews = review_service.get_user_reviews("user1")
    assert len(reviews) == 2
    assert all(r.user_id == "user1" for r in reviews)

  def test_update_review(self, review_service):
    """レビュー更新のテスト"""
    review = review_service.create_review("recipe1", "user1", 5, "Great!")

    updated = review_service.update_review(
      review_id=review.id,
      user_id="user1",
      rating=4,
      comment="Good but not great"
    )

    assert updated.rating == 4
    assert updated.comment == "Good but not great"
    assert updated.updated_at is not None

  def test_update_review_unauthorized(self, review_service):
    """権限のないレビュー更新のテスト"""
    review = review_service.create_review("recipe1", "user1", 5, "Great!")

    with pytest.raises(ValueError, match="Permission denied"):
      review_service.update_review(
        review_id=review.id,
        user_id="user2",
        rating=4
      )

  def test_update_review_not_found(self, review_service):
    """存在しないレビュー更新のテスト"""
    with pytest.raises(ValueError, match="Review not found"):
      review_service.update_review(
        review_id="nonexistent",
        user_id="user1",
        rating=4
      )

  def test_delete_review(self, review_service):
    """レビュー削除のテスト"""
    review = review_service.create_review("recipe1", "user1", 5, "Great!")

    result = review_service.delete_review(review.id, "user1")
    assert result is True

    reviews = review_service.get_recipe_reviews("recipe1")
    assert len(reviews) == 0

  def test_delete_review_unauthorized(self, review_service):
    """権限のないレビュー削除のテスト"""
    review = review_service.create_review("recipe1", "user1", 5, "Great!")

    with pytest.raises(ValueError, match="Permission denied"):
      review_service.delete_review(review.id, "user2")

  def test_mark_helpful(self, review_service):
    """役に立ったマークのテスト"""
    review = review_service.create_review("recipe1", "user1", 5, "Great!")

    updated = review_service.mark_helpful(review.id, "user2")
    assert updated.helpful_count == 1
    assert "user2" in updated.helpful_users

  def test_mark_helpful_duplicate(self, review_service):
    """重複の役に立ったマークのテスト"""
    review = review_service.create_review("recipe1", "user1", 5, "Great!")
    review_service.mark_helpful(review.id, "user2")

    with pytest.raises(ValueError, match="already marked"):
      review_service.mark_helpful(review.id, "user2")

  def test_unmark_helpful(self, review_service):
    """役に立ったマーク解除のテスト"""
    review = review_service.create_review("recipe1", "user1", 5, "Great!")
    review_service.mark_helpful(review.id, "user2")

    updated = review_service.unmark_helpful(review.id, "user2")
    assert updated.helpful_count == 0
    assert "user2" not in updated.helpful_users

  def test_get_recipe_rating_summary(self, review_service):
    """評価サマリー取得のテスト"""
    review_service.create_review("recipe1", "user1", 5, "Great!")
    review_service.create_review("recipe1", "user2", 4, "Good")
    review_service.create_review("recipe1", "user3", 5, "Excellent!")
    review_service.create_review("recipe1", "user4", 3, "OK")

    summary = review_service.get_recipe_rating_summary("recipe1")

    assert summary.recipe_id == "recipe1"
    assert summary.total_reviews == 4
    assert summary.average_rating == 4.2
    assert summary.rating_distribution[5] == 2
    assert summary.rating_distribution[4] == 1
    assert summary.rating_distribution[3] == 1
    assert summary.rating_distribution[2] == 0
    assert summary.rating_distribution[1] == 0

  def test_get_recipe_rating_summary_no_reviews(self, review_service):
    """レビューなしの評価サマリーテスト"""
    summary = review_service.get_recipe_rating_summary("recipe1")

    assert summary.recipe_id == "recipe1"
    assert summary.total_reviews == 0
    assert summary.average_rating == 0.0
    assert all(count == 0 for count in summary.rating_distribution.values())

  def test_get_popular_reviews(self, review_service):
    """人気レビュー取得のテスト"""
    review1 = review_service.create_review("recipe1", "user1", 5, "Great!")
    review2 = review_service.create_review("recipe1", "user2", 4, "Good")
    review3 = review_service.create_review("recipe1", "user3", 5, "Excellent!")

    # 役に立ったマークを追加
    review_service.mark_helpful(review2.id, "user4")
    review_service.mark_helpful(review2.id, "user5")
    review_service.mark_helpful(review3.id, "user4")

    popular = review_service.get_popular_reviews("recipe1", limit=2)

    assert len(popular) == 2
    assert popular[0].id == review2.id  # 2 helpful
    assert popular[1].id == review3.id  # 1 helpful

  def test_comment_max_length(self, review_service):
    """コメント最大文字数のテスト"""
    long_comment = "a" * 3000
    review = review_service.create_review(
      recipe_id="recipe1",
      user_id="user1",
      rating=5,
      comment=long_comment
    )

    # 2000文字に制限されることを確認
    assert len(review.comment) == 2000

  def test_persistence(self, review_service):
    """永続化のテスト"""
    review = review_service.create_review("recipe1", "user1", 5, "Great!")

    # 新しいサービスインスタンスを作成
    new_service = ReviewService(data_dir=review_service.data_dir)
    reviews = new_service.get_recipe_reviews("recipe1")

    assert len(reviews) == 1
    assert reviews[0].id == review.id
    assert reviews[0].rating == review.rating
    assert reviews[0].comment == review.comment

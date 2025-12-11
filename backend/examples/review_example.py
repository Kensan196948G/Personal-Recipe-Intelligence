"""
Example usage of review service
レビューサービスの使用例
"""

from backend.services.review_service import ReviewService


def main():
  """レビュー機能のデモ"""
  print("=== Personal Recipe Intelligence - Review Example ===\n")

  # サービスの初期化
  service = ReviewService(data_dir="data/reviews")
  print("✓ Review service initialized\n")

  # レシピID
  recipe_id = "recipe_001"

  # 1. レビューの投稿
  print("1. Creating reviews...")
  reviews_data = [
    ("user_alice", 5, "このレシピは最高です！家族みんなが喜んでくれました。"),
    ("user_bob", 4, "美味しかったですが、少し時間がかかりました。"),
    ("user_charlie", 5, "簡単で美味しい！リピート確定です。"),
    ("user_diana", 3, "まあまあでした。もう少し味付けを濃くしても良いかも。"),
    ("user_eve", 5, "素晴らしいレシピ！写真通りに作れました。")
  ]

  for user_id, rating, comment in reviews_data:
    try:
      review = service.create_review(
        recipe_id=recipe_id,
        user_id=user_id,
        rating=rating,
        comment=comment
      )
      print(f"  ✓ {user_id}: {rating}★ - {comment[:30]}...")
    except ValueError as e:
      print(f"  ✗ {user_id}: {e}")

  print()

  # 2. 評価サマリーの取得
  print("2. Rating Summary:")
  summary = service.get_recipe_rating_summary(recipe_id)
  print(f"  Average Rating: {summary.average_rating} ★")
  print(f"  Total Reviews: {summary.total_reviews}")
  print("  Rating Distribution:")
  for star in range(5, 0, -1):
    count = summary.rating_distribution[star]
    bar = "█" * count
    print(f"    {star}★: {bar} ({count})")
  print()

  # 3. レビュー一覧の取得（評価順）
  print("3. Reviews (sorted by rating):")
  reviews = service.get_recipe_reviews(recipe_id, sort_by="rating", limit=3)
  for i, review in enumerate(reviews, 1):
    print(f"  {i}. {review.user_id} - {review.rating}★")
    print(f"     {review.comment[:50]}...")
    print(f"     Helpful: {review.helpful_count}")
    print()

  # 4. 役に立ったマークの追加
  print("4. Marking reviews as helpful...")
  if len(reviews) >= 2:
    # 最初のレビューに複数のユーザーがマーク
    for user in ["user_fan1", "user_fan2", "user_fan3"]:
      service.mark_helpful(reviews[0].id, user)
      print(f"  ✓ {user} marked review by {reviews[0].user_id} as helpful")

    # 2番目のレビューに1人がマーク
    service.mark_helpful(reviews[1].id, "user_fan1")
    print(f"  ✓ user_fan1 marked review by {reviews[1].user_id} as helpful")
  print()

  # 5. 人気レビューの取得
  print("5. Popular Reviews:")
  popular = service.get_popular_reviews(recipe_id, limit=3)
  for i, review in enumerate(popular, 1):
    print(f"  {i}. {review.user_id} - {review.rating}★ ({review.helpful_count} helpful)")
    print(f"     {review.comment[:50]}...")
    print()

  # 6. レビューの編集
  print("6. Updating a review...")
  if reviews:
    updated = service.update_review(
      review_id=reviews[0].id,
      user_id=reviews[0].user_id,
      comment=reviews[0].comment + "\n\n【追記】何度作っても美味しいです！"
    )
    print(f"  ✓ Updated review by {updated.user_id}")
    print(f"    New comment: {updated.comment[:80]}...")
    print()

  # 7. ユーザーのレビュー一覧
  print("7. User's reviews (user_alice):")
  user_reviews = service.get_user_reviews("user_alice")
  for review in user_reviews:
    print(f"  Recipe: {review.recipe_id}")
    print(f"  Rating: {review.rating}★")
    print(f"  Comment: {review.comment[:50]}...")
    print(f"  Created: {review.created_at.strftime('%Y-%m-%d %H:%M')}")
    if review.updated_at:
      print(f"  Updated: {review.updated_at.strftime('%Y-%m-%d %H:%M')}")
    print()

  # 8. XSS対策のデモ
  print("8. XSS Protection Demo:")
  xss_review = service.create_review(
    recipe_id="recipe_002",
    user_id="user_hacker",
    rating=5,
    comment="<script>alert('XSS')</script>美味しい<b>太字</b>"
  )
  print("  Original: <script>alert('XSS')</script>美味しい<b>太字</b>")
  print(f"  Sanitized: {xss_review.comment}")
  print()

  # 9. 統計情報
  print("9. Statistics:")
  all_reviews = service.get_recipe_reviews(recipe_id)
  total_helpful = sum(r.helpful_count for r in all_reviews)
  avg_comment_length = sum(len(r.comment) for r in all_reviews) / len(all_reviews)

  print(f"  Total Reviews: {len(all_reviews)}")
  print(f"  Total Helpful Marks: {total_helpful}")
  print(f"  Average Comment Length: {avg_comment_length:.0f} characters")
  print(f"  Reviews with Updates: {sum(1 for r in all_reviews if r.updated_at)}")
  print()

  print("=== Demo completed successfully! ===")


if __name__ == "__main__":
  main()

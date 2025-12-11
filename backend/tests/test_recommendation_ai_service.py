"""
レシピ推薦AIサービスのテスト
"""

import pytest
from datetime import datetime, timedelta
import tempfile
import shutil

from backend.services.recommendation_ai_service import RecommendationAIService


@pytest.fixture
def temp_data_dir():
  """一時データディレクトリ"""
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)


@pytest.fixture
def service(temp_data_dir):
  """推薦サービスインスタンス"""
  return RecommendationAIService(data_dir=temp_data_dir)


@pytest.fixture
def sample_recipes():
  """サンプルレシピデータ"""
  return [
    {
      "id": "recipe_001",
      "title": "カレーライス",
      "category": "主菜",
      "tags": ["簡単", "人気"],
      "ingredients": [
        {"name": "じゃがいも", "amount": "2個"},
        {"name": "にんじん", "amount": "1本"},
        {"name": "玉ねぎ", "amount": "1個"},
      ],
      "cooking_time": 30,
      "difficulty": "easy",
    },
    {
      "id": "recipe_002",
      "title": "肉じゃが",
      "category": "主菜",
      "tags": ["和食", "定番"],
      "ingredients": [
        {"name": "じゃがいも", "amount": "3個"},
        {"name": "にんじん", "amount": "1本"},
        {"name": "牛肉", "amount": "200g"},
      ],
      "cooking_time": 40,
      "difficulty": "medium",
    },
    {
      "id": "recipe_003",
      "title": "サラダチキン",
      "category": "副菜",
      "tags": ["ヘルシー", "時短"],
      "ingredients": [
        {"name": "鶏むね肉", "amount": "1枚"},
      ],
      "cooking_time": 15,
      "difficulty": "easy",
    },
    {
      "id": "recipe_004",
      "title": "ペペロンチーノ",
      "category": "主食",
      "tags": ["イタリアン", "時短"],
      "ingredients": [
        {"name": "パスタ", "amount": "200g"},
        {"name": "にんにく", "amount": "2片"},
      ],
      "cooking_time": 20,
      "difficulty": "easy",
    },
    {
      "id": "recipe_005",
      "title": "麻婆豆腐",
      "category": "主菜",
      "tags": ["中華", "辛い"],
      "ingredients": [
        {"name": "豆腐", "amount": "1丁"},
        {"name": "豚ひき肉", "amount": "100g"},
      ],
      "cooking_time": 25,
      "difficulty": "medium",
    },
  ]


class TestRecommendationAIService:
  """推薦AIサービステスト"""

  def test_record_activity(self, service):
    """行動記録テスト"""
    service.record_activity(
      user_id="user_001",
      recipe_id="recipe_001",
      activity_type="viewed",
      metadata={"source": "search"},
    )

    activities = service._get_user_history("user_001")
    assert len(activities) == 1
    assert activities[0]["recipe_id"] == "recipe_001"
    assert activities[0]["activity_type"] == "viewed"
    assert activities[0]["metadata"]["source"] == "search"

  def test_multiple_activities(self, service):
    """複数行動記録テスト"""
    service.record_activity("user_001", "recipe_001", "viewed")
    service.record_activity("user_001", "recipe_001", "cooked")
    service.record_activity("user_001", "recipe_002", "favorited")

    activities = service._get_user_history("user_001")
    assert len(activities) == 3

  def test_personalized_recommendations_new_user(self, service, sample_recipes):
    """新規ユーザーへの推薦（トレンドベース）"""
    recommendations = service.get_personalized_recommendations(
      user_id="new_user", recipes=sample_recipes, limit=5
    )

    # 新規ユーザーにはトレンド推薦が返される
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5

  def test_personalized_recommendations_with_history(
    self, service, sample_recipes
  ):
    """履歴ありユーザーへのパーソナライズ推薦"""
    # ユーザー行動を記録
    service.record_activity("user_001", "recipe_001", "cooked")
    service.record_activity("user_001", "recipe_001", "favorited")
    service.record_activity("user_001", "recipe_002", "viewed")

    recommendations = service.get_personalized_recommendations(
      user_id="user_001", recipes=sample_recipes, limit=5
    )

    assert len(recommendations) > 0
    assert len(recommendations) <= 5

    # 各推薦にスコアと理由が含まれる
    for rec in recommendations:
      assert "recipe" in rec
      assert "score" in rec
      assert "reason" in rec
      assert "match_percentage" in rec
      assert 0 <= rec["match_percentage"] <= 100

  def test_similar_recipes(self, service, sample_recipes):
    """類似レシピ取得テスト"""
    similar_recipes = service.get_similar_recipes(
      recipe_id="recipe_001", recipes=sample_recipes, limit=3
    )

    assert len(similar_recipes) <= 3

    # recipe_001（カレーライス）と類似するのは recipe_002（肉じゃが）のはず
    # 両方とも主菜で、じゃがいも・にんじんを使用
    if len(similar_recipes) > 0:
      top_similar = similar_recipes[0]
      assert "recipe" in top_similar
      assert "similarity" in top_similar
      assert "match_percentage" in top_similar
      assert top_similar["recipe"]["id"] != "recipe_001"

  def test_similar_recipes_invalid_id(self, service, sample_recipes):
    """無効なレシピIDでの類似レシピ取得"""
    similar_recipes = service.get_similar_recipes(
      recipe_id="invalid_id", recipes=sample_recipes, limit=3
    )

    assert similar_recipes == []

  def test_trending_recommendations(self, service, sample_recipes):
    """トレンド推薦テスト"""
    # 複数ユーザーの行動を記録
    service.record_activity("user_001", "recipe_001", "viewed")
    service.record_activity("user_001", "recipe_001", "cooked")
    service.record_activity("user_002", "recipe_001", "viewed")
    service.record_activity("user_003", "recipe_002", "viewed")

    trending = service.get_trending_recommendations(
      recipes=sample_recipes, limit=5
    )

    assert len(trending) > 0
    assert len(trending) <= 5

    # recipe_001 が最もトレンドスコアが高いはず
    if len(trending) > 0:
      assert trending[0]["recipe"]["id"] == "recipe_001"

  def test_submit_feedback(self, service):
    """フィードバック記録テスト"""
    service.submit_feedback(
      user_id="user_001",
      recipe_id="recipe_001",
      feedback_type="interested",
      metadata={"context": "recommendation"},
    )

    feedback = service.feedback_data.get("user_001", [])
    assert len(feedback) == 1
    assert feedback[0]["recipe_id"] == "recipe_001"
    assert feedback[0]["feedback_type"] == "interested"

  def test_user_preferences(self, service, sample_recipes):
    """ユーザー嗜好分析テスト"""
    # 行動を記録
    service.record_activity("user_001", "recipe_001", "cooked")
    service.record_activity("user_001", "recipe_002", "cooked")
    service.record_activity("user_001", "recipe_005", "viewed")

    preferences = service.get_user_preferences(
      user_id="user_001", recipes=sample_recipes
    )

    assert preferences["user_id"] == "user_001"
    assert preferences["total_activities"] == 3
    assert len(preferences["favorite_ingredients"]) > 0
    assert len(preferences["favorite_categories"]) > 0
    assert preferences["cooking_frequency"] >= 0
    assert preferences["average_cooking_time"] >= 0

  def test_user_preferences_new_user(self, service, sample_recipes):
    """新規ユーザーの嗜好分析"""
    preferences = service.get_user_preferences(
      user_id="new_user", recipes=sample_recipes
    )

    assert preferences["user_id"] == "new_user"
    assert preferences["total_activities"] == 0
    assert preferences["favorite_ingredients"] == []
    assert preferences["favorite_categories"] == []

  def test_calculate_recipe_similarity(self, service, sample_recipes):
    """レシピ類似度計算テスト"""
    recipe1 = sample_recipes[0]  # カレーライス
    recipe2 = sample_recipes[1]  # 肉じゃが
    recipe3 = sample_recipes[2]  # サラダチキン

    similarity_1_2 = service._calculate_recipe_similarity(recipe1, recipe2)
    similarity_1_3 = service._calculate_recipe_similarity(recipe1, recipe3)

    # カレーと肉じゃがの方が、カレーとサラダチキンより類似度が高いはず
    assert similarity_1_2 > similarity_1_3
    assert 0.0 <= similarity_1_2 <= 1.0
    assert 0.0 <= similarity_1_3 <= 1.0

  def test_collaborative_filtering(self, service, sample_recipes):
    """協調フィルタリングテスト"""
    # ユーザー1と2が似た行動を取る
    service.record_activity("user_001", "recipe_001", "cooked")
    service.record_activity("user_001", "recipe_002", "cooked")

    service.record_activity("user_002", "recipe_001", "cooked")
    service.record_activity("user_002", "recipe_002", "cooked")
    service.record_activity("user_002", "recipe_003", "cooked")

    # user_001 に対する協調フィルタリングスコアを計算
    # user_002 が好きな recipe_003 が推薦されるはず
    score = service._calculate_collaborative_score(
      "user_001", "recipe_003", sample_recipes
    )

    assert score > 0.0

  def test_find_similar_users(self, service):
    """類似ユーザー検出テスト"""
    # 3人のユーザーの行動を記録
    service.record_activity("user_001", "recipe_001", "cooked")
    service.record_activity("user_001", "recipe_002", "cooked")

    service.record_activity("user_002", "recipe_001", "cooked")
    service.record_activity("user_002", "recipe_002", "cooked")

    service.record_activity("user_003", "recipe_003", "cooked")
    service.record_activity("user_003", "recipe_004", "cooked")

    similar_users = service._find_similar_users("user_001", top_n=2)

    # user_002 が最も類似しているはず
    assert len(similar_users) > 0
    assert similar_users[0][0] == "user_002"
    assert similar_users[0][1] > 0.0

  def test_content_based_filtering(self, service, sample_recipes):
    """コンテンツベースフィルタリングテスト"""
    # ユーザーが「主菜」カテゴリを好む
    service.record_activity("user_001", "recipe_001", "cooked")
    service.record_activity("user_001", "recipe_002", "cooked")

    user_history = service._get_user_history("user_001")

    # recipe_005（麻婆豆腐、主菜）のコンテンツスコアを計算
    score = service._calculate_content_score(
      "user_001", sample_recipes[4], user_history, sample_recipes
    )

    assert score > 0.0

  def test_diversity_penalty(self, service):
    """多様性ペナルティテスト"""
    # 直近に同じカテゴリを多く閲覧（カテゴリ情報を含む履歴を直接作成）
    from datetime import datetime

    user_history = [
      {
        "recipe_id": "recipe_001",
        "activity_type": "viewed",
        "timestamp": datetime.utcnow().isoformat(),
        "category": "主菜",
      },
      {
        "recipe_id": "recipe_002",
        "activity_type": "viewed",
        "timestamp": datetime.utcnow().isoformat(),
        "category": "主菜",
      },
    ]

    recipe_main = {"category": "主菜"}
    recipe_side = {"category": "副菜"}

    penalty_main = service._calculate_diversity_penalty(
      recipe_main, user_history
    )
    penalty_side = service._calculate_diversity_penalty(
      recipe_side, user_history
    )

    # 主菜の方がペナルティが高いはず
    assert penalty_main > penalty_side

  def test_is_already_interacted(self, service):
    """既交流チェックテスト"""
    service.record_activity("user_001", "recipe_001", "not_interested")

    # 却下済みレシピは True
    assert service._is_already_interacted("user_001", "recipe_001") is True

    # 未交流レシピは False
    assert service._is_already_interacted("user_001", "recipe_002") is False

  def test_ensure_diversity(self, service):
    """多様性確保テスト"""
    scored_recipes = [
      {"recipe": {"id": "1", "category": "主菜"}, "score": 0.9},
      {"recipe": {"id": "2", "category": "主菜"}, "score": 0.85},
      {"recipe": {"id": "3", "category": "主菜"}, "score": 0.8},
      {"recipe": {"id": "4", "category": "主菜"}, "score": 0.75},
      {"recipe": {"id": "5", "category": "副菜"}, "score": 0.7},
      {"recipe": {"id": "6", "category": "主食"}, "score": 0.65},
    ]

    diverse = service._ensure_diversity(scored_recipes, limit=5)

    # 多様性が確保されているか確認
    categories = [item["recipe"]["category"] for item in diverse]

    # 同じカテゴリは最大3つまで
    from collections import Counter
    category_counts = Counter(categories)
    for category, count in category_counts.items():
      assert count <= 3, f"{category}が{count}個あり、3個以上です"

    # 5件取得されていることを確認
    assert len(diverse) == 5

  def test_persistence(self, service, temp_data_dir):
    """データ永続化テスト"""
    service.record_activity("user_001", "recipe_001", "cooked")
    service.submit_feedback("user_001", "recipe_001", "interested")

    # 新しいサービスインスタンスを作成
    new_service = RecommendationAIService(data_dir=temp_data_dir)

    # データが永続化されているか確認
    activities = new_service._get_user_history("user_001")
    assert len(activities) == 2  # activity と feedback

    feedback = new_service.feedback_data.get("user_001", [])
    assert len(feedback) == 1

  def test_extract_recipe_features(self, service, sample_recipes):
    """レシピ特徴抽出テスト"""
    recipe = sample_recipes[0]
    features = service._extract_recipe_features(recipe)

    assert "ingredient:じゃがいも" in features
    assert "ingredient:にんじん" in features
    assert "category:主菜" in features
    assert "tag:簡単" in features
    assert "difficulty:easy" in features

  def test_cosine_similarity(self, service):
    """コサイン類似度テスト"""
    features1 = {"a": 1.0, "b": 2.0, "c": 3.0}
    features2 = {"a": 1.0, "b": 2.0, "c": 3.0}
    features3 = {"d": 1.0, "e": 2.0}

    # 同じ特徴ベクトル
    similarity_same = service._cosine_similarity(features1, features2)
    assert similarity_same == pytest.approx(1.0, rel=0.01)

    # 完全に異なる特徴ベクトル
    similarity_different = service._cosine_similarity(features1, features3)
    assert similarity_different == 0.0

  def test_get_user_rating_for_recipe(self, service):
    """ユーザー評価計算テスト"""
    service.record_activity("user_001", "recipe_001", "cooked")
    service.record_activity("user_001", "recipe_001", "favorited")
    service.record_activity("user_001", "recipe_001", "viewed")

    rating = service._get_user_rating_for_recipe("user_001", "recipe_001")

    # 評価は 0-1 の範囲
    assert 0.0 <= rating <= 1.0
    assert rating > 0.0  # 複数の行動があるのでスコアは正

  def test_generate_recommendation_reason(self, service, sample_recipes):
    """推薦理由生成テスト"""
    recipe = sample_recipes[0]  # カレーライス

    reason = service._generate_recommendation_reason(
      recipe, collab_score=0.8, content_score=0.75, trend_score=0.6
    )

    assert isinstance(reason, str)
    assert len(reason) > 0

  def test_is_recent(self, service):
    """日時判定テスト"""
    now = datetime.utcnow()
    recent = (now - timedelta(days=10)).isoformat()
    old = (now - timedelta(days=40)).isoformat()

    assert service._is_recent(recent, days=30) is True
    assert service._is_recent(old, days=30) is False

  def test_trend_score_calculation(self, service):
    """トレンドスコア計算テスト"""
    # 複数ユーザーが最近アクセス
    service.record_activity("user_001", "recipe_001", "viewed")
    service.record_activity("user_002", "recipe_001", "cooked")
    service.record_activity("user_003", "recipe_002", "viewed")

    score_001 = service._calculate_trend_score("recipe_001")
    score_002 = service._calculate_trend_score("recipe_002")
    score_003 = service._calculate_trend_score("recipe_003")

    # recipe_001 が最もトレンドスコアが高い
    assert score_001 > score_002
    assert score_002 > score_003
    assert 0.0 <= score_001 <= 1.0

  def test_empty_recipes_list(self, service):
    """空のレシピリスト処理"""
    recommendations = service.get_personalized_recommendations(
      user_id="user_001", recipes=[], limit=10
    )

    assert recommendations == []

  def test_limit_parameter(self, service, sample_recipes):
    """limit パラメータテスト"""
    recommendations = service.get_personalized_recommendations(
      user_id="new_user", recipes=sample_recipes, limit=3
    )

    assert len(recommendations) <= 3

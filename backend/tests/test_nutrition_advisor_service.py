"""
栄養士AI相談サービスのテスト
"""

import pytest
import json
from pathlib import Path

from backend.services.nutrition_advisor_service import NutritionAdvisorService


@pytest.fixture
def test_data_dir(tmp_path):
  """テスト用データディレクトリ"""
  return str(tmp_path / "test_advisor_data")


@pytest.fixture
def advisor_service(test_data_dir):
  """テスト用アドバイザーサービス"""
  return NutritionAdvisorService(data_dir=test_data_dir)


@pytest.fixture
def sample_user_id():
  """テスト用ユーザーID"""
  return "test-user-123"


class TestNutritionAdvisorService:
  """NutritionAdvisorService のテスト"""

  def test_service_initialization(self, advisor_service, test_data_dir):
    """サービスの初期化テスト"""
    assert advisor_service is not None
    assert Path(test_data_dir).exists()
    assert advisor_service.knowledge_base is not None
    assert advisor_service.quick_actions is not None
    assert len(advisor_service.quick_actions) > 0

  def test_chat_basic_greeting(self, advisor_service, sample_user_id):
    """基本的な挨拶のテスト"""
    result = advisor_service.chat(user_id=sample_user_id, message="こんにちは")

    assert result is not None
    assert "message" in result
    assert result["message"]["role"] == "assistant"
    assert len(result["message"]["content"]) > 0
    assert result["message"]["type"] == "greetings"

  def test_chat_protein_question(self, advisor_service, sample_user_id):
    """タンパク質に関する質問のテスト"""
    result = advisor_service.chat(
      user_id=sample_user_id, message="タンパク質について教えてください"
    )

    assert result is not None
    assert result["message"]["type"] == "protein"
    assert "タンパク質" in result["message"]["content"]
    assert len(result["message"]["tips"]) > 0

  def test_chat_carbohydrates_question(self, advisor_service, sample_user_id):
    """炭水化物に関する質問のテスト"""
    result = advisor_service.chat(
      user_id=sample_user_id, message="炭水化物はどのくらい摂ればいいですか"
    )

    assert result is not None
    assert result["message"]["type"] == "carbohydrates"
    assert "炭水化物" in result["message"]["content"]

  def test_chat_weight_loss_question(self, advisor_service, sample_user_id):
    """ダイエットに関する質問のテスト"""
    result = advisor_service.chat(user_id=sample_user_id, message="痩せたいです")

    assert result is not None
    assert result["message"]["type"] == "weight_loss"
    assert len(result["message"]["content"]) > 0

  def test_chat_unknown_question(self, advisor_service, sample_user_id):
    """未知の質問のテスト"""
    result = advisor_service.chat(
      user_id=sample_user_id, message="これは未知の質問です xyz123"
    )

    assert result is not None
    assert result["message"]["type"] == "unknown"

  def test_chat_history_saved(self, advisor_service, sample_user_id):
    """チャット履歴が保存されることのテスト"""
    # メッセージ送信
    advisor_service.chat(user_id=sample_user_id, message="こんにちは")

    # 履歴確認
    assert sample_user_id in advisor_service.chat_history
    history = advisor_service.chat_history[sample_user_id]
    assert len(history) == 2  # ユーザーメッセージ + アシスタント応答

  def test_get_chat_history(self, advisor_service, sample_user_id):
    """チャット履歴取得のテスト"""
    # 複数メッセージ送信
    advisor_service.chat(user_id=sample_user_id, message="こんにちは")
    advisor_service.chat(user_id=sample_user_id, message="タンパク質について教えてください")

    # 履歴取得
    result = advisor_service.get_chat_history(user_id=sample_user_id, limit=10)

    assert result is not None
    assert "history" in result
    assert result["total"] == 4  # 2往復
    assert len(result["history"]) == 4

  def test_get_chat_history_pagination(self, advisor_service, sample_user_id):
    """チャット履歴のページネーションテスト"""
    # 5往復分のメッセージ
    for i in range(5):
      advisor_service.chat(user_id=sample_user_id, message=f"質問{i}")

    # ページネーション
    result = advisor_service.get_chat_history(user_id=sample_user_id, limit=4, offset=0)

    assert result["total"] == 10
    assert len(result["history"]) == 4

  def test_clear_chat_history(self, advisor_service, sample_user_id):
    """チャット履歴クリアのテスト"""
    # メッセージ送信
    advisor_service.chat(user_id=sample_user_id, message="こんにちは")

    # 履歴クリア
    result = advisor_service.clear_chat_history(user_id=sample_user_id)

    assert result is True
    assert len(advisor_service.chat_history[sample_user_id]) == 0

  def test_clear_chat_history_nonexistent_user(self, advisor_service):
    """存在しないユーザーの履歴クリアテスト"""
    result = advisor_service.clear_chat_history(user_id="nonexistent-user")
    assert result is False

  def test_analyze_meal_basic(self, advisor_service, sample_user_id):
    """基本的な食事分析のテスト"""
    meal_data = {
      "meal_type": "lunch",
      "items": [
        {"recipe_id": "recipe-1", "servings": 1},
        {"recipe_id": "recipe-2", "servings": 1},
      ],
    }

    result = advisor_service.analyze_meal(user_id=sample_user_id, meal_data=meal_data)

    assert result is not None
    assert "nutrition" in result
    assert "advice" in result
    assert "score" in result
    assert 0 <= result["score"] <= 100

  def test_analyze_meal_breakfast(self, advisor_service, sample_user_id):
    """朝食分析のテスト"""
    meal_data = {"meal_type": "breakfast", "items": []}

    result = advisor_service.analyze_meal(user_id=sample_user_id, meal_data=meal_data)

    assert result is not None
    assert result["meal_type"] == "breakfast"
    assert isinstance(result["advice"], list)

  def test_get_daily_tip(self, advisor_service, sample_user_id):
    """今日のワンポイント取得のテスト"""
    result = advisor_service.get_daily_tip(user_id=sample_user_id)

    assert result is not None
    assert "date" in result
    assert "category" in result
    assert "title" in result
    assert "content" in result
    assert len(result["content"]) > 0

  def test_get_daily_tip_consistent(self, advisor_service, sample_user_id):
    """同じ日は同じワンポイントが返ることのテスト"""
    result1 = advisor_service.get_daily_tip(user_id=sample_user_id)
    result2 = advisor_service.get_daily_tip(user_id=sample_user_id)

    assert result1["category"] == result2["category"]
    assert result1["content"] == result2["content"]

  def test_generate_meal_plan_default(self, advisor_service, sample_user_id):
    """デフォルト食事プラン生成のテスト"""
    result = advisor_service.generate_meal_plan(user_id=sample_user_id, preferences={})

    assert result is not None
    assert "target_calories" in result
    assert "meals" in result
    assert "breakfast" in result["meals"]
    assert "lunch" in result["meals"]
    assert "dinner" in result["meals"]
    assert "snacks" in result["meals"]
    assert "hydration" in result
    assert "general_advice" in result

  def test_generate_meal_plan_with_target_calories(
    self, advisor_service, sample_user_id
  ):
    """カロリー指定付き食事プラン生成のテスト"""
    preferences = {"target_calories": 1800}

    result = advisor_service.generate_meal_plan(
      user_id=sample_user_id, preferences=preferences
    )

    assert result["target_calories"] == 1800
    assert "target_protein" in result
    assert "target_carbs" in result
    assert "target_fat" in result

  def test_generate_meal_plan_weight_loss_goal(self, advisor_service, sample_user_id):
    """減量目標での食事プラン生成のテスト"""
    preferences = {"goals": ["weight_loss"]}

    result = advisor_service.generate_meal_plan(
      user_id=sample_user_id, preferences=preferences
    )

    assert any("減量" in advice for advice in result["general_advice"])

  def test_generate_meal_plan_muscle_gain_goal(self, advisor_service, sample_user_id):
    """筋肉増強目標での食事プラン生成のテスト"""
    preferences = {"goals": ["muscle_gain"]}

    result = advisor_service.generate_meal_plan(
      user_id=sample_user_id, preferences=preferences
    )

    assert any("筋肉" in advice or "タンパク質" in advice for advice in result["general_advice"])

  def test_generate_meal_plan_with_restrictions(self, advisor_service, sample_user_id):
    """制限事項付き食事プラン生成のテスト"""
    preferences = {"restrictions": ["diabetes"]}

    result = advisor_service.generate_meal_plan(
      user_id=sample_user_id, preferences=preferences
    )

    assert any("血糖値" in advice or "糖尿病" in advice for advice in result["general_advice"])

  def test_update_user_profile(self, advisor_service, sample_user_id):
    """ユーザープロファイル更新のテスト"""
    profile_updates = {
      "preferences": {"favorite_foods": ["fish", "vegetables"]},
      "goals": ["weight_loss"],
      "restrictions": ["allergy"],
    }

    result = advisor_service.update_user_profile(
      user_id=sample_user_id, profile_updates=profile_updates
    )

    assert result is not None
    assert "preferences" in result
    assert "goals" in result
    assert "restrictions" in result
    assert result["goals"] == ["weight_loss"]
    assert result["restrictions"] == ["allergy"]

  def test_get_user_profile(self, advisor_service, sample_user_id):
    """ユーザープロファイル取得のテスト"""
    # プロファイルを作成
    advisor_service.update_user_profile(
      user_id=sample_user_id,
      profile_updates={"goals": ["muscle_gain"]},
    )

    # プロファイル取得
    result = advisor_service.get_user_profile(user_id=sample_user_id)

    assert result is not None
    assert "created_at" in result
    assert "goals" in result
    assert result["goals"] == ["muscle_gain"]

  def test_get_user_profile_nonexistent(self, advisor_service):
    """存在しないユーザープロファイル取得のテスト"""
    result = advisor_service.get_user_profile(user_id="nonexistent-user")
    assert result is None

  def test_personalized_response(self, advisor_service, sample_user_id):
    """パーソナライズされた応答のテスト"""
    # ユーザープロファイルを設定
    advisor_service.update_user_profile(
      user_id=sample_user_id,
      profile_updates={"goals": ["weight_loss"]},
    )

    # 炭水化物に関する質問
    result = advisor_service.chat(
      user_id=sample_user_id, message="炭水化物について教えてください"
    )

    # 減量目標が反映されているか確認
    assert "減量" in result["message"]["content"] or "カロリー" in result["message"]["content"]

  def test_meal_analysis_history(self, advisor_service, sample_user_id):
    """食事分析履歴が保存されることのテスト"""
    meal_data = {"meal_type": "lunch", "items": []}

    # 分析実行
    advisor_service.analyze_meal(user_id=sample_user_id, meal_data=meal_data)

    # プロファイルに履歴が保存されているか確認
    profile = advisor_service.get_user_profile(user_id=sample_user_id)
    assert "meal_analyses" in profile
    assert len(profile["meal_analyses"]) == 1

  def test_meal_analysis_history_limit(self, advisor_service, sample_user_id):
    """食事分析履歴が30件に制限されることのテスト"""
    meal_data = {"meal_type": "lunch", "items": []}

    # 35件の分析を実行
    for i in range(35):
      advisor_service.analyze_meal(user_id=sample_user_id, meal_data=meal_data)

    # 最新30件のみ保持されているか確認
    profile = advisor_service.get_user_profile(user_id=sample_user_id)
    assert len(profile["meal_analyses"]) == 30

  def test_knowledge_base_categories(self, advisor_service):
    """知識ベースに必要なカテゴリが存在することのテスト"""
    required_categories = [
      "greetings",
      "protein",
      "carbohydrates",
      "fat",
      "vitamins",
      "minerals",
      "weight_loss",
      "weight_gain",
      "allergies",
      "diabetes",
      "hydration",
      "meal_timing",
      "exercise",
      "sleep",
      "stress",
      "pregnancy",
      "elderly",
      "unknown",
    ]

    for category in required_categories:
      assert category in advisor_service.knowledge_base

  def test_quick_actions_structure(self, advisor_service):
    """クイックアクションの構造テスト"""
    for action in advisor_service.quick_actions:
      assert "id" in action
      assert "label" in action
      assert "message" in action
      assert len(action["label"]) > 0
      assert len(action["message"]) > 0

  def test_data_persistence(self, advisor_service, sample_user_id, test_data_dir):
    """データの永続化テスト"""
    # チャットメッセージ送信
    advisor_service.chat(user_id=sample_user_id, message="こんにちは")

    # ファイルが作成されているか確認
    chat_history_file = Path(test_data_dir) / "advisor_chat_history.json"
    assert chat_history_file.exists()

    # データを読み込んで確認
    with open(chat_history_file, "r", encoding="utf-8") as f:
      data = json.load(f)
      assert sample_user_id in data
      assert len(data[sample_user_id]) == 2

  def test_user_profile_persistence(self, advisor_service, sample_user_id, test_data_dir):
    """ユーザープロファイルの永続化テスト"""
    # プロファイル更新
    advisor_service.update_user_profile(
      user_id=sample_user_id,
      profile_updates={"goals": ["weight_loss"]},
    )

    # ファイルが作成されているか確認
    profiles_file = Path(test_data_dir) / "advisor_user_profiles.json"
    assert profiles_file.exists()

    # データを読み込んで確認
    with open(profiles_file, "r", encoding="utf-8") as f:
      data = json.load(f)
      assert sample_user_id in data
      assert data[sample_user_id]["goals"] == ["weight_loss"]

  def test_chat_history_limit(self, advisor_service, sample_user_id):
    """チャット履歴が100件に制限されることのテスト"""
    # 60往復（120メッセージ）送信
    for i in range(60):
      advisor_service.chat(user_id=sample_user_id, message=f"質問{i}")

    # 最新100件のみ保持されているか確認
    history = advisor_service.chat_history[sample_user_id]
    assert len(history) == 100

  def test_meal_score_calculation(self, advisor_service, sample_user_id):
    """食事スコア計算のテスト"""
    meal_data = {"meal_type": "lunch", "items": []}

    result = advisor_service.analyze_meal(user_id=sample_user_id, meal_data=meal_data)

    # スコアが0〜100の範囲内か確認
    assert 0 <= result["score"] <= 100
    assert isinstance(result["score"], (int, float))


if __name__ == "__main__":
  pytest.main([__file__, "-v"])

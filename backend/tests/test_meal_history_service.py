"""
食事履歴サービスのテスト
"""

import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from backend.services.meal_history_service import (
  MealHistoryService,
  MealRecord,
  DailyNutrition,
  NutritionTrend,
  TrendAnalysis,
)


@pytest.fixture
def temp_dir():
  """一時ディレクトリを作成"""
  temp = tempfile.mkdtemp()
  yield temp
  shutil.rmtree(temp)


@pytest.fixture
def service(temp_dir):
  """テスト用サービスインスタンス"""
  return MealHistoryService(data_dir=temp_dir)


@pytest.fixture
def sample_nutrition():
  """サンプル栄養情報"""
  return {
    "calories": 500.0,
    "protein": 20.0,
    "fat": 15.0,
    "carbohydrates": 60.0,
    "fiber": 5.0,
    "sodium": 800.0,
  }


@pytest.fixture
def sample_ingredients():
  """サンプル食材リスト"""
  return ["鶏肉", "玉ねぎ", "にんじん", "じゃがいも"]


class TestMealHistoryService:
  """食事履歴サービスのテスト"""

  def test_init_creates_data_directory(self, temp_dir):
    """初期化時にデータディレクトリが作成されることを確認"""
    service = MealHistoryService(data_dir=temp_dir)
    assert Path(temp_dir).exists()
    assert service.meal_history_file == Path(temp_dir) / "meal_history.json"

  def test_record_meal_creates_record(
    self, service, sample_nutrition, sample_ingredients
  ):
    """食事記録が正しく作成されることを確認"""
    record = service.record_meal(
      user_id="user123",
      recipe_id="recipe456",
      recipe_name="チキンカレー",
      meal_type="lunch",
      servings=2.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
    )

    assert isinstance(record, MealRecord)
    assert record.user_id == "user123"
    assert record.recipe_id == "recipe456"
    assert record.recipe_name == "チキンカレー"
    assert record.meal_type == "lunch"
    assert record.servings == 2.0
    assert record.nutrition == sample_nutrition
    assert record.ingredients == sample_ingredients
    assert record.id.startswith("user123_")

  def test_record_meal_saves_to_file(
    self, service, sample_nutrition, sample_ingredients
  ):
    """食事記録がファイルに保存されることを確認"""
    service.record_meal(
      user_id="user123",
      recipe_id="recipe456",
      recipe_name="チキンカレー",
      meal_type="lunch",
      servings=2.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
    )

    assert service.meal_history_file.exists()

    with open(service.meal_history_file, "r", encoding="utf-8") as f:
      data = json.load(f)

    assert len(data) == 1
    assert data[0]["recipe_name"] == "チキンカレー"

  def test_record_meal_with_custom_time(
    self, service, sample_nutrition, sample_ingredients
  ):
    """カスタム食事時刻で記録できることを確認"""
    custom_time = "2025-12-10T12:00:00"

    record = service.record_meal(
      user_id="user123",
      recipe_id="recipe456",
      recipe_name="チキンカレー",
      meal_type="lunch",
      servings=2.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
      consumed_at=custom_time,
    )

    assert record.consumed_at == custom_time

  def test_get_daily_nutrition_empty(self, service):
    """記録がない日の栄養摂取量を取得"""
    daily = service.get_daily_nutrition("user123", "2025-12-10")

    assert isinstance(daily, DailyNutrition)
    assert daily.date == "2025-12-10"
    assert daily.total_nutrition == {}
    assert daily.meals == []
    assert daily.meal_count == 0

  def test_get_daily_nutrition_with_records(
    self, service, sample_nutrition, sample_ingredients
  ):
    """記録がある日の栄養摂取量を取得"""
    # 2食分記録
    service.record_meal(
      user_id="user123",
      recipe_id="recipe1",
      recipe_name="朝食",
      meal_type="breakfast",
      servings=1.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
      consumed_at="2025-12-10T08:00:00",
    )

    service.record_meal(
      user_id="user123",
      recipe_id="recipe2",
      recipe_name="昼食",
      meal_type="lunch",
      servings=1.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
      consumed_at="2025-12-10T12:00:00",
    )

    daily = service.get_daily_nutrition("user123", "2025-12-10")

    assert daily.meal_count == 2
    assert daily.total_nutrition["calories"] == 1000.0  # 500 * 2
    assert daily.total_nutrition["protein"] == 40.0  # 20 * 2
    assert len(daily.meals) == 2

  def test_get_daily_nutrition_filters_by_user(
    self, service, sample_nutrition, sample_ingredients
  ):
    """ユーザー別にフィルタされることを確認"""
    service.record_meal(
      user_id="user123",
      recipe_id="recipe1",
      recipe_name="食事1",
      meal_type="lunch",
      servings=1.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
      consumed_at="2025-12-10T12:00:00",
    )

    service.record_meal(
      user_id="user456",
      recipe_id="recipe2",
      recipe_name="食事2",
      meal_type="lunch",
      servings=1.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
      consumed_at="2025-12-10T12:00:00",
    )

    daily = service.get_daily_nutrition("user123", "2025-12-10")

    assert daily.meal_count == 1
    assert daily.meals[0]["recipe_name"] == "食事1"

  def test_get_weekly_nutrition(self, service, sample_nutrition, sample_ingredients):
    """週間栄養摂取量を取得"""
    # 3日分記録
    for i in range(3):
      date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
      service.record_meal(
        user_id="user123",
        recipe_id=f"recipe{i}",
        recipe_name=f"食事{i}",
        meal_type="lunch",
        servings=1.0,
        nutrition=sample_nutrition,
        ingredients=sample_ingredients,
        consumed_at=f"{date}T12:00:00",
      )

    weekly = service.get_weekly_nutrition("user123")

    assert len(weekly) == 7
    assert all(isinstance(d, DailyNutrition) for d in weekly)

  def test_get_monthly_nutrition(self, service, sample_nutrition, sample_ingredients):
    """月間栄養摂取量を取得"""
    monthly = service.get_monthly_nutrition("user123", 2025, 12)

    assert len(monthly) == 31  # 12月は31日
    assert all(isinstance(d, DailyNutrition) for d in monthly)

  def test_get_nutrition_trend(self, service, sample_nutrition, sample_ingredients):
    """栄養素推移を取得"""
    # 5日分記録
    for i in range(5):
      date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
      nutrition = sample_nutrition.copy()
      nutrition["calories"] = 500.0 + (i * 100)  # カロリーを変化させる

      service.record_meal(
        user_id="user123",
        recipe_id=f"recipe{i}",
        recipe_name=f"食事{i}",
        meal_type="lunch",
        servings=1.0,
        nutrition=nutrition,
        ingredients=sample_ingredients,
        consumed_at=f"{date}T12:00:00",
      )

    trend = service.get_nutrition_trend("user123", "calories", days=5)

    assert isinstance(trend, NutritionTrend)
    assert trend.nutrient_name == "calories"
    assert len(trend.dates) == 5
    assert len(trend.values) == 5
    assert trend.average > 0
    assert trend.target == 2000.0

  def test_analyze_trends(self, service, sample_nutrition, sample_ingredients):
    """傾向分析を実行"""
    # 複数回同じレシピを記録
    for i in range(5):
      date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
      service.record_meal(
        user_id="user123",
        recipe_id="recipe1",
        recipe_name="チキンカレー",
        meal_type="lunch",
        servings=1.0,
        nutrition=sample_nutrition,
        ingredients=["鶏肉", "玉ねぎ", "カレールー"],
        consumed_at=f"{date}T12:00:00",
      )

    analysis = service.analyze_trends("user123", days=30)

    assert isinstance(analysis, TrendAnalysis)
    assert len(analysis.top_ingredients) > 0
    assert len(analysis.favorite_recipes) > 0
    assert "lunch" in analysis.meal_time_pattern
    assert len(analysis.nutrition_balance) > 0

  def test_analyze_trends_top_ingredients(
    self, service, sample_nutrition, sample_ingredients
  ):
    """よく使う食材が正しく集計されることを確認"""
    # 鶏肉を多く使う
    for i in range(3):
      date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
      service.record_meal(
        user_id="user123",
        recipe_id=f"recipe{i}",
        recipe_name=f"料理{i}",
        meal_type="lunch",
        servings=1.0,
        nutrition=sample_nutrition,
        ingredients=["鶏肉", "その他"],
        consumed_at=f"{date}T12:00:00",
      )

    analysis = service.analyze_trends("user123", days=30)

    # 鶏肉が最も多いはず
    assert analysis.top_ingredients[0][0] == "鶏肉"
    assert analysis.top_ingredients[0][1] == 3

  def test_nutrition_balance_evaluation(
    self, service, sample_nutrition, sample_ingredients
  ):
    """栄養バランス評価が正しく行われることを確認"""
    # 十分なカロリーを記録
    high_calorie = sample_nutrition.copy()
    high_calorie["calories"] = 2500.0

    for i in range(7):
      date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
      service.record_meal(
        user_id="user123",
        recipe_id=f"recipe{i}",
        recipe_name=f"食事{i}",
        meal_type="lunch",
        servings=1.0,
        nutrition=high_calorie,
        ingredients=sample_ingredients,
        consumed_at=f"{date}T12:00:00",
      )

    analysis = service.analyze_trends("user123", days=7)

    # カロリーは過剰のはず
    assert analysis.nutrition_balance["calories"] == "excessive"

  def test_get_nutrition_summary(self, service, sample_nutrition, sample_ingredients):
    """栄養摂取量サマリーを取得"""
    # 3日分記録
    for i in range(3):
      date = f"2025-12-{10+i:02d}"
      service.record_meal(
        user_id="user123",
        recipe_id=f"recipe{i}",
        recipe_name=f"食事{i}",
        meal_type="lunch",
        servings=1.0,
        nutrition=sample_nutrition,
        ingredients=sample_ingredients,
        consumed_at=f"{date}T12:00:00",
      )

    summary = service.get_nutrition_summary("user123", "2025-12-10", "2025-12-12")

    assert summary["period"]["days"] == 3
    assert summary["meal_count"] == 3
    assert summary["total"]["calories"] == 1500.0  # 500 * 3
    assert summary["average_per_day"]["calories"] == 500.0  # 1500 / 3
    assert "targets" in summary

  def test_multiple_users_isolation(
    self, service, sample_nutrition, sample_ingredients
  ):
    """複数ユーザーのデータが分離されることを確認"""
    # ユーザー1の記録
    service.record_meal(
      user_id="user1",
      recipe_id="recipe1",
      recipe_name="食事1",
      meal_type="lunch",
      servings=1.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
      consumed_at="2025-12-10T12:00:00",
    )

    # ユーザー2の記録
    service.record_meal(
      user_id="user2",
      recipe_id="recipe2",
      recipe_name="食事2",
      meal_type="lunch",
      servings=1.0,
      nutrition=sample_nutrition,
      ingredients=sample_ingredients,
      consumed_at="2025-12-10T12:00:00",
    )

    # ユーザー1のデータ取得
    daily1 = service.get_daily_nutrition("user1", "2025-12-10")
    assert daily1.meal_count == 1
    assert daily1.meals[0]["recipe_name"] == "食事1"

    # ユーザー2のデータ取得
    daily2 = service.get_daily_nutrition("user2", "2025-12-10")
    assert daily2.meal_count == 1
    assert daily2.meals[0]["recipe_name"] == "食事2"

  def test_empty_trend_analysis(self, service):
    """記録がない場合の傾向分析"""
    analysis = service.analyze_trends("user123", days=30)

    assert isinstance(analysis, TrendAnalysis)
    assert len(analysis.top_ingredients) == 0
    assert len(analysis.favorite_recipes) == 0
    assert len(analysis.meal_time_pattern) == 0

"""
季節推薦サービスのユニットテスト
"""

from datetime import datetime
from backend.services.seasonal_service import (
    SeasonalService,
    Season,
    MealTime,
)


# テスト用のサンプルレシピデータ
SAMPLE_RECIPES = [
    {
        "id": 1,
        "title": "たけのこご飯",
        "description": "春の味覚、たけのこを使った炊き込みご飯",
        "ingredients": [
            {"name": "たけのこ", "amount": "200g"},
            {"name": "米", "amount": "2合"},
        ],
        "tags": ["和食", "ご飯", "春", "昼食", "夕食"],
    },
    {
        "id": 2,
        "title": "冷やし中華",
        "description": "夏にぴったりの冷たい麺料理",
        "ingredients": [
            {"name": "中華麺", "amount": "2玉"},
            {"name": "きゅうり", "amount": "1本"},
            {"name": "トマト", "amount": "1個"},
        ],
        "tags": ["中華", "麺類", "冷たい", "夏", "昼食"],
    },
    {
        "id": 3,
        "title": "さつまいもの煮物",
        "description": "ほっこり甘い秋の味覚",
        "ingredients": [
            {"name": "さつまいも", "amount": "2本"},
            {"name": "砂糖", "amount": "大さじ2"},
        ],
        "tags": ["和食", "煮物", "温かい", "秋", "夕食"],
    },
    {
        "id": 4,
        "title": "白菜と豚肉の鍋",
        "description": "冬の定番、体が温まる鍋料理",
        "ingredients": [
            {"name": "白菜", "amount": "1/4個"},
            {"name": "豚肉", "amount": "200g"},
        ],
        "tags": ["和食", "鍋", "温かい", "冬", "夕食"],
    },
    {
        "id": 5,
        "title": "卵かけご飯",
        "description": "シンプルで美味しい朝食の定番",
        "ingredients": [
            {"name": "ご飯", "amount": "1膳"},
            {"name": "卵", "amount": "1個"},
        ],
        "tags": ["和食", "ご飯", "朝食", "簡単", "時短"],
    },
]


class TestSeasonalService:
    """SeasonalServiceのテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.service = SeasonalService(recipe_data=SAMPLE_RECIPES)

    def test_get_current_season_spring(self):
        """春の季節判定テスト"""
        # 3月
        date = datetime(2024, 3, 15)
        season = self.service.get_current_season(date)
        assert season == Season.SPRING

        # 5月
        date = datetime(2024, 5, 15)
        season = self.service.get_current_season(date)
        assert season == Season.SPRING

    def test_get_current_season_summer(self):
        """夏の季節判定テスト"""
        # 6月
        date = datetime(2024, 6, 15)
        season = self.service.get_current_season(date)
        assert season == Season.SUMMER

        # 8月
        date = datetime(2024, 8, 15)
        season = self.service.get_current_season(date)
        assert season == Season.SUMMER

    def test_get_current_season_autumn(self):
        """秋の季節判定テスト"""
        # 9月
        date = datetime(2024, 9, 15)
        season = self.service.get_current_season(date)
        assert season == Season.AUTUMN

        # 11月
        date = datetime(2024, 11, 15)
        season = self.service.get_current_season(date)
        assert season == Season.AUTUMN

    def test_get_current_season_winter(self):
        """冬の季節判定テスト"""
        # 12月
        date = datetime(2024, 12, 15)
        season = self.service.get_current_season(date)
        assert season == Season.WINTER

        # 1月
        date = datetime(2024, 1, 15)
        season = self.service.get_current_season(date)
        assert season == Season.WINTER

    def test_get_current_meal_time_breakfast(self):
        """朝食時間帯判定テスト"""
        time = datetime(2024, 1, 1, 7, 0)
        meal_time = self.service.get_current_meal_time(time)
        assert meal_time == MealTime.BREAKFAST

    def test_get_current_meal_time_lunch(self):
        """昼食時間帯判定テスト"""
        time = datetime(2024, 1, 1, 12, 0)
        meal_time = self.service.get_current_meal_time(time)
        assert meal_time == MealTime.LUNCH

    def test_get_current_meal_time_dinner(self):
        """夕食時間帯判定テスト"""
        time = datetime(2024, 1, 1, 18, 0)
        meal_time = self.service.get_current_meal_time(time)
        assert meal_time == MealTime.DINNER

    def test_get_current_meal_time_late_night(self):
        """夜食時間帯判定テスト"""
        time = datetime(2024, 1, 1, 23, 0)
        meal_time = self.service.get_current_meal_time(time)
        assert meal_time == MealTime.LATE_NIGHT

    def test_get_seasonal_ingredients_spring(self):
        """春の食材取得テスト"""
        ingredients = self.service.get_seasonal_ingredients(Season.SPRING)
        assert "たけのこ" in ingredients
        assert "菜の花" in ingredients
        assert "新玉ねぎ" in ingredients
        assert len(ingredients) > 0

    def test_get_seasonal_ingredients_summer(self):
        """夏の食材取得テスト"""
        ingredients = self.service.get_seasonal_ingredients(Season.SUMMER)
        assert "トマト" in ingredients
        assert "きゅうり" in ingredients
        assert "なす" in ingredients

    def test_recommend_by_season_spring(self):
        """春のレシピ推薦テスト"""
        recommendations = self.service.recommend_by_season(Season.SPRING, limit=5)
        assert len(recommendations) > 0
        # たけのこご飯が推薦されるはず
        recipe_titles = [r["title"] for r in recommendations]
        assert "たけのこご飯" in recipe_titles
        # スコアが付与されているか確認
        assert "season_score" in recommendations[0]

    def test_recommend_by_season_summer(self):
        """夏のレシピ推薦テスト"""
        recommendations = self.service.recommend_by_season(Season.SUMMER, limit=5)
        assert len(recommendations) > 0
        # 冷やし中華が推薦されるはず
        recipe_titles = [r["title"] for r in recommendations]
        assert "冷やし中華" in recipe_titles

    def test_recommend_by_meal_time_breakfast(self):
        """朝食レシピ推薦テスト"""
        recommendations = self.service.recommend_by_meal_time(
            MealTime.BREAKFAST, limit=5
        )
        assert len(recommendations) > 0
        # 卵かけご飯が推薦されるはず
        recipe_titles = [r["title"] for r in recommendations]
        assert "卵かけご飯" in recipe_titles

    def test_recommend_by_meal_time_dinner(self):
        """夕食レシピ推薦テスト"""
        recommendations = self.service.recommend_by_meal_time(MealTime.DINNER, limit=5)
        assert len(recommendations) > 0
        # 夕食タグを持つレシピが推薦されるはず
        for recipe in recommendations:
            assert "夕食" in recipe.get("tags", [])

    def test_recommend_by_temperature_hot(self):
        """暑い日のレシピ推薦テスト"""
        recommendations = self.service.recommend_by_temperature(30.0, limit=5)
        assert len(recommendations) > 0
        # 冷やし中華が推薦されるはず
        recipe_titles = [r["title"] for r in recommendations]
        assert "冷やし中華" in recipe_titles
        # カテゴリが付与されているか確認
        assert recommendations[0]["recommended_category"] == "hot"

    def test_recommend_by_temperature_warm(self):
        """寒い日のレシピ推薦テスト"""
        recommendations = self.service.recommend_by_temperature(10.0, limit=5)
        assert len(recommendations) > 0
        # 温かい料理が推薦されるはず
        for recipe in recommendations:
            assert "温かい" in recipe.get("tags", []) or "鍋" in recipe.get("tags", [])

    def test_recommend_comprehensive(self):
        """総合推薦テスト"""
        recommendations = self.service.recommend_comprehensive(
            season=Season.WINTER,
            meal_time=MealTime.DINNER,
            temperature=5.0,
            limit=5,
        )
        assert len(recommendations) > 0
        # 白菜と豚肉の鍋が高スコアで推薦されるはず
        recipe_titles = [r["title"] for r in recommendations]
        assert "白菜と豚肉の鍋" in recipe_titles
        # スコアが付与されているか確認
        assert "total_score" in recommendations[0]
        assert "season_score" in recommendations[0]
        assert "meal_time_score" in recommendations[0]
        assert "temperature_score" in recommendations[0]

    def test_recommend_comprehensive_no_temperature(self):
        """気温なしの総合推薦テスト"""
        recommendations = self.service.recommend_comprehensive(
            season=Season.SPRING,
            meal_time=MealTime.LUNCH,
            temperature=None,
            limit=5,
        )
        assert len(recommendations) > 0
        # 気温スコアは0になるはず
        for recipe in recommendations:
            assert recipe["temperature_score"] == 0

    def test_recommend_by_season_limit(self):
        """レシピ推薦の件数制限テスト"""
        recommendations = self.service.recommend_by_season(Season.SPRING, limit=2)
        assert len(recommendations) <= 2

    def test_recommend_with_empty_recipes(self):
        """レシピデータが空の場合のテスト"""
        service = SeasonalService(recipe_data=[])
        recommendations = service.recommend_by_season(Season.SPRING, limit=5)
        assert len(recommendations) == 0

    def test_seasonal_ingredients_all_seasons(self):
        """全季節の食材データが存在するかテスト"""
        for season in Season:
            ingredients = self.service.get_seasonal_ingredients(season)
            assert len(ingredients) > 0
            assert isinstance(ingredients, list)

    def test_recommend_sorting_by_score(self):
        """スコア順にソートされているかテスト"""
        recommendations = self.service.recommend_by_season(Season.SPRING, limit=10)
        if len(recommendations) > 1:
            # スコアが降順になっているか確認
            for i in range(len(recommendations) - 1):
                assert (
                    recommendations[i]["season_score"]
                    >= recommendations[i + 1]["season_score"]
                )

    def test_comprehensive_score_weighting(self):
        """総合スコアの重み付けテスト"""
        recommendations = self.service.recommend_comprehensive(
            season=Season.WINTER,
            meal_time=MealTime.DINNER,
            temperature=5.0,
            limit=10,
        )
        if len(recommendations) > 0:
            recipe = recommendations[0]
            # 総合スコアの計算式: (season_score * 3) + (meal_time_score * 2) + temperature_score
            expected_total = (
                (recipe["season_score"] * 3)
                + (recipe["meal_time_score"] * 2)
                + recipe["temperature_score"]
            )
            assert recipe["total_score"] == expected_total

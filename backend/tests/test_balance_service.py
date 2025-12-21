"""
BalanceService のユニットテスト
"""

from backend.services.balance_service import (
    BalanceService,
    DAILY_REFERENCE,
    PFC_IDEAL_RATIO,
)


class TestPFCBalance:
    """PFCバランス計算のテスト"""

    def test_ideal_pfc_balance(self):
        """理想的なPFCバランスのテスト"""
        # 理想比率に近い栄養データ
        nutrition = {
            "protein": 30,  # 120kcal (15%)
            "fat": 22,  # 198kcal (24.75%)
            "carbs": 120,  # 480kcal (60%)
        }

        result = BalanceService.calculate_pfc_balance(nutrition)

        assert result["total_cal"] > 0
        assert result["balance_score"] >= 90
        assert result["is_balanced"] is True
        assert len(result["pie_chart_data"]) == 3

    def test_high_fat_balance(self):
        """脂質過多のテスト"""
        nutrition = {"protein": 20, "fat": 50, "carbs": 80}  # 高脂質

        result = BalanceService.calculate_pfc_balance(nutrition)

        assert result["fat_ratio"] > PFC_IDEAL_RATIO["fat"]
        assert result["balance_score"] < 80
        assert any("脂質" in rec for rec in result["recommendations"])

    def test_high_carbs_balance(self):
        """炭水化物過多のテスト"""
        nutrition = {"protein": 15, "fat": 10, "carbs": 200}  # 高炭水化物

        result = BalanceService.calculate_pfc_balance(nutrition)

        assert result["carbs_ratio"] > PFC_IDEAL_RATIO["carbs"]
        assert any("炭水化物" in rec for rec in result["recommendations"])

    def test_zero_nutrition(self):
        """栄養データゼロのテスト"""
        nutrition = {"protein": 0, "fat": 0, "carbs": 0}

        result = BalanceService.calculate_pfc_balance(nutrition)

        assert result["total_cal"] == 0
        assert result["balance_score"] == 0
        assert result["is_balanced"] is False

    def test_pie_chart_data_format(self):
        """円グラフデータ形式のテスト"""
        nutrition = {"protein": 25, "fat": 20, "carbs": 100}

        result = BalanceService.calculate_pfc_balance(nutrition)

        assert "pie_chart_data" in result
        assert len(result["pie_chart_data"]) == 3

        for item in result["pie_chart_data"]:
            assert "name" in item
            assert "value" in item
            assert "calories" in item
            assert item["value"] >= 0


class TestDailyBalance:
    """1日の食事バランス評価のテスト"""

    def test_ideal_daily_balance(self):
        """理想的な1日の食事バランス"""
        recipes = [
            {
                "calories": 650,
                "protein": 20,
                "fat": 18,
                "carbs": 100,
                "fiber": 7,
                "salt": 2.5,
            },
            {
                "calories": 700,
                "protein": 22,
                "fat": 20,
                "carbs": 105,
                "fiber": 7,
                "salt": 2.5,
            },
            {
                "calories": 650,
                "protein": 18,
                "fat": 17,
                "carbs": 95,
                "fiber": 6,
                "salt": 2.5,
            },
        ]

        result = BalanceService.evaluate_daily_balance(recipes)

        assert result["overall_score"] >= 70
        assert result["evaluation_level"] in ["good", "excellent", "fair"]
        assert "bar_chart_data" in result
        assert "radar_chart_data" in result
        assert len(result["bar_chart_data"]) == 6
        assert len(result["radar_chart_data"]) == 6

    def test_low_protein_daily(self):
        """タンパク質不足の1日"""
        recipes = [
            {
                "calories": 600,
                "protein": 10,
                "fat": 15,
                "carbs": 110,
                "fiber": 5,
                "salt": 2,
            },
            {
                "calories": 700,
                "protein": 12,
                "fat": 18,
                "carbs": 120,
                "fiber": 6,
                "salt": 2.5,
            },
            {
                "calories": 650,
                "protein": 10,
                "fat": 16,
                "carbs": 115,
                "fiber": 5,
                "salt": 2.5,
            },
        ]

        result = BalanceService.evaluate_daily_balance(recipes)

        assert result["fulfillment"]["protein"] < 80
        assert any("タンパク質" in rec for rec in result["recommendations"])

    def test_high_salt_daily(self):
        """塩分過多の1日"""
        recipes = [
            {
                "calories": 650,
                "protein": 20,
                "fat": 18,
                "carbs": 100,
                "fiber": 5,
                "salt": 3.5,
            },
            {
                "calories": 700,
                "protein": 22,
                "fat": 20,
                "carbs": 105,
                "fiber": 6,
                "salt": 3.5,
            },
            {
                "calories": 650,
                "protein": 18,
                "fat": 17,
                "carbs": 95,
                "fiber": 5,
                "salt": 3,
            },
        ]

        result = BalanceService.evaluate_daily_balance(recipes)

        assert result["fulfillment"]["salt"] > 100
        assert any("塩分" in rec for rec in result["recommendations"])

    def test_single_meal(self):
        """1食のみのテスト"""
        recipes = [
            {
                "calories": 650,
                "protein": 25,
                "fat": 20,
                "carbs": 85,
                "fiber": 5,
                "salt": 2.5,
            }
        ]

        result = BalanceService.evaluate_daily_balance(recipes)

        assert result["total"]["calories"] == 650
        assert result["fulfillment"]["calories"] < 50  # 1日の半分以下

    def test_empty_meals(self):
        """空の食事リスト"""
        recipes = []

        result = BalanceService.evaluate_daily_balance(recipes)

        assert result["total"]["calories"] == 0
        # 空配列の場合、全栄養素が0で計算されるためスコアは低いが0ではない
        assert result["overall_score"] <= 20

    def test_chart_data_format(self):
        """グラフデータ形式のテスト"""
        recipes = [
            {
                "calories": 650,
                "protein": 20,
                "fat": 18,
                "carbs": 100,
                "fiber": 5,
                "salt": 2.5,
            }
        ]

        result = BalanceService.evaluate_daily_balance(recipes)

        # 棒グラフデータ
        assert "bar_chart_data" in result
        for item in result["bar_chart_data"]:
            assert "nutrient" in item
            assert "actual" in item
            assert "reference" in item
            assert "fulfillment" in item

        # レーダーチャートデータ
        assert "radar_chart_data" in result
        for item in result["radar_chart_data"]:
            assert "category" in item
            assert "score" in item
            assert 0 <= item["score"] <= 100


class TestNutritionScore:
    """栄養バランススコア算出のテスト"""

    def test_excellent_score(self):
        """優秀なスコア"""
        nutrition = {
            "calories": 670,
            "protein": 20,
            "fat": 18,
            "carbs": 100,
            "fiber": 7,
            "salt": 2.5,
        }

        result = BalanceService.calculate_nutrition_score(nutrition)

        assert result["overall_score"] >= 70
        assert result["is_healthy"] is True
        assert result["evaluation"] in ["good", "excellent"]

    def test_poor_score(self):
        """低スコア"""
        nutrition = {
            "calories": 1200,  # 高カロリー
            "protein": 10,  # 低タンパク
            "fat": 60,  # 高脂質
            "carbs": 150,
            "fiber": 2,  # 低食物繊維
            "salt": 5,  # 高塩分
        }

        result = BalanceService.calculate_nutrition_score(nutrition)

        assert result["overall_score"] < 70
        assert result["is_healthy"] is False

    def test_score_components(self):
        """スコアコンポーネントのテスト"""
        nutrition = {
            "calories": 650,
            "protein": 20,
            "fat": 18,
            "carbs": 100,
            "fiber": 6,
            "salt": 2.5,
        }

        result = BalanceService.calculate_nutrition_score(nutrition)

        assert "overall_score" in result
        assert "pfc_score" in result
        assert "nutrient_scores" in result
        assert "evaluation" in result
        assert "is_healthy" in result

        # 各栄養素のスコアが存在
        for key in DAILY_REFERENCE.keys():
            assert key in result["nutrient_scores"]


class TestRecipeBalanceEvaluation:
    """レシピバランス評価のテスト"""

    def test_complete_evaluation(self):
        """完全な評価データのテスト"""
        nutrition = {
            "calories": 650,
            "protein": 25,
            "fat": 20,
            "carbs": 85,
            "fiber": 5,
            "salt": 2.5,
        }

        result = BalanceService.get_recipe_balance_evaluation(nutrition)

        assert "nutrition" in result
        assert "pfc_balance" in result
        assert "score" in result
        assert "daily_reference_percentage" in result

    def test_daily_percentage(self):
        """日次基準パーセンテージのテスト"""
        nutrition = {
            "calories": 1000,
            "protein": 30,
            "fat": 27.5,
            "carbs": 150,
            "fiber": 10,
            "salt": 3.75,
        }

        result = BalanceService.get_recipe_balance_evaluation(nutrition)

        # 各栄養素が50%（半分）になるはず
        assert result["daily_reference_percentage"]["calories"] == 50.0
        assert result["daily_reference_percentage"]["protein"] == 50.0
        assert result["daily_reference_percentage"]["fat"] == 50.0


class TestEvaluationLevel:
    """評価レベル判定のテスト"""

    def test_excellent_level(self):
        """excellent レベル"""
        level = BalanceService._get_evaluation_level(95)
        assert level == "excellent"

    def test_good_level(self):
        """good レベル"""
        level = BalanceService._get_evaluation_level(80)
        assert level == "good"

    def test_fair_level(self):
        """fair レベル"""
        level = BalanceService._get_evaluation_level(65)
        assert level == "fair"

    def test_needs_improvement_level(self):
        """needs_improvement レベル"""
        level = BalanceService._get_evaluation_level(50)
        assert level == "needs_improvement"


class TestRecommendations:
    """アドバイス生成のテスト"""

    def test_pfc_recommendations(self):
        """PFCアドバイス生成"""
        # タンパク質不足
        recs = BalanceService._generate_pfc_recommendations(0.08, 0.25, 0.67)
        assert any("タンパク質" in rec for rec in recs)

        # 脂質過多
        recs = BalanceService._generate_pfc_recommendations(0.15, 0.40, 0.45)
        assert any("脂質" in rec for rec in recs)

    def test_daily_recommendations(self):
        """1日のアドバイス生成"""
        fulfillment = {
            "calories": 60,
            "protein": 70,
            "fat": 80,
            "carbs": 75,
            "fiber": 65,
            "salt": 90,
        }
        total = {
            "calories": 1200,
            "protein": 42,
            "fat": 44,
            "carbs": 225,
            "fiber": 13,
            "salt": 6.75,
        }

        recs = BalanceService._generate_daily_recommendations(fulfillment, total)

        assert len(recs) > 0
        assert any(
            "カロリー" in rec
            or "タンパク質" in rec
            or "炭水化物" in rec
            or "食物繊維" in rec
            for rec in recs
        )

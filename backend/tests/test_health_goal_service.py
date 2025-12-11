"""
Health Goal Service のテスト
"""

import pytest
from datetime import date, timedelta
from backend.services.health_goal_service import (
    HealthGoalService,
    Gender,
    ActivityLevel,
)


@pytest.fixture
def service(tmp_path):
    """テスト用サービスインスタンス"""
    return HealthGoalService(data_dir=str(tmp_path))


@pytest.fixture
def sample_profile():
    """サンプルプロファイル"""
    return {
        "age": 30,
        "gender": Gender.MALE,
        "weight": 70.0,
        "height": 170.0,
        "activity_level": ActivityLevel.MODERATE,
    }


class TestProfileManagement:
    """プロファイル管理のテスト"""

    def test_set_profile(self, service, sample_profile):
        """プロファイル設定のテスト"""
        profile = service.set_profile(**sample_profile)

        assert profile["age"] == 30
        assert profile["gender"] == "male"
        assert profile["weight"] == 70.0
        assert profile["height"] == 170.0
        assert profile["activity_level"] == "moderate"
        assert "updated_at" in profile

    def test_get_profile(self, service, sample_profile):
        """プロファイル取得のテスト"""
        # プロファイル設定
        service.set_profile(**sample_profile)

        # 取得
        profile = service.get_profile()
        assert profile is not None
        assert profile["age"] == 30
        assert profile["gender"] == "male"

    def test_get_profile_not_found(self, service):
        """プロファイル未設定時のテスト"""
        profile = service.get_profile()
        assert profile is None


class TestBMRCalculation:
    """BMR計算のテスト"""

    def test_calculate_bmr_male(self, service):
        """男性のBMR計算テスト"""
        bmr = service.calculate_bmr(30, Gender.MALE, 70.0, 170.0)
        # 66.47 + (13.75 * 70) + (5.00 * 170) - (6.76 * 30)
        # = 66.47 + 962.5 + 850 - 202.8 = 1676.17
        assert abs(bmr - 1676.2) < 1.0

    def test_calculate_bmr_female(self, service):
        """女性のBMR計算テスト"""
        bmr = service.calculate_bmr(30, Gender.FEMALE, 55.0, 160.0)
        # 655.1 + (9.56 * 55) + (1.85 * 160) - (4.68 * 30)
        # = 655.1 + 525.8 + 296 - 140.4 = 1336.5
        assert abs(bmr - 1336.5) < 1.0


class TestTDEECalculation:
    """TDEE計算のテスト"""

    def test_calculate_tdee_low_activity(self, service):
        """低活動レベルのTDEE計算テスト"""
        tdee = service.calculate_tdee(30, Gender.MALE, 70.0, 170.0, ActivityLevel.LOW)
        bmr = service.calculate_bmr(30, Gender.MALE, 70.0, 170.0)
        expected = bmr * 1.2
        assert abs(tdee - expected) < 1.0

    def test_calculate_tdee_moderate_activity(self, service):
        """中活動レベルのTDEE計算テスト"""
        tdee = service.calculate_tdee(
            30, Gender.MALE, 70.0, 170.0, ActivityLevel.MODERATE
        )
        bmr = service.calculate_bmr(30, Gender.MALE, 70.0, 170.0)
        expected = bmr * 1.375
        assert abs(tdee - expected) < 1.0

    def test_calculate_tdee_high_activity(self, service):
        """高活動レベルのTDEE計算テスト"""
        tdee = service.calculate_tdee(30, Gender.MALE, 70.0, 170.0, ActivityLevel.HIGH)
        bmr = service.calculate_bmr(30, Gender.MALE, 70.0, 170.0)
        expected = bmr * 1.55
        assert abs(tdee - expected) < 1.0

    def test_calculate_tdee_athlete(self, service):
        """アスリートレベルのTDEE計算テスト"""
        tdee = service.calculate_tdee(
            30, Gender.MALE, 70.0, 170.0, ActivityLevel.ATHLETE
        )
        bmr = service.calculate_bmr(30, Gender.MALE, 70.0, 170.0)
        expected = bmr * 1.725
        assert abs(tdee - expected) < 1.0


class TestRecommendations:
    """推奨値計算のテスト"""

    def test_get_recommendations(self, service, sample_profile):
        """推奨値取得のテスト"""
        service.set_profile(**sample_profile)
        recommendations = service.get_recommendations()

        assert "calories" in recommendations
        assert "protein" in recommendations
        assert "fat" in recommendations
        assert "carbohydrate" in recommendations
        assert "fiber" in recommendations
        assert "salt" in recommendations

        # 値の妥当性チェック
        assert recommendations["calories"] > 0
        assert recommendations["protein"] > 0
        assert recommendations["fat"] > 0
        assert recommendations["carbohydrate"] > 0
        assert recommendations["fiber"] == 21.0  # 男性
        assert recommendations["salt"] == 7.5  # 男性

    def test_get_recommendations_female(self, service):
        """女性の推奨値取得のテスト"""
        service.set_profile(
            age=25,
            gender=Gender.FEMALE,
            weight=55.0,
            height=160.0,
            activity_level=ActivityLevel.MODERATE,
        )
        recommendations = service.get_recommendations()

        assert recommendations["fiber"] == 18.0  # 女性
        assert recommendations["salt"] == 6.5  # 女性

    def test_get_recommendations_no_profile(self, service):
        """プロファイル未設定時のエラーテスト"""
        with pytest.raises(ValueError, match="プロファイルが設定されていません"):
            service.get_recommendations()


class TestTargetsManagement:
    """目標値管理のテスト"""

    def test_set_targets(self, service):
        """目標値設定のテスト"""
        targets = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }
        result = service.set_targets(targets)

        assert "targets" in result
        assert "updated_at" in result
        assert result["targets"]["calories"] == 2000.0

    def test_get_targets(self, service):
        """目標値取得のテスト"""
        targets = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }
        service.set_targets(targets)

        retrieved = service.get_targets()
        assert retrieved is not None
        assert retrieved["calories"] == 2000.0

    def test_get_targets_not_found(self, service):
        """目標値未設定時のテスト"""
        targets = service.get_targets()
        assert targets is None


class TestProgressCalculation:
    """達成率計算のテスト"""

    def test_calculate_progress(self, service):
        """達成率計算のテスト"""
        # 目標値設定
        targets = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }
        service.set_targets(targets)

        # 実際の摂取データ
        nutrition_data = {
            "calories": 1800.0,
            "protein": 70.0,
            "fat": 50.0,
            "carbohydrate": 280.0,
            "fiber": 18.0,
            "salt": 6.0,
        }

        # 達成率計算
        progress = service.calculate_progress(nutrition_data)

        assert "date" in progress
        assert "progress" in progress

        # カロリー達成率: 1800 / 2000 = 90%
        assert progress["progress"]["calories"]["achievement"] == 90.0
        assert progress["progress"]["calories"]["status"] == "excellent"

        # タンパク質達成率: 70 / 75 ≈ 93.3%
        assert abs(progress["progress"]["protein"]["achievement"] - 93.3) < 0.1
        assert progress["progress"]["protein"]["status"] == "excellent"

    def test_calculate_progress_salt(self, service):
        """塩分の達成率計算テスト（少ないほど良い）"""
        targets = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }
        service.set_targets(targets)

        # 塩分が目標の半分
        nutrition_data = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 3.75,
        }

        progress = service.calculate_progress(nutrition_data)
        # 達成率 = (1 - 3.75/7.5) * 100 = 50%
        assert progress["progress"]["salt"]["achievement"] == 50.0

    def test_calculate_progress_no_targets(self, service):
        """目標値未設定時のエラーテスト"""
        nutrition_data = {
            "calories": 2000.0,
            "protein": 75.0,
        }

        with pytest.raises(ValueError, match="目標値が設定されていません"):
            service.calculate_progress(nutrition_data)


class TestHistoryManagement:
    """履歴管理のテスト"""

    def test_save_and_get_history(self, service):
        """履歴保存・取得のテスト"""
        # 目標値設定
        targets = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }
        service.set_targets(targets)

        # 複数日分のデータを保存
        for i in range(3):
            nutrition_data = {
                "calories": 1800.0 + i * 100,
                "protein": 70.0,
                "fat": 50.0,
                "carbohydrate": 280.0,
                "fiber": 18.0,
                "salt": 6.0,
            }
            target_date = date.today() - timedelta(days=i)
            service.calculate_progress(nutrition_data, target_date)

        # 履歴取得
        history = service.get_history(days=7)
        assert len(history) == 7

        # データがある日を確認
        days_with_data = [h for h in history if h["progress"] is not None]
        assert len(days_with_data) == 3

    def test_get_history_empty(self, service):
        """履歴なしのテスト"""
        history = service.get_history(days=7)
        assert len(history) == 7
        assert all(h["progress"] is None for h in history)


class TestAdviceGeneration:
    """アドバイス生成のテスト"""

    def test_get_advice_protein_poor(self, service):
        """タンパク質不足のアドバイステスト"""
        targets = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }
        service.set_targets(targets)

        nutrition_data = {
            "calories": 2000.0,
            "protein": 30.0,  # 大幅に不足
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }

        progress = service.calculate_progress(nutrition_data)
        advice = service.get_advice(progress)

        # タンパク質のアドバイスが含まれるべき
        protein_advice = [a for a in advice if a["nutrient"] == "protein"]
        assert len(protein_advice) > 0
        assert "不足" in protein_advice[0]["advice"]

    def test_get_advice_salt_excessive(self, service):
        """塩分過剰のアドバイステスト"""
        targets = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }
        service.set_targets(targets)

        nutrition_data = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 12.0,  # 過剰
        }

        progress = service.calculate_progress(nutrition_data)
        advice = service.get_advice(progress)

        # 塩分のアドバイスが含まれるべき
        salt_advice = [a for a in advice if a["nutrient"] == "salt"]
        assert len(salt_advice) > 0
        assert "過剰" in salt_advice[0]["advice"]

    def test_get_advice_all_excellent(self, service):
        """すべて優秀な場合のアドバイステスト"""
        targets = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 7.5,
        }
        service.set_targets(targets)

        nutrition_data = {
            "calories": 2000.0,
            "protein": 75.0,
            "fat": 55.0,
            "carbohydrate": 300.0,
            "fiber": 21.0,
            "salt": 5.0,
        }

        progress = service.calculate_progress(nutrition_data)
        advice = service.get_advice(progress)

        # アドバイスがないか、ごく少ない
        assert len(advice) <= 1


class TestStatusDetermination:
    """ステータス判定のテスト"""

    def test_status_excellent(self, service):
        """優秀ステータスのテスト"""
        assert service._get_status(95.0, "protein") == "excellent"
        assert service._get_status(100.0, "calories") == "excellent"

    def test_status_good(self, service):
        """良好ステータスのテスト"""
        assert service._get_status(80.0, "protein") == "good"
        assert service._get_status(75.0, "carbohydrate") == "good"

    def test_status_fair(self, service):
        """要改善ステータスのテスト"""
        assert service._get_status(60.0, "protein") == "fair"
        assert service._get_status(55.0, "fat") == "fair"

    def test_status_poor(self, service):
        """不足ステータスのテスト"""
        assert service._get_status(40.0, "protein") == "poor"
        assert service._get_status(30.0, "fiber") == "poor"

    def test_status_salt(self, service):
        """塩分のステータステスト（逆転）"""
        assert service._get_status(85.0, "salt") == "excellent"
        assert service._get_status(65.0, "salt") == "good"
        assert service._get_status(45.0, "salt") == "fair"
        assert service._get_status(30.0, "salt") == "poor"

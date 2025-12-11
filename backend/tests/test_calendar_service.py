"""
カレンダーサービスのテスト
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import tempfile
import shutil

# icalendarがインストールされていない場合はスキップ
try:
    from backend.services.calendar_service import CalendarService, MealPlanModel
    CALENDAR_SERVICE_AVAILABLE = True
except ImportError:
    CALENDAR_SERVICE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not CALENDAR_SERVICE_AVAILABLE,
    reason="calendar_service requires icalendar",
)


@pytest.fixture
def temp_data_dir():
    """一時データディレクトリを作成"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def calendar_service(temp_data_dir):
    """テスト用カレンダーサービス"""
    return CalendarService(data_dir=temp_data_dir)


class TestMealPlanModel:
    """MealPlanModel のテスト"""

    def test_meal_plan_model_creation(self):
        """献立計画モデルの作成"""
        plan = MealPlanModel(
            date=date(2025, 12, 15),
            meal_type="昼食",
            recipe_name="カレーライス",
            servings=2,
        )

        assert plan.date == date(2025, 12, 15)
        assert plan.meal_type == "昼食"
        assert plan.recipe_name == "カレーライス"
        assert plan.servings == 2

    def test_meal_plan_model_with_optional_fields(self):
        """オプションフィールド付き献立計画モデル"""
        plan = MealPlanModel(
            date=date(2025, 12, 15),
            meal_type="夕食",
            recipe_id=123,
            recipe_name="ハンバーグ",
            servings=4,
            notes="特別な日のディナー",
        )

        assert plan.recipe_id == 123
        assert plan.notes == "特別な日のディナー"


class TestCalendarService:
    """CalendarService のテスト"""

    def test_service_initialization(self, calendar_service, temp_data_dir):
        """サービスの初期化"""
        assert calendar_service.data_dir == Path(temp_data_dir)
        assert calendar_service.plans_file.exists()

    def test_create_plan(self, calendar_service):
        """献立計画の作成"""
        plan = MealPlanModel(
            date=date(2025, 12, 15),
            meal_type="朝食",
            recipe_name="トースト",
            servings=1,
        )

        created = calendar_service.create_plan(plan)

        assert created.id is not None
        assert created.date == date(2025, 12, 15)
        assert created.meal_type == "朝食"
        assert created.recipe_name == "トースト"
        assert created.created_at is not None

    def test_get_plans_all(self, calendar_service):
        """全献立計画の取得"""
        # テストデータ作成
        plan1 = MealPlanModel(
            date=date(2025, 12, 15),
            meal_type="朝食",
            recipe_name="トースト",
            servings=1,
        )
        plan2 = MealPlanModel(
            date=date(2025, 12, 16),
            meal_type="昼食",
            recipe_name="ラーメン",
            servings=2,
        )

        calendar_service.create_plan(plan1)
        calendar_service.create_plan(plan2)

        # 全取得
        plans = calendar_service.get_plans()
        assert len(plans) == 2

    def test_get_plans_with_date_filter(self, calendar_service):
        """日付フィルタ付き献立計画の取得"""
        # テストデータ作成
        for i in range(5):
            plan = MealPlanModel(
                date=date(2025, 12, 15) + timedelta(days=i),
                meal_type="昼食",
                recipe_name=f"レシピ{i}",
                servings=1,
            )
            calendar_service.create_plan(plan)

        # 範囲フィルタ
        plans = calendar_service.get_plans(
            start_date=date(2025, 12, 16), end_date=date(2025, 12, 18)
        )

        assert len(plans) == 3
        assert all(date(2025, 12, 16) <= p.date <= date(2025, 12, 18) for p in plans)

    def test_get_plans_with_meal_type_filter(self, calendar_service):
        """食事タイプフィルタ付き献立計画の取得"""
        # テストデータ作成
        meal_types = ["朝食", "昼食", "夕食", "朝食"]
        for i, meal_type in enumerate(meal_types):
            plan = MealPlanModel(
                date=date(2025, 12, 15),
                meal_type=meal_type,
                recipe_name=f"レシピ{i}",
                servings=1,
            )
            calendar_service.create_plan(plan)

        # 食事タイプフィルタ
        plans = calendar_service.get_plans(meal_type="朝食")

        assert len(plans) == 2
        assert all(p.meal_type == "朝食" for p in plans)

    def test_update_plan(self, calendar_service):
        """献立計画の更新"""
        # 作成
        plan = MealPlanModel(
            date=date(2025, 12, 15), meal_type="昼食", recipe_name="カレー", servings=2
        )
        created = calendar_service.create_plan(plan)

        # 更新
        updates = {"recipe_name": "カレーライス（更新）", "servings": 4}
        updated = calendar_service.update_plan(created.id, updates)

        assert updated is not None
        assert updated.recipe_name == "カレーライス（更新）"
        assert updated.servings == 4
        assert updated.date == date(2025, 12, 15)

    def test_update_nonexistent_plan(self, calendar_service):
        """存在しない献立計画の更新"""
        result = calendar_service.update_plan(999, {"recipe_name": "test"})
        assert result is None

    def test_delete_plan(self, calendar_service):
        """献立計画の削除"""
        # 作成
        plan = MealPlanModel(
            date=date(2025, 12, 15), meal_type="夕食", recipe_name="寿司", servings=2
        )
        created = calendar_service.create_plan(plan)

        # 削除
        success = calendar_service.delete_plan(created.id)
        assert success is True

        # 削除確認
        plans = calendar_service.get_plans()
        assert len(plans) == 0

    def test_delete_nonexistent_plan(self, calendar_service):
        """存在しない献立計画の削除"""
        success = calendar_service.delete_plan(999)
        assert success is False

    def test_export_to_ical(self, calendar_service):
        """iCal エクスポート"""
        # テストデータ作成
        plan1 = MealPlanModel(
            date=date(2025, 12, 15),
            meal_type="朝食",
            recipe_name="トースト",
            servings=1,
        )
        plan2 = MealPlanModel(
            date=date(2025, 12, 16),
            meal_type="昼食",
            recipe_name="パスタ",
            servings=2,
            notes="テストメモ",
        )

        calendar_service.create_plan(plan1)
        calendar_service.create_plan(plan2)

        # エクスポート
        ical_content = calendar_service.export_to_ical()

        # 検証
        assert "BEGIN:VCALENDAR" in ical_content
        assert "END:VCALENDAR" in ical_content
        assert "朝食: トースト" in ical_content
        assert "昼食: パスタ" in ical_content
        assert "テストメモ" in ical_content

    def test_export_to_ical_with_date_filter(self, calendar_service):
        """日付フィルタ付き iCal エクスポート"""
        # テストデータ作成
        for i in range(5):
            plan = MealPlanModel(
                date=date(2025, 12, 15) + timedelta(days=i),
                meal_type="昼食",
                recipe_name=f"レシピ{i}",
                servings=1,
            )
            calendar_service.create_plan(plan)

        # 範囲指定でエクスポート
        ical_content = calendar_service.export_to_ical(
            start_date=date(2025, 12, 16), end_date=date(2025, 12, 17)
        )

        # 検証
        assert "レシピ1" in ical_content
        assert "レシピ2" in ical_content
        assert "レシピ0" not in ical_content
        assert "レシピ3" not in ical_content

    def test_prepare_google_calendar_event(self, calendar_service):
        """Google Calendar イベントデータの準備"""
        plan = MealPlanModel(
            date=date(2025, 12, 15),
            meal_type="夕食",
            recipe_name="ステーキ",
            servings=2,
            notes="記念日ディナー",
        )

        event = calendar_service.prepare_google_calendar_event(plan)

        assert event["summary"] == "夕食: ステーキ"
        assert "ステーキ" in event["description"]
        assert "2人分" in event["description"]
        assert "記念日ディナー" in event["description"]
        assert event["start"]["date"] == "2025-12-15"
        assert event["end"]["date"] == "2025-12-16"
        assert event["start"]["timeZone"] == "Asia/Tokyo"

    def test_get_week_plans(self, calendar_service):
        """週間献立計画の取得"""
        # 2025年12月15日（月曜日）を含む週のデータを作成
        target_date = date(2025, 12, 15)

        for i in range(7):
            plan_date = target_date + timedelta(days=i)
            for meal_type in ["朝食", "昼食"]:
                plan = MealPlanModel(
                    date=plan_date,
                    meal_type=meal_type,
                    recipe_name=f"{meal_type}-{i}",
                    servings=1,
                )
                calendar_service.create_plan(plan)

        # 週間プラン取得
        grouped = calendar_service.get_week_plans(target_date)

        # 検証
        assert len(grouped) == 7  # 7日分
        for date_key, plans in grouped.items():
            assert len(plans) == 2  # 各日2食

    def test_get_month_plans(self, calendar_service):
        """月間献立計画の取得"""
        # 2025年12月のデータを作成
        for day in range(1, 11):  # 1日〜10日
            plan = MealPlanModel(
                date=date(2025, 12, day),
                meal_type="昼食",
                recipe_name=f"レシピ{day}",
                servings=1,
            )
            calendar_service.create_plan(plan)

        # 月間プラン取得
        grouped = calendar_service.get_month_plans(2025, 12)

        # 検証
        assert len(grouped) == 10  # 10日分

    def test_meal_type_sorting(self, calendar_service):
        """食事タイプのソート順確認"""
        target_date = date(2025, 12, 15)

        # 逆順で作成
        for meal_type in ["間食", "夕食", "昼食", "朝食"]:
            plan = MealPlanModel(
                date=target_date, meal_type=meal_type, recipe_name=meal_type, servings=1
            )
            calendar_service.create_plan(plan)

        # 週間プラン取得
        grouped = calendar_service.get_week_plans(target_date)
        plans = grouped[target_date.isoformat()]

        # ソート順検証
        meal_types = [p.meal_type for p in plans]
        assert meal_types == ["朝食", "昼食", "夕食", "間食"]


class TestCalendarServiceEdgeCases:
    """エッジケースのテスト"""

    def test_empty_plans_file(self, calendar_service):
        """空の献立計画ファイル"""
        plans = calendar_service.get_plans()
        assert plans == []

    def test_invalid_json_file(self, calendar_service):
        """不正な JSON ファイル"""
        calendar_service.plans_file.write_text("invalid json", encoding="utf-8")
        plans = calendar_service.get_plans()
        assert plans == []

    def test_multiple_plans_same_date_and_meal(self, calendar_service):
        """同日同食事タイプの複数献立"""
        for i in range(3):
            plan = MealPlanModel(
                date=date(2025, 12, 15),
                meal_type="昼食",
                recipe_name=f"レシピ{i}",
                servings=1,
            )
            calendar_service.create_plan(plan)

        plans = calendar_service.get_plans(
            start_date=date(2025, 12, 15), end_date=date(2025, 12, 15)
        )

        assert len(plans) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

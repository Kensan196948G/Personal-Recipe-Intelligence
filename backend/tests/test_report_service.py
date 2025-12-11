"""
レポートサービスのテスト
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from backend.services.report_service import ReportService


class MockNutritionService:
    """モック栄養サービス"""

    def get_nutrition_summary(self, user_id: str, start_date: str, end_date: str):
        """栄養サマリーを取得（モック）"""
        return {
            "total_calories": 14000.0,
            "total_protein": 350.0,
            "total_fat": 280.0,
            "total_carbs": 1750.0,
        }


class MockGoalService:
    """モック目標サービス"""

    def get_goals(self, user_id: str):
        """目標リストを取得（モック）"""
        return [
            {
                "goal_id": "goal_001",
                "title": "週3回自炊する",
                "status": "completed",
                "progress": 100,
            },
            {
                "goal_id": "goal_002",
                "title": "タンパク質を毎日60g摂取",
                "status": "in_progress",
                "progress": 75,
            },
            {
                "goal_id": "goal_003",
                "title": "1日のカロリーを2000kcal以下に",
                "status": "in_progress",
                "progress": 50,
            },
        ]


@pytest.fixture
def temp_data_dir():
    """一時データディレクトリ"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def report_service(temp_data_dir):
    """レポートサービス"""
    nutrition_service = MockNutritionService()
    goal_service = MockGoalService()
    return ReportService(
        nutrition_service=nutrition_service,
        goal_service=goal_service,
        data_dir=temp_data_dir,
    )


def test_generate_weekly_report(report_service):
    """週次レポート生成のテスト"""
    user_id = "test_user"

    # 今週のレポート生成
    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    assert report_data is not None
    assert report_data.report_type == "weekly"
    assert report_data.start_date is not None
    assert report_data.end_date is not None
    assert report_data.nutrition_summary is not None
    assert report_data.expense_summary is not None
    assert report_data.goal_summary is not None
    assert len(report_data.recommendations) > 0


def test_generate_monthly_report(report_service):
    """月次レポート生成のテスト"""
    user_id = "test_user"

    # 今月のレポート生成
    report_data = report_service.generate_monthly_report(
        user_id=user_id, month_offset=0
    )

    assert report_data is not None
    assert report_data.report_type == "monthly"
    assert report_data.start_date.endswith("-01")  # 月初
    assert report_data.nutrition_summary is not None
    assert report_data.expense_summary is not None
    assert report_data.goal_summary is not None


def test_generate_custom_report(report_service):
    """カスタムレポート生成のテスト"""
    user_id = "test_user"
    start_date = "2025-01-01"
    end_date = "2025-01-31"

    report_data = report_service.generate_custom_report(
        user_id=user_id, start_date=start_date, end_date=end_date
    )

    assert report_data is not None
    assert report_data.report_type == "custom"
    assert report_data.start_date == start_date
    assert report_data.end_date == end_date


def test_nutrition_summary_calculation(report_service):
    """栄養サマリーの計算テスト"""
    user_id = "test_user"

    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    nutrition = report_data.nutrition_summary

    # 合計値が正しいこと
    assert nutrition.total_calories == 14000.0
    assert nutrition.total_protein == 350.0
    assert nutrition.total_fat == 280.0
    assert nutrition.total_carbs == 1750.0

    # 平均値が計算されていること（7日間）
    assert nutrition.avg_daily_calories == 14000.0 / 7
    assert nutrition.avg_daily_protein == 350.0 / 7
    assert nutrition.avg_daily_fat == 280.0 / 7
    assert nutrition.avg_daily_carbs == 1750.0 / 7


def test_goal_summary_calculation(report_service):
    """目標サマリーの計算テスト"""
    user_id = "test_user"

    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    goal = report_data.goal_summary

    # 目標数が正しいこと
    assert goal.total_goals == 3
    assert goal.completed_goals == 1
    assert goal.in_progress_goals == 2

    # 達成率が計算されていること
    assert goal.completion_rate == pytest.approx(33.33, rel=0.1)

    # 目標詳細が含まれること
    assert len(goal.goal_details) > 0


def test_recommendations_generation(report_service):
    """レコメンデーション生成のテスト"""
    user_id = "test_user"

    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    recommendations = report_data.recommendations

    # レコメンデーションが生成されること
    assert len(recommendations) > 0
    assert all(isinstance(rec, str) for rec in recommendations)
    assert all(len(rec) > 0 for rec in recommendations)


def test_generate_pdf(report_service, temp_data_dir):
    """PDF生成のテスト"""
    user_id = "test_user"

    # レポート生成
    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    # PDF生成
    pdf_bytes = report_service.generate_pdf(report_data)

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")  # PDFマジックナンバー


def test_generate_pdf_with_output_path(report_service, temp_data_dir):
    """PDF生成（ファイル出力）のテスト"""
    user_id = "test_user"

    # レポート生成
    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    # PDF生成（ファイルに保存）
    output_path = Path(temp_data_dir) / "test_report.pdf"
    pdf_bytes = report_service.generate_pdf(report_data, output_path=str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert pdf_bytes is not None


def test_generate_html_report(report_service):
    """HTMLレポート生成のテスト"""
    user_id = "test_user"

    # レポート生成
    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    # HTML生成
    html_content = report_service.generate_html_report(report_data)

    assert html_content is not None
    assert len(html_content) > 0
    assert "<!DOCTYPE html>" in html_content
    assert "Personal Recipe Intelligence" in html_content
    assert "栄養サマリー" in html_content
    assert "支出サマリー" in html_content
    assert "目標サマリー" in html_content


def test_generate_markdown_report(report_service):
    """Markdownレポート生成のテスト"""
    user_id = "test_user"

    # レポート生成
    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    # Markdown生成
    markdown_content = report_service.generate_markdown_report(report_data)

    assert markdown_content is not None
    assert len(markdown_content) > 0
    assert "# Personal Recipe Intelligence" in markdown_content
    assert "## 栄養サマリー" in markdown_content
    assert "## 支出サマリー" in markdown_content
    assert "## 目標サマリー" in markdown_content
    assert "|" in markdown_content  # テーブル記法


def test_report_history_save_and_load(report_service):
    """レポート履歴の保存と読み込みテスト"""
    user_id = "test_user"

    # レポート生成（自動的に履歴に保存される）
    report_data1 = report_service.generate_weekly_report(user_id=user_id, week_offset=0)
    report_data2 = report_service.generate_monthly_report(
        user_id=user_id, month_offset=0
    )

    # 履歴取得
    history = report_service.get_report_history(user_id=user_id)

    assert len(history) >= 2
    assert any(h["report_id"] == report_data1.report_id for h in history)
    assert any(h["report_id"] == report_data2.report_id for h in history)


def test_get_report_history_limit(report_service):
    """レポート履歴取得の件数制限テスト"""
    user_id = "test_user"

    # 複数のレポートを生成
    for i in range(5):
        report_service.generate_weekly_report(user_id=user_id, week_offset=-i)

    # 履歴取得（制限あり）
    history = report_service.get_report_history(user_id=user_id, limit=3)

    assert len(history) == 3


def test_get_report_by_id(report_service):
    """レポートID検索のテスト"""
    user_id = "test_user"

    # レポート生成
    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    # レポートID検索
    found_report = report_service.get_report_by_id(report_data.report_id)

    assert found_report is not None
    assert found_report["report_id"] == report_data.report_id


def test_get_report_by_id_not_found(report_service):
    """レポートID検索（存在しない）のテスト"""
    found_report = report_service.get_report_by_id("non_existent_id")

    assert found_report is None


def test_multiple_users_report_history(report_service):
    """複数ユーザーのレポート履歴テスト"""
    user1 = "user_001"
    user2 = "user_002"

    # ユーザー1のレポート
    report_service.generate_weekly_report(user_id=user1, week_offset=0)
    report_service.generate_weekly_report(user_id=user1, week_offset=-1)

    # ユーザー2のレポート
    report_service.generate_weekly_report(user_id=user2, week_offset=0)

    # それぞれの履歴取得
    history1 = report_service.get_report_history(user_id=user1)
    history2 = report_service.get_report_history(user_id=user2)

    assert len(history1) == 2
    assert len(history2) == 1


def test_report_date_validation(report_service):
    """レポート日付の妥当性テスト"""
    user_id = "test_user"

    # 週次レポート
    weekly_report = report_service.generate_weekly_report(
        user_id=user_id, week_offset=0
    )
    start_dt = datetime.strptime(weekly_report.start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(weekly_report.end_date, "%Y-%m-%d")

    # 週次は7日間
    assert (end_dt - start_dt).days == 6

    # 月次レポート
    monthly_report = report_service.generate_monthly_report(
        user_id=user_id, month_offset=0
    )

    # 月初から始まること
    assert monthly_report.start_date.endswith("-01")


def test_expense_summary_structure(report_service):
    """支出サマリー構造のテスト"""
    user_id = "test_user"

    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    expense = report_data.expense_summary

    assert expense.total_expense > 0
    assert expense.avg_daily_expense > 0
    assert expense.meal_count > 0
    assert expense.avg_expense_per_meal > 0


def test_report_id_uniqueness(report_service):
    """レポートIDの一意性テスト"""
    user_id = "test_user"

    # 同じ条件で複数回生成
    report1 = report_service.generate_weekly_report(user_id=user_id, week_offset=0)
    report2 = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    # IDが異なること
    assert report1.report_id != report2.report_id


def test_html_report_encoding(report_service):
    """HTMLレポートのエンコーディングテスト"""
    user_id = "test_user"

    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)
    html_content = report_service.generate_html_report(report_data)

    # UTF-8が指定されていること
    assert 'charset="UTF-8"' in html_content

    # 日本語が含まれていること
    assert "栄養" in html_content
    assert "カロリー" in html_content


def test_markdown_report_table_format(report_service):
    """Markdownレポートのテーブル形式テスト"""
    user_id = "test_user"

    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)
    markdown_content = report_service.generate_markdown_report(report_data)

    # Markdownテーブルの行が存在すること
    lines = markdown_content.split("\n")
    table_lines = [line for line in lines if "|" in line]

    assert len(table_lines) > 0


def test_recommendations_not_empty(report_service):
    """レコメンデーションが空でないことのテスト"""
    user_id = "test_user"

    report_data = report_service.generate_weekly_report(user_id=user_id, week_offset=0)

    # 必ず何らかのレコメンデーションが返されること
    assert len(report_data.recommendations) > 0

    # すべてのレコメンデーションが文字列であること
    for rec in report_data.recommendations:
        assert isinstance(rec, str)
        assert len(rec) > 10  # 意味のある長さ


def test_report_history_sorted_by_date(report_service):
    """レポート履歴が日付順にソートされることのテスト"""
    user_id = "test_user"

    # 複数のレポートを生成
    for i in range(3):
        report_service.generate_weekly_report(user_id=user_id, week_offset=-i)

    history = report_service.get_report_history(user_id=user_id)

    # 最新が先頭に来ること
    for i in range(len(history) - 1):
        current = datetime.fromisoformat(history[i]["generated_at"])
        next_item = datetime.fromisoformat(history[i + 1]["generated_at"])
        assert current >= next_item


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

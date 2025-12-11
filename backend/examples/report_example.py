"""
レポート機能の使用例

このスクリプトは、レポート生成機能の基本的な使い方を示します。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.report_service import ReportService  # noqa: E402
from backend.services.nutrition_service import NutritionService  # noqa: E402
from backend.services.goal_service import GoalService  # noqa: E402
from datetime import datetime  # noqa: E402


def main():
    """メイン関数"""
    print("=" * 80)
    print("レポート機能の使用例")
    print("=" * 80)

    # サービス初期化
    print("\n[1] サービス初期化...")
    nutrition_service = NutritionService()
    goal_service = GoalService()
    report_service = ReportService(
        nutrition_service=nutrition_service, goal_service=goal_service
    )
    print("✓ サービス初期化完了")

    # ユーザーID
    user_id = "example_user_001"

    # 週次レポート生成
    print("\n[2] 週次レポート生成...")
    weekly_report = report_service.generate_weekly_report(
        user_id=user_id, week_offset=0
    )
    print("✓ 週次レポート生成完了")
    print(f"  - レポートID: {weekly_report.report_id}")
    print(f"  - 期間: {weekly_report.start_date} 〜 {weekly_report.end_date}")
    print(f"  - 総カロリー: {weekly_report.nutrition_summary.total_calories:.1f} kcal")
    print(
        f"  - 1日平均カロリー: {weekly_report.nutrition_summary.avg_daily_calories:.1f} kcal"
    )

    # 月次レポート生成
    print("\n[3] 月次レポート生成...")
    monthly_report = report_service.generate_monthly_report(
        user_id=user_id, month_offset=0
    )
    print("✓ 月次レポート生成完了")
    print(f"  - レポートID: {monthly_report.report_id}")
    print(f"  - 期間: {monthly_report.start_date} 〜 {monthly_report.end_date}")

    # カスタム期間レポート生成
    print("\n[4] カスタム期間レポート生成...")
    custom_report = report_service.generate_custom_report(
        user_id=user_id, start_date="2025-01-01", end_date="2025-01-15"
    )
    print("✓ カスタムレポート生成完了")
    print(f"  - レポートID: {custom_report.report_id}")
    print(f"  - 期間: {custom_report.start_date} 〜 {custom_report.end_date}")

    # PDF 生成
    print("\n[5] PDF レポート生成...")
    pdf_path = (
        Path("data/reports")
        / f"example_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    pdf_bytes = report_service.generate_pdf(weekly_report, output_path=str(pdf_path))
    print("✓ PDF生成完了")
    print(f"  - ファイルパス: {pdf_path}")
    print(f"  - ファイルサイズ: {len(pdf_bytes) / 1024:.2f} KB")

    # HTML 生成
    print("\n[6] HTML レポート生成...")
    html_path = (
        Path("data/reports")
        / f"example_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )
    html_content = report_service.generate_html_report(weekly_report)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✓ HTML生成完了")
    print(f"  - ファイルパス: {html_path}")
    print(f"  - ファイルサイズ: {len(html_content) / 1024:.2f} KB")

    # Markdown 生成
    print("\n[7] Markdown レポート生成...")
    markdown_path = (
        Path("data/reports")
        / f"example_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    markdown_content = report_service.generate_markdown_report(weekly_report)

    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print("✓ Markdown生成完了")
    print(f"  - ファイルパス: {markdown_path}")
    print(f"  - ファイルサイズ: {len(markdown_content) / 1024:.2f} KB")

    # レポート履歴取得
    print("\n[8] レポート履歴取得...")
    history = report_service.get_report_history(user_id=user_id, limit=10)
    print("✓ レポート履歴取得完了")
    print(f"  - 履歴件数: {len(history)} 件")

    if history:
        print("\n  最新のレポート:")
        latest = history[0]
        print(f"    - レポートID: {latest['report_id']}")
        print(f"    - タイプ: {latest['report_type']}")
        print(f"    - 期間: {latest['start_date']} 〜 {latest['end_date']}")
        print(f"    - 生成日時: {latest['generated_at']}")

    # レポート詳細表示
    print("\n[9] レポート詳細...")
    print("\n  栄養サマリー:")
    print(
        f"    - 総カロリー: {weekly_report.nutrition_summary.total_calories:.1f} kcal"
    )
    print(f"    - 総タンパク質: {weekly_report.nutrition_summary.total_protein:.1f} g")
    print(f"    - 総脂質: {weekly_report.nutrition_summary.total_fat:.1f} g")
    print(f"    - 総炭水化物: {weekly_report.nutrition_summary.total_carbs:.1f} g")

    print("\n  支出サマリー:")
    print(f"    - 総支出: ¥{weekly_report.expense_summary.total_expense:,.0f}")
    print(f"    - 1日平均: ¥{weekly_report.expense_summary.avg_daily_expense:,.0f}")
    print(f"    - 食事回数: {weekly_report.expense_summary.meal_count} 回")
    print(f"    - 1食平均: ¥{weekly_report.expense_summary.avg_expense_per_meal:,.0f}")

    print("\n  目標サマリー:")
    print(f"    - 総目標数: {weekly_report.goal_summary.total_goals} 件")
    print(f"    - 完了: {weekly_report.goal_summary.completed_goals} 件")
    print(f"    - 進行中: {weekly_report.goal_summary.in_progress_goals} 件")
    print(f"    - 達成率: {weekly_report.goal_summary.completion_rate:.1f}%")

    print("\n  アドバイス:")
    for i, rec in enumerate(weekly_report.recommendations, 1):
        print(f"    {i}. {rec}")

    # まとめ
    print("\n" + "=" * 80)
    print("レポート生成完了！")
    print("=" * 80)
    print("\n生成されたファイル:")
    print(f"  - PDF: {pdf_path}")
    print(f"  - HTML: {html_path}")
    print(f"  - Markdown: {markdown_path}")
    print(f"\n履歴件数: {len(history)} 件")
    print("\n✓ すべての処理が正常に完了しました")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

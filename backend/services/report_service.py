"""
レポート生成サービス

週次・月次レポートの生成、PDF出力、レポート履歴管理を提供する。
"""

import io
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER

from backend.services.nutrition_service import NutritionService
from backend.services.goal_service import GoalService


@dataclass
class NutritionSummary:
    """栄養サマリー"""

    total_calories: float
    total_protein: float
    total_fat: float
    total_carbs: float
    avg_daily_calories: float
    avg_daily_protein: float
    avg_daily_fat: float
    avg_daily_carbs: float


@dataclass
class ExpenseSummary:
    """支出サマリー"""

    total_expense: float
    avg_daily_expense: float
    meal_count: int
    avg_expense_per_meal: float


@dataclass
class GoalSummary:
    """目標サマリー"""

    total_goals: int
    completed_goals: int
    in_progress_goals: int
    completion_rate: float
    goal_details: List[Dict[str, Any]]


@dataclass
class ReportData:
    """レポートデータ"""

    report_id: str
    report_type: str  # weekly, monthly, custom
    start_date: str
    end_date: str
    generated_at: str
    nutrition_summary: NutritionSummary
    expense_summary: ExpenseSummary
    goal_summary: GoalSummary
    recommendations: List[str]


class ReportService:
    """レポート生成サービス"""

    def __init__(
        self,
        nutrition_service: NutritionService,
        goal_service: GoalService,
        data_dir: str = "data",
    ):
        self.nutrition_service = nutrition_service
        self.goal_service = goal_service
        self.data_dir = Path(data_dir)
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.reports_dir / "history.json"

        # 日本語フォント登録（存在する場合）
        self._register_japanese_fonts()

    def _register_japanese_fonts(self) -> None:
        """日本語フォントを登録"""
        font_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansJP-Regular.otf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for font_path in font_paths:
            if Path(font_path).exists():
                try:
                    if font_path.endswith(".ttc"):
                        # TTC フォントの場合
                        pdfmetrics.registerFont(
                            TTFont("Japanese", font_path, subfontIndex=0)
                        )
                    else:
                        pdfmetrics.registerFont(TTFont("Japanese", font_path))
                    print(f"Registered font: {font_path}")
                    return
                except Exception as e:
                    print(f"Failed to register font {font_path}: {e}")

        # フォールバック（標準フォント）
        print("Warning: Japanese font not found, using default font")

    def generate_weekly_report(self, user_id: str, week_offset: int = 0) -> ReportData:
        """
        週次レポートを生成

        Args:
          user_id: ユーザーID
          week_offset: 週オフセット（0=今週、-1=先週）

        Returns:
          ReportData: レポートデータ
        """
        # 期間計算
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday() + (7 * abs(week_offset)))
        end_of_week = start_of_week + timedelta(days=6)

        start_date = start_of_week.strftime("%Y-%m-%d")
        end_date = end_of_week.strftime("%Y-%m-%d")

        return self._generate_report(
            user_id=user_id,
            report_type="weekly",
            start_date=start_date,
            end_date=end_date,
        )

    def generate_monthly_report(
        self, user_id: str, month_offset: int = 0
    ) -> ReportData:
        """
        月次レポートを生成

        Args:
          user_id: ユーザーID
          month_offset: 月オフセット（0=今月、-1=先月）

        Returns:
          ReportData: レポートデータ
        """
        # 期間計算
        today = datetime.now()
        year = today.year
        month = today.month + month_offset

        # 月の調整
        while month < 1:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1

        start_date = f"{year}-{month:02d}-01"

        # 月末日を計算
        if month == 12:
            next_month = f"{year + 1}-01-01"
        else:
            next_month = f"{year}-{month + 1:02d}-01"

        end_date = (
            datetime.strptime(next_month, "%Y-%m-%d") - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        return self._generate_report(
            user_id=user_id,
            report_type="monthly",
            start_date=start_date,
            end_date=end_date,
        )

    def generate_custom_report(
        self, user_id: str, start_date: str, end_date: str
    ) -> ReportData:
        """
        カスタム期間レポートを生成

        Args:
          user_id: ユーザーID
          start_date: 開始日（YYYY-MM-DD）
          end_date: 終了日（YYYY-MM-DD）

        Returns:
          ReportData: レポートデータ
        """
        return self._generate_report(
            user_id=user_id,
            report_type="custom",
            start_date=start_date,
            end_date=end_date,
        )

    def _generate_report(
        self, user_id: str, report_type: str, start_date: str, end_date: str
    ) -> ReportData:
        """
        レポートを生成（内部メソッド）

        Args:
          user_id: ユーザーID
          report_type: レポートタイプ
          start_date: 開始日
          end_date: 終了日

        Returns:
          ReportData: レポートデータ
        """
        # 栄養サマリーを取得
        nutrition_data = self.nutrition_service.get_nutrition_summary(
            user_id=user_id, start_date=start_date, end_date=end_date
        )

        # 日数を計算
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days + 1

        nutrition_summary = NutritionSummary(
            total_calories=nutrition_data.get("total_calories", 0),
            total_protein=nutrition_data.get("total_protein", 0),
            total_fat=nutrition_data.get("total_fat", 0),
            total_carbs=nutrition_data.get("total_carbs", 0),
            avg_daily_calories=(
                nutrition_data.get("total_calories", 0) / days if days > 0 else 0
            ),
            avg_daily_protein=(
                nutrition_data.get("total_protein", 0) / days if days > 0 else 0
            ),
            avg_daily_fat=nutrition_data.get("total_fat", 0) / days if days > 0 else 0,
            avg_daily_carbs=(
                nutrition_data.get("total_carbs", 0) / days if days > 0 else 0
            ),
        )

        # 支出サマリー（仮実装 - 実際は meal_plan から取得）
        expense_summary = ExpenseSummary(
            total_expense=15000.0,  # ダミーデータ
            avg_daily_expense=15000.0 / days if days > 0 else 0,
            meal_count=21,  # ダミーデータ
            avg_expense_per_meal=15000.0 / 21 if 21 > 0 else 0,
        )

        # 目標サマリーを取得
        goals = self.goal_service.get_goals(user_id)
        completed = sum(1 for g in goals if g.get("status") == "completed")
        in_progress = sum(1 for g in goals if g.get("status") == "in_progress")

        goal_summary = GoalSummary(
            total_goals=len(goals),
            completed_goals=completed,
            in_progress_goals=in_progress,
            completion_rate=completed / len(goals) * 100 if len(goals) > 0 else 0,
            goal_details=[
                {
                    "title": g.get("title", ""),
                    "status": g.get("status", ""),
                    "progress": g.get("progress", 0),
                }
                for g in goals[:5]  # 上位5件
            ],
        )

        # レコメンデーション生成
        recommendations = self._generate_recommendations(
            nutrition_summary, expense_summary, goal_summary
        )

        # レポートID生成
        report_id = f"{report_type}_{user_id}_{start_date}_{end_date}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # レポートデータ作成
        report_data = ReportData(
            report_id=report_id,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now().isoformat(),
            nutrition_summary=nutrition_summary,
            expense_summary=expense_summary,
            goal_summary=goal_summary,
            recommendations=recommendations,
        )

        # レポート履歴に保存
        self._save_to_history(user_id, report_data)

        return report_data

    def _generate_recommendations(
        self, nutrition: NutritionSummary, expense: ExpenseSummary, goal: GoalSummary
    ) -> List[str]:
        """
        レコメンデーションを生成

        Args:
          nutrition: 栄養サマリー
          expense: 支出サマリー
          goal: 目標サマリー

        Returns:
          List[str]: レコメンデーションリスト
        """
        recommendations = []

        # 栄養バランスチェック
        if nutrition.avg_daily_calories < 1800:
            recommendations.append(
                "カロリー摂取量が少ない傾向にあります。バランスの良い食事を心がけましょう。"
            )
        elif nutrition.avg_daily_calories > 2500:
            recommendations.append(
                "カロリー摂取量が多めです。野菜中心の食事を増やすことをお勧めします。"
            )

        if nutrition.avg_daily_protein < 50:
            recommendations.append(
                "タンパク質が不足しています。魚・肉・豆類を積極的に摂取しましょう。"
            )

        # 支出チェック
        if expense.avg_expense_per_meal > 1000:
            recommendations.append(
                "1食あたりの支出が高めです。自炊を増やすことでコスト削減が可能です。"
            )

        # 目標達成率チェック
        if goal.completion_rate < 50 and goal.total_goals > 0:
            recommendations.append(
                "目標達成率が低めです。小さな目標から始めて達成感を積み重ねましょう。"
            )
        elif goal.completion_rate >= 80:
            recommendations.append("素晴らしい達成率です！この調子で継続しましょう。")

        if not recommendations:
            recommendations.append(
                "バランスの取れた食生活を継続できています。この調子で頑張りましょう！"
            )

        return recommendations

    def generate_pdf(
        self, report_data: ReportData, output_path: Optional[str] = None
    ) -> bytes:
        """
        PDF レポートを生成

        Args:
          report_data: レポートデータ
          output_path: 出力パス（指定しない場合はバイトストリームを返す）

        Returns:
          bytes: PDF バイナリデータ
        """
        # バッファを作成
        buffer = io.BytesIO()

        # PDF ドキュメントを作成
        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=A4)

        # スタイル定義
        styles = getSampleStyleSheet()

        # 日本語対応スタイル
        try:
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontName="Japanese",
                fontSize=20,
                alignment=TA_CENTER,
                spaceAfter=12,
            )
            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontName="Japanese",
                fontSize=14,
                spaceAfter=10,
            )
            normal_style = ParagraphStyle(
                "CustomNormal",
                parent=styles["Normal"],
                fontName="Japanese",
                fontSize=10,
                leading=14,
            )
        except Exception:
            # フォールバック
            title_style = styles["Heading1"]
            heading_style = styles["Heading2"]
            normal_style = styles["Normal"]

        # コンテンツ構築
        story = []

        # タイトル
        report_type_ja = {
            "weekly": "週次レポート",
            "monthly": "月次レポート",
            "custom": "カスタムレポート",
        }.get(report_data.report_type, "レポート")

        story.append(Paragraph("Personal Recipe Intelligence", title_style))
        story.append(Paragraph(report_type_ja, heading_style))
        story.append(Spacer(1, 12))

        # 期間情報
        story.append(
            Paragraph(
                f"期間: {report_data.start_date} 〜 {report_data.end_date}",
                normal_style,
            )
        )
        story.append(Paragraph(f"生成日時: {report_data.generated_at}", normal_style))
        story.append(Spacer(1, 20))

        # 栄養サマリー
        story.append(Paragraph("栄養サマリー", heading_style))
        nutrition_data = [
            ["項目", "合計", "1日平均"],
            [
                "カロリー",
                f"{report_data.nutrition_summary.total_calories:.1f} kcal",
                f"{report_data.nutrition_summary.avg_daily_calories:.1f} kcal",
            ],
            [
                "タンパク質",
                f"{report_data.nutrition_summary.total_protein:.1f} g",
                f"{report_data.nutrition_summary.avg_daily_protein:.1f} g",
            ],
            [
                "脂質",
                f"{report_data.nutrition_summary.total_fat:.1f} g",
                f"{report_data.nutrition_summary.avg_daily_fat:.1f} g",
            ],
            [
                "炭水化物",
                f"{report_data.nutrition_summary.total_carbs:.1f} g",
                f"{report_data.nutrition_summary.avg_daily_carbs:.1f} g",
            ],
        ]
        nutrition_table = Table(nutrition_data, colWidths=[100, 100, 100])
        nutrition_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        (
                            "Japanese"
                            if "Japanese" in pdfmetrics.getRegisteredFontNames()
                            else "Helvetica"
                        ),
                    ),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(nutrition_table)
        story.append(Spacer(1, 20))

        # 支出サマリー
        story.append(Paragraph("支出サマリー", heading_style))
        expense_data = [
            ["項目", "金額"],
            ["総支出", f"¥{report_data.expense_summary.total_expense:,.0f}"],
            ["1日平均", f"¥{report_data.expense_summary.avg_daily_expense:,.0f}"],
            ["食事回数", f"{report_data.expense_summary.meal_count} 回"],
            ["1食平均", f"¥{report_data.expense_summary.avg_expense_per_meal:,.0f}"],
        ]
        expense_table = Table(expense_data, colWidths=[150, 150])
        expense_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        (
                            "Japanese"
                            if "Japanese" in pdfmetrics.getRegisteredFontNames()
                            else "Helvetica"
                        ),
                    ),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(expense_table)
        story.append(Spacer(1, 20))

        # 目標サマリー
        story.append(Paragraph("目標サマリー", heading_style))
        goal_data = [
            ["項目", "値"],
            ["総目標数", f"{report_data.goal_summary.total_goals} 件"],
            ["完了", f"{report_data.goal_summary.completed_goals} 件"],
            ["進行中", f"{report_data.goal_summary.in_progress_goals} 件"],
            ["達成率", f"{report_data.goal_summary.completion_rate:.1f}%"],
        ]
        goal_table = Table(goal_data, colWidths=[150, 150])
        goal_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        (
                            "Japanese"
                            if "Japanese" in pdfmetrics.getRegisteredFontNames()
                            else "Helvetica"
                        ),
                    ),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(goal_table)
        story.append(Spacer(1, 20))

        # レコメンデーション
        story.append(Paragraph("アドバイス", heading_style))
        for i, rec in enumerate(report_data.recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", normal_style))
            story.append(Spacer(1, 6))

        # PDF ビルド
        doc.build(story)

        if output_path:
            return Path(output_path).read_bytes()
        else:
            pdf_data = buffer.getvalue()
            buffer.close()
            return pdf_data

    def generate_html_report(self, report_data: ReportData) -> str:
        """
        HTML レポートを生成

        Args:
          report_data: レポートデータ

        Returns:
          str: HTML 文字列
        """
        report_type_ja = {
            "weekly": "週次レポート",
            "monthly": "月次レポート",
            "custom": "カスタムレポート",
        }.get(report_data.report_type, "レポート")

        html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{report_type_ja} - Personal Recipe Intelligence</title>
  <style>
    body {{
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
      background-color: #f5f5f5;
    }}
    .header {{
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      border-radius: 10px;
      text-align: center;
      margin-bottom: 30px;
    }}
    .header h1 {{
      margin: 0;
      font-size: 2em;
    }}
    .header p {{
      margin: 10px 0 0 0;
      opacity: 0.9;
    }}
    .section {{
      background: white;
      padding: 25px;
      margin-bottom: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .section h2 {{
      color: #667eea;
      border-bottom: 2px solid #667eea;
      padding-bottom: 10px;
      margin-top: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
    }}
    th, td {{
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #ddd;
    }}
    th {{
      background-color: #667eea;
      color: white;
    }}
    tr:hover {{
      background-color: #f5f5f5;
    }}
    .recommendations {{
      list-style: none;
      padding: 0;
    }}
    .recommendations li {{
      padding: 15px;
      margin: 10px 0;
      background: #f8f9fa;
      border-left: 4px solid #667eea;
      border-radius: 4px;
    }}
    .stat-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-top: 15px;
    }}
    .stat-card {{
      background: #f8f9fa;
      padding: 15px;
      border-radius: 8px;
      text-align: center;
    }}
    .stat-card .value {{
      font-size: 2em;
      font-weight: bold;
      color: #667eea;
      margin: 10px 0;
    }}
    .stat-card .label {{
      color: #666;
      font-size: 0.9em;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Personal Recipe Intelligence</h1>
    <p>{report_type_ja}</p>
    <p>期間: {report_data.start_date} 〜 {report_data.end_date}</p>
    <p>生成日時: {report_data.generated_at}</p>
  </div>

  <div class="section">
    <h2>栄養サマリー</h2>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="label">総カロリー</div>
        <div class="value">{report_data.nutrition_summary.total_calories:.0f}</div>
        <div class="label">kcal</div>
      </div>
      <div class="stat-card">
        <div class="label">1日平均カロリー</div>
        <div class="value">{report_data.nutrition_summary.avg_daily_calories:.0f}</div>
        <div class="label">kcal/日</div>
      </div>
      <div class="stat-card">
        <div class="label">総タンパク質</div>
        <div class="value">{report_data.nutrition_summary.total_protein:.1f}</div>
        <div class="label">g</div>
      </div>
      <div class="stat-card">
        <div class="label">1日平均タンパク質</div>
        <div class="value">{report_data.nutrition_summary.avg_daily_protein:.1f}</div>
        <div class="label">g/日</div>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th>項目</th>
          <th>合計</th>
          <th>1日平均</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>カロリー</td>
          <td>{report_data.nutrition_summary.total_calories:.1f} kcal</td>
          <td>{report_data.nutrition_summary.avg_daily_calories:.1f} kcal</td>
        </tr>
        <tr>
          <td>タンパク質</td>
          <td>{report_data.nutrition_summary.total_protein:.1f} g</td>
          <td>{report_data.nutrition_summary.avg_daily_protein:.1f} g</td>
        </tr>
        <tr>
          <td>脂質</td>
          <td>{report_data.nutrition_summary.total_fat:.1f} g</td>
          <td>{report_data.nutrition_summary.avg_daily_fat:.1f} g</td>
        </tr>
        <tr>
          <td>炭水化物</td>
          <td>{report_data.nutrition_summary.total_carbs:.1f} g</td>
          <td>{report_data.nutrition_summary.avg_daily_carbs:.1f} g</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>支出サマリー</h2>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="label">総支出</div>
        <div class="value">¥{report_data.expense_summary.total_expense:,.0f}</div>
      </div>
      <div class="stat-card">
        <div class="label">1日平均</div>
        <div class="value">¥{report_data.expense_summary.avg_daily_expense:,.0f}</div>
      </div>
      <div class="stat-card">
        <div class="label">食事回数</div>
        <div class="value">{report_data.expense_summary.meal_count}</div>
        <div class="label">回</div>
      </div>
      <div class="stat-card">
        <div class="label">1食平均</div>
        <div class="value">¥{report_data.expense_summary.avg_expense_per_meal:,.0f}</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>目標サマリー</h2>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="label">総目標数</div>
        <div class="value">{report_data.goal_summary.total_goals}</div>
        <div class="label">件</div>
      </div>
      <div class="stat-card">
        <div class="label">完了</div>
        <div class="value">{report_data.goal_summary.completed_goals}</div>
        <div class="label">件</div>
      </div>
      <div class="stat-card">
        <div class="label">進行中</div>
        <div class="value">{report_data.goal_summary.in_progress_goals}</div>
        <div class="label">件</div>
      </div>
      <div class="stat-card">
        <div class="label">達成率</div>
        <div class="value">{report_data.goal_summary.completion_rate:.1f}%</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>アドバイス</h2>
    <ul class="recommendations">
"""
        for rec in report_data.recommendations:
            html += f"      <li>{rec}</li>\n"

        html += """
    </ul>
  </div>
</body>
</html>
"""
        return html

    def generate_markdown_report(self, report_data: ReportData) -> str:
        """
        Markdown レポートを生成

        Args:
          report_data: レポートデータ

        Returns:
          str: Markdown 文字列
        """
        report_type_ja = {
            "weekly": "週次レポート",
            "monthly": "月次レポート",
            "custom": "カスタムレポート",
        }.get(report_data.report_type, "レポート")

        md = f"""# Personal Recipe Intelligence - {report_type_ja}

**期間**: {report_data.start_date} 〜 {report_data.end_date}
**生成日時**: {report_data.generated_at}

---

## 栄養サマリー

| 項目 | 合計 | 1日平均 |
|------|------|---------|
| カロリー | {report_data.nutrition_summary.total_calories:.1f} kcal | {report_data.nutrition_summary.avg_daily_calories:.1f} kcal |
| タンパク質 | {report_data.nutrition_summary.total_protein:.1f} g | {report_data.nutrition_summary.avg_daily_protein:.1f} g |
| 脂質 | {report_data.nutrition_summary.total_fat:.1f} g | {report_data.nutrition_summary.avg_daily_fat:.1f} g |
| 炭水化物 | {report_data.nutrition_summary.total_carbs:.1f} g | {report_data.nutrition_summary.avg_daily_carbs:.1f} g |

---

## 支出サマリー

| 項目 | 金額 |
|------|------|
| 総支出 | ¥{report_data.expense_summary.total_expense:,.0f} |
| 1日平均 | ¥{report_data.expense_summary.avg_daily_expense:,.0f} |
| 食事回数 | {report_data.expense_summary.meal_count} 回 |
| 1食平均 | ¥{report_data.expense_summary.avg_expense_per_meal:,.0f} |

---

## 目標サマリー

| 項目 | 値 |
|------|------|
| 総目標数 | {report_data.goal_summary.total_goals} 件 |
| 完了 | {report_data.goal_summary.completed_goals} 件 |
| 進行中 | {report_data.goal_summary.in_progress_goals} 件 |
| 達成率 | {report_data.goal_summary.completion_rate:.1f}% |

---

## アドバイス

"""
        for i, rec in enumerate(report_data.recommendations, 1):
            md += f"{i}. {rec}\n"

        return md

    def _save_to_history(self, user_id: str, report_data: ReportData) -> None:
        """
        レポート履歴に保存

        Args:
          user_id: ユーザーID
          report_data: レポートデータ
        """
        # 履歴ファイル読み込み
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {}

        # ユーザーごとの履歴
        if user_id not in history:
            history[user_id] = []

        # レポート追加
        history[user_id].append(
            {
                "report_id": report_data.report_id,
                "report_type": report_data.report_type,
                "start_date": report_data.start_date,
                "end_date": report_data.end_date,
                "generated_at": report_data.generated_at,
            }
        )

        # 最新100件のみ保持
        history[user_id] = history[user_id][-100:]

        # 保存
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_report_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        レポート履歴を取得

        Args:
          user_id: ユーザーID
          limit: 取得件数

        Returns:
          List[Dict[str, Any]]: レポート履歴
        """
        if not self.history_file.exists():
            return []

        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)

        user_history = history.get(user_id, [])
        return sorted(user_history, key=lambda x: x["generated_at"], reverse=True)[
            :limit
        ]

    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        レポートIDからレポートを取得

        Args:
          report_id: レポートID

        Returns:
          Optional[Dict[str, Any]]: レポートデータ（存在しない場合はNone）
        """
        if not self.history_file.exists():
            return None

        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)

        for user_id, reports in history.items():
            for report in reports:
                if report["report_id"] == report_id:
                    return report

        return None

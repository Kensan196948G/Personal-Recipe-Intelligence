"""
レポートAPI ルーター

週次・月次・カスタムレポートの生成とPDF出力を提供する。
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
from datetime import datetime

from backend.services.report_service import ReportService
from backend.services.nutrition_service import NutritionService
from backend.services.goal_service import GoalService


router = APIRouter(prefix="/api/v1/report", tags=["report"])


# サービスインスタンス（依存性注入を想定）
nutrition_service = NutritionService()
goal_service = GoalService()
report_service = ReportService(
    nutrition_service=nutrition_service, goal_service=goal_service
)


class ReportResponse(BaseModel):
    """レポートレスポンス"""

    status: str = "ok"
    data: dict
    error: Optional[str] = None


class ReportHistoryResponse(BaseModel):
    """レポート履歴レスポンス"""

    status: str = "ok"
    data: list
    error: Optional[str] = None


class CustomReportRequest(BaseModel):
    """カスタムレポートリクエスト"""

    user_id: str = Field(..., description="ユーザーID")
    start_date: str = Field(..., description="開始日（YYYY-MM-DD）")
    end_date: str = Field(..., description="終了日（YYYY-MM-DD）")


@router.get("/weekly", response_model=ReportResponse)
async def get_weekly_report(
    user_id: str = Query(..., description="ユーザーID"),
    week_offset: int = Query(0, description="週オフセット（0=今週、-1=先週）"),
):
    """
    週次レポートを取得

    Args:
      user_id: ユーザーID
      week_offset: 週オフセット

    Returns:
      ReportResponse: 週次レポート
    """
    try:
        report_data = report_service.generate_weekly_report(
            user_id=user_id, week_offset=week_offset
        )

        return ReportResponse(
            status="ok",
            data={
                "report_id": report_data.report_id,
                "report_type": report_data.report_type,
                "start_date": report_data.start_date,
                "end_date": report_data.end_date,
                "generated_at": report_data.generated_at,
                "nutrition_summary": {
                    "total_calories": report_data.nutrition_summary.total_calories,
                    "total_protein": report_data.nutrition_summary.total_protein,
                    "total_fat": report_data.nutrition_summary.total_fat,
                    "total_carbs": report_data.nutrition_summary.total_carbs,
                    "avg_daily_calories": report_data.nutrition_summary.avg_daily_calories,
                    "avg_daily_protein": report_data.nutrition_summary.avg_daily_protein,
                    "avg_daily_fat": report_data.nutrition_summary.avg_daily_fat,
                    "avg_daily_carbs": report_data.nutrition_summary.avg_daily_carbs,
                },
                "expense_summary": {
                    "total_expense": report_data.expense_summary.total_expense,
                    "avg_daily_expense": report_data.expense_summary.avg_daily_expense,
                    "meal_count": report_data.expense_summary.meal_count,
                    "avg_expense_per_meal": report_data.expense_summary.avg_expense_per_meal,
                },
                "goal_summary": {
                    "total_goals": report_data.goal_summary.total_goals,
                    "completed_goals": report_data.goal_summary.completed_goals,
                    "in_progress_goals": report_data.goal_summary.in_progress_goals,
                    "completion_rate": report_data.goal_summary.completion_rate,
                    "goal_details": report_data.goal_summary.goal_details,
                },
                "recommendations": report_data.recommendations,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"週次レポート生成エラー: {str(e)}")


@router.get("/monthly", response_model=ReportResponse)
async def get_monthly_report(
    user_id: str = Query(..., description="ユーザーID"),
    month_offset: int = Query(0, description="月オフセット（0=今月、-1=先月）"),
):
    """
    月次レポートを取得

    Args:
      user_id: ユーザーID
      month_offset: 月オフセット

    Returns:
      ReportResponse: 月次レポート
    """
    try:
        report_data = report_service.generate_monthly_report(
            user_id=user_id, month_offset=month_offset
        )

        return ReportResponse(
            status="ok",
            data={
                "report_id": report_data.report_id,
                "report_type": report_data.report_type,
                "start_date": report_data.start_date,
                "end_date": report_data.end_date,
                "generated_at": report_data.generated_at,
                "nutrition_summary": {
                    "total_calories": report_data.nutrition_summary.total_calories,
                    "total_protein": report_data.nutrition_summary.total_protein,
                    "total_fat": report_data.nutrition_summary.total_fat,
                    "total_carbs": report_data.nutrition_summary.total_carbs,
                    "avg_daily_calories": report_data.nutrition_summary.avg_daily_calories,
                    "avg_daily_protein": report_data.nutrition_summary.avg_daily_protein,
                    "avg_daily_fat": report_data.nutrition_summary.avg_daily_fat,
                    "avg_daily_carbs": report_data.nutrition_summary.avg_daily_carbs,
                },
                "expense_summary": {
                    "total_expense": report_data.expense_summary.total_expense,
                    "avg_daily_expense": report_data.expense_summary.avg_daily_expense,
                    "meal_count": report_data.expense_summary.meal_count,
                    "avg_expense_per_meal": report_data.expense_summary.avg_expense_per_meal,
                },
                "goal_summary": {
                    "total_goals": report_data.goal_summary.total_goals,
                    "completed_goals": report_data.goal_summary.completed_goals,
                    "in_progress_goals": report_data.goal_summary.in_progress_goals,
                    "completion_rate": report_data.goal_summary.completion_rate,
                    "goal_details": report_data.goal_summary.goal_details,
                },
                "recommendations": report_data.recommendations,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"月次レポート生成エラー: {str(e)}")


@router.post("/custom", response_model=ReportResponse)
async def generate_custom_report(request: CustomReportRequest):
    """
    カスタム期間レポートを生成

    Args:
      request: カスタムレポートリクエスト

    Returns:
      ReportResponse: カスタムレポート
    """
    try:
        # 日付検証
        try:
            datetime.strptime(request.start_date, "%Y-%m-%d")
            datetime.strptime(request.end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="日付フォーマットが不正です（YYYY-MM-DD形式で指定してください）",
            )

        report_data = report_service.generate_custom_report(
            user_id=request.user_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return ReportResponse(
            status="ok",
            data={
                "report_id": report_data.report_id,
                "report_type": report_data.report_type,
                "start_date": report_data.start_date,
                "end_date": report_data.end_date,
                "generated_at": report_data.generated_at,
                "nutrition_summary": {
                    "total_calories": report_data.nutrition_summary.total_calories,
                    "total_protein": report_data.nutrition_summary.total_protein,
                    "total_fat": report_data.nutrition_summary.total_fat,
                    "total_carbs": report_data.nutrition_summary.total_carbs,
                    "avg_daily_calories": report_data.nutrition_summary.avg_daily_calories,
                    "avg_daily_protein": report_data.nutrition_summary.avg_daily_protein,
                    "avg_daily_fat": report_data.nutrition_summary.avg_daily_fat,
                    "avg_daily_carbs": report_data.nutrition_summary.avg_daily_carbs,
                },
                "expense_summary": {
                    "total_expense": report_data.expense_summary.total_expense,
                    "avg_daily_expense": report_data.expense_summary.avg_daily_expense,
                    "meal_count": report_data.expense_summary.meal_count,
                    "avg_expense_per_meal": report_data.expense_summary.avg_expense_per_meal,
                },
                "goal_summary": {
                    "total_goals": report_data.goal_summary.total_goals,
                    "completed_goals": report_data.goal_summary.completed_goals,
                    "in_progress_goals": report_data.goal_summary.in_progress_goals,
                    "completion_rate": report_data.goal_summary.completion_rate,
                    "goal_details": report_data.goal_summary.goal_details,
                },
                "recommendations": report_data.recommendations,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"カスタムレポート生成エラー: {str(e)}"
        )


@router.get("/generate/pdf")
async def generate_pdf_report(
    user_id: str = Query(..., description="ユーザーID"),
    report_type: str = Query(
        ..., description="レポートタイプ（weekly/monthly/custom）"
    ),
    start_date: Optional[str] = Query(None, description="開始日（customの場合必須）"),
    end_date: Optional[str] = Query(None, description="終了日（customの場合必須）"),
    week_offset: int = Query(0, description="週オフセット（weeklyの場合）"),
    month_offset: int = Query(0, description="月オフセット（monthlyの場合）"),
):
    """
    PDF レポートを生成してダウンロード

    Args:
      user_id: ユーザーID
      report_type: レポートタイプ
      start_date: 開始日（カスタムレポートの場合）
      end_date: 終了日（カスタムレポートの場合）
      week_offset: 週オフセット
      month_offset: 月オフセット

    Returns:
      Response: PDF ファイル
    """
    try:
        # レポートデータ生成
        if report_type == "weekly":
            report_data = report_service.generate_weekly_report(
                user_id=user_id, week_offset=week_offset
            )
        elif report_type == "monthly":
            report_data = report_service.generate_monthly_report(
                user_id=user_id, month_offset=month_offset
            )
        elif report_type == "custom":
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=400,
                    detail="カスタムレポートには start_date と end_date が必要です",
                )
            report_data = report_service.generate_custom_report(
                user_id=user_id, start_date=start_date, end_date=end_date
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="無効なレポートタイプです（weekly/monthly/custom のいずれかを指定してください）",
            )

        # PDF 生成
        pdf_bytes = report_service.generate_pdf(report_data)

        # ファイル名生成
        filename = f"report_{report_type}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        # PDF レスポンス
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF生成エラー: {str(e)}")


@router.get("/generate/html")
async def generate_html_report(
    user_id: str = Query(..., description="ユーザーID"),
    report_type: str = Query(
        ..., description="レポートタイプ（weekly/monthly/custom）"
    ),
    start_date: Optional[str] = Query(None, description="開始日（customの場合必須）"),
    end_date: Optional[str] = Query(None, description="終了日（customの場合必須）"),
    week_offset: int = Query(0, description="週オフセット（weeklyの場合）"),
    month_offset: int = Query(0, description="月オフセット（monthlyの場合）"),
):
    """
    HTML レポートを生成

    Args:
      user_id: ユーザーID
      report_type: レポートタイプ
      start_date: 開始日（カスタムレポートの場合）
      end_date: 終了日（カスタムレポートの場合）
      week_offset: 週オフセット
      month_offset: 月オフセット

    Returns:
      Response: HTML コンテンツ
    """
    try:
        # レポートデータ生成
        if report_type == "weekly":
            report_data = report_service.generate_weekly_report(
                user_id=user_id, week_offset=week_offset
            )
        elif report_type == "monthly":
            report_data = report_service.generate_monthly_report(
                user_id=user_id, month_offset=month_offset
            )
        elif report_type == "custom":
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=400,
                    detail="カスタムレポートには start_date と end_date が必要です",
                )
            report_data = report_service.generate_custom_report(
                user_id=user_id, start_date=start_date, end_date=end_date
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="無効なレポートタイプです（weekly/monthly/custom のいずれかを指定してください）",
            )

        # HTML 生成
        html_content = report_service.generate_html_report(report_data)

        return Response(content=html_content, media_type="text/html")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML生成エラー: {str(e)}")


@router.get("/generate/markdown")
async def generate_markdown_report(
    user_id: str = Query(..., description="ユーザーID"),
    report_type: str = Query(
        ..., description="レポートタイプ（weekly/monthly/custom）"
    ),
    start_date: Optional[str] = Query(None, description="開始日（customの場合必須）"),
    end_date: Optional[str] = Query(None, description="終了日（customの場合必須）"),
    week_offset: int = Query(0, description="週オフセット（weeklyの場合）"),
    month_offset: int = Query(0, description="月オフセット（monthlyの場合）"),
):
    """
    Markdown レポートを生成

    Args:
      user_id: ユーザーID
      report_type: レポートタイプ
      start_date: 開始日（カスタムレポートの場合）
      end_date: 終了日（カスタムレポートの場合）
      week_offset: 週オフセット
      month_offset: 月オフセット

    Returns:
      Response: Markdown コンテンツ
    """
    try:
        # レポートデータ生成
        if report_type == "weekly":
            report_data = report_service.generate_weekly_report(
                user_id=user_id, week_offset=week_offset
            )
        elif report_type == "monthly":
            report_data = report_service.generate_monthly_report(
                user_id=user_id, month_offset=month_offset
            )
        elif report_type == "custom":
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=400,
                    detail="カスタムレポートには start_date と end_date が必要です",
                )
            report_data = report_service.generate_custom_report(
                user_id=user_id, start_date=start_date, end_date=end_date
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="無効なレポートタイプです（weekly/monthly/custom のいずれかを指定してください）",
            )

        # Markdown 生成
        markdown_content = report_service.generate_markdown_report(report_data)

        # ファイル名生成
        filename = f"report_{report_type}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Markdown生成エラー: {str(e)}")


@router.get("/history", response_model=ReportHistoryResponse)
async def get_report_history(
    user_id: str = Query(..., description="ユーザーID"),
    limit: int = Query(20, description="取得件数"),
):
    """
    レポート履歴を取得

    Args:
      user_id: ユーザーID
      limit: 取得件数

    Returns:
      ReportHistoryResponse: レポート履歴
    """
    try:
        history = report_service.get_report_history(user_id=user_id, limit=limit)

        return ReportHistoryResponse(status="ok", data=history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レポート履歴取得エラー: {str(e)}")


@router.get("/{report_id}")
async def get_report_by_id(report_id: str):
    """
    レポートIDからレポートを取得

    Args:
      report_id: レポートID

    Returns:
      ReportResponse: レポートデータ
    """
    try:
        report = report_service.get_report_by_id(report_id)

        if not report:
            raise HTTPException(status_code=404, detail="レポートが見つかりません")

        return ReportResponse(status="ok", data=report)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レポート取得エラー: {str(e)}")

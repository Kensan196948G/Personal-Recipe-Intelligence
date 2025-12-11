"""
食事履歴 API ルーター

食事記録、栄養摂取量の取得、傾向分析のエンドポイントを提供します。
"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.meal_history_service import MealHistoryService


router = APIRouter(prefix="/api/v1/meal-history", tags=["meal-history"])
service = MealHistoryService()


# リクエストモデル
class MealRecordRequest(BaseModel):
  """食事記録リクエスト"""

  user_id: str = Field(..., description="ユーザーID")
  recipe_id: str = Field(..., description="レシピID")
  recipe_name: str = Field(..., description="レシピ名")
  meal_type: str = Field(
    ..., description="食事タイプ", pattern="^(breakfast|lunch|dinner|snack)$"
  )
  servings: float = Field(..., gt=0, description="人前数")
  nutrition: Dict[str, float] = Field(..., description="栄養素情報")
  ingredients: List[str] = Field(..., description="食材リスト")
  consumed_at: Optional[str] = Field(None, description="食事日時（ISO8601形式）")


# レスポンスモデル
class ApiResponse(BaseModel):
  """API レスポンス"""

  status: str
  data: Optional[Dict] = None
  error: Optional[str] = None


@router.post("/record", response_model=ApiResponse)
async def record_meal(request: MealRecordRequest):
  """
  食事記録を保存

  食事内容、栄養情報、食材を記録します。
  """
  try:
    # consumed_at の検証
    if request.consumed_at:
      try:
        datetime.fromisoformat(request.consumed_at)
      except ValueError:
        raise HTTPException(
          status_code=400, detail="consumed_at must be in ISO8601 format"
        )

    record = service.record_meal(
      user_id=request.user_id,
      recipe_id=request.recipe_id,
      recipe_name=request.recipe_name,
      meal_type=request.meal_type,
      servings=request.servings,
      nutrition=request.nutrition,
      ingredients=request.ingredients,
      consumed_at=request.consumed_at,
    )

    return ApiResponse(
      status="ok",
      data={
        "id": record.id,
        "consumed_at": record.consumed_at,
        "message": "Meal recorded successfully",
      },
    )

  except Exception as e:
    return ApiResponse(status="error", error=str(e))


@router.get("/daily/{date}", response_model=ApiResponse)
async def get_daily_nutrition(
  date: str, user_id: str = Query(..., description="ユーザーID")
):
  """
  日別栄養摂取量を取得

  指定した日付の全食事記録と栄養摂取量を返します。
  """
  try:
    # 日付形式の検証
    try:
      datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
      raise HTTPException(status_code=400, detail="date must be in YYYY-MM-DD format")

    daily = service.get_daily_nutrition(user_id, date)

    return ApiResponse(
      status="ok",
      data={
        "date": daily.date,
        "total_nutrition": daily.total_nutrition,
        "meals": daily.meals,
        "meal_count": daily.meal_count,
      },
    )

  except Exception as e:
    return ApiResponse(status="error", error=str(e))


@router.get("/weekly", response_model=ApiResponse)
async def get_weekly_nutrition(
  user_id: str = Query(..., description="ユーザーID"),
  start_date: Optional[str] = Query(None, description="開始日（YYYY-MM-DD）"),
):
  """
  週間栄養摂取量を取得

  7日分の日別栄養摂取量を返します。
  start_date を省略すると、今週月曜日から取得します。
  """
  try:
    if start_date:
      try:
        datetime.strptime(start_date, "%Y-%m-%d")
      except ValueError:
        raise HTTPException(
          status_code=400, detail="start_date must be in YYYY-MM-DD format"
        )

    weekly = service.get_weekly_nutrition(user_id, start_date)

    return ApiResponse(
      status="ok",
      data={
        "period": "weekly",
        "start_date": weekly[0].date if weekly else None,
        "end_date": weekly[-1].date if weekly else None,
        "daily_data": [
          {
            "date": d.date,
            "total_nutrition": d.total_nutrition,
            "meal_count": d.meal_count,
          }
          for d in weekly
        ],
      },
    )

  except Exception as e:
    return ApiResponse(status="error", error=str(e))


@router.get("/monthly", response_model=ApiResponse)
async def get_monthly_nutrition(
  user_id: str = Query(..., description="ユーザーID"),
  year: int = Query(..., description="年", ge=2000, le=2100),
  month: int = Query(..., description="月", ge=1, le=12),
):
  """
  月間栄養摂取量を取得

  指定した月の日別栄養摂取量を返します。
  """
  try:
    monthly = service.get_monthly_nutrition(user_id, year, month)

    return ApiResponse(
      status="ok",
      data={
        "period": "monthly",
        "year": year,
        "month": month,
        "daily_data": [
          {
            "date": d.date,
            "total_nutrition": d.total_nutrition,
            "meal_count": d.meal_count,
          }
          for d in monthly
        ],
      },
    )

  except Exception as e:
    return ApiResponse(status="error", error=str(e))


@router.get("/trends", response_model=ApiResponse)
async def get_trends(
  user_id: str = Query(..., description="ユーザーID"),
  days: int = Query(30, description="分析対象日数", ge=1, le=365),
):
  """
  食事傾向を分析

  よく食べる食材、時間帯別パターン、栄養バランスを返します。
  """
  try:
    analysis = service.analyze_trends(user_id, days)

    return ApiResponse(
      status="ok",
      data={
        "period_days": days,
        "top_ingredients": [
          {"name": name, "count": count} for name, count in analysis.top_ingredients
        ],
        "meal_time_pattern": analysis.meal_time_pattern,
        "favorite_recipes": [
          {"name": name, "count": count} for name, count in analysis.favorite_recipes
        ],
        "nutrition_balance": analysis.nutrition_balance,
      },
    )

  except Exception as e:
    return ApiResponse(status="error", error=str(e))


@router.get("/nutrition-trend", response_model=ApiResponse)
async def get_nutrition_trend(
  user_id: str = Query(..., description="ユーザーID"),
  nutrient: str = Query(..., description="栄養素名"),
  days: int = Query(30, description="取得日数", ge=1, le=365),
):
  """
  栄養素の推移を取得

  指定した栄養素の日別推移データをグラフ用に返します。
  """
  try:
    trend = service.get_nutrition_trend(user_id, nutrient, days)

    return ApiResponse(
      status="ok",
      data={
        "nutrient_name": trend.nutrient_name,
        "dates": trend.dates,
        "values": trend.values,
        "statistics": {
          "average": trend.average,
          "std_dev": trend.std_dev,
          "target": trend.target,
        },
      },
    )

  except Exception as e:
    return ApiResponse(status="error", error=str(e))


@router.get("/summary", response_model=ApiResponse)
async def get_nutrition_summary(
  user_id: str = Query(..., description="ユーザーID"),
  start_date: str = Query(..., description="開始日（YYYY-MM-DD）"),
  end_date: str = Query(..., description="終了日（YYYY-MM-DD）"),
):
  """
  期間内の栄養摂取量サマリーを取得

  指定期間の合計・平均栄養摂取量を返します。
  """
  try:
    # 日付形式の検証
    try:
      datetime.strptime(start_date, "%Y-%m-%d")
      datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
      raise HTTPException(status_code=400, detail="Dates must be in YYYY-MM-DD format")

    if start_date > end_date:
      raise HTTPException(status_code=400, detail="start_date must be before end_date")

    summary = service.get_nutrition_summary(user_id, start_date, end_date)

    return ApiResponse(status="ok", data=summary)

  except HTTPException:
    raise
  except Exception as e:
    return ApiResponse(status="error", error=str(e))

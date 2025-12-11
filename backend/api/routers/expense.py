"""
費用管理APIルーター

支出記録・予算管理・分析のエンドポイントを提供。
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

from backend.services.expense_service import (
  ExpenseService,
  ExpenseCategory,
  ExpenseRecord,
  Budget,
  ExpenseSummary
)


router = APIRouter(prefix="/api/v1/expense", tags=["expense"])
expense_service = ExpenseService()


# リクエスト/レスポンスモデル
class ExpenseRecordRequest(BaseModel):
  """支出記録リクエスト"""
  date: str = Field(..., description="日付（ISO8601形式）")
  amount: float = Field(..., gt=0, description="金額")
  category: str = Field(..., description="カテゴリ")
  description: str = Field(..., min_length=1, description="説明")
  recipe_id: Optional[str] = Field(None, description="関連レシピID")


class ExpenseRecordResponse(BaseModel):
  """支出記録レスポンス"""
  id: str
  date: str
  amount: float
  category: str
  description: str
  recipe_id: Optional[str]
  created_at: Optional[str]


class BudgetRequest(BaseModel):
  """予算設定リクエスト"""
  month: str = Field(..., description="対象月（YYYY-MM形式）")
  total_budget: float = Field(..., gt=0, description="総予算")
  category_budgets: Optional[Dict[str, float]] = Field(None, description="カテゴリ別予算")


class BudgetResponse(BaseModel):
  """予算設定レスポンス"""
  month: str
  total_budget: float
  category_budgets: Dict[str, float]
  created_at: str


class ExpenseSummaryResponse(BaseModel):
  """支出サマリーレスポンス"""
  period: str
  total_spent: float
  budget_remaining: Optional[float]
  category_breakdown: Dict[str, float]
  daily_average: float
  trend: str


class ApiResponse(BaseModel):
  """標準APIレスポンス"""
  status: str
  data: Optional[Dict] = None
  error: Optional[str] = None


@router.post("/record", response_model=ApiResponse)
async def record_expense(request: ExpenseRecordRequest):
  """
  支出を記録

  Args:
      request: 支出記録リクエスト

  Returns:
      作成された支出記録
  """
  try:
    # カテゴリの検証
    try:
      category = ExpenseCategory(request.category)
    except ValueError:
      raise HTTPException(
        status_code=400,
        detail=f"Invalid category. Must be one of: {[c.value for c in ExpenseCategory]}"
      )

    # 日付の検証
    try:
      datetime.fromisoformat(request.date.split('T')[0])
    except ValueError:
      raise HTTPException(status_code=400, detail="Invalid date format. Use ISO8601 format.")

    # 支出を記録
    expense = expense_service.add_expense(
      date=request.date,
      amount=request.amount,
      category=category,
      description=request.description,
      recipe_id=request.recipe_id
    )

    return ApiResponse(
      status="ok",
      data={
        "expense": {
          "id": expense.id,
          "date": expense.date,
          "amount": expense.amount,
          "category": expense.category.value,
          "description": expense.description,
          "recipe_id": expense.recipe_id,
          "created_at": expense.created_at
        }
      }
    )

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to record expense: {str(e)}")


@router.get("/summary", response_model=ApiResponse)
async def get_summary(
  period: str = Query("month", regex="^(day|week|month)$"),
  date: Optional[str] = Query(None, description="基準日（ISO8601形式）")
):
  """
  支出サマリーを取得

  Args:
      period: 集計期間（day/week/month）
      date: 基準日（デフォルトは今日）

  Returns:
      支出サマリー
  """
  try:
    # 日付の検証
    if date:
      try:
        datetime.fromisoformat(date.split('T')[0])
      except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO8601 format.")

    summary = expense_service.get_summary(period=period, date=date)

    return ApiResponse(
      status="ok",
      data={
        "summary": {
          "period": summary.period,
          "total_spent": summary.total_spent,
          "budget_remaining": summary.budget_remaining,
          "category_breakdown": summary.category_breakdown,
          "daily_average": summary.daily_average,
          "trend": summary.trend
        }
      }
    )

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.post("/budget", response_model=ApiResponse)
async def set_budget(request: BudgetRequest):
  """
  予算を設定

  Args:
      request: 予算設定リクエスト

  Returns:
      設定された予算
  """
  try:
    # 月フォーマットの検証
    try:
      datetime.strptime(request.month, '%Y-%m')
    except ValueError:
      raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM format.")

    # カテゴリ予算の検証
    if request.category_budgets:
      valid_categories = [c.value for c in ExpenseCategory]
      for category in request.category_budgets.keys():
        if category not in valid_categories:
          raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{category}'. Must be one of: {valid_categories}"
          )

    budget = expense_service.set_budget(
      month=request.month,
      total_budget=request.total_budget,
      category_budgets=request.category_budgets
    )

    return ApiResponse(
      status="ok",
      data={
        "budget": {
          "month": budget.month,
          "total_budget": budget.total_budget,
          "category_budgets": budget.category_budgets,
          "created_at": budget.created_at
        }
      }
    )

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to set budget: {str(e)}")


@router.get("/budget", response_model=ApiResponse)
async def get_budget(month: str = Query(..., description="対象月（YYYY-MM形式）")):
  """
  予算を取得

  Args:
      month: 対象月

  Returns:
      予算設定
  """
  try:
    # 月フォーマットの検証
    try:
      datetime.strptime(month, '%Y-%m')
    except ValueError:
      raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM format.")

    budget = expense_service.get_budget(month)

    if budget is None:
      return ApiResponse(
        status="ok",
        data={"budget": None}
      )

    return ApiResponse(
      status="ok",
      data={
        "budget": {
          "month": budget.month,
          "total_budget": budget.total_budget,
          "category_budgets": budget.category_budgets,
          "created_at": budget.created_at
        }
      }
    )

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get budget: {str(e)}")


@router.get("/category-breakdown", response_model=ApiResponse)
async def get_category_breakdown(month: str = Query(..., description="対象月（YYYY-MM形式）")):
  """
  カテゴリ別内訳を取得

  Args:
      month: 対象月

  Returns:
      カテゴリ別支出額
  """
  try:
    # 月フォーマットの検証
    try:
      datetime.strptime(month, '%Y-%m')
    except ValueError:
      raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM format.")

    breakdown = expense_service.get_category_breakdown(month)

    return ApiResponse(
      status="ok",
      data={"breakdown": breakdown}
    )

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get category breakdown: {str(e)}")


@router.get("/trends", response_model=ApiResponse)
async def get_trends(months: int = Query(6, ge=1, le=24, description="過去何ヶ月分を取得するか")):
  """
  支出傾向を取得

  Args:
      months: 取得する月数（1-24）

  Returns:
      月次推移データ
  """
  try:
    trends = expense_service.get_trends(months=months)

    return ApiResponse(
      status="ok",
      data={"trends": trends}
    )

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


@router.get("/expenses", response_model=ApiResponse)
async def get_expenses(
  start_date: Optional[str] = Query(None, description="開始日（ISO8601形式）"),
  end_date: Optional[str] = Query(None, description="終了日（ISO8601形式）"),
  category: Optional[str] = Query(None, description="カテゴリフィルタ")
):
  """
  支出記録を取得

  Args:
      start_date: 開始日
      end_date: 終了日
      category: カテゴリ

  Returns:
      支出記録のリスト
  """
  try:
    # 日付の検証
    if start_date:
      try:
        datetime.fromisoformat(start_date.split('T')[0])
      except ValueError:
        raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO8601 format.")

    if end_date:
      try:
        datetime.fromisoformat(end_date.split('T')[0])
      except ValueError:
        raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO8601 format.")

    # カテゴリの検証
    category_enum = None
    if category:
      try:
        category_enum = ExpenseCategory(category)
      except ValueError:
        raise HTTPException(
          status_code=400,
          detail=f"Invalid category. Must be one of: {[c.value for c in ExpenseCategory]}"
        )

    expenses = expense_service.get_expenses(
      start_date=start_date,
      end_date=end_date,
      category=category_enum
    )

    return ApiResponse(
      status="ok",
      data={
        "expenses": [
          {
            "id": exp.id,
            "date": exp.date,
            "amount": exp.amount,
            "category": exp.category.value,
            "description": exp.description,
            "recipe_id": exp.recipe_id,
            "created_at": exp.created_at
          }
          for exp in expenses
        ]
      }
    )

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get expenses: {str(e)}")

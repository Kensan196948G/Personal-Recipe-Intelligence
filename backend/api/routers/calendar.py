"""
カレンダーAPIルーター - 献立計画のCRUD操作とエクスポート機能
"""

from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

from backend.services.calendar_service import CalendarService, MealPlanModel
from backend.services.meal_plan_service import MealPlanService, ShoppingListItem


router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])

calendar_service = CalendarService()
meal_plan_service = MealPlanService()


# リクエスト / レスポンスモデル
class CreateMealPlanRequest(BaseModel):
    """献立計画作成リクエスト"""

    date: str = Field(..., description="日付 (YYYY-MM-DD)")
    meal_type: str = Field(..., description="朝食/昼食/夕食/間食")
    recipe_id: Optional[int] = None
    recipe_name: str
    servings: int = Field(default=1, ge=1)
    notes: Optional[str] = None


class UpdateMealPlanRequest(BaseModel):
    """献立計画更新リクエスト"""

    date: Optional[str] = None
    meal_type: Optional[str] = None
    recipe_id: Optional[int] = None
    recipe_name: Optional[str] = None
    servings: Optional[int] = Field(default=None, ge=1)
    notes: Optional[str] = None


class MealPlanResponse(BaseModel):
    """献立計画レスポンス"""

    status: str = "ok"
    data: Optional[MealPlanModel] = None
    error: Optional[str] = None


class MealPlansListResponse(BaseModel):
    """献立計画リストレスポンス"""

    status: str = "ok"
    data: List[MealPlanModel] = Field(default_factory=list)
    error: Optional[str] = None


class ShoppingListResponse(BaseModel):
    """買い物リストレスポンス"""

    status: str = "ok"
    data: List[ShoppingListItem] = Field(default_factory=list)
    error: Optional[str] = None


class WeeklySummaryResponse(BaseModel):
    """週間サマリーレスポンス"""

    status: str = "ok"
    data: Optional[dict] = None
    error: Optional[str] = None


@router.get("/plans", response_model=MealPlansListResponse)
async def get_meal_plans(
    start_date: Optional[str] = Query(None, description="開始日 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="終了日 (YYYY-MM-DD)"),
    meal_type: Optional[str] = Query(None, description="食事タイプでフィルタ"),
):
    """
    献立計画一覧を取得

    - start_date, end_date で期間フィルタリング可能
    - meal_type で食事タイプフィルタリング可能
    """
    try:
        # 日付パース
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None

        plans = calendar_service.get_plans(
            start_date=start, end_date=end, meal_type=meal_type
        )

        return MealPlansListResponse(status="ok", data=plans)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        return MealPlansListResponse(status="error", data=[], error=str(e))


@router.post("/plans", response_model=MealPlanResponse)
async def create_meal_plan(request: CreateMealPlanRequest):
    """
    献立計画を作成

    - date: 日付 (YYYY-MM-DD)
    - meal_type: 朝食/昼食/夕食/間食
    - recipe_id: レシピID（オプション）
    - recipe_name: レシピ名
    - servings: 人数（デフォルト1）
    - notes: メモ（オプション）
    """
    try:
        # 日付パース
        plan_date = date.fromisoformat(request.date)

        # 献立計画モデル作成
        meal_plan = MealPlanModel(
            date=plan_date,
            meal_type=request.meal_type,
            recipe_id=request.recipe_id,
            recipe_name=request.recipe_name,
            servings=request.servings,
            notes=request.notes,
        )

        # 保存
        created_plan = calendar_service.create_plan(meal_plan)

        return MealPlanResponse(status="ok", data=created_plan)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        return MealPlanResponse(status="error", data=None, error=str(e))


@router.put("/plans/{plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(plan_id: int, request: UpdateMealPlanRequest):
    """
    献立計画を更新

    - plan_id: 更新する献立計画のID
    - リクエストボディ: 更新する項目（部分更新可能）
    """
    try:
        # None でない項目のみ更新
        updates = {}

        if request.date is not None:
            updates["date"] = date.fromisoformat(request.date)
        if request.meal_type is not None:
            updates["meal_type"] = request.meal_type
        if request.recipe_id is not None:
            updates["recipe_id"] = request.recipe_id
        if request.recipe_name is not None:
            updates["recipe_name"] = request.recipe_name
        if request.servings is not None:
            updates["servings"] = request.servings
        if request.notes is not None:
            updates["notes"] = request.notes

        updated_plan = calendar_service.update_plan(plan_id, updates)

        if not updated_plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

        return MealPlanResponse(status="ok", data=updated_plan)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        return MealPlanResponse(status="error", data=None, error=str(e))


@router.delete("/plans/{plan_id}")
async def delete_meal_plan(plan_id: int):
    """
    献立計画を削除

    - plan_id: 削除する献立計画のID
    """
    try:
        success = calendar_service.delete_plan(plan_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

        return {"status": "ok", "message": f"Plan {plan_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/export/ical")
async def export_ical(
    start_date: Optional[str] = Query(None, description="開始日 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="終了日 (YYYY-MM-DD)"),
):
    """
    iCal 形式で献立カレンダーをエクスポート

    - start_date, end_date で期間を指定可能
    - レスポンスは .ics ファイルとしてダウンロード可能
    """
    try:
        # 日付パース
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None

        ical_content = calendar_service.export_to_ical(start_date=start, end_date=end)

        # iCalendar ファイルとして返す
        return Response(
            content=ical_content,
            media_type="text/calendar",
            headers={"Content-Disposition": "attachment; filename=meal_calendar.ics"},
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shopping-list", response_model=ShoppingListResponse)
async def get_shopping_list(
    start_date: str = Query(..., description="開始日 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="終了日 (YYYY-MM-DD)"),
):
    """
    指定期間の買い物リストを自動生成

    - start_date: 開始日
    - end_date: 終了日
    - 献立計画から必要な材料を集約して返す
    """
    try:
        # 日付パース
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        # 献立計画を取得
        plans = calendar_service.get_plans(start_date=start, end_date=end)
        plans_dict = [plan.dict() for plan in plans]

        # 買い物リスト生成
        shopping_list = meal_plan_service.generate_shopping_list(plans_dict, start, end)

        return ShoppingListResponse(status="ok", data=shopping_list)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        return ShoppingListResponse(status="error", data=[], error=str(e))


@router.get("/nutrition", response_model=dict)
async def get_nutrition_balance(
    start_date: str = Query(..., description="開始日 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="終了日 (YYYY-MM-DD)"),
):
    """
    指定期間の栄養バランスを計算

    - start_date: 開始日
    - end_date: 終了日
    - カロリー、タンパク質、脂質、炭水化物の合計を返す
    """
    try:
        # 日付パース
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        # 献立計画を取得
        plans = calendar_service.get_plans(start_date=start, end_date=end)
        plans_dict = [plan.dict() for plan in plans]

        # 栄養バランス計算
        nutrition = meal_plan_service.calculate_nutrition_balance(
            plans_dict, start, end
        )

        return {"status": "ok", "data": nutrition.dict(), "error": None}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        return {"status": "error", "data": None, "error": str(e)}


@router.get("/weekly-summary", response_model=WeeklySummaryResponse)
async def get_weekly_summary(
    target_date: Optional[str] = Query(
        None, description="対象週を含む日付 (YYYY-MM-DD)"
    ),
):
    """
    週間サマリーを取得（栄養バランス + 買い物リスト）

    - target_date: 対象週を含む日付（省略時は今日）
    - その週の月曜日〜日曜日の献立計画をサマリー化
    """
    try:
        # 日付パース
        target = date.fromisoformat(target_date) if target_date else date.today()

        # 献立計画を取得
        plans = calendar_service.get_plans()
        plans_dict = [plan.dict() for plan in plans]

        # 週間サマリー生成
        summary = meal_plan_service.get_weekly_summary(plans_dict, target)

        return WeeklySummaryResponse(status="ok", data=summary)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        return WeeklySummaryResponse(status="error", data=None, error=str(e))


@router.get("/week/{target_date}")
async def get_week_plans(target_date: str):
    """
    指定日を含む週の献立計画を取得（日付ごとにグループ化）

    - target_date: 対象週を含む日付 (YYYY-MM-DD)
    """
    try:
        target = date.fromisoformat(target_date)
        grouped_plans = calendar_service.get_week_plans(target)

        return {
            "status": "ok",
            "data": {
                date_key: [plan.dict() for plan in plans]
                for date_key, plans in grouped_plans.items()
            },
            "error": None,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        return {"status": "error", "data": None, "error": str(e)}


@router.get("/month/{year}/{month}")
async def get_month_plans(year: int, month: int):
    """
    指定月の献立計画を取得（日付ごとにグループ化）

    - year: 年
    - month: 月 (1-12)
    """
    try:
        if not (1 <= month <= 12):
            raise HTTPException(
                status_code=400, detail="Month must be between 1 and 12"
            )

        grouped_plans = calendar_service.get_month_plans(year, month)

        return {
            "status": "ok",
            "data": {
                date_key: [plan.dict() for plan in plans]
                for date_key, plans in grouped_plans.items()
            },
            "error": None,
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "data": None, "error": str(e)}

"""
カレンダーサービス - 献立計画のカレンダー連携機能を提供
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from icalendar import Calendar, Event
from pydantic import BaseModel, Field
import json
from pathlib import Path


class MealPlanModel(BaseModel):
    """献立計画データモデル"""

    id: Optional[int] = None
    date: date
    meal_type: str = Field(..., description="朝食/昼食/夕食/間食")
    recipe_id: Optional[int] = None
    recipe_name: str
    servings: int = Field(default=1, ge=1)
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ShoppingItem(BaseModel):
    """買い物リストアイテム"""

    ingredient: str
    quantity: str
    unit: str
    recipes: List[str] = Field(default_factory=list)


class CalendarService:
    """カレンダーサービス - iCal エクスポートと Google Calendar 連携準備"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.plans_file = self.data_dir / "meal_plans.json"
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """データディレクトリの存在を保証"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.plans_file.exists():
            self.plans_file.write_text("[]", encoding="utf-8")

    def _load_plans(self) -> List[Dict[str, Any]]:
        """献立計画をファイルから読み込み"""
        try:
            data = json.loads(self.plans_file.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error loading plans: {e}")
            return []

    def _save_plans(self, plans: List[Dict[str, Any]]) -> None:
        """献立計画をファイルに保存"""
        self.plans_file.write_text(
            json.dumps(plans, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    def _generate_id(self, plans: List[Dict[str, Any]]) -> int:
        """新しいIDを生成"""
        if not plans:
            return 1
        return max(plan.get("id", 0) for plan in plans) + 1

    def create_plan(self, plan: MealPlanModel) -> MealPlanModel:
        """献立計画を作成"""
        plans = self._load_plans()

        plan_dict = plan.dict()
        plan_dict["id"] = self._generate_id(plans)
        plan_dict["created_at"] = datetime.now().isoformat()
        plan_dict["updated_at"] = datetime.now().isoformat()
        plan_dict["date"] = plan.date.isoformat()

        plans.append(plan_dict)
        self._save_plans(plans)

        return MealPlanModel(**plan_dict)

    def get_plans(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        meal_type: Optional[str] = None,
    ) -> List[MealPlanModel]:
        """献立計画を取得（フィルタリング可能）"""
        plans = self._load_plans()

        # フィルタリング
        filtered_plans = []
        for plan in plans:
            plan_date = date.fromisoformat(plan["date"])

            # 日付範囲フィルタ
            if start_date and plan_date < start_date:
                continue
            if end_date and plan_date > end_date:
                continue

            # 食事タイプフィルタ
            if meal_type and plan.get("meal_type") != meal_type:
                continue

            filtered_plans.append(plan)

        return [MealPlanModel(**plan) for plan in filtered_plans]

    def update_plan(
        self, plan_id: int, updates: Dict[str, Any]
    ) -> Optional[MealPlanModel]:
        """献立計画を更新"""
        plans = self._load_plans()

        for plan in plans:
            if plan.get("id") == plan_id:
                # 日付の変換処理
                if "date" in updates and isinstance(updates["date"], date):
                    updates["date"] = updates["date"].isoformat()

                plan.update(updates)
                plan["updated_at"] = datetime.now().isoformat()
                self._save_plans(plans)
                return MealPlanModel(**plan)

        return None

    def delete_plan(self, plan_id: int) -> bool:
        """献立計画を削除"""
        plans = self._load_plans()
        original_length = len(plans)
        plans = [p for p in plans if p.get("id") != plan_id]

        if len(plans) < original_length:
            self._save_plans(plans)
            return True
        return False

    def export_to_ical(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        """iCal 形式でエクスポート"""
        cal = Calendar()
        cal.add("prodid", "-//Personal Recipe Intelligence//Meal Planner//JP")
        cal.add("version", "2.0")
        cal.add("x-wr-calname", "献立カレンダー")
        cal.add("x-wr-timezone", "Asia/Tokyo")

        plans = self.get_plans(start_date=start_date, end_date=end_date)

        for plan in plans:
            event = Event()
            event.add("summary", f"{plan.meal_type}: {plan.recipe_name}")

            # 全日イベントとして設定
            event.add("dtstart", plan.date)
            event.add("dtend", plan.date + timedelta(days=1))

            # 説明
            description_parts = [
                f"レシピ: {plan.recipe_name}",
                f"食事タイプ: {plan.meal_type}",
                f"人数: {plan.servings}人分",
            ]
            if plan.notes:
                description_parts.append(f"メモ: {plan.notes}")

            event.add("description", "\n".join(description_parts))
            event.add("uid", f"meal-plan-{plan.id}@personal-recipe-intelligence")
            event.add("dtstamp", datetime.now())

            cal.add_component(event)

        return cal.to_ical().decode("utf-8")

    def prepare_google_calendar_event(self, plan: MealPlanModel) -> Dict[str, Any]:
        """Google Calendar API 用のイベントデータを準備"""
        event = {
            "summary": f"{plan.meal_type}: {plan.recipe_name}",
            "description": f"レシピ: {plan.recipe_name}\n人数: {plan.servings}人分",
            "start": {"date": plan.date.isoformat(), "timeZone": "Asia/Tokyo"},
            "end": {
                "date": (plan.date + timedelta(days=1)).isoformat(),
                "timeZone": "Asia/Tokyo",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 60}],
            },
        }

        if plan.notes:
            event["description"] += f"\n\nメモ: {plan.notes}"

        return event

    def get_week_plans(self, target_date: date) -> Dict[str, List[MealPlanModel]]:
        """指定日を含む週の献立計画を取得（日付ごとにグループ化）"""
        # 週の開始日（月曜日）を計算
        start_of_week = target_date - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        plans = self.get_plans(start_date=start_of_week, end_date=end_of_week)

        # 日付ごとにグループ化
        grouped: Dict[str, List[MealPlanModel]] = {}
        for plan in plans:
            date_key = plan.date.isoformat()
            if date_key not in grouped:
                grouped[date_key] = []
            grouped[date_key].append(plan)

        # 日付順にソート（各日の中では meal_type でソート）
        for date_key in grouped:
            meal_type_order = {"朝食": 0, "昼食": 1, "夕食": 2, "間食": 3}
            grouped[date_key].sort(key=lambda p: meal_type_order.get(p.meal_type, 99))

        return grouped

    def get_month_plans(self, year: int, month: int) -> Dict[str, List[MealPlanModel]]:
        """指定月の献立計画を取得（日付ごとにグループ化）"""
        start_date = date(year, month, 1)

        # 月末日を計算
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        plans = self.get_plans(start_date=start_date, end_date=end_date)

        # 日付ごとにグループ化
        grouped: Dict[str, List[MealPlanModel]] = {}
        for plan in plans:
            date_key = plan.date.isoformat()
            if date_key not in grouped:
                grouped[date_key] = []
            grouped[date_key].append(plan)

        # 日付順にソート
        for date_key in grouped:
            meal_type_order = {"朝食": 0, "昼食": 1, "夕食": 2, "間食": 3}
            grouped[date_key].sort(key=lambda p: meal_type_order.get(p.meal_type, 99))

        return grouped

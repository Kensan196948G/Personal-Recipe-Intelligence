"""
食事履歴分析サービス

食事記録の保存・取得、栄養摂取量の集計、傾向分析を提供します。
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter


@dataclass
class MealRecord:
    """食事記録"""

    id: str
    user_id: str
    recipe_id: str
    recipe_name: str
    meal_type: str  # breakfast, lunch, dinner, snack
    consumed_at: str  # ISO8601 format
    servings: float
    nutrition: Dict[str, float]  # 栄養素別の摂取量
    ingredients: List[str]  # 使用した食材リスト
    created_at: str


@dataclass
class DailyNutrition:
    """日別栄養摂取量"""

    date: str
    total_nutrition: Dict[str, float]
    meals: List[Dict]
    meal_count: int


@dataclass
class NutritionTrend:
    """栄養素推移データ"""

    nutrient_name: str
    dates: List[str]
    values: List[float]
    average: float
    std_dev: float
    target: Optional[float]


@dataclass
class TrendAnalysis:
    """傾向分析結果"""

    top_ingredients: List[Tuple[str, int]]  # (食材名, 回数)
    meal_time_pattern: Dict[str, int]  # 時間帯別の食事回数
    favorite_recipes: List[Tuple[str, int]]  # (レシピ名, 回数)
    nutrition_balance: Dict[str, str]  # 栄養素別の評価（過剰/適正/不足）


class MealHistoryService:
    """食事履歴管理サービス"""

    def __init__(self, data_dir: str = "data"):
        """
        初期化

        Args:
            data_dir: データ保存ディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.meal_history_file = self.data_dir / "meal_history.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 推奨栄養摂取量（成人1日あたりの目安）
        self.daily_targets = {
            "calories": 2000.0,
            "protein": 60.0,
            "fat": 55.0,
            "carbohydrates": 300.0,
            "fiber": 20.0,
            "sodium": 2300.0,
            "calcium": 700.0,
            "iron": 8.0,
            "vitamin_c": 100.0,
        }

    def _load_records(self) -> List[Dict]:
        """食事記録を読み込む"""
        if not self.meal_history_file.exists():
            return []

        try:
            with open(self.meal_history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save_records(self, records: List[Dict]) -> None:
        """食事記録を保存する"""
        with open(self.meal_history_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def record_meal(
        self,
        user_id: str,
        recipe_id: str,
        recipe_name: str,
        meal_type: str,
        servings: float,
        nutrition: Dict[str, float],
        ingredients: List[str],
        consumed_at: Optional[str] = None,
    ) -> MealRecord:
        """
        食事記録を保存

        Args:
            user_id: ユーザーID
            recipe_id: レシピID
            recipe_name: レシピ名
            meal_type: 食事タイプ（breakfast/lunch/dinner/snack）
            servings: 人前数
            nutrition: 栄養素情報
            ingredients: 食材リスト
            consumed_at: 食事日時（省略時は現在時刻）

        Returns:
            保存した食事記録
        """
        now = datetime.now().isoformat()
        meal_time = consumed_at or now

        record = MealRecord(
            id=f"{user_id}_{datetime.now().timestamp()}",
            user_id=user_id,
            recipe_id=recipe_id,
            recipe_name=recipe_name,
            meal_type=meal_type,
            consumed_at=meal_time,
            servings=servings,
            nutrition=nutrition,
            ingredients=ingredients,
            created_at=now,
        )

        records = self._load_records()
        records.append(asdict(record))
        self._save_records(records)

        return record

    def get_daily_nutrition(self, user_id: str, date: str) -> DailyNutrition:
        """
        日別栄養摂取量を取得

        Args:
            user_id: ユーザーID
            date: 日付（YYYY-MM-DD形式）

        Returns:
            日別栄養摂取量
        """
        records = self._load_records()

        # 指定日の記録をフィルタ
        daily_records = [
            r
            for r in records
            if r["user_id"] == user_id and r["consumed_at"].startswith(date)
        ]

        # 栄養素を集計
        total_nutrition = defaultdict(float)
        for record in daily_records:
            for nutrient, value in record["nutrition"].items():
                total_nutrition[nutrient] += value

        meals = [
            {
                "id": r["id"],
                "recipe_name": r["recipe_name"],
                "meal_type": r["meal_type"],
                "consumed_at": r["consumed_at"],
                "nutrition": r["nutrition"],
            }
            for r in daily_records
        ]

        return DailyNutrition(
            date=date,
            total_nutrition=dict(total_nutrition),
            meals=meals,
            meal_count=len(daily_records),
        )

    def get_weekly_nutrition(
        self, user_id: str, start_date: Optional[str] = None
    ) -> List[DailyNutrition]:
        """
        週間栄養摂取量を取得

        Args:
            user_id: ユーザーID
            start_date: 開始日（省略時は今週月曜日）

        Returns:
            7日分の日別栄養摂取量リスト
        """
        if start_date:
            start = datetime.fromisoformat(start_date)
        else:
            today = datetime.now()
            start = today - timedelta(days=today.weekday())

        weekly_data = []
        for i in range(7):
            date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
            daily = self.get_daily_nutrition(user_id, date)
            weekly_data.append(daily)

        return weekly_data

    def get_monthly_nutrition(
        self, user_id: str, year: int, month: int
    ) -> List[DailyNutrition]:
        """
        月間栄養摂取量を取得

        Args:
            user_id: ユーザーID
            year: 年
            month: 月

        Returns:
            月内の日別栄養摂取量リスト
        """
        # 月の日数を計算
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        last_day = (next_month - timedelta(days=1)).day

        monthly_data = []
        for day in range(1, last_day + 1):
            date = f"{year:04d}-{month:02d}-{day:02d}"
            daily = self.get_daily_nutrition(user_id, date)
            monthly_data.append(daily)

        return monthly_data

    def get_nutrition_trend(
        self, user_id: str, nutrient_name: str, days: int = 30
    ) -> NutritionTrend:
        """
        栄養素の推移を取得

        Args:
            user_id: ユーザーID
            nutrient_name: 栄養素名
            days: 取得日数

        Returns:
            栄養素推移データ
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)

        dates = []
        values = []

        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            daily = self.get_daily_nutrition(user_id, date)

            dates.append(date)
            values.append(daily.total_nutrition.get(nutrient_name, 0.0))

        # 統計計算
        non_zero_values = [v for v in values if v > 0]
        avg = statistics.mean(non_zero_values) if non_zero_values else 0.0
        std = statistics.stdev(non_zero_values) if len(non_zero_values) > 1 else 0.0

        return NutritionTrend(
            nutrient_name=nutrient_name,
            dates=dates,
            values=values,
            average=avg,
            std_dev=std,
            target=self.daily_targets.get(nutrient_name),
        )

    def analyze_trends(self, user_id: str, days: int = 30) -> TrendAnalysis:
        """
        食事傾向を分析

        Args:
            user_id: ユーザーID
            days: 分析対象日数

        Returns:
            傾向分析結果
        """
        records = self._load_records()

        # 期間でフィルタ
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        recent_records = [
            r
            for r in records
            if r["user_id"] == user_id and r["consumed_at"] >= cutoff_date
        ]

        # 食材の集計
        ingredient_counter = Counter()
        for record in recent_records:
            ingredient_counter.update(record["ingredients"])

        # レシピの集計
        recipe_counter = Counter()
        for record in recent_records:
            recipe_counter[record["recipe_name"]] += 1

        # 食事タイプの集計
        meal_type_counter = Counter()
        for record in recent_records:
            meal_type_counter[record["meal_type"]] += 1

        # 栄養バランスの評価
        nutrition_balance = self._evaluate_nutrition_balance(user_id, days)

        return TrendAnalysis(
            top_ingredients=ingredient_counter.most_common(10),
            meal_time_pattern=dict(meal_type_counter),
            favorite_recipes=recipe_counter.most_common(10),
            nutrition_balance=nutrition_balance,
        )

    def _evaluate_nutrition_balance(self, user_id: str, days: int) -> Dict[str, str]:
        """
        栄養バランスを評価

        Args:
            user_id: ユーザーID
            days: 評価期間

        Returns:
            栄養素別の評価（excessive/adequate/insufficient）
        """
        balance = {}

        for nutrient, target in self.daily_targets.items():
            trend = self.get_nutrition_trend(user_id, nutrient, days)

            if trend.average >= target * 1.2:
                balance[nutrient] = "excessive"
            elif trend.average >= target * 0.8:
                balance[nutrient] = "adequate"
            else:
                balance[nutrient] = "insufficient"

        return balance

    def get_nutrition_summary(
        self, user_id: str, start_date: str, end_date: str
    ) -> Dict[str, any]:
        """
        期間内の栄養摂取量サマリーを取得

        Args:
            user_id: ユーザーID
            start_date: 開始日
            end_date: 終了日

        Returns:
            栄養摂取量サマリー
        """
        records = self._load_records()

        # 期間でフィルタ
        period_records = [
            r
            for r in records
            if r["user_id"] == user_id
            and start_date <= r["consumed_at"][:10] <= end_date
        ]

        # 栄養素を集計
        total_nutrition = defaultdict(float)
        for record in period_records:
            for nutrient, value in record["nutrition"].items():
                total_nutrition[nutrient] += value

        # 日数を計算
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        days = (end - start).days + 1

        # 平均を計算
        avg_nutrition = {k: v / days for k, v in total_nutrition.items()}

        return {
            "period": {"start": start_date, "end": end_date, "days": days},
            "total": dict(total_nutrition),
            "average_per_day": avg_nutrition,
            "meal_count": len(period_records),
            "targets": self.daily_targets,
        }

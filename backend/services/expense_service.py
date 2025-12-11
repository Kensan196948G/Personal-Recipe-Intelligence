"""
費用管理サービス

食費の記録・集計・分析を行う。
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class ExpenseCategory(str, Enum):
  """支出カテゴリ"""
  INGREDIENTS = "食材"
  DINING_OUT = "外食"
  SEASONINGS = "調味料"
  BEVERAGES = "飲料"
  OTHER = "その他"


@dataclass
class ExpenseRecord:
  """支出記録"""
  id: str
  date: str  # ISO8601形式
  amount: float
  category: ExpenseCategory
  description: str
  recipe_id: Optional[str] = None
  created_at: Optional[str] = None

  def to_dict(self) -> Dict:
    """辞書形式に変換"""
    return {
      "id": self.id,
      "date": self.date,
      "amount": self.amount,
      "category": self.category.value if isinstance(self.category, ExpenseCategory) else self.category,
      "description": self.description,
      "recipe_id": self.recipe_id,
      "created_at": self.created_at
    }


@dataclass
class Budget:
  """予算設定"""
  month: str  # YYYY-MM形式
  total_budget: float
  category_budgets: Dict[str, float]
  created_at: str

  def to_dict(self) -> Dict:
    """辞書形式に変換"""
    return asdict(self)


@dataclass
class ExpenseSummary:
  """支出サマリー"""
  period: str
  total_spent: float
  budget_remaining: Optional[float]
  category_breakdown: Dict[str, float]
  daily_average: float
  trend: str  # "increasing", "decreasing", "stable"

  def to_dict(self) -> Dict:
    """辞書形式に変換"""
    return asdict(self)


class ExpenseService:
  """費用管理サービス"""

  def __init__(self, data_dir: str = "data/expenses"):
    """
    初期化

    Args:
        data_dir: データ保存ディレクトリ
    """
    self.data_dir = Path(data_dir)
    self.data_dir.mkdir(parents=True, exist_ok=True)
    self.expenses_file = self.data_dir / "expenses.json"
    self.budgets_file = self.data_dir / "budgets.json"
    self._ensure_data_files()

  def _ensure_data_files(self) -> None:
    """データファイルの存在を確認"""
    if not self.expenses_file.exists():
      self._save_expenses([])
    if not self.budgets_file.exists():
      self._save_budgets([])

  def _load_expenses(self) -> List[ExpenseRecord]:
    """支出記録を読み込み"""
    try:
      with open(self.expenses_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [
          ExpenseRecord(
            id=item['id'],
            date=item['date'],
            amount=item['amount'],
            category=ExpenseCategory(item['category']),
            description=item['description'],
            recipe_id=item.get('recipe_id'),
            created_at=item.get('created_at')
          )
          for item in data
        ]
    except Exception as e:
      print(f"Error loading expenses: {e}")
      return []

  def _save_expenses(self, expenses: List[ExpenseRecord]) -> None:
    """支出記録を保存"""
    try:
      with open(self.expenses_file, 'w', encoding='utf-8') as f:
        json.dump([exp.to_dict() for exp in expenses], f, ensure_ascii=False, indent=2)
    except Exception as e:
      print(f"Error saving expenses: {e}")
      raise

  def _load_budgets(self) -> List[Budget]:
    """予算設定を読み込み"""
    try:
      with open(self.budgets_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [Budget(**item) for item in data]
    except Exception as e:
      print(f"Error loading budgets: {e}")
      return []

  def _save_budgets(self, budgets: List[Budget]) -> None:
    """予算設定を保存"""
    try:
      with open(self.budgets_file, 'w', encoding='utf-8') as f:
        json.dump([budget.to_dict() for budget in budgets], f, ensure_ascii=False, indent=2)
    except Exception as e:
      print(f"Error saving budgets: {e}")
      raise

  def add_expense(
    self,
    date: str,
    amount: float,
    category: ExpenseCategory,
    description: str,
    recipe_id: Optional[str] = None
  ) -> ExpenseRecord:
    """
    支出を記録

    Args:
        date: 日付（ISO8601形式）
        amount: 金額
        category: カテゴリ
        description: 説明
        recipe_id: 関連レシピID

    Returns:
        作成された支出記録
    """
    expenses = self._load_expenses()
    expense_id = f"exp_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    expense = ExpenseRecord(
      id=expense_id,
      date=date,
      amount=amount,
      category=category,
      description=description,
      recipe_id=recipe_id,
      created_at=datetime.now().isoformat()
    )

    expenses.append(expense)
    self._save_expenses(expenses)

    return expense

  def get_expenses(
    self,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[ExpenseCategory] = None
  ) -> List[ExpenseRecord]:
    """
    支出記録を取得

    Args:
        start_date: 開始日（ISO8601形式）
        end_date: 終了日（ISO8601形式）
        category: フィルタするカテゴリ

    Returns:
        支出記録のリスト
    """
    expenses = self._load_expenses()

    # フィルタリング（日付部分のみで比較）
    if start_date:
      start_date_only = start_date.split('T')[0]
      expenses = [e for e in expenses if e.date.split('T')[0] >= start_date_only]
    if end_date:
      end_date_only = end_date.split('T')[0]
      expenses = [e for e in expenses if e.date.split('T')[0] <= end_date_only]
    if category:
      expenses = [e for e in expenses if e.category == category]

    return sorted(expenses, key=lambda x: x.date, reverse=True)

  def set_budget(
    self,
    month: str,
    total_budget: float,
    category_budgets: Optional[Dict[str, float]] = None
  ) -> Budget:
    """
    予算を設定

    Args:
        month: 対象月（YYYY-MM形式）
        total_budget: 総予算
        category_budgets: カテゴリ別予算

    Returns:
        設定された予算
    """
    budgets = self._load_budgets()

    # 既存の同月予算を削除
    budgets = [b for b in budgets if b.month != month]

    budget = Budget(
      month=month,
      total_budget=total_budget,
      category_budgets=category_budgets or {},
      created_at=datetime.now().isoformat()
    )

    budgets.append(budget)
    self._save_budgets(budgets)

    return budget

  def get_budget(self, month: str) -> Optional[Budget]:
    """
    予算を取得

    Args:
        month: 対象月（YYYY-MM形式）

    Returns:
        予算設定（存在しない場合はNone）
    """
    budgets = self._load_budgets()
    for budget in budgets:
      if budget.month == month:
        return budget
    return None

  def get_summary(
    self,
    period: str = "month",
    date: Optional[str] = None
  ) -> ExpenseSummary:
    """
    支出サマリーを取得

    Args:
        period: 集計期間（"day", "week", "month"）
        date: 基準日（ISO8601形式、デフォルトは今日）

    Returns:
        支出サマリー
    """
    if date is None:
      date = datetime.now().isoformat()

    base_date = datetime.fromisoformat(date.split('T')[0])

    # 期間の開始・終了日を計算
    if period == "day":
      start_date = base_date
      end_date = base_date
      period_str = base_date.strftime('%Y-%m-%d')
    elif period == "week":
      start_date = base_date - timedelta(days=base_date.weekday())
      end_date = start_date + timedelta(days=6)
      period_str = f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}"
    else:  # month
      start_date = base_date.replace(day=1)
      next_month = start_date.replace(day=28) + timedelta(days=4)
      end_date = next_month.replace(day=1) - timedelta(days=1)
      period_str = start_date.strftime('%Y-%m')

    # 支出を取得
    expenses = self.get_expenses(
      start_date=start_date.isoformat(),
      end_date=end_date.isoformat()
    )

    # 合計金額
    total_spent = sum(e.amount for e in expenses)

    # カテゴリ別内訳
    category_breakdown = {}
    for category in ExpenseCategory:
      category_expenses = [e for e in expenses if e.category == category]
      category_breakdown[category.value] = sum(e.amount for e in category_expenses)

    # 予算残額（月次のみ）
    budget_remaining = None
    if period == "month":
      budget = self.get_budget(period_str)
      if budget:
        budget_remaining = budget.total_budget - total_spent

    # 日平均
    days = (end_date - start_date).days + 1
    daily_average = total_spent / days if days > 0 else 0

    # トレンド分析
    trend = self._calculate_trend(period, base_date)

    return ExpenseSummary(
      period=period_str,
      total_spent=total_spent,
      budget_remaining=budget_remaining,
      category_breakdown=category_breakdown,
      daily_average=daily_average,
      trend=trend
    )

  def get_category_breakdown(self, month: str) -> Dict[str, float]:
    """
    カテゴリ別内訳を取得

    Args:
        month: 対象月（YYYY-MM形式）

    Returns:
        カテゴリ別支出額
    """
    year, month_num = month.split('-')
    start_date = datetime(int(year), int(month_num), 1)
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month.replace(day=1) - timedelta(days=1)

    expenses = self.get_expenses(
      start_date=start_date.isoformat(),
      end_date=end_date.isoformat()
    )

    breakdown = {}
    for category in ExpenseCategory:
      category_expenses = [e for e in expenses if e.category == category]
      breakdown[category.value] = sum(e.amount for e in category_expenses)

    return breakdown

  def get_trends(self, months: int = 6) -> Dict[str, List[Dict]]:
    """
    支出傾向を取得

    Args:
        months: 過去何ヶ月分を取得するか

    Returns:
        月次推移データ
    """
    trends = {
      "monthly_totals": [],
      "category_trends": {}
    }

    today = datetime.now()

    for i in range(months):
      # 対象月を計算
      target_date = today - timedelta(days=30 * i)
      month_str = target_date.strftime('%Y-%m')

      # 月の開始・終了日
      start_date = target_date.replace(day=1)
      next_month = start_date.replace(day=28) + timedelta(days=4)
      end_date = next_month.replace(day=1) - timedelta(days=1)

      # 支出を取得
      expenses = self.get_expenses(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
      )

      total = sum(e.amount for e in expenses)
      trends["monthly_totals"].insert(0, {
        "month": month_str,
        "total": total
      })

      # カテゴリ別
      for category in ExpenseCategory:
        category_expenses = [e for e in expenses if e.category == category]
        category_total = sum(e.amount for e in category_expenses)

        if category.value not in trends["category_trends"]:
          trends["category_trends"][category.value] = []

        trends["category_trends"][category.value].insert(0, {
          "month": month_str,
          "total": category_total
        })

    return trends

  def _calculate_trend(self, period: str, base_date: datetime) -> str:
    """
    トレンドを計算

    Args:
        period: 集計期間
        base_date: 基準日

    Returns:
        "increasing", "decreasing", "stable"
    """
    # 現在期間と前期間の支出を比較
    if period == "month":
      # 今月の期間
      current_start = base_date.replace(day=1)
      current_next = current_start.replace(day=28) + timedelta(days=4)
      current_end = current_next.replace(day=1) - timedelta(days=1)

      # 先月の期間
      prev_end = current_start - timedelta(days=1)
      prev_start = prev_end.replace(day=1)

      # 直接支出を取得して集計（get_summaryを呼ばない）
      current_expenses = self.get_expenses(
        start_date=current_start.isoformat(),
        end_date=current_end.isoformat()
      )
      prev_expenses = self.get_expenses(
        start_date=prev_start.isoformat(),
        end_date=prev_end.isoformat()
      )

      current_total = sum(e.amount for e in current_expenses)
      prev_total = sum(e.amount for e in prev_expenses)

      if prev_total == 0:
        return "stable"

      change_rate = (current_total - prev_total) / prev_total

      if change_rate > 0.1:
        return "increasing"
      elif change_rate < -0.1:
        return "decreasing"
      else:
        return "stable"

    return "stable"

"""
費用管理サービスのテスト
"""

import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from backend.services.expense_service import (
  ExpenseService,
  ExpenseCategory,
  ExpenseRecord,
  Budget,
  ExpenseSummary
)


@pytest.fixture
def temp_data_dir():
  """テスト用一時ディレクトリ"""
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)


@pytest.fixture
def expense_service(temp_data_dir):
  """テスト用ExpenseService"""
  return ExpenseService(data_dir=temp_data_dir)


class TestExpenseService:
  """ExpenseServiceのテスト"""

  def test_init_creates_data_files(self, temp_data_dir):
    """初期化時にデータファイルが作成される"""
    ExpenseService(data_dir=temp_data_dir)

    expenses_file = Path(temp_data_dir) / "expenses.json"
    budgets_file = Path(temp_data_dir) / "budgets.json"

    assert expenses_file.exists()
    assert budgets_file.exists()

  def test_add_expense(self, expense_service):
    """支出記録の追加"""
    date = datetime.now().isoformat()
    expense = expense_service.add_expense(
      date=date,
      amount=1500.0,
      category=ExpenseCategory.INGREDIENTS,
      description="野菜購入"
    )

    assert expense.id is not None
    assert expense.date == date
    assert expense.amount == 1500.0
    assert expense.category == ExpenseCategory.INGREDIENTS
    assert expense.description == "野菜購入"
    assert expense.created_at is not None

  def test_add_expense_with_recipe_id(self, expense_service):
    """レシピIDを含む支出記録の追加"""
    date = datetime.now().isoformat()
    expense = expense_service.add_expense(
      date=date,
      amount=1500.0,
      category=ExpenseCategory.INGREDIENTS,
      description="カレー用材料",
      recipe_id="recipe_123"
    )

    assert expense.recipe_id == "recipe_123"

  def test_get_expenses_all(self, expense_service):
    """全支出記録の取得"""
    # テストデータを追加
    today = datetime.now()
    expense_service.add_expense(
      date=today.isoformat(),
      amount=1500.0,
      category=ExpenseCategory.INGREDIENTS,
      description="野菜"
    )
    expense_service.add_expense(
      date=today.isoformat(),
      amount=800.0,
      category=ExpenseCategory.DINING_OUT,
      description="ランチ"
    )

    expenses = expense_service.get_expenses()
    assert len(expenses) == 2

  def test_get_expenses_with_date_filter(self, expense_service):
    """日付フィルタ付き支出記録の取得"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # テストデータを追加
    expense_service.add_expense(
      date=yesterday.isoformat(),
      amount=1000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="昨日"
    )
    expense_service.add_expense(
      date=today.isoformat(),
      amount=2000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="今日"
    )
    expense_service.add_expense(
      date=tomorrow.isoformat(),
      amount=3000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="明日"
    )

    # 今日以降のデータを取得
    expenses = expense_service.get_expenses(start_date=today.isoformat())
    assert len(expenses) == 2
    assert all(e.date >= today.isoformat() for e in expenses)

    # 今日以前のデータを取得
    expenses = expense_service.get_expenses(end_date=today.isoformat())
    assert len(expenses) == 2
    assert all(e.date <= today.isoformat() for e in expenses)

  def test_get_expenses_with_category_filter(self, expense_service):
    """カテゴリフィルタ付き支出記録の取得"""
    today = datetime.now().isoformat()

    expense_service.add_expense(
      date=today,
      amount=1000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="食材"
    )
    expense_service.add_expense(
      date=today,
      amount=2000.0,
      category=ExpenseCategory.DINING_OUT,
      description="外食"
    )

    expenses = expense_service.get_expenses(category=ExpenseCategory.INGREDIENTS)
    assert len(expenses) == 1
    assert expenses[0].category == ExpenseCategory.INGREDIENTS

  def test_set_budget(self, expense_service):
    """予算設定"""
    month = "2025-12"
    budget = expense_service.set_budget(
      month=month,
      total_budget=50000.0,
      category_budgets={
        "食材": 30000.0,
        "外食": 15000.0,
        "その他": 5000.0
      }
    )

    assert budget.month == month
    assert budget.total_budget == 50000.0
    assert budget.category_budgets["食材"] == 30000.0
    assert budget.created_at is not None

  def test_set_budget_overwrites_existing(self, expense_service):
    """同月の予算設定は上書きされる"""
    month = "2025-12"

    # 最初の予算設定
    expense_service.set_budget(month=month, total_budget=50000.0)

    # 同月の予算を再設定
    expense_service.set_budget(month=month, total_budget=60000.0)

    # 取得して確認
    retrieved_budget = expense_service.get_budget(month)
    assert retrieved_budget.total_budget == 60000.0

    # 予算は1つだけ
    budgets = expense_service._load_budgets()
    month_budgets = [b for b in budgets if b.month == month]
    assert len(month_budgets) == 1

  def test_get_budget(self, expense_service):
    """予算取得"""
    month = "2025-12"
    expense_service.set_budget(month=month, total_budget=50000.0)

    budget = expense_service.get_budget(month)
    assert budget is not None
    assert budget.month == month
    assert budget.total_budget == 50000.0

  def test_get_budget_not_found(self, expense_service):
    """存在しない月の予算取得"""
    budget = expense_service.get_budget("2025-01")
    assert budget is None

  def test_get_summary_day(self, expense_service):
    """日次サマリーの取得"""
    today = datetime.now()
    date_str = today.isoformat()

    # テストデータを追加
    expense_service.add_expense(
      date=date_str,
      amount=1000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="食材"
    )
    expense_service.add_expense(
      date=date_str,
      amount=500.0,
      category=ExpenseCategory.BEVERAGES,
      description="飲料"
    )

    summary = expense_service.get_summary(period="day", date=date_str)

    assert summary.total_spent == 1500.0
    assert summary.category_breakdown["食材"] == 1000.0
    assert summary.category_breakdown["飲料"] == 500.0
    assert summary.daily_average == 1500.0

  def test_get_summary_month(self, expense_service):
    """月次サマリーの取得"""
    today = datetime.now()
    month_start = today.replace(day=1)

    # テストデータを追加
    expense_service.add_expense(
      date=month_start.isoformat(),
      amount=1000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="食材1"
    )
    expense_service.add_expense(
      date=(month_start + timedelta(days=5)).isoformat(),
      amount=2000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="食材2"
    )

    # 予算を設定
    month_str = month_start.strftime('%Y-%m')
    expense_service.set_budget(month=month_str, total_budget=50000.0)

    summary = expense_service.get_summary(period="month", date=month_start.isoformat())

    assert summary.total_spent == 3000.0
    assert summary.budget_remaining == 47000.0
    assert summary.category_breakdown["食材"] == 3000.0

  def test_get_summary_with_budget_remaining(self, expense_service):
    """予算残額を含むサマリー"""
    today = datetime.now()
    month_str = today.strftime('%Y-%m')

    # 予算を設定
    expense_service.set_budget(month=month_str, total_budget=50000.0)

    # 支出を記録
    expense_service.add_expense(
      date=today.isoformat(),
      amount=15000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="買い物"
    )

    summary = expense_service.get_summary(period="month", date=today.isoformat())

    assert summary.budget_remaining == 35000.0

  def test_get_category_breakdown(self, expense_service):
    """カテゴリ別内訳の取得"""
    today = datetime.now()
    month_str = today.strftime('%Y-%m')

    # テストデータを追加
    expense_service.add_expense(
      date=today.isoformat(),
      amount=1000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="食材"
    )
    expense_service.add_expense(
      date=today.isoformat(),
      amount=2000.0,
      category=ExpenseCategory.DINING_OUT,
      description="外食"
    )
    expense_service.add_expense(
      date=today.isoformat(),
      amount=500.0,
      category=ExpenseCategory.BEVERAGES,
      description="飲料"
    )

    breakdown = expense_service.get_category_breakdown(month_str)

    assert breakdown["食材"] == 1000.0
    assert breakdown["外食"] == 2000.0
    assert breakdown["飲料"] == 500.0
    assert breakdown["調味料"] == 0.0
    assert breakdown["その他"] == 0.0

  def test_get_trends(self, expense_service):
    """支出傾向の取得"""
    today = datetime.now()

    # 過去3ヶ月分のテストデータを追加
    for i in range(3):
      date = today - timedelta(days=30 * i)
      expense_service.add_expense(
        date=date.isoformat(),
        amount=10000.0 * (i + 1),
        category=ExpenseCategory.INGREDIENTS,
        description=f"Month {i}"
      )

    trends = expense_service.get_trends(months=3)

    assert "monthly_totals" in trends
    assert "category_trends" in trends
    assert len(trends["monthly_totals"]) == 3
    assert "食材" in trends["category_trends"]

  def test_calculate_trend_increasing(self, expense_service):
    """増加トレンドの判定"""
    today = datetime.now()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)

    # 先月は少なめ
    expense_service.add_expense(
      date=last_month.isoformat(),
      amount=10000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="先月"
    )

    # 今月は多め（20%以上増加）
    expense_service.add_expense(
      date=this_month.isoformat(),
      amount=15000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="今月"
    )

    summary = expense_service.get_summary(period="month", date=this_month.isoformat())
    assert summary.trend == "increasing"

  def test_calculate_trend_decreasing(self, expense_service):
    """減少トレンドの判定"""
    today = datetime.now()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)

    # 先月は多め
    expense_service.add_expense(
      date=last_month.isoformat(),
      amount=20000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="先月"
    )

    # 今月は少なめ（20%以上減少）
    expense_service.add_expense(
      date=this_month.isoformat(),
      amount=15000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="今月"
    )

    summary = expense_service.get_summary(period="month", date=this_month.isoformat())
    assert summary.trend == "decreasing"

  def test_calculate_trend_stable(self, expense_service):
    """安定トレンドの判定"""
    today = datetime.now()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)

    # 先月と今月がほぼ同じ
    expense_service.add_expense(
      date=last_month.isoformat(),
      amount=10000.0,
      category=ExpenseCategory.INGREDIENTS,
      description="先月"
    )

    expense_service.add_expense(
      date=this_month.isoformat(),
      amount=10500.0,
      category=ExpenseCategory.INGREDIENTS,
      description="今月"
    )

    summary = expense_service.get_summary(period="month", date=this_month.isoformat())
    assert summary.trend == "stable"

  def test_expense_record_to_dict(self):
    """ExpenseRecordの辞書変換"""
    expense = ExpenseRecord(
      id="exp_123",
      date="2025-12-11",
      amount=1500.0,
      category=ExpenseCategory.INGREDIENTS,
      description="野菜",
      recipe_id="recipe_456",
      created_at="2025-12-11T10:00:00"
    )

    expense_dict = expense.to_dict()

    assert expense_dict["id"] == "exp_123"
    assert expense_dict["date"] == "2025-12-11"
    assert expense_dict["amount"] == 1500.0
    assert expense_dict["category"] == "食材"
    assert expense_dict["description"] == "野菜"
    assert expense_dict["recipe_id"] == "recipe_456"
    assert expense_dict["created_at"] == "2025-12-11T10:00:00"

  def test_budget_to_dict(self):
    """Budgetの辞書変換"""
    budget = Budget(
      month="2025-12",
      total_budget=50000.0,
      category_budgets={"食材": 30000.0},
      created_at="2025-12-11T10:00:00"
    )

    budget_dict = budget.to_dict()

    assert budget_dict["month"] == "2025-12"
    assert budget_dict["total_budget"] == 50000.0
    assert budget_dict["category_budgets"]["食材"] == 30000.0
    assert budget_dict["created_at"] == "2025-12-11T10:00:00"

  def test_expense_summary_to_dict(self):
    """ExpenseSummaryの辞書変換"""
    summary = ExpenseSummary(
      period="2025-12",
      total_spent=15000.0,
      budget_remaining=35000.0,
      category_breakdown={"食材": 10000.0, "外食": 5000.0},
      daily_average=500.0,
      trend="stable"
    )

    summary_dict = summary.to_dict()

    assert summary_dict["period"] == "2025-12"
    assert summary_dict["total_spent"] == 15000.0
    assert summary_dict["budget_remaining"] == 35000.0
    assert summary_dict["category_breakdown"]["食材"] == 10000.0
    assert summary_dict["daily_average"] == 500.0
    assert summary_dict["trend"] == "stable"

  def test_persistence(self, expense_service):
    """データの永続化"""
    # 支出を追加
    expense_service.add_expense(
      date=datetime.now().isoformat(),
      amount=1500.0,
      category=ExpenseCategory.INGREDIENTS,
      description="野菜"
    )

    # 予算を設定
    expense_service.set_budget(
      month="2025-12",
      total_budget=50000.0
    )

    # 新しいインスタンスを作成
    new_service = ExpenseService(data_dir=expense_service.data_dir)

    # データが読み込まれることを確認
    expenses = new_service.get_expenses()
    assert len(expenses) == 1

    budget = new_service.get_budget("2025-12")
    assert budget is not None
    assert budget.total_budget == 50000.0

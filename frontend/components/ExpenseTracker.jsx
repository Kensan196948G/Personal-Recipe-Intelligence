/**
 * 支出トラッカーコンポーネント
 *
 * 食費の記録・予算管理・分析を行う。
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  LinearProgress,
  Paper,
  Alert,
  Tabs,
  Tab,
  InputAdornment
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';


const CATEGORIES = [
  '食材',
  '外食',
  '調味料',
  '飲料',
  'その他'
];

const CATEGORY_COLORS = {
  '食材': '#FF6384',
  '外食': '#36A2EB',
  '調味料': '#FFCE56',
  '飲料': '#4BC0C0',
  'その他': '#9966FF'
};


const ExpenseTracker = () => {
  const [tabValue, setTabValue] = useState(0);

  // 支出入力フォーム
  const [expenseForm, setExpenseForm] = useState({
    date: new Date().toISOString().split('T')[0],
    amount: '',
    category: '食材',
    description: ''
  });

  // 予算設定フォーム
  const [budgetForm, setBudgetForm] = useState({
    month: new Date().toISOString().slice(0, 7),
    totalBudget: '',
    categoryBudgets: {}
  });

  // データ
  const [summary, setSummary] = useState(null);
  const [budget, setBudget] = useState(null);
  const [categoryBreakdown, setCategoryBreakdown] = useState({});
  const [trends, setTrends] = useState(null);
  const [expenses, setExpenses] = useState([]);

  // UI状態
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);


  // 初期データ読み込み
  useEffect(() => {
    loadSummary();
    loadBudget();
    loadCategoryBreakdown();
    loadTrends();
    loadExpenses();
  }, []);


  // API呼び出し
  const apiCall = async (endpoint, method = 'GET', body = null) => {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(endpoint, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || data.detail || 'API call failed');
    }

    return data;
  };


  // サマリー読み込み
  const loadSummary = async (period = 'month') => {
    try {
      const data = await apiCall(`/api/v1/expense/summary?period=${period}`);
      setSummary(data.data.summary);
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  };


  // 予算読み込み
  const loadBudget = async () => {
    try {
      const month = budgetForm.month;
      const data = await apiCall(`/api/v1/expense/budget?month=${month}`);
      setBudget(data.data.budget);
    } catch (err) {
      console.error('Failed to load budget:', err);
    }
  };


  // カテゴリ別内訳読み込み
  const loadCategoryBreakdown = async () => {
    try {
      const month = budgetForm.month;
      const data = await apiCall(`/api/v1/expense/category-breakdown?month=${month}`);
      setCategoryBreakdown(data.data.breakdown);
    } catch (err) {
      console.error('Failed to load category breakdown:', err);
    }
  };


  // トレンド読み込み
  const loadTrends = async () => {
    try {
      const data = await apiCall('/api/v1/expense/trends?months=6');
      setTrends(data.data.trends);
    } catch (err) {
      console.error('Failed to load trends:', err);
    }
  };


  // 支出記録読み込み
  const loadExpenses = async () => {
    try {
      const today = new Date();
      const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
      const startDate = startOfMonth.toISOString().split('T')[0];

      const data = await apiCall(`/api/v1/expense/expenses?start_date=${startDate}`);
      setExpenses(data.data.expenses);
    } catch (err) {
      console.error('Failed to load expenses:', err);
    }
  };


  // 支出記録
  const handleAddExpense = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiCall('/api/v1/expense/record', 'POST', {
        date: expenseForm.date,
        amount: parseFloat(expenseForm.amount),
        category: expenseForm.category,
        description: expenseForm.description
      });

      setSuccess('支出を記録しました');
      setExpenseForm({
        date: new Date().toISOString().split('T')[0],
        amount: '',
        category: '食材',
        description: ''
      });

      // データを再読み込み
      await loadSummary();
      await loadCategoryBreakdown();
      await loadExpenses();

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };


  // 予算設定
  const handleSetBudget = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiCall('/api/v1/expense/budget', 'POST', {
        month: budgetForm.month,
        total_budget: parseFloat(budgetForm.totalBudget),
        category_budgets: budgetForm.categoryBudgets
      });

      setSuccess('予算を設定しました');

      // データを再読み込み
      await loadBudget();
      await loadSummary();

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };


  // 円グラフ用データ変換
  const getPieChartData = () => {
    return Object.entries(categoryBreakdown)
      .filter(([_, amount]) => amount > 0)
      .map(([category, amount]) => ({
        name: category,
        value: amount
      }));
  };


  // 折れ線グラフ用データ変換
  const getLineChartData = () => {
    if (!trends || !trends.monthly_totals) return [];
    return trends.monthly_totals;
  };


  // 予算プログレスバー
  const renderBudgetProgress = () => {
    if (!summary || !budget) return null;

    const percentage = (summary.total_spent / budget.total_budget) * 100;
    const remaining = budget.total_budget - summary.total_spent;
    const color = percentage > 100 ? 'error' : percentage > 80 ? 'warning' : 'primary';

    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          月次予算
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2">
            {summary.total_spent.toLocaleString()}円 / {budget.total_budget.toLocaleString()}円
          </Typography>
          <Typography variant="body2" color={color}>
            残り {remaining.toLocaleString()}円
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={Math.min(percentage, 100)}
          color={color}
          sx={{ height: 10, borderRadius: 5 }}
        />
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
          {percentage.toFixed(1)}% 使用
        </Typography>
      </Box>
    );
  };


  // 支出入力タブ
  const renderExpenseTab = () => (
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            支出を記録
          </Typography>

          <form onSubmit={handleAddExpense}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="日付"
                  type="date"
                  value={expenseForm.date}
                  onChange={(e) => setExpenseForm({ ...expenseForm, date: e.target.value })}
                  fullWidth
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  label="金額"
                  type="number"
                  value={expenseForm.amount}
                  onChange={(e) => setExpenseForm({ ...expenseForm, amount: e.target.value })}
                  fullWidth
                  required
                  InputProps={{
                    endAdornment: <InputAdornment position="end">円</InputAdornment>
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>カテゴリ</InputLabel>
                  <Select
                    value={expenseForm.category}
                    onChange={(e) => setExpenseForm({ ...expenseForm, category: e.target.value })}
                    label="カテゴリ"
                  >
                    {CATEGORIES.map((cat) => (
                      <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  label="説明"
                  value={expenseForm.description}
                  onChange={(e) => setExpenseForm({ ...expenseForm, description: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  disabled={loading}
                >
                  記録する
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      {summary && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              今月のサマリー
            </Typography>

            {budget && renderBudgetProgress()}

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    合計支出
                  </Typography>
                  <Typography variant="h5">
                    {summary.total_spent.toLocaleString()}円
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={6}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    日平均
                  </Typography>
                  <Typography variant="h5">
                    {summary.daily_average.toFixed(0).toLocaleString()}円
                  </Typography>
                </Paper>
              </Grid>
            </Grid>

            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                トレンド:
                <Typography
                  component="span"
                  sx={{
                    ml: 1,
                    color: summary.trend === 'increasing' ? 'error.main' :
                           summary.trend === 'decreasing' ? 'success.main' : 'text.primary'
                  }}
                >
                  {summary.trend === 'increasing' ? '増加傾向' :
                   summary.trend === 'decreasing' ? '減少傾向' : '安定'}
                </Typography>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {expenses.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              最近の支出
            </Typography>

            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              {expenses.slice(0, 10).map((expense) => (
                <Paper key={expense.id} sx={{ p: 2, mb: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="body1">{expense.description}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {expense.category} • {expense.date}
                      </Typography>
                    </Box>
                    <Typography variant="h6">
                      {expense.amount.toLocaleString()}円
                    </Typography>
                  </Box>
                </Paper>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );


  // 予算設定タブ
  const renderBudgetTab = () => (
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            月次予算を設定
          </Typography>

          <form onSubmit={handleSetBudget}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="対象月"
                  type="month"
                  value={budgetForm.month}
                  onChange={(e) => setBudgetForm({ ...budgetForm, month: e.target.value })}
                  fullWidth
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  label="総予算"
                  type="number"
                  value={budgetForm.totalBudget}
                  onChange={(e) => setBudgetForm({ ...budgetForm, totalBudget: e.target.value })}
                  fullWidth
                  required
                  InputProps={{
                    endAdornment: <InputAdornment position="end">円</InputAdornment>
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  disabled={loading}
                >
                  予算を設定
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      {budget && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              現在の予算設定
            </Typography>

            <Typography variant="body1">
              対象月: {budget.month}
            </Typography>
            <Typography variant="h5" sx={{ mt: 1 }}>
              {budget.total_budget.toLocaleString()}円
            </Typography>

            {summary && (
              <Box sx={{ mt: 2 }}>
                {renderBudgetProgress()}
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );


  // 分析タブ
  const renderAnalyticsTab = () => (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                カテゴリ別支出
              </Typography>

              {getPieChartData().length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={getPieChartData()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value.toLocaleString()}円`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {getPieChartData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.name]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value.toLocaleString()}円`} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 5 }}>
                  データがありません
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                カテゴリ別内訳
              </Typography>

              <Box sx={{ mt: 2 }}>
                {CATEGORIES.map((category) => {
                  const amount = categoryBreakdown[category] || 0;
                  const total = Object.values(categoryBreakdown).reduce((sum, val) => sum + val, 0);
                  const percentage = total > 0 ? (amount / total) * 100 : 0;

                  return (
                    <Box key={category} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2">{category}</Typography>
                        <Typography variant="body2">{amount.toLocaleString()}円</Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={percentage}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: '#e0e0e0',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: CATEGORY_COLORS[category]
                          }
                        }}
                      />
                    </Box>
                  );
                })}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                月次支出推移
              </Typography>

              {getLineChartData().length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={getLineChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value.toLocaleString()}円`} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="total"
                      stroke="#8884d8"
                      strokeWidth={2}
                      name="支出額"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 5 }}>
                  データがありません
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );


  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        支出トラッカー
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, val) => setTabValue(val)}>
          <Tab label="支出記録" />
          <Tab label="予算設定" />
          <Tab label="分析" />
        </Tabs>
      </Box>

      {tabValue === 0 && renderExpenseTab()}
      {tabValue === 1 && renderBudgetTab()}
      {tabValue === 2 && renderAnalyticsTab()}
    </Box>
  );
};


export default ExpenseTracker;

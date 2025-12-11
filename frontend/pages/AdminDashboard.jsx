/**
 * 管理者ダッシュボードページ
 *
 * システム統計、レシピ・ユーザー統計、設定管理、ログ表示を提供。
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [systemStats, setSystemStats] = useState(null);
  const [recipeStats, setRecipeStats] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [settings, setSettings] = useState(null);
  const [logs, setLogs] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statsPeriod, setStatsPeriod] = useState(30);

  const adminToken = localStorage.getItem('adminToken');

  useEffect(() => {
    if (!adminToken) {
      setError('管理者トークンが設定されていません。');
      return;
    }

    loadData();
  }, [activeTab, statsPeriod]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      if (activeTab === 'overview') {
        await loadSystemStats();
        await loadHealth();
      } else if (activeTab === 'recipes') {
        await loadRecipeStats();
      } else if (activeTab === 'users') {
        await loadUserStats();
      } else if (activeTab === 'settings') {
        await loadSettings();
      } else if (activeTab === 'logs') {
        await loadLogs();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchAdmin = async (endpoint, options = {}) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${adminToken}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API エラー: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    if (data.status !== 'ok') {
      throw new Error(data.error || 'Unknown error');
    }

    return data.data;
  };

  const loadSystemStats = async () => {
    const data = await fetchAdmin('/api/v1/admin/stats');
    setSystemStats(data);
  };

  const loadRecipeStats = async () => {
    const data = await fetchAdmin(`/api/v1/admin/stats/recipes?days=${statsPeriod}`);
    setRecipeStats(data);
  };

  const loadUserStats = async () => {
    const data = await fetchAdmin(`/api/v1/admin/stats/users?days=${statsPeriod}`);
    setUserStats(data);
  };

  const loadSettings = async () => {
    const data = await fetchAdmin('/api/v1/admin/settings');
    setSettings(data);
  };

  const loadLogs = async () => {
    const data = await fetchAdmin('/api/v1/admin/logs?limit=50');
    setLogs(data.logs);
  };

  const loadHealth = async () => {
    const data = await fetchAdmin('/api/v1/admin/health');
    setHealth(data);
  };

  const handleUpdateSettings = async (updatedSettings) => {
    try {
      const data = await fetchAdmin('/api/v1/admin/settings', {
        method: 'PUT',
        body: JSON.stringify(updatedSettings),
      });
      setSettings(data);
      alert('設定を更新しました。');
    } catch (err) {
      alert(`設定の更新に失敗しました: ${err.message}`);
    }
  };

  const handleClearCache = async () => {
    try {
      await fetchAdmin('/api/v1/admin/cache/clear', { method: 'POST' });
      alert('キャッシュをクリアしました。');
      await loadData();
    } catch (err) {
      alert(`キャッシュのクリアに失敗しました: ${err.message}`);
    }
  };

  if (!adminToken) {
    return <AdminLogin onLogin={(token) => localStorage.setItem('adminToken', token)} />;
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>管理者ダッシュボード</h1>
        <button
          className="btn-logout"
          onClick={() => {
            localStorage.removeItem('adminToken');
            window.location.reload();
          }}
        >
          ログアウト
        </button>
      </header>

      <nav className="admin-nav">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          概要
        </button>
        <button
          className={activeTab === 'recipes' ? 'active' : ''}
          onClick={() => setActiveTab('recipes')}
        >
          レシピ統計
        </button>
        <button
          className={activeTab === 'users' ? 'active' : ''}
          onClick={() => setActiveTab('users')}
        >
          ユーザー統計
        </button>
        <button
          className={activeTab === 'settings' ? 'active' : ''}
          onClick={() => setActiveTab('settings')}
        >
          設定
        </button>
        <button
          className={activeTab === 'logs' ? 'active' : ''}
          onClick={() => setActiveTab('logs')}
        >
          ログ
        </button>
      </nav>

      {error && <div className="error-message">{error}</div>}

      {loading && <div className="loading">読み込み中...</div>}

      <div className="admin-content">
        {activeTab === 'overview' && systemStats && (
          <OverviewTab stats={systemStats} health={health} onClearCache={handleClearCache} />
        )}
        {activeTab === 'recipes' && recipeStats && (
          <RecipeStatsTab
            stats={recipeStats}
            period={statsPeriod}
            onPeriodChange={setStatsPeriod}
          />
        )}
        {activeTab === 'users' && userStats && (
          <UserStatsTab
            stats={userStats}
            period={statsPeriod}
            onPeriodChange={setStatsPeriod}
          />
        )}
        {activeTab === 'settings' && settings && (
          <SettingsTab settings={settings} onUpdate={handleUpdateSettings} />
        )}
        {activeTab === 'logs' && <LogsTab logs={logs} />}
      </div>

      <style jsx>{`
        .admin-dashboard {
          max-width: 1400px;
          margin: 0 auto;
          padding: 20px;
        }

        .admin-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 2px solid #e0e0e0;
        }

        .admin-header h1 {
          margin: 0;
          font-size: 28px;
          color: #333;
        }

        .btn-logout {
          padding: 8px 16px;
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .btn-logout:hover {
          background: #c82333;
        }

        .admin-nav {
          display: flex;
          gap: 10px;
          margin-bottom: 30px;
        }

        .admin-nav button {
          padding: 10px 20px;
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .admin-nav button:hover {
          background: #e9ecef;
        }

        .admin-nav button.active {
          background: #007bff;
          color: white;
          border-color: #007bff;
        }

        .error-message {
          padding: 15px;
          background: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .loading {
          text-align: center;
          padding: 40px;
          font-size: 18px;
          color: #666;
        }

        .admin-content {
          min-height: 400px;
        }
      `}</style>
    </div>
  );
};

const OverviewTab = ({ stats, health, onClearCache }) => {
  const recipeData = [
    { name: '公開', value: stats.recipes.public },
    { name: '非公開', value: stats.recipes.private },
  ];

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return '#28a745';
      case 'degraded':
        return '#ffc107';
      case 'unhealthy':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  return (
    <div className="overview-tab">
      <div className="stats-grid">
        <div className="stat-card">
          <h3>レシピ総数</h3>
          <p className="stat-number">{stats.recipes.total}</p>
          <small>直近7日: {stats.recipes.recent_week}</small>
        </div>
        <div className="stat-card">
          <h3>ユーザー数</h3>
          <p className="stat-number">{stats.users.total}</p>
          <small>アクティブ（30日）: {stats.users.active_30d}</small>
        </div>
        <div className="stat-card">
          <h3>タグ数</h3>
          <p className="stat-number">{stats.tags.total}</p>
        </div>
        <div className="stat-card">
          <h3>ストレージ使用量</h3>
          <p className="stat-number">{stats.system.storage_used}</p>
          <small>DB: {stats.system.database_size}</small>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>レシピの公開設定</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={recipeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {recipeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>人気タグ TOP 10</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.tags.top}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {health && (
        <div className="health-card">
          <h3>システムヘルスチェック</h3>
          <div
            className="health-status"
            style={{ backgroundColor: getHealthStatusColor(health.status) }}
          >
            {health.status.toUpperCase()}
          </div>
          <div className="health-checks">
            {Object.entries(health.checks).map(([key, check]) => (
              <div key={key} className="health-check-item">
                <span className="check-name">{key}:</span>
                <span className={`check-status status-${check.status}`}>{check.status}</span>
                {check.message && <span className="check-message">{check.message}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="actions">
        <button className="btn btn-primary" onClick={onClearCache}>
          統計キャッシュをクリア
        </button>
      </div>

      <style jsx>{`
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .stat-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .stat-card h3 {
          margin: 0 0 10px 0;
          font-size: 14px;
          color: #666;
          text-transform: uppercase;
        }

        .stat-number {
          font-size: 32px;
          font-weight: bold;
          margin: 10px 0;
          color: #007bff;
        }

        .stat-card small {
          color: #999;
          font-size: 12px;
        }

        .charts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .chart-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .chart-card h3 {
          margin: 0 0 20px 0;
          font-size: 16px;
          color: #333;
        }

        .health-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          margin-bottom: 20px;
        }

        .health-status {
          display: inline-block;
          padding: 8px 16px;
          color: white;
          border-radius: 4px;
          font-weight: bold;
          margin-bottom: 15px;
        }

        .health-checks {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .health-check-item {
          display: flex;
          gap: 10px;
          padding: 10px;
          background: #f8f9fa;
          border-radius: 4px;
        }

        .check-name {
          font-weight: bold;
          min-width: 150px;
        }

        .check-status {
          padding: 2px 8px;
          border-radius: 3px;
          font-size: 12px;
          font-weight: bold;
        }

        .status-ok {
          background: #d4edda;
          color: #155724;
        }

        .status-warning {
          background: #fff3cd;
          color: #856404;
        }

        .status-error {
          background: #f8d7da;
          color: #721c24;
        }

        .check-message {
          color: #666;
          font-size: 12px;
        }

        .actions {
          display: flex;
          gap: 10px;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
        }
      `}</style>
    </div>
  );
};

const RecipeStatsTab = ({ stats, period, onPeriodChange }) => {
  return (
    <div className="recipe-stats-tab">
      <div className="period-selector">
        <label>集計期間: </label>
        <select value={period} onChange={(e) => onPeriodChange(Number(e.target.value))}>
          <option value={7}>7日間</option>
          <option value={30}>30日間</option>
          <option value={90}>90日間</option>
          <option value={365}>1年間</option>
        </select>
      </div>

      <div className="stats-summary">
        <h3>期間内のレシピ総数: {stats.total_recipes}</h3>
        <p>平均調理時間: {stats.averages.cooking_time} 分</p>
        <p>平均人数: {stats.averages.servings} 人分</p>
      </div>

      <div className="chart-card">
        <h3>日別レシピ作成数</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={stats.daily_counts}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#8884d8" name="レシピ数" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <h3>ソース別レシピ数</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stats.source_counts}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="source" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <style jsx>{`
        .period-selector {
          margin-bottom: 20px;
        }

        .period-selector label {
          margin-right: 10px;
          font-weight: bold;
        }

        .period-selector select {
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .stats-summary {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          margin-bottom: 20px;
        }

        .stats-summary h3 {
          margin: 0 0 10px 0;
          color: #007bff;
        }

        .chart-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          margin-bottom: 20px;
        }

        .chart-card h3 {
          margin: 0 0 20px 0;
        }
      `}</style>
    </div>
  );
};

const UserStatsTab = ({ stats, period, onPeriodChange }) => {
  return (
    <div className="user-stats-tab">
      <div className="period-selector">
        <label>集計期間: </label>
        <select value={period} onChange={(e) => onPeriodChange(Number(e.target.value))}>
          <option value={7}>7日間</option>
          <option value={30}>30日間</option>
          <option value={90}>90日間</option>
          <option value={365}>1年間</option>
        </select>
      </div>

      <div className="stats-summary">
        <h3>新規ユーザー: {stats.new_users}</h3>
        <p>アクティブユーザー: {stats.active_users}</p>
      </div>

      <div className="chart-card">
        <h3>日別ログイン数</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={stats.daily_logins}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#ff7300" name="ログイン数" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="contributors-card">
        <h3>レシピ投稿ランキング TOP 10</h3>
        <table>
          <thead>
            <tr>
              <th>順位</th>
              <th>ユーザー名</th>
              <th>メール</th>
              <th>レシピ数</th>
            </tr>
          </thead>
          <tbody>
            {stats.top_contributors.map((user, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>{user.recipe_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style jsx>{`
        .period-selector {
          margin-bottom: 20px;
        }

        .period-selector label {
          margin-right: 10px;
          font-weight: bold;
        }

        .period-selector select {
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .stats-summary {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          margin-bottom: 20px;
        }

        .stats-summary h3 {
          margin: 0 0 10px 0;
          color: #007bff;
        }

        .chart-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          margin-bottom: 20px;
        }

        .chart-card h3 {
          margin: 0 0 20px 0;
        }

        .contributors-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .contributors-card h3 {
          margin: 0 0 20px 0;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        th,
        td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #ddd;
        }

        th {
          background: #f8f9fa;
          font-weight: bold;
        }

        tr:hover {
          background: #f8f9fa;
        }
      `}</style>
    </div>
  );
};

const SettingsTab = ({ settings, onUpdate }) => {
  const [formData, setFormData] = useState(settings);

  const handleChange = (key, value) => {
    setFormData({ ...formData, [key]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate(formData);
  };

  return (
    <div className="settings-tab">
      <form onSubmit={handleSubmit}>
        <div className="settings-section">
          <h3>基本設定</h3>
          <div className="form-group">
            <label>サイト名</label>
            <input
              type="text"
              value={formData.site_name}
              onChange={(e) => handleChange('site_name', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>デフォルト言語</label>
            <select
              value={formData.default_language}
              onChange={(e) => handleChange('default_language', e.target.value)}
            >
              <option value="ja">日本語</option>
              <option value="en">English</option>
            </select>
          </div>
          <div className="form-group">
            <label>タイムゾーン</label>
            <input
              type="text"
              value={formData.timezone}
              onChange={(e) => handleChange('timezone', e.target.value)}
            />
          </div>
        </div>

        <div className="settings-section">
          <h3>機能設定</h3>
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={formData.enable_public_recipes}
                onChange={(e) => handleChange('enable_public_recipes', e.target.checked)}
              />
              公開レシピを有効化
            </label>
          </div>
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={formData.enable_user_registration}
                onChange={(e) => handleChange('enable_user_registration', e.target.checked)}
              />
              ユーザー登録を有効化
            </label>
          </div>
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={formData.ocr_enabled}
                onChange={(e) => handleChange('ocr_enabled', e.target.checked)}
              />
              OCR機能を有効化
            </label>
          </div>
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={formData.scraping_enabled}
                onChange={(e) => handleChange('scraping_enabled', e.target.checked)}
              />
              スクレイピング機能を有効化
            </label>
          </div>
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={formData.maintenance_mode}
                onChange={(e) => handleChange('maintenance_mode', e.target.checked)}
              />
              メンテナンスモード
            </label>
          </div>
        </div>

        <div className="settings-section">
          <h3>制限設定</h3>
          <div className="form-group">
            <label>最大アップロードサイズ (MB)</label>
            <input
              type="number"
              min="1"
              max="100"
              value={formData.max_upload_size_mb}
              onChange={(e) => handleChange('max_upload_size_mb', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>ユーザーあたりの最大レシピ数</label>
            <input
              type="number"
              min="100"
              max="10000"
              value={formData.max_recipes_per_user}
              onChange={(e) => handleChange('max_recipes_per_user', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>ページネーションサイズ</label>
            <input
              type="number"
              min="10"
              max="100"
              value={formData.pagination_size}
              onChange={(e) => handleChange('pagination_size', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>キャッシュTTL (秒)</label>
            <input
              type="number"
              min="60"
              max="3600"
              value={formData.cache_ttl_seconds}
              onChange={(e) => handleChange('cache_ttl_seconds', parseInt(e.target.value))}
            />
          </div>
        </div>

        <button type="submit" className="btn btn-primary">
          設定を保存
        </button>
      </form>

      <style jsx>{`
        .settings-tab {
          background: white;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .settings-section {
          margin-bottom: 30px;
          padding-bottom: 30px;
          border-bottom: 1px solid #e0e0e0;
        }

        .settings-section:last-of-type {
          border-bottom: none;
        }

        .settings-section h3 {
          margin: 0 0 20px 0;
          color: #333;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
          color: #555;
        }

        .form-group input[type='text'],
        .form-group input[type='number'],
        .form-group select {
          width: 100%;
          max-width: 400px;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .form-group.checkbox label {
          display: flex;
          align-items: center;
          font-weight: normal;
        }

        .form-group.checkbox input[type='checkbox'] {
          width: auto;
          margin-right: 10px;
        }

        .btn {
          padding: 12px 24px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 16px;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
        }
      `}</style>
    </div>
  );
};

const LogsTab = ({ logs }) => {
  const [filter, setFilter] = useState('all');

  const filteredLogs =
    filter === 'all' ? logs : logs.filter((log) => log.level === filter);

  const getLevelColor = (level) => {
    switch (level) {
      case 'ERROR':
        return '#dc3545';
      case 'WARNING':
        return '#ffc107';
      case 'INFO':
        return '#17a2b8';
      case 'DEBUG':
        return '#6c757d';
      default:
        return '#333';
    }
  };

  return (
    <div className="logs-tab">
      <div className="logs-header">
        <h3>システムログ ({filteredLogs.length}件)</h3>
        <div className="filter">
          <label>フィルタ: </label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">すべて</option>
            <option value="ERROR">ERROR</option>
            <option value="WARNING">WARNING</option>
            <option value="INFO">INFO</option>
            <option value="DEBUG">DEBUG</option>
          </select>
        </div>
      </div>

      <div className="logs-list">
        {filteredLogs.map((log, index) => (
          <div key={index} className="log-entry">
            <span className="log-timestamp">{log.timestamp}</span>
            <span className="log-level" style={{ color: getLevelColor(log.level) }}>
              [{log.level}]
            </span>
            <span className="log-message">{log.message}</span>
          </div>
        ))}
      </div>

      <style jsx>{`
        .logs-tab {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .logs-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 1px solid #e0e0e0;
        }

        .logs-header h3 {
          margin: 0;
        }

        .filter label {
          margin-right: 10px;
          font-weight: bold;
        }

        .filter select {
          padding: 6px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .logs-list {
          max-height: 600px;
          overflow-y: auto;
        }

        .log-entry {
          padding: 10px;
          margin-bottom: 5px;
          background: #f8f9fa;
          border-left: 3px solid #ddd;
          font-family: monospace;
          font-size: 13px;
        }

        .log-timestamp {
          color: #666;
          margin-right: 10px;
        }

        .log-level {
          font-weight: bold;
          margin-right: 10px;
        }

        .log-message {
          color: #333;
        }
      `}</style>
    </div>
  );
};

const AdminLogin = ({ onLogin }) => {
  const [token, setToken] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (token.trim()) {
      onLogin(token);
      window.location.reload();
    }
  };

  return (
    <div className="admin-login">
      <div className="login-card">
        <h2>管理者ログイン</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>管理者トークン</label>
            <input
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="管理者APIキーを入力"
              required
            />
          </div>
          <button type="submit" className="btn btn-primary">
            ログイン
          </button>
        </form>
      </div>

      <style jsx>{`
        .admin-login {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          background: #f0f2f5;
        }

        .login-card {
          background: white;
          padding: 40px;
          border-radius: 8px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          width: 100%;
          max-width: 400px;
        }

        .login-card h2 {
          margin: 0 0 30px 0;
          text-align: center;
          color: #333;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-weight: bold;
          color: #555;
        }

        .form-group input {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .btn {
          width: 100%;
          padding: 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 16px;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
        }
      `}</style>
    </div>
  );
};

export default AdminDashboard;

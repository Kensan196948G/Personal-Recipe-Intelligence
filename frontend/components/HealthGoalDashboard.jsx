/**
 * Health Goal Dashboard - 健康目標ダッシュボードコンポーネント
 */

import React, { useState, useEffect } from 'react';

const API_BASE = '/api/v1/health-goal';

const HealthGoalDashboard = () => {
  // State
  const [profile, setProfile] = useState(null);
  const [targets, setTargets] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [progress, setProgress] = useState(null);
  const [history, setHistory] = useState([]);
  const [advice, setAdvice] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Form state
  const [profileForm, setProfileForm] = useState({
    age: 30,
    gender: 'male',
    weight: 70,
    height: 170,
    activity_level: 'moderate'
  });

  const [targetsForm, setTargetsForm] = useState({
    calories: 2000,
    protein: 75,
    fat: 55,
    carbohydrate: 300,
    fiber: 21,
    salt: 7.5
  });

  const [nutritionInput, setNutritionInput] = useState({
    calories: 0,
    protein: 0,
    fat: 0,
    carbohydrate: 0,
    fiber: 0,
    salt: 0
  });

  // 初期データ読み込み
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadProfile(),
        loadTargets(),
        loadHistory()
      ]);
    } catch (error) {
      console.error('データ読み込みエラー:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadProfile = async () => {
    try {
      const response = await fetch(`${API_BASE}/profile`);
      if (response.ok) {
        const result = await response.json();
        setProfile(result.data);
        setProfileForm(result.data);
        await loadRecommendations();
      }
    } catch (error) {
      console.error('プロファイル読み込みエラー:', error);
    }
  };

  const loadTargets = async () => {
    try {
      const response = await fetch(`${API_BASE}/targets`);
      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          setTargets(result.data);
          setTargetsForm(result.data);
        }
      }
    } catch (error) {
      console.error('目標値読み込みエラー:', error);
    }
  };

  const loadRecommendations = async () => {
    try {
      const response = await fetch(`${API_BASE}/recommendations`);
      if (response.ok) {
        const result = await response.json();
        setRecommendations(result.data);
      }
    } catch (error) {
      console.error('推奨値読み込みエラー:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/history?days=7`);
      if (response.ok) {
        const result = await response.json();
        setHistory(result.data.history || []);
      }
    } catch (error) {
      console.error('履歴読み込みエラー:', error);
    }
  };

  // プロファイル保存
  const saveProfile = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileForm)
      });

      if (response.ok) {
        const result = await response.json();
        setProfile(result.data);
        await loadRecommendations();
        alert('プロファイルを保存しました');
      }
    } catch (error) {
      console.error('プロファイル保存エラー:', error);
      alert('保存に失敗しました');
    }
  };

  // 目標値保存
  const saveTargets = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/targets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(targetsForm)
      });

      if (response.ok) {
        const result = await response.json();
        setTargets(result.data.targets);
        alert('目標値を保存しました');
      }
    } catch (error) {
      console.error('目標値保存エラー:', error);
      alert('保存に失敗しました');
    }
  };

  // 達成率計算
  const calculateProgress = async () => {
    try {
      const response = await fetch(`${API_BASE}/progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nutrition_data: nutritionInput,
          target_date: new Date().toISOString().split('T')[0]
        })
      });

      if (response.ok) {
        const result = await response.json();
        setProgress(result.data);
        await getAdvice();
        await loadHistory();
      }
    } catch (error) {
      console.error('達成率計算エラー:', error);
    }
  };

  // アドバイス取得
  const getAdvice = async () => {
    try {
      const response = await fetch(`${API_BASE}/advice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nutrition_data: nutritionInput,
          target_date: new Date().toISOString().split('T')[0]
        })
      });

      if (response.ok) {
        const result = await response.json();
        setAdvice(result.data);
      }
    } catch (error) {
      console.error('アドバイス取得エラー:', error);
    }
  };

  // 推奨値を目標値にコピー
  const useRecommendations = () => {
    if (recommendations) {
      setTargetsForm(recommendations);
    }
  };

  // ステータスカラー取得
  const getStatusColor = (status) => {
    const colors = {
      excellent: '#4caf50',
      good: '#8bc34a',
      fair: '#ff9800',
      poor: '#f44336'
    };
    return colors[status] || '#9e9e9e';
  };

  // ステータステキスト取得
  const getStatusText = (status) => {
    const texts = {
      excellent: '優秀',
      good: '良好',
      fair: '要改善',
      poor: '不足'
    };
    return texts[status] || '-';
  };

  // 栄養素名の日本語変換
  const getNutrientLabel = (key) => {
    const labels = {
      calories: 'カロリー',
      protein: 'タンパク質',
      fat: '脂質',
      carbohydrate: '炭水化物',
      fiber: '食物繊維',
      salt: '塩分'
    };
    return labels[key] || key;
  };

  // 単位取得
  const getUnit = (key) => {
    return key === 'calories' ? 'kcal' : 'g';
  };

  // ゲージコンポーネント
  const ProgressGauge = ({ label, value, target, achievement, status }) => {
    const percentage = Math.min(achievement, 150);
    const color = getStatusColor(status);

    return (
      <div style={styles.gaugeContainer}>
        <div style={styles.gaugeHeader}>
          <span style={styles.gaugeLabel}>{label}</span>
          <span style={styles.gaugeStatus}>{getStatusText(status)}</span>
        </div>
        <div style={styles.gaugeBar}>
          <div
            style={{
              ...styles.gaugeFill,
              width: `${percentage}%`,
              backgroundColor: color
            }}
          />
        </div>
        <div style={styles.gaugeFooter}>
          <span>{value.toFixed(1)} / {target.toFixed(1)} {getUnit(label.toLowerCase())}</span>
          <span>{achievement.toFixed(1)}%</span>
        </div>
      </div>
    );
  };

  if (loading) {
    return <div style={styles.loading}>読み込み中...</div>;
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>健康目標ダッシュボード</h1>

      {/* タブ */}
      <div style={styles.tabs}>
        <button
          style={activeTab === 'dashboard' ? styles.tabActive : styles.tab}
          onClick={() => setActiveTab('dashboard')}
        >
          ダッシュボード
        </button>
        <button
          style={activeTab === 'profile' ? styles.tabActive : styles.tab}
          onClick={() => setActiveTab('profile')}
        >
          プロファイル設定
        </button>
        <button
          style={activeTab === 'targets' ? styles.tabActive : styles.tab}
          onClick={() => setActiveTab('targets')}
        >
          目標値設定
        </button>
      </div>

      {/* ダッシュボードタブ */}
      {activeTab === 'dashboard' && (
        <div style={styles.content}>
          {/* 栄養入力 */}
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>今日の栄養摂取</h2>
            <div style={styles.inputGrid}>
              {Object.keys(nutritionInput).map(key => (
                <div key={key} style={styles.inputGroup}>
                  <label style={styles.label}>{getNutrientLabel(key)}</label>
                  <input
                    type="number"
                    value={nutritionInput[key]}
                    onChange={(e) => setNutritionInput({
                      ...nutritionInput,
                      [key]: parseFloat(e.target.value) || 0
                    })}
                    style={styles.input}
                  />
                  <span style={styles.unit}>{getUnit(key)}</span>
                </div>
              ))}
            </div>
            <button onClick={calculateProgress} style={styles.button}>
              達成率を計算
            </button>
          </div>

          {/* 達成率ゲージ */}
          {progress && (
            <div style={styles.section}>
              <h2 style={styles.sectionTitle}>達成率</h2>
              <div style={styles.gaugesGrid}>
                {Object.entries(progress.progress).map(([key, data]) => (
                  <ProgressGauge
                    key={key}
                    label={getNutrientLabel(key)}
                    value={data.actual}
                    target={data.target}
                    achievement={data.achievement}
                    status={data.status}
                  />
                ))}
              </div>
            </div>
          )}

          {/* アドバイス */}
          {advice.length > 0 && (
            <div style={styles.section}>
              <h2 style={styles.sectionTitle}>改善アドバイス</h2>
              <div style={styles.adviceList}>
                {advice.map((item, index) => (
                  <div key={index} style={styles.adviceItem}>
                    <div style={styles.adviceHeader}>
                      <span style={styles.adviceNutrient}>
                        {getNutrientLabel(item.nutrient)}
                      </span>
                      <span
                        style={{
                          ...styles.adviceBadge,
                          backgroundColor: getStatusColor(item.status)
                        }}
                      >
                        {getStatusText(item.status)}
                      </span>
                    </div>
                    <p style={styles.adviceText}>{item.advice}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 週間履歴 */}
          {history.length > 0 && (
            <div style={styles.section}>
              <h2 style={styles.sectionTitle}>週間達成履歴</h2>
              <div style={styles.historyGrid}>
                {history.map((day, index) => (
                  <div
                    key={index}
                    style={day.progress ? styles.historyDay : styles.historyDayEmpty}
                  >
                    <div style={styles.historyDate}>
                      {new Date(day.date).toLocaleDateString('ja-JP', {
                        month: 'numeric',
                        day: 'numeric'
                      })}
                    </div>
                    {day.progress && (
                      <div style={styles.historyStatus}>
                        {Object.values(day.progress).filter(
                          p => p.status === 'excellent' || p.status === 'good'
                        ).length} / 6
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* プロファイル設定タブ */}
      {activeTab === 'profile' && (
        <div style={styles.content}>
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>個人プロファイル</h2>
            <form onSubmit={saveProfile} style={styles.form}>
              <div style={styles.formGroup}>
                <label style={styles.label}>年齢</label>
                <input
                  type="number"
                  value={profileForm.age}
                  onChange={(e) => setProfileForm({
                    ...profileForm,
                    age: parseInt(e.target.value)
                  })}
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>性別</label>
                <select
                  value={profileForm.gender}
                  onChange={(e) => setProfileForm({
                    ...profileForm,
                    gender: e.target.value
                  })}
                  style={styles.select}
                >
                  <option value="male">男性</option>
                  <option value="female">女性</option>
                </select>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>体重（kg）</label>
                <input
                  type="number"
                  step="0.1"
                  value={profileForm.weight}
                  onChange={(e) => setProfileForm({
                    ...profileForm,
                    weight: parseFloat(e.target.value)
                  })}
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>身長（cm）</label>
                <input
                  type="number"
                  step="0.1"
                  value={profileForm.height}
                  onChange={(e) => setProfileForm({
                    ...profileForm,
                    height: parseFloat(e.target.value)
                  })}
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>活動レベル</label>
                <select
                  value={profileForm.activity_level}
                  onChange={(e) => setProfileForm({
                    ...profileForm,
                    activity_level: e.target.value
                  })}
                  style={styles.select}
                >
                  <option value="low">低（座り仕事中心）</option>
                  <option value="moderate">中（軽い運動・立ち仕事）</option>
                  <option value="high">高（定期的な運動）</option>
                  <option value="athlete">アスリート</option>
                </select>
              </div>

              <button type="submit" style={styles.button}>
                プロファイルを保存
              </button>
            </form>

            {recommendations && (
              <div style={styles.recommendationsBox}>
                <h3 style={styles.subsectionTitle}>推奨栄養素摂取量</h3>
                <div style={styles.recommendationsGrid}>
                  {Object.entries(recommendations).map(([key, value]) => (
                    <div key={key} style={styles.recommendationItem}>
                      <span>{getNutrientLabel(key)}</span>
                      <span style={styles.recommendationValue}>
                        {value.toFixed(1)} {getUnit(key)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 目標値設定タブ */}
      {activeTab === 'targets' && (
        <div style={styles.content}>
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>目標値設定</h2>
            {recommendations && (
              <button onClick={useRecommendations} style={styles.buttonSecondary}>
                推奨値を使用
              </button>
            )}
            <form onSubmit={saveTargets} style={styles.form}>
              {Object.keys(targetsForm).map(key => (
                <div key={key} style={styles.formGroup}>
                  <label style={styles.label}>{getNutrientLabel(key)}</label>
                  <input
                    type="number"
                    step="0.1"
                    value={targetsForm[key]}
                    onChange={(e) => setTargetsForm({
                      ...targetsForm,
                      [key]: parseFloat(e.target.value)
                    })}
                    style={styles.input}
                    required
                  />
                  <span style={styles.unit}>{getUnit(key)}</span>
                </div>
              ))}
              <button type="submit" style={styles.button}>
                目標値を保存
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// スタイル
const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '18px',
    color: '#666'
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#333'
  },
  tabs: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
    borderBottom: '2px solid #e0e0e0'
  },
  tab: {
    padding: '10px 20px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    color: '#666',
    borderBottom: '2px solid transparent',
    marginBottom: '-2px'
  },
  tabActive: {
    padding: '10px 20px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    color: '#2196f3',
    borderBottom: '2px solid #2196f3',
    fontWeight: 'bold',
    marginBottom: '-2px'
  },
  content: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px'
  },
  section: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '15px',
    color: '#333'
  },
  subsectionTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#555'
  },
  inputGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '15px',
    marginBottom: '20px'
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px'
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#555'
  },
  input: {
    padding: '8px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px'
  },
  select: {
    padding: '8px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px'
  },
  unit: {
    fontSize: '12px',
    color: '#999'
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#2196f3',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  },
  buttonSecondary: {
    padding: '8px 16px',
    backgroundColor: '#fff',
    color: '#2196f3',
    border: '1px solid #2196f3',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
    marginBottom: '15px'
  },
  gaugesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '15px'
  },
  gaugeContainer: {
    padding: '15px',
    backgroundColor: '#f5f5f5',
    borderRadius: '6px'
  },
  gaugeHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '8px'
  },
  gaugeLabel: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333'
  },
  gaugeStatus: {
    fontSize: '12px',
    fontWeight: 'bold',
    color: '#555'
  },
  gaugeBar: {
    height: '20px',
    backgroundColor: '#e0e0e0',
    borderRadius: '10px',
    overflow: 'hidden',
    marginBottom: '8px'
  },
  gaugeFill: {
    height: '100%',
    transition: 'width 0.3s ease'
  },
  gaugeFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
    color: '#666'
  },
  adviceList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  adviceItem: {
    padding: '15px',
    backgroundColor: '#fff3cd',
    borderLeft: '4px solid #ff9800',
    borderRadius: '4px'
  },
  adviceHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px'
  },
  adviceNutrient: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#333'
  },
  adviceBadge: {
    padding: '4px 8px',
    borderRadius: '12px',
    fontSize: '12px',
    color: '#fff',
    fontWeight: 'bold'
  },
  adviceText: {
    fontSize: '14px',
    color: '#555',
    margin: 0,
    lineHeight: '1.5'
  },
  historyGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(7, 1fr)',
    gap: '10px'
  },
  historyDay: {
    padding: '10px',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    textAlign: 'center'
  },
  historyDayEmpty: {
    padding: '10px',
    backgroundColor: '#f5f5f5',
    borderRadius: '4px',
    textAlign: 'center',
    opacity: 0.5
  },
  historyDate: {
    fontSize: '12px',
    fontWeight: 'bold',
    marginBottom: '5px',
    color: '#333'
  },
  historyStatus: {
    fontSize: '14px',
    color: '#2196f3',
    fontWeight: 'bold'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px'
  },
  recommendationsBox: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: '#e8f5e9',
    borderRadius: '6px'
  },
  recommendationsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '10px'
  },
  recommendationItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '14px',
    padding: '8px',
    backgroundColor: '#fff',
    borderRadius: '4px'
  },
  recommendationValue: {
    fontWeight: 'bold',
    color: '#4caf50'
  }
};

export default HealthGoalDashboard;

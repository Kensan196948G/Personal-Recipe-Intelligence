/**
 * 食事バランス可視化コンポーネント
 *
 * PFCバランス、栄養充足率、バランス評価をグラフで表示
 */

import React, { useState, useEffect } from 'react';

/**
 * PFC円グラフコンポーネント
 */
export const PFCPieChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="no-data">データがありません</div>;
  }

  const colors = {
    'タンパク質': '#3b82f6',
    '脂質': '#f59e0b',
    '炭水化物': '#10b981'
  };

  return (
    <div className="pfc-pie-chart">
      <h3>PFCバランス</h3>
      <div className="chart-container">
        {/* SVG円グラフ（簡易版） */}
        <svg viewBox="0 0 200 200" className="pie-svg">
          {data.map((item, index) => {
            const startAngle = data
              .slice(0, index)
              .reduce((sum, d) => sum + (d.value / 100) * 360, 0);
            const endAngle = startAngle + (item.value / 100) * 360;

            return (
              <g key={item.name}>
                <path
                  d={describePieSlice(100, 100, 80, startAngle, endAngle)}
                  fill={colors[item.name] || '#999'}
                  stroke="#fff"
                  strokeWidth="2"
                />
              </g>
            );
          })}
        </svg>

        {/* 凡例 */}
        <div className="legend">
          {data.map((item) => (
            <div key={item.name} className="legend-item">
              <span
                className="legend-color"
                style={{ backgroundColor: colors[item.name] || '#999' }}
              />
              <span className="legend-label">
                {item.name}: {item.value}% ({item.calories}kcal)
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * 栄養充足率棒グラフコンポーネント
 */
export const NutritionBarChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="no-data">データがありません</div>;
  }

  const getBarColor = (fulfillment) => {
    if (fulfillment >= 80 && fulfillment <= 120) return '#10b981'; // 緑
    if (fulfillment >= 60 && fulfillment < 80) return '#f59e0b';   // 黄
    if (fulfillment > 120 && fulfillment <= 140) return '#f59e0b'; // 黄
    return '#ef4444'; // 赤
  };

  const maxValue = Math.max(...data.map(d => Math.max(d.actual, d.reference))) * 1.2;

  return (
    <div className="nutrition-bar-chart">
      <h3>栄養素充足率（1日の基準値比較）</h3>
      <div className="chart-container">
        {data.map((item) => (
          <div key={item.nutrient} className="bar-item">
            <div className="bar-label">{item.nutrient}</div>
            <div className="bar-graph">
              <div className="bar-wrapper">
                <div
                  className="bar-actual"
                  style={{
                    width: `${(item.actual / maxValue) * 100}%`,
                    backgroundColor: getBarColor(item.fulfillment)
                  }}
                >
                  <span className="bar-value">{item.actual.toFixed(1)}</span>
                </div>
                <div
                  className="bar-reference"
                  style={{
                    left: `${(item.reference / maxValue) * 100}%`
                  }}
                >
                  <span className="reference-line" />
                </div>
              </div>
              <div className="bar-fulfillment">
                {item.fulfillment.toFixed(0)}%
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="chart-note">
        <span className="note-item">
          <span className="color-box" style={{ backgroundColor: '#10b981' }} /> 適正範囲
        </span>
        <span className="note-item">
          <span className="color-box" style={{ backgroundColor: '#f59e0b' }} /> 注意
        </span>
        <span className="note-item">
          <span className="color-box" style={{ backgroundColor: '#ef4444' }} /> 要改善
        </span>
      </div>
    </div>
  );
};

/**
 * レーダーチャートコンポーネント
 */
export const BalanceRadarChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="no-data">データがありません</div>;
  }

  const size = 200;
  const center = size / 2;
  const radius = 70;
  const levels = 5;

  const angleStep = (2 * Math.PI) / data.length;

  // スコアを座標に変換
  const getPoint = (score, index) => {
    const angle = index * angleStep - Math.PI / 2;
    const r = (score / 100) * radius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle)
    };
  };

  // データポイントのパス
  const dataPath = data.map((item, i) => {
    const point = getPoint(item.score, i);
    return `${i === 0 ? 'M' : 'L'} ${point.x} ${point.y}`;
  }).join(' ') + ' Z';

  return (
    <div className="balance-radar-chart">
      <h3>バランス評価レーダーチャート</h3>
      <svg viewBox={`0 0 ${size} ${size}`} className="radar-svg">
        {/* 背景円 */}
        {[...Array(levels)].map((_, i) => (
          <circle
            key={`level-${i}`}
            cx={center}
            cy={center}
            r={(radius / levels) * (i + 1)}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        ))}

        {/* 軸 */}
        {data.map((item, i) => {
          const point = getPoint(100, i);
          return (
            <line
              key={`axis-${i}`}
              x1={center}
              y1={center}
              x2={point.x}
              y2={point.y}
              stroke="#d1d5db"
              strokeWidth="1"
            />
          );
        })}

        {/* データ領域 */}
        <path
          d={dataPath}
          fill="rgba(59, 130, 246, 0.2)"
          stroke="#3b82f6"
          strokeWidth="2"
        />

        {/* データポイント */}
        {data.map((item, i) => {
          const point = getPoint(item.score, i);
          return (
            <circle
              key={`point-${i}`}
              cx={point.x}
              cy={point.y}
              r="3"
              fill="#3b82f6"
            />
          );
        })}

        {/* ラベル */}
        {data.map((item, i) => {
          const labelPoint = getPoint(115, i);
          return (
            <text
              key={`label-${i}`}
              x={labelPoint.x}
              y={labelPoint.y}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="10"
              fill="#374151"
            >
              {item.category}
            </text>
          );
        })}
      </svg>
    </div>
  );
};

/**
 * バランススコア表示コンポーネント
 */
export const BalanceScore = ({ score, evaluation, recommendations }) => {
  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 75) return '#3b82f6';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getEvaluationText = (evaluation) => {
    const texts = {
      excellent: '優秀',
      good: '良好',
      fair: '普通',
      needs_improvement: '要改善'
    };
    return texts[evaluation] || '不明';
  };

  return (
    <div className="balance-score">
      <div className="score-display">
        <div
          className="score-circle"
          style={{ borderColor: getScoreColor(score) }}
        >
          <span className="score-value" style={{ color: getScoreColor(score) }}>
            {score.toFixed(1)}
          </span>
          <span className="score-max">/100</span>
        </div>
        <div className="score-evaluation">
          評価: {getEvaluationText(evaluation)}
        </div>
      </div>

      {recommendations && recommendations.length > 0 && (
        <div className="recommendations">
          <h4>アドバイス</h4>
          <ul>
            {recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

/**
 * 統合バランスダッシュボードコンポーネント
 */
export const BalanceDashboard = ({ recipeId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [balanceData, setBalanceData] = useState(null);

  useEffect(() => {
    fetchBalanceData();
  }, [recipeId]);

  const fetchBalanceData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/balance/${recipeId}`);
      const result = await response.json();

      if (result.status === 'ok') {
        setBalanceData(result.data.evaluation);
        setError(null);
      } else {
        setError(result.error || 'データ取得に失敗しました');
      }
    } catch (err) {
      setError(`エラー: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  if (error) {
    return <div className="error">エラー: {error}</div>;
  }

  if (!balanceData) {
    return <div className="no-data">データがありません</div>;
  }

  return (
    <div className="balance-dashboard">
      <h2>食事バランス分析</h2>

      <div className="dashboard-grid">
        {/* スコア */}
        <div className="dashboard-item">
          <BalanceScore
            score={balanceData.score.overall_score}
            evaluation={balanceData.score.evaluation}
            recommendations={balanceData.pfc_balance.recommendations}
          />
        </div>

        {/* PFC円グラフ */}
        <div className="dashboard-item">
          <PFCPieChart data={balanceData.pfc_balance.pie_chart_data} />
        </div>

        {/* 1日の基準値比較 */}
        <div className="dashboard-item full-width">
          <div className="daily-reference">
            <h3>1日の食事摂取基準との比較</h3>
            <div className="reference-grid">
              {Object.entries(balanceData.daily_reference_percentage).map(([key, value]) => (
                <div key={key} className="reference-item">
                  <span className="ref-label">{key}</span>
                  <span className="ref-value">{value.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * 1日の食事バランスダッシュボード
 */
export const DailyBalanceDashboard = ({ meals, targetDate }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [balanceData, setBalanceData] = useState(null);

  useEffect(() => {
    fetchDailyBalance();
  }, [meals, targetDate]);

  const fetchDailyBalance = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/balance/daily', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meals, target_date: targetDate })
      });

      const result = await response.json();

      if (result.status === 'ok') {
        setBalanceData(result.data.evaluation);
        setError(null);
      } else {
        setError(result.error || 'データ取得に失敗しました');
      }
    } catch (err) {
      setError(`エラー: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  if (error) {
    return <div className="error">エラー: {error}</div>;
  }

  if (!balanceData) {
    return <div className="no-data">データがありません</div>;
  }

  return (
    <div className="daily-balance-dashboard">
      <h2>1日の食事バランス分析</h2>
      <p className="target-date">対象日: {targetDate}</p>

      <div className="dashboard-grid">
        {/* 総合スコア */}
        <div className="dashboard-item">
          <BalanceScore
            score={balanceData.overall_score}
            evaluation={balanceData.evaluation_level}
            recommendations={balanceData.recommendations}
          />
        </div>

        {/* PFCバランス */}
        <div className="dashboard-item">
          <PFCPieChart data={balanceData.pfc_balance.pie_chart_data} />
        </div>

        {/* 栄養充足率 */}
        <div className="dashboard-item full-width">
          <NutritionBarChart data={balanceData.bar_chart_data} />
        </div>

        {/* レーダーチャート */}
        <div className="dashboard-item">
          <BalanceRadarChart data={balanceData.radar_chart_data} />
        </div>
      </div>
    </div>
  );
};

// ヘルパー関数: 円グラフのパス生成
function describePieSlice(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';

  return [
    'M', cx, cy,
    'L', start.x, start.y,
    'A', r, r, 0, largeArcFlag, 0, end.x, end.y,
    'Z'
  ].join(' ');
}

function polarToCartesian(cx, cy, r, angle) {
  const angleInRadians = (angle - 90) * Math.PI / 180.0;
  return {
    x: cx + (r * Math.cos(angleInRadians)),
    y: cy + (r * Math.sin(angleInRadians))
  };
}

export default BalanceDashboard;

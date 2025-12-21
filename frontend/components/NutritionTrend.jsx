/**
 * 栄養推移グラフコンポーネント
 *
 * 栄養素の推移を折れ線グラフで表示します。
 * 期間切り替え（週/月/3ヶ月）と目標値との比較表示に対応。
 */

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

const NutritionTrend = ({ userId, nutrient, initialPeriod = 'month' }) => {
  const [period, setPeriod] = useState(initialPeriod);
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const periodDays = {
    week: 7,
    month: 30,
    quarter: 90,
  };

  const nutrientLabels = {
    calories: 'カロリー (kcal)',
    protein: 'タンパク質 (g)',
    fat: '脂質 (g)',
    carbohydrates: '炭水化物 (g)',
    fiber: '食物繊維 (g)',
    sodium: 'ナトリウム (mg)',
    calcium: 'カルシウム (mg)',
    iron: '鉄 (mg)',
    vitamin_c: 'ビタミンC (mg)',
  };

  const periodLabels = {
    week: '週間',
    month: '月間',
    quarter: '3ヶ月',
  };

  useEffect(() => {
    fetchTrendData();
  }, [userId, nutrient, period]);

  const fetchTrendData = async () => {
    setLoading(true);
    setError(null);

    try {
      const days = periodDays[period];
      const response = await fetch(
        `/api/v1/meal-history/nutrition-trend?user_id=${userId}&nutrient=${nutrient}&days=${days}`
      );

      const result = await response.json();

      if (result.status === 'ok') {
        setTrendData(result.data);
      } else {
        setError(result.error || '栄養推移データの取得に失敗しました');
      }
    } catch (err) {
      setError(`エラー: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatChartData = () => {
    if (!trendData) return [];

    return trendData.dates.map((date, index) => ({
      date: formatDate(date, period),
      value: trendData.values[index],
      target: trendData.statistics.target,
    }));
  };

  const formatDate = (dateStr, period) => {
    const date = new Date(dateStr);

    if (period === 'week') {
      // 週間: MM/DD
      return `${date.getMonth() + 1}/${date.getDate()}`;
    } else if (period === 'month') {
      // 月間: MM/DD
      return `${date.getMonth() + 1}/${date.getDate()}`;
    } else {
      // 3ヶ月: MM/DD
      return `${date.getMonth() + 1}/${date.getDate()}`;
    }
  };

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          style={{
            backgroundColor: 'white',
            border: '1px solid #ccc',
            borderRadius: '4px',
            padding: '10px',
          }}
        >
          <p style={{ margin: 0, fontWeight: 'bold' }}>{label}</p>
          <p style={{ margin: '5px 0', color: '#8884d8' }}>
            実績: {data.value.toFixed(1)}
          </p>
          {data.target && (
            <p style={{ margin: '5px 0', color: '#82ca9d' }}>
              目標: {data.target.toFixed(1)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <p>読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: 'red' }}>
        <p>{error}</p>
        <button onClick={fetchTrendData}>再読み込み</button>
      </div>
    );
  }

  if (!trendData) {
    return null;
  }

  const chartData = formatChartData();
  const hasTarget = trendData.statistics.target !== null;

  return (
    <div style={{ width: '100%', padding: '20px' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
        }}
      >
        <h2 style={{ margin: 0 }}>
          {nutrientLabels[nutrient] || nutrient} の推移
        </h2>

        <div style={{ display: 'flex', gap: '10px' }}>
          {Object.keys(periodDays).map((p) => (
            <button
              key={p}
              onClick={() => handlePeriodChange(p)}
              style={{
                padding: '8px 16px',
                backgroundColor: period === p ? '#4CAF50' : '#e0e0e0',
                color: period === p ? 'white' : 'black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px',
              }}
            >
              {periodLabels[p]}
            </button>
          ))}
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '15px',
          marginBottom: '20px',
        }}
      >
        <div
          style={{
            padding: '15px',
            backgroundColor: '#f5f5f5',
            borderRadius: '8px',
          }}
        >
          <div style={{ fontSize: '12px', color: '#666' }}>平均値</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
            {trendData.statistics.average.toFixed(1)}
          </div>
        </div>

        {hasTarget && (
          <div
            style={{
              padding: '15px',
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
            }}
          >
            <div style={{ fontSize: '12px', color: '#666' }}>目標値</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
              {trendData.statistics.target.toFixed(1)}
            </div>
          </div>
        )}

        {hasTarget && (
          <div
            style={{
              padding: '15px',
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
            }}
          >
            <div style={{ fontSize: '12px', color: '#666' }}>達成率</div>
            <div
              style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color:
                  (trendData.statistics.average / trendData.statistics.target) *
                    100 >=
                  80
                    ? '#4CAF50'
                    : '#ff9800',
              }}
            >
              {(
                (trendData.statistics.average / trendData.statistics.target) *
                100
              ).toFixed(0)}
              %
            </div>
          </div>
        )}

        <div
          style={{
            padding: '15px',
            backgroundColor: '#f5f5f5',
            borderRadius: '8px',
          }}
        >
          <div style={{ fontSize: '12px', color: '#666' }}>標準偏差</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
            {trendData.statistics.std_dev.toFixed(1)}
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            angle={period === 'quarter' ? -45 : 0}
            textAnchor={period === 'quarter' ? 'end' : 'middle'}
            height={period === 'quarter' ? 80 : 60}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {hasTarget && (
            <ReferenceLine
              y={trendData.statistics.target}
              stroke="#82ca9d"
              strokeDasharray="5 5"
              label={{
                value: '目標',
                position: 'right',
                fill: '#82ca9d',
                fontSize: 12,
              }}
            />
          )}

          <Line
            type="monotone"
            dataKey="value"
            stroke="#8884d8"
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            name="実績"
          />
        </LineChart>
      </ResponsiveContainer>

      <div
        style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#e3f2fd',
          borderRadius: '8px',
          fontSize: '14px',
        }}
      >
        <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>分析結果</p>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          {hasTarget && (
            <li>
              {trendData.statistics.average >= trendData.statistics.target * 0.8
                ? '目標値に対して適切な摂取量です'
                : '目標値に対して不足しています'}
            </li>
          )}
          <li>
            標準偏差が{' '}
            {trendData.statistics.std_dev < trendData.statistics.average * 0.3
              ? '小さく、安定した摂取パターンです'
              : '大きく、摂取量にばらつきがあります'}
          </li>
        </ul>
      </div>
    </div>
  );
};

export default NutritionTrend;

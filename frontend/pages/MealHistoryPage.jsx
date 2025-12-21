/**
 * 食事履歴ページ
 *
 * 食事記録、栄養推移グラフ、傾向分析を統合したページコンポーネント
 */

import React, { useState, useEffect } from 'react';
import NutritionTrend from '../components/NutritionTrend';

const MealHistoryPage = () => {
  const [userId] = useState('user123'); // 実際はログイン情報から取得
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [dailyData, setDailyData] = useState(null);
  const [trends, setTrends] = useState(null);
  const [selectedNutrient, setSelectedNutrient] = useState('calories');
  const [activeTab, setActiveTab] = useState('daily');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const nutrients = [
    { key: 'calories', label: 'カロリー', unit: 'kcal' },
    { key: 'protein', label: 'タンパク質', unit: 'g' },
    { key: 'fat', label: '脂質', unit: 'g' },
    { key: 'carbohydrates', label: '炭水化物', unit: 'g' },
    { key: 'fiber', label: '食物繊維', unit: 'g' },
    { key: 'sodium', label: 'ナトリウム', unit: 'mg' },
  ];

  const mealTypeLabels = {
    breakfast: '朝食',
    lunch: '昼食',
    dinner: '夕食',
    snack: '間食',
  };

  useEffect(() => {
    if (activeTab === 'daily') {
      fetchDailyData();
    } else if (activeTab === 'trends') {
      fetchTrends();
    }
  }, [selectedDate, activeTab]);

  const fetchDailyData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/meal-history/daily/${selectedDate}?user_id=${userId}`
      );
      const result = await response.json();

      if (result.status === 'ok') {
        setDailyData(result.data);
      } else {
        setError(result.error || '日別データの取得に失敗しました');
      }
    } catch (err) {
      setError(`エラー: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrends = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/meal-history/trends?user_id=${userId}&days=30`
      );
      const result = await response.json();

      if (result.status === 'ok') {
        setTrends(result.data);
      } else {
        setError(result.error || '傾向分析データの取得に失敗しました');
      }
    } catch (err) {
      setError(`エラー: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const renderDailyView = () => {
    if (loading) {
      return <div style={{ textAlign: 'center', padding: '40px' }}>読み込み中...</div>;
    }

    if (error) {
      return (
        <div style={{ textAlign: 'center', padding: '40px', color: 'red' }}>
          {error}
        </div>
      );
    }

    if (!dailyData) {
      return null;
    }

    return (
      <div>
        <div style={{ marginBottom: '30px' }}>
          <h3>栄養摂取量サマリー</h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '15px',
            }}
          >
            {nutrients.map((nutrient) => (
              <div
                key={nutrient.key}
                style={{
                  padding: '15px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '8px',
                }}
              >
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {nutrient.label}
                </div>
                <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                  {dailyData.total_nutrition[nutrient.key]?.toFixed(1) || 0}
                </div>
                <div style={{ fontSize: '12px', color: '#999' }}>
                  {nutrient.unit}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3>食事記録 ({dailyData.meal_count}件)</h3>
          {dailyData.meals.length === 0 ? (
            <p style={{ color: '#999' }}>この日の食事記録はありません</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {dailyData.meals.map((meal) => (
                <div
                  key={meal.id}
                  style={{
                    padding: '15px',
                    backgroundColor: '#fff',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: '10px',
                    }}
                  >
                    <div>
                      <span
                        style={{
                          display: 'inline-block',
                          padding: '4px 12px',
                          backgroundColor: '#4CAF50',
                          color: 'white',
                          borderRadius: '4px',
                          fontSize: '12px',
                          marginRight: '10px',
                        }}
                      >
                        {mealTypeLabels[meal.meal_type]}
                      </span>
                      <span style={{ fontWeight: 'bold', fontSize: '16px' }}>
                        {meal.recipe_name}
                      </span>
                    </div>
                    <div style={{ fontSize: '14px', color: '#666' }}>
                      {new Date(meal.consumed_at).toLocaleTimeString('ja-JP', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>
                  <div
                    style={{
                      display: 'flex',
                      gap: '20px',
                      fontSize: '14px',
                      color: '#666',
                    }}
                  >
                    <span>
                      カロリー: {meal.nutrition.calories?.toFixed(0) || 0} kcal
                    </span>
                    <span>
                      タンパク質: {meal.nutrition.protein?.toFixed(1) || 0} g
                    </span>
                    <span>脂質: {meal.nutrition.fat?.toFixed(1) || 0} g</span>
                    <span>
                      炭水化物: {meal.nutrition.carbohydrates?.toFixed(1) || 0} g
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderTrendsView = () => {
    if (loading) {
      return <div style={{ textAlign: 'center', padding: '40px' }}>読み込み中...</div>;
    }

    if (error) {
      return (
        <div style={{ textAlign: 'center', padding: '40px', color: 'red' }}>
          {error}
        </div>
      );
    }

    if (!trends) {
      return null;
    }

    return (
      <div>
        <div style={{ marginBottom: '30px' }}>
          <h3>栄養バランス評価</h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '15px',
            }}
          >
            {Object.entries(trends.nutrition_balance).map(([nutrient, status]) => {
              const statusConfig = {
                excessive: { label: '過剰', color: '#ff9800' },
                adequate: { label: '適正', color: '#4CAF50' },
                insufficient: { label: '不足', color: '#f44336' },
              };

              const config = statusConfig[status];
              const nutrientLabel =
                nutrients.find((n) => n.key === nutrient)?.label || nutrient;

              return (
                <div
                  key={nutrient}
                  style={{
                    padding: '15px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '8px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div style={{ fontSize: '14px' }}>{nutrientLabel}</div>
                  <div
                    style={{
                      padding: '4px 12px',
                      backgroundColor: config.color,
                      color: 'white',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                    }}
                  >
                    {config.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <h3>よく食べる食材 Top 10</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {trends.top_ingredients.map((item, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '10px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '8px',
                }}
              >
                <div
                  style={{
                    width: '30px',
                    fontWeight: 'bold',
                    color: index < 3 ? '#4CAF50' : '#666',
                  }}
                >
                  {index + 1}
                </div>
                <div style={{ flex: 1 }}>{item.name}</div>
                <div style={{ fontWeight: 'bold' }}>{item.count}回</div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <h3>お気に入りレシピ Top 10</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {trends.favorite_recipes.map((item, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '10px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '8px',
                }}
              >
                <div
                  style={{
                    width: '30px',
                    fontWeight: 'bold',
                    color: index < 3 ? '#4CAF50' : '#666',
                  }}
                >
                  {index + 1}
                </div>
                <div style={{ flex: 1 }}>{item.name}</div>
                <div style={{ fontWeight: 'bold' }}>{item.count}回</div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3>食事タイプ別パターン</h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '15px',
            }}
          >
            {Object.entries(trends.meal_time_pattern).map(([type, count]) => (
              <div
                key={type}
                style={{
                  padding: '15px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '8px',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {mealTypeLabels[type]}
                </div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{count}回</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderNutritionTrendView = () => {
    return (
      <div>
        <div style={{ marginBottom: '20px' }}>
          <h3>栄養素を選択</h3>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {nutrients.map((nutrient) => (
              <button
                key={nutrient.key}
                onClick={() => setSelectedNutrient(nutrient.key)}
                style={{
                  padding: '8px 16px',
                  backgroundColor:
                    selectedNutrient === nutrient.key ? '#4CAF50' : '#e0e0e0',
                  color: selectedNutrient === nutrient.key ? 'white' : 'black',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                {nutrient.label}
              </button>
            ))}
          </div>
        </div>

        <NutritionTrend
          userId={userId}
          nutrient={selectedNutrient}
          initialPeriod="month"
        />
      </div>
    );
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1>食事履歴</h1>

      <div
        style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '30px',
          borderBottom: '2px solid #e0e0e0',
        }}
      >
        {[
          { key: 'daily', label: '日別' },
          { key: 'trends', label: '傾向分析' },
          { key: 'nutrition-trend', label: '栄養推移' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '12px 24px',
              backgroundColor: 'transparent',
              color: activeTab === tab.key ? '#4CAF50' : '#666',
              border: 'none',
              borderBottom:
                activeTab === tab.key ? '3px solid #4CAF50' : '3px solid transparent',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: activeTab === tab.key ? 'bold' : 'normal',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'daily' && (
        <div style={{ marginBottom: '20px' }}>
          <label style={{ marginRight: '10px', fontWeight: 'bold' }}>日付:</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            style={{
              padding: '8px',
              fontSize: '14px',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
          />
        </div>
      )}

      <div>
        {activeTab === 'daily' && renderDailyView()}
        {activeTab === 'trends' && renderTrendsView()}
        {activeTab === 'nutrition-trend' && renderNutritionTrendView()}
      </div>
    </div>
  );
};

export default MealHistoryPage;

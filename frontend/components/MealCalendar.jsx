/**
 * MealCalendar コンポーネント - 献立カレンダーUI
 *
 * 機能:
 * - カレンダービュー（週/月）
 * - ドラッグ&ドロップでレシピ配置
 * - 買い物リスト表示
 * - 栄養バランス表示
 */

import React, { useState, useEffect } from 'react';
import './MealCalendar.css';

const API_BASE = '/api/v1';

const MealCalendar = () => {
  const [viewMode, setViewMode] = useState('week'); // 'week' or 'month'
  const [currentDate, setCurrentDate] = useState(new Date());
  const [mealPlans, setMealPlans] = useState({});
  const [recipes, setRecipes] = useState([]);
  const [shoppingList, setShoppingList] = useState([]);
  const [nutrition, setNutrition] = useState(null);
  const [loading, setLoading] = useState(false);
  const [draggedRecipe, setDraggedRecipe] = useState(null);

  // 日付フォーマット
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // 週の開始日を取得（月曜日）
  const getWeekStart = (date) => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  };

  // 週の日付配列を生成
  const getWeekDates = (startDate) => {
    const dates = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  // 月の日付配列を生成
  const getMonthDates = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    const dates = [];
    for (let i = 1; i <= lastDay.getDate(); i++) {
      dates.push(new Date(year, month, i));
    }
    return dates;
  };

  // 献立計画を取得
  const fetchMealPlans = async () => {
    setLoading(true);
    try {
      let url;
      if (viewMode === 'week') {
        const weekStart = getWeekStart(currentDate);
        url = `${API_BASE}/calendar/week/${formatDate(weekStart)}`;
      } else {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth() + 1;
        url = `${API_BASE}/calendar/month/${year}/${month}`;
      }

      const response = await fetch(url);
      const result = await response.json();

      if (result.status === 'ok') {
        setMealPlans(result.data || {});
      }
    } catch (error) {
      console.error('Error fetching meal plans:', error);
    }
    setLoading(false);
  };

  // レシピ一覧を取得
  const fetchRecipes = async () => {
    try {
      const response = await fetch(`${API_BASE}/recipes`);
      const result = await response.json();

      if (result.status === 'ok') {
        setRecipes(result.data || []);
      }
    } catch (error) {
      console.error('Error fetching recipes:', error);
    }
  };

  // 買い物リストを取得
  const fetchShoppingList = async (startDate, endDate) => {
    try {
      const url = `${API_BASE}/calendar/shopping-list?start_date=${formatDate(startDate)}&end_date=${formatDate(endDate)}`;
      const response = await fetch(url);
      const result = await response.json();

      if (result.status === 'ok') {
        setShoppingList(result.data || []);
      }
    } catch (error) {
      console.error('Error fetching shopping list:', error);
    }
  };

  // 栄養バランスを取得
  const fetchNutrition = async (startDate, endDate) => {
    try {
      const url = `${API_BASE}/calendar/nutrition?start_date=${formatDate(startDate)}&end_date=${formatDate(endDate)}`;
      const response = await fetch(url);
      const result = await response.json();

      if (result.status === 'ok') {
        setNutrition(result.data);
      }
    } catch (error) {
      console.error('Error fetching nutrition:', error);
    }
  };

  // 献立計画を作成
  const createMealPlan = async (date, mealType, recipe) => {
    try {
      const response = await fetch(`${API_BASE}/calendar/plans`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          date: formatDate(date),
          meal_type: mealType,
          recipe_id: recipe.id,
          recipe_name: recipe.name,
          servings: 2,
        }),
      });

      const result = await response.json();

      if (result.status === 'ok') {
        await fetchMealPlans();
        updateWeeklyData();
      }
    } catch (error) {
      console.error('Error creating meal plan:', error);
    }
  };

  // 献立計画を削除
  const deleteMealPlan = async (planId) => {
    try {
      const response = await fetch(`${API_BASE}/calendar/plans/${planId}`, {
        method: 'DELETE',
      });

      const result = await response.json();

      if (result.status === 'ok') {
        await fetchMealPlans();
        updateWeeklyData();
      }
    } catch (error) {
      console.error('Error deleting meal plan:', error);
    }
  };

  // 週間データを更新
  const updateWeeklyData = () => {
    if (viewMode === 'week') {
      const weekStart = getWeekStart(currentDate);
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);

      fetchShoppingList(weekStart, weekEnd);
      fetchNutrition(weekStart, weekEnd);
    }
  };

  // 初期データ読み込み
  useEffect(() => {
    fetchMealPlans();
    fetchRecipes();
    updateWeeklyData();
  }, [currentDate, viewMode]);

  // ドラッグ開始
  const handleDragStart = (recipe) => {
    setDraggedRecipe(recipe);
  };

  // ドロップ
  const handleDrop = (date, mealType) => {
    if (draggedRecipe) {
      createMealPlan(date, mealType, draggedRecipe);
      setDraggedRecipe(null);
    }
  };

  // ドラッグオーバー
  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // 前週/前月へ移動
  const handlePrevious = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() - 7);
    } else {
      newDate.setMonth(newDate.getMonth() - 1);
    }
    setCurrentDate(newDate);
  };

  // 次週/次月へ移動
  const handleNext = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() + 7);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  // 今日へ移動
  const handleToday = () => {
    setCurrentDate(new Date());
  };

  // カレンダーレンダリング
  const renderCalendar = () => {
    const dates = viewMode === 'week' ? getWeekDates(getWeekStart(currentDate)) : getMonthDates(currentDate);
    const mealTypes = ['朝食', '昼食', '夕食'];

    return (
      <div className="calendar-grid">
        <div className="calendar-header">
          <div className="header-cell">日付</div>
          {mealTypes.map((type) => (
            <div key={type} className="header-cell">{type}</div>
          ))}
        </div>

        {dates.map((date) => {
          const dateKey = formatDate(date);
          const dayPlans = mealPlans[dateKey] || [];
          const isToday = formatDate(new Date()) === dateKey;

          return (
            <div key={dateKey} className={`calendar-row ${isToday ? 'today' : ''}`}>
              <div className="date-cell">
                <div className="date-label">
                  {date.getMonth() + 1}/{date.getDate()}
                  <span className="day-name">
                    {['日', '月', '火', '水', '木', '金', '土'][date.getDay()]}
                  </span>
                </div>
              </div>

              {mealTypes.map((mealType) => {
                const plan = dayPlans.find((p) => p.meal_type === mealType);

                return (
                  <div
                    key={`${dateKey}-${mealType}`}
                    className="meal-cell"
                    onDrop={() => handleDrop(date, mealType)}
                    onDragOver={handleDragOver}
                  >
                    {plan ? (
                      <div className="meal-plan-item">
                        <div className="recipe-name">{plan.recipe_name}</div>
                        <div className="servings">{plan.servings}人分</div>
                        <button
                          className="delete-btn"
                          onClick={() => deleteMealPlan(plan.id)}
                        >
                          ×
                        </button>
                      </div>
                    ) : (
                      <div className="empty-slot">ドロップしてレシピを追加</div>
                    )}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="meal-calendar">
      <div className="calendar-container">
        <div className="calendar-controls">
          <div className="view-controls">
            <button
              className={viewMode === 'week' ? 'active' : ''}
              onClick={() => setViewMode('week')}
            >
              週表示
            </button>
            <button
              className={viewMode === 'month' ? 'active' : ''}
              onClick={() => setViewMode('month')}
            >
              月表示
            </button>
          </div>

          <div className="navigation-controls">
            <button onClick={handlePrevious}>←</button>
            <button onClick={handleToday}>今日</button>
            <button onClick={handleNext}>→</button>
          </div>

          <div className="current-period">
            {viewMode === 'week'
              ? `${formatDate(getWeekStart(currentDate))} の週`
              : `${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月`}
          </div>
        </div>

        {loading ? (
          <div className="loading">読み込み中...</div>
        ) : (
          renderCalendar()
        )}
      </div>

      <div className="sidebar">
        <div className="recipe-list-section">
          <h3>レシピ一覧</h3>
          <div className="recipe-list">
            {recipes.map((recipe) => (
              <div
                key={recipe.id}
                className="recipe-item"
                draggable
                onDragStart={() => handleDragStart(recipe)}
              >
                {recipe.name}
              </div>
            ))}
          </div>
        </div>

        {viewMode === 'week' && (
          <>
            <div className="shopping-list-section">
              <h3>買い物リスト</h3>
              <div className="shopping-list">
                {shoppingList.length === 0 ? (
                  <p className="empty-message">献立を追加すると自動生成されます</p>
                ) : (
                  shoppingList.map((item, index) => (
                    <div key={index} className="shopping-item">
                      <span className="ingredient">{item.ingredient}</span>
                      <span className="quantity">
                        {item.total_quantity} {item.unit}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="nutrition-section">
              <h3>栄養バランス</h3>
              {nutrition ? (
                <div className="nutrition-info">
                  <div className="nutrition-item">
                    <span>総カロリー:</span>
                    <span>{nutrition.total_calories} kcal</span>
                  </div>
                  <div className="nutrition-item">
                    <span>1日平均:</span>
                    <span>{nutrition.avg_daily_calories} kcal</span>
                  </div>
                  <div className="nutrition-item">
                    <span>タンパク質:</span>
                    <span>{nutrition.total_protein} g</span>
                  </div>
                  <div className="nutrition-item">
                    <span>脂質:</span>
                    <span>{nutrition.total_fat} g</span>
                  </div>
                  <div className="nutrition-item">
                    <span>炭水化物:</span>
                    <span>{nutrition.total_carbs} g</span>
                  </div>
                </div>
              ) : (
                <p className="empty-message">データなし</p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default MealCalendar;

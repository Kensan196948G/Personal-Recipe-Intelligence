/**
 * レシピ自動生成コンポーネント
 */

import React, { useState, useEffect } from 'react';
import './RecipeGenerator.css';

const RecipeGenerator = () => {
  // 状態管理
  const [ingredients, setIngredients] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [category, setCategory] = useState('japanese');
  const [cookingTime, setCookingTime] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [useSeasonal, setUseSeasonal] = useState(true);
  const [generatedRecipe, setGeneratedRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [availableIngredients, setAvailableIngredients] = useState({});

  // 初期データ取得
  useEffect(() => {
    fetchAvailableIngredients();
  }, []);

  // 利用可能な食材リストを取得
  const fetchAvailableIngredients = async () => {
    try {
      const response = await fetch('/api/v1/ai/ingredients');
      const data = await response.json();
      if (data.status === 'ok') {
        setAvailableIngredients(data.data);
      }
    } catch (err) {
      console.error('食材リスト取得エラー:', err);
    }
  };

  // 食材追加
  const addIngredient = () => {
    if (inputValue.trim() && !ingredients.includes(inputValue.trim())) {
      setIngredients([...ingredients, inputValue.trim()]);
      setInputValue('');

      // 最初の食材が追加されたら提案を取得
      if (ingredients.length === 0) {
        fetchSuggestions(inputValue.trim());
      }
    }
  };

  // 食材削除
  const removeIngredient = (ingredient) => {
    setIngredients(ingredients.filter(i => i !== ingredient));
  };

  // Enter キーで食材追加
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      addIngredient();
    }
  };

  // 組み合わせ提案を取得
  const fetchSuggestions = async (mainIngredient) => {
    try {
      const response = await fetch(
        `/api/v1/ai/generate/suggestions?main_ingredient=${encodeURIComponent(mainIngredient)}&count=5`
      );
      const data = await response.json();
      if (data.status === 'ok') {
        setSuggestions(data.data);
      }
    } catch (err) {
      console.error('提案取得エラー:', err);
    }
  };

  // 提案から食材追加
  const addSuggestedIngredient = (ingredient) => {
    if (!ingredients.includes(ingredient)) {
      setIngredients([...ingredients, ingredient]);
    }
  };

  // レシピ生成
  const generateRecipe = async () => {
    if (ingredients.length === 0) {
      setError('食材を最低1つ追加してください');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/ai/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ingredients,
          category,
          cooking_time: cookingTime ? parseInt(cookingTime) : null,
          difficulty: difficulty || null,
          use_seasonal: useSeasonal,
        }),
      });

      const data = await response.json();

      if (data.status === 'ok') {
        setGeneratedRecipe(data.data);
        setSuggestions([]);
      } else {
        setError(data.error || 'レシピ生成に失敗しました');
      }
    } catch (err) {
      setError(`エラー: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // レシピ保存
  const saveRecipe = async () => {
    if (!generatedRecipe) return;

    try {
      const response = await fetch('/api/v1/recipes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(generatedRecipe),
      });

      const data = await response.json();

      if (data.status === 'ok') {
        alert('レシピを保存しました！');
        resetForm();
      } else {
        setError('保存に失敗しました');
      }
    } catch (err) {
      setError(`保存エラー: ${err.message}`);
    }
  };

  // レシピ改善
  const improveRecipe = async (focus) => {
    if (!generatedRecipe) return;

    setLoading(true);

    try {
      const response = await fetch('/api/v1/ai/generate/improve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipe: generatedRecipe,
          focus,
        }),
      });

      const data = await response.json();

      if (data.status === 'ok') {
        setGeneratedRecipe(data.data);
      } else {
        setError('改善に失敗しました');
      }
    } catch (err) {
      setError(`改善エラー: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // フォームリセット
  const resetForm = () => {
    setIngredients([]);
    setInputValue('');
    setCategory('japanese');
    setCookingTime('');
    setDifficulty('');
    setUseSeasonal(true);
    setGeneratedRecipe(null);
    setError(null);
    setSuggestions([]);
  };

  // カテゴリ名の表示
  const getCategoryName = (cat) => {
    const names = {
      japanese: '和食',
      western: '洋食',
      chinese: '中華',
    };
    return names[cat] || cat;
  };

  // 難易度の表示
  const getDifficultyName = (diff) => {
    const names = {
      easy: '簡単',
      medium: '普通',
      hard: '難しい',
    };
    return names[diff] || diff;
  };

  return (
    <div className="recipe-generator">
      <h2>レシピ自動生成</h2>

      {!generatedRecipe ? (
        <div className="generator-form">
          {/* 食材入力 */}
          <div className="form-section">
            <h3>使用する食材</h3>
            <div className="ingredient-input">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="食材を入力..."
              />
              <button onClick={addIngredient} className="btn-add">
                追加
              </button>
            </div>

            {/* 食材タグ */}
            <div className="ingredient-tags">
              {ingredients.map((ingredient, index) => (
                <span key={index} className="tag">
                  {ingredient}
                  <button onClick={() => removeIngredient(ingredient)}>×</button>
                </span>
              ))}
            </div>

            {/* 食材カテゴリ */}
            <div className="ingredient-categories">
              {Object.entries(availableIngredients).map(([category, items]) => (
                <div key={category} className="category-group">
                  <h4>{category}</h4>
                  <div className="category-items">
                    {items.map((item, idx) => (
                      <button
                        key={idx}
                        onClick={() => !ingredients.includes(item) && setIngredients([...ingredients, item])}
                        className={`btn-ingredient ${ingredients.includes(item) ? 'selected' : ''}`}
                      >
                        {item}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* 食材組み合わせ提案 */}
            {suggestions.length > 0 && (
              <div className="suggestions">
                <h4>おすすめの組み合わせ</h4>
                <div className="suggestion-list">
                  {suggestions.map((suggestion, idx) => (
                    <div key={idx} className="suggestion-item">
                      <span className="suggestion-text">
                        {suggestion.main} + {suggestion.sub}
                        {suggestion.seasonal && <span className="badge-seasonal">旬</span>}
                      </span>
                      <button
                        onClick={() => addSuggestedIngredient(suggestion.sub)}
                        className="btn-small"
                      >
                        追加
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* オプション設定 */}
          <div className="form-section">
            <h3>オプション設定</h3>

            <div className="form-group">
              <label>料理カテゴリ</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="japanese">和食</option>
                <option value="western">洋食</option>
                <option value="chinese">中華</option>
              </select>
            </div>

            <div className="form-group">
              <label>調理時間（分）</label>
              <input
                type="number"
                value={cookingTime}
                onChange={(e) => setCookingTime(e.target.value)}
                placeholder="指定なし"
                min="5"
                max="120"
              />
            </div>

            <div className="form-group">
              <label>難易度</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                <option value="">指定なし</option>
                <option value="easy">簡単</option>
                <option value="medium">普通</option>
                <option value="hard">難しい</option>
              </select>
            </div>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={useSeasonal}
                  onChange={(e) => setUseSeasonal(e.target.checked)}
                />
                季節の食材を活用する
              </label>
            </div>
          </div>

          {/* エラー表示 */}
          {error && <div className="error-message">{error}</div>}

          {/* 生成ボタン */}
          <div className="form-actions">
            <button onClick={generateRecipe} disabled={loading} className="btn-primary">
              {loading ? '生成中...' : 'レシピを生成'}
            </button>
            <button onClick={resetForm} className="btn-secondary">
              リセット
            </button>
          </div>
        </div>
      ) : (
        <div className="recipe-result">
          {/* 生成されたレシピ */}
          <div className="recipe-header">
            <h3>{generatedRecipe.name}</h3>
            <div className="recipe-meta">
              <span className="badge">{getCategoryName(generatedRecipe.category)}</span>
              <span className="badge">{getDifficultyName(generatedRecipe.difficulty)}</span>
              <span className="time">{generatedRecipe.cooking_time}分</span>
            </div>
          </div>

          {/* 材料 */}
          <div className="recipe-section">
            <h4>材料（{generatedRecipe.servings}人分）</h4>
            <ul className="ingredient-list">
              {generatedRecipe.ingredients.map((ingredient, idx) => (
                <li key={idx}>
                  {ingredient.name}: {ingredient.amount} {ingredient.unit}
                </li>
              ))}
            </ul>
          </div>

          {/* 手順 */}
          <div className="recipe-section">
            <h4>作り方</h4>
            <ol className="steps-list">
              {generatedRecipe.steps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ol>
          </div>

          {/* 栄養情報 */}
          {generatedRecipe.nutrition && (
            <div className="recipe-section">
              <h4>栄養バランス</h4>
              <div className="nutrition-info">
                <div className="nutrition-badges">
                  {generatedRecipe.nutrition.has_protein && (
                    <span className="badge-nutrition">たんぱく質</span>
                  )}
                  {generatedRecipe.nutrition.has_vegetable && (
                    <span className="badge-nutrition">野菜</span>
                  )}
                  {generatedRecipe.nutrition.has_carbohydrate && (
                    <span className="badge-nutrition">炭水化物</span>
                  )}
                </div>
                <div className="balance-score">
                  バランススコア: {generatedRecipe.nutrition.balance_score}%
                </div>
                <div className="recommendation">
                  {generatedRecipe.nutrition.recommendation}
                </div>
              </div>
            </div>
          )}

          {/* アクション */}
          <div className="recipe-actions">
            <button onClick={saveRecipe} className="btn-primary">
              保存
            </button>
            <button onClick={generateRecipe} className="btn-secondary">
              再生成
            </button>
            <button onClick={resetForm} className="btn-secondary">
              新しく作成
            </button>
          </div>

          {/* 改善オプション */}
          <div className="improvement-section">
            <h4>レシピを改善</h4>
            <div className="improvement-buttons">
              <button onClick={() => improveRecipe('taste')} className="btn-improve">
                味を改善
              </button>
              <button onClick={() => improveRecipe('health')} className="btn-improve">
                ヘルシーに
              </button>
              <button onClick={() => improveRecipe('speed')} className="btn-improve">
                時短に
              </button>
              <button onClick={() => improveRecipe('cost')} className="btn-improve">
                節約に
              </button>
            </div>
          </div>

          {/* エラー表示 */}
          {error && <div className="error-message">{error}</div>}
        </div>
      )}
    </div>
  );
};

export default RecipeGenerator;

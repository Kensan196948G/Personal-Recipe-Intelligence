/**
 * SmartSearch Component
 * 自然言語検索コンポーネント
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import './SmartSearch.css';

const SmartSearch = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [parsedQuery, setParsedQuery] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  const API_BASE = '/api/v1';

  // サジェスト取得
  const fetchSuggestions = useCallback(async (q) => {
    if (q.length < 1) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE}/ai/search/suggestions?q=${encodeURIComponent(q)}&limit=10`
      );
      const data = await response.json();
      setSuggestions(data.suggestions || []);
      setShowSuggestions(true);
    } catch (err) {
      console.error('サジェスト取得エラー:', err);
    }
  }, []);

  // クエリ解析（プレビュー）
  const parseQuery = useCallback(async (q) => {
    if (!q.trim()) {
      setParsedQuery(null);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/ai/search/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      });
      const data = await response.json();
      setParsedQuery(data);
    } catch (err) {
      console.error('クエリ解析エラー:', err);
      setParsedQuery(null);
    }
  }, []);

  // 検索実行
  const executeSearch = useCallback(async (q) => {
    if (!q.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/ai/search/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, limit: 20 })
      });

      if (!response.ok) {
        throw new Error('検索に失敗しました');
      }

      const data = await response.json();
      setSearchResults(data.results || []);
      setParsedQuery(data.parsed);
      setShowSuggestions(false);
    } catch (err) {
      console.error('検索エラー:', err);
      setError(err.message);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // 履歴取得
  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/ai/search/history?limit=20`);
      const data = await response.json();
      setHistory(data.history || []);
    } catch (err) {
      console.error('履歴取得エラー:', err);
    }
  }, []);

  // 入力変更ハンドラ
  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);

    // サジェスト取得（デバウンス）
    const timeoutId = setTimeout(() => {
      fetchSuggestions(value);
    }, 300);

    return () => clearTimeout(timeoutId);
  };

  // 検索送信ハンドラ
  const handleSubmit = (e) => {
    e.preventDefault();
    executeSearch(query);
  };

  // サジェスト選択ハンドラ
  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    executeSearch(suggestion);
  };

  // 履歴選択ハンドラ
  const handleHistoryClick = (historyQuery) => {
    setQuery(historyQuery);
    setShowHistory(false);
    executeSearch(historyQuery);
  };

  // クエリ解析プレビュー（デバウンス）
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      parseQuery(query);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [query, parseQuery]);

  // 外側クリックでサジェストを閉じる
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(e.target) &&
        !inputRef.current.contains(e.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 履歴読み込み
  useEffect(() => {
    if (showHistory) {
      fetchHistory();
    }
  }, [showHistory, fetchHistory]);

  return (
    <div className="smart-search">
      <div className="search-header">
        <h2>スマート検索</h2>
        <p className="search-description">
          日本語で自然に検索できます（例：「辛くない簡単な鶏肉料理」）
        </p>
      </div>

      {/* 検索フォーム */}
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="search-input-container">
          <input
            ref={inputRef}
            type="text"
            className="search-input"
            placeholder="料理を検索..."
            value={query}
            onChange={handleInputChange}
            onFocus={() => query && setShowSuggestions(true)}
          />
          <button
            type="button"
            className="history-button"
            onClick={() => setShowHistory(!showHistory)}
            title="検索履歴"
          >
            📜
          </button>
          <button
            type="submit"
            className="search-button"
            disabled={isSearching || !query.trim()}
          >
            {isSearching ? '検索中...' : '検索'}
          </button>
        </div>

        {/* サジェスト */}
        {showSuggestions && suggestions.length > 0 && (
          <div ref={suggestionsRef} className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="suggestion-item"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                <span className="suggestion-icon">🔍</span>
                {suggestion}
              </div>
            ))}
          </div>
        )}

        {/* 履歴 */}
        {showHistory && (
          <div className="history-panel">
            <div className="history-header">
              <h3>検索履歴</h3>
              <button
                type="button"
                className="close-button"
                onClick={() => setShowHistory(false)}
              >
                ×
              </button>
            </div>
            {history.length === 0 ? (
              <p className="no-history">履歴がありません</p>
            ) : (
              <div className="history-list">
                {history.map((item, index) => (
                  <div
                    key={index}
                    className="history-item"
                    onClick={() => handleHistoryClick(item.query)}
                  >
                    <span className="history-query">{item.query}</span>
                    <span className="history-time">
                      {new Date(item.timestamp).toLocaleString('ja-JP')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </form>

      {/* クエリ解析結果 */}
      {parsedQuery && (
        <div className="parsed-query">
          <h3>解析結果</h3>
          <div className="parsed-details">
            {parsedQuery.explanation && (
              <p className="explanation">{parsedQuery.explanation}</p>
            )}
            <div className="parsed-tags">
              {parsedQuery.ingredients_include.length > 0 && (
                <div className="tag-group">
                  <span className="tag-label">食材:</span>
                  {parsedQuery.ingredients_include.map((ing, idx) => (
                    <span key={idx} className="tag tag-ingredient">
                      {ing}
                    </span>
                  ))}
                </div>
              )}
              {parsedQuery.ingredients_exclude.length > 0 && (
                <div className="tag-group">
                  <span className="tag-label">除外:</span>
                  {parsedQuery.ingredients_exclude.map((ing, idx) => (
                    <span key={idx} className="tag tag-exclude">
                      {ing}
                    </span>
                  ))}
                </div>
              )}
              {parsedQuery.cooking_methods.length > 0 && (
                <div className="tag-group">
                  <span className="tag-label">調理法:</span>
                  {parsedQuery.cooking_methods.map((method, idx) => (
                    <span key={idx} className="tag tag-method">
                      {method}
                    </span>
                  ))}
                </div>
              )}
              {parsedQuery.categories.length > 0 && (
                <div className="tag-group">
                  <span className="tag-label">カテゴリ:</span>
                  {parsedQuery.categories.map((cat, idx) => (
                    <span key={idx} className="tag tag-category">
                      {cat}
                    </span>
                  ))}
                </div>
              )}
              {parsedQuery.adjectives.length > 0 && (
                <div className="tag-group">
                  <span className="tag-label">特徴:</span>
                  {parsedQuery.adjectives.map((adj, idx) => (
                    <span key={idx} className="tag tag-adjective">
                      {adj}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* エラー表示 */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* 検索結果 */}
      <div className="search-results">
        {isSearching ? (
          <div className="loading">検索中...</div>
        ) : searchResults.length === 0 && query ? (
          <div className="no-results">
            <p>「{query}」に一致するレシピが見つかりませんでした</p>
          </div>
        ) : (
          <div className="results-list">
            {searchResults.map((recipe) => (
              <div key={recipe.id} className="result-card">
                <h3 className="result-title">{recipe.title}</h3>
                {recipe.description && (
                  <p className="result-description">{recipe.description}</p>
                )}
                {recipe.ingredients && recipe.ingredients.length > 0 && (
                  <div className="result-ingredients">
                    <strong>材料:</strong>{' '}
                    {recipe.ingredients.slice(0, 5).join('、')}
                    {recipe.ingredients.length > 5 && '...'}
                  </div>
                )}
                {recipe.tags && recipe.tags.length > 0 && (
                  <div className="result-tags">
                    {recipe.tags.map((tag, idx) => (
                      <span key={idx} className="result-tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                <div className="result-meta">
                  {recipe.cooking_time && (
                    <span className="meta-item">⏱️ {recipe.cooking_time}</span>
                  )}
                  {recipe.servings && (
                    <span className="meta-item">👥 {recipe.servings}人前</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SmartSearch;

/**
 * 特売情報UIコンポーネント
 *
 * スーパーの特売情報を表示し、フィルタリングやレシピ連動機能を提供する。
 */

import React, { useState, useEffect, useMemo } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * カテゴリ定義
 */
const CATEGORIES = {
  all: '全て',
  vegetable: '野菜',
  fruit: '果物',
  meat: '肉類',
  fish: '魚介類',
  dairy: '乳製品',
  grain: '穀物',
  seasoning: '調味料',
  other: 'その他',
};

/**
 * 特売商品カード
 */
const SaleItemCard = ({ item, onSelect }) => {
  const discountBadge = item.discount_rate ? (
    <span className="discount-badge" style={styles.discountBadge}>
      {item.discount_rate}% OFF
    </span>
  ) : null;

  const originalPrice = item.original_price ? (
    <span className="original-price" style={styles.originalPrice}>
      ¥{item.original_price.toLocaleString()}
    </span>
  ) : null;

  const validUntil = new Date(item.valid_until).toLocaleDateString('ja-JP', {
    month: 'short',
    day: 'numeric',
  });

  return (
    <div className="sale-item-card" style={styles.card} onClick={() => onSelect(item)}>
      <div className="card-header" style={styles.cardHeader}>
        <h3 style={styles.productName}>{item.product_name}</h3>
        {discountBadge}
      </div>

      <div className="card-body" style={styles.cardBody}>
        <div className="price-info" style={styles.priceInfo}>
          {originalPrice}
          <span className="current-price" style={styles.currentPrice}>
            ¥{item.price.toLocaleString()}
          </span>
          <span className="unit" style={styles.unit}>/ {item.unit}</span>
        </div>

        <div className="meta-info" style={styles.metaInfo}>
          <span className="store-name" style={styles.storeName}>
            {item.store_name}
          </span>
          <span className="category" style={styles.category}>
            {CATEGORIES[item.category] || item.category}
          </span>
        </div>

        <div className="valid-until" style={styles.validUntil}>
          {validUntil}まで有効
        </div>
      </div>
    </div>
  );
};

/**
 * フィルターバー
 */
const FilterBar = ({ filters, onFilterChange, stores, onClearFilters }) => {
  return (
    <div className="filter-bar" style={styles.filterBar}>
      <div className="filter-group" style={styles.filterGroup}>
        <label style={styles.filterLabel}>店舗:</label>
        <select
          value={filters.store}
          onChange={(e) => onFilterChange('store', e.target.value)}
          style={styles.select}
        >
          <option value="">全ての店舗</option>
          {stores.map((store) => (
            <option key={store} value={store}>
              {store}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group" style={styles.filterGroup}>
        <label style={styles.filterLabel}>カテゴリ:</label>
        <select
          value={filters.category}
          onChange={(e) => onFilterChange('category', e.target.value)}
          style={styles.select}
        >
          {Object.entries(CATEGORIES).map(([key, label]) => (
            <option key={key} value={key === 'all' ? '' : key}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group" style={styles.filterGroup}>
        <label style={styles.filterLabel}>最小割引率:</label>
        <input
          type="number"
          value={filters.minDiscount}
          onChange={(e) => onFilterChange('minDiscount', e.target.value)}
          placeholder="0"
          min="0"
          max="100"
          style={styles.input}
        />
        <span style={styles.unit}>%</span>
      </div>

      <button onClick={onClearFilters} style={styles.clearButton}>
        フィルタクリア
      </button>
    </div>
  );
};

/**
 * 統計情報パネル
 */
const StatisticsPanel = ({ statistics }) => {
  if (!statistics) return null;

  return (
    <div className="statistics-panel" style={styles.statisticsPanel}>
      <div className="stat-item" style={styles.statItem}>
        <span className="stat-label">有効な特売:</span>
        <span className="stat-value">{statistics.total_active_sales}件</span>
      </div>
      <div className="stat-item" style={styles.statItem}>
        <span className="stat-label">平均割引率:</span>
        <span className="stat-value">{statistics.average_discount_rate}%</span>
      </div>
    </div>
  );
};

/**
 * レシピ推薦パネル
 */
const RecipeRecommendations = ({ recommendations, onRecipeSelect }) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div style={styles.emptyState}>
        特売食材を使ったレシピはありません
      </div>
    );
  }

  return (
    <div className="recipe-recommendations" style={styles.recommendationsContainer}>
      <h3 style={styles.recommendationsTitle}>特売食材で作れるレシピ</h3>
      <div className="recipe-list" style={styles.recipeList}>
        {recommendations.map((recipe, index) => (
          <div
            key={index}
            className="recipe-card"
            style={styles.recipeCard}
            onClick={() => onRecipeSelect(recipe)}
          >
            <h4 style={styles.recipeName}>{recipe.recipe_name}</h4>
            <div className="recipe-meta" style={styles.recipeMeta}>
              <span className="matching-count" style={styles.matchingCount}>
                {recipe.matching_ingredients.length}つの材料が特売中
              </span>
              <span className="estimated-cost" style={styles.estimatedCost}>
                約¥{recipe.estimated_cost.toLocaleString()}
              </span>
            </div>
            <div className="matching-ingredients" style={styles.matchingIngredients}>
              {recipe.matching_ingredients.join(', ')}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * メインコンポーネント
 */
const SaleInfo = () => {
  const [sales, setSales] = useState([]);
  const [filters, setFilters] = useState({
    store: '',
    category: '',
    minDiscount: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [showRecommendations, setShowRecommendations] = useState(false);

  /**
   * 特売情報を取得
   */
  const fetchSales = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (filters.store) params.append('store_name', filters.store);
      if (filters.category) params.append('category', filters.category);
      if (filters.minDiscount) params.append('min_discount', filters.minDiscount);

      const response = await fetch(`${API_BASE_URL}/api/v1/sales?${params}`);
      const data = await response.json();

      if (data.status === 'ok') {
        setSales(data.data);
      } else {
        setError(data.error || '特売情報の取得に失敗しました');
      }
    } catch (err) {
      setError(`エラー: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 統計情報を取得
   */
  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/sales/statistics`);
      const data = await response.json();

      if (data.status === 'ok') {
        setStatistics(data.data);
      }
    } catch (err) {
      console.error('統計情報の取得に失敗:', err);
    }
  };

  /**
   * レシピ推薦を取得
   */
  const fetchRecommendations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/sales/recommendations`);
      const data = await response.json();

      if (data.status === 'ok') {
        setRecommendations(data.data);
      }
    } catch (err) {
      console.error('レシピ推薦の取得に失敗:', err);
    }
  };

  /**
   * 初期ロード
   */
  useEffect(() => {
    fetchSales();
    fetchStatistics();
    fetchRecommendations();
  }, []);

  /**
   * フィルタ変更時
   */
  useEffect(() => {
    fetchSales();
  }, [filters]);

  /**
   * 店舗リストを抽出
   */
  const stores = useMemo(() => {
    const storeSet = new Set(sales.map((sale) => sale.store_name));
    return Array.from(storeSet).sort();
  }, [sales]);

  /**
   * フィルタ変更ハンドラ
   */
  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  /**
   * フィルタクリア
   */
  const handleClearFilters = () => {
    setFilters({
      store: '',
      category: '',
      minDiscount: '',
    });
  };

  /**
   * 商品選択ハンドラ
   */
  const handleSelectItem = (item) => {
    console.log('Selected item:', item);
    // TODO: 詳細モーダル表示など
  };

  /**
   * レシピ選択ハンドラ
   */
  const handleRecipeSelect = (recipe) => {
    console.log('Selected recipe:', recipe);
    // TODO: レシピ詳細画面へ遷移
  };

  return (
    <div className="sale-info-container" style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>特売情報</h1>
        <button
          onClick={() => setShowRecommendations(!showRecommendations)}
          style={styles.toggleButton}
        >
          {showRecommendations ? '特売一覧を表示' : 'レシピ推薦を表示'}
        </button>
      </header>

      <StatisticsPanel statistics={statistics} />

      {!showRecommendations && (
        <>
          <FilterBar
            filters={filters}
            onFilterChange={handleFilterChange}
            stores={stores}
            onClearFilters={handleClearFilters}
          />

          {loading && <div style={styles.loading}>読み込み中...</div>}
          {error && <div style={styles.error}>{error}</div>}

          <div className="sales-grid" style={styles.grid}>
            {sales.length === 0 && !loading && (
              <div style={styles.emptyState}>特売情報がありません</div>
            )}
            {sales.map((item) => (
              <SaleItemCard key={item.id} item={item} onSelect={handleSelectItem} />
            ))}
          </div>
        </>
      )}

      {showRecommendations && (
        <RecipeRecommendations
          recommendations={recommendations}
          onRecipeSelect={handleRecipeSelect}
        />
      )}
    </div>
  );
};

/**
 * スタイル定義
 */
const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0,
  },
  toggleButton: {
    padding: '10px 20px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  statisticsPanel: {
    display: 'flex',
    gap: '20px',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  statItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  filterBar: {
    display: 'flex',
    gap: '15px',
    alignItems: 'flex-end',
    padding: '15px',
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    marginBottom: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  filterGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  filterLabel: {
    fontSize: '12px',
    fontWeight: 'bold',
    color: '#666',
  },
  select: {
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '14px',
  },
  input: {
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '14px',
    width: '80px',
  },
  clearButton: {
    padding: '8px 16px',
    backgroundColor: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '20px',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    padding: '15px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '10px',
  },
  productName: {
    fontSize: '16px',
    fontWeight: 'bold',
    margin: 0,
    flex: 1,
  },
  discountBadge: {
    backgroundColor: '#dc3545',
    color: 'white',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 'bold',
  },
  cardBody: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  priceInfo: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '8px',
  },
  originalPrice: {
    textDecoration: 'line-through',
    color: '#999',
    fontSize: '14px',
  },
  currentPrice: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#dc3545',
  },
  unit: {
    fontSize: '14px',
    color: '#666',
  },
  metaInfo: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
  },
  storeName: {
    color: '#007bff',
    fontWeight: 'bold',
  },
  category: {
    color: '#666',
  },
  validUntil: {
    fontSize: '12px',
    color: '#666',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '16px',
    color: '#666',
  },
  error: {
    padding: '15px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    borderRadius: '4px',
    marginBottom: '20px',
  },
  emptyState: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '16px',
    color: '#666',
  },
  recommendationsContainer: {
    padding: '20px',
  },
  recommendationsTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '15px',
  },
  recipeList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  recipeCard: {
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    padding: '15px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    cursor: 'pointer',
  },
  recipeName: {
    fontSize: '18px',
    fontWeight: 'bold',
    margin: '0 0 10px 0',
  },
  recipeMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '10px',
  },
  matchingCount: {
    color: '#28a745',
    fontSize: '14px',
    fontWeight: 'bold',
  },
  estimatedCost: {
    color: '#666',
    fontSize: '14px',
  },
  matchingIngredients: {
    fontSize: '14px',
    color: '#666',
  },
};

export default SaleInfo;

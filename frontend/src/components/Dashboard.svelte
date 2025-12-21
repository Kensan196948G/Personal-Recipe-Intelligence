<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import StatCard from './StatCard.svelte';
  import { dashboardApi } from '../services/api.js';

  const dispatch = createEventDispatcher();

  let stats = null;
  let loading = true;
  let error = null;

  onMount(async () => {
    await loadStats();
  });

  async function loadStats() {
    loading = true;
    error = null;
    try {
      const response = await dashboardApi.getStats();
      if (response.status === 'ok') {
        stats = response.data;
      }
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function handleViewRecipe(recipe) {
    dispatch('viewRecipe', recipe);
  }

  function getSourceLabel(type) {
    const labels = {
      'manual': '手動入力',
      'web': 'Web取得',
      'ocr': 'OCR',
      'api': 'API収集',
    };
    return labels[type] || type;
  }
</script>

<div class="dashboard">
  <div class="dashboard-header">
    <h2>ダッシュボード</h2>
    <button class="refresh-btn" on:click={loadStats} disabled={loading}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
      </svg>
      更新
    </button>
  </div>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <span>読み込み中...</span>
    </div>
  {:else if error}
    <div class="error">
      <p>エラー: {error}</p>
      <button on:click={loadStats}>再試行</button>
    </div>
  {:else if stats}
    <div class="stats-grid">
      <StatCard
        icon="📚"
        title="総レシピ数"
        value={stats.total_recipes}
        color="blue"
      />
      <StatCard
        icon="📅"
        title="今週追加"
        value={stats.recipes_this_week}
        subtitle="過去7日間"
        color="green"
      />
      <StatCard
        icon="⭐"
        title="お気に入り"
        value={stats.favorites_count}
        color="orange"
      />
      <StatCard
        icon="🏷️"
        title="タグ数"
        value={stats.tags_count}
        color="purple"
      />
    </div>

    {#if stats.source_stats && Object.keys(stats.source_stats).length > 0}
      <div class="section">
        <h3>ソース別レシピ</h3>
        <div class="source-chart">
          {#each Object.entries(stats.source_stats) as [type, count]}
            <div class="source-bar">
              <div class="source-label">{getSourceLabel(type)}</div>
              <div class="source-progress">
                <div
                  class="source-fill source-fill--{type}"
                  style="width: {(count / stats.total_recipes) * 100}%"
                ></div>
              </div>
              <div class="source-count">{count}</div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    {#if stats.recent_recipes && stats.recent_recipes.length > 0}
      <div class="section">
        <h3>最近追加されたレシピ</h3>
        <div class="recent-list">
          {#each stats.recent_recipes as recipe}
            <button class="recent-item" on:click={() => handleViewRecipe(recipe)}>
              <span class="recent-title">{recipe.title}</span>
              <span class="recent-source">{getSourceLabel(recipe.source_type)}</span>
            </button>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .dashboard {
    padding: 0;
  }

  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .dashboard-header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #1a1a2e;
  }

  .refresh-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 0.875rem;
    color: #666;
    transition: all 0.2s;
  }

  .refresh-btn:hover:not(:disabled) {
    background: #f5f5f5;
    color: #333;
  }

  .refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .section {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    margin-bottom: 1.5rem;
  }

  .section h3 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    color: #333;
    font-weight: 600;
  }

  .source-chart {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .source-bar {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .source-label {
    width: 80px;
    font-size: 0.875rem;
    color: #666;
  }

  .source-progress {
    flex: 1;
    height: 24px;
    background: #f0f0f0;
    border-radius: 12px;
    overflow: hidden;
  }

  .source-fill {
    height: 100%;
    border-radius: 12px;
    min-width: 8px;
    transition: width 0.5s ease;
  }

  .source-fill--manual { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
  .source-fill--web { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
  .source-fill--ocr { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
  .source-fill--api { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }

  .source-count {
    width: 40px;
    text-align: right;
    font-size: 0.875rem;
    font-weight: 600;
    color: #333;
  }

  .recent-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .recent-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background: #f8f9fa;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    width: 100%;
  }

  .recent-item:hover {
    background: #e9ecef;
  }

  .recent-title {
    font-size: 0.9rem;
    color: #333;
    font-weight: 500;
  }

  .recent-source {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    background: #e3f2fd;
    color: #1976d2;
    border-radius: 4px;
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    color: #666;
    gap: 1rem;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f0f0f0;
    border-top-color: #0077aa;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error {
    text-align: center;
    padding: 2rem;
    background: #fff5f5;
    border-radius: 12px;
    color: #c00;
  }

  .error button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    border: 1px solid #c00;
    border-radius: 6px;
    background: white;
    color: #c00;
    cursor: pointer;
  }

  .error button:hover {
    background: #fff5f5;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 0.75rem;
    }

    .section {
      padding: 1rem;
    }

    .source-bar {
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .source-label {
      width: 100%;
      margin-bottom: -0.25rem;
    }

    .source-progress {
      flex: 1;
    }

    .recent-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .dashboard-header h2 {
      font-size: 1.25rem;
    }
  }
</style>

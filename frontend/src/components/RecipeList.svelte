<script>
  import { createEventDispatcher } from 'svelte';
  import {
    recipes,
    loading,
    error,
    pagination,
    fetchRecipes,
    deleteRecipe,
    searchRecipes,
  } from '../stores/recipes.js';
  import { recipeApi } from '../services/api.js';
  import { onMount } from 'svelte';
  import ConfirmModal from './ConfirmModal.svelte';
  import RecipeCard from './RecipeCard.svelte';

  const dispatch = createEventDispatcher();

  let searchInput = '';
  let showDeleteModal = false;
  let deleteTarget = { id: null, title: '' };
  let searchLabelId = 'search-label';

  // View mode and sorting
  let viewMode = 'grid'; // 'grid' or 'list'
  let sortBy = 'newest'; // 'newest', 'oldest', 'name', 'rating'
  let filterSource = ''; // '', 'manual', 'web', 'ocr', 'api'

  onMount(() => {
    fetchRecipes();
  });

  async function handleSearch() {
    await searchRecipes(searchInput);
  }

  function handleDelete(event) {
    const { id, title } = event.detail;
    deleteTarget = { id, title };
    showDeleteModal = true;
  }

  async function confirmDelete() {
    if (deleteTarget.id) {
      await deleteRecipe(deleteTarget.id);
      deleteTarget = { id: null, title: '' };
    }
  }

  function handleView(event) {
    dispatch('view', event.detail);
  }

  function handleEdit(event) {
    dispatch('edit', event.detail);
  }

  async function handleFavorite(event) {
    const recipe = event.detail;
    try {
      await recipeApi.update(recipe.id, {
        ...recipe,
        is_favorite: !recipe.is_favorite
      });
      await fetchRecipes();
    } catch (e) {
      console.error('Failed to toggle favorite:', e);
    }
  }

  function handleCreate() {
    dispatch('create');
  }

  function handleImport() {
    dispatch('import');
  }

  function handleCollector() {
    dispatch('collector');
  }

  async function handleExportMarkdown() {
    try {
      // 色なし・アイコン必須
      const response = await fetch('/api/v1/export/recipes-markdown?use_colors=false&use_icons=true');
      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `recipes_${new Date().toISOString().slice(0,10)}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      console.error('Export failed:', e);
      alert('エクスポートに失敗しました');
    }
  }

  async function handleExportHTML() {
    try {
      const response = await fetch('/api/v1/export/recipes-html?use_colors=true&use_icons=true');
      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `recipes_${new Date().toISOString().slice(0,10)}.html`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      console.error('Export failed:', e);
      alert('エクスポートに失敗しました');
    }
  }

  function setViewMode(mode) {
    viewMode = mode;
  }

  // Sort recipes
  $: sortedRecipes = [...($recipes || [])].sort((a, b) => {
    switch (sortBy) {
      case 'oldest':
        return new Date(a.created_at) - new Date(b.created_at);
      case 'name':
        return a.title.localeCompare(b.title, 'ja');
      case 'rating':
        return (b.rating || 0) - (a.rating || 0);
      case 'newest':
      default:
        return new Date(b.created_at) - new Date(a.created_at);
    }
  });

  // Filter by source
  $: filteredRecipes = filterSource
    ? sortedRecipes.filter(r => r.source_type === filterSource)
    : sortedRecipes;
</script>

<div class="recipe-list">
  <div class="toolbar">
    <div class="search-box">
      <label id={searchLabelId} class="visually-hidden">レシピを検索</label>
      <div class="search-input-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input
          type="text"
          placeholder="レシピを検索..."
          bind:value={searchInput}
          on:keydown={(e) => e.key === 'Enter' && handleSearch()}
          aria-labelledby={searchLabelId}
        />
        {#if searchInput}
          <button class="clear-btn" on:click={() => { searchInput = ''; handleSearch(); }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        {/if}
      </div>
      <button class="search-btn" on:click={handleSearch} aria-label="レシピを検索">検索</button>
    </div>
  </div>

  <div class="filter-bar">
    <div class="filter-left">
      <select bind:value={sortBy} class="filter-select">
        <option value="newest">新しい順</option>
        <option value="oldest">古い順</option>
        <option value="name">名前順</option>
        <option value="rating">評価順</option>
      </select>

      <select bind:value={filterSource} class="filter-select">
        <option value="">すべてのソース</option>
        <option value="manual">手動入力</option>
        <option value="web">Web取得</option>
        <option value="ocr">OCR</option>
        <option value="api">API収集</option>
      </select>

      <span class="result-count">{filteredRecipes.length}件</span>
    </div>

    <div class="filter-right">
      <div class="view-toggle">
        <button
          class="toggle-btn"
          class:active={viewMode === 'grid'}
          on:click={() => setViewMode('grid')}
          aria-label="グリッド表示"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
          </svg>
        </button>
        <button
          class="toggle-btn"
          class:active={viewMode === 'list'}
          on:click={() => setViewMode('list')}
          aria-label="リスト表示"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="8" y1="6" x2="21" y2="6"/>
            <line x1="8" y1="12" x2="21" y2="12"/>
            <line x1="8" y1="18" x2="21" y2="18"/>
            <line x1="3" y1="6" x2="3.01" y2="6"/>
            <line x1="3" y1="12" x2="3.01" y2="12"/>
            <line x1="3" y1="18" x2="3.01" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="action-buttons">
        <button class="btn-export-html" on:click={handleExportHTML} title="色付きHTML形式でエクスポート">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          HTML
        </button>
        <button class="btn-export-md" on:click={handleExportMarkdown} title="アイコン付きMarkdown形式でエクスポート">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          MD
        </button>
        <button class="btn-collector" on:click={handleCollector}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="12" cy="12" r="10"/>
            <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
          </svg>
          海外収集
        </button>
        <button class="btn-secondary" on:click={handleImport}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          CSV
        </button>
        <button class="btn-primary" on:click={handleCreate}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          新規作成
        </button>
      </div>
    </div>
  </div>

  {#if $loading}
    <div class="loading">
      <div class="spinner"></div>
      <span>読み込み中...</span>
    </div>
  {:else if $error}
    <div class="error">
      <p>エラー: {$error}</p>
      <button on:click={() => fetchRecipes()}>再読み込み</button>
    </div>
  {:else if !filteredRecipes || filteredRecipes.length === 0}
    <div class="empty">
      <div class="empty-icon">📚</div>
      <h3>レシピがありません</h3>
      <p>新しいレシピを作成するか、海外レシピを収集してください。</p>
      <div class="empty-actions">
        <button class="btn-primary" on:click={handleCreate}>最初のレシピを作成</button>
        <button class="btn-collector" on:click={handleCollector}>海外レシピを収集</button>
      </div>
    </div>
  {:else}
    <div class="recipes" class:recipes--grid={viewMode === 'grid'} class:recipes--list={viewMode === 'list'}>
      {#each filteredRecipes as recipe (recipe.id)}
        <RecipeCard
          {recipe}
          {viewMode}
          on:view={handleView}
          on:edit={handleEdit}
          on:delete={handleDelete}
          on:favorite={handleFavorite}
        />
      {/each}
    </div>

    {#if $pagination.total_pages > 1}
      <div class="pagination">
        <button
          class="page-btn"
          disabled={$pagination.page <= 1}
          on:click={() => fetchRecipes({ page: $pagination.page - 1 })}
          aria-label="前のページへ"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          前へ
        </button>
        <div class="page-info">
          <span class="page-current">{$pagination.page}</span>
          <span class="page-divider">/</span>
          <span class="page-total">{$pagination.total_pages}</span>
        </div>
        <button
          class="page-btn"
          disabled={$pagination.page >= $pagination.total_pages}
          on:click={() => fetchRecipes({ page: $pagination.page + 1 })}
          aria-label="次のページへ"
        >
          次へ
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>
    {/if}
  {/if}

  <ConfirmModal
    bind:show={showDeleteModal}
    title="レシピの削除"
    message={`「${deleteTarget.title}」を削除しますか？この操作は取り消せません。`}
    confirmText="削除"
    cancelText="キャンセル"
    danger={true}
    on:confirm={confirmDelete}
  />
</div>

<style>
  .recipe-list {
    width: 100%;
  }

  .toolbar {
    margin-bottom: 1rem;
  }

  .search-box {
    display: flex;
    gap: 0.5rem;
  }

  .search-input-wrapper {
    flex: 1;
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-icon {
    position: absolute;
    left: 1rem;
    color: #999;
    pointer-events: none;
  }

  .search-input-wrapper input {
    width: 100%;
    padding: 0.75rem 2.5rem 0.75rem 2.75rem;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    font-size: 1rem;
    transition: all 0.2s;
  }

  .search-input-wrapper input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .clear-btn {
    position: absolute;
    right: 0.75rem;
    padding: 0.25rem;
    background: transparent;
    border: none;
    color: #999;
    cursor: pointer;
    border-radius: 4px;
  }

  .clear-btn:hover {
    color: #666;
    background: #f0f0f0;
  }

  .search-btn {
    padding: 0.75rem 1.5rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .search-btn:hover {
    background: #5a6fd6;
  }

  .filter-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    flex-wrap: wrap;
    gap: 1rem;
  }

  .filter-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .filter-select {
    padding: 0.5rem 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    font-size: 0.9rem;
    background: white;
    cursor: pointer;
  }

  .result-count {
    font-size: 0.85rem;
    color: #888;
    padding: 0.5rem 0.75rem;
    background: #f5f5f5;
    border-radius: 6px;
  }

  .filter-right {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .view-toggle {
    display: flex;
    background: #f5f5f5;
    border-radius: 8px;
    padding: 4px;
  }

  .toggle-btn {
    padding: 0.5rem;
    background: transparent;
    border: none;
    border-radius: 6px;
    color: #888;
    cursor: pointer;
    transition: all 0.2s;
  }

  .toggle-btn.active {
    background: white;
    color: #667eea;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .action-buttons {
    display: flex;
    gap: 0.5rem;
  }

  .action-buttons button {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #667eea;
    color: white;
    border: none;
  }

  .btn-primary:hover {
    background: #5a6fd6;
  }

  .btn-secondary {
    background: white;
    color: #333;
    border: 1px solid #ddd;
  }

  .btn-secondary:hover {
    background: #f5f5f5;
  }

  .btn-collector {
    background: #28a745;
    color: white;
    border: none;
  }

  .btn-collector:hover {
    background: #218838;
  }

  .btn-export-html {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border: none;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(17, 153, 142, 0.3);
  }

  .btn-export-html:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(17, 153, 142, 0.4);
  }

  .btn-export-md {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  }

  .btn-export-md:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem;
    color: #666;
    gap: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f0f0f0;
    border-top-color: #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error {
    text-align: center;
    padding: 3rem;
    background: #fff5f5;
    border-radius: 12px;
    color: #c00;
  }

  .error button {
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    border: 1px solid #c00;
    border-radius: 8px;
    background: white;
    color: #c00;
    cursor: pointer;
  }

  .empty {
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }

  .empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
  }

  .empty h3 {
    margin: 0 0 0.5rem 0;
    color: #333;
  }

  .empty p {
    color: #666;
    margin: 0 0 1.5rem 0;
  }

  .empty-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
  }

  .empty-actions button {
    padding: 0.75rem 1.5rem;
  }

  .recipes--grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .recipes--list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 2rem;
    padding: 1rem;
  }

  .page-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .page-btn:hover:not(:disabled) {
    background: #f5f5f5;
    border-color: #667eea;
    color: #667eea;
  }

  .page-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .page-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
  }

  .page-current {
    font-weight: 600;
    color: #667eea;
  }

  .page-divider {
    color: #ccc;
  }

  .page-total {
    color: #666;
  }

  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .filter-bar {
      flex-direction: column;
      align-items: stretch;
    }

    .filter-left, .filter-right {
      width: 100%;
      justify-content: space-between;
    }

    .action-buttons {
      flex-wrap: wrap;
    }

    .recipes--grid {
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    }
  }

  @media (max-width: 480px) {
    .recipes--grid {
      grid-template-columns: 1fr;
    }

    .search-box {
      flex-direction: column;
    }

    .search-btn {
      width: 100%;
    }
  }
</style>

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
  import { onMount } from 'svelte';
  import ConfirmModal from './ConfirmModal.svelte';

  const dispatch = createEventDispatcher();

  let searchInput = '';
  let showDeleteModal = false;
  let deleteTarget = { id: null, title: '' };
  let searchLabelId = 'search-label';

  onMount(() => {
    fetchRecipes();
  });

  async function handleSearch() {
    await searchRecipes(searchInput);
  }

  function handleDelete(id, title) {
    deleteTarget = { id, title };
    showDeleteModal = true;
  }

  async function confirmDelete() {
    if (deleteTarget.id) {
      await deleteRecipe(deleteTarget.id);
      deleteTarget = { id: null, title: '' };
    }
  }

  function handleView(recipe) {
    dispatch('view', recipe);
  }

  function handleEdit(recipe) {
    dispatch('edit', recipe);
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

  function formatTime(minutes) {
    if (!minutes) return '-';
    if (minutes < 60) return `${minutes}分`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}時間${mins}分` : `${hours}時間`;
  }
</script>

<div class="recipe-list">
  <div class="toolbar">
    <div class="search-box">
      <label id={searchLabelId} class="visually-hidden">レシピを検索</label>
      <input
        type="text"
        placeholder="レシピを検索..."
        bind:value={searchInput}
        on:keydown={(e) => e.key === 'Enter' && handleSearch()}
        aria-labelledby={searchLabelId}
      />
      <button on:click={handleSearch} aria-label="レシピを検索">検索</button>
    </div>
    <div class="toolbar-actions">
      <button class="btn-collector" on:click={handleCollector}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <circle cx="12" cy="12" r="10"/>
          <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
        </svg>
        海外レシピ収集
      </button>
      <button class="btn-secondary" on:click={handleImport}>CSVインポート</button>
      <button class="btn-primary" on:click={handleCreate}>新規作成</button>
    </div>
  </div>

  {#if $loading}
    <div class="loading">読み込み中...</div>
  {:else if $error}
    <div class="error">エラー: {$error}</div>
  {:else if $recipes.length === 0}
    <div class="empty">
      <p>レシピがありません。</p>
      <button class="btn-primary" on:click={handleCreate}>最初のレシピを作成</button>
    </div>
  {:else}
    <div class="recipes">
      {#each $recipes as recipe (recipe.id)}
        <div class="recipe-card">
          <div class="recipe-header">
            <h3>{recipe.title}</h3>
            <span class="source-type">{recipe.source_type}</span>
          </div>
          {#if recipe.description}
            <p class="description">{recipe.description}</p>
          {/if}
          <div class="meta">
            {#if recipe.servings}
              <span>{recipe.servings}人前</span>
            {/if}
            {#if recipe.prep_time_minutes}
              <span>準備: {formatTime(recipe.prep_time_minutes)}</span>
            {/if}
            {#if recipe.cook_time_minutes}
              <span>調理: {formatTime(recipe.cook_time_minutes)}</span>
            {/if}
            {#if recipe.ingredient_count}
              <span>材料: {recipe.ingredient_count}品</span>
            {/if}
          </div>
          <div class="actions">
            <button on:click={() => handleView(recipe)}>詳細</button>
            <button on:click={() => handleEdit(recipe)}>編集</button>
            <button class="btn-danger" on:click={() => handleDelete(recipe.id, recipe.title)} aria-label="レシピを削除">
              削除
            </button>
          </div>
        </div>
      {/each}
    </div>

    {#if $pagination.total_pages > 1}
      <div class="pagination">
        <button
          disabled={$pagination.page <= 1}
          on:click={() => fetchRecipes({ page: $pagination.page - 1 })}
          aria-label="前のページへ"
        >
          前へ
        </button>
        <span>{$pagination.page} / {$pagination.total_pages}</span>
        <button
          disabled={$pagination.page >= $pagination.total_pages}
          on:click={() => fetchRecipes({ page: $pagination.page + 1 })}
          aria-label="次のページへ"
        >
          次へ
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
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    gap: 1rem;
  }

  .search-box {
    display: flex;
    gap: 0.5rem;
    flex: 1;
    max-width: 400px;
  }

  .search-box input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .loading,
  .error,
  .empty {
    text-align: center;
    padding: 2rem;
  }

  .error {
    color: #c00;
  }

  .recipes {
    display: grid;
    gap: 1rem;
  }

  .recipe-card {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .recipe-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .recipe-header h3 {
    margin: 0;
    color: #333;
  }

  .source-type {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    background: #e8f4f8;
    border-radius: 4px;
    color: #0077aa;
  }

  .description {
    color: #666;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .meta {
    display: flex;
    gap: 1rem;
    font-size: 0.85rem;
    color: #888;
    margin: 0.5rem 0;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  button {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  button:hover:not(:disabled) {
    background: #f5f5f5;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background: #0077aa;
    color: white;
    border-color: #0077aa;
  }

  .btn-primary:hover {
    background: #005580;
  }

  .btn-secondary {
    background: #f5f5f5;
    color: #333;
    border-color: #ccc;
  }

  .btn-secondary:hover {
    background: #e8e8e8;
  }

  .btn-collector {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #28a745;
    color: white;
    border-color: #28a745;
  }

  .btn-collector:hover {
    background: #218838;
  }

  .toolbar-actions {
    display: flex;
    gap: 0.5rem;
  }

  .btn-danger {
    color: #c00;
    border-color: #c00;
  }

  .btn-danger:hover {
    background: #ffe6e6;
  }

  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 1.5rem;
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
</style>

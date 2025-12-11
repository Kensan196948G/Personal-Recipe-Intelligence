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

  const dispatch = createEventDispatcher();

  let searchInput = '';

  onMount(() => {
    fetchRecipes();
  });

  async function handleSearch() {
    await searchRecipes(searchInput);
  }

  async function handleDelete(id, title) {
    if (confirm(`「${title}」を削除しますか？`)) {
      await deleteRecipe(id);
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
      <input
        type="text"
        placeholder="レシピを検索..."
        bind:value={searchInput}
        on:keydown={(e) => e.key === 'Enter' && handleSearch()}
      />
      <button on:click={handleSearch}>検索</button>
    </div>
    <button class="btn-primary" on:click={handleCreate}>新規作成</button>
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
            <button class="btn-danger" on:click={() => handleDelete(recipe.id, recipe.title)}>
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
        >
          前へ
        </button>
        <span>{$pagination.page} / {$pagination.total_pages}</span>
        <button
          disabled={$pagination.page >= $pagination.total_pages}
          on:click={() => fetchRecipes({ page: $pagination.page + 1 })}
        >
          次へ
        </button>
      </div>
    {/if}
  {/if}
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
</style>

<script>
  import { createEventDispatcher } from 'svelte';

  export let recipe;

  const dispatch = createEventDispatcher();

  function handleBack() {
    dispatch('back');
  }

  function handleEdit() {
    dispatch('edit', recipe);
  }

  function formatTime(minutes) {
    if (!minutes) return '-';
    if (minutes < 60) return `${minutes}分`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}時間${mins}分` : `${hours}時間`;
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
</script>

<div class="recipe-detail">
  <div class="header">
    <button class="back-btn" on:click={handleBack}>
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      戻る
    </button>
    <button class="edit-btn" on:click={handleEdit}>
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
      編集
    </button>
  </div>

  <div class="content">
    <h1>{recipe.title}</h1>

    <div class="meta-info">
      <span class="source-type">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        {recipe.source_type}
      </span>
      {#if recipe.servings}
        <span class="meta-item">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 00-3-3.87"/>
            <path d="M16 3.13a4 4 0 010 7.75"/>
          </svg>
          {recipe.servings}人前
        </span>
      {/if}
      {#if recipe.prep_time_minutes}
        <span class="meta-item">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 8 14"/>
          </svg>
          準備: {formatTime(recipe.prep_time_minutes)}
        </span>
      {/if}
      {#if recipe.cook_time_minutes}
        <span class="meta-item">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
          調理: {formatTime(recipe.cook_time_minutes)}
        </span>
      {/if}
    </div>

    {#if recipe.description}
      <p class="description">{recipe.description}</p>
    {/if}

    {#if recipe.source_url}
      <p class="source-url">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
          <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
        </svg>
        出典: <a href={recipe.source_url} target="_blank" rel="noopener noreferrer">
          {recipe.source_url}
        </a>
      </p>
    {/if}

    {#if recipe.tags && recipe.tags.length > 0}
      <div class="tags">
        {#each recipe.tags as tag}
          <span class="tag">
            <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/>
              <line x1="7" y1="7" x2="7.01" y2="7"/>
            </svg>
            {tag.name}
          </span>
        {/each}
      </div>
    {/if}

    <section class="ingredients">
      <h2>
        <svg class="icon-section" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/>
          <line x1="3" y1="6" x2="21" y2="6"/>
          <path d="M16 10a4 4 0 01-8 0"/>
        </svg>
        材料
      </h2>
      {#if recipe.ingredients && recipe.ingredients.length > 0}
        <ul>
          {#each recipe.ingredients as ingredient}
            <li>
              <span class="ingredient-name">{ingredient.name}</span>
              {#if ingredient.amount || ingredient.unit}
                <span class="ingredient-amount">
                  {ingredient.amount || ''}{ingredient.unit || ''}
                </span>
              {/if}
              {#if ingredient.note}
                <span class="ingredient-note">({ingredient.note})</span>
              {/if}
            </li>
          {/each}
        </ul>
      {:else}
        <p class="empty">材料が登録されていません</p>
      {/if}
    </section>

    <section class="steps">
      <h2>
        <svg class="icon-section" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="8" y1="6" x2="21" y2="6"/>
          <line x1="8" y1="12" x2="21" y2="12"/>
          <line x1="8" y1="18" x2="21" y2="18"/>
          <line x1="3" y1="6" x2="3.01" y2="6"/>
          <line x1="3" y1="12" x2="3.01" y2="12"/>
          <line x1="3" y1="18" x2="3.01" y2="18"/>
        </svg>
        手順
      </h2>
      {#if recipe.steps && recipe.steps.length > 0}
        <ol>
          {#each recipe.steps as step}
            <li>{step.description}</li>
          {/each}
        </ol>
      {:else}
        <p class="empty">手順が登録されていません</p>
      {/if}
    </section>

    <div class="dates">
      <p>作成日: {formatDate(recipe.created_at)}</p>
      <p>更新日: {formatDate(recipe.updated_at)}</p>
    </div>
  </div>
</div>

<style>
  .recipe-detail {
    max-width: 800px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1.5rem;
  }

  .back-btn,
  .edit-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .icon {
    width: 18px;
    height: 18px;
  }

  .icon-sm {
    width: 16px;
    height: 16px;
    vertical-align: middle;
  }

  .icon-xs {
    width: 12px;
    height: 12px;
    vertical-align: middle;
  }

  .icon-section {
    width: 24px;
    height: 24px;
    vertical-align: middle;
    margin-right: 0.5rem;
  }

  .back-btn:hover,
  .edit-btn:hover {
    background: #f5f5f5;
  }

  .edit-btn {
    background: #0077aa;
    color: white;
    border-color: #0077aa;
  }

  .edit-btn:hover {
    background: #005580;
  }

  .content {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  h1 {
    margin: 0 0 1rem 0;
    color: #333;
  }

  h2 {
    display: flex;
    align-items: center;
    color: #333;
    border-bottom: 2px solid #0077aa;
    padding-bottom: 0.5rem;
    margin-top: 2rem;
  }

  .meta-info {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: #666;
  }

  .source-type {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: #e8f4f8;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    color: #0077aa;
  }

  .meta-item {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }

  .description {
    color: #444;
    line-height: 1.6;
    margin: 1rem 0;
  }

  .source-url {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.85rem;
    color: #666;
  }

  .source-url a {
    color: #0077aa;
    text-decoration: none;
  }

  .source-url a:hover {
    text-decoration: underline;
  }

  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1rem 0;
  }

  .tag {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    background: #f0f0f0;
    padding: 0.25rem 0.75rem;
    border-radius: 16px;
    font-size: 0.85rem;
    color: #555;
  }

  .ingredients ul {
    list-style: none;
    padding: 0;
  }

  .ingredients li {
    padding: 0.5rem 0;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
  }

  .ingredients li:last-child {
    border-bottom: none;
  }

  .ingredient-name {
    font-weight: 500;
  }

  .ingredient-amount {
    color: #666;
  }

  .ingredient-note {
    color: #888;
    font-size: 0.85rem;
  }

  .steps ol {
    padding-left: 1.5rem;
  }

  .steps li {
    padding: 0.75rem 0;
    line-height: 1.6;
  }

  .empty {
    color: #888;
    font-style: italic;
  }

  .dates {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
    font-size: 0.85rem;
    color: #888;
  }

  .dates p {
    margin: 0.25rem 0;
  }
</style>

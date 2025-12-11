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
    <button class="back-btn" on:click={handleBack}>← 戻る</button>
    <button class="edit-btn" on:click={handleEdit}>編集</button>
  </div>

  <div class="content">
    <h1>{recipe.title}</h1>

    <div class="meta-info">
      <span class="source-type">{recipe.source_type}</span>
      {#if recipe.servings}
        <span>{recipe.servings}人前</span>
      {/if}
      {#if recipe.prep_time_minutes}
        <span>準備: {formatTime(recipe.prep_time_minutes)}</span>
      {/if}
      {#if recipe.cook_time_minutes}
        <span>調理: {formatTime(recipe.cook_time_minutes)}</span>
      {/if}
    </div>

    {#if recipe.description}
      <p class="description">{recipe.description}</p>
    {/if}

    {#if recipe.source_url}
      <p class="source-url">
        出典: <a href={recipe.source_url} target="_blank" rel="noopener noreferrer">
          {recipe.source_url}
        </a>
      </p>
    {/if}

    {#if recipe.tags && recipe.tags.length > 0}
      <div class="tags">
        {#each recipe.tags as tag}
          <span class="tag">{tag.name}</span>
        {/each}
      </div>
    {/if}

    <section class="ingredients">
      <h2>材料</h2>
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
      <h2>手順</h2>
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
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
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
    background: #e8f4f8;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    color: #0077aa;
  }

  .description {
    color: #444;
    line-height: 1.6;
    margin: 1rem 0;
  }

  .source-url {
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

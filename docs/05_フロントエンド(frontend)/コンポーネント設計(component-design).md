# コンポーネント設計 (Component Design)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のUIコンポーネント設計を定義する。

## 2. コンポーネント一覧

### 2.1 共通コンポーネント

| コンポーネント | 説明 | Props |
|---------------|------|-------|
| Button | ボタン | type, variant, disabled, onClick |
| Input | テキスト入力 | type, value, placeholder, error |
| TextArea | 複数行入力 | value, rows, placeholder |
| Select | セレクトボックス | options, value, placeholder |
| Modal | モーダルダイアログ | isOpen, title, onClose |
| Loading | ローディング表示 | size, message |
| Toast | 通知メッセージ | type, message, duration |
| Pagination | ページネーション | page, totalPages, onChange |
| TagChip | タグチップ | tag, removable, onClick |

### 2.2 レシピコンポーネント

| コンポーネント | 説明 | Props |
|---------------|------|-------|
| RecipeCard | レシピカード | recipe, onClick |
| RecipeForm | レシピフォーム | recipe, onSubmit |
| RecipeDetail | レシピ詳細 | recipe |
| RecipeList | レシピ一覧 | recipes, loading |
| IngredientList | 材料リスト | ingredients, editable |
| StepList | 手順リスト | steps, editable |
| SearchBox | 検索ボックス | value, onSearch |
| TagFilter | タグフィルタ | tags, selected, onChange |

### 2.3 レイアウトコンポーネント

| コンポーネント | 説明 | Props |
|---------------|------|-------|
| Header | ヘッダー | - |
| Footer | フッター | - |
| Sidebar | サイドバー | isOpen |
| Container | コンテナ | maxWidth |
| Grid | グリッドレイアウト | columns, gap |

## 3. コンポーネント詳細

### 3.1 Button

```svelte
<!-- Button.svelte -->
<script>
  export let type = 'button';
  export let variant = 'primary'; // primary, secondary, danger, ghost
  export let size = 'medium';     // small, medium, large
  export let disabled = false;
  export let loading = false;
</script>

<button
  {type}
  class="btn btn-{variant} btn-{size}"
  {disabled}
  disabled={disabled || loading}
  on:click
>
  {#if loading}
    <span class="spinner"></span>
  {/if}
  <slot />
</button>

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #FF6B35;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #E55A2B;
  }

  .btn-secondary {
    background: #E0E0E0;
    color: #333;
  }

  .btn-danger {
    background: #F44336;
    color: white;
  }

  .btn-ghost {
    background: transparent;
    color: #666;
  }

  .btn-small { padding: 4px 12px; font-size: 14px; }
  .btn-medium { padding: 8px 16px; font-size: 16px; }
  .btn-large { padding: 12px 24px; font-size: 18px; }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
```

### 3.2 RecipeCard

```svelte
<!-- RecipeCard.svelte -->
<script>
  import TagChip from '../common/TagChip.svelte';

  export let recipe;

  function formatTime(minutes) {
    if (!minutes) return '-';
    if (minutes < 60) return `${minutes}分`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins ? `${hours}時間${mins}分` : `${hours}時間`;
  }
</script>

<article class="recipe-card" on:click>
  <div class="image-container">
    {#if recipe.image_path}
      <img src={recipe.image_path} alt={recipe.title} />
    {:else}
      <div class="placeholder">
        <span>No Image</span>
      </div>
    {/if}
  </div>

  <div class="content">
    <h3 class="title">{recipe.title}</h3>

    <div class="meta">
      <span class="time">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <circle cx="12" cy="12" r="10" stroke="currentColor" fill="none"/>
          <path d="M12 6v6l4 2" stroke="currentColor" fill="none"/>
        </svg>
        {formatTime(recipe.cook_time_minutes)}
      </span>
      {#if recipe.servings}
        <span class="servings">{recipe.servings}人分</span>
      {/if}
    </div>

    {#if recipe.tags?.length}
      <div class="tags">
        {#each recipe.tags.slice(0, 3) as tag}
          <TagChip {tag} />
        {/each}
      </div>
    {/if}
  </div>
</article>

<style>
  .recipe-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .recipe-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }

  .image-container {
    aspect-ratio: 16 / 9;
    overflow: hidden;
  }

  .image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .placeholder {
    width: 100%;
    height: 100%;
    background: #F5F5F5;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
  }

  .content {
    padding: 16px;
  }

  .title {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 8px;
    color: #333;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .meta {
    display: flex;
    gap: 16px;
    font-size: 14px;
    color: #666;
    margin-bottom: 12px;
  }

  .time {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
</style>
```

### 3.3 SearchBox

```svelte
<!-- SearchBox.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';

  export let value = '';
  export let placeholder = 'レシピを検索...';

  const dispatch = createEventDispatcher();

  function handleSubmit(e) {
    e.preventDefault();
    dispatch('search', { query: value });
  }

  function handleClear() {
    value = '';
    dispatch('search', { query: '' });
  }
</script>

<form class="search-box" on:submit={handleSubmit}>
  <svg class="icon search-icon" viewBox="0 0 24 24">
    <circle cx="11" cy="11" r="8" stroke="currentColor" fill="none"/>
    <path d="M21 21l-4.35-4.35" stroke="currentColor"/>
  </svg>

  <input
    type="text"
    bind:value
    {placeholder}
    class="input"
  />

  {#if value}
    <button type="button" class="clear-btn" on:click={handleClear}>
      <svg viewBox="0 0 24 24" width="16" height="16">
        <path d="M18 6L6 18M6 6l12 12" stroke="currentColor"/>
      </svg>
    </button>
  {/if}

  <button type="submit" class="search-btn">検索</button>
</form>

<style>
  .search-box {
    display: flex;
    align-items: center;
    background: white;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 8px 16px;
    gap: 12px;
  }

  .search-box:focus-within {
    border-color: #FF6B35;
    box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2);
  }

  .search-icon {
    width: 20px;
    height: 20px;
    color: #999;
  }

  .input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 16px;
  }

  .clear-btn {
    background: none;
    border: none;
    padding: 4px;
    cursor: pointer;
    color: #999;
  }

  .search-btn {
    background: #FF6B35;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .search-btn:hover {
    background: #E55A2B;
  }
</style>
```

## 4. コンポーネント間通信

### 4.1 Props（親→子）

```svelte
<!-- 親コンポーネント -->
<RecipeCard recipe={selectedRecipe} />
```

### 4.2 Events（子→親）

```svelte
<!-- 子コンポーネント -->
<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  function handleClick() {
    dispatch('select', { id: recipe.id });
  }
</script>

<!-- 親コンポーネント -->
<RecipeCard on:select={handleSelect} />
```

### 4.3 Store（グローバル）

```svelte
<script>
  import { recipes } from '../stores/recipes.js';
</script>

{#each $recipes as recipe}
  <RecipeCard {recipe} />
{/each}
```

## 5. コンポーネントテスト

```javascript
// RecipeCard.test.js
import { render, fireEvent } from '@testing-library/svelte';
import RecipeCard from './RecipeCard.svelte';

describe('RecipeCard', () => {
  const mockRecipe = {
    id: 1,
    title: 'テストレシピ',
    cook_time_minutes: 30,
    servings: 4,
    tags: [{ name: '和食' }]
  };

  it('レシピタイトルを表示する', () => {
    const { getByText } = render(RecipeCard, { props: { recipe: mockRecipe } });
    expect(getByText('テストレシピ')).toBeInTheDocument();
  });

  it('クリックイベントを発火する', async () => {
    const { component, container } = render(RecipeCard, { props: { recipe: mockRecipe } });
    const mockFn = vi.fn();
    component.$on('click', mockFn);

    await fireEvent.click(container.querySelector('.recipe-card'));
    expect(mockFn).toHaveBeenCalled();
  });
});
```

## 6. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

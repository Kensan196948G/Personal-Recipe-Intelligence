<script>
  import { createEventDispatcher } from 'svelte';
  import { getImageUrl } from '../services/api.js';

  export let recipe;
  export let viewMode = 'grid'; // 'grid' or 'list'

  const dispatch = createEventDispatcher();

  // State for image loading
  let imageLoaded = false;
  let imageError = false;

  // 画像ステータスに応じたプレースホルダー画像を生成
  function getPlaceholderImage() {
    const status = recipe.image_status;
    let text = 'No Image';
    let bgColor = '%23f0f0f0';
    let textColor = '%23999';

    if (status === 'API制限到達。後日再取得') {
      text = '画像取得待ち';
      bgColor = '%23fff3cd';  // 黄色系
      textColor = '%23856404';
    } else if (status === '画像ソースなし') {
      text = '画像なし';
      bgColor = '%23f8d7da';  // 赤系
      textColor = '%23721c24';
    }

    return `data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150"%3E%3Crect fill="${bgColor}" width="200" height="150"/%3E%3Ctext fill="${textColor}" font-family="sans-serif" font-size="12" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle"%3E${encodeURIComponent(text)}%3C/text%3E%3C/svg%3E`;
  }

  // 画像URL取得
  function getRecipeImageUrl() {
    const imageUrl = getImageUrl(recipe);
    return imageUrl || getPlaceholderImage();
  }

  function handleImageLoad() {
    imageLoaded = true;
    imageError = false;
  }

  function handleImageError() {
    imageError = true;
    imageLoaded = true;
  }

  function formatTime(minutes) {
    if (!minutes) return null;
    if (minutes < 60) return `${minutes}分`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}時間${mins}分` : `${hours}時間`;
  }

  function getTotalTime() {
    const prep = recipe.prep_time_minutes || 0;
    const cook = recipe.cook_time_minutes || 0;
    const total = prep + cook;
    return total > 0 ? formatTime(total) : null;
  }

  function getSourceIcon(type) {
    const icons = {
      'manual': '✍️',
      'web': '🌐',
      'ocr': '📷',
      'api': '🤖',
    };
    return icons[type] || '📄';
  }

  function handleView() {
    dispatch('view', recipe);
  }

  function handleEdit() {
    dispatch('edit', recipe);
  }

  function handleDelete() {
    dispatch('delete', { id: recipe.id, title: recipe.title });
  }

  function handleFavorite() {
    dispatch('favorite', recipe);
  }

  function handleExportMarkdown() {
    // Markdownエクスポート - 直接ダウンロードリンクを開く
    const exportUrl = `/api/v1/recipes/${recipe.id}/export/markdown`;
    window.open(exportUrl, '_blank');
  }
</script>

{#if viewMode === 'grid'}
  <article class="card card--grid">
    <div class="card-image" on:click={handleView} on:keypress={handleView} role="button" tabindex="0">
      {#if !imageLoaded}
        <div class="image-skeleton"></div>
      {/if}
      <img
        src={getRecipeImageUrl()}
        alt={recipe.title}
        loading="lazy"
        class:loaded={imageLoaded}
        on:load={handleImageLoad}
        on:error={handleImageError}
      />
      {#if recipe.is_favorite}
        <span class="favorite-badge">⭐</span>
      {/if}
      <span class="source-badge" title={recipe.source_type}>
        {getSourceIcon(recipe.source_type)}
      </span>
    </div>

    <div class="card-content">
      <h3 class="card-title" on:click={handleView} on:keypress={handleView} role="button" tabindex="0">
        {recipe.title}
      </h3>

      {#if recipe.description}
        <p class="card-description">{recipe.description}</p>
      {/if}

      <div class="card-meta">
        {#if recipe.servings}
          <span class="meta-item" title="人前">
            <span class="meta-icon">👥</span>
            {recipe.servings}人前
          </span>
        {/if}
        {#if getTotalTime()}
          <span class="meta-item" title="調理時間">
            <span class="meta-icon">⏱️</span>
            {getTotalTime()}
          </span>
        {/if}
        {#if recipe.ingredient_count}
          <span class="meta-item" title="材料数">
            <span class="meta-icon">🥗</span>
            {recipe.ingredient_count}品
          </span>
        {/if}
      </div>

      {#if recipe.rating}
        <div class="card-rating">
          {#each Array(5) as _, i}
            <span class="star" class:star--filled={i < Math.round(recipe.rating)}>★</span>
          {/each}
          <span class="rating-value">({recipe.rating.toFixed(1)})</span>
        </div>
      {/if}
    </div>

    <div class="card-actions">
      <button class="action-btn action-btn--view" on:click={handleView} title="詳細を見る">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
      </button>
      <button class="action-btn action-btn--edit" on:click={handleEdit} title="編集">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </button>
      <button class="action-btn action-btn--export" on:click={handleExportMarkdown} title="MDでダウンロード">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      </button>
      <button class="action-btn action-btn--favorite" class:active={recipe.is_favorite} on:click={handleFavorite} title="お気に入り">
        <svg viewBox="0 0 24 24" fill={recipe.is_favorite ? "currentColor" : "none"} stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/>
        </svg>
      </button>
      <button class="action-btn action-btn--delete" on:click={handleDelete} title="削除">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
        </svg>
      </button>
    </div>
  </article>
{:else}
  <article class="card card--list">
    <div class="list-image" on:click={handleView} on:keypress={handleView} role="button" tabindex="0">
      {#if !imageLoaded}
        <div class="image-skeleton"></div>
      {/if}
      <img
        src={getRecipeImageUrl()}
        alt={recipe.title}
        loading="lazy"
        class:loaded={imageLoaded}
        on:load={handleImageLoad}
        on:error={handleImageError}
      />
    </div>

    <div class="list-content">
      <div class="list-header">
        <h3 class="card-title" on:click={handleView} on:keypress={handleView} role="button" tabindex="0">
          {recipe.title}
        </h3>
        <div class="list-badges">
          {#if recipe.is_favorite}
            <span class="badge badge--favorite">⭐</span>
          {/if}
          <span class="badge badge--source" title={recipe.source_type}>
            {getSourceIcon(recipe.source_type)} {recipe.source_type}
          </span>
        </div>
      </div>

      {#if recipe.description}
        <p class="card-description">{recipe.description}</p>
      {/if}

      <div class="list-footer">
        <div class="card-meta">
          {#if recipe.servings}
            <span class="meta-item">👥 {recipe.servings}人前</span>
          {/if}
          {#if getTotalTime()}
            <span class="meta-item">⏱️ {getTotalTime()}</span>
          {/if}
          {#if recipe.ingredient_count}
            <span class="meta-item">🥗 {recipe.ingredient_count}品</span>
          {/if}
        </div>

        <div class="card-actions">
          <button class="btn btn--primary" on:click={handleView}>詳細</button>
          <button class="btn btn--secondary" on:click={handleEdit}>編集</button>
          <button class="btn btn--export" on:click={handleExportMarkdown} title="MDでダウンロード">📥 MD</button>
          <button class="btn btn--danger" on:click={handleDelete}>削除</button>
        </div>
      </div>
    </div>
  </article>
{/if}

<style>
  /* Grid View */
  .card--grid {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
  }

  .card--grid:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  .card-image {
    position: relative;
    aspect-ratio: 16 / 10;
    overflow: hidden;
    cursor: pointer;
  }

  .card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s, opacity 0.3s;
    opacity: 0;
  }

  .card-image img.loaded {
    opacity: 1;
  }

  .image-skeleton {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
  }

  @keyframes skeleton-loading {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }

  .card--grid:hover .card-image img {
    transform: scale(1.05);
  }

  .favorite-badge {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    font-size: 1.25rem;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
  }

  .source-badge {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    background: rgba(255, 255, 255, 0.9);
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.875rem;
  }

  .card-content {
    padding: 1rem;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .card-title {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #1a1a2e;
    cursor: pointer;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .card-title:hover {
    color: #667eea;
  }

  .card-description {
    margin: 0 0 0.75rem 0;
    font-size: 0.85rem;
    color: #666;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: auto;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.8rem;
    color: #888;
  }

  .meta-icon {
    font-size: 0.9rem;
  }

  .card-rating {
    display: flex;
    align-items: center;
    gap: 0.125rem;
    margin-top: 0.5rem;
  }

  .star {
    color: #ddd;
    font-size: 0.875rem;
  }

  .star--filled {
    color: #ffc107;
  }

  .rating-value {
    font-size: 0.75rem;
    color: #888;
    margin-left: 0.25rem;
  }

  .card-actions {
    display: flex;
    gap: 0.25rem;
    padding: 0.75rem 1rem;
    border-top: 1px solid #f0f0f0;
    background: #fafafa;
  }

  .action-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
  }

  .action-btn:hover {
    background: #f0f0f0;
  }

  .action-btn--view:hover { color: #667eea; }
  .action-btn--edit:hover { color: #28a745; }
  .action-btn--export:hover { color: #17a2b8; }
  .action-btn--favorite:hover, .action-btn--favorite.active { color: #ff6b6b; }
  .action-btn--delete:hover { color: #dc3545; }

  /* List View */
  .card--list {
    display: flex;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: box-shadow 0.2s;
  }

  .card--list:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }

  .list-image {
    width: 160px;
    min-width: 160px;
    cursor: pointer;
  }

  .list-image {
    position: relative;
  }

  .list-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: opacity 0.3s;
    opacity: 0;
  }

  .list-image img.loaded {
    opacity: 1;
  }

  .list-image .image-skeleton {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
  }

  .list-content {
    flex: 1;
    padding: 1rem;
    display: flex;
    flex-direction: column;
  }

  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 0.5rem;
  }

  .list-badges {
    display: flex;
    gap: 0.5rem;
    flex-shrink: 0;
  }

  .badge {
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.75rem;
  }

  .badge--favorite {
    background: #fff3cd;
  }

  .badge--source {
    background: #e3f2fd;
    color: #1976d2;
  }

  .list-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
  }

  .card--list .card-actions {
    border-top: none;
    background: transparent;
    padding: 0;
  }

  .btn {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    background: white;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn--primary {
    background: #667eea;
    color: white;
    border-color: #667eea;
  }

  .btn--primary:hover {
    background: #5a6fd6;
  }

  .btn--secondary:hover {
    background: #f5f5f5;
  }

  .btn--danger {
    color: #dc3545;
    border-color: #dc3545;
  }

  .btn--danger:hover {
    background: #fff5f5;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .list-image {
      width: 100px;
      min-width: 100px;
    }

    .list-footer {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.75rem;
    }
  }
</style>

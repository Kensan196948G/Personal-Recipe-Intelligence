<script>
  import { createEventDispatcher } from 'svelte';
  import { recipeApi, getImageUrl } from '../services/api.js';

  export let recipe;

  const dispatch = createEventDispatcher();

  // State
  let checkedIngredients = new Set();
  let showCookingMode = false;
  let currentStep = 0;
  let showImageModal = false;
  let imageLoaded = false;

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

    return `data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"%3E%3Crect fill="${bgColor}" width="400" height="300"/%3E%3Ctext fill="${textColor}" font-family="sans-serif" font-size="16" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle"%3E${encodeURIComponent(text)}%3C/text%3E%3C/svg%3E`;
  }

  // 画像URL取得
  function getRecipeImageUrl() {
    const imageUrl = getImageUrl(recipe);
    return imageUrl || getPlaceholderImage();
  }

  function handleImageLoad() {
    imageLoaded = true;
  }

  function openImageModal() {
    const imageUrl = getImageUrl(recipe);
    if (imageUrl) {
      showImageModal = true;
    }
  }

  function closeImageModal() {
    showImageModal = false;
  }

  function handleModalClick(event) {
    if (event.target.classList.contains('image-modal')) {
      closeImageModal();
    }
  }

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

  function getTotalTime() {
    const prep = recipe.prep_time_minutes || 0;
    const cook = recipe.cook_time_minutes || 0;
    return prep + cook;
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
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

  function toggleIngredient(index) {
    if (checkedIngredients.has(index)) {
      checkedIngredients.delete(index);
    } else {
      checkedIngredients.add(index);
    }
    checkedIngredients = checkedIngredients;
  }

  async function toggleFavorite() {
    try {
      await recipeApi.update(recipe.id, {
        ...recipe,
        is_favorite: !recipe.is_favorite
      });
      recipe.is_favorite = !recipe.is_favorite;
    } catch (e) {
      console.error('Failed to toggle favorite:', e);
    }
  }

  function handlePrint() {
    window.print();
  }

  function handleShare() {
    if (navigator.share) {
      navigator.share({
        title: recipe.title,
        text: recipe.description || '',
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('URLをコピーしました');
    }
  }

  function startCookingMode() {
    showCookingMode = true;
    currentStep = 0;
  }

  function exitCookingMode() {
    showCookingMode = false;
  }

  function nextStep() {
    if (currentStep < recipe.steps.length - 1) {
      currentStep++;
    }
  }

  function prevStep() {
    if (currentStep > 0) {
      currentStep--;
    }
  }
</script>

{#if showCookingMode}
  <!-- Cooking Mode -->
  <div class="cooking-mode">
    <div class="cooking-header">
      <button class="exit-btn" on:click={exitCookingMode}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
      <h2>{recipe.title}</h2>
    </div>

    <div class="cooking-progress">
      <div class="progress-bar">
        <div class="progress-fill" style="width: {((currentStep + 1) / recipe.steps.length) * 100}%"></div>
      </div>
      <span class="progress-text">ステップ {currentStep + 1} / {recipe.steps.length}</span>
    </div>

    <div class="cooking-content">
      <div class="step-number">{currentStep + 1}</div>
      <p class="step-text">{recipe.steps[currentStep]?.description || ''}</p>
    </div>

    <div class="cooking-nav">
      <button class="nav-btn" on:click={prevStep} disabled={currentStep === 0}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        前へ
      </button>
      {#if currentStep === recipe.steps.length - 1}
        <button class="nav-btn nav-btn--complete" on:click={exitCookingMode}>
          完了
        </button>
      {:else}
        <button class="nav-btn nav-btn--next" on:click={nextStep}>
          次へ
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      {/if}
    </div>
  </div>
{:else}
  <!-- Normal Detail View -->
  <div class="recipe-detail">
    <div class="header">
      <button class="back-btn" on:click={handleBack}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        戻る
      </button>
      <div class="header-actions">
        <button class="action-btn" on:click={handlePrint} title="印刷">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <polyline points="6 9 6 2 18 2 18 9"/>
            <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2"/>
            <rect x="6" y="14" width="12" height="8"/>
          </svg>
        </button>
        <button class="action-btn" on:click={handleShare} title="共有">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <circle cx="18" cy="5" r="3"/>
            <circle cx="6" cy="12" r="3"/>
            <circle cx="18" cy="19" r="3"/>
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
          </svg>
        </button>
        <button class="edit-btn" on:click={handleEdit}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          編集
        </button>
      </div>
    </div>

    <div class="content">
      <div class="hero">
        <div class="hero-image" on:click={openImageModal} on:keypress={(e) => e.key === 'Enter' && openImageModal()} role="button" tabindex="0" class:clickable={getImageUrl(recipe)}>
          {#if !imageLoaded}
            <div class="image-skeleton"></div>
          {/if}
          <img
            src={getRecipeImageUrl()}
            alt={recipe.title}
            class:loaded={imageLoaded}
            on:load={handleImageLoad}
          />
          {#if getImageUrl(recipe)}
            <div class="image-overlay">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="32" height="32">
                <circle cx="11" cy="11" r="8"/>
                <path d="M21 21l-4.35-4.35"/>
                <line x1="11" y1="8" x2="11" y2="14"/>
                <line x1="8" y1="11" x2="14" y2="11"/>
              </svg>
            </div>
          {/if}
          <button class="favorite-btn" on:click|stopPropagation={toggleFavorite} class:active={recipe.is_favorite}>
            <svg viewBox="0 0 24 24" fill={recipe.is_favorite ? "currentColor" : "none"} stroke="currentColor" stroke-width="2" width="24" height="24">
              <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/>
            </svg>
          </button>
        </div>

        <div class="hero-content">
          <h1>{recipe.title}</h1>

          {#if recipe.rating}
            <div class="rating">
              {#each Array(5) as _, i}
                <span class="star" class:star--filled={i < Math.round(recipe.rating)}>★</span>
              {/each}
              <span class="rating-value">{recipe.rating.toFixed(1)}</span>
            </div>
          {/if}

          <div class="meta-cards">
            <div class="meta-card">
              <span class="meta-icon">👥</span>
              <span class="meta-value">{recipe.servings || '-'}</span>
              <span class="meta-label">人前</span>
            </div>
            <div class="meta-card">
              <span class="meta-icon">⏱️</span>
              <span class="meta-value">{getTotalTime() || '-'}</span>
              <span class="meta-label">分</span>
            </div>
            <div class="meta-card">
              <span class="meta-icon">{getSourceIcon(recipe.source_type)}</span>
              <span class="meta-value meta-value--small">{recipe.source_type}</span>
              <span class="meta-label">ソース</span>
            </div>
          </div>

          {#if recipe.tags && recipe.tags.length > 0}
            <div class="tags">
              {#each recipe.tags as tag}
                <span class="tag">{tag.name}</span>
              {/each}
            </div>
          {/if}

          {#if recipe.steps && recipe.steps.length > 0}
            <button class="cooking-mode-btn" on:click={startCookingMode}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
              調理モードを開始
            </button>
          {/if}
        </div>
      </div>

      {#if recipe.description}
        <section class="description-section">
          <h2>📖 説明</h2>
          <p>{recipe.description}</p>
        </section>
      {/if}

      {#if recipe.source_url}
        <div class="source-url">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
            <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
          </svg>
          出典: <a href={recipe.source_url} target="_blank" rel="noopener noreferrer">
            {recipe.source_url}
          </a>
        </div>
      {/if}

      <div class="two-column">
        <section class="ingredients">
          <h2>🥗 材料 ({recipe.ingredients?.length || 0}品)</h2>
          {#if recipe.ingredients && recipe.ingredients.length > 0}
            <ul>
              {#each recipe.ingredients as ingredient, index}
                <li class:checked={checkedIngredients.has(index)}>
                  <label class="ingredient-check">
                    <input type="checkbox" checked={checkedIngredients.has(index)} on:change={() => toggleIngredient(index)} />
                    <span class="checkmark"></span>
                    <span class="ingredient-name">{ingredient.name}</span>
                    {#if ingredient.amount || ingredient.unit}
                      <span class="ingredient-amount">
                        {ingredient.amount || ''}{ingredient.unit || ''}
                      </span>
                    {/if}
                    {#if ingredient.note}
                      <span class="ingredient-note">({ingredient.note})</span>
                    {/if}
                  </label>
                </li>
              {/each}
            </ul>
          {:else}
            <p class="empty">材料が登録されていません</p>
          {/if}
        </section>

        <section class="steps">
          <h2>👩‍🍳 手順</h2>
          {#if recipe.steps && recipe.steps.length > 0}
            <ol>
              {#each recipe.steps as step, index}
                <li>
                  <div class="step-marker">{index + 1}</div>
                  <div class="step-content">{step.description}</div>
                </li>
              {/each}
            </ol>
          {:else}
            <p class="empty">手順が登録されていません</p>
          {/if}
        </section>
      </div>

      <div class="dates">
        <span>作成: {formatDate(recipe.created_at)}</span>
        <span>更新: {formatDate(recipe.updated_at)}</span>
      </div>
    </div>
  </div>
{/if}

<!-- Image Modal -->
{#if showImageModal}
  <div class="image-modal" on:click={handleModalClick} on:keypress={(e) => e.key === 'Escape' && closeImageModal()}>
    <div class="modal-content">
      <button class="modal-close" on:click={closeImageModal} aria-label="閉じる">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
      <img src={getRecipeImageUrl()} alt={recipe.title} />
      <div class="modal-caption">{recipe.title}</div>
    </div>
  </div>
{/if}

<style>
  /* Cooking Mode Styles */
  .cooking-mode {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    flex-direction: column;
    z-index: 1000;
  }

  .cooking-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 2rem;
    background: rgba(0, 0, 0, 0.1);
  }

  .cooking-header h2 {
    margin: 0;
    font-size: 1.25rem;
  }

  .exit-btn {
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 8px;
    color: white;
    cursor: pointer;
  }

  .cooking-progress {
    padding: 1rem 2rem;
    text-align: center;
  }

  .progress-bar {
    height: 8px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .progress-fill {
    height: 100%;
    background: white;
    border-radius: 4px;
    transition: width 0.3s;
  }

  .progress-text {
    font-size: 0.9rem;
    opacity: 0.9;
  }

  .cooking-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
  }

  .step-number {
    width: 80px;
    height: 80px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 2rem;
  }

  .step-text {
    font-size: 1.5rem;
    line-height: 1.6;
    max-width: 600px;
  }

  .cooking-nav {
    display: flex;
    justify-content: center;
    gap: 1rem;
    padding: 2rem;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 12px;
    color: white;
    font-size: 1.1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .nav-btn:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.3);
  }

  .nav-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .nav-btn--next, .nav-btn--complete {
    background: white;
    color: #667eea;
  }

  .nav-btn--complete {
    background: #28a745;
    color: white;
  }

  /* Normal Detail Styles */
  .recipe-detail {
    max-width: 1000px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }

  .back-btn, .action-btn, .edit-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .back-btn:hover, .action-btn:hover {
    background: #f5f5f5;
  }

  .edit-btn {
    background: #667eea;
    color: white;
    border-color: #667eea;
  }

  .edit-btn:hover {
    background: #5a6fd6;
  }

  .content {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  }

  .hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    padding: 2rem;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  }

  .hero-image {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    aspect-ratio: 4/3;
  }

  .hero-image.clickable {
    cursor: pointer;
  }

  .hero-image.clickable:hover .image-overlay {
    opacity: 1;
  }

  .hero-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: opacity 0.3s;
    opacity: 0;
  }

  .hero-image img.loaded {
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

  .image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s;
    color: white;
  }

  .favorite-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 48px;
    height: 48px;
    background: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.2s;
    color: #ccc;
  }

  .favorite-btn:hover {
    transform: scale(1.1);
  }

  .favorite-btn.active {
    color: #ff6b6b;
  }

  .hero-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .hero-content h1 {
    margin: 0 0 1rem 0;
    font-size: 1.75rem;
    color: #1a1a2e;
    line-height: 1.3;
  }

  .rating {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    margin-bottom: 1.5rem;
  }

  .star {
    font-size: 1.25rem;
    color: #ddd;
  }

  .star--filled {
    color: #ffc107;
  }

  .rating-value {
    margin-left: 0.5rem;
    font-size: 1rem;
    color: #666;
    font-weight: 600;
  }

  .meta-cards {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .meta-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 1.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .meta-icon {
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
  }

  .meta-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #333;
  }

  .meta-value--small {
    font-size: 0.9rem;
  }

  .meta-label {
    font-size: 0.75rem;
    color: #888;
  }

  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .tag {
    padding: 0.4rem 0.75rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 20px;
    font-size: 0.8rem;
  }

  .cooking-mode-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.875rem 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .cooking-mode-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  .description-section {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid #f0f0f0;
  }

  .description-section h2 {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    color: #333;
  }

  .description-section p {
    margin: 0;
    color: #555;
    line-height: 1.8;
  }

  .source-url {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    background: #f8f9fa;
    font-size: 0.85rem;
    color: #666;
  }

  .source-url a {
    color: #667eea;
    text-decoration: none;
  }

  .source-url a:hover {
    text-decoration: underline;
  }

  .two-column {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    border-top: 1px solid #f0f0f0;
  }

  .ingredients, .steps {
    padding: 2rem;
  }

  .ingredients {
    background: #fafbfc;
    border-right: 1px solid #f0f0f0;
  }

  .ingredients h2, .steps h2 {
    margin: 0 0 1.5rem 0;
    font-size: 1.1rem;
    color: #333;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .ingredients ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .ingredients li {
    padding: 0.75rem 0;
    border-bottom: 1px solid #eee;
  }

  .ingredients li:last-child {
    border-bottom: none;
  }

  .ingredients li.checked .ingredient-name,
  .ingredients li.checked .ingredient-amount {
    text-decoration: line-through;
    opacity: 0.5;
  }

  .ingredient-check {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    user-select: none;
  }

  .ingredient-check input {
    display: none;
  }

  .checkmark {
    width: 22px;
    height: 22px;
    border: 2px solid #ddd;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .ingredient-check input:checked + .checkmark {
    background: #667eea;
    border-color: #667eea;
  }

  .ingredient-check input:checked + .checkmark::after {
    content: '✓';
    color: white;
    font-size: 14px;
  }

  .ingredient-name {
    font-weight: 500;
    color: #333;
  }

  .ingredient-amount {
    color: #666;
    margin-left: auto;
  }

  .ingredient-note {
    color: #888;
    font-size: 0.85rem;
  }

  .steps ol {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .steps li {
    display: flex;
    gap: 1rem;
    padding: 1rem 0;
    border-bottom: 1px solid #f0f0f0;
  }

  .steps li:last-child {
    border-bottom: none;
  }

  .step-marker {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    flex-shrink: 0;
  }

  .step-content {
    flex: 1;
    line-height: 1.7;
    color: #444;
    padding-top: 0.25rem;
  }

  .empty {
    color: #888;
    font-style: italic;
    padding: 1rem 0;
  }

  .dates {
    display: flex;
    gap: 2rem;
    padding: 1rem 2rem;
    background: #f8f9fa;
    font-size: 0.85rem;
    color: #888;
  }

  /* Image Modal */
  .image-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    padding: 2rem;
  }

  .modal-content {
    position: relative;
    max-width: 90vw;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .modal-content img {
    max-width: 100%;
    max-height: calc(90vh - 4rem);
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  }

  .modal-close {
    position: absolute;
    top: -3rem;
    right: 0;
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 50%;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
  }

  .modal-close:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  .modal-caption {
    margin-top: 1rem;
    color: white;
    font-size: 1rem;
    text-align: center;
  }

  /* Print styles */
  @media print {
    .header, .cooking-mode-btn, .favorite-btn, .image-modal {
      display: none;
    }

    .content {
      box-shadow: none;
    }
  }

  /* Responsive */
  @media (max-width: 768px) {
    .header {
      flex-wrap: wrap;
      gap: 0.75rem;
    }

    .hero {
      grid-template-columns: 1fr;
      padding: 1rem;
    }

    .hero-content h1 {
      font-size: 1.35rem;
    }

    .two-column {
      grid-template-columns: 1fr;
    }

    .ingredients {
      border-right: none;
      border-bottom: 1px solid #f0f0f0;
    }

    .ingredients, .steps {
      padding: 1.25rem;
    }

    .meta-cards {
      flex-wrap: wrap;
    }

    .meta-card {
      padding: 0.75rem 1rem;
    }

    .step-text {
      font-size: 1.25rem;
    }

    .description-section {
      padding: 1rem 1.25rem;
    }

    .source-url {
      padding: 0.75rem 1.25rem;
    }

    .dates {
      padding: 0.75rem 1.25rem;
      flex-direction: column;
      gap: 0.5rem;
    }
  }

  @media (max-width: 480px) {
    .cooking-header {
      padding: 0.75rem 1rem;
    }

    .cooking-header h2 {
      font-size: 1rem;
    }

    .cooking-content {
      padding: 1.5rem 1rem;
    }

    .step-number {
      width: 60px;
      height: 60px;
      font-size: 2rem;
    }

    .step-text {
      font-size: 1.1rem;
    }

    .cooking-nav {
      padding: 1rem;
    }

    .nav-btn {
      padding: 0.75rem 1.25rem;
      font-size: 0.95rem;
    }

    .action-btn {
      padding: 0.5rem;
    }

    .action-btn svg + span,
    .edit-btn svg + span {
      display: none;
    }
  }
</style>

# 画像表示クイックガイド

## 概要

レシピ画像を表示する際の基本パターンとベストプラクティスをまとめたクイックガイドです。

## 基本パターン

### 1. 画像URLを取得する

```javascript
import { getImageUrl } from '../services/api.js';

const imageUrl = getImageUrl(recipe);
// image_path優先 → image_url → null
```

### 2. 画像を表示する（基本）

```svelte
<script>
  import { getImageUrl } from '../services/api.js';

  export let recipe;
  const placeholderImage = 'data:image/svg+xml,...';

  function getRecipeImageUrl() {
    return getImageUrl(recipe) || placeholderImage;
  }
</script>

<img
  src={getRecipeImageUrl()}
  alt={recipe.title}
  loading="lazy"
/>
```

### 3. 画像を表示する（フルバージョン）

```svelte
<script>
  import { getImageUrl } from '../services/api.js';

  export let recipe;
  let imageLoaded = false;
  let imageError = false;

  const placeholderImage = 'data:image/svg+xml,...';

  function getRecipeImageUrl() {
    return getImageUrl(recipe) || placeholderImage;
  }

  function handleImageLoad() {
    imageLoaded = true;
    imageError = false;
  }

  function handleImageError() {
    imageError = true;
    imageLoaded = true;
  }
</script>

<div class="image-container">
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

<style>
  .image-container {
    position: relative;
    aspect-ratio: 16 / 9;
    overflow: hidden;
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
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: opacity 0.3s;
    opacity: 0;
  }

  img.loaded {
    opacity: 1;
  }
</style>
```

## ユースケース別実装

### カード表示（グリッド）

```svelte
<div class="card-image">
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

<style>
  .card-image {
    aspect-ratio: 16 / 10;
    overflow: hidden;
    cursor: pointer;
  }

  .card-image img {
    transition: transform 0.3s;
  }

  .card-image:hover img {
    transform: scale(1.05);
  }
</style>
```

### リスト表示

```svelte
<div class="list-image">
  <img
    src={getRecipeImageUrl()}
    alt={recipe.title}
    loading="lazy"
  />
</div>

<style>
  .list-image {
    width: 160px;
    min-width: 160px;
    height: 120px;
  }

  .list-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
</style>
```

### 詳細ページ（ヒーロー画像）

```svelte
<div class="hero-image" on:click={openImageModal}>
  {#if !imageLoaded}
    <div class="image-skeleton"></div>
  {/if}
  <img
    src={getRecipeImageUrl()}
    alt={recipe.title}
    class:loaded={imageLoaded}
    on:load={handleImageLoad}
  />
  <div class="image-overlay">
    <svg><!-- 拡大アイコン --></svg>
  </div>
</div>

<style>
  .hero-image {
    position: relative;
    aspect-ratio: 4 / 3;
    cursor: pointer;
  }

  .image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    opacity: 0;
    transition: opacity 0.3s;
  }

  .hero-image:hover .image-overlay {
    opacity: 1;
  }
</style>
```

### モーダル拡大表示

```svelte
<script>
  let showImageModal = false;

  function openImageModal() {
    if (getImageUrl(recipe)) {
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
</script>

{#if showImageModal}
  <div class="image-modal" on:click={handleModalClick}>
    <div class="modal-content">
      <button class="modal-close" on:click={closeImageModal}>
        ×
      </button>
      <img src={getRecipeImageUrl()} alt={recipe.title} />
      <div class="modal-caption">{recipe.title}</div>
    </div>
  </div>
{/if}

<style>
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
  }

  .modal-content img {
    max-width: 90vw;
    max-height: 90vh;
    object-fit: contain;
  }
</style>
```

## レスポンシブ対応

### モバイルファースト

```css
/* モバイル */
.recipe-image {
  width: 100%;
  aspect-ratio: 1 / 1;
}

/* タブレット */
@media (min-width: 768px) {
  .recipe-image {
    aspect-ratio: 16 / 9;
  }
}

/* デスクトップ */
@media (min-width: 1024px) {
  .recipe-image {
    aspect-ratio: 4 / 3;
  }
}
```

## パフォーマンス最適化

### 1. Lazy Loading（必須）

```html
<img loading="lazy" src="..." alt="..." />
```

### 2. アスペクト比の維持（推奨）

```css
.image-container {
  aspect-ratio: 16 / 9; /* レイアウトシフト防止 */
}
```

### 3. スケルトンローディング（推奨）

```svelte
{#if !imageLoaded}
  <div class="image-skeleton"></div>
{/if}
```

### 4. トランジション最適化

```css
img {
  /* GPU加速 */
  transform: translateZ(0);
  will-change: transform, opacity;
}
```

## アクセシビリティ

### 1. Alt属性（必須）

```html
<img alt="チョコレートチップクッキーのレシピ" src="..." />
```

### 2. キーボード操作（推奨）

```svelte
<div
  role="button"
  tabindex="0"
  on:click={openModal}
  on:keypress={(e) => e.key === 'Enter' && openModal()}
>
  <img ... />
</div>
```

### 3. ARIAラベル（推奨）

```html
<button aria-label="画像を拡大表示">
  <img ... />
</button>
```

## よくある問題と解決方法

### 問題1: 画像が表示されない

**原因**: APIエンドポイントが正しくない

**解決**:
```javascript
// api.jsを確認
const API_BASE = "/api/v1";
// 画像パス例: /api/v1/images/recipes/2024/01/image.jpg
```

### 問題2: スケルトンが消えない

**原因**: `on:load`イベントが発火していない

**解決**:
```svelte
<img
  on:load={handleImageLoad}
  on:error={handleImageError}  <!-- エラー時も消す -->
/>
```

### 問題3: レイアウトシフトが発生

**原因**: 画像のアスペクト比が未定義

**解決**:
```css
.image-container {
  aspect-ratio: 16 / 9;  /* 固定アスペクト比 */
  overflow: hidden;
}
```

### 問題4: モバイルで画像が大きすぎる

**原因**: レスポンシブ対応が不足

**解決**:
```css
@media (max-width: 768px) {
  .recipe-image {
    max-height: 300px;
    object-fit: cover;
  }
}
```

## チェックリスト

実装時に確認すべき項目:

- [ ] `getImageUrl()`ヘルパーを使用
- [ ] `loading="lazy"`属性を追加
- [ ] `alt`属性を設定（レシピタイトル）
- [ ] スケルトンローディングを実装
- [ ] `on:load`と`on:error`ハンドラを設定
- [ ] アスペクト比を設定（レイアウトシフト防止）
- [ ] レスポンシブ対応（768px、480pxブレークポイント）
- [ ] ホバーエフェクトを追加（オプション）
- [ ] モーダル拡大表示（詳細ページのみ）
- [ ] キーボード操作対応（アクセシビリティ）

## 参考ファイル

- `/frontend/src/services/api.js` - `getImageUrl()`ヘルパー
- `/frontend/src/components/RecipeCard.svelte` - カード表示実装
- `/frontend/src/components/RecipeDetail.svelte` - 詳細ページ実装
- `/frontend/src/styles/recipe-images.css` - 共通スタイル

## 最小限の実装例

最もシンプルな実装:

```svelte
<script>
  import { getImageUrl } from '../services/api.js';
  export let recipe;
</script>

<img
  src={getImageUrl(recipe) || '/placeholder.svg'}
  alt={recipe.title}
  loading="lazy"
  style="width: 100%; aspect-ratio: 16/9; object-fit: cover;"
/>
```

これだけでも:
- 画像が正しく表示される
- プレースホルダーが表示される
- Lazy loadingが有効
- レイアウトシフトが防止される

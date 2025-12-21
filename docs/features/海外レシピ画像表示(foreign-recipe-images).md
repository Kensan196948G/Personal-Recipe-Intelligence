# 海外レシピ画像表示機能

## 概要

海外レシピを含むすべてのレシピに対して、画像表示機能を実装しました。
`image_path`（ローカル画像）と`image_url`（外部URL）の両方に対応し、UX向上のための各種機能を実装しています。

## 実装内容

### 1. 画像URL取得ヘルパー関数

**ファイル**: `/frontend/src/services/api.js`

```javascript
export function getImageUrl(recipe) {
  if (!recipe) return null;

  // Priority: image_path (local/backend) > image_url (external)
  if (recipe.image_path) {
    return `${API_BASE}/images/${recipe.image_path}`;
  }

  if (recipe.image_url) {
    return recipe.image_url;
  }

  return null;
}
```

**優先順位**:
1. `image_path` - バックエンドに保存されたローカル画像
2. `image_url` - 外部URLの画像
3. `null` - 画像なし（プレースホルダー表示）

### 2. RecipeCard.svelte の画像表示

**機能**:
- 画像読み込み中のスケルトン表示
- 画像読み込み完了時のフェードイン効果
- エラーハンドリング（画像読み込み失敗時）
- Lazy loading による遅延読み込み
- グリッド表示・リスト表示の両方に対応

**スケルトンローディング**:
```svelte
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
```

**CSS アニメーション**:
```css
.image-skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}
```

### 3. RecipeDetail.svelte の画像表示

**機能**:
- ヒーロー画像として詳細ページ上部に表示
- 画像クリックでモーダル拡大表示
- 画像ホバー時のオーバーレイ表示（虫眼鏡アイコン）
- お気に入りボタンとの統合
- スケルトンローディング

**画像モーダル**:
```svelte
{#if showImageModal}
  <div class="image-modal" on:click={handleModalClick}>
    <div class="modal-content">
      <button class="modal-close" on:click={closeImageModal}>×</button>
      <img src={getRecipeImageUrl()} alt={recipe.title} />
      <div class="modal-caption">{recipe.title}</div>
    </div>
  </div>
{/if}
```

**モーダル機能**:
- 背景クリックで閉じる
- Escapeキーで閉じる
- 閉じるボタン
- レシピ名キャプション表示
- レスポンシブ対応（最大90vw x 90vh）

### 4. スタイル実装

**レスポンシブ画像**:
```css
.card-image {
  aspect-ratio: 16 / 10;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s, opacity 0.3s;
}
```

**ホバーエフェクト**:
```css
.card--grid:hover .card-image img {
  transform: scale(1.05);
}
```

**画像オーバーレイ**:
```css
.image-overlay {
  position: absolute;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.3s;
}

.hero-image.clickable:hover .image-overlay {
  opacity: 1;
}
```

## 使用方法

### コンポーネントでの使用

```svelte
<script>
  import { getImageUrl } from '../services/api.js';

  export let recipe;

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

### APIレスポンス構造

```json
{
  "id": 1,
  "title": "Chocolate Chip Cookies",
  "image_url": "https://example.com/recipe.jpg",
  "image_path": "recipes/2024/01/chocolate-cookies.jpg",
  "description": "Delicious homemade cookies",
  ...
}
```

## パフォーマンス最適化

### 1. Lazy Loading
- ブラウザネイティブの`loading="lazy"`属性を使用
- ビューポート外の画像は読み込みを遅延

### 2. スケルトンローディング
- 画像読み込み中のレイアウトシフトを防止
- ユーザーに視覚的フィードバックを提供

### 3. 画像最適化
- `object-fit: cover`でアスペクト比維持
- レスポンシブ対応（モバイル・タブレット・デスクトップ）

### 4. トランジション効果
- スムーズなフェードイン（0.3s）
- GPU加速のtransform使用

## エラーハンドリング

### 画像読み込みエラー

```javascript
function handleImageError() {
  imageError = true;
  imageLoaded = true;
  // プレースホルダー画像を表示
}
```

### プレースホルダー画像

SVG形式のインラインプレースホルダーを使用:
```javascript
const placeholderImage = 'data:image/svg+xml,%3Csvg...%3E...%3C/svg%3E';
```

## アクセシビリティ

### 1. Alt属性
- すべての画像に適切な`alt`属性を設定
- レシピタイトルを使用

### 2. キーボード操作
- 画像モーダル: Escapeキーで閉じる
- 画像拡大: Enterキーでモーダル表示

### 3. スクリーンリーダー
- ARIA属性による適切なラベリング
- `role="button"`でクリック可能エリアを明示

### 4. フォーカス管理
- `tabindex="0"`でキーボードフォーカス可能
- フォーカス時の視覚的フィードバック

## モバイル対応

### レスポンシブブレークポイント

**768px以下（タブレット）**:
```css
@media (max-width: 768px) {
  .list-image {
    width: 100px;
    min-width: 100px;
  }
}
```

**480px以下（モバイル）**:
```css
@media (max-width: 480px) {
  .recipes--grid {
    grid-template-columns: 1fr;
  }
}
```

### タッチ操作
- タップで画像拡大
- スワイプでモーダル閉じる（背景タップ）

## ブラウザ対応

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### フォールバック
- CSS Grid非対応ブラウザ: flexboxフォールバック
- Lazy loading非対応: 即座に読み込み
- aspect-ratio非対応: padding-topフォールバック

## 今後の拡張予定

### 1. 画像最適化
- WebP対応
- レスポンシブ画像（srcset）
- 画像圧縮

### 2. 画像編集機能
- トリミング
- フィルター適用
- 回転・反転

### 3. 画像アップロード
- ドラッグ&ドロップ
- クリップボードから貼り付け
- 複数画像対応

### 4. ギャラリー機能
- 複数画像のスライドショー
- サムネイルナビゲーション
- ズーム・パン操作

## トラブルシューティング

### 画像が表示されない

1. **APIエンドポイント確認**
   ```bash
   curl http://localhost:8000/api/v1/images/{image_path}
   ```

2. **CORS設定確認**
   - バックエンドのCORS設定を確認
   - 外部URLの場合、CORS許可を確認

3. **画像パス確認**
   ```javascript
   console.log(getImageUrl(recipe));
   ```

### スケルトンが表示され続ける

1. **画像読み込みイベント確認**
   - `on:load`ハンドラが正しく設定されているか
   - ブラウザコンソールでエラー確認

2. **ネットワーク確認**
   - DevToolsのNetworkタブで画像リクエスト確認

### モーダルが開かない

1. **画像URL確認**
   ```javascript
   // getImageUrl(recipe)がnullを返している可能性
   if (getImageUrl(recipe)) {
     showImageModal = true;
   }
   ```

2. **イベントハンドラ確認**
   - `on:click`と`on:keypress`が正しく設定されているか

## 参考リンク

- [MDN - Lazy Loading](https://developer.mozilla.org/en-US/docs/Web/Performance/Lazy_loading)
- [Web.dev - Image Performance](https://web.dev/fast/#optimize-your-images)
- [WCAG 2.1 - Images](https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html)

## 変更履歴

- 2025-01-XX: 初版作成
- 海外レシピ画像表示機能実装
- モーダル拡大表示追加
- スケルトンローディング実装
- レスポンシブ対応完了

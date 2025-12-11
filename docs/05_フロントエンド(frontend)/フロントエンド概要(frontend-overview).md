# フロントエンド概要 (Frontend Overview)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のフロントエンド技術スタックと構成について説明する。

## 2. 技術スタック

### 2.1 主要技術

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Svelte | 4.x | UIフレームワーク |
| Vite | 5.x | ビルドツール |
| Bun | 最新 | パッケージマネージャ・ランタイム |

### 2.2 選定理由

**Svelte**
- コンパイル時最適化による軽量バンドル
- シンプルな構文
- 仮想DOMなしの高速レンダリング
- 少ない定型コード

**Vite**
- 高速な開発サーバー
- HMR (Hot Module Replacement)
- 最適化されたビルド

**Bun**
- 高速なパッケージインストール
- TypeScript ネイティブサポート
- Node.js 互換

## 3. ディレクトリ構成

```
frontend/
├── public/               # 静的ファイル
│   ├── favicon.ico
│   └── images/
├── src/
│   ├── components/       # UIコンポーネント
│   │   ├── common/       # 共通コンポーネント
│   │   │   ├── Button.svelte
│   │   │   ├── Input.svelte
│   │   │   ├── Modal.svelte
│   │   │   └── Loading.svelte
│   │   ├── recipe/       # レシピ関連
│   │   │   ├── RecipeCard.svelte
│   │   │   ├── RecipeForm.svelte
│   │   │   └── RecipeDetail.svelte
│   │   └── layout/       # レイアウト
│   │       ├── Header.svelte
│   │       ├── Footer.svelte
│   │       └── Sidebar.svelte
│   ├── pages/            # ページコンポーネント
│   │   ├── Home.svelte
│   │   ├── RecipeList.svelte
│   │   ├── RecipeDetail.svelte
│   │   ├── RecipeCreate.svelte
│   │   ├── RecipeEdit.svelte
│   │   └── Import.svelte
│   ├── stores/           # 状態管理
│   │   ├── recipes.js
│   │   ├── tags.js
│   │   └── ui.js
│   ├── lib/              # ユーティリティ
│   │   ├── api.js        # API通信
│   │   ├── utils.js      # ヘルパー関数
│   │   └── constants.js  # 定数
│   ├── styles/           # グローバルスタイル
│   │   ├── global.css
│   │   └── variables.css
│   ├── App.svelte        # ルートコンポーネント
│   └── main.js           # エントリポイント
├── index.html
├── package.json
├── vite.config.js
└── jsconfig.json
```

## 4. 開発環境セットアップ

### 4.1 必要条件

- Bun 1.0+
- Node.js 20+ (互換性のため)

### 4.2 セットアップ手順

```bash
# プロジェクトディレクトリに移動
cd frontend

# 依存関係インストール
bun install

# 開発サーバー起動
bun run dev

# ビルド
bun run build

# プレビュー
bun run preview
```

## 5. ビルド設定

### 5.1 vite.config.js

```javascript
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['svelte']
        }
      }
    }
  }
})
```

### 5.2 package.json スクリプト

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src/**/*.{js,svelte}",
    "format": "prettier --write src/**/*.{js,svelte,css}",
    "test": "bun test"
  }
}
```

## 6. コーディング規約

### 6.1 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| コンポーネント | PascalCase | `RecipeCard.svelte` |
| 関数 | camelCase | `fetchRecipes()` |
| 変数 | camelCase | `recipeList` |
| 定数 | UPPER_SNAKE | `API_BASE_URL` |
| CSS クラス | kebab-case | `.recipe-card` |

### 6.2 コンポーネント構造

```svelte
<script>
  // 1. インポート
  import { onMount } from 'svelte';
  import { recipes } from '../stores/recipes.js';

  // 2. Props
  export let id;
  export let title = '';

  // 3. リアクティブ変数
  $: formattedTitle = title.toUpperCase();

  // 4. ローカル変数
  let isLoading = false;

  // 5. ライフサイクル
  onMount(() => {
    // 初期化処理
  });

  // 6. 関数
  function handleClick() {
    // イベント処理
  }
</script>

<!-- テンプレート -->
<div class="component">
  {#if isLoading}
    <Loading />
  {:else}
    <h1>{formattedTitle}</h1>
  {/if}
</div>

<style>
  /* スコープ付きスタイル */
  .component {
    /* ... */
  }
</style>
```

## 7. 状態管理

### 7.1 Svelte Store

```javascript
// stores/recipes.js
import { writable, derived } from 'svelte/store';

// 基本のStore
export const recipes = writable([]);

// 派生Store
export const recipeCount = derived(recipes, $recipes => $recipes.length);

// カスタムStore
function createRecipeStore() {
  const { subscribe, set, update } = writable([]);

  return {
    subscribe,
    fetch: async () => {
      const response = await fetch('/api/v1/recipes');
      const data = await response.json();
      set(data.data.items);
    },
    add: (recipe) => update(recipes => [...recipes, recipe]),
    remove: (id) => update(recipes => recipes.filter(r => r.id !== id))
  };
}

export const recipeStore = createRecipeStore();
```

## 8. API通信

### 8.1 API クライアント

```javascript
// lib/api.js
const API_BASE = '/api/v1';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  const response = await fetch(url, config);
  const data = await response.json();

  if (data.status === 'error') {
    throw new Error(data.error.message);
  }

  return data;
}

export const api = {
  get: (endpoint) => request(endpoint),
  post: (endpoint, body) => request(endpoint, {
    method: 'POST',
    body: JSON.stringify(body)
  }),
  put: (endpoint, body) => request(endpoint, {
    method: 'PUT',
    body: JSON.stringify(body)
  }),
  delete: (endpoint) => request(endpoint, { method: 'DELETE' })
};
```

## 9. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

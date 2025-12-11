# スタイルガイド (Style Guide)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のフロントエンドスタイルガイドを定義する。

## 2. デザイントークン

### 2.1 カラーパレット

```css
/* variables.css */
:root {
  /* Primary */
  --color-primary: #FF6B35;
  --color-primary-dark: #E55A2B;
  --color-primary-light: #FF8A5C;

  /* Secondary */
  --color-secondary: #4CAF50;
  --color-secondary-dark: #388E3C;
  --color-secondary-light: #81C784;

  /* Neutral */
  --color-white: #FFFFFF;
  --color-gray-50: #FAFAFA;
  --color-gray-100: #F5F5F5;
  --color-gray-200: #E0E0E0;
  --color-gray-300: #BDBDBD;
  --color-gray-400: #9E9E9E;
  --color-gray-500: #757575;
  --color-gray-600: #666666;
  --color-gray-700: #424242;
  --color-gray-800: #333333;
  --color-gray-900: #212121;
  --color-black: #000000;

  /* Semantic */
  --color-success: #4CAF50;
  --color-warning: #FF9800;
  --color-error: #F44336;
  --color-info: #2196F3;

  /* Background */
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F5F5F5;
  --color-bg-tertiary: #E0E0E0;

  /* Text */
  --color-text-primary: #333333;
  --color-text-secondary: #666666;
  --color-text-tertiary: #999999;
  --color-text-inverse: #FFFFFF;

  /* Border */
  --color-border: #E0E0E0;
  --color-border-focus: #FF6B35;
}
```

### 2.2 タイポグラフィ

```css
:root {
  /* Font Family */
  --font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: 'SF Mono', 'Monaco', 'Consolas', monospace;

  /* Font Size */
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 28px;
  --font-size-4xl: 32px;

  /* Font Weight */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Line Height */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

### 2.3 スペーシング

```css
:root {
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  --spacing-3xl: 64px;
}
```

### 2.4 シャドウ

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.15);
  --shadow-xl: 0 8px 32px rgba(0, 0, 0, 0.2);
}
```

### 2.5 ボーダー

```css
:root {
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  --border-radius-full: 9999px;

  --border-width: 1px;
  --border-width-thick: 2px;
}
```

### 2.6 トランジション

```css
:root {
  --transition-fast: 0.15s ease;
  --transition-normal: 0.2s ease;
  --transition-slow: 0.3s ease;
}
```

## 3. グローバルスタイル

### 3.1 リセット

```css
/* global.css */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  line-height: var(--line-height-normal);
  color: var(--color-text-primary);
  background: var(--color-bg-secondary);
}

a {
  color: var(--color-primary);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

button {
  font-family: inherit;
  font-size: inherit;
  cursor: pointer;
}

img {
  max-width: 100%;
  height: auto;
}

ul, ol {
  list-style: none;
}
```

### 3.2 タイポグラフィクラス

```css
.heading-1 {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
}

.heading-2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
}

.heading-3 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
}

.body-large {
  font-size: var(--font-size-lg);
  line-height: var(--line-height-normal);
}

.body-normal {
  font-size: var(--font-size-md);
  line-height: var(--line-height-normal);
}

.body-small {
  font-size: var(--font-size-sm);
  line-height: var(--line-height-normal);
}

.caption {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}
```

## 4. レイアウト

### 4.1 コンテナ

```css
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.container-sm { max-width: 640px; }
.container-md { max-width: 768px; }
.container-lg { max-width: 1024px; }
.container-xl { max-width: 1280px; }
```

### 4.2 グリッド

```css
.grid {
  display: grid;
  gap: var(--spacing-md);
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* レスポンシブ */
@media (max-width: 640px) {
  .grid-cols-2, .grid-cols-3, .grid-cols-4 {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 641px) and (max-width: 768px) {
  .grid-cols-3, .grid-cols-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .grid-cols-4 {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 4.3 Flexbox

```css
.flex { display: flex; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }

.items-start { align-items: flex-start; }
.items-center { align-items: center; }
.items-end { align-items: flex-end; }

.justify-start { justify-content: flex-start; }
.justify-center { justify-content: center; }
.justify-end { justify-content: flex-end; }
.justify-between { justify-content: space-between; }

.gap-sm { gap: var(--spacing-sm); }
.gap-md { gap: var(--spacing-md); }
.gap-lg { gap: var(--spacing-lg); }
```

## 5. コンポーネントスタイル

### 5.1 ボタン

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  transition: var(--transition-normal);
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### 5.2 フォーム要素

```css
.input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-md);
  transition: var(--transition-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2);
}

.input:invalid {
  border-color: var(--color-error);
}

.label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.helper-text {
  margin-top: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.error-text {
  margin-top: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-error);
}
```

### 5.3 カード

```css
.card {
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.card-header {
  padding: var(--spacing-md);
  border-bottom: var(--border-width) solid var(--color-border);
}

.card-body {
  padding: var(--spacing-md);
}

.card-footer {
  padding: var(--spacing-md);
  border-top: var(--border-width) solid var(--color-border);
}
```

## 6. レスポンシブブレークポイント

```css
/* モバイル優先 */
/* sm: 640px */
/* md: 768px */
/* lg: 1024px */
/* xl: 1280px */

@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

## 7. アクセシビリティ

### 7.1 フォーカス表示

```css
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* キーボードフォーカスのみ表示 */
:focus:not(:focus-visible) {
  outline: none;
}
```

### 7.2 スクリーンリーダー用

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## 8. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

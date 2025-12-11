# E2E テストガイド

Personal Recipe Intelligence の E2E テスト（Playwright）に関するドキュメント。

## セットアップ

### 依存関係のインストール

```bash
cd frontend
bun install
bun run playwright:install
```

SSH + Ubuntu CLI 環境の場合、依存パッケージも追加でインストール：

```bash
bun run playwright:install-deps
```

## テスト実行

### 基本実行

```bash
# すべてのブラウザでテスト実行
bun run e2e

# ヘッドレスモードを無効化（GUIが必要）
bun run e2e:headed

# デバッグモード
bun run e2e:debug

# UI モード（インタラクティブ）
bun run e2e:ui
```

### ブラウザ別実行

```bash
# Chromium のみ
bun run e2e:chromium

# Firefox のみ
bun run e2e:firefox

# WebKit のみ
bun run e2e:webkit

# モバイルブラウザ
bun run e2e:mobile
```

### レポート表示

```bash
bun run e2e:report
```

## テストファイル構成

```
frontend/e2e/
├── fixtures.js           # 共通フィクスチャ・ページオブジェクト・テストデータ
├── home.test.js          # ホームページのテスト
├── add-recipe.test.js    # レシピ追加ページのテスト
├── recipe-detail.test.js # レシピ詳細ページのテスト
└── README.md             # このファイル
```

## ページオブジェクトパターン

### HomePage

```javascript
import { test } from './fixtures.js';

test('ホームページのテスト', async ({ homePage }) => {
  await homePage.goto();
  await homePage.search('カレー');
  const count = await homePage.getRecipeCount();
});
```

### AddRecipePage

```javascript
import { test, testRecipes } from './fixtures.js';

test('レシピ追加のテスト', async ({ addRecipePage }) => {
  await addRecipePage.goto();
  await addRecipePage.fillRecipeForm(testRecipes.basic);
  await addRecipePage.submit();
});
```

### RecipeDetailPage

```javascript
import { test } from './fixtures.js';

test('レシピ詳細のテスト', async ({ recipeDetailPage }) => {
  await recipeDetailPage.goto(1);
  const title = await recipeDetailPage.getTitle();
  await recipeDetailPage.edit();
});
```

## テストデータ

共通のテストデータは `fixtures.js` に定義：

```javascript
import { testRecipes, searchQueries, mockApiResponses } from './fixtures.js';

// レシピデータ
testRecipes.basic
testRecipes.withUrl
testRecipes.minimal
testRecipes.japanese

// 検索クエリ
searchQueries.basic
searchQueries.tag
searchQueries.ingredient

// API モックレスポンス
mockApiResponses.recipeList
mockApiResponses.recipeDetail
mockApiResponses.parseUrlSuccess
```

## API モック化

テストで API をモック化する例：

```javascript
import { test, mockApiRoute, mockApiResponses } from './fixtures.js';

test('API モックのテスト', async ({ page }) => {
  await mockApiRoute(page, '**/api/v1/recipes', mockApiResponses.recipeList);
  await page.goto('/');
});
```

## CI/CD 環境

GitHub Actions で自動実行される設定：

- `.github/workflows/e2e.yml`
- すべてのブラウザで並列実行
- モバイルテストも含む
- 失敗時はスクリーンショット・動画を保存

### CI でのみ実行

```bash
CI=true bun run e2e
```

## ベストプラクティス

### 1. data-testid 属性を使用

```jsx
<button data-testid="submit-button">送信</button>
```

```javascript
const button = page.locator('[data-testid="submit-button"]');
```

### 2. 明示的な待機を避ける

```javascript
// ❌ 悪い例
await page.waitForTimeout(1000);

// ✅ 良い例
await expect(page.locator('[data-testid="element"]')).toBeVisible();
```

### 3. ページオブジェクトを活用

```javascript
// ❌ 悪い例
await page.locator('[data-testid="title-input"]').fill('テスト');
await page.locator('[data-testid="submit-button"]').click();

// ✅ 良い例
await addRecipePage.fillRecipeForm({ title: 'テスト' });
await addRecipePage.submit();
```

### 4. テストデータをクリーンアップ

```javascript
test('テスト', async ({ cleanDatabase }) => {
  // cleanDatabase フィクスチャが自動的にクリーンアップ
});
```

### 5. スクリーンショットを活用

```javascript
// 失敗時のみ（設定済み）
screenshot: 'only-on-failure'

// 手動でスクリーンショット
await page.screenshot({ path: 'screenshot.png' });
```

## トラブルシューティング

### SSH 環境でブラウザが起動しない

ヘッドレスモードが有効になっているか確認：

```javascript
// playwright.config.js
use: {
  headless: true,
}
```

### タイムアウトエラー

タイムアウト時間を延長：

```javascript
test('長時間テスト', async ({ page }) => {
  test.setTimeout(60000); // 60秒
});
```

### セレクタが見つからない

デバッグモードで要素を確認：

```bash
bun run e2e:debug
```

または Playwright Inspector を使用：

```javascript
await page.pause();
```

## パフォーマンス目標

- テスト実行時間: 各テスト 10秒以内
- 全体実行時間: 5分以内
- API レスポンス: 200ms 以内（モック化により担保）

## 参考リンク

- [Playwright 公式ドキュメント](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Page Object Model](https://playwright.dev/docs/pom)

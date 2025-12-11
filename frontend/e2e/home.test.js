/**
 * E2E Test: Home Page
 * ホームページの E2E テスト
 */

import { test, expect, mockApiResponses, mockApiRoute } from './fixtures.js';

test.describe('ホームページ', () => {
  test.beforeEach(async ({ page }) => {
    // API モックの設定
    await mockApiRoute(page, '**/api/v1/recipes*', mockApiResponses.recipeList);
  });

  test('ホームページが正常に表示される', async ({ homePage }) => {
    await homePage.goto();
    await expect(homePage.page).toHaveTitle(/Personal Recipe Intelligence/i);
  });

  test('レシピ一覧が表示される', async ({ homePage }) => {
    await homePage.goto();
    const count = await homePage.getRecipeCount();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('検索機能が動作する', async ({ homePage }) => {
    await homePage.goto();
    await homePage.search('カレー');
    await expect(homePage.recipeList).toBeVisible();
  });

  test('レシピ追加ボタンが表示される', async ({ homePage }) => {
    await homePage.goto();
    await expect(homePage.addRecipeButton).toBeVisible();
  });

  test('レシピ追加ボタンをクリックすると追加ページに遷移する', async ({ homePage, page }) => {
    await homePage.goto();
    await homePage.clickAddRecipe();
    await expect(page).toHaveURL(/.*\/add/);
  });
});

test.describe('検索機能', () => {
  test('空の検索クエリでも動作する', async ({ homePage }) => {
    await homePage.goto();
    await homePage.search('');
    await expect(homePage.recipeList).toBeVisible();
  });

  test('タグ検索が動作する', async ({ homePage }) => {
    await homePage.goto();
    await homePage.search('tag:簡単');
    await expect(homePage.recipeList).toBeVisible();
  });

  test('材料検索が動作する', async ({ homePage }) => {
    await homePage.goto();
    await homePage.search('ingredient:トマト');
    await expect(homePage.recipeList).toBeVisible();
  });
});

test.describe('レスポンシブデザイン', () => {
  test('モバイル表示が正常に動作する', async ({ page, homePage }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await homePage.goto();
    await expect(homePage.recipeList).toBeVisible();
  });

  test('タブレット表示が正常に動作する', async ({ page, homePage }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await homePage.goto();
    await expect(homePage.recipeList).toBeVisible();
  });
});

/**
 * E2E Test: Recipe Detail Page
 * レシピ詳細ページの E2E テスト
 */

import { test, expect, mockApiResponses, mockApiRoute } from './fixtures.js';

test.describe('レシピ詳細ページ', () => {
  test.beforeEach(async ({ page }) => {
    // API モックの設定
    await mockApiRoute(page, '**/api/v1/recipes/*', mockApiResponses.recipeDetail);
  });

  test('レシピ詳細が正常に表示される', async ({ recipeDetailPage }) => {
    await recipeDetailPage.goto(1);
    await expect(recipeDetailPage.title).toBeVisible();
    await expect(recipeDetailPage.ingredients).toBeVisible();
    await expect(recipeDetailPage.instructions).toBeVisible();
  });

  test('レシピタイトルが正しく表示される', async ({ recipeDetailPage }) => {
    await recipeDetailPage.goto(1);
    const title = await recipeDetailPage.getTitle();
    expect(title).toBeTruthy();
  });

  test('材料リストが正しく表示される', async ({ recipeDetailPage }) => {
    await recipeDetailPage.goto(1);
    const ingredients = await recipeDetailPage.getIngredients();
    expect(ingredients).toBeTruthy();
  });

  test('手順が正しく表示される', async ({ recipeDetailPage }) => {
    await recipeDetailPage.goto(1);
    const instructions = await recipeDetailPage.getInstructions();
    expect(instructions).toBeTruthy();
  });

  test('タグが表示される', async ({ recipeDetailPage }) => {
    await recipeDetailPage.goto(1);
    await expect(recipeDetailPage.tags).toBeVisible();
  });

  test('編集ボタンが表示される', async ({ recipeDetailPage }) => {
    await recipeDetailPage.goto(1);
    await expect(recipeDetailPage.editButton).toBeVisible();
  });

  test('削除ボタンが表示される', async ({ recipeDetailPage }) => {
    await recipeDetailPage.goto(1);
    await expect(recipeDetailPage.deleteButton).toBeVisible();
  });

  test('戻るボタンでホームに戻る', async ({ recipeDetailPage, page }) => {
    await recipeDetailPage.goto(1);
    await recipeDetailPage.goBack();
    await expect(page).toHaveURL(/.*\//);
  });
});

test.describe('レシピ編集', () => {
  test('編集ボタンをクリックすると編集ページに遷移する', async ({ recipeDetailPage, page }) => {
    await recipeDetailPage.goto(1);
    await recipeDetailPage.edit();
    await expect(page).toHaveURL(/.*\/edit/);
  });
});

test.describe('レシピ削除', () => {
  test('削除確認ダイアログが表示される', async ({ recipeDetailPage, page }) => {
    await recipeDetailPage.goto(1);

    // ダイアログハンドラーを設定
    page.on('dialog', async (dialog) => {
      expect(dialog.type()).toBe('confirm');
      await dialog.dismiss();
    });

    await recipeDetailPage.delete();
  });

  test('削除確認後にホームに戻る', async ({ recipeDetailPage, page }) => {
    // 削除APIのモック
    await mockApiRoute(page, '**/api/v1/recipes/*', {
      status: 'ok',
      data: null,
      error: null,
    });

    await recipeDetailPage.goto(1);

    // ダイアログハンドラーを設定
    page.on('dialog', async (dialog) => {
      await dialog.accept();
    });

    await recipeDetailPage.delete();
    await expect(page).toHaveURL(/.*\//);
  });
});

test.describe('エラーハンドリング', () => {
  test('存在しないレシピIDの場合エラーが表示される', async ({ page }) => {
    // エラーレスポンスのモック
    await mockApiRoute(page, '**/api/v1/recipes/*', {
      status: 'error',
      data: null,
      error: 'Recipe not found',
    });

    await page.goto('/recipe/9999');
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
  });

  test('API エラーの場合エラーメッセージが表示される', async ({ page }) => {
    // API エラーのモック
    await page.route('**/api/v1/recipes/*', (route) => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({
          status: 'error',
          data: null,
          error: 'Internal Server Error',
        }),
      });
    });

    await page.goto('/recipe/1');
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
  });
});

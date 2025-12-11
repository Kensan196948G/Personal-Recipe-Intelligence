/**
 * E2E Test: Add Recipe Page
 * レシピ追加ページの E2E テスト
 */

import { test, expect, testRecipes, mockApiResponses, mockApiRoute } from './fixtures.js';

test.describe('レシピ追加ページ', () => {
  test.beforeEach(async ({ page }) => {
    // API モックの設定
    await mockApiRoute(page, '**/api/v1/recipes', {
      status: 'ok',
      data: { id: 1, ...testRecipes.basic },
      error: null,
    });
  });

  test('レシピ追加ページが正常に表示される', async ({ addRecipePage }) => {
    await addRecipePage.goto();
    await expect(addRecipePage.titleInput).toBeVisible();
    await expect(addRecipePage.ingredientsTextarea).toBeVisible();
    await expect(addRecipePage.instructionsTextarea).toBeVisible();
  });

  test('基本的なレシピを追加できる', async ({ addRecipePage, page }) => {
    await addRecipePage.goto();
    await addRecipePage.fillRecipeForm(testRecipes.basic);
    await addRecipePage.submit();

    // 成功後にホームページにリダイレクトされる
    await expect(page).toHaveURL(/.*\//);
  });

  test('URL付きレシピを追加できる', async ({ addRecipePage, page }) => {
    await addRecipePage.goto();
    await addRecipePage.fillRecipeForm(testRecipes.withUrl);
    await addRecipePage.submit();
    await expect(page).toHaveURL(/.*\//);
  });

  test('最小限の情報でレシピを追加できる', async ({ addRecipePage, page }) => {
    await addRecipePage.goto();
    await addRecipePage.fillRecipeForm(testRecipes.minimal);
    await addRecipePage.submit();
    await expect(page).toHaveURL(/.*\//);
  });

  test('キャンセルボタンでホームに戻る', async ({ addRecipePage, page }) => {
    await addRecipePage.goto();
    await addRecipePage.fillRecipeForm(testRecipes.basic);
    await addRecipePage.cancel();
    await expect(page).toHaveURL(/.*\//);
  });
});

test.describe('URL解析機能', () => {
  test('URLを解析してレシピを自動入力できる', async ({ addRecipePage, page }) => {
    // URL解析APIのモック
    await mockApiRoute(page, '**/api/v1/recipes/parse', mockApiResponses.parseUrlSuccess);

    await addRecipePage.goto();
    await addRecipePage.urlInput.fill('https://cookpad.com/recipe/example');
    await addRecipePage.parseUrl();

    // 解析結果が入力される
    await expect(addRecipePage.titleInput).not.toBeEmpty();
  });

  test('無効なURLの場合エラーメッセージが表示される', async ({ addRecipePage, page }) => {
    // エラーレスポンスのモック
    await mockApiRoute(page, '**/api/v1/recipes/parse', mockApiResponses.parseUrlError);

    await addRecipePage.goto();
    await addRecipePage.urlInput.fill('invalid-url');
    await addRecipePage.parseUrl();

    // エラーメッセージが表示される
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
  });
});

test.describe('フォームバリデーション', () => {
  test('タイトルが空の場合エラーが表示される', async ({ addRecipePage }) => {
    await addRecipePage.goto();
    await addRecipePage.fillRecipeForm({
      title: '',
      ingredients: '材料',
      instructions: '手順',
    });
    await addRecipePage.submit();

    // バリデーションエラーが表示される
    const errorMessage = addRecipePage.page.locator('[data-testid="title-error"]');
    await expect(errorMessage).toBeVisible();
  });

  test('材料が空の場合エラーが表示される', async ({ addRecipePage }) => {
    await addRecipePage.goto();
    await addRecipePage.fillRecipeForm({
      title: 'テストレシピ',
      ingredients: '',
      instructions: '手順',
    });
    await addRecipePage.submit();

    // バリデーションエラーが表示される
    const errorMessage = addRecipePage.page.locator('[data-testid="ingredients-error"]');
    await expect(errorMessage).toBeVisible();
  });

  test('手順が空の場合エラーが表示される', async ({ addRecipePage }) => {
    await addRecipePage.goto();
    await addRecipePage.fillRecipeForm({
      title: 'テストレシピ',
      ingredients: '材料',
      instructions: '',
    });
    await addRecipePage.submit();

    // バリデーションエラーが表示される
    const errorMessage = addRecipePage.page.locator('[data-testid="instructions-error"]');
    await expect(errorMessage).toBeVisible();
  });
});

test.describe('日本語入力', () => {
  test('日本語でレシピを追加できる', async ({ addRecipePage, page }) => {
    await addRecipePage.goto();
    await addRecipePage.fillRecipeForm(testRecipes.japanese);
    await addRecipePage.submit();
    await expect(page).toHaveURL(/.*\//);
  });

  test('日本語のタグを追加できる', async ({ addRecipePage }) => {
    await addRecipePage.goto();
    await addRecipePage.tagsInput.fill('和食,簡単,ヘルシー');
    const value = await addRecipePage.tagsInput.inputValue();
    expect(value).toContain('和食');
  });
});

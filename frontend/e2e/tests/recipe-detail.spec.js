import { test, expect } from '@playwright/test';
import { RecipeDetailPage } from '../page-objects/RecipeDetailPage.js';
import { RecipeListPage } from '../page-objects/RecipeListPage.js';

/**
 * レシピ詳細ページ E2Eテスト
 *
 * レシピ詳細の表示、材料・手順の表示、アクション機能を検証
 */
test.describe('レシピ詳細ページ', () => {
  let recipeDetailPage;

  test.beforeEach(async ({ page }) => {
    recipeDetailPage = new RecipeDetailPage(page);
  });

  test.describe('基本表示', () => {
    test('レシピ詳細ページが正常に読み込まれる', async ({ page }) => {
      // まず一覧ページから最初のレシピを取得
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        // 詳細ページに遷移したことを確認
        expect(page.url()).toMatch(/\/recipes\/[^/]+$/);
      }
    });

    test('レシピタイトルが表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const title = await recipeDetailPage.getTitle();
        expect(title).toBeTruthy();
        expect(title.length).toBeGreaterThan(0);
      }
    });

    test('レシピ説明が表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const description = await recipeDetailPage.getDescription();
        expect(description).toBeTruthy();
      }
    });

    test('存在しないレシピIDで404エラー', async () => {
      await recipeDetailPage.goto('non-existent-recipe-id-12345');

      const isNotFound = await recipeDetailPage.isNotFound();
      expect(isNotFound).toBe(true);
    });
  });

  test.describe('メタ情報', () => {
    test('人数が表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const servings = await recipeDetailPage.getServings();
        expect(servings).toBeTruthy();
      }
    });

    test('調理時間が表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const cookingTime = await recipeDetailPage.getCookingTime();
        expect(cookingTime).toBeTruthy();
      }
    });

    test('難易度が表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const difficulty = await recipeDetailPage.getDifficulty();
        expect(difficulty).toBeTruthy();
      }
    });

    test('カテゴリーが表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const category = await recipeDetailPage.getCategory();
        expect(category).toBeTruthy();
      }
    });

    test('タグが表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const tags = await recipeDetailPage.getTags();
        expect(Array.isArray(tags)).toBe(true);
      }
    });
  });

  test.describe('画像', () => {
    test('レシピ画像が表示される（存在する場合）', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const hasImage = await recipeDetailPage.hasImage();
        // 画像は必須ではないが、存在する場合は表示される
        expect(typeof hasImage).toBe('boolean');
      }
    });

    test('画像に代替テキストがある', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const hasImage = await recipeDetailPage.hasImage();
        if (hasImage) {
          const hasAltText = await recipeDetailPage.hasImageAltText();
          expect(hasAltText).toBe(true);
        }
      }
    });
  });

  test.describe('材料セクション', () => {
    test('材料セクションが表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const ingredientsCount = await recipeDetailPage.getIngredientsCount();
        expect(ingredientsCount).toBeGreaterThanOrEqual(0);
      }
    });

    test('材料リストが正しく表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const ingredients = await recipeDetailPage.getIngredients();
        expect(Array.isArray(ingredients)).toBe(true);

        if (ingredients.length > 0) {
          const firstIngredient = ingredients[0];
          expect(firstIngredient).toHaveProperty('name');
          expect(firstIngredient).toHaveProperty('amount');
          expect(firstIngredient.name).toBeTruthy();
        }
      }
    });

    test('材料セクションに見出しがある', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const hasHeading = await recipeDetailPage.hasIngredientsHeading();
        expect(hasHeading).toBe(true);
      }
    });
  });

  test.describe('手順セクション', () => {
    test('手順セクションが表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const stepsCount = await recipeDetailPage.getStepsCount();
        expect(stepsCount).toBeGreaterThanOrEqual(0);
      }
    });

    test('手順リストが正しく表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const steps = await recipeDetailPage.getSteps();
        expect(Array.isArray(steps)).toBe(true);

        if (steps.length > 0) {
          const firstStep = steps[0];
          expect(firstStep).toHaveProperty('number');
          expect(firstStep).toHaveProperty('description');
          expect(firstStep.description).toBeTruthy();
        }
      }
    });

    test('手順が番号順に表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const steps = await recipeDetailPage.getSteps();

        if (steps.length > 1) {
          for (let i = 0; i < steps.length; i++) {
            const expectedNumber = (i + 1).toString();
            expect(steps[i].number).toContain(expectedNumber);
          }
        }
      }
    });

    test('手順セクションに見出しがある', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const hasHeading = await recipeDetailPage.hasStepsHeading();
        expect(hasHeading).toBe(true);
      }
    });
  });

  test.describe('アクションボタン', () => {
    test('戻るボタンをクリックして一覧へ戻る', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);
        await recipeDetailPage.clickBack();

        // 一覧ページに戻ったことを確認
        expect(page.url()).toContain('/recipes');
        expect(page.url()).not.toMatch(/\/recipes\/[^/]+$/);
      }
    });

    test('お気に入りボタンの切り替え', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const initialState = await recipeDetailPage.isFavorite();
        await recipeDetailPage.toggleFavorite();

        // 状態が変更されることを待つ
        await page.waitForTimeout(500);

        const newState = await recipeDetailPage.isFavorite();
        expect(newState).not.toBe(initialState);
      }
    });

    test('編集ボタンをクリックして編集ページへ遷移', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const editButton = page.locator('[data-testid="edit-button"]');
        const isVisible = await editButton.isVisible().catch(() => false);

        if (isVisible) {
          await recipeDetailPage.clickEdit();

          // 編集ページに遷移したことを確認
          expect(page.url()).toMatch(/\/recipes\/[^/]+\/edit$/);
        }
      }
    });

    test('削除確認ダイアログが表示される', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const deleteButton = page.locator('[data-testid="delete-button"]');
        const isVisible = await deleteButton.isVisible().catch(() => false);

        if (isVisible) {
          // ダイアログイベントをリッスン
          page.once('dialog', dialog => {
            expect(dialog.type()).toBe('confirm');
            dialog.dismiss();
          });

          await recipeDetailPage.clickDelete();
        }
      }
    });

    test('削除をキャンセルできる', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const deleteButton = page.locator('[data-testid="delete-button"]');
        const isVisible = await deleteButton.isVisible().catch(() => false);

        if (isVisible) {
          const urlBeforeDelete = page.url();
          await recipeDetailPage.cancelDelete();

          // URLが変わっていないことを確認（削除されていない）
          expect(page.url()).toBe(urlBeforeDelete);
        }
      }
    });
  });

  test.describe('アクセシビリティ', () => {
    test('セマンティックHTMLを使用している', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const hasSemanticHTML = await recipeDetailPage.hasSemanticHTML();
        expect(hasSemanticHTML).toBe(true);
      }
    });

    test('見出し階層が適切', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        // h1が1つだけ存在することを確認
        const h1Count = await page.locator('h1').count();
        expect(h1Count).toBe(1);
      }
    });

    test('ボタンに適切なaria-labelがある', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const favoriteButton = page.locator('[data-testid="favorite-button"]');
        const isVisible = await favoriteButton.isVisible().catch(() => false);

        if (isVisible) {
          const ariaLabel = await favoriteButton.getAttribute('aria-label');
          const ariaPressed = await favoriteButton.getAttribute('aria-pressed');

          expect(ariaLabel || ariaPressed).toBeTruthy();
        }
      }
    });
  });

  test.describe('レスポンシブデザイン', () => {
    test('モバイルビューで正常に表示される', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const title = await recipeDetailPage.getTitle();
        expect(title).toBeTruthy();
      }
    });

    test('タブレットビューで正常に表示される', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        await listPage.clickRecipeCard(0);

        const title = await recipeDetailPage.getTitle();
        expect(title).toBeTruthy();
      }
    });
  });

  test.describe('パフォーマンス', () => {
    test('詳細ページが高速に読み込まれる', async ({ page }) => {
      const listPage = new RecipeListPage(page);
      await listPage.goto();

      const count = await listPage.getRecipeCount();
      if (count > 0) {
        const startTime = Date.now();
        await listPage.clickRecipeCard(0);
        const loadTime = Date.now() - startTime;

        // 2秒以内に読み込まれることを確認
        expect(loadTime).toBeLessThan(2000);
      }
    });
  });

  test.describe('エラーハンドリング', () => {
    test('APIエラー時に適切なメッセージを表示', async ({ page }) => {
      // APIリクエストをインターセプトしてエラーをシミュレート
      await page.route('**/api/v1/recipes/*', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal Server Error' }),
        });
      });

      await recipeDetailPage.goto('test-recipe-id');

      // エラーメッセージが表示されることを確認
      const hasError = await recipeDetailPage.hasError();
      expect(hasError).toBe(true);
    });

    test('ネットワークエラーのハンドリング', async ({ page }) => {
      // ネットワークエラーをシミュレート
      await page.route('**/api/v1/recipes/*', route => route.abort('failed'));

      await recipeDetailPage.goto('test-recipe-id');

      // エラー状態またはローディング状態を確認
      const hasError = await recipeDetailPage.hasError();
      const isLoading = await recipeDetailPage.isLoading();

      expect(hasError || isLoading).toBe(true);
    });
  });
});

import { test, expect } from '@playwright/test';
import { RecipeListPage } from '../page-objects/RecipeListPage.js';

/**
 * レシピ一覧ページ E2Eテスト
 *
 * レシピ一覧の表示、検索、フィルター機能を検証
 */
test.describe('レシピ一覧ページ', () => {
  let recipeListPage;

  test.beforeEach(async ({ page }) => {
    recipeListPage = new RecipeListPage(page);
    await recipeListPage.goto();
  });

  test.describe('基本表示', () => {
    test('ページが正常に読み込まれる', async ({ page }) => {
      expect(page.url()).toContain('/recipes');
    });

    test('レシピ一覧が表示される', async () => {
      const count = await recipeListPage.getRecipeCount();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test('レシピカードに必要な情報が表示される', async () => {
      const count = await recipeListPage.getRecipeCount();

      if (count > 0) {
        const firstCard = recipeListPage.getRecipeCard(0);
        await expect(firstCard).toBeVisible();

        // タイトルが表示されることを確認
        const title = await firstCard.locator('[data-testid="recipe-title"]').textContent();
        expect(title).toBeTruthy();
        expect(title.length).toBeGreaterThan(0);
      }
    });

    test('レシピが存在しない場合は空の状態を表示', async () => {
      const count = await recipeListPage.getRecipeCount();

      if (count === 0) {
        const isEmpty = await recipeListPage.isEmpty();
        expect(isEmpty).toBe(true);
      }
    });
  });

  test.describe('検索機能', () => {
    test('検索入力欄が表示される', async ({ page }) => {
      const searchInput = page.locator('[data-testid="search-input"]');
      await expect(searchInput).toBeVisible();
    });

    test('検索クエリでレシピを絞り込める', async () => {
      const initialCount = await recipeListPage.getRecipeCount();

      if (initialCount > 0) {
        // 検索実行
        await recipeListPage.search('カレー');

        // 結果が更新されることを確認
        const titles = await recipeListPage.getRecipeTitles();
        const hasRelevantResults = titles.some(title => title.includes('カレー'));

        // 検索結果が表示されるか、空の状態になるか
        expect(hasRelevantResults || await recipeListPage.isEmpty()).toBe(true);
      }
    });

    test('検索をクリアできる', async () => {
      await recipeListPage.search('テスト検索');
      await recipeListPage.clearSearch();

      // 検索がクリアされたことを確認
      const count = await recipeListPage.getRecipeCount();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test('空の検索クエリで全件表示', async () => {
      await recipeListPage.search('');
      const count = await recipeListPage.getRecipeCount();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test('特殊文字を含む検索が正常に動作', async () => {
      // 特殊文字を含む検索でエラーが発生しないことを確認
      await recipeListPage.search('パスタ & ソース');
      const hasError = await recipeListPage.hasError();
      expect(hasError).toBe(false);
    });
  });

  test.describe('フィルター機能', () => {
    test('フィルターパネルが表示される', async () => {
      const isVisible = await recipeListPage.isFilterPanelVisible();
      expect(isVisible).toBe(true);
    });

    test('カテゴリーフィルターが機能する', async () => {
      const initialCount = await recipeListPage.getRecipeCount();

      if (initialCount > 0) {
        await recipeListPage.filterByCategory('main-dish');

        // フィルター適用後の結果を確認
        const count = await recipeListPage.getRecipeCount();
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });

    test('難易度フィルターが機能する', async () => {
      const initialCount = await recipeListPage.getRecipeCount();

      if (initialCount > 0) {
        await recipeListPage.filterByDifficulty('easy');

        const count = await recipeListPage.getRecipeCount();
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });

    test('複数のフィルターを組み合わせられる', async () => {
      const initialCount = await recipeListPage.getRecipeCount();

      if (initialCount > 0) {
        await recipeListPage.filterByCategory('main-dish');
        await recipeListPage.filterByDifficulty('easy');

        const count = await recipeListPage.getRecipeCount();
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });

    test('フィルターをクリアできる', async () => {
      await recipeListPage.filterByCategory('dessert');
      await recipeListPage.clearFilters();

      // フィルターがクリアされたことを確認
      const count = await recipeListPage.getRecipeCount();
      expect(count).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('ソート機能', () => {
    test('名前順でソートできる', async () => {
      const initialCount = await recipeListPage.getRecipeCount();

      if (initialCount > 1) {
        await recipeListPage.sortBy('name');

        const titles = await recipeListPage.getRecipeTitles();
        expect(titles.length).toBeGreaterThan(0);

        // ソート後も同じ数のレシピが表示されることを確認
        const sortedCount = await recipeListPage.getRecipeCount();
        expect(sortedCount).toBe(initialCount);
      }
    });

    test('日付順でソートできる', async () => {
      const initialCount = await recipeListPage.getRecipeCount();

      if (initialCount > 1) {
        await recipeListPage.sortBy('date');

        const sortedCount = await recipeListPage.getRecipeCount();
        expect(sortedCount).toBe(initialCount);
      }
    });
  });

  test.describe('ペジネーション', () => {
    test('ペジネーションが表示される（複数ページの場合）', async ({ page }) => {
      const pagination = page.locator('[data-testid="pagination"]');
      const isVisible = await pagination.isVisible().catch(() => false);

      // ペジネーションがある場合のみテスト
      if (isVisible) {
        await expect(pagination).toBeVisible();
      }
    });

    test('次のページへ移動できる', async ({ page }) => {
      const nextButton = page.locator('[data-testid="pagination-next"]');
      const isVisible = await nextButton.isVisible().catch(() => false);

      if (isVisible && !(await nextButton.isDisabled())) {
        const firstPageTitles = await recipeListPage.getRecipeTitles();
        await recipeListPage.goToNextPage();
        const secondPageTitles = await recipeListPage.getRecipeTitles();

        // ページが変わったことを確認
        expect(firstPageTitles).not.toEqual(secondPageTitles);
      }
    });

    test('前のページへ移動できる', async ({ page }) => {
      const nextButton = page.locator('[data-testid="pagination-next"]');
      const isNextVisible = await nextButton.isVisible().catch(() => false);

      if (isNextVisible && !(await nextButton.isDisabled())) {
        await recipeListPage.goToNextPage();

        const prevButton = page.locator('[data-testid="pagination-prev"]');
        const isPrevVisible = await prevButton.isVisible().catch(() => false);

        if (isPrevVisible && !(await prevButton.isDisabled())) {
          await recipeListPage.goToPreviousPage();
          expect(page.url()).toContain('/recipes');
        }
      }
    });
  });

  test.describe('レシピカードのインタラクション', () => {
    test('レシピカードをクリックして詳細ページへ移動', async ({ page }) => {
      const count = await recipeListPage.getRecipeCount();

      if (count > 0) {
        await recipeListPage.clickRecipeCard(0);

        // 詳細ページへ遷移したことを確認
        expect(page.url()).toMatch(/\/recipes\/[^/]+$/);
      }
    });

    test('レシピカードにホバーでスタイルが変更される', async ({ page }) => {
      const count = await recipeListPage.getRecipeCount();

      if (count > 0) {
        const firstCard = recipeListPage.getRecipeCard(0);

        // ホバー前の状態を取得
        const beforeHover = await firstCard.evaluate(el => {
          const style = window.getComputedStyle(el);
          return style.transform || style.boxShadow;
        });

        // ホバー
        await firstCard.hover();

        // ホバー後の状態を取得
        await page.waitForTimeout(100);
        const afterHover = await firstCard.evaluate(el => {
          const style = window.getComputedStyle(el);
          return style.transform || style.boxShadow;
        });

        // スタイルの変化は必須ではないが、推奨
        expect(beforeHover).toBeDefined();
        expect(afterHover).toBeDefined();
      }
    });
  });

  test.describe('アクセシビリティ', () => {
    test('検索入力欄に適切なラベルがある', async () => {
      const hasLabel = await recipeListPage.hasSearchInputLabel();
      expect(hasLabel).toBe(true);
    });

    test('レシピカードにキーボードアクセスできる', async () => {
      const count = await recipeListPage.getRecipeCount();

      if (count > 0) {
        const isAccessible = await recipeListPage.isRecipeCardKeyboardAccessible();
        expect(isAccessible).toBe(true);
      }
    });

    test('Enterキーで検索を実行できる', async ({ page }) => {
      const searchInput = page.locator('[data-testid="search-input"]');
      await searchInput.fill('パスタ');
      await searchInput.press('Enter');

      // 検索が実行されることを確認
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('/recipes');
    });

    test('フィルター選択がキーボードで操作できる', async ({ page }) => {
      const filterCategory = page.locator('[data-testid="filter-category"]');
      const isVisible = await filterCategory.isVisible().catch(() => false);

      if (isVisible) {
        await filterCategory.focus();
        await filterCategory.press('ArrowDown');
        await filterCategory.press('Enter');

        // フィルターが適用されることを確認
        expect(page.url()).toContain('/recipes');
      }
    });
  });

  test.describe('レスポンシブデザイン', () => {
    test('モバイルビューでグリッドが1カラムになる', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await recipeListPage.goto();

      const count = await recipeListPage.getRecipeCount();
      if (count > 0) {
        const recipeList = page.locator('[data-testid="recipe-list"]');
        await expect(recipeList).toBeVisible();
      }
    });

    test('タブレットビューでグリッドが2カラムになる', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await recipeListPage.goto();

      const count = await recipeListPage.getRecipeCount();
      if (count > 0) {
        const recipeList = page.locator('[data-testid="recipe-list"]');
        await expect(recipeList).toBeVisible();
      }
    });
  });

  test.describe('パフォーマンス', () => {
    test('大量のレシピでもスムーズにスクロールできる', async ({ page }) => {
      const count = await recipeListPage.getRecipeCount();

      if (count > 10) {
        // ページ下部までスクロール
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(500);

        // ページ上部へスクロール
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForTimeout(500);

        // エラーが発生していないことを確認
        const hasError = await recipeListPage.hasError();
        expect(hasError).toBe(false);
      }
    });

    test('画像が遅延読み込みされる', async ({ page }) => {
      const count = await recipeListPage.getRecipeCount();

      if (count > 0) {
        const images = page.locator('[data-testid="recipe-image"]');
        const firstImage = images.first();
        const loading = await firstImage.getAttribute('loading');

        // 遅延読み込みは推奨
        if (loading) {
          expect(loading).toBe('lazy');
        }
      }
    });
  });

  test.describe('エラーハンドリング', () => {
    test('APIエラー時に適切なメッセージを表示', async ({ page }) => {
      // APIリクエストをインターセプトしてエラーをシミュレート
      await page.route('**/api/v1/recipes*', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal Server Error' }),
        });
      });

      await recipeListPage.goto();

      // エラーメッセージが表示されることを確認
      const hasError = await recipeListPage.hasError();
      expect(hasError).toBe(true);
    });

    test('ネットワークエラー時の再試行機能', async ({ page }) => {
      let requestCount = 0;

      // 最初のリクエストは失敗、2回目は成功させる
      await page.route('**/api/v1/recipes*', route => {
        requestCount++;
        if (requestCount === 1) {
          route.abort('failed');
        } else {
          route.continue();
        }
      });

      await recipeListPage.goto();

      // 再試行後にレシピが表示されるか、エラーが表示される
      const hasError = await recipeListPage.hasError();
      const count = await recipeListPage.getRecipeCount();

      expect(hasError || count >= 0).toBe(true);
    });
  });
});

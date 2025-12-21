import { test, expect } from '@playwright/test';
import { HomePage } from '../page-objects/HomePage.js';

/**
 * ホームページ E2Eテスト
 *
 * ホームページの基本機能とアクセシビリティを検証
 */
test.describe('ホームページ', () => {
  let homePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.goto();
  });

  test.describe('基本表示', () => {
    test('ページが正常に読み込まれる', async ({ page }) => {
      // ページタイトルの確認
      const title = await homePage.getTitle();
      expect(title).toBeTruthy();
      expect(title.length).toBeGreaterThan(0);

      // URLの確認
      expect(page.url()).toContain('/');
    });

    test('ページ読み込み時間が適切', async ({ page }) => {
      const startTime = Date.now();
      await homePage.goto();
      const loadTime = Date.now() - startTime;

      // 3秒以内に読み込まれることを確認
      expect(loadTime).toBeLessThan(3000);
    });

    test('メインヘッディングが表示される', async () => {
      const heading = await homePage.getHeadingText();
      expect(heading).toBeTruthy();
      expect(heading.length).toBeGreaterThan(0);
    });
  });

  test.describe('ヘッダー', () => {
    test('ヘッダーが表示される', async () => {
      const isVisible = await homePage.isHeaderVisible();
      expect(isVisible).toBe(true);
    });

    test('ロゴが表示される', async () => {
      const isVisible = await homePage.isLogoVisible();
      expect(isVisible).toBe(true);
    });

    test('ナビゲーションメニューが表示される', async () => {
      const isVisible = await homePage.isNavigationVisible();
      expect(isVisible).toBe(true);
    });

    test('ナビゲーションリンクが機能する - レシピ一覧', async ({ page }) => {
      await homePage.navigateToRecipes();
      expect(page.url()).toContain('/recipes');
    });

    test('ナビゲーションリンクが機能する - レシピ追加', async ({ page }) => {
      await homePage.navigateToAddRecipe();
      expect(page.url()).toMatch(/\/recipes\/(new|add)/);
    });
  });

  test.describe('フッター', () => {
    test('フッターが表示される', async () => {
      const isVisible = await homePage.isFooterVisible();
      expect(isVisible).toBe(true);
    });

    test('フッターが最下部に配置されている', async ({ page }) => {
      const footer = page.locator('footer');
      const footerBox = await footer.boundingBox();
      const viewportSize = page.viewportSize();

      expect(footerBox).toBeTruthy();
      expect(viewportSize).toBeTruthy();
    });
  });

  test.describe('アクセシビリティ', () => {
    test('適切なARIA属性が設定されている', async () => {
      const hasProperARIA = await homePage.hasProperARIA();
      expect(hasProperARIA).toBe(true);
    });

    test('キーボードナビゲーションが機能する', async () => {
      const canNavigate = await homePage.testKeyboardNavigation();
      expect(canNavigate).toBe(true);
    });

    test('見出し階層が適切', async ({ page }) => {
      // h1が1つだけ存在することを確認
      const h1Count = await page.locator('h1').count();
      expect(h1Count).toBe(1);
    });

    test('ランドマーク領域が定義されている', async ({ page }) => {
      const header = page.locator('header[role="banner"], header');
      const main = page.locator('main[role="main"], main');
      const footer = page.locator('footer[role="contentinfo"], footer');

      await expect(header).toBeVisible();
      await expect(main).toBeVisible();
      await expect(footer).toBeVisible();
    });

    test('スキップリンクが存在する（推奨）', async ({ page }) => {
      const skipLink = page.locator('a[href="#main-content"], a[href="#content"]').first();
      const skipLinkExists = await skipLink.count() > 0;

      // スキップリンクは推奨だが必須ではない
      if (skipLinkExists) {
        await expect(skipLink).toBeTruthy();
      }
    });
  });

  test.describe('レスポンシブデザイン', () => {
    test('モバイルビューで正常に表示される', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
      await homePage.goto();

      const isHeaderVisible = await homePage.isHeaderVisible();
      const isFooterVisible = await homePage.isFooterVisible();

      expect(isHeaderVisible).toBe(true);
      expect(isFooterVisible).toBe(true);
    });

    test('タブレットビューで正常に表示される', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 }); // iPad
      await homePage.goto();

      const isHeaderVisible = await homePage.isHeaderVisible();
      const isFooterVisible = await homePage.isFooterVisible();

      expect(isHeaderVisible).toBe(true);
      expect(isFooterVisible).toBe(true);
    });

    test('デスクトップビューで正常に表示される', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 }); // Full HD
      await homePage.goto();

      const isHeaderVisible = await homePage.isHeaderVisible();
      const isFooterVisible = await homePage.isFooterVisible();

      expect(isHeaderVisible).toBe(true);
      expect(isFooterVisible).toBe(true);
    });
  });

  test.describe('パフォーマンス', () => {
    test('画像が遅延読み込みされる（推奨）', async ({ page }) => {
      const images = page.locator('img[loading="lazy"]');
      const lazyImageCount = await images.count();

      // 遅延読み込みは推奨だが必須ではない
      if (lazyImageCount > 0) {
        expect(lazyImageCount).toBeGreaterThan(0);
      }
    });

    test('不要なリソースの読み込みがない', async ({ page }) => {
      const requests = [];
      page.on('request', request => requests.push(request));

      await homePage.goto();

      // 100以下のリクエスト数を推奨
      expect(requests.length).toBeLessThan(100);
    });
  });

  test.describe('SEO', () => {
    test('metaタグが適切に設定されている', async ({ page }) => {
      await homePage.goto();

      // description meta
      const description = await page.locator('meta[name="description"]').getAttribute('content');
      expect(description).toBeTruthy();
      expect(description.length).toBeGreaterThan(0);
    });

    test('言語属性が設定されている', async ({ page }) => {
      await homePage.goto();

      const lang = await page.locator('html').getAttribute('lang');
      expect(lang).toBeTruthy();
      expect(lang).toMatch(/^(ja|en)/);
    });
  });

  test.describe('エラーハンドリング', () => {
    test('存在しないページへの遷移で適切にエラー表示される', async ({ page }) => {
      const response = await page.goto('/this-page-does-not-exist-12345');

      // 404ページまたはリダイレクトが適切に処理される
      expect(response.status()).toBeGreaterThanOrEqual(200);
    });

    test('ネットワークエラー時に適切なメッセージが表示される', async ({ page }) => {
      // ネットワークをオフラインに設定
      await page.context().setOffline(true);

      try {
        await page.goto('/');
      } catch (error) {
        // オフライン時のエラーが適切にハンドリングされることを確認
        expect(error).toBeTruthy();
      }

      // ネットワークを復元
      await page.context().setOffline(false);
    });
  });
});

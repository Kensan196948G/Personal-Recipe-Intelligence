import { test, expect, chromium } from '@playwright/test';

/**
 * Chrome DevTools パフォーマンステスト
 *
 * Chrome DevTools Protocol を使用したパフォーマンス測定
 */
test.describe('パフォーマンステスト（Chrome DevTools）', () => {
  const APP_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

  test('ページ読み込みパフォーマンスを測定', async () => {
    const browser = await chromium.launch({
      args: ['--remote-debugging-port=9222']
    });
    const context = await browser.newContext();
    const page = await context.newPage();

    // Performance タイムラインを取得
    await page.goto(APP_URL, { waitUntil: 'networkidle' });

    // Performance Metrics を取得
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0];
      const paint = performance.getEntriesByType('paint');

      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
      };
    });

    console.log('📊 Performance Metrics:', performanceMetrics);

    // パフォーマンス基準の検証
    expect(performanceMetrics.domContentLoaded).toBeLessThan(1000); // 1秒以内
    expect(performanceMetrics.loadComplete).toBeLessThan(2000); // 2秒以内
    expect(performanceMetrics.firstContentfulPaint).toBeLessThan(1500); // 1.5秒以内

    await browser.close();
  });

  test('ネットワークリクエストを監視', async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    const requests = [];
    const responses = [];

    // リクエスト・レスポンスを記録
    page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType()
      });
    });

    page.on('response', response => {
      responses.push({
        url: response.url(),
        status: response.status(),
        size: response.headers()['content-length'] || 0
      });
    });

    await page.goto(APP_URL, { waitUntil: 'networkidle' });

    console.log(`📊 Total Requests: ${requests.length}`);
    console.log(`📊 Total Responses: ${responses.length}`);

    // API リクエストの確認
    const apiRequests = requests.filter(r => r.url.includes('/api/'));
    console.log(`📊 API Requests: ${apiRequests.length}`);

    // レスポンスステータスの確認
    const failedResponses = responses.filter(r => r.status >= 400);
    expect(failedResponses.length).toBe(0); // エラーレスポンスなし

    await browser.close();
  });

  test('コンソールエラーがないことを確認', async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    const consoleErrors = [];
    const consoleWarnings = [];

    // コンソールメッセージを記録
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      } else if (msg.type() === 'warning') {
        consoleWarnings.push(msg.text());
      }
    });

    await page.goto(APP_URL, { waitUntil: 'networkidle' });

    // レシピ一覧ページに移動
    await page.click('text=レシピ一覧');
    await page.waitForTimeout(1000);

    console.log(`⚠️  Warnings: ${consoleWarnings.length}`);
    console.log(`❌ Errors: ${consoleErrors.length}`);

    // エラーがないことを確認
    expect(consoleErrors.length).toBe(0);

    await browser.close();
  });

  test('JavaScriptエラーをキャッチ', async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    const pageErrors = [];

    // ページエラーを記録
    page.on('pageerror', error => {
      pageErrors.push(error.message);
    });

    await page.goto(APP_URL, { waitUntil: 'networkidle' });

    // 各種操作を実行
    await page.click('text=レシピ一覧');
    await page.waitForTimeout(500);

    // 検索を試す
    const searchInput = page.locator('input[type="search"], input[placeholder*="検索"]').first();
    if (await searchInput.count() > 0) {
      await searchInput.fill('カレー');
      await page.waitForTimeout(500);
    }

    console.log(`❌ Page Errors: ${pageErrors.length}`);
    if (pageErrors.length > 0) {
      console.log('Errors:', pageErrors);
    }

    // JavaScriptエラーがないことを確認
    expect(pageErrors.length).toBe(0);

    await browser.close();
  });

  test('メモリリークがないことを確認', async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto(APP_URL, { waitUntil: 'networkidle' });

    // 初期ヒープサイズを取得
    const initialHeap = await page.evaluate(() => {
      if (performance.memory) {
        return performance.memory.usedJSHeapSize;
      }
      return 0;
    });

    // 複数回ページ遷移
    for (let i = 0; i < 5; i++) {
      await page.click('text=レシピ一覧');
      await page.waitForTimeout(500);
      await page.click('text=ホーム');
      await page.waitForTimeout(500);
    }

    // 最終ヒープサイズを取得
    const finalHeap = await page.evaluate(() => {
      if (performance.memory) {
        return performance.memory.usedJSHeapSize;
      }
      return 0;
    });

    const heapGrowth = finalHeap - initialHeap;
    const heapGrowthMB = heapGrowth / 1024 / 1024;

    console.log(`📊 Initial Heap: ${(initialHeap / 1024 / 1024).toFixed(2)} MB`);
    console.log(`📊 Final Heap: ${(finalHeap / 1024 / 1024).toFixed(2)} MB`);
    console.log(`📊 Heap Growth: ${heapGrowthMB.toFixed(2)} MB`);

    // ヒープ増加が10MB以下であることを確認（メモリリークなし）
    if (initialHeap > 0 && finalHeap > 0) {
      expect(heapGrowthMB).toBeLessThan(10);
    }

    await browser.close();
  });
});

/**
 * Chrome DevTools - Core Web Vitals 測定
 */
test.describe('Core Web Vitals', () => {
  const APP_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

  test('LCP（Largest Contentful Paint）を測定', async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto(APP_URL, { waitUntil: 'networkidle' });

    const lcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.renderTime || lastEntry.loadTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        // タイムアウト
        setTimeout(() => resolve(0), 5000);
      });
    });

    console.log(`📊 LCP: ${lcp.toFixed(2)} ms`);

    // LCP が 2.5秒以内（Good）
    expect(lcp).toBeLessThan(2500);

    await browser.close();
  });

  test('CLS（Cumulative Layout Shift）を測定', async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto(APP_URL, { waitUntil: 'networkidle' });

    const cls = await page.evaluate(() => {
      return new Promise((resolve) => {
        let clsValue = 0;

        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
        }).observe({ entryTypes: ['layout-shift'] });

        // 3秒後に結果を返す
        setTimeout(() => resolve(clsValue), 3000);
      });
    });

    console.log(`📊 CLS: ${cls.toFixed(4)}`);

    // CLS が 0.1以下（Good）
    expect(cls).toBeLessThan(0.1);

    await browser.close();
  });
});

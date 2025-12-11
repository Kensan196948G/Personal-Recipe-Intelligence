/**
 * Playwright Configuration for Personal Recipe Intelligence
 * E2E テスト設定 - SSH + Ubuntu CLI 環境対応
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // テストディレクトリ
  testDir: './e2e',

  // テストファイルのパターン
  testMatch: '**/*.test.js',

  // タイムアウト設定
  timeout: 30000,
  expect: {
    timeout: 5000,
  },

  // 並列実行設定
  fullyParallel: true,

  // 失敗時のリトライ回数
  retries: process.env.CI ? 2 : 0,

  // ワーカー数（CI環境では1に制限）
  workers: process.env.CI ? 1 : undefined,

  // レポーター設定
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['list'],
  ],

  // スクリーンショット・動画設定
  use: {
    // ベースURL
    baseURL: process.env.BASE_URL || 'http://localhost:5173',

    // トレース設定
    trace: 'on-first-retry',

    // スクリーンショット設定
    screenshot: 'only-on-failure',

    // 動画設定
    video: 'retain-on-failure',

    // タイムゾーン
    timezoneId: 'Asia/Tokyo',

    // ロケール
    locale: 'ja-JP',

    // ヘッドレスモード（SSH環境では必須）
    headless: true,

    // ビューポート
    viewport: { width: 1280, height: 720 },

    // アクションのタイムアウト
    actionTimeout: 10000,

    // ナビゲーションのタイムアウト
    navigationTimeout: 15000,
  },

  // プロジェクト（ブラウザ）設定
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
          ],
        },
      },
    },

    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
      },
    },

    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
      },
    },

    // モバイルテスト（オプション）
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
      },
    },

    {
      name: 'mobile-safari',
      use: {
        ...devices['iPhone 12'],
      },
    },
  ],

  // 開発サーバー設定
  webServer: {
    command: 'bun run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});

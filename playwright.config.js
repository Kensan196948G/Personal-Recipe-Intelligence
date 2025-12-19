/**
 * Playwright E2E Test Configuration
 *
 * Role: Automated testing, CI/CD integration, regression testing
 * Complementary tool: chrome-devtools MCP (for interactive debugging)
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Test directory
  testDir: './tests/e2e',

  // Test file pattern
  testMatch: '**/*.spec.js',

  // Parallel execution
  fullyParallel: true,

  // Fail the build on CI if test.only is left in code
  forbidOnly: !!process.env.CI,

  // Retry failed tests
  retries: process.env.CI ? 2 : 0,

  // Number of parallel workers
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'tests/e2e/reports' }],
    ['list'],
  ],

  // Shared settings for all projects
  use: {
    // Base URL for navigation
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',

    // Collect trace on failure
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video recording
    video: 'on-first-retry',

    // Timeout for actions
    actionTimeout: 10000,

    // Navigation timeout
    navigationTimeout: 30000,
  },

  // Test timeout
  timeout: 60000,

  // Projects (browser configurations)
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Viewport size
        viewport: { width: 1280, height: 720 },
      },
    },
    // Add more browsers if needed
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
  ],

  // Web server configuration
  // Note: Start servers manually before running tests, or uncomment below
  // webServer: [
  //   {
  //     // Frontend dev server
  //     command: 'cd frontend && npm run dev',
  //     url: 'http://localhost:5173',
  //     reuseExistingServer: true,
  //     timeout: 120000,
  //   },
  //   {
  //     // Backend API server
  //     command: 'python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000',
  //     url: 'http://localhost:8000/health',
  //     reuseExistingServer: true,
  //     timeout: 120000,
  //   },
  // ],

  // Output directory for test artifacts
  outputDir: 'tests/e2e/results',
});

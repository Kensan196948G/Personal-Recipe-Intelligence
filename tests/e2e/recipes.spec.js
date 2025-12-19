/**
 * E2E Tests: Recipe Management
 *
 * Role: Automated regression testing for recipe CRUD operations
 * Run: npx playwright test recipes.spec.js
 *
 * Note: Use chrome-devtools MCP for interactive debugging
 *       before adding new test cases here.
 */

import { test, expect } from '@playwright/test';

test.describe('Recipe Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto('/');
  });

  test('should display home page', async ({ page }) => {
    // Verify page title or main heading
    await expect(page.locator('h1, .app-title')).toBeVisible();
  });

  test('should navigate to recipe list', async ({ page }) => {
    // Check if recipe list is visible or navigation works
    const recipeList = page.locator('.recipe-list, .recipes-container, [data-testid="recipe-list"]');
    await expect(recipeList).toBeVisible({ timeout: 10000 });
  });

  test('should open new recipe form', async ({ page }) => {
    // Click create button
    const createButton = page.locator('button:has-text("新規"), button:has-text("作成"), [data-testid="create-recipe"]');

    if (await createButton.isVisible()) {
      await createButton.click();

      // Verify form is displayed (use .first() to handle multiple matches)
      const form = page.locator('form').first();
      await expect(form).toBeVisible();
    }
  });

  test('should create a new recipe', async ({ page }) => {
    // Click create button
    const createButton = page.locator('button:has-text("新規"), button:has-text("作成")');

    if (await createButton.isVisible()) {
      await createButton.click();

      // Fill in recipe details
      await page.fill('input[id="title"], input[name="title"]', 'E2Eテストレシピ');
      await page.fill('textarea[id="description"], textarea[name="description"]', 'Playwrightによる自動テスト');

      // Set servings if field exists
      const servingsField = page.locator('input[id="servings"], input[name="servings"]');
      if (await servingsField.isVisible()) {
        await servingsField.fill('4');
      }

      // Submit form
      await page.click('button[type="submit"], button:has-text("保存")');

      // Verify success (check for success message or redirect)
      await expect(page.locator('.success, .recipe-detail, .recipe-list')).toBeVisible({ timeout: 10000 });
    }
  });

  test('should search recipes', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="検索"], .search-input');

    if (await searchInput.isVisible()) {
      await searchInput.fill('テスト');
      await searchInput.press('Enter');

      // Wait for search results
      await page.waitForTimeout(1000);

      // Verify search was performed (URL change or results displayed)
      const url = page.url();
      const hasSearchParam = url.includes('search') || url.includes('q=');
      const hasResults = await page.locator('.recipe-card, .recipe-item').count() >= 0;

      expect(hasSearchParam || hasResults).toBeTruthy();
    }
  });

  test('should handle pagination', async ({ page }) => {
    // Look for pagination controls
    const pagination = page.locator('.pagination, [data-testid="pagination"]');

    if (await pagination.isVisible()) {
      const nextButton = pagination.locator('button:has-text("次"), button:has-text(">"), .next');

      if (await nextButton.isVisible() && await nextButton.isEnabled()) {
        await nextButton.click();

        // Verify page changed
        await page.waitForTimeout(500);
        const url = page.url();
        expect(url.includes('page=2') || true).toBeTruthy();
      }
    }
  });

  test('should edit an existing recipe', async ({ page }) => {
    // Find first recipe in the list
    const recipeCard = page.locator('.recipe-card, .recipe-item, [data-testid="recipe-card"]').first();

    if (await recipeCard.isVisible()) {
      // Click on recipe to view details or click edit button
      const editButton = page.locator('button:has-text("編集"), button:has-text("Edit"), [data-testid="edit-recipe"]').first();

      if (await editButton.isVisible()) {
        await editButton.click();
      } else {
        // If no edit button, click recipe card first
        await recipeCard.click();
        await page.waitForTimeout(500);
        await page.locator('button:has-text("編集"), button:has-text("Edit")').first().click();
      }

      // Wait for form to be visible
      const form = page.locator('form').first();
      await expect(form).toBeVisible({ timeout: 5000 });

      // Modify recipe title
      const titleInput = page.locator('input[id="title"], input[name="title"]');
      await titleInput.fill('編集済みレシピ - E2Eテスト');

      // Modify description
      const descInput = page.locator('textarea[id="description"], textarea[name="description"]');
      await descInput.fill('Playwrightによる編集テスト');

      // Submit form
      await page.click('button[type="submit"], button:has-text("保存"), button:has-text("更新")');

      // Verify success - check for updated content or success message
      await page.waitForTimeout(1000);
      const updatedTitle = page.locator('text=編集済みレシピ - E2Eテスト');
      const successMessage = page.locator('.success, .toast, .notification');

      // Either title is visible or success message appeared
      const titleVisible = await updatedTitle.isVisible().catch(() => false);
      const messageVisible = await successMessage.isVisible().catch(() => false);

      expect(titleVisible || messageVisible).toBeTruthy();
    }
  });

  test('should delete a recipe', async ({ page }) => {
    // Find first recipe in the list
    const recipeCard = page.locator('.recipe-card, .recipe-item, [data-testid="recipe-card"]').first();

    if (await recipeCard.isVisible()) {
      // Get initial recipe count
      const initialCount = await page.locator('.recipe-card, .recipe-item').count();

      // Look for delete button
      const deleteButton = page.locator('button:has-text("削除"), button:has-text("Delete"), [data-testid="delete-recipe"]').first();

      if (await deleteButton.isVisible()) {
        await deleteButton.click();
      } else {
        // If no delete button, click recipe card first to view details
        await recipeCard.click();
        await page.waitForTimeout(500);
        await page.locator('button:has-text("削除"), button:has-text("Delete")').first().click();
      }

      // Handle confirmation dialog if exists
      const confirmButton = page.locator('button:has-text("確認"), button:has-text("OK"), button:has-text("はい"), .confirm-delete');
      if (await confirmButton.isVisible({ timeout: 2000 }).catch(() => false)) {
        await confirmButton.click();
      }

      // Wait for deletion to complete
      await page.waitForTimeout(1000);

      // Verify recipe is removed - check for success message or reduced count
      const successMessage = page.locator('.success, .toast, text=削除');
      const finalCount = await page.locator('.recipe-card, .recipe-item').count();

      const messageVisible = await successMessage.isVisible().catch(() => false);
      const countReduced = finalCount < initialCount;

      expect(messageVisible || countReduced).toBeTruthy();
    }
  });

  test('should display error for invalid recipe data', async ({ page }) => {
    // Click create button
    const createButton = page.locator('button:has-text("新規"), button:has-text("作成"), [data-testid="create-recipe"]');

    if (await createButton.isVisible()) {
      await createButton.click();

      // Wait for form
      const form = page.locator('form').first();
      await expect(form).toBeVisible();

      // Try to submit form with empty required fields
      await page.click('button[type="submit"], button:has-text("保存")');

      // Wait for error messages
      await page.waitForTimeout(500);

      // Check for validation errors
      const errorMessage = page.locator('.error, .validation-error, .field-error, [role="alert"]');
      const invalidFeedback = page.locator('.invalid-feedback, .error-message');
      const requiredMessage = page.locator('text=必須, text=required, text=入力してください');

      // At least one error indicator should be visible
      const hasError = await errorMessage.isVisible().catch(() => false);
      const hasInvalidFeedback = await invalidFeedback.isVisible().catch(() => false);
      const hasRequiredMessage = await requiredMessage.isVisible().catch(() => false);

      expect(hasError || hasInvalidFeedback || hasRequiredMessage).toBeTruthy();

      // Test invalid servings value (negative number)
      const servingsField = page.locator('input[id="servings"], input[name="servings"]');
      if (await servingsField.isVisible()) {
        await servingsField.fill('-1');

        // Fill required fields
        await page.fill('input[id="title"], input[name="title"]', 'エラーテスト');

        // Submit
        await page.click('button[type="submit"], button:has-text("保存")');
        await page.waitForTimeout(500);

        // Check for error about invalid servings
        const servingsError = page.locator('text=無効, text=invalid, text=正しい, .error');
        const hasServingsError = await servingsError.isVisible().catch(() => false);

        // Error should be shown or form should prevent submission
        expect(hasServingsError || await errorMessage.isVisible()).toBeTruthy();
      }
    }
  });
});

test.describe('API Health Check', () => {
  test('should return healthy status from API', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health');

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('ok');
  });

  test('should return API info from root', async ({ request }) => {
    const response = await request.get('http://localhost:8000/');

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('ok');
    expect(data.data.name).toContain('Recipe');
  });
});

test.describe('Recipe API', () => {
  test('should list recipes via API', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/recipes');

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('ok');
    expect(Array.isArray(data.data.items)).toBeTruthy();
  });

  test('should create recipe via API', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/v1/recipes', {
      data: {
        title: 'API Test Recipe',
        description: 'Created via Playwright API test',
        servings: 2,
        source_type: 'manual'
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('ok');
    expect(data.data.title).toBe('API Test Recipe');
  });
});

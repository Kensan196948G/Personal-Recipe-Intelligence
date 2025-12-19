import { test, expect } from '@playwright/test';

/**
 * API統合 E2Eテスト
 *
 * データベース連携とAPI全体の動作を検証
 */
test.describe('API統合テスト', () => {
  const API_BASE_URL = process.env.E2E_API_URL || 'http://localhost:8000';

  test.describe('レシピAPI', () => {
    test('レシピ一覧取得が動作する', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes`);

      expect(response.ok()).toBeTruthy();
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      expect(data.length).toBeGreaterThanOrEqual(3); // シードデータ
    });

    test('レシピ詳細取得が動作する', async ({ request }) => {
      // シードデータのレシピID=1を取得
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes/1`);

      expect(response.ok()).toBeTruthy();
      expect(response.status()).toBe(200);

      const recipe = await response.json();
      expect(recipe).toHaveProperty('id');
      expect(recipe).toHaveProperty('title');
      expect(recipe).toHaveProperty('description');
      expect(recipe.title).toContain('カレーライス');
    });

    test('レシピ作成が動作する', async ({ request }) => {
      const newRecipe = {
        title: 'E2Eテストレシピ',
        description: 'Playwright により自動作成されたテストレシピ',
        servings: 2,
        prep_time_minutes: 10,
        cook_time_minutes: 15,
        source_type: 'manual',
        source_url: 'https://test.example.com/recipe'
      };

      const response = await request.post(`${API_BASE_URL}/api/v1/recipes`, {
        data: newRecipe
      });

      expect(response.ok()).toBeTruthy();
      expect(response.status()).toBe(201);

      const created = await response.json();
      expect(created).toHaveProperty('id');
      expect(created.title).toBe(newRecipe.title);
    });

    test('レシピ検索が動作する', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes/search?q=カレー`);

      expect(response.ok()).toBeTruthy();

      const results = await response.json();
      expect(Array.isArray(results)).toBeTruthy();
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].title).toContain('カレー');
    });
  });

  test.describe('タグAPI', () => {
    test('タグ一覧取得が動作する', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/tags`);

      expect(response.ok()).toBeTruthy();

      const tags = await response.json();
      expect(Array.isArray(tags)).toBeTruthy();
      expect(tags.length).toBeGreaterThanOrEqual(6); // シードデータ

      const tagNames = tags.map(t => t.name);
      expect(tagNames).toContain('和食');
      expect(tagNames).toContain('洋食');
    });

    test('タグでフィルタリングが動作する', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes?tag=和食`);

      expect(response.ok()).toBeTruthy();

      const recipes = await response.json();
      expect(Array.isArray(recipes)).toBeTruthy();
      expect(recipes.length).toBeGreaterThan(0);
    });
  });

  test.describe('データベース連携', () => {
    test('レシピと材料の関連が正しく取得できる', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes/1`);
      const recipe = await response.json();

      expect(recipe).toHaveProperty('ingredients');
      expect(Array.isArray(recipe.ingredients)).toBeTruthy();
      expect(recipe.ingredients.length).toBeGreaterThan(0);

      const firstIngredient = recipe.ingredients[0];
      expect(firstIngredient).toHaveProperty('name');
      expect(firstIngredient).toHaveProperty('amount');
      expect(firstIngredient).toHaveProperty('unit');
    });

    test('レシピと手順の関連が正しく取得できる', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes/1`);
      const recipe = await response.json();

      expect(recipe).toHaveProperty('steps');
      expect(Array.isArray(recipe.steps)).toBeTruthy();
      expect(recipe.steps.length).toBeGreaterThan(0);

      const firstStep = recipe.steps[0];
      expect(firstStep).toHaveProperty('description');
      expect(firstStep).toHaveProperty('order');
    });

    test('レシピとタグの関連が正しく取得できる', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes/1`);
      const recipe = await response.json();

      expect(recipe).toHaveProperty('tags');
      expect(Array.isArray(recipe.tags)).toBeTruthy();
      expect(recipe.tags.length).toBeGreaterThan(0);
    });
  });

  test.describe('エラーハンドリング', () => {
    test('存在しないレシピIDでは404エラー', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes/99999`);
      expect(response.status()).toBe(404);
    });

    test('不正なデータでレシピ作成すると400エラー', async ({ request }) => {
      const invalidRecipe = {
        // title が必須だが省略
        description: 'Invalid recipe'
      };

      const response = await request.post(`${API_BASE_URL}/api/v1/recipes`, {
        data: invalidRecipe
      });

      expect(response.status()).toBe(400);
    });
  });

  test.describe('パフォーマンス', () => {
    test('レシピ一覧取得が200ms以内', async ({ request }) => {
      const startTime = Date.now();
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes`);
      const duration = Date.now() - startTime;

      expect(response.ok()).toBeTruthy();
      expect(duration).toBeLessThan(200);
    });

    test('レシピ詳細取得が200ms以内', async ({ request }) => {
      const startTime = Date.now();
      const response = await request.get(`${API_BASE_URL}/api/v1/recipes/1`);
      const duration = Date.now() - startTime;

      expect(response.ok()).toBeTruthy();
      expect(duration).toBeLessThan(200);
    });
  });
});

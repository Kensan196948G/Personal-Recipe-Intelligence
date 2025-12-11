/**
 * Playwright Test Fixtures
 * 共通フィクスチャ・ページオブジェクト・テストデータ
 */

import { test as base, expect } from '@playwright/test';

/**
 * ページオブジェクト: ホームページ
 */
class HomePage {
  constructor(page) {
    this.page = page;
    this.searchInput = page.locator('[data-testid="search-input"]');
    this.searchButton = page.locator('[data-testid="search-button"]');
    this.recipeList = page.locator('[data-testid="recipe-list"]');
    this.addRecipeButton = page.locator('[data-testid="add-recipe-button"]');
  }

  async goto() {
    await this.page.goto('/');
  }

  async search(query) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
  }

  async clickAddRecipe() {
    await this.addRecipeButton.click();
  }

  async getRecipeCount() {
    return await this.recipeList.locator('[data-testid="recipe-item"]').count();
  }
}

/**
 * ページオブジェクト: レシピ追加ページ
 */
class AddRecipePage {
  constructor(page) {
    this.page = page;
    this.urlInput = page.locator('[data-testid="recipe-url-input"]');
    this.titleInput = page.locator('[data-testid="recipe-title-input"]');
    this.ingredientsTextarea = page.locator('[data-testid="recipe-ingredients-textarea"]');
    this.instructionsTextarea = page.locator('[data-testid="recipe-instructions-textarea"]');
    this.tagsInput = page.locator('[data-testid="recipe-tags-input"]');
    this.submitButton = page.locator('[data-testid="submit-recipe-button"]');
    this.cancelButton = page.locator('[data-testid="cancel-button"]');
    this.parseUrlButton = page.locator('[data-testid="parse-url-button"]');
  }

  async goto() {
    await this.page.goto('/add');
  }

  async fillRecipeForm(recipeData) {
    if (recipeData.url) {
      await this.urlInput.fill(recipeData.url);
    }
    if (recipeData.title) {
      await this.titleInput.fill(recipeData.title);
    }
    if (recipeData.ingredients) {
      await this.ingredientsTextarea.fill(recipeData.ingredients);
    }
    if (recipeData.instructions) {
      await this.instructionsTextarea.fill(recipeData.instructions);
    }
    if (recipeData.tags) {
      await this.tagsInput.fill(recipeData.tags);
    }
  }

  async submit() {
    await this.submitButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }

  async parseUrl() {
    await this.parseUrlButton.click();
  }
}

/**
 * ページオブジェクト: レシピ詳細ページ
 */
class RecipeDetailPage {
  constructor(page) {
    this.page = page;
    this.title = page.locator('[data-testid="recipe-title"]');
    this.ingredients = page.locator('[data-testid="recipe-ingredients"]');
    this.instructions = page.locator('[data-testid="recipe-instructions"]');
    this.tags = page.locator('[data-testid="recipe-tags"]');
    this.editButton = page.locator('[data-testid="edit-recipe-button"]');
    this.deleteButton = page.locator('[data-testid="delete-recipe-button"]');
    this.backButton = page.locator('[data-testid="back-button"]');
  }

  async goto(recipeId) {
    await this.page.goto(`/recipe/${recipeId}`);
  }

  async getTitle() {
    return await this.title.textContent();
  }

  async getIngredients() {
    return await this.ingredients.textContent();
  }

  async getInstructions() {
    return await this.instructions.textContent();
  }

  async edit() {
    await this.editButton.click();
  }

  async delete() {
    await this.deleteButton.click();
  }

  async goBack() {
    await this.backButton.click();
  }
}

/**
 * テストデータ: サンプルレシピ
 */
export const testRecipes = {
  basic: {
    title: 'テスト用カレーライス',
    ingredients: 'じゃがいも 2個\nにんじん 1本\nたまねぎ 1個\nカレールー 1箱',
    instructions: '1. 野菜を切る\n2. 炒める\n3. 煮込む\n4. カレールーを入れる',
    tags: 'カレー,簡単,和食',
  },
  withUrl: {
    url: 'https://cookpad.com/recipe/example',
    title: 'URLから取得したレシピ',
    ingredients: 'トマト 2個\nバジル 適量',
    instructions: '1. トマトを切る\n2. バジルを添える',
    tags: 'イタリアン,サラダ',
  },
  minimal: {
    title: '最小レシピ',
    ingredients: '材料A',
    instructions: '手順1',
    tags: '',
  },
  japanese: {
    title: '和食レシピ（味噌汁）',
    ingredients: 'だし 500ml\n味噌 大さじ2\n豆腐 1丁\nわかめ 適量',
    instructions: '1. だしを沸かす\n2. 豆腐とわかめを入れる\n3. 味噌を溶く',
    tags: '和食,味噌汁,簡単',
  },
};

/**
 * テストデータ: 検索クエリ
 */
export const searchQueries = {
  basic: 'カレー',
  tag: 'tag:簡単',
  ingredient: 'ingredient:トマト',
  noResults: 'zzz存在しないレシピzzz',
};

/**
 * API モックデータ
 */
export const mockApiResponses = {
  recipeList: {
    status: 'ok',
    data: [
      {
        id: 1,
        title: 'カレーライス',
        tags: ['カレー', '簡単'],
        created_at: '2025-12-01T10:00:00Z',
      },
      {
        id: 2,
        title: '味噌汁',
        tags: ['和食', '簡単'],
        created_at: '2025-12-02T10:00:00Z',
      },
    ],
    error: null,
  },
  recipeDetail: {
    status: 'ok',
    data: {
      id: 1,
      title: 'カレーライス',
      ingredients: [
        { name: 'じゃがいも', amount: '2個' },
        { name: 'にんじん', amount: '1本' },
      ],
      instructions: ['野菜を切る', '炒める', '煮込む'],
      tags: ['カレー', '簡単'],
      created_at: '2025-12-01T10:00:00Z',
    },
    error: null,
  },
  parseUrlSuccess: {
    status: 'ok',
    data: {
      title: '解析されたレシピ',
      ingredients: ['材料1', '材料2'],
      instructions: ['手順1', '手順2'],
      tags: [],
    },
    error: null,
  },
  parseUrlError: {
    status: 'error',
    data: null,
    error: 'URL解析に失敗しました',
  },
};

/**
 * カスタムフィクスチャの定義
 */
export const test = base.extend({
  // ホームページ
  homePage: async ({ page }, use) => {
    const homePage = new HomePage(page);
    await use(homePage);
  },

  // レシピ追加ページ
  addRecipePage: async ({ page }, use) => {
    const addRecipePage = new AddRecipePage(page);
    await use(addRecipePage);
  },

  // レシピ詳細ページ
  recipeDetailPage: async ({ page }, use) => {
    const recipeDetailPage = new RecipeDetailPage(page);
    await use(recipeDetailPage);
  },

  // テストデータのクリーンアップ
  cleanDatabase: async ({ request }, use) => {
    // テスト前のクリーンアップ
    await request.post('/api/v1/test/cleanup', {
      headers: { 'Content-Type': 'application/json' },
    }).catch(() => {
      // クリーンアップエンドポイントが存在しない場合は無視
    });

    await use();

    // テスト後のクリーンアップ
    await request.post('/api/v1/test/cleanup', {
      headers: { 'Content-Type': 'application/json' },
    }).catch(() => {
      // クリーンアップエンドポイントが存在しない場合は無視
    });
  },
});

export { expect };

/**
 * ユーティリティ関数: ランダムな文字列生成
 */
export function randomString(length = 10) {
  return Math.random().toString(36).substring(2, 2 + length);
}

/**
 * ユーティリティ関数: 遅延処理
 */
export function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * ユーティリティ関数: APIレスポンスのモック化
 */
export async function mockApiRoute(page, route, response) {
  await page.route(route, async (routeHandler) => {
    await routeHandler.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(response),
    });
  });
}

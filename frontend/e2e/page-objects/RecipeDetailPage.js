/**
 * レシピ詳細ページ ページオブジェクト
 *
 * レシピ詳細の要素とアクションをカプセル化
 */
export class RecipeDetailPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;

    // セレクター定義
    this.selectors = {
      // ページ要素
      heading: '[data-testid="recipe-title"]',
      image: '[data-testid="recipe-image"]',
      description: '[data-testid="recipe-description"]',

      // メタ情報
      metadata: '[data-testid="recipe-metadata"]',
      servings: '[data-testid="recipe-servings"]',
      cookingTime: '[data-testid="recipe-cooking-time"]',
      difficulty: '[data-testid="recipe-difficulty"]',
      category: '[data-testid="recipe-category"]',
      tags: '[data-testid="recipe-tags"]',

      // 材料セクション
      ingredientsSection: '[data-testid="ingredients-section"]',
      ingredientsList: '[data-testid="ingredients-list"]',
      ingredientItem: '[data-testid="ingredient-item"]',
      ingredientName: '[data-testid="ingredient-name"]',
      ingredientAmount: '[data-testid="ingredient-amount"]',

      // 手順セクション
      stepsSection: '[data-testid="steps-section"]',
      stepsList: '[data-testid="steps-list"]',
      stepItem: '[data-testid="step-item"]',
      stepNumber: '[data-testid="step-number"]',
      stepDescription: '[data-testid="step-description"]',

      // アクションボタン
      editButton: '[data-testid="edit-button"]',
      deleteButton: '[data-testid="delete-button"]',
      shareButton: '[data-testid="share-button"]',
      printButton: '[data-testid="print-button"]',
      favoriteButton: '[data-testid="favorite-button"]',

      // ナビゲーション
      backButton: '[data-testid="back-button"]',

      // ローディング・エラー
      loadingSpinner: '[data-testid="loading-spinner"]',
      errorMessage: '[data-testid="error-message"]',
      notFoundMessage: '[data-testid="not-found-message"]',
    };
  }

  /**
   * レシピ詳細ページへ移動
   * @param {string} recipeId - レシピID
   */
  async goto(recipeId) {
    await this.page.goto(`/recipes/${recipeId}`);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * レシピタイトルを取得
   * @returns {Promise<string>}
   */
  async getTitle() {
    return await this.page.locator(this.selectors.heading).textContent();
  }

  /**
   * レシピ説明を取得
   * @returns {Promise<string>}
   */
  async getDescription() {
    return await this.page.locator(this.selectors.description).textContent();
  }

  /**
   * 画像が表示されているか確認
   * @returns {Promise<boolean>}
   */
  async hasImage() {
    return await this.page.locator(this.selectors.image).isVisible();
  }

  /**
   * 人数を取得
   * @returns {Promise<string>}
   */
  async getServings() {
    return await this.page.locator(this.selectors.servings).textContent();
  }

  /**
   * 調理時間を取得
   * @returns {Promise<string>}
   */
  async getCookingTime() {
    return await this.page.locator(this.selectors.cookingTime).textContent();
  }

  /**
   * 難易度を取得
   * @returns {Promise<string>}
   */
  async getDifficulty() {
    return await this.page.locator(this.selectors.difficulty).textContent();
  }

  /**
   * カテゴリーを取得
   * @returns {Promise<string>}
   */
  async getCategory() {
    return await this.page.locator(this.selectors.category).textContent();
  }

  /**
   * タグのリストを取得
   * @returns {Promise<string[]>}
   */
  async getTags() {
    return await this.page.locator(`${this.selectors.tags} span`).allTextContents();
  }

  /**
   * 材料の数を取得
   * @returns {Promise<number>}
   */
  async getIngredientsCount() {
    return await this.page.locator(this.selectors.ingredientItem).count();
  }

  /**
   * 材料リストを取得
   * @returns {Promise<Array<{name: string, amount: string}>>}
   */
  async getIngredients() {
    const count = await this.getIngredientsCount();
    const ingredients = [];

    for (let i = 0; i < count; i++) {
      const item = this.page.locator(this.selectors.ingredientItem).nth(i);
      const name = await item.locator(this.selectors.ingredientName).textContent();
      const amount = await item.locator(this.selectors.ingredientAmount).textContent();
      ingredients.push({ name, amount });
    }

    return ingredients;
  }

  /**
   * 手順の数を取得
   * @returns {Promise<number>}
   */
  async getStepsCount() {
    return await this.page.locator(this.selectors.stepItem).count();
  }

  /**
   * 手順リストを取得
   * @returns {Promise<Array<{number: string, description: string}>>}
   */
  async getSteps() {
    const count = await this.getStepsCount();
    const steps = [];

    for (let i = 0; i < count; i++) {
      const item = this.page.locator(this.selectors.stepItem).nth(i);
      const number = await item.locator(this.selectors.stepNumber).textContent();
      const description = await item.locator(this.selectors.stepDescription).textContent();
      steps.push({ number, description });
    }

    return steps;
  }

  /**
   * 編集ボタンをクリック
   */
  async clickEdit() {
    await this.page.click(this.selectors.editButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 削除ボタンをクリック
   */
  async clickDelete() {
    await this.page.click(this.selectors.deleteButton);
  }

  /**
   * 削除確認ダイアログで確定
   */
  async confirmDelete() {
    this.page.once('dialog', dialog => dialog.accept());
    await this.clickDelete();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 削除確認ダイアログでキャンセル
   */
  async cancelDelete() {
    this.page.once('dialog', dialog => dialog.dismiss());
    await this.clickDelete();
  }

  /**
   * お気に入りボタンをクリック
   */
  async toggleFavorite() {
    await this.page.click(this.selectors.favoriteButton);
  }

  /**
   * お気に入り状態を確認
   * @returns {Promise<boolean>}
   */
  async isFavorite() {
    const ariaPressed = await this.page.locator(this.selectors.favoriteButton).getAttribute('aria-pressed');
    return ariaPressed === 'true';
  }

  /**
   * 共有ボタンをクリック
   */
  async clickShare() {
    await this.page.click(this.selectors.shareButton);
  }

  /**
   * 印刷ボタンをクリック
   */
  async clickPrint() {
    await this.page.click(this.selectors.printButton);
  }

  /**
   * 戻るボタンをクリック
   */
  async clickBack() {
    await this.page.click(this.selectors.backButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * ローディング状態か確認
   * @returns {Promise<boolean>}
   */
  async isLoading() {
    return await this.page.locator(this.selectors.loadingSpinner).isVisible();
  }

  /**
   * エラーメッセージが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async hasError() {
    return await this.page.locator(this.selectors.errorMessage).isVisible();
  }

  /**
   * Not Foundメッセージが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async isNotFound() {
    return await this.page.locator(this.selectors.notFoundMessage).isVisible();
  }

  /**
   * アクセシビリティ: 材料セクションに見出しがあるか確認
   * @returns {Promise<boolean>}
   */
  async hasIngredientsHeading() {
    const heading = this.page.locator(`${this.selectors.ingredientsSection} h2, ${this.selectors.ingredientsSection} h3`);
    return await heading.count() > 0;
  }

  /**
   * アクセシビリティ: 手順セクションに見出しがあるか確認
   * @returns {Promise<boolean>}
   */
  async hasStepsHeading() {
    const heading = this.page.locator(`${this.selectors.stepsSection} h2, ${this.selectors.stepsSection} h3`);
    return await heading.count() > 0;
  }

  /**
   * アクセシビリティ: 画像に代替テキストがあるか確認
   * @returns {Promise<boolean>}
   */
  async hasImageAltText() {
    const alt = await this.page.locator(this.selectors.image).getAttribute('alt');
    return alt !== null && alt.trim() !== '';
  }

  /**
   * アクセシビリティ: セマンティックHTMLを使用しているか確認
   * @returns {Promise<boolean>}
   */
  async hasSemanticHTML() {
    const article = this.page.locator('article');
    return await article.count() > 0;
  }
}

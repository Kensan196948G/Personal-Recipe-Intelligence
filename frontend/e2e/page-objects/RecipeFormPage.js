/**
 * レシピフォームページ ページオブジェクト
 *
 * レシピ作成・編集フォームの要素とアクションをカプセル化
 */
export class RecipeFormPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;

    // セレクター定義
    this.selectors = {
      // フォーム
      form: '[data-testid="recipe-form"]',
      heading: 'h1',

      // 基本情報フィールド
      titleInput: '[data-testid="title-input"]',
      descriptionTextarea: '[data-testid="description-textarea"]',
      categorySelect: '[data-testid="category-select"]',
      servingsInput: '[data-testid="servings-input"]',
      cookingTimeInput: '[data-testid="cooking-time-input"]',
      difficultySelect: '[data-testid="difficulty-select"]',
      imageInput: '[data-testid="image-input"]',
      imagePreview: '[data-testid="image-preview"]',

      // タグ入力
      tagsInput: '[data-testid="tags-input"]',
      tagsList: '[data-testid="tags-list"]',
      tagItem: '[data-testid="tag-item"]',
      tagRemoveButton: '[data-testid="tag-remove"]',

      // 材料セクション
      ingredientsSection: '[data-testid="ingredients-section"]',
      ingredientItem: '[data-testid="ingredient-item"]',
      ingredientNameInput: '[data-testid="ingredient-name-input"]',
      ingredientAmountInput: '[data-testid="ingredient-amount-input"]',
      addIngredientButton: '[data-testid="add-ingredient-button"]',
      removeIngredientButton: '[data-testid="remove-ingredient-button"]',

      // 手順セクション
      stepsSection: '[data-testid="steps-section"]',
      stepItem: '[data-testid="step-item"]',
      stepDescriptionTextarea: '[data-testid="step-description-textarea"]',
      addStepButton: '[data-testid="add-step-button"]',
      removeStepButton: '[data-testid="remove-step-button"]',

      // フォームアクション
      submitButton: '[data-testid="submit-button"]',
      cancelButton: '[data-testid="cancel-button"]',
      resetButton: '[data-testid="reset-button"]',

      // バリデーションエラー
      errorMessage: '[data-testid="error-message"]',
      fieldError: '[data-testid="field-error"]',
      titleError: '[data-testid="title-error"]',
      descriptionError: '[data-testid="description-error"]',

      // ローディング
      loadingSpinner: '[data-testid="loading-spinner"]',
      successMessage: '[data-testid="success-message"]',
    };
  }

  /**
   * 新規レシピ作成ページへ移動
   */
  async gotoNew() {
    await this.page.goto('/recipes/new');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * レシピ編集ページへ移動
   * @param {string} recipeId - レシピID
   */
  async gotoEdit(recipeId) {
    await this.page.goto(`/recipes/${recipeId}/edit`);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * タイトルを入力
   * @param {string} title - レシピタイトル
   */
  async fillTitle(title) {
    await this.page.fill(this.selectors.titleInput, title);
  }

  /**
   * 説明を入力
   * @param {string} description - レシピ説明
   */
  async fillDescription(description) {
    await this.page.fill(this.selectors.descriptionTextarea, description);
  }

  /**
   * カテゴリーを選択
   * @param {string} category - カテゴリー名
   */
  async selectCategory(category) {
    await this.page.selectOption(this.selectors.categorySelect, category);
  }

  /**
   * 人数を入力
   * @param {number} servings - 人数
   */
  async fillServings(servings) {
    await this.page.fill(this.selectors.servingsInput, servings.toString());
  }

  /**
   * 調理時間を入力
   * @param {number} minutes - 調理時間（分）
   */
  async fillCookingTime(minutes) {
    await this.page.fill(this.selectors.cookingTimeInput, minutes.toString());
  }

  /**
   * 難易度を選択
   * @param {string} difficulty - 難易度（easy, medium, hard）
   */
  async selectDifficulty(difficulty) {
    await this.page.selectOption(this.selectors.difficultySelect, difficulty);
  }

  /**
   * 画像をアップロード
   * @param {string} filePath - 画像ファイルパス
   */
  async uploadImage(filePath) {
    await this.page.setInputFiles(this.selectors.imageInput, filePath);
  }

  /**
   * 画像プレビューが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async hasImagePreview() {
    return await this.page.locator(this.selectors.imagePreview).isVisible();
  }

  /**
   * タグを追加
   * @param {string} tag - タグ名
   */
  async addTag(tag) {
    await this.page.fill(this.selectors.tagsInput, tag);
    await this.page.press(this.selectors.tagsInput, 'Enter');
  }

  /**
   * タグを削除
   * @param {number} index - タグのインデックス
   */
  async removeTag(index) {
    const tagItem = this.page.locator(this.selectors.tagItem).nth(index);
    await tagItem.locator(this.selectors.tagRemoveButton).click();
  }

  /**
   * タグの数を取得
   * @returns {Promise<number>}
   */
  async getTagsCount() {
    return await this.page.locator(this.selectors.tagItem).count();
  }

  /**
   * 材料を追加
   * @param {string} name - 材料名
   * @param {string} amount - 分量
   */
  async addIngredient(name, amount) {
    await this.page.click(this.selectors.addIngredientButton);
    const count = await this.page.locator(this.selectors.ingredientItem).count();
    const lastIndex = count - 1;

    const item = this.page.locator(this.selectors.ingredientItem).nth(lastIndex);
    await item.locator(this.selectors.ingredientNameInput).fill(name);
    await item.locator(this.selectors.ingredientAmountInput).fill(amount);
  }

  /**
   * 材料を削除
   * @param {number} index - 材料のインデックス
   */
  async removeIngredient(index) {
    const item = this.page.locator(this.selectors.ingredientItem).nth(index);
    await item.locator(this.selectors.removeIngredientButton).click();
  }

  /**
   * 材料の数を取得
   * @returns {Promise<number>}
   */
  async getIngredientsCount() {
    return await this.page.locator(this.selectors.ingredientItem).count();
  }

  /**
   * 手順を追加
   * @param {string} description - 手順の説明
   */
  async addStep(description) {
    await this.page.click(this.selectors.addStepButton);
    const count = await this.page.locator(this.selectors.stepItem).count();
    const lastIndex = count - 1;

    const item = this.page.locator(this.selectors.stepItem).nth(lastIndex);
    await item.locator(this.selectors.stepDescriptionTextarea).fill(description);
  }

  /**
   * 手順を削除
   * @param {number} index - 手順のインデックス
   */
  async removeStep(index) {
    const item = this.page.locator(this.selectors.stepItem).nth(index);
    await item.locator(this.selectors.removeStepButton).click();
  }

  /**
   * 手順の数を取得
   * @returns {Promise<number>}
   */
  async getStepsCount() {
    return await this.page.locator(this.selectors.stepItem).count();
  }

  /**
   * フォームを送信
   */
  async submit() {
    await this.page.click(this.selectors.submitButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * フォームをキャンセル
   */
  async cancel() {
    await this.page.click(this.selectors.cancelButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * フォームをリセット
   */
  async reset() {
    await this.page.click(this.selectors.resetButton);
  }

  /**
   * 完全なレシピを入力
   * @param {Object} recipe - レシピデータ
   */
  async fillCompleteRecipe(recipe) {
    // 基本情報
    await this.fillTitle(recipe.title);
    await this.fillDescription(recipe.description);
    await this.selectCategory(recipe.category);
    await this.fillServings(recipe.servings);
    await this.fillCookingTime(recipe.cookingTime);
    await this.selectDifficulty(recipe.difficulty);

    // タグ
    if (recipe.tags) {
      for (const tag of recipe.tags) {
        await this.addTag(tag);
      }
    }

    // 材料
    if (recipe.ingredients) {
      for (const ingredient of recipe.ingredients) {
        await this.addIngredient(ingredient.name, ingredient.amount);
      }
    }

    // 手順
    if (recipe.steps) {
      for (const step of recipe.steps) {
        await this.addStep(step);
      }
    }
  }

  /**
   * エラーメッセージが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async hasError() {
    return await this.page.locator(this.selectors.errorMessage).isVisible();
  }

  /**
   * エラーメッセージのテキストを取得
   * @returns {Promise<string>}
   */
  async getErrorMessage() {
    return await this.page.locator(this.selectors.errorMessage).textContent();
  }

  /**
   * 特定フィールドのエラーメッセージを取得
   * @param {string} fieldName - フィールド名
   * @returns {Promise<string|null>}
   */
  async getFieldError(fieldName) {
    const errorSelector = `[data-testid="${fieldName}-error"]`;
    const isVisible = await this.page.locator(errorSelector).isVisible();
    if (!isVisible) return null;
    return await this.page.locator(errorSelector).textContent();
  }

  /**
   * 成功メッセージが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async hasSuccessMessage() {
    return await this.page.locator(this.selectors.successMessage).isVisible();
  }

  /**
   * ローディング状態か確認
   * @returns {Promise<boolean>}
   */
  async isLoading() {
    return await this.page.locator(this.selectors.loadingSpinner).isVisible();
  }

  /**
   * 送信ボタンが無効化されているか確認
   * @returns {Promise<boolean>}
   */
  async isSubmitButtonDisabled() {
    return await this.page.locator(this.selectors.submitButton).isDisabled();
  }

  /**
   * アクセシビリティ: 必須フィールドにaria-requiredがあるか確認
   * @returns {Promise<boolean>}
   */
  async hasRequiredFieldsMarked() {
    const titleRequired = await this.page.locator(this.selectors.titleInput).getAttribute('aria-required');
    return titleRequired === 'true';
  }

  /**
   * アクセシビリティ: エラーメッセージがaria-liveで通知されるか確認
   * @returns {Promise<boolean>}
   */
  async hasLiveRegionForErrors() {
    const ariaLive = await this.page.locator(this.selectors.errorMessage).getAttribute('aria-live');
    return ariaLive === 'polite' || ariaLive === 'assertive';
  }
}

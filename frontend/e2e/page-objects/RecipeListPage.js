/**
 * レシピ一覧ページ ページオブジェクト
 *
 * レシピ一覧の要素とアクションをカプセル化
 */
export class RecipeListPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;

    // セレクター定義
    this.selectors = {
      // ページ要素
      heading: 'h1',
      recipeList: '[data-testid="recipe-list"]',
      recipeCard: '[data-testid="recipe-card"]',
      recipeTitle: '[data-testid="recipe-title"]',
      recipeImage: '[data-testid="recipe-image"]',
      recipeTags: '[data-testid="recipe-tags"]',

      // 検索・フィルター
      searchInput: '[data-testid="search-input"]',
      searchButton: '[data-testid="search-button"]',
      filterPanel: '[data-testid="filter-panel"]',
      filterCategory: '[data-testid="filter-category"]',
      filterTag: '[data-testid="filter-tag"]',
      filterDifficulty: '[data-testid="filter-difficulty"]',
      clearFiltersButton: '[data-testid="clear-filters"]',

      // ソート
      sortSelect: '[data-testid="sort-select"]',

      // ペジネーション
      pagination: '[data-testid="pagination"]',
      paginationPrev: '[data-testid="pagination-prev"]',
      paginationNext: '[data-testid="pagination-next"]',
      paginationPage: '[data-testid="pagination-page"]',

      // ローディング・エラー
      loadingSpinner: '[data-testid="loading-spinner"]',
      emptyState: '[data-testid="empty-state"]',
      errorMessage: '[data-testid="error-message"]',
    };
  }

  /**
   * レシピ一覧ページへ移動
   */
  async goto() {
    await this.page.goto('/recipes');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * レシピカードの数を取得
   * @returns {Promise<number>}
   */
  async getRecipeCount() {
    return await this.page.locator(this.selectors.recipeCard).count();
  }

  /**
   * 特定のレシピカードを取得
   * @param {number} index - カードのインデックス
   * @returns {import('@playwright/test').Locator}
   */
  getRecipeCard(index) {
    return this.page.locator(this.selectors.recipeCard).nth(index);
  }

  /**
   * レシピタイトルのリストを取得
   * @returns {Promise<string[]>}
   */
  async getRecipeTitles() {
    return await this.page.locator(this.selectors.recipeTitle).allTextContents();
  }

  /**
   * レシピを検索
   * @param {string} query - 検索クエリ
   */
  async search(query) {
    await this.page.fill(this.selectors.searchInput, query);
    await this.page.click(this.selectors.searchButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 検索入力欄をクリア
   */
  async clearSearch() {
    await this.page.fill(this.selectors.searchInput, '');
    await this.page.click(this.selectors.searchButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * カテゴリーフィルターを適用
   * @param {string} category - カテゴリー名
   */
  async filterByCategory(category) {
    await this.page.selectOption(this.selectors.filterCategory, category);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * タグフィルターを適用
   * @param {string} tag - タグ名
   */
  async filterByTag(tag) {
    await this.page.click(`${this.selectors.filterTag}[value="${tag}"]`);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 難易度フィルターを適用
   * @param {string} difficulty - 難易度（easy, medium, hard）
   */
  async filterByDifficulty(difficulty) {
    await this.page.selectOption(this.selectors.filterDifficulty, difficulty);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * すべてのフィルターをクリア
   */
  async clearFilters() {
    await this.page.click(this.selectors.clearFiltersButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * ソート順を変更
   * @param {string} sortBy - ソート基準（name, date, popularity）
   */
  async sortBy(sortBy) {
    await this.page.selectOption(this.selectors.sortSelect, sortBy);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * レシピカードをクリックして詳細ページへ移動
   * @param {number} index - カードのインデックス
   */
  async clickRecipeCard(index) {
    await this.getRecipeCard(index).click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 次のページへ移動
   */
  async goToNextPage() {
    await this.page.click(this.selectors.paginationNext);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 前のページへ移動
   */
  async goToPreviousPage() {
    await this.page.click(this.selectors.paginationPrev);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 特定のページへ移動
   * @param {number} pageNumber - ページ番号
   */
  async goToPage(pageNumber) {
    await this.page.click(`${this.selectors.paginationPage}[data-page="${pageNumber}"]`);
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
   * 空の状態（レシピなし）か確認
   * @returns {Promise<boolean>}
   */
  async isEmpty() {
    return await this.page.locator(this.selectors.emptyState).isVisible();
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
   * フィルターパネルが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async isFilterPanelVisible() {
    return await this.page.locator(this.selectors.filterPanel).isVisible();
  }

  /**
   * アクセシビリティ: 検索入力欄にラベルがあるか確認
   * @returns {Promise<boolean>}
   */
  async hasSearchInputLabel() {
    const ariaLabel = await this.page.locator(this.selectors.searchInput).getAttribute('aria-label');
    const ariaLabelledBy = await this.page.locator(this.selectors.searchInput).getAttribute('aria-labelledby');
    return ariaLabel !== null || ariaLabelledBy !== null;
  }

  /**
   * アクセシビリティ: レシピカードにキーボードアクセス可能か確認
   * @returns {Promise<boolean>}
   */
  async isRecipeCardKeyboardAccessible() {
    const firstCard = this.getRecipeCard(0);
    const tabIndex = await firstCard.getAttribute('tabindex');
    const role = await firstCard.getAttribute('role');
    return (tabIndex === '0' || role === 'button' || role === 'link');
  }
}

/**
 * ホームページ ページオブジェクト
 *
 * ホームページの要素とアクションをカプセル化
 */
export class HomePage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;

    // セレクター定義
    this.selectors = {
      // ヘッダー要素
      header: 'header',
      logo: '[data-testid="logo"]',
      navigation: '[data-testid="navigation"]',
      navHome: '[data-testid="nav-home"]',
      navRecipes: '[data-testid="nav-recipes"]',
      navAddRecipe: '[data-testid="nav-add-recipe"]',

      // フッター要素
      footer: 'footer',
      footerCopyright: '[data-testid="footer-copyright"]',

      // メインコンテンツ
      main: 'main',
      heading: 'h1',
      description: '[data-testid="description"]',

      // アクションボタン
      ctaButton: '[data-testid="cta-button"]',
      searchInput: '[data-testid="search-input"]',
    };
  }

  /**
   * ホームページへ移動
   */
  async goto() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * ページタイトルを取得
   * @returns {Promise<string>}
   */
  async getTitle() {
    return await this.page.title();
  }

  /**
   * ヘッダーが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async isHeaderVisible() {
    return await this.page.locator(this.selectors.header).isVisible();
  }

  /**
   * フッターが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async isFooterVisible() {
    return await this.page.locator(this.selectors.footer).isVisible();
  }

  /**
   * ロゴが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async isLogoVisible() {
    return await this.page.locator(this.selectors.logo).isVisible();
  }

  /**
   * ナビゲーションメニューが表示されているか確認
   * @returns {Promise<boolean>}
   */
  async isNavigationVisible() {
    return await this.page.locator(this.selectors.navigation).isVisible();
  }

  /**
   * メインヘッディングのテキストを取得
   * @returns {Promise<string>}
   */
  async getHeadingText() {
    return await this.page.locator(this.selectors.heading).textContent();
  }

  /**
   * レシピページへ移動
   */
  async navigateToRecipes() {
    await this.page.click(this.selectors.navRecipes);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 新規レシピ追加ページへ移動
   */
  async navigateToAddRecipe() {
    await this.page.click(this.selectors.navAddRecipe);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * CTAボタンをクリック
   */
  async clickCTA() {
    await this.page.click(this.selectors.ctaButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 検索を実行
   * @param {string} query - 検索クエリ
   */
  async search(query) {
    await this.page.fill(this.selectors.searchInput, query);
    await this.page.press(this.selectors.searchInput, 'Enter');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * アクセシビリティチェック（ARIA属性）
   * @returns {Promise<boolean>}
   */
  async hasProperARIA() {
    const header = this.page.locator(this.selectors.header);
    const main = this.page.locator(this.selectors.main);
    const footer = this.page.locator(this.selectors.footer);

    const headerRole = await header.getAttribute('role');
    const mainRole = await main.getAttribute('role');
    const footerRole = await footer.getAttribute('role');

    return headerRole === 'banner' && mainRole === 'main' && footerRole === 'contentinfo';
  }

  /**
   * キーボードナビゲーションテスト
   */
  async testKeyboardNavigation() {
    await this.page.keyboard.press('Tab');
    const focusedElement = await this.page.evaluate(() => document.activeElement.tagName);
    return focusedElement !== 'BODY';
  }
}

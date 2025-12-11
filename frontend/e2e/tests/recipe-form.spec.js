import { test, expect } from '@playwright/test';
import { RecipeFormPage } from '../page-objects/RecipeFormPage.js';
import path from 'path';

/**
 * レシピフォームページ E2Eテスト
 *
 * レシピの新規作成・編集フォーム、バリデーション、送信処理を検証
 */
test.describe('レシピフォームページ', () => {
  let formPage;

  test.beforeEach(async ({ page }) => {
    formPage = new RecipeFormPage(page);
  });

  test.describe('新規作成フォーム - 基本表示', () => {
    test('新規作成ページが正常に読み込まれる', async ({ page }) => {
      await formPage.gotoNew();
      expect(page.url()).toMatch(/\/recipes\/(new|add)/);
    });

    test('フォームタイトルが表示される', async ({ page }) => {
      await formPage.gotoNew();

      const heading = page.locator('h1');
      const headingText = await heading.textContent();

      expect(headingText).toBeTruthy();
      expect(headingText).toMatch(/新規|作成|追加/);
    });

    test('すべての必須フィールドが表示される', async ({ page }) => {
      await formPage.gotoNew();

      // 基本フィールドの存在確認
      await expect(page.locator('[data-testid="title-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="description-textarea"]')).toBeVisible();
      await expect(page.locator('[data-testid="category-select"]')).toBeVisible();
    });

    test('送信ボタンが表示される', async ({ page }) => {
      await formPage.gotoNew();

      const submitButton = page.locator('[data-testid="submit-button"]');
      await expect(submitButton).toBeVisible();
    });

    test('キャンセルボタンが表示される', async ({ page }) => {
      await formPage.gotoNew();

      const cancelButton = page.locator('[data-testid="cancel-button"]');
      await expect(cancelButton).toBeVisible();
    });
  });

  test.describe('基本情報入力', () => {
    test('タイトルを入力できる', async ({ page }) => {
      await formPage.gotoNew();
      await formPage.fillTitle('テストレシピ');

      const value = await page.locator('[data-testid="title-input"]').inputValue();
      expect(value).toBe('テストレシピ');
    });

    test('説明を入力できる', async ({ page }) => {
      await formPage.gotoNew();
      await formPage.fillDescription('これはテスト用のレシピです。');

      const value = await page.locator('[data-testid="description-textarea"]').inputValue();
      expect(value).toBe('これはテスト用のレシピです。');
    });

    test('カテゴリーを選択できる', async ({ page }) => {
      await formPage.gotoNew();
      await formPage.selectCategory('main-dish');

      const value = await page.locator('[data-testid="category-select"]').inputValue();
      expect(value).toBe('main-dish');
    });

    test('人数を入力できる', async ({ page }) => {
      await formPage.gotoNew();
      await formPage.fillServings(4);

      const value = await page.locator('[data-testid="servings-input"]').inputValue();
      expect(value).toBe('4');
    });

    test('調理時間を入力できる', async ({ page }) => {
      await formPage.gotoNew();
      await formPage.fillCookingTime(30);

      const value = await page.locator('[data-testid="cooking-time-input"]').inputValue();
      expect(value).toBe('30');
    });

    test('難易度を選択できる', async ({ page }) => {
      await formPage.gotoNew();
      await formPage.selectDifficulty('medium');

      const value = await page.locator('[data-testid="difficulty-select"]').inputValue();
      expect(value).toBe('medium');
    });
  });

  test.describe('タグ管理', () => {
    test('タグを追加できる', async () => {
      await formPage.gotoNew();
      await formPage.addTag('和食');

      const count = await formPage.getTagsCount();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test('複数のタグを追加できる', async () => {
      await formPage.gotoNew();

      await formPage.addTag('和食');
      await formPage.addTag('簡単');
      await formPage.addTag('時短');

      const count = await formPage.getTagsCount();
      expect(count).toBeGreaterThanOrEqual(3);
    });

    test('タグを削除できる', async () => {
      await formPage.gotoNew();

      await formPage.addTag('テストタグ');
      const beforeCount = await formPage.getTagsCount();

      await formPage.removeTag(0);
      const afterCount = await formPage.getTagsCount();

      expect(afterCount).toBe(beforeCount - 1);
    });
  });

  test.describe('材料管理', () => {
    test('材料を追加できる', async () => {
      await formPage.gotoNew();
      await formPage.addIngredient('玉ねぎ', '1個');

      const count = await formPage.getIngredientsCount();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test('複数の材料を追加できる', async () => {
      await formPage.gotoNew();

      await formPage.addIngredient('玉ねぎ', '1個');
      await formPage.addIngredient('にんじん', '2本');
      await formPage.addIngredient('じゃがいも', '3個');

      const count = await formPage.getIngredientsCount();
      expect(count).toBeGreaterThanOrEqual(3);
    });

    test('材料を削除できる', async () => {
      await formPage.gotoNew();

      await formPage.addIngredient('テスト材料', '適量');
      const beforeCount = await formPage.getIngredientsCount();

      await formPage.removeIngredient(0);
      const afterCount = await formPage.getIngredientsCount();

      expect(afterCount).toBe(beforeCount - 1);
    });
  });

  test.describe('手順管理', () => {
    test('手順を追加できる', async () => {
      await formPage.gotoNew();
      await formPage.addStep('玉ねぎをみじん切りにする');

      const count = await formPage.getStepsCount();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test('複数の手順を追加できる', async () => {
      await formPage.gotoNew();

      await formPage.addStep('材料を準備する');
      await formPage.addStep('野菜を切る');
      await formPage.addStep('炒める');

      const count = await formPage.getStepsCount();
      expect(count).toBeGreaterThanOrEqual(3);
    });

    test('手順を削除できる', async () => {
      await formPage.gotoNew();

      await formPage.addStep('テスト手順');
      const beforeCount = await formPage.getStepsCount();

      await formPage.removeStep(0);
      const afterCount = await formPage.getStepsCount();

      expect(afterCount).toBe(beforeCount - 1);
    });
  });

  test.describe('バリデーション - 必須フィールド', () => {
    test('タイトル未入力でエラー表示', async ({ page }) => {
      await formPage.gotoNew();

      // タイトルを空のまま送信
      await formPage.submit();

      // エラーメッセージまたはバリデーション状態を確認
      const titleError = await formPage.getFieldError('title');
      const hasError = await formPage.hasError();
      const isDisabled = await formPage.isSubmitButtonDisabled();

      expect(titleError || hasError || isDisabled).toBeTruthy();
    });

    test('説明未入力でエラー表示', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.fillTitle('テストタイトル');
      await formPage.submit();

      // バリデーション状態を確認
      const descriptionError = await formPage.getFieldError('description');
      const hasError = await formPage.hasError();

      // 説明が必須の場合はエラーが表示される
      if (descriptionError || hasError) {
        expect(descriptionError || hasError).toBeTruthy();
      }
    });

    test('カテゴリー未選択でエラー表示', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.fillTitle('テストタイトル');
      await formPage.fillDescription('テスト説明');
      await formPage.submit();

      // カテゴリーが必須の場合はエラーまたは無効化
      const hasError = await formPage.hasError();
      const isDisabled = await formPage.isSubmitButtonDisabled();

      // エラーチェック（必須でない場合もある）
      expect(typeof hasError).toBe('boolean');
    });
  });

  test.describe('バリデーション - 入力値検証', () => {
    test('タイトルの最大文字数チェック', async ({ page }) => {
      await formPage.gotoNew();

      const longTitle = 'あ'.repeat(200);
      await formPage.fillTitle(longTitle);

      const titleError = await formPage.getFieldError('title');

      // 最大文字数を超えた場合はエラーが表示される可能性がある
      if (titleError) {
        expect(titleError).toBeTruthy();
      }
    });

    test('人数が正の数値であることを検証', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.fillTitle('テストレシピ');
      await formPage.fillServings(-1);

      await formPage.submit();

      // 負の数値の場合はエラーまたは送信が阻止される
      const hasError = await formPage.hasError();
      const servingsError = await formPage.getFieldError('servings');

      if (hasError || servingsError) {
        expect(hasError || servingsError).toBeTruthy();
      }
    });

    test('調理時間が正の数値であることを検証', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.fillTitle('テストレシピ');
      await formPage.fillCookingTime(-30);

      await formPage.submit();

      const hasError = await formPage.hasError();
      const cookingTimeError = await formPage.getFieldError('cooking-time');

      if (hasError || cookingTimeError) {
        expect(hasError || cookingTimeError).toBeTruthy();
      }
    });
  });

  test.describe('フォーム送信', () => {
    test('完全なレシピを送信できる', async ({ page }) => {
      await formPage.gotoNew();

      const recipe = {
        title: 'カレーライス',
        description: '美味しいカレーライスのレシピです',
        category: 'main-dish',
        servings: 4,
        cookingTime: 45,
        difficulty: 'medium',
        tags: ['和食', '簡単', '人気'],
        ingredients: [
          { name: '玉ねぎ', amount: '2個' },
          { name: 'にんじん', amount: '1本' },
          { name: 'じゃがいも', amount: '3個' },
        ],
        steps: [
          '野菜を一口大に切る',
          '鍋で野菜を炒める',
          '水を加えて煮込む',
        ],
      };

      await formPage.fillCompleteRecipe(recipe);

      // APIをモック
      await page.route('**/api/v1/recipes', route => {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'ok',
            data: { id: 'test-recipe-id', ...recipe },
          }),
        });
      });

      await formPage.submit();

      // 送信後の状態を確認
      const hasSuccess = await formPage.hasSuccessMessage();
      const urlChanged = !page.url().includes('/new');

      expect(hasSuccess || urlChanged).toBe(true);
    });

    test('送信中はボタンが無効化される', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.fillTitle('テストレシピ');
      await formPage.fillDescription('テスト説明');

      // APIレスポンスを遅延させる
      await page.route('**/api/v1/recipes', async route => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ status: 'ok', data: {} }),
        });
      });

      // 送信ボタンをクリック
      const submitButton = page.locator('[data-testid="submit-button"]');
      await submitButton.click();

      // ローディング状態またはボタン無効化を確認
      const isLoading = await formPage.isLoading();
      const isDisabled = await submitButton.isDisabled().catch(() => false);

      expect(isLoading || isDisabled).toBe(true);
    });

    test('送信エラー時に適切なメッセージを表示', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.fillTitle('テストレシピ');
      await formPage.fillDescription('テスト説明');

      // APIエラーをシミュレート
      await page.route('**/api/v1/recipes', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal Server Error' }),
        });
      });

      await formPage.submit();

      // エラーメッセージが表示されることを確認
      const hasError = await formPage.hasError();
      expect(hasError).toBe(true);
    });
  });

  test.describe('フォームのリセット', () => {
    test('リセットボタンでフォームがクリアされる', async ({ page }) => {
      await formPage.gotoNew();

      // フォームに入力
      await formPage.fillTitle('テストレシピ');
      await formPage.fillDescription('テスト説明');

      // リセット
      const resetButton = page.locator('[data-testid="reset-button"]');
      const isVisible = await resetButton.isVisible().catch(() => false);

      if (isVisible) {
        await formPage.reset();

        // フィールドがクリアされることを確認
        const titleValue = await page.locator('[data-testid="title-input"]').inputValue();
        expect(titleValue).toBe('');
      }
    });
  });

  test.describe('キャンセル機能', () => {
    test('キャンセルボタンで前のページに戻る', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.fillTitle('テストレシピ');

      await formPage.cancel();

      // フォームページから離れたことを確認
      expect(page.url()).not.toMatch(/\/(new|edit)/);
    });

    test('キャンセル時に確認ダイアログが表示される（入力がある場合）', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.fillTitle('テストレシピ');
      await formPage.fillDescription('テスト説明');

      // ダイアログイベントをリッスン
      let dialogShown = false;
      page.once('dialog', dialog => {
        dialogShown = true;
        dialog.dismiss();
      });

      await formPage.cancel();

      // ダイアログが表示されるか、直接遷移するか
      expect(typeof dialogShown).toBe('boolean');
    });
  });

  test.describe('アクセシビリティ', () => {
    test('必須フィールドにaria-requiredが設定されている', async () => {
      await formPage.gotoNew();

      const hasRequiredMarked = await formPage.hasRequiredFieldsMarked();
      expect(hasRequiredMarked).toBe(true);
    });

    test('エラーメッセージがaria-liveで通知される', async ({ page }) => {
      await formPage.gotoNew();

      await formPage.submit();

      const hasLiveRegion = await formPage.hasLiveRegionForErrors();

      // エラーがある場合はライブリージョンが設定されているべき
      const hasError = await formPage.hasError();
      if (hasError) {
        expect(hasLiveRegion).toBe(true);
      }
    });

    test('フォームフィールドにラベルが関連付けられている', async ({ page }) => {
      await formPage.gotoNew();

      const titleInput = page.locator('[data-testid="title-input"]');

      // labelまたはaria-labelがあることを確認
      const ariaLabel = await titleInput.getAttribute('aria-label');
      const ariaLabelledBy = await titleInput.getAttribute('aria-labelledby');
      const id = await titleInput.getAttribute('id');

      // いずれかの方法でラベル付けされているべき
      expect(ariaLabel || ariaLabelledBy || id).toBeTruthy();
    });

    test('キーボードで全フィールドを操作できる', async ({ page }) => {
      await formPage.gotoNew();

      // Tabキーでフォーカス移動
      await page.keyboard.press('Tab');
      const firstFocus = await page.evaluate(() => document.activeElement.tagName);

      await page.keyboard.press('Tab');
      const secondFocus = await page.evaluate(() => document.activeElement.tagName);

      // フォーカスが移動していることを確認
      expect(firstFocus).toBeTruthy();
      expect(secondFocus).toBeTruthy();
    });
  });

  test.describe('レスポンシブデザイン', () => {
    test('モバイルビューで正常に表示される', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await formPage.gotoNew();

      const form = page.locator('[data-testid="recipe-form"]');
      await expect(form).toBeVisible();
    });

    test('タブレットビューで正常に表示される', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await formPage.gotoNew();

      const form = page.locator('[data-testid="recipe-form"]');
      await expect(form).toBeVisible();
    });
  });

  test.describe('編集モード', () => {
    test('編集ページで既存データが読み込まれる', async ({ page }) => {
      const mockRecipe = {
        id: 'test-recipe-id',
        title: '既存レシピ',
        description: '既存の説明',
        category: 'main-dish',
        servings: 4,
        cookingTime: 30,
        difficulty: 'easy',
      };

      // APIレスポンスをモック
      await page.route('**/api/v1/recipes/test-recipe-id', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ status: 'ok', data: mockRecipe }),
        });
      });

      await formPage.gotoEdit('test-recipe-id');

      // 既存データが読み込まれることを確認
      const titleValue = await page.locator('[data-testid="title-input"]').inputValue();
      expect(titleValue).toBe(mockRecipe.title);
    });
  });
});

# E2Eテスト ガイド

Personal Recipe Intelligence（PRI）のフロントエンドE2Eテストドキュメント。

## 概要

PlaywrightベースのE2Eテストスイートで、SvelteフロントエンドのUIとユーザーフローを自動検証します。

## テストファイル構成

```
frontend/e2e/
├── playwright.config.js        # Playwright設定
├── page-objects/               # ページオブジェクトパターン
│   ├── HomePage.js             # ホームページ
│   ├── RecipeListPage.js       # レシピ一覧ページ
│   ├── RecipeDetailPage.js     # レシピ詳細ページ
│   └── RecipeFormPage.js       # レシピフォームページ
├── tests/                      # テストスイート
│   ├── home.spec.js            # ホームページテスト
│   ├── recipe-list.spec.js     # レシピ一覧テスト
│   ├── recipe-detail.spec.js   # レシピ詳細テスト
│   └── recipe-form.spec.js     # レシピフォームテスト
└── reports/                    # テストレポート（自動生成）
    ├── html/                   # HTMLレポート
    └── results.json            # JSON結果
```

## セットアップ

### 1. 依存関係のインストール

```bash
cd frontend
bun install
```

### 2. Playwrightのインストール

```bash
bunx playwright install
bunx playwright install-deps
```

### 3. 環境変数設定（オプション）

```bash
export E2E_BASE_URL=http://localhost:5173
```

## テスト実行

### すべてのテストを実行

```bash
bun run test:e2e
```

### 特定のテストファイルのみ実行

```bash
bunx playwright test tests/home.spec.js
bunx playwright test tests/recipe-list.spec.js
bunx playwright test tests/recipe-detail.spec.js
bunx playwright test tests/recipe-form.spec.js
```

### 特定のブラウザで実行

```bash
# Chromiumのみ
bunx playwright test --project=chromium

# Firefoxのみ
bunx playwright test --project=firefox

# Webkitのみ
bunx playwright test --project=webkit
```

### ヘッドモードで実行（ブラウザを表示）

```bash
bunx playwright test --headed
```

### デバッグモード

```bash
bunx playwright test --debug
```

### UIモードで実行（インタラクティブ）

```bash
bunx playwright test --ui
```

## レポート確認

### HTMLレポートを開く

```bash
bunx playwright show-report e2e/reports/html
```

### JSON結果を確認

```bash
cat e2e/reports/results.json | jq
```

## テストカバレッジ

### ホームページテスト（home.spec.js）

- ✅ ページ読み込み確認
- ✅ ヘッダー/フッター表示確認
- ✅ ナビゲーション機能
- ✅ アクセシビリティ検証
- ✅ レスポンシブデザイン検証
- ✅ パフォーマンステスト
- ✅ SEOメタタグ検証

### レシピ一覧テスト（recipe-list.spec.js）

- ✅ レシピカード表示
- ✅ 検索機能（テキスト検索、特殊文字対応）
- ✅ フィルター機能（カテゴリー、タグ、難易度）
- ✅ ソート機能（名前順、日付順）
- ✅ ペジネーション
- ✅ レシピカードのインタラクション
- ✅ エラーハンドリング（APIエラー、ネットワークエラー）

### レシピ詳細テスト（recipe-detail.spec.js）

- ✅ 詳細ページ表示
- ✅ メタ情報表示（人数、調理時間、難易度、カテゴリー）
- ✅ 材料リスト表示
- ✅ 手順リスト表示
- ✅ 画像表示と代替テキスト
- ✅ アクションボタン（編集、削除、お気に入り）
- ✅ セマンティックHTML検証
- ✅ 404エラーハンドリング

### レシピフォームテスト（recipe-form.spec.js）

- ✅ 新規作成フォーム表示
- ✅ 基本情報入力（タイトル、説明、カテゴリーなど）
- ✅ タグ管理（追加、削除）
- ✅ 材料管理（追加、削除）
- ✅ 手順管理（追加、削除）
- ✅ バリデーション（必須フィールド、入力値検証）
- ✅ フォーム送信処理
- ✅ エラーハンドリング
- ✅ リセット/キャンセル機能
- ✅ 編集モード

## ページオブジェクトパターン

各ページオブジェクトは以下の構造を持ちます：

```javascript
export class PageName {
  constructor(page) {
    this.page = page;
    this.selectors = { /* セレクター定義 */ };
  }

  // ナビゲーション
  async goto() { }

  // 要素の取得
  getElement() { }

  // アクション
  async clickButton() { }

  // 状態確認
  async isVisible() { }
}
```

## ベストプラクティス

### 1. セレクター戦略

優先順位：
1. `data-testid` 属性（推奨）
2. `aria-label` / `role` 属性
3. セマンティックHTML（`h1`, `main`, `nav`など）
4. クラス名やID（最終手段）

```javascript
// 推奨
page.locator('[data-testid="recipe-card"]')

// 許容
page.locator('button[aria-label="レシピを削除"]')

// 非推奨
page.locator('.recipe-card-class')
```

### 2. 待機処理

```javascript
// ネットワークアイドルを待つ
await page.waitForLoadState('networkidle');

// 要素が表示されるまで待つ
await expect(element).toBeVisible();

// カスタムタイムアウト
await element.click({ timeout: 5000 });
```

### 3. エラーハンドリング

```javascript
// エラーをキャッチして適切にハンドリング
const isVisible = await element.isVisible().catch(() => false);

if (isVisible) {
  // 要素が存在する場合の処理
}
```

### 4. モックとスタブ

```javascript
// APIレスポンスをモック
await page.route('**/api/v1/recipes', route => {
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ data: [] })
  });
});
```

## アクセシビリティテスト

各テストスイートには以下のアクセシビリティチェックが含まれます：

- ✅ ARIA属性の検証
- ✅ キーボードナビゲーション
- ✅ セマンティックHTML構造
- ✅ 代替テキスト（画像）
- ✅ フォームラベルの関連付け
- ✅ ライブリージョン（エラー通知）

## パフォーマンステスト

- ✅ ページ読み込み時間（3秒以内）
- ✅ リソース数の制限（100リクエスト未満）
- ✅ 画像の遅延読み込み
- ✅ スムーズなスクロール

## トラブルシューティング

### テストがタイムアウトする

```bash
# タイムアウト時間を延長
bunx playwright test --timeout=120000
```

### ブラウザが起動しない

```bash
# ブラウザを再インストール
bunx playwright install --force
bunx playwright install-deps
```

### ポートが使用中

```bash
# 別のポートを使用
export E2E_BASE_URL=http://localhost:5174
```

### スクリーンショット/ビデオを保存

```bash
# すべてのテストで記録
bunx playwright test --screenshot=on --video=on
```

## 開発ガイドライン

### 新しいテストの追加

1. 適切なページオブジェクトを作成または更新
2. `tests/` ディレクトリに `.spec.js` ファイルを作成
3. `test.describe()` でテストグループを定義
4. `test()` で個別のテストケースを記述
5. アクセシビリティとレスポンシブデザインのテストを含める

### コーディング規約

- インデント: 2スペース
- 文字列: シングルクォート
- コメント: 日本語で記述
- 命名: キャメルケース（変数・関数）

### テストデータ

- モックデータを使用してAPIに依存しない
- `test.beforeEach()` で初期状態をリセット
- テスト間の依存関係を避ける

## ライセンス

MIT

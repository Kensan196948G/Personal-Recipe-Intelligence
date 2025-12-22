# E2Eテストガイド (E2E Testing Guide)

Personal Recipe Intelligence プロジェクトのE2Eテスト戦略とツール使用方法。

---

## 1. ツール構成と役割分担

### 1.1 概要

```
+----------------------+----------------------------------+
| ツール               | 役割                             |
+----------------------+----------------------------------+
| chrome-devtools MCP  | 対話的デバッグ・シナリオ検証     |
| Playwright           | 自動テスト・CI/CD・回帰テスト    |
+----------------------+----------------------------------+
```

### 1.2 chrome-devtools MCP

**用途:**
- 新機能の動作確認
- バグの調査・デバッグ
- UI/UXの検証
- テストシナリオの検討

**特徴:**
- Claude Code経由での対話的操作
- リアルタイムでの画面確認
- DOMスナップショット取得
- ネットワーク通信監視

### 1.3 Playwright

**用途:**
- 自動回帰テスト
- CI/CDパイプライン統合
- 複数ブラウザテスト
- APIテスト

**特徴:**
- スクリプトによる自動実行
- 並列テスト実行
- レポート生成
- スクリーンショット/動画記録

---

## 2. chrome-devtools MCP シナリオ検証

### 2.1 基本操作

```
=== ページ操作 ===
navigate_page     : URLへ移動
take_snapshot     : 画面状態をテキストで取得
take_screenshot   : スクリーンショット撮影
wait_for          : テキスト出現まで待機

=== 要素操作 ===
click             : 要素をクリック
fill              : テキスト入力
fill_form         : フォーム一括入力
press_key         : キーボード操作

=== デバッグ ===
list_console_messages  : コンソールログ確認
list_network_requests  : API通信確認
evaluate_script        : JavaScript実行
```

### 2.2 シナリオ検証手順

**Step 1: 事前準備**
```
1. Chromeを起動してDevToolsポートを開く
   chrome --remote-debugging-port=9222

2. バックエンド/フロントエンドを起動
   - Backend: python -m uvicorn backend.app:app --port 8001
   - Frontend: npm run dev --prefix frontend
```

**Step 2: シナリオ実行例（レシピ作成）**
```
[Claude Code での操作]

1. ページを開く
   → navigate_page: http://localhost:5173

2. 画面状態を確認
   → take_snapshot

3. 「新規作成」ボタンをクリック
   → click: uid="create-button" (snapshotで確認したuid)

4. フォームに入力
   → fill_form: [
       { uid: "title", value: "テストレシピ" },
       { uid: "description", value: "検証用" }
     ]

5. 保存ボタンをクリック
   → click: uid="save-button"

6. 成功確認
   → wait_for: "保存しました"
   → take_screenshot: evidence.png

7. エラーチェック
   → list_console_messages
```

### 2.3 検証シナリオ一覧

| シナリオID | 名前 | 検証内容 |
|------------|------|----------|
| SC-001 | レシピ一覧表示 | ホーム画面でレシピ一覧が表示される |
| SC-002 | レシピ作成 | 新規レシピを作成できる |
| SC-003 | レシピ編集 | 既存レシピを編集できる |
| SC-004 | レシピ削除 | レシピを削除できる |
| SC-005 | 検索機能 | キーワードでレシピを検索できる |
| SC-006 | タグフィルタ | タグでレシピを絞り込める |
| SC-007 | ページネーション | ページ切り替えが動作する |
| SC-008 | エラーハンドリング | エラー時に適切なメッセージが表示される |

---

## 3. Playwright 自動テスト

### 3.1 ディレクトリ構造

```
tests/
└── e2e/
    ├── recipes.spec.js    # レシピ管理テスト
    ├── fixtures/          # テストデータ
    │   └── test-data.json
    ├── reports/           # HTMLレポート出力
    └── results/           # テスト結果・スクリーンショット
```

### 3.2 テスト実行コマンド

```bash
# 全テスト実行
npx playwright test

# 特定ファイルのみ
npx playwright test recipes.spec.js

# UIモード（対話的）
npx playwright test --ui

# デバッグモード
npx playwright test --debug

# レポート表示
npx playwright show-report tests/e2e/reports
```

### 3.3 テストケース追加方法

```javascript
// tests/e2e/new-feature.spec.js
import { test, expect } from '@playwright/test';

test.describe('新機能テスト', () => {
  test('機能が動作する', async ({ page }) => {
    // chrome-devtools MCPで検証したシナリオを自動化
    await page.goto('/');
    await page.click('button:text("新機能")');
    await expect(page.locator('.result')).toBeVisible();
  });
});
```

---

## 4. ワークフロー

### 4.1 新機能開発時

```
[開発フロー]

1. 機能実装
   ↓
2. chrome-devtools MCPでシナリオ検証
   - 手動で動作確認
   - 問題点を特定・修正
   ↓
3. Playwrightテストケース作成
   - 検証済みシナリオをスクリプト化
   ↓
4. 自動テスト実行
   - npx playwright test
   ↓
5. CI/CDに組み込み
```

### 4.2 バグ調査時

```
[調査フロー]

1. バグ報告を受領
   ↓
2. chrome-devtools MCPで再現
   - navigate_page → 問題のページへ
   - take_snapshot → 画面状態確認
   - list_console_messages → エラーログ確認
   - list_network_requests → API通信確認
   ↓
3. 原因特定・修正
   ↓
4. chrome-devtools MCPで修正確認
   ↓
5. Playwrightで回帰テスト追加
```

---

## 5. CI/CD統合

### 5.1 GitHub Actions設定例

```yaml
# .github/workflows/e2e-test.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps chromium

      - name: Start backend
        run: |
          pip install -r requirements.txt
          python -m uvicorn backend.app:app --port 8001 &
          sleep 5

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: tests/e2e/reports
```

---

## 6. ベストプラクティス

### 6.1 chrome-devtools MCP

```
[推奨事項]

✓ 新しいテストケース追加前に必ずMCPで検証
✓ スナップショットでuid を確認してからクリック
✓ wait_for で安定した待機
✓ list_console_messages でエラーチェック
✓ スクリーンショットで証跡保存

[注意事項]

✗ 自動化スクリプトからの直接呼び出し不可
✗ 並列実行不可（MCP同時起動数1）
✗ Chromeが起動していないと使用不可
```

### 6.2 Playwright

```
[推奨事項]

✓ data-testid 属性でセレクタを安定化
✓ 適切なタイムアウト設定
✓ 失敗時のスクリーンショット活用
✓ 並列実行でテスト時間短縮
✓ フィクスチャでテストデータ管理

[注意事項]

✗ 脆弱なセレクタ（n番目の要素など）を避ける
✗ 固定待機（waitForTimeout）を多用しない
✗ テスト間の依存関係を作らない
```

---

更新日: 2025-12-19

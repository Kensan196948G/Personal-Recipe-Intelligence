# PWA（Progressive Web App）実装ガイド

Personal Recipe Intelligence プロジェクトのPWA化実装ドキュメント

## 実装されたファイル

### 1. Service Worker (`frontend/sw.js`)
- **キャッシュ戦略**
  - Static Assets: Cache First（CSS, JS, HTML）
  - API Requests: Network First（データの鮮度優先）
  - Dynamic Content: Cache First with Network Fallback
- **オフライン対応**
  - オフライン時は `/offline.html` を表示
  - キャッシュサイズ制限（最大50アイテム）
- **バックグラウンド同期**
  - `sync-recipes` タグで同期キューを処理
  - IndexedDB から同期待ちデータを取得して API に送信

### 2. Web App Manifest (`frontend/manifest.json`)
- **アプリ情報**
  - 名前: Personal Recipe Intelligence
  - 短縮名: PRI
  - テーマカラー: #4CAF50
- **表示モード**: standalone（ネイティブアプリライク）
- **アイコン**: 72px～512px の各サイズ対応
- **ショートカット**
  - 新しいレシピ追加
  - レシピ検索
  - お気に入り
- **共有ターゲット**: レシピURLの共有に対応

### 3. PWA登録スクリプト (`frontend/js/pwa-register.js`)
- **Service Worker 登録**
  - 自動登録と状態管理
  - エラーハンドリング
- **インストールプロンプト**
  - `beforeinstallprompt` イベントのキャプチャ
  - カスタムインストールボタンの表示
- **アップデート検出**
  - 新しいバージョンの自動検出
  - ユーザーへの通知と更新適用
- **オンライン/オフライン監視**
  - 接続状態の変化を検出
  - UI への状態反映

### 4. オフラインページ (`frontend/offline.html`)
- **ユーザーフレンドリーなデザイン**
  - グラデーション背景
  - アイコンとアニメーション
- **機能**
  - 再接続ボタン
  - ホームに戻るボタン
  - 接続状態の自動検出
  - 5秒ごとの自動再接続試行
- **オフラインでできることの説明**

### 5. IndexedDB ラッパー (`frontend/js/indexed-db.js`)
- **データストア**
  - `recipes`: レシピデータ
  - `syncQueue`: 同期待ちキュー
  - `favorites`: お気に入り
  - `tags`: タグ管理
  - `settings`: アプリ設定
- **主要メソッド**
  - `saveRecipe()`: レシピ保存
  - `getAllRecipes()`: 全レシピ取得
  - `searchRecipesByTag()`: タグ検索
  - `addToSyncQueue()`: 同期キューに追加
  - `addFavorite()`: お気に入り追加
  - `exportData()`: データエクスポート
  - `importData()`: データインポート

## セットアップ手順

### 1. 依存関係のインストール
```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend
# 依存関係がある場合はインストール
```

### 2. アイコンの準備
以下のサイズのアイコン画像を `frontend/icons/` に配置してください：
- icon-16.png (16x16)
- icon-32.png (32x32)
- icon-72.png (72x72)
- icon-96.png (96x96)
- icon-128.png (128x128)
- icon-144.png (144x144)
- icon-152.png (152x152)
- icon-192.png (192x192)
- icon-384.png (384x384)
- icon-512.png (512x512)
- icon-maskable-192.png (192x192, maskable用)
- icon-maskable-512.png (512x512, maskable用)

### 3. HTMLファイルへの統合
既存の `index.html` に以下を追加：

```html
<head>
  <!-- PWA Manifest -->
  <link rel="manifest" href="/manifest.json">

  <!-- Apple Touch Icon -->
  <link rel="apple-touch-icon" href="/icons/icon-192.png">

  <!-- Theme Color -->
  <meta name="theme-color" content="#4CAF50">
</head>

<body>
  <!-- PWA UI Elements -->
  <button id="pwa-install-button">アプリをインストール</button>

  <div id="pwa-update-notification">
    <h3>新しいバージョンがあります</h3>
    <p>アプリを最新バージョンに更新してください。</p>
    <button class="update-button">今すぐ更新</button>
  </div>

  <div id="pwa-connection-status"></div>

  <!-- Scripts -->
  <script src="/js/indexed-db.js"></script>
  <script src="/js/pwa-register.js"></script>
</body>
```

### 4. WebサーバーでHTTPSを有効化
PWAはHTTPS環境が必須です（localhost除く）。

```bash
# 開発環境の場合
# backend/dev.sh で既にHTTPSが設定されているか確認
```

### 5. 動作確認

#### Service Worker の確認
1. ブラウザの開発者ツールを開く
2. Application タブ → Service Workers
3. Service Worker が登録されていることを確認

#### キャッシュの確認
1. Application タブ → Cache Storage
2. `pri-v1.0.0-static`, `pri-v1.0.0-dynamic`, `pri-v1.0.0-api` が存在することを確認

#### IndexedDB の確認
1. Application タブ → IndexedDB
2. `PRIDatabase` が存在し、各ストアが作成されていることを確認

#### オフライン動作の確認
1. Network タブで「Offline」にチェック
2. ページをリロード
3. キャッシュされたコンテンツが表示されることを確認
4. `/offline.html` が表示されることを確認

## 使用方法

### アプリのインストール
1. 対応ブラウザでアクセス
2. 「アプリをインストール」ボタンをクリック
3. プロンプトで「インストール」を選択

### レシピの保存（オフライン対応）
```javascript
// レシピを保存
await dbManager.saveRecipe({
  title: 'カレーライス',
  ingredients: ['玉ねぎ', 'にんじん', '牛肉'],
  steps: ['材料を切る', '炒める', '煮込む'],
  tags: ['和食', '簡単']
});

// レシピを取得
const recipes = await dbManager.getAllRecipes();

// タグで検索
const curryRecipes = await dbManager.searchRecipesByTag('和食');
```

### 同期キューの使用
```javascript
// オフライン時の変更を同期キューに追加
await dbManager.addToSyncQueue(
  'create-recipe',
  '/api/v1/recipes',
  'POST',
  { title: 'カレーライス', ... }
);

// バックグラウンド同期を登録
await pwaManager.registerBackgroundSync('sync-recipes');
```

### お気に入り管理
```javascript
// お気に入りに追加
await dbManager.addFavorite(recipeId);

// お気に入りから削除
await dbManager.removeFavorite(recipeId);

// お気に入り一覧を取得
const favorites = await dbManager.getFavorites();
```

## イベントハンドリング

### PWA イベント
```javascript
// Service Worker 登録完了
window.addEventListener('pwa:sw-registered', (event) => {
  console.log('Service Worker registered:', event.detail.registration);
});

// インストール可能
window.addEventListener('pwa:install-available', (event) => {
  console.log('Install available');
});

// アプリインストール完了
window.addEventListener('pwa:app-installed', (event) => {
  console.log('App installed');
});

// アップデート可能
window.addEventListener('pwa:update-available', (event) => {
  console.log('Update available');
});

// オンライン
window.addEventListener('pwa:online', (event) => {
  console.log('Online');
});

// オフライン
window.addEventListener('pwa:offline', (event) => {
  console.log('Offline');
});
```

## キャッシュ戦略

### Cache First (Static Assets)
```
Request → Cache → Network (if not in cache) → Cache → Response
```
静的ファイル（HTML, CSS, JS）に最適。高速表示を実現。

### Network First (API)
```
Request → Network → Cache (fallback) → Response
```
API リクエストに最適。最新データを優先しつつ、オフライン対応。

## トラブルシューティング

### Service Worker が登録されない
- HTTPS が有効か確認（localhost は例外）
- ブラウザのコンソールでエラーを確認
- Service Worker のスコープを確認

### キャッシュが更新されない
- Service Worker のバージョンを更新（`CACHE_VERSION`）
- ブラウザの開発者ツールで「Update on reload」を有効化
- キャッシュを手動でクリア

### オフラインで動作しない
- Service Worker が active 状態か確認
- キャッシュに必要なファイルが含まれているか確認
- Network タブで「Offline」時のリクエストを確認

### IndexedDB エラー
- ブラウザの IndexedDB サポートを確認
- ストレージ容量を確認
- データベースバージョンの競合を確認

## パフォーマンス最適化

### 推奨事項
1. **静的アセットの最小化**: CSS/JS を minify
2. **画像の最適化**: WebP 形式を使用
3. **レイジーローディング**: 画像とコンポーネントの遅延読み込み
4. **キャッシュサイズ制限**: 適切な上限を設定（現在50アイテム）
5. **定期的な同期**: バックグラウンド同期の適切な間隔設定

## セキュリティ考慮事項

- **HTTPS必須**: Service Worker は HTTPS 環境でのみ動作
- **データ検証**: IndexedDB に保存する前にバリデーション
- **機密データ**: トークンやAPIキーはキャッシュしない
- **CSP設定**: Content Security Policy を適切に設定

## ブラウザサポート

| 機能 | Chrome | Firefox | Safari | Edge |
|------|--------|---------|--------|------|
| Service Worker | ✓ | ✓ | ✓ | ✓ |
| Web App Manifest | ✓ | ✓ | ✓ | ✓ |
| IndexedDB | ✓ | ✓ | ✓ | ✓ |
| Background Sync | ✓ | × | × | ✓ |
| Push Notifications | ✓ | ✓ | △ | ✓ |

## 今後の拡張

1. **プッシュ通知**: レシピ更新時の通知
2. **バックグラウンド同期の強化**: より複雑な同期ロジック
3. **データ圧縮**: IndexedDB のストレージ効率化
4. **共有機能**: Web Share API の活用
5. **オフライン検索**: 全文検索の IndexedDB 実装

## 参考リソース

- [MDN: Progressive Web Apps](https://developer.mozilla.org/ja/docs/Web/Progressive_web_apps)
- [Google: PWA Checklist](https://web.dev/pwa-checklist/)
- [Service Worker Cookbook](https://serviceworke.rs/)
- [IndexedDB API](https://developer.mozilla.org/ja/docs/Web/API/IndexedDB_API)

## ライセンス

MIT License - CLAUDE.md に準拠

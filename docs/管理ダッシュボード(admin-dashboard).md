# 管理者ダッシュボード - 使用ガイド

## 概要

Personal Recipe Intelligence の管理者ダッシュボードは、システムの統計情報、設定管理、ログ監視、ヘルスチェックを提供する管理者専用ツールです。

## 機能一覧

### 1. 概要ダッシュボード
- システム全体の統計情報
  - レシピ総数（公開/非公開）
  - ユーザー数（総数/アクティブ）
  - タグ数
  - ストレージ使用量
- グラフ表示
  - レシピの公開設定（円グラフ）
  - 人気タグ TOP 10（棒グラフ）
- システムヘルスチェック
  - データベース接続
  - ディスク容量
  - メモリ使用率
  - データディレクトリ書き込み権限

### 2. レシピ統計
- 期間指定（7日/30日/90日/1年）での統計
- 日別レシピ作成数（折れ線グラフ）
- ソース別レシピ数（棒グラフ）
- 平均調理時間・平均人数

### 3. ユーザー統計
- 期間指定での統計
- 新規ユーザー数
- アクティブユーザー数
- 日別ログイン数（折れ線グラフ）
- レシピ投稿ランキング TOP 10

### 4. システム設定
- 基本設定
  - サイト名
  - デフォルト言語
  - タイムゾーン
- 機能設定
  - 公開レシピの有効/無効
  - ユーザー登録の有効/無効
  - OCR機能の有効/無効
  - スクレイピング機能の有効/無効
  - メンテナンスモード
- 制限設定
  - 最大アップロードサイズ
  - ユーザーあたりの最大レシピ数
  - ページネーションサイズ
  - キャッシュTTL

### 5. システムログ
- ログレベルフィルタ（ERROR/WARNING/INFO/DEBUG）
- 最新50件のログ表示
- タイムスタンプ・レベル・メッセージ

## セットアップ

### 1. 管理者APIキーの設定

`.env` ファイルに管理者APIキーを設定します：

```bash
# .env
ADMIN_API_KEY=your_secure_admin_api_key_here
```

**重要:** 本番環境では必ず強力なランダム文字列を使用してください。

```bash
# ランダム文字列の生成例
openssl rand -hex 32
```

### 2. バックエンドAPI の起動

管理者ダッシュボードのエンドポイントは自動的に有効になります。

```bash
cd backend
python -m uvicorn main:app --reload
```

### 3. フロントエンドの起動

```bash
cd frontend
npm start
# または
bun start
```

### 4. アクセス

ブラウザで以下にアクセス：

```
http://localhost:3000/admin
```

## 使用方法

### ログイン

1. 管理者ダッシュボードにアクセス
2. `.env` で設定した `ADMIN_API_KEY` を入力
3. 「ログイン」ボタンをクリック

トークンは `localStorage` に保存され、次回以降は自動的にログイン状態が維持されます。

### 統計の閲覧

1. 「概要」タブで全体の統計を確認
2. 「レシピ統計」または「ユーザー統計」タブで詳細を確認
3. 期間セレクタで集計期間を変更可能

### 設定の変更

1. 「設定」タブを開く
2. 変更したい設定項目を編集
3. 「設定を保存」ボタンをクリック

設定は即座に `data/settings.json` に保存されます。

### ログの確認

1. 「ログ」タブを開く
2. フィルタでログレベルを選択
3. 最新のログエントリーが表示されます

### キャッシュのクリア

統計データは5分間キャッシュされます。最新のデータを取得するには：

1. 「概要」タブを開く
2. 「統計キャッシュをクリア」ボタンをクリック

## APIエンドポイント

すべてのエンドポイントは Bearer Token 認証が必要です。

### 統計API

```bash
# システム統計
GET /api/v1/admin/stats
Authorization: Bearer {ADMIN_API_KEY}

# レシピ統計
GET /api/v1/admin/stats/recipes?days=30
Authorization: Bearer {ADMIN_API_KEY}

# ユーザー統計
GET /api/v1/admin/stats/users?days=30
Authorization: Bearer {ADMIN_API_KEY}
```

### 設定API

```bash
# 設定取得
GET /api/v1/admin/settings
Authorization: Bearer {ADMIN_API_KEY}

# 設定更新
PUT /api/v1/admin/settings
Authorization: Bearer {ADMIN_API_KEY}
Content-Type: application/json

{
  "site_name": "My Recipe Site",
  "maintenance_mode": false
}
```

### ログAPI

```bash
# ログ取得
GET /api/v1/admin/logs?limit=50&level=ERROR
Authorization: Bearer {ADMIN_API_KEY}
```

### ヘルスチェックAPI

```bash
# ヘルスチェック
GET /api/v1/admin/health
Authorization: Bearer {ADMIN_API_KEY}
```

### キャッシュAPI

```bash
# キャッシュクリア
POST /api/v1/admin/cache/clear
Authorization: Bearer {ADMIN_API_KEY}
```

## cURL サンプル

```bash
# 環境変数設定
export ADMIN_TOKEN="your_admin_api_key"

# システム統計
curl -X GET "http://localhost:8001/api/v1/admin/stats" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"

# レシピ統計（30日間）
curl -X GET "http://localhost:8001/api/v1/admin/stats/recipes?days=30" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"

# 設定更新
curl -X PUT "http://localhost:8001/api/v1/admin/settings" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "maintenance_mode": true,
    "max_upload_size_mb": 20
  }'

# ヘルスチェック
curl -X GET "http://localhost:8001/api/v1/admin/health" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

## セキュリティ

### 管理者APIキーの管理

1. **強力なキーを使用**: 32文字以上のランダム文字列を推奨
2. **定期的な更新**: 定期的にキーを変更
3. **環境変数で管理**: `.env` ファイルを使用し、バージョン管理には含めない
4. **HTTPS使用**: 本番環境では必ずHTTPSを使用

### アクセス制限

- 管理者ダッシュボードは信頼できるネットワークからのみアクセス
- ファイアウォールで適切にポートを保護
- VPN経由でのアクセスを推奨

### 監査ログ

設定変更やキャッシュクリアなどの管理操作は自動的にログに記録されます。

## トラブルシューティング

### ログインできない

1. `.env` ファイルの `ADMIN_API_KEY` が正しく設定されているか確認
2. バックエンドAPIが起動しているか確認
3. ブラウザのコンソールでエラーを確認

### 統計が表示されない

1. データベースにデータが存在するか確認
2. データベース接続が正常か確認（ヘルスチェック）
3. キャッシュをクリアして再試行

### 設定が保存されない

1. `data/` ディレクトリの書き込み権限を確認
2. ディスク容量を確認
3. バックエンドログでエラーを確認

### ヘルスチェックでエラーが出る

- **database error**: データベース接続を確認
- **disk warning**: ディスク容量を確認（90%以上で警告）
- **data_directory error**: `data/` ディレクトリの権限を確認

## パフォーマンス

### キャッシュ

統計データは5分間キャッシュされます。大量のデータがある場合、初回取得に時間がかかる可能性があります。

キャッシュTTLは設定で変更可能：

```json
{
  "cache_ttl_seconds": 300
}
```

### データベース最適化

大量のレシピがある場合、定期的にデータベースの最適化を実施：

```bash
sqlite3 data/recipes.db "VACUUM;"
```

## FAQ

### Q: 管理者アカウントは複数作れますか？

A: 現在の実装では単一の管理者APIキーのみサポートしています。複数の管理者が必要な場合は、同じキーを共有するか、ユーザーベースの認証システムの実装が必要です。

### Q: 統計データをエクスポートできますか？

A: 現在、Web UIからの直接エクスポートはサポートしていません。APIエンドポイントから JSON 形式でデータを取得し、別途処理してください。

### Q: メンテナンスモードとは何ですか？

A: メンテナンスモードを有効にすると、一般ユーザーのアクセスを制限できます（実装依存）。現在は設定項目のみで、実際の制限機能は別途実装が必要です。

### Q: ログはどこに保存されますか？

A: ログは `logs/` ディレクトリに保存されます。ファイル名は日付ベースでローテーションされます。

## 今後の機能拡張

- [ ] グラフのエクスポート機能
- [ ] 統計データのCSVエクスポート
- [ ] メール通知機能
- [ ] より詳細なユーザー管理機能
- [ ] コンテンツモデレーション機能
- [ ] APIレート制限の設定
- [ ] ロールベースアクセス制御（RBAC）

## 関連ドキュメント

- [API仕様](./API.md)
- [セキュリティガイド](./SECURITY.md)
- [データベーススキーマ](./DATABASE.md)

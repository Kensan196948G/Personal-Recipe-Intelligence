# API概要 (API Overview)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) の API 仕様の概要を定義する。

## 2. 基本情報

### 2.1 API バージョン
- 現行バージョン: **v1**
- ベースURL: `http://localhost:8000/api/v1`

### 2.2 API スタイル
- **RESTful API**
- JSON ベースのリクエスト/レスポンス

### 2.3 認証
- 個人利用のため認証なし（localhost のみ）
- 将来的には API Key 認証を検討

## 3. エンドポイント一覧

### 3.1 レシピ (Recipes)

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| GET | /recipes | レシピ一覧取得 |
| GET | /recipes/{id} | レシピ詳細取得 |
| POST | /recipes | レシピ作成 |
| PUT | /recipes/{id} | レシピ更新 |
| DELETE | /recipes/{id} | レシピ削除 |
| GET | /recipes/search | レシピ検索 |

### 3.2 材料 (Ingredients)

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| GET | /ingredients | 材料一覧取得 |
| GET | /ingredients/{id} | 材料詳細取得 |
| POST | /ingredients | 材料作成 |
| PUT | /ingredients/{id} | 材料更新 |
| DELETE | /ingredients/{id} | 材料削除 |

### 3.3 タグ (Tags)

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| GET | /tags | タグ一覧取得 |
| GET | /tags/{id} | タグ詳細取得 |
| POST | /tags | タグ作成 |
| PUT | /tags/{id} | タグ更新 |
| DELETE | /tags/{id} | タグ削除 |

### 3.4 スクレイピング (Scraping)

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| POST | /scrape | URLからレシピ取得 |
| GET | /scrape/supported | 対応サイト一覧 |

### 3.5 OCR

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| POST | /ocr | 画像からレシピ抽出 |
| POST | /ocr/preview | OCR プレビュー |

### 3.6 システム (System)

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| GET | /health | ヘルスチェック |
| GET | /version | バージョン情報 |
| GET | /stats | 統計情報 |

## 4. 共通仕様

### 4.1 リクエストヘッダー

```http
Content-Type: application/json
Accept: application/json
```

### 4.2 レスポンス形式

**成功時**
```json
{
  "status": "ok",
  "data": { ... },
  "error": null
}
```

**エラー時**
```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ"
  }
}
```

### 4.3 ステータスコード

| コード | 説明 |
|--------|------|
| 200 | 成功 |
| 201 | 作成成功 |
| 204 | 削除成功 |
| 400 | リクエスト不正 |
| 404 | リソース未発見 |
| 409 | 競合 |
| 422 | バリデーションエラー |
| 500 | サーバーエラー |

### 4.4 ページネーション

```json
{
  "status": "ok",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
}
```

**クエリパラメータ**
| パラメータ | 型 | デフォルト | 説明 |
|------------|-----|-----------|------|
| page | int | 1 | ページ番号 |
| per_page | int | 20 | 1ページあたりの件数 |

## 5. エラーコード

| コード | 説明 |
|--------|------|
| VALIDATION_ERROR | バリデーションエラー |
| NOT_FOUND | リソースが見つからない |
| ALREADY_EXISTS | リソースが既に存在 |
| SCRAPE_FAILED | スクレイピング失敗 |
| OCR_FAILED | OCR 処理失敗 |
| TRANSLATION_FAILED | 翻訳失敗 |
| INTERNAL_ERROR | 内部エラー |

## 6. レート制限

- 個人利用のため制限なし

## 7. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |

# 外部レシピサイト連携機能 仕様書

## 概要

Personal Recipe Intelligence における外部レシピサイトからのレシピインポート機能の仕様書。

## 対応サイト

### 1. Cookpad (cookpad.com)
- JSON-LD 構造化データ対応
- HTML パース フォールバック対応

### 2. クラシル (kurashiru.com)
- JSON-LD 構造化データ対応
- HTML パース フォールバック対応

### 3. DELISH KITCHEN (delishkitchen.tv)
- JSON-LD 構造化データ対応
- HTML パース フォールバック対応

### 4. 汎用 (Schema.org Recipe 対応サイト)
- JSON-LD 構造化データ対応
- マイクロデータ対応
- ヒューリスティック解析フォールバック

## アーキテクチャ

```
ExternalRecipeService (サービス層)
  ├── CookpadParser
  ├── KurashiruParser
  ├── DelishKitchenParser
  └── GenericRecipeParser (フォールバック)
```

## データ構造

### RecipeData

```python
{
  "title": str,                    # レシピタイトル
  "ingredients": [                 # 材料リスト
    {
      "name": str,                 # 材料名（正規化済み）
      "amount": str,               # 分量
      "unit": str                  # 単位
    }
  ],
  "steps": [str],                  # 手順リスト
  "description": str | None,       # 説明
  "servings": str | None,          # 分量（何人分）
  "cooking_time": str | None,      # 調理時間
  "image_url": str | None,         # 画像URL
  "source_url": str | None,        # 元URL
  "tags": [str],                   # タグリスト
  "author": str | None             # 作者名
}
```

## API エンドポイント

### POST /api/v1/external/import

URLからレシピをインポート

**リクエスト:**
```json
{
  "url": "https://cookpad.com/recipe/123456"
}
```

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "title": "美味しいカレー",
    "ingredients": [...],
    "steps": [...],
    ...
  },
  "error": null
}
```

### POST /api/v1/external/preview

レシピのプレビューを取得（インポート前確認用）

**リクエスト:**
```json
{
  "url": "https://cookpad.com/recipe/123456"
}
```

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "title": "美味しいカレー",
    "description": "簡単で美味しいカレーです",
    "image_url": "https://...",
    "cooking_time": "30分",
    "servings": "4人分",
    "ingredient_count": 8,
    "step_count": 5,
    "source_url": "https://...",
    "author": "料理人"
  },
  "error": null
}
```

### GET /api/v1/external/supported-sites

対応サイト一覧を取得

**レスポンス:**
```json
{
  "status": "ok",
  "data": [
    {
      "name": "Cookpad",
      "domain": "cookpad.com",
      "icon": "🍳"
    },
    {
      "name": "クラシル",
      "domain": "kurashiru.com",
      "icon": "📱"
    },
    ...
  ],
  "error": null
}
```

## 実装詳細

### パーサー選択フロー

1. URL を解析してドメインを取得
2. 各パーサーの `can_parse()` を順番に実行
3. 最初にマッチしたパーサーを使用
4. マッチしなければ GenericRecipeParser を使用（フォールバック）

### データ抽出フロー

1. **JSON-LD 抽出試行**
   - `<script type="application/ld+json">` を検索
   - Recipe タイプを探す
   - 成功すれば構造化データを使用

2. **マイクロデータ抽出試行**（GenericRecipeParser のみ）
   - `itemtype="*Recipe"` を検索
   - itemprop から値を抽出

3. **HTML パース（フォールバック）**
   - class名、id名などからヒューリスティックに抽出
   - タイトル、材料、手順を推測

### 材料正規化

- カタカナ → ひらがな変換
- 分量と単位の分離
- 単位リスト: 個、本、枚、g、kg、ml、L、カップ、大さじ、小さじ、適量、少々

### 時間パース

ISO 8601 duration を日本語に変換:
- `PT30M` → `30分`
- `PT1H` → `1時間`
- `PT1H30M` → `1時間30分`

## フロントエンドコンポーネント

### ExternalRecipeImport.jsx

**機能:**
- URL入力フォーム
- プレビュー表示
- インポート確認
- 対応サイト一覧表示

**状態管理:**
- `url`: 入力されたURL
- `loading`: ローディング状態
- `preview`: プレビューデータ
- `error`: エラーメッセージ
- `importSuccess`: インポート成功フラグ
- `supportedSites`: 対応サイト一覧

## テスト

### テスト項目

1. **RecipeData クラス**
   - 初期化
   - カタカナ正規化
   - 辞書変換

2. **各パーサー**
   - URL判定
   - JSON-LD パース
   - HTML パース
   - 材料パース
   - 時間パース

3. **ExternalRecipeService**
   - パーサー選択
   - URL検証
   - レシピインポート

### テスト実行

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pytest backend/tests/test_external_recipe.py -v
```

## セキュリティ考慮事項

1. **URL検証**
   - 妥当なURLのみ許可
   - スキーム（http/https）検証

2. **HTTP リクエスト**
   - タイムアウト: 30秒
   - リダイレクト追従: 有効
   - User-Agent 設定

3. **データサニタイズ**
   - HTMLタグ除去
   - XSS対策

## パフォーマンス

- HTTP リクエストタイムアウト: 30秒
- 非同期処理による高速化
- BeautifulSoup による高速HTMLパース

## エラーハンドリング

1. **URL取得失敗**
   - HTTP エラー → 400 Bad Request
   - タイムアウト → 400 Bad Request

2. **パース失敗**
   - 構造化データなし → ヒューリスティック解析へフォールバック
   - すべて失敗 → 400 Bad Request

3. **サポート外サイト**
   - GenericRecipeParser でフォールバック試行
   - 失敗時は適切なエラーメッセージ

## 今後の拡張

1. **対応サイト追加**
   - 楽天レシピ
   - Nadia
   - その他人気レシピサイト

2. **機能強化**
   - レシピの重複チェック
   - 自動タグ付け
   - 画像ダウンロード

3. **パフォーマンス改善**
   - キャッシュ機構
   - バッチインポート

## ファイル構成

```
backend/
  services/
    external_recipe_service.py       # サービス本体
    recipe_parsers/
      __init__.py
      cookpad_parser.py              # Cookpad パーサー
      kurashiru_parser.py            # クラシル パーサー
      delish_kitchen_parser.py       # DELISH KITCHEN パーサー
      generic_recipe_parser.py       # 汎用パーサー
  api/
    routers/
      external_recipe.py             # APIルーター
  tests/
    test_external_recipe.py          # テスト

frontend/
  components/
    ExternalRecipeImport.jsx         # UIコンポーネント

docs/
  external-recipe-integration.md     # 本ドキュメント
```

## 依存ライブラリ

- fastapi: Web フレームワーク
- httpx: HTTP クライアント
- beautifulsoup4: HTML パーサー
- lxml: XML/HTML パーサー
- pydantic: データバリデーション

## 参考

- [Schema.org Recipe](https://schema.org/Recipe)
- [JSON-LD](https://json-ld.org/)
- [Microdata](https://www.w3.org/TR/microdata/)

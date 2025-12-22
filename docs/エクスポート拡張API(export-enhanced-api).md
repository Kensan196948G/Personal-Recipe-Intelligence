# エクスポート強化API仕様

## 概要

Personal Recipe Intelligence のデータエクスポート強化機能を提供するAPIです。
複数フォーマットでのエクスポート、レシピブック生成、買い物リスト、栄養レポート、バックアップ/リストア機能を提供します。

## エンドポイント

### 1. 対応フォーマット一覧取得

対応しているエクスポートフォーマットの一覧を取得します。

**エンドポイント:** `GET /api/v1/export/formats`

**レスポンス例:**
```json
{
  "json": {
    "name": "JSON",
    "mime": "application/json",
    "ext": ".json"
  },
  "csv": {
    "name": "CSV",
    "mime": "text/csv",
    "ext": ".csv"
  },
  "xml": {
    "name": "XML (RecipeML)",
    "mime": "application/xml",
    "ext": ".xml"
  },
  "markdown": {
    "name": "Markdown",
    "mime": "text/markdown",
    "ext": ".md"
  },
  "pdf": {
    "name": "PDF",
    "mime": "application/pdf",
    "ext": ".pdf"
  }
}
```

---

### 2. レシピエクスポート

指定したレシピを選択したフォーマットでエクスポートします。

**エンドポイント:** `POST /api/v1/export/recipes`

**リクエストボディ:**
```json
{
  "recipe_ids": ["recipe-001", "recipe-002"],
  "format": "json",
  "options": {
    "indent": 2,
    "ensure_ascii": false
  }
}
```

**パラメータ:**
- `recipe_ids` (required): エクスポート対象のレシピIDリスト
- `format` (optional, default: "json"): エクスポートフォーマット (json/csv/xml/markdown/pdf)
- `options` (optional): フォーマット固有のオプション

**レスポンス:**
- Content-Type: 選択したフォーマットに応じたMIMEタイプ
- Content-Disposition: `attachment; filename="recipes.{ext}"`
- Body: エクスポートデータ（バイナリ）

---

### 3. レシピブック生成

複数のレシピを1つのPDFファイルにまとめたレシピブックを生成します。

**エンドポイント:** `POST /api/v1/export/recipe-book`

**リクエストボディ:**
```json
{
  "recipe_ids": ["recipe-001", "recipe-002", "recipe-003"],
  "title": "私のお気に入りレシピ集",
  "theme": "elegant",
  "options": {
    "include_index": true,
    "page_numbers": true
  }
}
```

**パラメータ:**
- `recipe_ids` (required): レシピIDリスト
- `title` (optional, default: "レシピブック"): ブックタイトル
- `theme` (optional, default: "default"): テーマ (default/elegant/modern)
- `options` (optional): その他オプション

**レスポンス:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="recipe_book.pdf"`
- Body: PDFデータ（バイナリ）

---

### 4. 買い物リストエクスポート

選択したレシピの材料をまとめた買い物リストを生成します。
同じ材料は自動的に集計されます。

**エンドポイント:** `POST /api/v1/export/shopping-list`

**リクエストボディ:**
```json
{
  "recipe_ids": ["recipe-001", "recipe-002"],
  "format": "markdown",
  "options": {}
}
```

**パラメータ:**
- `recipe_ids` (required): レシピIDリスト
- `format` (optional, default: "markdown"): エクスポートフォーマット (markdown/json)
- `options` (optional): その他オプション

**レスポンス例（Markdown）:**
```markdown
# 買い物リスト

エクスポート日時: 2025年01月01日 10:00:00

対象レシピ数: 2件

## 材料一覧

- [ ] 玉ねぎ 3 個
- [ ] じゃがいも 3 個
- [ ] にんじん 1 本
- [ ] 豚肉 300 g
- [ ] パスタ 200 g

---

## 使用レシピ

- カレーライス
- パスタカルボナーラ
```

---

### 5. 栄養レポートエクスポート

レシピの栄養情報を集計したレポートを生成します。

**エンドポイント:** `POST /api/v1/export/nutrition-report`

**リクエストボディ:**
```json
{
  "recipe_ids": ["recipe-001", "recipe-002"],
  "format": "json",
  "options": {}
}
```

**パラメータ:**
- `recipe_ids` (required): レシピIDリスト
- `format` (optional, default: "json"): エクスポートフォーマット (json/csv)
- `options` (optional): その他オプション

**レスポンス例（JSON）:**
```json
{
  "exported_at": "2025-01-01T10:00:00",
  "recipe_count": 2,
  "recipes": [
    {
      "id": "recipe-001",
      "title": "カレーライス",
      "nutrition": {
        "calories": 550,
        "protein": 25,
        "fat": 18,
        "carbohydrates": 65
      }
    },
    {
      "id": "recipe-002",
      "title": "パスタカルボナーラ",
      "nutrition": {
        "calories": 680,
        "protein": 30,
        "fat": 28,
        "carbohydrates": 75
      }
    }
  ]
}
```

---

### 6. フルバックアップ作成

全レシピデータをJSONファイルにバックアップします。

**エンドポイント:** `POST /api/v1/export/backup`

**リクエストボディ:**
```json
{
  "metadata": {
    "note": "月次バックアップ"
  }
}
```

**パラメータ:**
- `metadata` (optional): バックアップに関するメタデータ

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "backup_file": "/path/to/data/backups/backup_20250101_100000.json",
    "recipe_count": 42
  },
  "error": null
}
```

---

### 7. バックアップからリストア

バックアップファイルからレシピデータをリストアします。

**エンドポイント:** `POST /api/v1/export/restore`

**リクエストボディ:**
```json
{
  "backup_file": "/path/to/data/backups/backup_20250101_100000.json"
}
```

**パラメータ:**
- `backup_file` (required): バックアップファイルのパス

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "restored_recipe_count": 42,
    "backup_created_at": "2025-01-01T10:00:00"
  },
  "error": null
}
```

**エラーレスポンス:**
- 404: バックアップファイルが見つからない
- 400: 不正なバックアップファイル

---

### 8. バックアップ一覧取得

作成済みバックアップの一覧を取得します。

**エンドポイント:** `GET /api/v1/export/backups`

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "backups": [
      {
        "file": "/path/to/data/backups/backup_20250101_120000.json",
        "filename": "backup_20250101_120000.json",
        "created_at": "2025-01-01T12:00:00",
        "recipe_count": 45,
        "size_bytes": 125648
      },
      {
        "file": "/path/to/data/backups/backup_20250101_100000.json",
        "filename": "backup_20250101_100000.json",
        "created_at": "2025-01-01T10:00:00",
        "recipe_count": 42,
        "size_bytes": 118234
      }
    ],
    "count": 2
  },
  "error": null
}
```

---

## エクスポートフォーマット詳細

### JSON
- 完全な構造化データ
- インデント設定可能
- 日本語対応（ensure_ascii: false推奨）

### CSV
- Excel互換（BOM付きUTF-8）
- 各レシピが1行に展開される
- 材料・手順はセミコロン区切り

### XML (RecipeML)
- RecipeML 0.5互換
- 階層構造を保持
- メタデータ完全対応

### Markdown
- 可読性の高いテキスト形式
- GitHub/GitLab等で表示可能
- 画像リンク対応

### PDF
- 日本語フォント対応（Noto Sans CJK / IPAゴシック）
- テーブルレイアウト
- ページ区切り対応

---

## 使用例

### cURLでのエクスポート

```bash
# JSON形式でエクスポート
curl -X POST http://localhost:8001/api/v1/export/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_ids": ["recipe-001", "recipe-002"],
    "format": "json"
  }' \
  -o recipes.json

# レシピブック生成
curl -X POST http://localhost:8001/api/v1/export/recipe-book \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_ids": ["recipe-001", "recipe-002", "recipe-003"],
    "title": "家族のレシピ集"
  }' \
  -o recipe_book.pdf

# 買い物リスト生成
curl -X POST http://localhost:8001/api/v1/export/shopping-list \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_ids": ["recipe-001", "recipe-002"],
    "format": "markdown"
  }' \
  -o shopping_list.md

# バックアップ作成
curl -X POST http://localhost:8001/api/v1/export/backup \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "note": "定期バックアップ"
    }
  }'
```

---

## エラーコード

- **400 Bad Request**: 不正なリクエストパラメータ
- **404 Not Found**: レシピまたはバックアップファイルが見つからない
- **500 Internal Server Error**: エクスポート処理の失敗

---

## 実装詳細

### 日本語PDF対応

システムに以下のフォントがインストールされている必要があります：

- Noto Sans CJK
- IPAゴシック

インストール方法（Ubuntu）:
```bash
sudo apt-get install fonts-noto-cjk fonts-ipafont-gothic
```

### バックアップファイル形式

```json
{
  "backup_version": "1.0",
  "created_at": "2025-01-01T10:00:00",
  "recipe_count": 42,
  "metadata": {
    "note": "任意のメモ"
  },
  "recipes": [
    // レシピデータの配列
  ]
}
```

---

## セキュリティ考慮事項

1. **ファイルパス検証**: バックアップファイルのパスは厳密に検証
2. **データサイズ制限**: 大量データのエクスポートはタイムアウト考慮
3. **権限チェック**: 本番環境では認証・認可を実装すること

---

## パフォーマンス

- JSON/CSV/Markdown: 1000件のレシピで 1秒未満
- PDF: 100件のレシピで 5秒程度（フォント読み込み含む）
- バックアップ: データ量に依存（10MB程度で1秒未満）

---

## 今後の拡張

- [ ] Google Drive / Dropbox へのエクスポート
- [ ] スケジュールバックアップ
- [ ] インクリメンタルバックアップ
- [ ] 画像付きPDFエクスポート
- [ ] カスタムテンプレート機能

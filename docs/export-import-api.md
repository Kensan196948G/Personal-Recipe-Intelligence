# Export/Import API Documentation

Personal Recipe Intelligence のレシピエクスポート・インポート機能のドキュメント

## 概要

JSON形式でのレシピデータのエクスポート・インポート機能を提供します。

### 主な機能

- 全レシピのエクスポート
- 単一レシピのエクスポート
- 選択したレシピ群のエクスポート
- JSONファイルからのインポート
- インポート前のバリデーション
- 重複チェックと処理オプション

---

## エクスポート機能

### 1. 全レシピエクスポート

**エンドポイント:** `GET /api/v1/export/recipes`

**パラメータ:**
- `download` (boolean, optional): ファイルとしてダウンロードするか (デフォルト: false)

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "version": "1.0",
    "exported_at": "2025-12-11T10:30:00.000000",
    "recipe_count": 100,
    "recipes": [
      {
        "id": 1,
        "title": "カレーライス",
        "source_url": "https://example.com/curry",
        "source_type": "web",
        "ingredients": [
          {
            "name": "玉ねぎ",
            "amount": "2",
            "unit": "個"
          },
          {
            "name": "豚肉",
            "amount": "300",
            "unit": "g"
          }
        ],
        "steps": [
          "玉ねぎをみじん切りにする",
          "豚肉を一口大に切る",
          "鍋で炒める"
        ],
        "cooking_time": 45,
        "servings": 4,
        "tags": ["簡単", "定番"],
        "notes": "辛さはお好みで調整",
        "created_at": "2025-12-01T09:00:00.000000",
        "updated_at": "2025-12-10T15:30:00.000000"
      }
    ]
  }
}
```

**使用例:**

```bash
# 通常のエクスポート
curl -X GET "http://localhost:8000/api/v1/export/recipes"

# ファイルダウンロード
curl -X GET "http://localhost:8000/api/v1/export/recipes?download=true" \
  -o recipes_export.json
```

---

### 2. 単一レシピエクスポート

**エンドポイント:** `GET /api/v1/export/recipes/{recipe_id}`

**パスパラメータ:**
- `recipe_id` (integer, required): レシピID

**クエリパラメータ:**
- `download` (boolean, optional): ファイルとしてダウンロードするか

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "version": "1.0",
    "exported_at": "2025-12-11T10:35:00.000000",
    "recipe_count": 1,
    "recipes": [
      {
        "id": 42,
        "title": "特製ハンバーグ",
        "ingredients": [...],
        "steps": [...]
      }
    ]
  }
}
```

**使用例:**

```bash
# レシピID 42をエクスポート
curl -X GET "http://localhost:8000/api/v1/export/recipes/42"

# ファイルとしてダウンロード
curl -X GET "http://localhost:8000/api/v1/export/recipes/42?download=true" \
  -o recipe_42.json
```

---

### 3. バッチエクスポート

**エンドポイント:** `POST /api/v1/export/recipes/batch`

**リクエストボディ:**
```json
{
  "recipe_ids": [1, 5, 10, 15]
}
```

**クエリパラメータ:**
- `download` (boolean, optional): ファイルとしてダウンロードするか

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "version": "1.0",
    "exported_at": "2025-12-11T10:40:00.000000",
    "recipe_count": 4,
    "recipes": [...]
  }
}
```

**使用例:**

```bash
# 複数レシピをエクスポート
curl -X POST "http://localhost:8000/api/v1/export/recipes/batch" \
  -H "Content-Type: application/json" \
  -d '{"recipe_ids": [1, 5, 10, 15]}'

# ファイルとしてダウンロード
curl -X POST "http://localhost:8000/api/v1/export/recipes/batch?download=true" \
  -H "Content-Type: application/json" \
  -d '{"recipe_ids": [1, 5, 10, 15]}' \
  -o selected_recipes.json
```

---

## インポート機能

### 4. インポート前バリデーション

**エンドポイント:** `POST /api/v1/import/validate`

**リクエストボディ:**
```json
{
  "data": {
    "version": "1.0",
    "exported_at": "2025-12-11T10:00:00.000000",
    "recipe_count": 2,
    "recipes": [...]
  },
  "check_duplicates": true
}
```

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "is_valid": true,
    "total_recipes": 2,
    "valid_recipes": 2,
    "invalid_recipes": 0,
    "errors": [],
    "warnings": [
      {
        "type": "version_mismatch",
        "message": "Version 2.0 may not be fully compatible"
      }
    ],
    "duplicates": [
      {
        "index": 0,
        "title": "カレーライス",
        "duplicate_info": {
          "id": 10,
          "title": "カレーライス",
          "source_url": "https://example.com/curry"
        }
      }
    ]
  }
}
```

**使用例:**

```bash
# バリデーション実行
curl -X POST "http://localhost:8000/api/v1/import/validate" \
  -H "Content-Type: application/json" \
  -d @recipes_to_import.json
```

---

### 5. JSONデータインポート

**エンドポイント:** `POST /api/v1/import/recipes`

**リクエストボディ:**
```json
{
  "data": {
    "version": "1.0",
    "exported_at": "2025-12-11T10:00:00.000000",
    "recipe_count": 3,
    "recipes": [...]
  },
  "skip_duplicates": true,
  "overwrite_duplicates": false
}
```

**パラメータ説明:**
- `skip_duplicates`: 重複レシピをスキップ (デフォルト: true)
- `overwrite_duplicates`: 重複レシピを上書き (デフォルト: false)

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "success": true,
    "imported_count": 2,
    "skipped_count": 1,
    "failed_count": 0,
    "details": [
      {
        "index": 0,
        "title": "新しいレシピ",
        "status": "imported",
        "recipe_id": 101
      },
      {
        "index": 1,
        "title": "カレーライス",
        "status": "skipped",
        "reason": "duplicate",
        "duplicate_id": 10
      },
      {
        "index": 2,
        "title": "パスタ",
        "status": "imported",
        "recipe_id": 102
      }
    ]
  }
}
```

**使用例:**

```bash
# 重複をスキップしてインポート
curl -X POST "http://localhost:8000/api/v1/import/recipes" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {...},
    "skip_duplicates": true,
    "overwrite_duplicates": false
  }'

# 重複を上書き
curl -X POST "http://localhost:8000/api/v1/import/recipes" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {...},
    "skip_duplicates": false,
    "overwrite_duplicates": true
  }'
```

---

### 6. ファイルからインポート

**エンドポイント:** `POST /api/v1/import/recipes/file`

**リクエスト形式:** multipart/form-data

**パラメータ:**
- `file` (file, required): JSONファイル
- `skip_duplicates` (boolean, optional): 重複をスキップ (デフォルト: true)
- `overwrite_duplicates` (boolean, optional): 重複を上書き (デフォルト: false)

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "success": true,
    "imported_count": 5,
    "skipped_count": 2,
    "failed_count": 0,
    "details": [...]
  }
}
```

**使用例:**

```bash
# ファイルからインポート
curl -X POST "http://localhost:8000/api/v1/import/recipes/file" \
  -F "file=@recipes_export.json"

# パラメータ付きでインポート
curl -X POST "http://localhost:8000/api/v1/import/recipes/file?skip_duplicates=false&overwrite_duplicates=true" \
  -F "file=@recipes_export.json"
```

---

## ヘルスチェック

**エンドポイント:** `GET /api/v1/export/health`

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "service": "export-import",
    "version": "1.0",
    "endpoints": [
      "GET /api/v1/export/recipes",
      "GET /api/v1/export/recipes/{recipe_id}",
      "POST /api/v1/export/recipes/batch",
      "POST /api/v1/import/validate",
      "POST /api/v1/import/recipes",
      "POST /api/v1/import/recipes/file"
    ]
  }
}
```

---

## エラーレスポンス

### 404 Not Found
```json
{
  "detail": "Recipe with ID 999 not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid JSON file: Expecting value: line 1 column 1 (char 0)"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "recipe_ids"],
      "msg": "ensure this value has at least 1 items",
      "type": "value_error.list.min_items"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Export failed: Database connection error"
}
```

---

## データスキーマ

### RecipeExportSchema

```typescript
{
  id?: number;                    // レシピID（任意）
  title: string;                  // タイトル（必須）
  source_url?: string;            // ソースURL
  source_type: string;            // ソースタイプ（デフォルト: "manual"）
  ingredients: Array<{            // 材料リスト（必須）
    name: string;
    amount?: string;
    unit?: string;
  }>;
  steps: Array<string>;           // 手順リスト（必須）
  cooking_time?: number;          // 調理時間（分）
  servings?: number;              // 人数
  tags?: Array<string>;           // タグ
  notes?: string;                 // メモ
  image_path?: string;            // 画像パス
  created_at?: string;            // 作成日時（ISO8601）
  updated_at?: string;            // 更新日時（ISO8601）
}
```

---

## Python SDK 使用例

```python
from backend.services.export_service import ExportService, export_to_file, import_from_file

# サービス初期化
export_service = ExportService(db_session=db)

# 全レシピエクスポート
export_data = export_service.export_all_recipes()

# ファイルに保存
export_to_file(export_data, "/path/to/export.json")

# ファイルから読み込み
import_data = import_from_file("/path/to/import.json")

# バリデーション
validation_result = export_service.validate_import_data(import_data)

if validation_result.is_valid:
    # インポート実行
    import_result = export_service.import_recipes(
        import_data,
        skip_duplicates=True,
        overwrite_duplicates=False
    )

    print(f"Imported: {import_result.imported_count}")
    print(f"Skipped: {import_result.skipped_count}")
    print(f"Failed: {import_result.failed_count}")
```

---

## セキュリティ考慮事項

1. **ファイルサイズ制限**: 大きすぎるファイルのアップロードを防ぐ
2. **入力バリデーション**: すべての入力データはPydanticで検証
3. **SQL インジェクション対策**: ORMを使用した安全なDB操作
4. **レート制限**: 必要に応じてAPI呼び出し回数を制限

---

## パフォーマンス

- エクスポート処理: レシピ1000件あたり約2秒
- インポート処理: レシピ1000件あたり約5秒（バリデーション含む）
- ファイルサイズ: レシピ1件あたり約1-2KB（JSON）

---

## トラブルシューティング

### Q: インポート時に "validation_error" が発生する

A: JSONデータのスキーマを確認してください。特に `title`、`ingredients`、`steps` は必須項目です。

### Q: 重複チェックの基準は？

A: タイトルとソースURLの組み合わせで判定します。

### Q: インポート時に一部のレシピが失敗する

A: `details` フィールドを確認し、各レシピの `status` と `error` を確認してください。

---

## 今後の拡張予定

- [ ] CSV形式のエクスポート/インポート
- [ ] 画像ファイルの一括エクスポート
- [ ] インポート時のマージオプション
- [ ] スケジュールエクスポート機能
- [ ] クラウドストレージ連携

---

## 関連ドキュメント

- [API 仕様書](/docs/api-spec.md)
- [データベーススキーマ](/docs/database-schema.md)
- [開発ガイド](/README.md)

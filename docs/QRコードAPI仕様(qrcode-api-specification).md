# QRコード共有機能 API仕様書

## 概要
Personal Recipe Intelligence のレシピQRコード共有機能のAPI仕様書

---

## エンドポイント一覧

### 1. レシピQRコード取得（PNG）
**エンドポイント**: `GET /api/v1/qrcode/{recipe_id}`

**説明**: レシピ共有用QRコード画像を取得（PNG形式）

**パスパラメータ**:
- `recipe_id` (int, required): レシピID

**クエリパラメータ**:
| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| `box_size` | int | 10 | QRコードのボックスサイズ（1-50） |
| `border` | int | 4 | QRコードのボーダー幅（0-10） |
| `fill_color` | string | "black" | QRコードの色 |
| `back_color` | string | "white" | 背景色 |
| `style` | enum | "square" | QRコードスタイル（square/rounded/circle） |
| `add_logo` | bool | false | ロゴ埋め込みフラグ |

**レスポンス**:
- Content-Type: `image/png`
- PNG画像データ

**使用例**:
```bash
curl -o recipe_123.png "http://localhost:8001/api/v1/qrcode/123?box_size=15&style=rounded"
```

---

### 2. レシピQRコード取得（SVG）
**エンドポイント**: `GET /api/v1/qrcode/{recipe_id}/svg`

**説明**: レシピ共有用QRコード画像を取得（SVG形式）

**パスパラメータ**:
- `recipe_id` (int, required): レシピID

**クエリパラメータ**:
| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| `box_size` | int | 10 | QRコードのボックスサイズ（1-50） |
| `border` | int | 4 | QRコードのボーダー幅（0-10） |
| `fill_color` | string | "black" | QRコードの色 |
| `back_color` | string | "white" | 背景色 |

**レスポンス**:
- Content-Type: `image/svg+xml`
- SVG画像データ

**使用例**:
```bash
curl "http://localhost:8001/api/v1/qrcode/123/svg" > recipe_123.svg
```

---

### 3. レシピQRコードデータ取得
**エンドポイント**: `GET /api/v1/qrcode/{recipe_id}/data`

**説明**: レシピQRコードに埋め込まれるデータを取得

**パスパラメータ**:
- `recipe_id` (int, required): レシピID

**レスポンス**:
```json
{
  "status": "ok",
  "data": {
    "recipe_id": 123,
    "url": "http://localhost:8001/recipe/123",
    "qrcode_png_url": "/api/v1/qrcode/123",
    "qrcode_svg_url": "/api/v1/qrcode/123/svg"
  },
  "error": null
}
```

**使用例**:
```bash
curl "http://localhost:8001/api/v1/qrcode/123/data"
```

---

### 4. レシピデータ埋め込みQRコード生成
**エンドポイント**: `POST /api/v1/qrcode/{recipe_id}/data-embed`

**説明**: レシピデータを埋め込んだQRコードを生成（データモード）

**パスパラメータ**:
- `recipe_id` (int, required): レシピID

**クエリパラメータ**:
| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| `format` | enum | "png" | 出力形式（png/svg） |
| `box_size` | int | 10 | QRコードのボックスサイズ（1-50） |
| `border` | int | 4 | QRコードのボーダー幅（0-10） |
| `fill_color` | string | "black" | QRコードの色 |
| `back_color` | string | "white" | 背景色 |
| `style` | enum | "square" | QRコードスタイル（square/rounded/circle） |
| `add_logo` | bool | false | ロゴ埋め込みフラグ |

**リクエストボディ**:
```json
{
  "name": "カレーライス",
  "url": "https://example.com/curry",
  "ingredients": ["玉ねぎ", "じゃがいも", "にんじん", "カレールー"],
  "steps": [
    "野菜を一口大に切る",
    "鍋で炒める",
    "水を加えて煮込む",
    "カレールーを溶かす"
  ]
}
```

**レスポンス**:
- Content-Type: `image/png` または `image/svg+xml`
- 画像データ

**使用例**:
```bash
curl -X POST "http://localhost:8001/api/v1/qrcode/123/data-embed?format=png" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "カレーライス",
    "url": "https://example.com/curry",
    "ingredients": ["玉ねぎ", "じゃがいも"],
    "steps": ["炒める", "煮込む"]
  }' \
  -o recipe_123_data.png
```

---

## QRコードスタイル

### スタイル一覧
1. **square**: 標準の正方形スタイル
2. **rounded**: 角丸スタイル
3. **circle**: 円形スタイル

### カラーカスタマイズ
- `fill_color`: QRコード本体の色（例: "black", "#FF0000", "rgb(255,0,0)"）
- `back_color`: 背景色（例: "white", "#FFFFFF", "transparent"）

### ロゴ埋め込み
- `add_logo=true` でロゴをQRコード中央に埋め込み
- ロゴファイルは `QRCodeService` 初期化時に指定
- エラー訂正レベル HIGH により読み取り精度を維持

---

## データモードの制限

### QRコード容量
- バージョン自動調整（最大40）
- データサイズが大きい場合は自動的にバージョンアップ
- 推奨データサイズ: 1KB 以下

### レシピデータのコンパクト化
埋め込みデータは以下の形式に最適化:
```json
{
  "id": 123,
  "name": "レシピ名",
  "url": "元URL",
  "ingredients": ["材料1", "材料2"],
  "steps": ["手順1", "手順2"]
}
```

---

## エラーレスポンス

### 500 Internal Server Error
```json
{
  "detail": "QRコード生成エラー: <エラー詳細>"
}
```

---

## セキュリティ

### 入力バリデーション
- `box_size`: 1-50 の範囲制限
- `border`: 0-10 の範囲制限
- `fill_color`, `back_color`: 文字列形式チェック

### レート制限
- 個人用途のため未実装
- 必要に応じて将来実装

---

## 使用例（統合）

### Python
```python
import requests

# PNG取得
response = requests.get("http://localhost:8001/api/v1/qrcode/123?style=rounded&fill_color=blue")
with open("qrcode.png", "wb") as f:
    f.write(response.content)

# SVG取得
response = requests.get("http://localhost:8001/api/v1/qrcode/123/svg")
with open("qrcode.svg", "w") as f:
    f.write(response.text)

# データモード
recipe_data = {
    "name": "カレーライス",
    "url": "https://example.com/curry",
    "ingredients": ["玉ねぎ", "じゃがいも"],
    "steps": ["炒める", "煮込む"]
}
response = requests.post(
    "http://localhost:8001/api/v1/qrcode/123/data-embed",
    json=recipe_data
)
with open("qrcode_data.png", "wb") as f:
    f.write(response.content)
```

### JavaScript
```javascript
// PNG取得
fetch('http://localhost:8001/api/v1/qrcode/123?style=circle')
  .then(res => res.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    document.getElementById('qrcode-img').src = url;
  });

// データ取得
fetch('http://localhost:8001/api/v1/qrcode/123/data')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 統合方法

### FastAPI アプリへの統合
```python
from fastapi import FastAPI
from backend.api.routers import qrcode

app = FastAPI()
app.include_router(qrcode.router)
```

---

## 依存関係インストール
```bash
pip install -r requirements-qrcode.txt
```

---

## テスト実行
```bash
pytest backend/tests/test_qrcode_service.py -v
```

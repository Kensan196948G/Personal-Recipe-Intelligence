# カメラ統合機能 セットアップガイド

Personal Recipe Intelligence のカメラ統合機能のセットアップと使用方法

## クイックスタート

### 1. ファイル構成の確認

以下のファイルが正しく配置されていることを確認してください。

```
personal-recipe-intelligence/
├── frontend/
│   ├── js/
│   │   ├── camera-service.js
│   │   ├── image-processor.js
│   │   └── barcode-scanner.js
│   ├── components/
│   │   ├── CameraCapture.jsx
│   │   ├── RecipePhotoCapture.jsx
│   │   └── CameraExample.jsx
│   └── tests/
│       ├── camera-service.test.js
│       ├── image-processor.test.js
│       └── barcode-scanner.test.js
├── docs/
│   ├── camera-integration.md
│   └── camera-setup-guide.md
└── scripts/
    └── test-camera.sh
```

### 2. 依存関係のインストール

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend

# Bunを使用（推奨）
bun install

# または npm
npm install
```

### 3. テストの実行

```bash
# すべてのカメラ関連テストを実行
bash ../scripts/test-camera.sh

# または個別に実行
bun test tests/camera-service.test.js
bun test tests/image-processor.test.js
bun test tests/barcode-scanner.test.js

# カバレッジ付き
bash ../scripts/test-camera.sh --coverage
```

### 4. 開発サーバーの起動

```bash
# HTTPS必須（カメラアクセスのため）
bun run dev --https

# または自己署名証明書を使用
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
bun run dev --cert cert.pem --key key.pem
```

---

## 基本的な使用方法

### カメラ撮影の実装

```jsx
import React, { useState } from 'react';
import CameraCapture from './components/CameraCapture.jsx';

function MyComponent() {
  const [showCamera, setShowCamera] = useState(false);

  const handleCapture = async (blob) => {
    // 撮影した画像をサーバーに送信
    const formData = new FormData();
    formData.append('image', blob, 'photo.jpg');

    try {
      const response = await fetch('/api/v1/recipes/ocr', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        console.log('レシピ抽出成功:', result);
      }
    } catch (error) {
      console.error('エラー:', error);
    }

    setShowCamera(false);
  };

  return (
    <div>
      <button onClick={() => setShowCamera(true)}>
        レシピを撮影
      </button>

      {showCamera && (
        <CameraCapture
          onCapture={handleCapture}
          onClose={() => setShowCamera(false)}
          allowGallery={true}
          autoRotate={true}
        />
      )}
    </div>
  );
}
```

### 複数枚撮影の実装

```jsx
import React, { useState } from 'react';
import RecipePhotoCapture from './components/RecipePhotoCapture.jsx';

function RecipeForm() {
  const [showCamera, setShowCamera] = useState(false);

  const handleComplete = async (blobs) => {
    // 複数の画像をサーバーに送信
    const formData = new FormData();
    blobs.forEach((blob, index) => {
      formData.append('images', blob, `page-${index}.jpg`);
    });

    try {
      const response = await fetch('/api/v1/recipes/ocr-multi', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        console.log('複数ページ処理完了:', result);
      }
    } catch (error) {
      console.error('エラー:', error);
    }

    setShowCamera(false);
  };

  return (
    <div>
      <button onClick={() => setShowCamera(true)}>
        レシピを撮影（複数ページ）
      </button>

      {showCamera && (
        <RecipePhotoCapture
          onComplete={handleComplete}
          onClose={() => setShowCamera(false)}
          maxPhotos={5}
          showGuide={true}
        />
      )}
    </div>
  );
}
```

---

## バックエンドAPI実装例

### OCRエンドポイント（単一画像）

```python
# backend/api/recipes.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Optional
import logging

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])
logger = logging.getLogger(__name__)

@router.post("/ocr")
async def ocr_recipe(image: UploadFile = File(...)):
    """
    画像からレシピをOCR抽出
    """
    try:
        # 画像データを読み込み
        image_data = await image.read()

        # OCR処理（適切なOCRライブラリを使用）
        # 例: Tesseract, Google Cloud Vision, Azure Computer Vision
        recipe_text = await extract_text_from_image(image_data)

        # レシピ構造化
        structured_recipe = parse_recipe_text(recipe_text)

        return {
            "status": "ok",
            "data": structured_recipe,
            "error": None
        }

    except Exception as e:
        logger.error(f"OCR処理エラー: {e}")
        raise HTTPException(status_code=500, detail="OCR処理に失敗しました")


async def extract_text_from_image(image_data: bytes) -> str:
    """
    画像からテキストを抽出
    """
    # Tesseractの例
    from PIL import Image
    import pytesseract
    import io

    image = Image.open(io.BytesIO(image_data))
    text = pytesseract.image_to_string(image, lang='jpn')

    return text


def parse_recipe_text(text: str) -> dict:
    """
    テキストからレシピを構造化
    """
    # 正規表現やNLPでレシピを解析
    # 材料、分量、手順などを抽出

    return {
        "title": "抽出されたレシピ名",
        "ingredients": [
            {"name": "玉ねぎ", "amount": "1個"},
            {"name": "にんじん", "amount": "1本"}
        ],
        "steps": [
            "玉ねぎをみじん切りにする",
            "にんじんを乱切りにする"
        ]
    }
```

### OCRエンドポイント（複数画像）

```python
@router.post("/ocr-multi")
async def ocr_recipe_multi(images: list[UploadFile] = File(...)):
    """
    複数画像からレシピをOCR抽出
    """
    try:
        all_text = []

        for image in images:
            image_data = await image.read()
            text = await extract_text_from_image(image_data)
            all_text.append(text)

        # 複数ページを結合
        combined_text = "\n\n".join(all_text)

        # レシピ構造化
        structured_recipe = parse_recipe_text(combined_text)

        return {
            "status": "ok",
            "data": structured_recipe,
            "pages": len(images),
            "error": None
        }

    except Exception as e:
        logger.error(f"複数画像OCR処理エラー: {e}")
        raise HTTPException(status_code=500, detail="OCR処理に失敗しました")
```

### バーコード検索エンドポイント

```python
@router.get("/ingredients/barcode/{barcode}")
async def get_ingredient_by_barcode(barcode: str):
    """
    バーコードから食材情報を取得
    """
    try:
        # データベースまたは外部APIで検索
        ingredient = await search_ingredient_by_barcode(barcode)

        if not ingredient:
            raise HTTPException(status_code=404, detail="食材が見つかりません")

        return {
            "status": "ok",
            "data": ingredient,
            "error": None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"バーコード検索エラー: {e}")
        raise HTTPException(status_code=500, detail="検索に失敗しました")


async def search_ingredient_by_barcode(barcode: str) -> Optional[dict]:
    """
    バーコードから食材を検索
    """
    # データベース検索の例
    from database import get_db

    db = get_db()
    ingredient = db.query(Ingredient).filter(
        Ingredient.barcode == barcode
    ).first()

    if ingredient:
        return {
            "id": ingredient.id,
            "name": ingredient.name,
            "barcode": ingredient.barcode,
            "category": ingredient.category
        }

    return None
```

---

## トラブルシューティング

### カメラが起動しない

**原因1**: HTTPS接続が必要

```bash
# 開発環境でHTTPSを有効化
bun run dev --https

# または自己署名証明書を生成
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

**原因2**: ブラウザの権限が拒否されている

ブラウザの設定でカメラ権限を確認してください。

Chrome: `chrome://settings/content/camera`
Firefox: `about:preferences#privacy`

### バーコードが検出されない

**原因1**: BarcodeDetector APIが非対応

```javascript
// サポート確認
if ('BarcodeDetector' in window) {
  console.log('対応しています');
} else {
  console.log('非対応です。ポリフィルが必要です。');
}
```

**原因2**: 照明不足

フラッシュを有効化するか、明るい場所で試してください。

### 画像サイズが大きすぎる

圧縮設定を調整してください。

```javascript
import imageProcessor from './js/image-processor.js';

const compressed = await imageProcessor.compress(blob, {
  quality: 0.7,      // 品質を下げる
  maxSizeMB: 1       // 1MB以下に制限
});
```

### テストが失敗する

```bash
# キャッシュをクリア
rm -rf node_modules
bun install

# テストを再実行
bash scripts/test-camera.sh
```

---

## パフォーマンス最適化

### 1. 解像度の最適化

```javascript
// モバイルデバイスでは低解像度
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);
const maxWidth = isMobile ? 1280 : 1920;
const maxHeight = isMobile ? 720 : 1080;
```

### 2. 画像圧縮の最適化

```javascript
// OCR用には低品質でも十分
const ocrBlob = await imageProcessor.compress(blob, {
  quality: 0.7,
  maxSizeMB: 1
});
```

### 3. レイジーローディング

```jsx
import React, { lazy, Suspense } from 'react';

const CameraCapture = lazy(() => import('./components/CameraCapture.jsx'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <CameraCapture />
    </Suspense>
  );
}
```

---

## セキュリティ考慮事項

### 1. HTTPS必須

本番環境では必ずHTTPSを使用してください。

### 2. 権限の適切な管理

ユーザー操作後にのみカメラを起動してください。

```javascript
// 良い例
button.addEventListener('click', async () => {
  await cameraService.startCamera();
});

// 悪い例（ページロード時に起動）
window.onload = async () => {
  await cameraService.startCamera(); // NG
};
```

### 3. ストリームの適切な停止

コンポーネントのクリーンアップで必ずストリームを停止してください。

```jsx
useEffect(() => {
  return () => {
    cameraService.stopCamera();
  };
}, []);
```

### 4. 画像データの取り扱い

不要になったBlobは速やかに破棄してください。

```javascript
const url = URL.createObjectURL(blob);
// 使用後
URL.revokeObjectURL(url);
```

---

## よくある質問（FAQ）

### Q: iOSでカメラが起動しない

A: iOSではHTTPSが必須です。また、`playsinline`属性も必要です。

```jsx
<video autoPlay playsInline muted />
```

### Q: Androidでフラッシュが動作しない

A: 一部のAndroidデバイスではトーチモードがサポートされていません。

```javascript
const capabilities = cameraService.getCapabilities();
if (capabilities.torch) {
  await cameraService.setFlash(true);
}
```

### Q: 画像が横向きになる

A: `autoRotate`オプションを有効化してください。

```jsx
<CameraCapture autoRotate={true} />
```

### Q: テストでモック化できない

A: グローバルオブジェクトを適切にモック化してください。

```javascript
global.navigator = {
  mediaDevices: {
    getUserMedia: mock(async () => mockStream)
  }
};
```

---

## 次のステップ

1. [完全なドキュメント](camera-integration.md)を確認
2. [使用例](../frontend/components/CameraExample.jsx)を参照
3. バックエンドAPIを実装
4. 本番環境にデプロイ

---

## サポート

問題が発生した場合は、GitHubのIssueを作成してください。

- エラーメッセージ
- ブラウザ情報
- 再現手順

を含めてください。

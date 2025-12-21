# カメラ統合機能ドキュメント

Personal Recipe Intelligence のネイティブカメラ統合機能の完全ドキュメント

## 目次

1. [概要](#概要)
2. [機能一覧](#機能一覧)
3. [ファイル構成](#ファイル構成)
4. [セットアップ](#セットアップ)
5. [使用方法](#使用方法)
6. [API リファレンス](#api-リファレンス)
7. [ブラウザ互換性](#ブラウザ互換性)
8. [トラブルシューティング](#トラブルシューティング)

---

## 概要

Personal Recipe Intelligence のカメラ統合機能は、レシピの撮影とOCR処理を簡単に行うためのモジュール群です。

### 主な特徴

- **MediaDevices API**: ネイティブカメラアクセス
- **高度な画像処理**: リサイズ、圧縮、回転補正
- **バーコード/QRコード**: 食材検索とレシピ共有
- **複数枚撮影**: レシピの複数ページ対応
- **レスポンシブUI**: モバイル・デスクトップ対応

---

## 機能一覧

### 1. カメラサービス (`camera-service.js`)

| 機能 | 説明 |
|------|------|
| カメラ起動/停止 | MediaDevices APIによるカメラアクセス |
| 前面/背面切り替え | facingMode による切り替え |
| 解像度設定 | 最大1920x1080の高画質撮影 |
| フラッシュ制御 | トーチモードの有効/無効 |
| ズーム制御 | デバイスがサポートする場合のズーム |
| デバイス列挙 | 利用可能なカメラデバイス一覧 |

### 2. 画像処理 (`image-processor.js`)

| 機能 | 説明 |
|------|------|
| リサイズ | アスペクト比維持のリサイズ |
| 圧縮 | JPEG品質調整とファイルサイズ制限 |
| クロッピング | 指定領域の切り出し |
| 回転補正 | 90/180/270度の回転 |
| 自動回転 | EXIF情報に基づく自動回転 |
| グレースケール | モノクロ変換（OCR精度向上） |
| 明るさ・コントラスト | 画像の調整 |

### 3. バーコードスキャナー (`barcode-scanner.js`)

| 機能 | 説明 |
|------|------|
| バーコード検出 | BarcodeDetector APIによるリアルタイム検出 |
| QRコード読み取り | レシピ共有用QRコード |
| 食材バーコード | 商品バーコードからの食材情報取得 |
| 対応形式 | QR, EAN-13, EAN-8, Code 128, UPC-A/E など |
| 画像検出 | 静止画からの検出 |
| ハイライト表示 | 検出結果の視覚化 |

### 4. カメラUIコンポーネント (`CameraCapture.jsx`)

- ライブプレビュー
- シャッターボタン
- ギャラリー選択
- カメラ切り替え
- フラッシュボタン
- プレビュー/再撮影

### 5. レシピ写真撮影 (`RecipePhotoCapture.jsx`)

- 複数枚撮影（最大5枚）
- 撮影ガイドオーバーレイ
- サムネイル一覧
- 個別削除
- 撮影ヒント

---

## ファイル構成

```
frontend/
├── js/
│   ├── camera-service.js          # カメラサービス
│   ├── image-processor.js         # 画像処理ユーティリティ
│   └── barcode-scanner.js         # バーコードスキャナー
├── components/
│   ├── CameraCapture.jsx          # カメラUIコンポーネント
│   ├── RecipePhotoCapture.jsx     # レシピ写真撮影
│   └── CameraExample.jsx          # 使用例
└── docs/
    └── camera-integration.md      # 本ドキュメント
```

---

## セットアップ

### 1. 依存関係

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

### 2. HTTPS要件

カメラアクセスにはHTTPSが必要です（localhost は例外）。

開発環境での設定:

```bash
# 開発サーバーをHTTPSで起動
npm run dev -- --https

# または自己署名証明書を使用
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### 3. ブラウザ権限

初回アクセス時にカメラ権限のリクエストが表示されます。

---

## 使用方法

### 基本的なカメラ撮影

```jsx
import React, { useState } from 'react';
import CameraCapture from './components/CameraCapture.jsx';

function App() {
  const [showCamera, setShowCamera] = useState(false);

  const handleCapture = async (blob) => {
    // 撮影した画像をアップロード
    const formData = new FormData();
    formData.append('image', blob, 'photo.jpg');

    const response = await fetch('/api/v1/recipes/ocr', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();
    console.log('OCR結果:', result);

    setShowCamera(false);
  };

  return (
    <div>
      <button onClick={() => setShowCamera(true)}>
        写真を撮影
      </button>

      {showCamera && (
        <CameraCapture
          onCapture={handleCapture}
          onClose={() => setShowCamera(false)}
          allowGallery={true}
          autoRotate={true}
          maxWidth={1920}
          maxHeight={1080}
          quality={0.92}
        />
      )}
    </div>
  );
}
```

### レシピ写真の複数枚撮影

```jsx
import React, { useState } from 'react';
import RecipePhotoCapture from './components/RecipePhotoCapture.jsx';

function RecipeForm() {
  const [showCamera, setShowCamera] = useState(false);

  const handleComplete = async (blobs) => {
    // 複数の画像をアップロード
    const formData = new FormData();
    blobs.forEach((blob, index) => {
      formData.append('images', blob, `page-${index}.jpg`);
    });

    const response = await fetch('/api/v1/recipes/ocr-multi', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();
    console.log(`${blobs.length}枚を処理しました:`, result);

    setShowCamera(false);
  };

  return (
    <div>
      <button onClick={() => setShowCamera(true)}>
        レシピを撮影
      </button>

      {showCamera && (
        <RecipePhotoCapture
          onComplete={handleComplete}
          onClose={() => setShowCamera(false)}
          maxPhotos={5}
          showGuide={true}
          autoRotate={true}
        />
      )}
    </div>
  );
}
```

### バーコードスキャン

```javascript
import barcodeScanner from './js/barcode-scanner.js';

// カメラからスキャン
const videoElement = document.querySelector('video');

await barcodeScanner.startScanning(
  videoElement,
  async (barcodes) => {
    const barcode = barcodes[0];
    console.log('検出:', barcode.format, barcode.rawValue);

    // QRコードの場合
    if (barcode.format === 'qr_code') {
      const recipe = await barcodeScanner.loadRecipeFromQR(barcode.rawValue);
      console.log('レシピ:', recipe);
    }
    // 商品バーコードの場合
    else {
      const ingredient = await barcodeScanner.searchIngredientBarcode(barcode.rawValue);
      console.log('食材:', ingredient);
    }
  },
  {
    scanInterval: 500,
    continuous: false
  }
);

// スキャン停止
barcodeScanner.stopScanning();
```

### 画像処理

```javascript
import imageProcessor from './js/image-processor.js';

// リサイズ
const resized = await imageProcessor.resize(blob, {
  maxWidth: 1920,
  maxHeight: 1080,
  quality: 0.92,
  maintainAspectRatio: true
});

// 圧縮（2MB以下に）
const compressed = await imageProcessor.compress(blob, {
  quality: 0.8,
  maxSizeMB: 2
});

// クロッピング
const cropped = await imageProcessor.crop(blob, {
  x: 100,
  y: 100,
  width: 800,
  height: 600
});

// 90度回転
const rotated = await imageProcessor.rotate(blob, 90);

// EXIF情報に基づく自動回転
const autoRotated = await imageProcessor.autoRotate(blob);

// グレースケール変換（OCR用）
const grayscale = await imageProcessor.toGrayscale(blob);

// 明るさ・コントラスト調整
const adjusted = await imageProcessor.adjustBrightnessContrast(blob, {
  brightness: 10,
  contrast: 20
});
```

---

## API リファレンス

### CameraService

#### `startCamera(constraints?)`

カメラストリームを開始

```javascript
const stream = await cameraService.startCamera();
videoElement.srcObject = stream;
```

#### `stopCamera()`

カメラストリームを停止

```javascript
cameraService.stopCamera();
```

#### `switchCamera()`

前面/背面カメラを切り替え

```javascript
await cameraService.switchCamera();
```

#### `setResolution(width, height)`

解像度を設定

```javascript
await cameraService.setResolution(1920, 1080);
```

#### `setFlash(enabled)`

フラッシュを制御

```javascript
await cameraService.setFlash(true);
```

#### `capturePhoto(videoElement, options?)`

写真を撮影

```javascript
const blob = await cameraService.capturePhoto(videoElement, {
  format: 'image/jpeg',
  quality: 0.92
});
```

---

### ImageProcessor

#### `resize(blob, options)`

画像をリサイズ

```javascript
const resized = await imageProcessor.resize(blob, {
  maxWidth: 1920,
  maxHeight: 1080,
  quality: 0.92,
  maintainAspectRatio: true
});
```

#### `compress(blob, options)`

画像を圧縮

```javascript
const compressed = await imageProcessor.compress(blob, {
  quality: 0.8,
  maxSizeMB: 2
});
```

#### `crop(blob, cropArea, options)`

画像をクロップ

```javascript
const cropped = await imageProcessor.crop(blob, {
  x: 100,
  y: 100,
  width: 800,
  height: 600
});
```

#### `rotate(blob, degrees, options)`

画像を回転

```javascript
const rotated = await imageProcessor.rotate(blob, 90);
```

#### `autoRotate(blob, options)`

EXIF情報に基づいて自動回転

```javascript
const autoRotated = await imageProcessor.autoRotate(blob);
```

---

### BarcodeScanner

#### `startScanning(videoElement, onDetected, options)`

バーコードスキャンを開始

```javascript
await barcodeScanner.startScanning(
  videoElement,
  (barcodes) => console.log(barcodes),
  {
    scanInterval: 500,
    continuous: true
  }
);
```

#### `stopScanning()`

スキャンを停止

```javascript
barcodeScanner.stopScanning();
```

#### `detectFromImage(imageFile)`

画像ファイルから検出

```javascript
const barcodes = await barcodeScanner.detectFromImage(file);
```

#### `searchIngredientBarcode(barcode)`

バーコードから食材を検索

```javascript
const ingredient = await barcodeScanner.searchIngredientBarcode('4901234567890');
```

#### `loadRecipeFromQR(qrData)`

QRコードからレシピを読み込み

```javascript
const recipe = await barcodeScanner.loadRecipeFromQR('https://example.com/recipe/123');
```

---

### CameraCapture Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| onCapture | `(blob: Blob) => void` | required | 撮影完了時のコールバック |
| onClose | `() => void` | required | 閉じる時のコールバック |
| allowGallery | `boolean` | `true` | ギャラリー選択を許可 |
| autoRotate | `boolean` | `true` | 自動回転を有効化 |
| maxWidth | `number` | `1920` | 最大幅 |
| maxHeight | `number` | `1080` | 最大高さ |
| quality | `number` | `0.92` | JPEG品質 (0-1) |

---

### RecipePhotoCapture Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| onComplete | `(blobs: Blob[]) => void` | required | 撮影完了時のコールバック |
| onClose | `() => void` | required | 閉じる時のコールバック |
| maxPhotos | `number` | `5` | 最大撮影枚数 |
| showGuide | `boolean` | `true` | ガイド表示 |
| autoRotate | `boolean` | `true` | 自動回転を有効化 |

---

## ブラウザ互換性

### MediaDevices API

| ブラウザ | サポート |
|----------|----------|
| Chrome | ✅ 53+ |
| Firefox | ✅ 36+ |
| Safari | ✅ 11+ |
| Edge | ✅ 12+ |
| Mobile Safari | ✅ 11+ |
| Chrome Android | ✅ 53+ |

### BarcodeDetector API

| ブラウザ | サポート |
|----------|----------|
| Chrome | ✅ 88+ |
| Firefox | ❌ (フォールバック必要) |
| Safari | ❌ (フォールバック必要) |
| Edge | ✅ 88+ |
| Chrome Android | ✅ 88+ |

**注意**: BarcodeDetector 非対応ブラウザでは、jsQR などのポリフィルが必要です。

---

## トラブルシューティング

### カメラが起動しない

**原因**: 権限が拒否されている

**解決策**:
1. ブラウザの設定からカメラ権限を確認
2. HTTPS接続を確認（localhostを除く）
3. 別のカメラデバイスを試す

```javascript
// 利用可能なデバイスを確認
const devices = await cameraService.getAvailableDevices();
console.log('利用可能なカメラ:', devices);
```

### フラッシュが動作しない

**原因**: デバイスがフラッシュをサポートしていない

**解決策**:
```javascript
const capabilities = cameraService.getCapabilities();
if (capabilities.torch) {
  await cameraService.setFlash(true);
} else {
  console.warn('フラッシュ非対応');
}
```

### 画像が回転している

**原因**: EXIF情報が考慮されていない

**解決策**:
```javascript
// 自動回転を有効化
const corrected = await imageProcessor.autoRotate(blob);
```

### バーコードが検出されない

**原因**: 照明不足、ピントが合っていない

**解決策**:
1. フラッシュを有効化
2. カメラと対象物の距離を調整
3. 明るい場所で試す

```javascript
// デバッグ用にハイライト表示
barcodeScanner.highlightBarcodes(canvas, barcodes);
```

### 画像サイズが大きすぎる

**原因**: 圧縮設定が不適切

**解決策**:
```javascript
// ファイルサイズを制限
const compressed = await imageProcessor.compress(blob, {
  quality: 0.7,
  maxSizeMB: 1
});
```

---

## パフォーマンス最適化

### 1. 解像度の最適化

```javascript
// モバイルデバイスでは低解像度
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);
const maxWidth = isMobile ? 1280 : 1920;
const maxHeight = isMobile ? 720 : 1080;

await cameraService.setResolution(maxWidth, maxHeight);
```

### 2. 圧縮の最適化

```javascript
// OCR用には低品質でも十分
const ocrBlob = await imageProcessor.compress(blob, {
  quality: 0.7,
  maxSizeMB: 1
});
```

### 3. グレースケール変換

```javascript
// OCR精度向上のためグレースケール化
const grayscale = await imageProcessor.toGrayscale(blob);
```

---

## セキュリティ考慮事項

### 1. HTTPS必須

カメラアクセスには必ずHTTPSを使用してください。

### 2. 権限の適切な管理

```javascript
// ユーザー操作後にのみカメラを起動
button.addEventListener('click', async () => {
  await cameraService.startCamera();
});
```

### 3. ストリームの適切な停止

```javascript
// コンポーネントのクリーンアップ
useEffect(() => {
  return () => {
    cameraService.stopCamera();
  };
}, []);
```

### 4. 画像データの取り扱い

```javascript
// 不要になったBlobは速やかに破棄
URL.revokeObjectURL(imageUrl);
```

---

## ライセンス

MIT License

---

## サポート

問題が発生した場合は、以下を確認してください:

1. ブラウザコンソールのエラーメッセージ
2. カメラ権限の設定
3. HTTPS接続
4. ブラウザのバージョン

それでも解決しない場合は、Issue を作成してください。

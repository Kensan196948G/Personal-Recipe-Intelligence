/**
 * Camera Integration Example
 * カメラ機能の使用例
 */

import React, { useState } from 'react';
import CameraCapture from './CameraCapture.jsx';
import RecipePhotoCapture from './RecipePhotoCapture.jsx';
import barcodeScanner from '../js/barcode-scanner.js';

const CameraExample = () => {
  const [showCamera, setShowCamera] = useState(false);
  const [showRecipeCamera, setShowRecipeCamera] = useState(false);
  const [showBarcodeScanner, setShowBarcodeScanner] = useState(false);
  const [capturedImages, setCapturedImages] = useState([]);
  const [scanResult, setScanResult] = useState(null);

  /**
   * 通常カメラでの撮影完了
   */
  const handleCameraCapture = async (blob) => {
    console.log('撮影完了:', blob);

    // 画像をアップロード
    const formData = new FormData();
    formData.append('image', blob, 'photo.jpg');

    try {
      const response = await fetch('/api/v1/recipes/ocr', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        console.log('OCR結果:', result);
        alert('レシピを抽出しました');
      } else {
        alert('画像の処理に失敗しました');
      }
    } catch (error) {
      console.error('アップロードエラー:', error);
      alert('アップロードに失敗しました');
    }

    setShowCamera(false);
  };

  /**
   * レシピカメラでの撮影完了
   */
  const handleRecipeCapture = async (blobs) => {
    console.log(`${blobs.length}枚の写真を撮影しました`);

    // すべての画像をアップロード
    const formData = new FormData();
    blobs.forEach((blob, index) => {
      formData.append('images', blob, `recipe-${index}.jpg`);
    });

    try {
      const response = await fetch('/api/v1/recipes/ocr-multi', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        console.log('複数画像OCR結果:', result);
        alert(`${blobs.length}枚のレシピを処理しました`);
      } else {
        alert('画像の処理に失敗しました');
      }
    } catch (error) {
      console.error('アップロードエラー:', error);
      alert('アップロードに失敗しました');
    }

    setShowRecipeCamera(false);
  };

  /**
   * バーコードスキャン開始
   */
  const handleStartBarcodeScanner = () => {
    if (!barcodeScanner.isSupported()) {
      alert('このブラウザはバーコードスキャンに対応していません');
      return;
    }
    setShowBarcodeScanner(true);
  };

  /**
   * バーコード検出
   */
  const handleBarcodeDetected = async (barcodes) => {
    const barcode = barcodes[0];
    console.log('バーコード検出:', barcode);

    setScanResult({
      format: barcode.format,
      value: barcode.rawValue,
      info: barcodeScanner.getBarcodeInfo(barcode.format)
    });

    // QRコードの場合はレシピ読み込み
    if (barcode.format === 'qr_code') {
      const recipe = await barcodeScanner.loadRecipeFromQR(barcode.rawValue);
      if (recipe) {
        console.log('QRコードからレシピを読み込みました:', recipe);
        alert('レシピを読み込みました');
      }
    }
    // バーコードの場合は食材検索
    else {
      const ingredient = await barcodeScanner.searchIngredientBarcode(barcode.rawValue);
      if (ingredient) {
        console.log('食材情報:', ingredient);
        alert(`食材: ${ingredient.data.name}`);
      }
    }

    setShowBarcodeScanner(false);
  };

  return (
    <div className="camera-example">
      <div className="example-container">
        <h1>カメラ機能の使用例</h1>

        <div className="buttons">
          <button
            onClick={() => setShowCamera(true)}
            className="btn-primary"
          >
            通常カメラで撮影
          </button>

          <button
            onClick={() => setShowRecipeCamera(true)}
            className="btn-primary"
          >
            レシピ写真を撮影
          </button>

          <button
            onClick={handleStartBarcodeScanner}
            className="btn-primary"
          >
            バーコード/QRスキャン
          </button>
        </div>

        {/* スキャン結果 */}
        {scanResult && (
          <div className="scan-result">
            <h3>スキャン結果</h3>
            <dl>
              <dt>形式:</dt>
              <dd>{scanResult.info.name}</dd>
              <dt>値:</dt>
              <dd>{scanResult.value}</dd>
              <dt>用途:</dt>
              <dd>{scanResult.info.usage}</dd>
            </dl>
          </div>
        )}

        {/* 撮影画像プレビュー */}
        {capturedImages.length > 0 && (
          <div className="preview-grid">
            <h3>撮影した画像</h3>
            <div className="image-grid">
              {capturedImages.map((img, index) => (
                <img
                  key={index}
                  src={img}
                  alt={`撮影画像 ${index + 1}`}
                  className="preview-image"
                />
              ))}
            </div>
          </div>
        )}

        {/* 機能説明 */}
        <div className="feature-description">
          <h2>実装機能</h2>

          <section>
            <h3>1. カメラサービス (camera-service.js)</h3>
            <ul>
              <li>MediaDevices APIによるカメラアクセス</li>
              <li>前面/背面カメラの切り替え</li>
              <li>解像度設定（最大1920x1080）</li>
              <li>フラッシュ（トーチ）制御</li>
              <li>ズーム制御</li>
              <li>複数カメラデバイス対応</li>
            </ul>
          </section>

          <section>
            <h3>2. 画像処理 (image-processor.js)</h3>
            <ul>
              <li>リサイズ（アスペクト比維持）</li>
              <li>圧縮（JPEG品質調整、ファイルサイズ制限）</li>
              <li>クロッピング</li>
              <li>回転補正（90/180/270度）</li>
              <li>EXIF情報に基づく自動回転</li>
              <li>グレースケール変換</li>
              <li>明るさ・コントラスト調整</li>
            </ul>
          </section>

          <section>
            <h3>3. バーコードスキャナー (barcode-scanner.js)</h3>
            <ul>
              <li>BarcodeDetector APIによるリアルタイム検出</li>
              <li>QRコード、EAN-13、UPC-A等に対応</li>
              <li>食材バーコード検索</li>
              <li>QRコードからのレシピ読み込み</li>
              <li>画像ファイルからの検出</li>
              <li>検出結果のハイライト表示</li>
            </ul>
          </section>

          <section>
            <h3>4. カメラUIコンポーネント (CameraCapture.jsx)</h3>
            <ul>
              <li>ライブプレビュー</li>
              <li>シャッターボタン</li>
              <li>ギャラリーからの選択</li>
              <li>カメラ切り替えボタン</li>
              <li>フラッシュボタン</li>
              <li>撮影後のプレビュー/再撮影</li>
            </ul>
          </section>

          <section>
            <h3>5. レシピ写真撮影 (RecipePhotoCapture.jsx)</h3>
            <ul>
              <li>複数枚撮影（最大5枚）</li>
              <li>撮影ガイドオーバーレイ</li>
              <li>サムネイル一覧表示</li>
              <li>個別削除機能</li>
              <li>撮影ヒント表示</li>
            </ul>
          </section>
        </div>

        {/* 使用方法 */}
        <div className="usage-guide">
          <h2>使用方法</h2>

          <h3>基本的なカメラ撮影</h3>
          <pre><code>{`import CameraCapture from './components/CameraCapture.jsx';

<CameraCapture
  onCapture={(blob) => {
    // 撮影した画像の処理
    console.log('撮影完了:', blob);
  }}
  onClose={() => {
    // カメラを閉じる
  }}
  allowGallery={true}
  autoRotate={true}
  maxWidth={1920}
  maxHeight={1080}
  quality={0.92}
/>`}</code></pre>

          <h3>レシピ写真撮影</h3>
          <pre><code>{`import RecipePhotoCapture from './components/RecipePhotoCapture.jsx';

<RecipePhotoCapture
  onComplete={(blobs) => {
    // 複数の画像の処理
    console.log('撮影完了:', blobs);
  }}
  onClose={() => {
    // カメラを閉じる
  }}
  maxPhotos={5}
  showGuide={true}
  autoRotate={true}
/>`}</code></pre>

          <h3>バーコードスキャン</h3>
          <pre><code>{`import barcodeScanner from './js/barcode-scanner.js';

// スキャン開始
await barcodeScanner.startScanning(
  videoElement,
  (barcodes) => {
    console.log('検出:', barcodes);
  },
  {
    scanInterval: 500,
    continuous: false
  }
);

// スキャン停止
barcodeScanner.stopScanning();`}</code></pre>

          <h3>画像処理</h3>
          <pre><code>{`import imageProcessor from './js/image-processor.js';

// リサイズ
const resized = await imageProcessor.resize(blob, {
  maxWidth: 1920,
  maxHeight: 1080,
  quality: 0.92
});

// 圧縮
const compressed = await imageProcessor.compress(blob, {
  quality: 0.8,
  maxSizeMB: 2
});

// 回転
const rotated = await imageProcessor.rotate(blob, 90);

// 自動回転
const autoRotated = await imageProcessor.autoRotate(blob);`}</code></pre>
        </div>
      </div>

      {/* カメラモーダル */}
      {showCamera && (
        <CameraCapture
          onCapture={handleCameraCapture}
          onClose={() => setShowCamera(false)}
          allowGallery={true}
          autoRotate={true}
        />
      )}

      {/* レシピカメラモーダル */}
      {showRecipeCamera && (
        <RecipePhotoCapture
          onComplete={handleRecipeCapture}
          onClose={() => setShowRecipeCamera(false)}
          maxPhotos={5}
          showGuide={true}
        />
      )}

      {/* バーコードスキャナー */}
      {showBarcodeScanner && (
        <BarcodeScannerView
          onDetected={handleBarcodeDetected}
          onClose={() => setShowBarcodeScanner(false)}
        />
      )}

      <style jsx>{`
        .camera-example {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .example-container {
          background: #fff;
          border-radius: 8px;
          padding: 24px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        h1 {
          margin: 0 0 24px 0;
          font-size: 28px;
          color: #333;
        }

        h2 {
          margin: 32px 0 16px 0;
          font-size: 22px;
          color: #444;
          border-bottom: 2px solid #4caf50;
          padding-bottom: 8px;
        }

        h3 {
          margin: 24px 0 12px 0;
          font-size: 18px;
          color: #555;
        }

        .buttons {
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
          margin-bottom: 24px;
        }

        .btn-primary {
          background: #4caf50;
          color: #fff;
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-primary:hover {
          background: #45a049;
        }

        .scan-result {
          background: #f5f5f5;
          padding: 16px;
          border-radius: 6px;
          margin-bottom: 24px;
        }

        .scan-result h3 {
          margin-top: 0;
        }

        .scan-result dl {
          display: grid;
          grid-template-columns: 100px 1fr;
          gap: 8px;
          margin: 0;
        }

        .scan-result dt {
          font-weight: 600;
          color: #666;
        }

        .scan-result dd {
          margin: 0;
          color: #333;
        }

        .preview-grid {
          margin-bottom: 24px;
        }

        .image-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 12px;
        }

        .preview-image {
          width: 100%;
          height: 200px;
          object-fit: cover;
          border-radius: 6px;
          border: 2px solid #ddd;
        }

        .feature-description section,
        .usage-guide {
          margin-bottom: 24px;
        }

        ul {
          margin: 8px 0;
          padding-left: 24px;
        }

        li {
          margin-bottom: 4px;
          color: #555;
        }

        pre {
          background: #f5f5f5;
          padding: 16px;
          border-radius: 6px;
          overflow-x: auto;
          margin: 12px 0;
        }

        code {
          font-family: 'Consolas', 'Monaco', monospace;
          font-size: 14px;
          line-height: 1.6;
          color: #333;
        }
      `}</style>
    </div>
  );
};

/**
 * BarcodeScannerView Component
 * バーコードスキャナービュー
 */
const BarcodeScannerView = ({ onDetected, onClose }) => {
  const videoRef = React.useRef(null);

  React.useEffect(() => {
    let mounted = true;

    const start = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }
        });

        if (videoRef.current && mounted) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();

          // スキャン開始
          await barcodeScanner.startScanning(
            videoRef.current,
            onDetected,
            { continuous: false }
          );
        }
      } catch (error) {
        console.error('カメラ起動エラー:', error);
        alert('カメラの起動に失敗しました');
        onClose();
      }
    };

    start();

    return () => {
      mounted = false;
      barcodeScanner.stopScanning();
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      background: '#000',
      zIndex: 1000
    }}>
      <video
        ref={videoRef}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain'
        }}
        autoPlay
        playsInline
      />
      <button
        onClick={onClose}
        style={{
          position: 'absolute',
          top: 16,
          right: 16,
          background: 'rgba(0,0,0,0.6)',
          color: '#fff',
          border: 'none',
          borderRadius: '50%',
          width: 40,
          height: 40,
          fontSize: 24,
          cursor: 'pointer'
        }}
      >
        ✕
      </button>
    </div>
  );
};

export default CameraExample;

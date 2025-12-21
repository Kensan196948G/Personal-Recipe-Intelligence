/**
 * Barcode Scanner
 * バーコード/QRコード読み取りサービス
 *
 * @module barcode-scanner
 */

import cameraService from './camera-service.js';

class BarcodeScanner {
  constructor() {
    this.isScanning = false;
    this.scanInterval = null;
    this.detectorAvailable = false;
    this.barcodeDetector = null;
    this.initDetector();
  }

  /**
   * バーコード検出器を初期化
   * @private
   */
  async initDetector() {
    if ('BarcodeDetector' in window) {
      try {
        const formats = await window.BarcodeDetector.getSupportedFormats();
        console.log('サポートされているバーコード形式:', formats);
        this.barcodeDetector = new window.BarcodeDetector({ formats });
        this.detectorAvailable = true;
      } catch (error) {
        console.warn('BarcodeDetector初期化エラー:', error);
        this.detectorAvailable = false;
      }
    } else {
      console.warn('BarcodeDetector APIがサポートされていません');
      this.detectorAvailable = false;
    }
  }

  /**
   * バーコード検出器が利用可能かチェック
   * @returns {boolean}
   */
  isSupported() {
    return this.detectorAvailable;
  }

  /**
   * バーコードスキャンを開始
   * @param {HTMLVideoElement} videoElement - ビデオ要素
   * @param {Function} onDetected - 検出時のコールバック
   * @param {Object} options - オプション
   * @returns {Promise<void>}
   */
  async startScanning(videoElement, onDetected, options = {}) {
    const {
      scanInterval = 500,
      formats = null,
      continuous = true
    } = options;

    if (!this.isSupported()) {
      throw new Error('バーコードスキャナーがサポートされていません');
    }

    if (this.isScanning) {
      this.stopScanning();
    }

    this.isScanning = true;

    // フォーマット指定がある場合は再初期化
    if (formats) {
      this.barcodeDetector = new window.BarcodeDetector({ formats });
    }

    // スキャンループ
    this.scanInterval = setInterval(async () => {
      if (!this.isScanning) {
        return;
      }

      try {
        const barcodes = await this.detectFromVideo(videoElement);
        if (barcodes && barcodes.length > 0) {
          onDetected(barcodes);

          if (!continuous) {
            this.stopScanning();
          }
        }
      } catch (error) {
        console.error('バーコード検出エラー:', error);
      }
    }, scanInterval);
  }

  /**
   * バーコードスキャンを停止
   */
  stopScanning() {
    this.isScanning = false;
    if (this.scanInterval) {
      clearInterval(this.scanInterval);
      this.scanInterval = null;
    }
  }

  /**
   * ビデオからバーコードを検出
   * @param {HTMLVideoElement} videoElement - ビデオ要素
   * @returns {Promise<Array>}
   */
  async detectFromVideo(videoElement) {
    if (!this.barcodeDetector) {
      throw new Error('バーコード検出器が初期化されていません');
    }

    try {
      const barcodes = await this.barcodeDetector.detect(videoElement);
      return barcodes.map(barcode => ({
        format: barcode.format,
        rawValue: barcode.rawValue,
        boundingBox: barcode.boundingBox,
        cornerPoints: barcode.cornerPoints
      }));
    } catch (error) {
      console.error('検出エラー:', error);
      return [];
    }
  }

  /**
   * 画像ファイルからバーコードを検出
   * @param {File|Blob} imageFile - 画像ファイル
   * @returns {Promise<Array>}
   */
  async detectFromImage(imageFile) {
    if (!this.barcodeDetector) {
      throw new Error('バーコード検出器が初期化されていません');
    }

    try {
      const img = await this.loadImage(imageFile);
      const barcodes = await this.barcodeDetector.detect(img);
      return barcodes.map(barcode => ({
        format: barcode.format,
        rawValue: barcode.rawValue,
        boundingBox: barcode.boundingBox,
        cornerPoints: barcode.cornerPoints
      }));
    } catch (error) {
      console.error('画像からの検出エラー:', error);
      return [];
    }
  }

  /**
   * QRコードをデコード（フォールバック用）
   * @param {HTMLVideoElement|HTMLImageElement} source - ソース要素
   * @returns {Promise<string|null>}
   */
  async decodeQRCode(source) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = source.videoWidth || source.width;
    canvas.height = source.videoHeight || source.height;

    ctx.drawImage(source, 0, 0, canvas.width, canvas.height);

    try {
      // jsQRライブラリを使用（別途読み込みが必要）
      if (typeof jsQR !== 'undefined') {
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);
        return code ? code.data : null;
      }
    } catch (error) {
      console.error('QRコードデコードエラー:', error);
    }

    return null;
  }

  /**
   * 食材バーコードを検索
   * @param {string} barcode - バーコード値
   * @returns {Promise<Object>}
   */
  async searchIngredientBarcode(barcode) {
    try {
      // APIエンドポイントに問い合わせ
      const response = await fetch(`/api/v1/ingredients/barcode/${barcode}`);
      if (!response.ok) {
        throw new Error('バーコード検索に失敗しました');
      }
      return await response.json();
    } catch (error) {
      console.error('バーコード検索エラー:', error);
      return null;
    }
  }

  /**
   * QRコードからレシピを読み込み
   * @param {string} qrData - QRコードデータ
   * @returns {Promise<Object>}
   */
  async loadRecipeFromQR(qrData) {
    try {
      // QRデータがURLの場合
      if (qrData.startsWith('http://') || qrData.startsWith('https://')) {
        const response = await fetch(`/api/v1/recipes/import?url=${encodeURIComponent(qrData)}`);
        if (!response.ok) {
          throw new Error('レシピの読み込みに失敗しました');
        }
        return await response.json();
      }

      // QRデータがJSON形式の場合
      try {
        const recipeData = JSON.parse(qrData);
        return recipeData;
      } catch (parseError) {
        console.error('QRコードのパースエラー:', parseError);
        return null;
      }
    } catch (error) {
      console.error('QRコードからのレシピ読み込みエラー:', error);
      return null;
    }
  }

  /**
   * バーコード形式を判定
   * @param {string} format - バーコード形式
   * @returns {Object}
   */
  getBarcodeInfo(format) {
    const formatInfo = {
      'qr_code': {
        name: 'QRコード',
        type: 'qr',
        usage: 'URL、テキスト、レシピデータ'
      },
      'ean_13': {
        name: 'EAN-13',
        type: 'barcode',
        usage: '商品バーコード（13桁）'
      },
      'ean_8': {
        name: 'EAN-8',
        type: 'barcode',
        usage: '商品バーコード（8桁）'
      },
      'code_128': {
        name: 'Code 128',
        type: 'barcode',
        usage: '流通バーコード'
      },
      'code_39': {
        name: 'Code 39',
        type: 'barcode',
        usage: '工業用バーコード'
      },
      'upc_a': {
        name: 'UPC-A',
        type: 'barcode',
        usage: '北米商品バーコード'
      },
      'upc_e': {
        name: 'UPC-E',
        type: 'barcode',
        usage: '北米商品バーコード（短縮版）'
      }
    };

    return formatInfo[format] || {
      name: format,
      type: 'unknown',
      usage: '不明'
    };
  }

  /**
   * バーコードをハイライト表示
   * @param {HTMLCanvasElement} canvas - Canvas要素
   * @param {Array} barcodes - 検出されたバーコード
   */
  highlightBarcodes(canvas, barcodes) {
    const ctx = canvas.getContext('2d');

    barcodes.forEach(barcode => {
      const { boundingBox, cornerPoints } = barcode;

      // バウンディングボックスを描画
      if (boundingBox) {
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3;
        ctx.strokeRect(
          boundingBox.x,
          boundingBox.y,
          boundingBox.width,
          boundingBox.height
        );
      }

      // コーナーポイントを描画
      if (cornerPoints && cornerPoints.length === 4) {
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cornerPoints[0].x, cornerPoints[0].y);
        cornerPoints.forEach(point => {
          ctx.lineTo(point.x, point.y);
        });
        ctx.closePath();
        ctx.stroke();
      }
    });
  }

  /**
   * 画像を読み込み
   * @param {Blob|File} imageBlob - 画像Blob
   * @returns {Promise<HTMLImageElement>}
   * @private
   */
  loadImage(imageBlob) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const url = URL.createObjectURL(imageBlob);

      img.onload = () => {
        URL.revokeObjectURL(url);
        resolve(img);
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('画像の読み込みに失敗しました'));
      };

      img.src = url;
    });
  }
}

// シングルトンインスタンス
const barcodeScanner = new BarcodeScanner();

export default barcodeScanner;

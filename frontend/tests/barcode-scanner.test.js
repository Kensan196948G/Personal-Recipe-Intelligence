/**
 * Barcode Scanner Tests
 * バーコードスキャナーのテスト
 */

import { describe, test, expect, beforeEach, afterEach, mock } from 'bun:test';
import barcodeScanner from '../js/barcode-scanner.js';

describe('BarcodeScanner', () => {
  let mockBarcodeDetector;
  let mockBarcodes;

  beforeEach(() => {
    mockBarcodes = [
      {
        format: 'qr_code',
        rawValue: 'https://example.com/recipe/123',
        boundingBox: { x: 100, y: 100, width: 200, height: 200 },
        cornerPoints: [
          { x: 100, y: 100 },
          { x: 300, y: 100 },
          { x: 300, y: 300 },
          { x: 100, y: 300 }
        ]
      }
    ];

    mockBarcodeDetector = {
      detect: mock(async () => mockBarcodes)
    };

    global.window = {
      BarcodeDetector: class {
        constructor(options) {
          return mockBarcodeDetector;
        }
        static getSupportedFormats = mock(async () => [
          'qr_code',
          'ean_13',
          'ean_8',
          'code_128'
        ])
      }
    };

    // BarcodeDetectorを初期化
    barcodeScanner.initDetector();
  });

  afterEach(() => {
    barcodeScanner.stopScanning();
  });

  test('isSupported() should return true when BarcodeDetector is available', () => {
    expect(barcodeScanner.isSupported()).toBe(true);
  });

  test('isSupported() should return false when BarcodeDetector is not available', () => {
    delete global.window.BarcodeDetector;
    const scanner = new (barcodeScanner.constructor)();
    expect(scanner.detectorAvailable).toBe(false);
  });

  test('startScanning() should start scanning interval', async () => {
    const mockVideo = document.createElement('video');
    const onDetected = mock(() => {});

    await barcodeScanner.startScanning(mockVideo, onDetected, {
      scanInterval: 100,
      continuous: true
    });

    expect(barcodeScanner.isScanning).toBe(true);
    expect(barcodeScanner.scanInterval).not.toBeNull();
  });

  test('startScanning() should throw when not supported', async () => {
    barcodeScanner.detectorAvailable = false;

    await expect(
      barcodeScanner.startScanning(null, () => {})
    ).rejects.toThrow('バーコードスキャナーがサポートされていません');
  });

  test('stopScanning() should clear interval', async () => {
    const mockVideo = document.createElement('video');
    await barcodeScanner.startScanning(mockVideo, () => {});

    barcodeScanner.stopScanning();

    expect(barcodeScanner.isScanning).toBe(false);
    expect(barcodeScanner.scanInterval).toBeNull();
  });

  test('detectFromVideo() should detect barcodes', async () => {
    const mockVideo = document.createElement('video');
    const result = await barcodeScanner.detectFromVideo(mockVideo);

    expect(result).toHaveLength(1);
    expect(result[0].format).toBe('qr_code');
    expect(result[0].rawValue).toBe('https://example.com/recipe/123');
  });

  test('detectFromImage() should detect barcodes from image', async () => {
    const mockImage = new Blob(['test'], { type: 'image/jpeg' });

    global.Image = class {
      constructor() {
        this.onload = null;
        this.onerror = null;
        setTimeout(() => {
          if (this.onload) this.onload();
        }, 0);
      }
    };

    global.URL = {
      createObjectURL: mock(() => 'blob:test'),
      revokeObjectURL: mock(() => {})
    };

    const result = await barcodeScanner.detectFromImage(mockImage);

    expect(result).toHaveLength(1);
    expect(result[0].format).toBe('qr_code');
  });

  test('searchIngredientBarcode() should search ingredient', async () => {
    global.fetch = mock(async () => ({
      ok: true,
      json: async () => ({
        status: 'ok',
        data: {
          name: 'トマト',
          barcode: '4901234567890'
        }
      })
    }));

    const result = await barcodeScanner.searchIngredientBarcode('4901234567890');

    expect(result).not.toBeNull();
    expect(result.data.name).toBe('トマト');
  });

  test('searchIngredientBarcode() should return null on error', async () => {
    global.fetch = mock(async () => ({
      ok: false
    }));

    const result = await barcodeScanner.searchIngredientBarcode('invalid');

    expect(result).toBeNull();
  });

  test('loadRecipeFromQR() should load recipe from URL', async () => {
    global.fetch = mock(async () => ({
      ok: true,
      json: async () => ({
        status: 'ok',
        data: {
          title: 'カレーライス',
          ingredients: ['玉ねぎ', 'にんじん', 'じゃがいも']
        }
      })
    }));

    const result = await barcodeScanner.loadRecipeFromQR(
      'https://example.com/recipe/123'
    );

    expect(result).not.toBeNull();
    expect(result.data.title).toBe('カレーライス');
  });

  test('loadRecipeFromQR() should parse JSON data', async () => {
    const recipeJSON = JSON.stringify({
      title: 'カレーライス',
      ingredients: ['玉ねぎ', 'にんじん']
    });

    const result = await barcodeScanner.loadRecipeFromQR(recipeJSON);

    expect(result).not.toBeNull();
    expect(result.title).toBe('カレーライス');
  });

  test('loadRecipeFromQR() should return null for invalid data', async () => {
    const result = await barcodeScanner.loadRecipeFromQR('invalid json');

    expect(result).toBeNull();
  });

  test('getBarcodeInfo() should return barcode information', () => {
    const info = barcodeScanner.getBarcodeInfo('qr_code');

    expect(info.name).toBe('QRコード');
    expect(info.type).toBe('qr');
  });

  test('getBarcodeInfo() should return unknown for unsupported format', () => {
    const info = barcodeScanner.getBarcodeInfo('unknown_format');

    expect(info.type).toBe('unknown');
  });

  test('highlightBarcodes() should draw on canvas', () => {
    const mockCanvas = {
      getContext: mock(() => ({
        strokeStyle: '',
        lineWidth: 0,
        strokeRect: mock(() => {}),
        beginPath: mock(() => {}),
        moveTo: mock(() => {}),
        lineTo: mock(() => {}),
        closePath: mock(() => {}),
        stroke: mock(() => {})
      }))
    };

    const barcodes = [
      {
        boundingBox: { x: 100, y: 100, width: 200, height: 200 },
        cornerPoints: [
          { x: 100, y: 100 },
          { x: 300, y: 100 },
          { x: 300, y: 300 },
          { x: 100, y: 300 }
        ]
      }
    ];

    barcodeScanner.highlightBarcodes(mockCanvas, barcodes);

    const ctx = mockCanvas.getContext();
    expect(ctx.strokeRect).toHaveBeenCalled();
    expect(ctx.stroke).toHaveBeenCalled();
  });

  test('loadImage() should reject on error', async () => {
    const mockBlob = new Blob(['test'], { type: 'image/jpeg' });

    global.Image = class {
      constructor() {
        this.onload = null;
        this.onerror = null;
        setTimeout(() => {
          if (this.onerror) this.onerror();
        }, 0);
      }
    };

    global.URL = {
      createObjectURL: mock(() => 'blob:test'),
      revokeObjectURL: mock(() => {})
    };

    await expect(barcodeScanner.loadImage(mockBlob)).rejects.toThrow(
      '画像の読み込みに失敗しました'
    );
  });
});

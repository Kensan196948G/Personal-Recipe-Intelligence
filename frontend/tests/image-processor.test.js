/**
 * Image Processor Tests
 * 画像処理ユーティリティのテスト
 */

import { describe, test, expect, beforeEach, mock } from 'bun:test';
import imageProcessor from '../js/image-processor.js';

describe('ImageProcessor', () => {
  let mockBlob;
  let mockImage;
  let mockCanvas;
  let mockContext;

  beforeEach(() => {
    mockBlob = new Blob(['test'], { type: 'image/jpeg' });

    mockContext = {
      drawImage: mock(() => {}),
      getImageData: mock(() => ({
        data: new Uint8ClampedArray([255, 0, 0, 255, 0, 255, 0, 255]),
        width: 2,
        height: 1
      })),
      putImageData: mock(() => {}),
      translate: mock(() => {}),
      rotate: mock(() => {})
    };

    mockCanvas = {
      width: 0,
      height: 0,
      getContext: mock(() => mockContext),
      toBlob: mock((callback, format, quality) => {
        callback(new Blob(['result'], { type: format }));
      })
    };

    mockImage = {
      width: 1920,
      height: 1080,
      onload: null,
      onerror: null,
      src: ''
    };

    global.Image = class {
      constructor() {
        Object.assign(this, mockImage);
        setTimeout(() => {
          if (this.onload) this.onload();
        }, 0);
      }
    };

    global.document = {
      createElement: mock(() => mockCanvas)
    };

    global.URL = {
      createObjectURL: mock(() => 'blob:test'),
      revokeObjectURL: mock(() => {})
    };
  });

  test('resize() should resize image maintaining aspect ratio', async () => {
    const result = await imageProcessor.resize(mockBlob, {
      maxWidth: 1280,
      maxHeight: 720,
      maintainAspectRatio: true
    });

    expect(result).toBeInstanceOf(Blob);
    expect(mockCanvas.toBlob).toHaveBeenCalled();
  });

  test('resize() should resize without maintaining aspect ratio', async () => {
    const result = await imageProcessor.resize(mockBlob, {
      maxWidth: 1280,
      maxHeight: 720,
      maintainAspectRatio: false
    });

    expect(result).toBeInstanceOf(Blob);
  });

  test('compress() should compress image to target size', async () => {
    // 大きなBlobをシミュレート
    Object.defineProperty(mockBlob, 'size', {
      value: 5 * 1024 * 1024, // 5MB
      writable: true
    });

    const result = await imageProcessor.compress(mockBlob, {
      quality: 0.8,
      maxSizeMB: 2
    });

    expect(result).toBeInstanceOf(Blob);
  });

  test('crop() should crop image to specified area', async () => {
    const result = await imageProcessor.crop(
      mockBlob,
      { x: 100, y: 100, width: 800, height: 600 }
    );

    expect(result).toBeInstanceOf(Blob);
    expect(mockCanvas.width).toBe(800);
    expect(mockCanvas.height).toBe(600);
  });

  test('rotate() should rotate image by 90 degrees', async () => {
    const result = await imageProcessor.rotate(mockBlob, 90);

    expect(result).toBeInstanceOf(Blob);
    expect(mockContext.rotate).toHaveBeenCalled();
  });

  test('rotate() should rotate image by 180 degrees', async () => {
    const result = await imageProcessor.rotate(mockBlob, 180);

    expect(result).toBeInstanceOf(Blob);
    expect(mockContext.rotate).toHaveBeenCalled();
  });

  test('getDimensions() should return image dimensions', async () => {
    const dimensions = await imageProcessor.getDimensions(mockBlob);

    expect(dimensions).toEqual({
      width: 1920,
      height: 1080
    });
  });

  test('toBase64() should convert blob to base64', async () => {
    const mockFileReader = {
      readAsDataURL: mock(function() {
        this.result = 'data:image/jpeg;base64,test';
        this.onload();
      }),
      result: null,
      onload: null,
      onerror: null
    };

    global.FileReader = class {
      constructor() {
        Object.assign(this, mockFileReader);
      }
    };

    const result = await imageProcessor.toBase64(mockBlob);

    expect(result).toBe('data:image/jpeg;base64,test');
  });

  test('fromBase64() should convert base64 to blob', async () => {
    global.fetch = mock(async () => ({
      blob: async () => new Blob(['test'])
    }));

    const result = await imageProcessor.fromBase64('data:image/jpeg;base64,test');

    expect(result).toBeInstanceOf(Blob);
  });

  test('toGrayscale() should convert image to grayscale', async () => {
    const result = await imageProcessor.toGrayscale(mockBlob);

    expect(result).toBeInstanceOf(Blob);
    expect(mockContext.getImageData).toHaveBeenCalled();
    expect(mockContext.putImageData).toHaveBeenCalled();
  });

  test('adjustBrightnessContrast() should adjust image properties', async () => {
    const result = await imageProcessor.adjustBrightnessContrast(
      mockBlob,
      { brightness: 10, contrast: 20 }
    );

    expect(result).toBeInstanceOf(Blob);
  });

  test('getOrientation() should return orientation from EXIF', async () => {
    const jpegBlob = new Blob([
      new Uint8Array([
        0xFF, 0xD8, // JPEG SOI
        0xFF, 0xE1, // APP1 marker
        0x00, 0x10, // segment size
        0x45, 0x78, 0x69, 0x66, 0x00, 0x00, // "Exif"
        0x4D, 0x4D, // big endian
        0x00, 0x2A, // TIFF magic
        0x00, 0x00, 0x00, 0x08 // IFD offset
      ])
    ], { type: 'image/jpeg' });

    const orientation = await imageProcessor.getOrientation(jpegBlob);

    expect(typeof orientation).toBe('number');
  });

  test('loadImage() should reject on error', async () => {
    global.Image = class {
      constructor() {
        Object.assign(this, mockImage);
        setTimeout(() => {
          if (this.onerror) this.onerror();
        }, 0);
      }
    };

    await expect(imageProcessor.loadImage(mockBlob)).rejects.toThrow(
      '画像の読み込みに失敗しました'
    );
  });

  test('canvasToBlob() should reject when blob is null', async () => {
    mockCanvas.toBlob = mock((callback) => {
      callback(null);
    });

    await expect(
      imageProcessor.canvasToBlob(mockCanvas, 'image/jpeg', 0.92)
    ).rejects.toThrow('Blob変換に失敗しました');
  });
});

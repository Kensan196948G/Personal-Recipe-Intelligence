/**
 * Image Processor
 * 画像処理ユーティリティ（リサイズ、圧縮、クロップ、回転）
 *
 * @module image-processor
 */

class ImageProcessor {
  /**
   * 画像をリサイズ
   * @param {Blob|File} imageBlob - 画像Blob
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async resize(imageBlob, options = {}) {
    const {
      maxWidth = 1920,
      maxHeight = 1080,
      quality = 0.92,
      format = 'image/jpeg',
      maintainAspectRatio = true
    } = options;

    const img = await this.loadImage(imageBlob);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    let { width, height } = img;

    if (maintainAspectRatio) {
      // アスペクト比を維持してリサイズ
      const ratio = Math.min(maxWidth / width, maxHeight / height);
      if (ratio < 1) {
        width *= ratio;
        height *= ratio;
      }
    } else {
      width = Math.min(width, maxWidth);
      height = Math.min(height, maxHeight);
    }

    canvas.width = width;
    canvas.height = height;

    ctx.drawImage(img, 0, 0, width, height);

    return this.canvasToBlob(canvas, format, quality);
  }

  /**
   * 画像を圧縮
   * @param {Blob|File} imageBlob - 画像Blob
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async compress(imageBlob, options = {}) {
    const {
      quality = 0.8,
      format = 'image/jpeg',
      maxSizeMB = 2
    } = options;

    let currentQuality = quality;
    let compressed = await this.resize(imageBlob, {
      maxWidth: 1920,
      maxHeight: 1080,
      quality: currentQuality,
      format
    });

    // 目標サイズまで品質を下げる
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    while (compressed.size > maxSizeBytes && currentQuality > 0.1) {
      currentQuality -= 0.1;
      compressed = await this.resize(imageBlob, {
        maxWidth: 1920,
        maxHeight: 1080,
        quality: currentQuality,
        format
      });
    }

    return compressed;
  }

  /**
   * 画像をクロップ
   * @param {Blob|File} imageBlob - 画像Blob
   * @param {Object} cropArea - クロップ領域 {x, y, width, height}
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async crop(imageBlob, cropArea, options = {}) {
    const {
      quality = 0.92,
      format = 'image/jpeg'
    } = options;

    const { x, y, width, height } = cropArea;

    const img = await this.loadImage(imageBlob);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = width;
    canvas.height = height;

    ctx.drawImage(
      img,
      x, y, width, height,  // ソース領域
      0, 0, width, height   // 描画先領域
    );

    return this.canvasToBlob(canvas, format, quality);
  }

  /**
   * 画像を回転
   * @param {Blob|File} imageBlob - 画像Blob
   * @param {number} degrees - 回転角度（90, 180, 270, -90など）
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async rotate(imageBlob, degrees, options = {}) {
    const {
      quality = 0.92,
      format = 'image/jpeg'
    } = options;

    const img = await this.loadImage(imageBlob);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // 90度または270度の回転では幅と高さを入れ替える
    const isRotated90or270 = degrees % 180 !== 0;
    canvas.width = isRotated90or270 ? img.height : img.width;
    canvas.height = isRotated90or270 ? img.width : img.height;

    // 中心点を基準に回転
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate((degrees * Math.PI) / 180);
    ctx.drawImage(img, -img.width / 2, -img.height / 2);

    return this.canvasToBlob(canvas, format, quality);
  }

  /**
   * EXIF情報に基づいて自動回転
   * @param {Blob|File} imageBlob - 画像Blob
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async autoRotate(imageBlob, options = {}) {
    const orientation = await this.getOrientation(imageBlob);
    const rotationMap = {
      3: 180,
      6: 90,
      8: -90
    };

    const degrees = rotationMap[orientation] || 0;
    if (degrees === 0) {
      return imageBlob;
    }

    return this.rotate(imageBlob, degrees, options);
  }

  /**
   * 画像のEXIF Orientationを取得
   * @param {Blob|File} imageBlob - 画像Blob
   * @returns {Promise<number>}
   */
  async getOrientation(imageBlob) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const view = new DataView(e.target.result);
        if (view.getUint16(0, false) !== 0xFFD8) {
          resolve(1); // JPEG以外
          return;
        }

        const length = view.byteLength;
        let offset = 2;

        while (offset < length) {
          const marker = view.getUint16(offset, false);
          offset += 2;

          if (marker === 0xFFE1) {
            // EXIF marker
            const exifOffset = offset + 2;
            if (view.getUint32(exifOffset, false) !== 0x45786966) {
              resolve(1);
              return;
            }

            const tiffOffset = exifOffset + 6;
            const littleEndian = view.getUint16(tiffOffset, false) === 0x4949;
            const ifdOffset = view.getUint32(tiffOffset + 4, littleEndian) + tiffOffset;
            const tags = view.getUint16(ifdOffset, littleEndian);

            for (let i = 0; i < tags; i++) {
              const tagOffset = ifdOffset + i * 12 + 2;
              const tag = view.getUint16(tagOffset, littleEndian);
              if (tag === 0x0112) {
                // Orientation tag
                resolve(view.getUint16(tagOffset + 8, littleEndian));
                return;
              }
            }
          }

          const size = view.getUint16(offset, false);
          offset += size;
        }

        resolve(1);
      };
      reader.readAsArrayBuffer(imageBlob);
    });
  }

  /**
   * 画像をBase64エンコード
   * @param {Blob|File} imageBlob - 画像Blob
   * @returns {Promise<string>}
   */
  async toBase64(imageBlob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(imageBlob);
    });
  }

  /**
   * Base64から画像Blobに変換
   * @param {string} base64 - Base64文字列
   * @returns {Promise<Blob>}
   */
  async fromBase64(base64) {
    const response = await fetch(base64);
    return response.blob();
  }

  /**
   * 画像の寸法を取得
   * @param {Blob|File} imageBlob - 画像Blob
   * @returns {Promise<Object>}
   */
  async getDimensions(imageBlob) {
    const img = await this.loadImage(imageBlob);
    return {
      width: img.width,
      height: img.height
    };
  }

  /**
   * 画像をグレースケールに変換
   * @param {Blob|File} imageBlob - 画像Blob
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async toGrayscale(imageBlob, options = {}) {
    const {
      quality = 0.92,
      format = 'image/jpeg'
    } = options;

    const img = await this.loadImage(imageBlob);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = img.width;
    canvas.height = img.height;

    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      data[i] = gray;
      data[i + 1] = gray;
      data[i + 2] = gray;
    }

    ctx.putImageData(imageData, 0, 0);

    return this.canvasToBlob(canvas, format, quality);
  }

  /**
   * 画像の明るさ・コントラストを調整
   * @param {Blob|File} imageBlob - 画像Blob
   * @param {Object} adjustments - 調整値 {brightness: -100~100, contrast: -100~100}
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async adjustBrightnessContrast(imageBlob, adjustments = {}, options = {}) {
    const {
      brightness = 0,
      contrast = 0
    } = adjustments;

    const {
      quality = 0.92,
      format = 'image/jpeg'
    } = options;

    const img = await this.loadImage(imageBlob);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = img.width;
    canvas.height = img.height;

    ctx.filter = `brightness(${100 + brightness}%) contrast(${100 + contrast}%)`;
    ctx.drawImage(img, 0, 0);

    return this.canvasToBlob(canvas, format, quality);
  }

  /**
   * BlobからImageオブジェクトをロード
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

  /**
   * CanvasをBlobに変換
   * @param {HTMLCanvasElement} canvas - Canvas要素
   * @param {string} format - 画像フォーマット
   * @param {number} quality - 品質
   * @returns {Promise<Blob>}
   * @private
   */
  canvasToBlob(canvas, format, quality) {
    return new Promise((resolve, reject) => {
      canvas.toBlob(
        blob => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Blob変換に失敗しました'));
          }
        },
        format,
        quality
      );
    });
  }
}

// シングルトンインスタンス
const imageProcessor = new ImageProcessor();

export default imageProcessor;

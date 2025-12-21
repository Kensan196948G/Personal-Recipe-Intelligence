/**
 * image-optimizer.js
 * Personal Recipe Intelligence
 * 画像最適化ユーティリティ
 * - srcset/sizes対応
 * - 遅延読み込み
 * - WebP対応
 */

/**
 * 画像最適化クラス
 */
class ImageOptimizer {
  constructor(options = {}) {
    this.options = {
      lazyLoadThreshold: options.lazyLoadThreshold || '200px',
      enableWebP: options.enableWebP !== undefined ? options.enableWebP : true,
      defaultSizes: options.defaultSizes || '100vw',
      imageSizes: options.imageSizes || [320, 480, 768, 1024, 1200, 1600],
      quality: options.quality || 85,
      placeholderColor: options.placeholderColor || '#f3f4f6',
      ...options,
    };

    this.webPSupported = null;
    this.intersectionObserver = null;

    this.init();
  }

  /**
   * 初期化
   */
  init() {
    this.checkWebPSupport();
    this.setupLazyLoading();
  }

  /**
   * WebPサポートをチェック
   * @returns {Promise<boolean>}
   */
  async checkWebPSupport() {
    if (this.webPSupported !== null) {
      return this.webPSupported;
    }

    return new Promise((resolve) => {
      const webP = new Image();
      webP.onload = () => {
        this.webPSupported = webP.width > 0 && webP.height > 0;
        resolve(this.webPSupported);
      };
      webP.onerror = () => {
        this.webPSupported = false;
        resolve(false);
      };
      webP.src =
        'data:image/webp;base64,UklGRhoAAABXRUJQVlA4TA0AAAAvAAAAEAcQERGIiP4HAA==';
    });
  }

  /**
   * 遅延読み込みのセットアップ
   */
  setupLazyLoading() {
    if ('IntersectionObserver' in window) {
      this.intersectionObserver = new IntersectionObserver(
        (entries, observer) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              this.loadImage(entry.target);
              observer.unobserve(entry.target);
            }
          });
        },
        {
          rootMargin: this.options.lazyLoadThreshold,
        }
      );
    }
  }

  /**
   * 画像を遅延読み込み
   * @param {HTMLImageElement} img - 画像要素
   */
  loadImage(img) {
    const src = img.dataset.src;
    const srcset = img.dataset.srcset;

    if (srcset) {
      img.srcset = srcset;
    }

    if (src) {
      img.src = src;
    }

    img.classList.add('loaded');
    img.removeAttribute('data-src');
    img.removeAttribute('data-srcset');
  }

  /**
   * srcsetを生成
   * @param {string} imagePath - 画像パス
   * @param {Array<number>} sizes - サイズ配列
   * @returns {string}
   */
  generateSrcSet(imagePath, sizes = this.options.imageSizes) {
    const extension = this.getExtension(imagePath);
    const basePath = imagePath.replace(new RegExp(`\\.${extension}$`), '');

    return sizes
      .map((size) => {
        const url = this.getResizedImageUrl(basePath, extension, size);
        return `${url} ${size}w`;
      })
      .join(', ');
  }

  /**
   * リサイズされた画像URLを取得
   * @param {string} basePath - ベースパス
   * @param {string} extension - 拡張子
   * @param {number} width - 幅
   * @returns {string}
   */
  getResizedImageUrl(basePath, extension, width) {
    // WebPサポート時は.webp拡張子を使用
    const ext =
      this.options.enableWebP && this.webPSupported ? 'webp' : extension;
    return `${basePath}-${width}w.${ext}`;
  }

  /**
   * 拡張子を取得
   * @param {string} path - ファイルパス
   * @returns {string}
   */
  getExtension(path) {
    return path.split('.').pop().toLowerCase();
  }

  /**
   * レスポンシブ画像要素を作成
   * @param {Object} options - オプション
   * @returns {HTMLImageElement}
   */
  createResponsiveImage(options) {
    const {
      src,
      alt = '',
      sizes = this.options.defaultSizes,
      className = '',
      lazy = true,
      width,
      height,
    } = options;

    const img = document.createElement('img');
    img.alt = alt;

    if (className) {
      img.className = className;
    }

    if (width) {
      img.width = width;
    }

    if (height) {
      img.height = height;
    }

    // srcsetを生成
    const srcset = this.generateSrcSet(src);

    if (lazy && this.intersectionObserver) {
      // 遅延読み込み
      img.dataset.src = src;
      img.dataset.srcset = srcset;
      img.setAttribute('sizes', sizes);

      // プレースホルダー
      img.src = this.createPlaceholder(width, height);
      img.classList.add('lazy');

      this.intersectionObserver.observe(img);
    } else {
      // 即座に読み込み
      img.src = src;
      img.srcset = srcset;
      img.setAttribute('sizes', sizes);
    }

    return img;
  }

  /**
   * プレースホルダーSVGを作成
   * @param {number} width - 幅
   * @param {number} height - 高さ
   * @returns {string}
   */
  createPlaceholder(width = 400, height = 300) {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
      <rect fill="${this.options.placeholderColor}" width="${width}" height="${height}"/>
    </svg>`;

    return `data:image/svg+xml,${encodeURIComponent(svg)}`;
  }

  /**
   * 画像をプリロード
   * @param {string} src - 画像ソース
   * @returns {Promise}
   */
  preloadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }

  /**
   * 複数の画像をプリロード
   * @param {Array<string>} srcs - 画像ソース配列
   * @returns {Promise<Array>}
   */
  async preloadImages(srcs) {
    return Promise.all(srcs.map((src) => this.preloadImage(src)));
  }

  /**
   * 画像を圧縮
   * @param {File} file - ファイル
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async compressImage(file, options = {}) {
    const {
      maxWidth = 1600,
      maxHeight = 1600,
      quality = this.options.quality / 100,
      outputFormat = 'image/jpeg',
    } = options;

    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        const img = new Image();

        img.onload = () => {
          const canvas = document.createElement('canvas');
          let { width, height } = img;

          // アスペクト比を維持してリサイズ
          if (width > maxWidth || height > maxHeight) {
            const ratio = Math.min(maxWidth / width, maxHeight / height);
            width *= ratio;
            height *= ratio;
          }

          canvas.width = width;
          canvas.height = height;

          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);

          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(blob);
              } else {
                reject(new Error('画像の圧縮に失敗しました'));
              }
            },
            outputFormat,
            quality
          );
        };

        img.onerror = () => reject(new Error('画像の読み込みに失敗しました'));
        img.src = e.target.result;
      };

      reader.onerror = () => reject(new Error('ファイルの読み込みに失敗しました'));
      reader.readAsDataURL(file);
    });
  }

  /**
   * 画像をBase64に変換
   * @param {File} file - ファイル
   * @returns {Promise<string>}
   */
  async fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  /**
   * 画像のメタデータを取得
   * @param {string|File} source - 画像ソースまたはファイル
   * @returns {Promise<Object>}
   */
  async getImageMetadata(source) {
    let src;

    if (source instanceof File) {
      src = await this.fileToBase64(source);
    } else {
      src = source;
    }

    return new Promise((resolve, reject) => {
      const img = new Image();

      img.onload = () => {
        resolve({
          width: img.naturalWidth,
          height: img.naturalHeight,
          aspectRatio: img.naturalWidth / img.naturalHeight,
          orientation:
            img.naturalWidth > img.naturalHeight ? 'landscape' : 'portrait',
        });
      };

      img.onerror = () => reject(new Error('画像のメタデータ取得に失敗しました'));
      img.src = src;
    });
  }

  /**
   * 既存のimg要素に遅延読み込みを適用
   * @param {string} selector - セレクター
   */
  applyLazyLoading(selector = 'img[data-src]') {
    if (!this.intersectionObserver) {
      return;
    }

    const images = document.querySelectorAll(selector);
    images.forEach((img) => {
      this.intersectionObserver.observe(img);
    });
  }

  /**
   * クリーンアップ
   */
  destroy() {
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
      this.intersectionObserver = null;
    }
  }
}

/**
 * ユーティリティ関数
 */

/**
 * 画像の読み込み完了を待つ
 * @param {HTMLImageElement} img - 画像要素
 * @returns {Promise}
 */
export function waitForImageLoad(img) {
  return new Promise((resolve, reject) => {
    if (img.complete) {
      resolve(img);
    } else {
      img.onload = () => resolve(img);
      img.onerror = reject;
    }
  });
}

/**
 * 画像のアスペクト比を計算
 * @param {number} width - 幅
 * @param {number} height - 高さ
 * @returns {string}
 */
export function calculateAspectRatio(width, height) {
  const gcd = (a, b) => (b === 0 ? a : gcd(b, a % b));
  const divisor = gcd(width, height);
  return `${width / divisor}:${height / divisor}`;
}

/**
 * アスペクト比を保持したサイズを計算
 * @param {Object} original - オリジナルサイズ {width, height}
 * @param {Object} target - ターゲットサイズ {width?, height?}
 * @returns {Object}
 */
export function calculateAspectRatioSize(original, target) {
  const ratio = original.width / original.height;

  if (target.width && !target.height) {
    return {
      width: target.width,
      height: Math.round(target.width / ratio),
    };
  }

  if (target.height && !target.width) {
    return {
      width: Math.round(target.height * ratio),
      height: target.height,
    };
  }

  // 両方指定されている場合は、小さい方に合わせる
  const widthRatio = target.width / original.width;
  const heightRatio = target.height / original.height;
  const scale = Math.min(widthRatio, heightRatio);

  return {
    width: Math.round(original.width * scale),
    height: Math.round(original.height * scale),
  };
}

/**
 * 画像をトリミング
 * @param {HTMLImageElement|string} source - 画像要素またはURL
 * @param {Object} crop - トリミング設定 {x, y, width, height}
 * @param {Object} options - オプション
 * @returns {Promise<Blob>}
 */
export async function cropImage(source, crop, options = {}) {
  const { quality = 0.9, format = 'image/jpeg' } = options;

  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = crop.width;
      canvas.height = crop.height;

      const ctx = canvas.getContext('2d');
      ctx.drawImage(
        img,
        crop.x,
        crop.y,
        crop.width,
        crop.height,
        0,
        0,
        crop.width,
        crop.height
      );

      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('画像のトリミングに失敗しました'));
          }
        },
        format,
        quality
      );
    };

    img.onerror = () => reject(new Error('画像の読み込みに失敗しました'));

    if (typeof source === 'string') {
      img.src = source;
    } else {
      img.src = source.src;
    }
  });
}

/**
 * 画像を回転
 * @param {HTMLImageElement|string} source - 画像要素またはURL
 * @param {number} degrees - 回転角度（90, 180, 270）
 * @param {Object} options - オプション
 * @returns {Promise<Blob>}
 */
export async function rotateImage(source, degrees, options = {}) {
  const { quality = 0.9, format = 'image/jpeg' } = options;

  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      // 90度または270度の場合は幅と高さを入れ替え
      if (degrees === 90 || degrees === 270) {
        canvas.width = img.height;
        canvas.height = img.width;
      } else {
        canvas.width = img.width;
        canvas.height = img.height;
      }

      // 回転の中心点を設定
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate((degrees * Math.PI) / 180);
      ctx.drawImage(img, -img.width / 2, -img.height / 2);

      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('画像の回転に失敗しました'));
          }
        },
        format,
        quality
      );
    };

    img.onerror = () => reject(new Error('画像の読み込みに失敗しました'));

    if (typeof source === 'string') {
      img.src = source;
    } else {
      img.src = source.src;
    }
  });
}

// デフォルトエクスポート
export default ImageOptimizer;

// グローバルインスタンスを作成（ブラウザ環境の場合）
if (typeof window !== 'undefined') {
  window.ImageOptimizer = ImageOptimizer;
}

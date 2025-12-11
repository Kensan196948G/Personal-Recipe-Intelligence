/**
 * Camera Service
 * MediaDevices APIを使用したカメラ制御サービス
 *
 * @module camera-service
 */

class CameraService {
  constructor() {
    this.stream = null;
    this.currentFacingMode = 'environment'; // 'user' or 'environment'
    this.capabilities = null;
    this.settings = {
      width: { ideal: 1920 },
      height: { ideal: 1080 },
      facingMode: 'environment'
    };
  }

  /**
   * カメラが利用可能かチェック
   * @returns {boolean}
   */
  isSupported() {
    return !!(
      navigator.mediaDevices &&
      navigator.mediaDevices.getUserMedia
    );
  }

  /**
   * カメラストリームを開始
   * @param {Object} constraints - メディア制約
   * @returns {Promise<MediaStream>}
   */
  async startCamera(constraints = null) {
    if (!this.isSupported()) {
      throw new Error('カメラAPIがサポートされていません');
    }

    const finalConstraints = constraints || {
      video: {
        ...this.settings,
        facingMode: this.currentFacingMode
      },
      audio: false
    };

    try {
      // 既存のストリームを停止
      if (this.stream) {
        this.stopCamera();
      }

      this.stream = await navigator.mediaDevices.getUserMedia(finalConstraints);

      // カメラ機能を取得
      const videoTrack = this.stream.getVideoTracks()[0];
      this.capabilities = videoTrack.getCapabilities();

      return this.stream;
    } catch (error) {
      console.error('カメラ起動エラー:', error);
      throw new Error(`カメラの起動に失敗しました: ${error.message}`);
    }
  }

  /**
   * カメラストリームを停止
   */
  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => {
        track.stop();
      });
      this.stream = null;
    }
  }

  /**
   * 前面/背面カメラを切り替え
   * @returns {Promise<MediaStream>}
   */
  async switchCamera() {
    this.currentFacingMode = this.currentFacingMode === 'user' ? 'environment' : 'user';
    this.settings.facingMode = this.currentFacingMode;
    return await this.startCamera();
  }

  /**
   * 解像度を設定
   * @param {number} width - 幅
   * @param {number} height - 高さ
   * @returns {Promise<MediaStream>}
   */
  async setResolution(width, height) {
    this.settings.width = { ideal: width };
    this.settings.height = { ideal: height };
    return await this.startCamera();
  }

  /**
   * フラッシュ（トーチ）を制御
   * @param {boolean} enabled - 有効/無効
   * @returns {Promise<void>}
   */
  async setFlash(enabled) {
    if (!this.stream) {
      throw new Error('カメラが起動していません');
    }

    const videoTrack = this.stream.getVideoTracks()[0];
    const capabilities = videoTrack.getCapabilities();

    if (!capabilities.torch) {
      console.warn('このデバイスはフラッシュ機能をサポートしていません');
      return;
    }

    try {
      await videoTrack.applyConstraints({
        advanced: [{ torch: enabled }]
      });
    } catch (error) {
      console.error('フラッシュ制御エラー:', error);
      throw new Error('フラッシュの制御に失敗しました');
    }
  }

  /**
   * ズームを設定
   * @param {number} zoomLevel - ズームレベル
   * @returns {Promise<void>}
   */
  async setZoom(zoomLevel) {
    if (!this.stream) {
      throw new Error('カメラが起動していません');
    }

    const videoTrack = this.stream.getVideoTracks()[0];
    const capabilities = videoTrack.getCapabilities();

    if (!capabilities.zoom) {
      console.warn('このデバイスはズーム機能をサポートしていません');
      return;
    }

    const minZoom = capabilities.zoom.min;
    const maxZoom = capabilities.zoom.max;
    const clampedZoom = Math.max(minZoom, Math.min(maxZoom, zoomLevel));

    try {
      await videoTrack.applyConstraints({
        advanced: [{ zoom: clampedZoom }]
      });
    } catch (error) {
      console.error('ズーム設定エラー:', error);
      throw new Error('ズームの設定に失敗しました');
    }
  }

  /**
   * 利用可能なカメラデバイスを取得
   * @returns {Promise<Array>}
   */
  async getAvailableDevices() {
    if (!this.isSupported()) {
      return [];
    }

    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter(device => device.kind === 'videoinput');
    } catch (error) {
      console.error('デバイス列挙エラー:', error);
      return [];
    }
  }

  /**
   * 特定のデバイスIDでカメラを起動
   * @param {string} deviceId - デバイスID
   * @returns {Promise<MediaStream>}
   */
  async startCameraWithDevice(deviceId) {
    const constraints = {
      video: {
        deviceId: { exact: deviceId },
        width: this.settings.width,
        height: this.settings.height
      },
      audio: false
    };

    return await this.startCamera(constraints);
  }

  /**
   * 現在のカメラ設定を取得
   * @returns {Object}
   */
  getCurrentSettings() {
    if (!this.stream) {
      return null;
    }

    const videoTrack = this.stream.getVideoTracks()[0];
    return videoTrack.getSettings();
  }

  /**
   * カメラ機能を取得
   * @returns {Object}
   */
  getCapabilities() {
    return this.capabilities;
  }

  /**
   * 写真を撮影
   * @param {HTMLVideoElement} videoElement - ビデオ要素
   * @param {Object} options - オプション
   * @returns {Promise<Blob>}
   */
  async capturePhoto(videoElement, options = {}) {
    const {
      format = 'image/jpeg',
      quality = 0.92,
      width = null,
      height = null
    } = options;

    const canvas = document.createElement('canvas');
    const video = videoElement;

    // サイズ設定
    canvas.width = width || video.videoWidth;
    canvas.height = height || video.videoHeight;

    // 描画
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Blob変換
    return new Promise((resolve, reject) => {
      canvas.toBlob(
        blob => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('画像の生成に失敗しました'));
          }
        },
        format,
        quality
      );
    });
  }
}

// シングルトンインスタンス
const cameraService = new CameraService();

export default cameraService;

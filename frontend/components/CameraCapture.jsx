/**
 * CameraCapture Component
 * カメラ撮影UIコンポーネント
 */

import React, { useState, useRef, useEffect } from 'react';
import cameraService from '../js/camera-service.js';
import imageProcessor from '../js/image-processor.js';

const CameraCapture = ({
  onCapture,
  onClose,
  allowGallery = true,
  autoRotate = true,
  maxWidth = 1920,
  maxHeight = 1080,
  quality = 0.92
}) => {
  const [isActive, setIsActive] = useState(false);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [error, setError] = useState(null);
  const [flashEnabled, setFlashEnabled] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [facingMode, setFacingMode] = useState('environment');
  const [availableDevices, setAvailableDevices] = useState([]);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    startCamera();
    loadAvailableDevices();

    return () => {
      stopCamera();
    };
  }, []);

  /**
   * カメラを起動
   */
  const startCamera = async () => {
    try {
      setError(null);
      const stream = await cameraService.startCamera();

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          setIsCameraReady(true);
          setIsActive(true);
        };
      }
    } catch (err) {
      setError(err.message);
      console.error('カメラ起動エラー:', err);
    }
  };

  /**
   * カメラを停止
   */
  const stopCamera = () => {
    cameraService.stopCamera();
    setIsActive(false);
    setIsCameraReady(false);
  };

  /**
   * 利用可能なデバイスを読み込み
   */
  const loadAvailableDevices = async () => {
    const devices = await cameraService.getAvailableDevices();
    setAvailableDevices(devices);
  };

  /**
   * カメラを切り替え
   */
  const handleSwitchCamera = async () => {
    try {
      setIsCameraReady(false);
      await cameraService.switchCamera();
      const newMode = facingMode === 'user' ? 'environment' : 'user';
      setFacingMode(newMode);
      setIsCameraReady(true);
    } catch (err) {
      setError('カメラの切り替えに失敗しました');
      console.error('カメラ切り替えエラー:', err);
    }
  };

  /**
   * フラッシュを切り替え
   */
  const handleToggleFlash = async () => {
    try {
      const newState = !flashEnabled;
      await cameraService.setFlash(newState);
      setFlashEnabled(newState);
    } catch (err) {
      console.error('フラッシュ制御エラー:', err);
    }
  };

  /**
   * 写真を撮影
   */
  const handleCapture = async () => {
    if (!videoRef.current) {
      return;
    }

    try {
      let blob = await cameraService.capturePhoto(videoRef.current, {
        format: 'image/jpeg',
        quality: quality
      });

      // リサイズ処理
      blob = await imageProcessor.resize(blob, {
        maxWidth,
        maxHeight,
        quality,
        maintainAspectRatio: true
      });

      // 自動回転
      if (autoRotate) {
        blob = await imageProcessor.autoRotate(blob);
      }

      // プレビュー表示
      const url = URL.createObjectURL(blob);
      setCapturedImage(url);

    } catch (err) {
      setError('撮影に失敗しました');
      console.error('撮影エラー:', err);
    }
  };

  /**
   * 撮影した写真を確定
   */
  const handleConfirmCapture = async () => {
    if (!capturedImage) {
      return;
    }

    try {
      const blob = await fetch(capturedImage).then(r => r.blob());
      onCapture(blob);
      handleClose();
    } catch (err) {
      setError('画像の処理に失敗しました');
      console.error('画像処理エラー:', err);
    }
  };

  /**
   * 再撮影
   */
  const handleRetake = () => {
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage);
    }
    setCapturedImage(null);
  };

  /**
   * ギャラリーから選択
   */
  const handleGallerySelect = () => {
    fileInputRef.current?.click();
  };

  /**
   * ファイル選択時の処理
   */
  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    try {
      let blob = file;

      // リサイズ処理
      blob = await imageProcessor.resize(blob, {
        maxWidth,
        maxHeight,
        quality,
        maintainAspectRatio: true
      });

      // 自動回転
      if (autoRotate) {
        blob = await imageProcessor.autoRotate(blob);
      }

      onCapture(blob);
      handleClose();
    } catch (err) {
      setError('画像の処理に失敗しました');
      console.error('ファイル処理エラー:', err);
    }
  };

  /**
   * 閉じる
   */
  const handleClose = () => {
    stopCamera();
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage);
    }
    onClose();
  };

  return (
    <div className="camera-capture">
      <div className="camera-container">
        {/* ヘッダー */}
        <div className="camera-header">
          <button
            onClick={handleClose}
            className="btn-close"
            aria-label="閉じる"
          >
            ✕
          </button>
          <h2>写真を撮影</h2>
          <div className="spacer"></div>
        </div>

        {/* エラー表示 */}
        {error && (
          <div className="camera-error">
            {error}
          </div>
        )}

        {/* カメラプレビュー */}
        <div className="camera-preview">
          {!capturedImage ? (
            <>
              <video
                ref={videoRef}
                className="camera-video"
                autoPlay
                playsInline
                muted
              />
              <canvas
                ref={canvasRef}
                className="camera-canvas"
                style={{ display: 'none' }}
              />
            </>
          ) : (
            <img
              src={capturedImage}
              alt="撮影した写真"
              className="captured-image"
            />
          )}
        </div>

        {/* コントロール */}
        <div className="camera-controls">
          {!capturedImage ? (
            <>
              {/* ギャラリーボタン */}
              {allowGallery && (
                <button
                  onClick={handleGallerySelect}
                  className="btn-gallery"
                  aria-label="ギャラリーから選択"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                    <path d="M21 15L16 10L5 21" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </button>
              )}

              {/* シャッターボタン */}
              <button
                onClick={handleCapture}
                className="btn-shutter"
                disabled={!isCameraReady}
                aria-label="撮影"
              >
                <div className="shutter-outer">
                  <div className="shutter-inner"></div>
                </div>
              </button>

              {/* カメラ切り替えボタン */}
              {availableDevices.length > 1 && (
                <button
                  onClick={handleSwitchCamera}
                  className="btn-switch"
                  disabled={!isCameraReady}
                  aria-label="カメラ切り替え"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M20 5H16L14 3H10L8 5H4C2.9 5 2 5.9 2 7V19C2 20.1 2.9 21 4 21H20C21.1 21 22 20.1 22 19V7C22 5.9 21.1 5 20 5Z" stroke="currentColor" strokeWidth="2"/>
                    <path d="M15 11L12 8L9 11" stroke="currentColor" strokeWidth="2"/>
                    <path d="M9 13L12 16L15 13" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </button>
              )}
            </>
          ) : (
            <>
              {/* 再撮影ボタン */}
              <button
                onClick={handleRetake}
                className="btn-retake"
              >
                再撮影
              </button>

              {/* 確定ボタン */}
              <button
                onClick={handleConfirmCapture}
                className="btn-confirm"
              >
                この写真を使用
              </button>
            </>
          )}
        </div>

        {/* フラッシュボタン（常時表示） */}
        {!capturedImage && (
          <button
            onClick={handleToggleFlash}
            className={`btn-flash ${flashEnabled ? 'active' : ''}`}
            disabled={!isCameraReady}
            aria-label="フラッシュ"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M7 2V13H10V22L17 10H13L17 2H7Z" fill={flashEnabled ? '#ffeb3b' : 'currentColor'}/>
            </svg>
          </button>
        )}

        {/* ファイル入力（非表示） */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      <style jsx>{`
        .camera-capture {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: #000;
          z-index: 1000;
        }

        .camera-container {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .camera-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px;
          background: rgba(0, 0, 0, 0.8);
          color: #fff;
        }

        .camera-header h2 {
          margin: 0;
          font-size: 18px;
          font-weight: 500;
        }

        .btn-close {
          background: none;
          border: none;
          color: #fff;
          font-size: 24px;
          cursor: pointer;
          padding: 0;
          width: 32px;
          height: 32px;
        }

        .spacer {
          width: 32px;
        }

        .camera-error {
          padding: 12px 16px;
          background: #f44336;
          color: #fff;
          text-align: center;
        }

        .camera-preview {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          background: #000;
        }

        .camera-video,
        .captured-image {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }

        .camera-controls {
          padding: 24px;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 24px;
        }

        .btn-gallery,
        .btn-switch {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          border-radius: 50%;
          width: 56px;
          height: 56px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-gallery:hover,
        .btn-switch:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .btn-gallery:disabled,
        .btn-switch:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-shutter {
          background: none;
          border: none;
          padding: 0;
          cursor: pointer;
        }

        .btn-shutter:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .shutter-outer {
          width: 72px;
          height: 72px;
          border: 4px solid #fff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.1s;
        }

        .btn-shutter:active .shutter-outer {
          transform: scale(0.95);
        }

        .shutter-inner {
          width: 56px;
          height: 56px;
          background: #fff;
          border-radius: 50%;
        }

        .btn-retake,
        .btn-confirm {
          padding: 12px 24px;
          border: none;
          border-radius: 24px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-retake {
          background: rgba(255, 255, 255, 0.2);
          color: #fff;
        }

        .btn-retake:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .btn-confirm {
          background: #4caf50;
          color: #fff;
        }

        .btn-confirm:hover {
          background: #45a049;
        }

        .btn-flash {
          position: absolute;
          top: 80px;
          right: 16px;
          background: rgba(0, 0, 0, 0.5);
          border: none;
          border-radius: 50%;
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-flash:hover {
          background: rgba(0, 0, 0, 0.7);
        }

        .btn-flash.active {
          background: rgba(255, 235, 59, 0.3);
        }

        .btn-flash:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default CameraCapture;

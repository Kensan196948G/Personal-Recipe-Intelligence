/**
 * RecipePhotoCapture Component
 * レシピ写真撮影フロー
 */

import React, { useState, useRef, useEffect } from 'react';
import cameraService from '../js/camera-service.js';
import imageProcessor from '../js/image-processor.js';

const RecipePhotoCapture = ({
  onComplete,
  onClose,
  maxPhotos = 5,
  showGuide = true,
  autoRotate = true
}) => {
  const [step, setStep] = useState('capture'); // 'capture', 'preview', 'complete'
  const [photos, setPhotos] = useState([]);
  const [currentPhoto, setCurrentPhoto] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [error, setError] = useState(null);
  const [guideVisible, setGuideVisible] = useState(showGuide);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    startCamera();

    return () => {
      stopCamera();
      cleanupPhotos();
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
   * 写真をクリーンアップ
   */
  const cleanupPhotos = () => {
    photos.forEach(photo => {
      if (photo.url) {
        URL.revokeObjectURL(photo.url);
      }
    });
    if (currentPhoto?.url) {
      URL.revokeObjectURL(currentPhoto.url);
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
        quality: 0.92
      });

      // リサイズ処理
      blob = await imageProcessor.resize(blob, {
        maxWidth: 1920,
        maxHeight: 1080,
        quality: 0.92,
        maintainAspectRatio: true
      });

      // 自動回転
      if (autoRotate) {
        blob = await imageProcessor.autoRotate(blob);
      }

      // プレビュー表示
      const url = URL.createObjectURL(blob);
      setCurrentPhoto({
        blob,
        url,
        timestamp: Date.now()
      });
      setStep('preview');

    } catch (err) {
      setError('撮影に失敗しました');
      console.error('撮影エラー:', err);
    }
  };

  /**
   * 撮影した写真を保存
   */
  const handleSavePhoto = () => {
    if (!currentPhoto) {
      return;
    }

    const newPhotos = [...photos, currentPhoto];
    setPhotos(newPhotos);
    setCurrentPhoto(null);
    setStep('capture');

    // 最大枚数に達した場合は完了
    if (newPhotos.length >= maxPhotos) {
      handleComplete(newPhotos);
    }
  };

  /**
   * 再撮影
   */
  const handleRetake = () => {
    if (currentPhoto?.url) {
      URL.revokeObjectURL(currentPhoto.url);
    }
    setCurrentPhoto(null);
    setStep('capture');
  };

  /**
   * 写真を削除
   */
  const handleDeletePhoto = (index) => {
    const photo = photos[index];
    if (photo?.url) {
      URL.revokeObjectURL(photo.url);
    }
    setPhotos(photos.filter((_, i) => i !== index));
  };

  /**
   * 完了
   */
  const handleComplete = (photosToSend = photos) => {
    if (photosToSend.length === 0) {
      setError('最低1枚の写真を撮影してください');
      return;
    }

    stopCamera();
    onComplete(photosToSend.map(p => p.blob));
  };

  /**
   * キャンセル
   */
  const handleCancel = () => {
    stopCamera();
    cleanupPhotos();
    onClose();
  };

  /**
   * ガイドを非表示
   */
  const handleDismissGuide = () => {
    setGuideVisible(false);
  };

  return (
    <div className="recipe-photo-capture">
      <div className="capture-container">
        {/* ヘッダー */}
        <div className="capture-header">
          <button
            onClick={handleCancel}
            className="btn-cancel"
            aria-label="キャンセル"
          >
            ✕
          </button>
          <h2>レシピ写真を撮影</h2>
          <div className="photo-counter">
            {photos.length}/{maxPhotos}
          </div>
        </div>

        {/* エラー表示 */}
        {error && (
          <div className="capture-error">
            {error}
          </div>
        )}

        {/* メインビュー */}
        <div className="capture-main">
          {step === 'capture' && (
            <div className="camera-view">
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

              {/* 撮影ガイドオーバーレイ */}
              {guideVisible && (
                <div className="guide-overlay">
                  <div className="guide-frame">
                    <div className="guide-corner top-left"></div>
                    <div className="guide-corner top-right"></div>
                    <div className="guide-corner bottom-left"></div>
                    <div className="guide-corner bottom-right"></div>
                  </div>
                  <div className="guide-text">
                    <p>レシピが枠内に収まるように撮影してください</p>
                    <button
                      onClick={handleDismissGuide}
                      className="btn-dismiss-guide"
                    >
                      ガイドを非表示
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {step === 'preview' && currentPhoto && (
            <div className="preview-view">
              <img
                src={currentPhoto.url}
                alt="撮影プレビュー"
                className="preview-image"
              />
            </div>
          )}
        </div>

        {/* サムネイル一覧 */}
        {photos.length > 0 && (
          <div className="thumbnails">
            {photos.map((photo, index) => (
              <div key={index} className="thumbnail">
                <img src={photo.url} alt={`写真 ${index + 1}`} />
                <button
                  onClick={() => handleDeletePhoto(index)}
                  className="btn-delete-thumbnail"
                  aria-label="削除"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {/* コントロール */}
        <div className="capture-controls">
          {step === 'capture' && (
            <>
              <button
                onClick={() => handleComplete()}
                className="btn-complete"
                disabled={photos.length === 0}
              >
                完了 ({photos.length})
              </button>

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

              <div className="spacer"></div>
            </>
          )}

          {step === 'preview' && (
            <>
              <button
                onClick={handleRetake}
                className="btn-retake"
              >
                再撮影
              </button>

              <button
                onClick={handleSavePhoto}
                className="btn-save"
              >
                保存
              </button>
            </>
          )}
        </div>

        {/* ヒント */}
        <div className="capture-hints">
          <div className="hint-item">
            <span className="hint-icon">💡</span>
            <span className="hint-text">明るい場所で撮影すると認識精度が向上します</span>
          </div>
          <div className="hint-item">
            <span className="hint-icon">📐</span>
            <span className="hint-text">真上から撮影すると文字が読み取りやすくなります</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .recipe-photo-capture {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: #000;
          z-index: 1000;
        }

        .capture-container {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .capture-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px;
          background: rgba(0, 0, 0, 0.8);
          color: #fff;
        }

        .capture-header h2 {
          margin: 0;
          font-size: 18px;
          font-weight: 500;
        }

        .btn-cancel {
          background: none;
          border: none;
          color: #fff;
          font-size: 24px;
          cursor: pointer;
          padding: 0;
          width: 32px;
          height: 32px;
        }

        .photo-counter {
          font-size: 16px;
          font-weight: 500;
          min-width: 50px;
          text-align: right;
        }

        .capture-error {
          padding: 12px 16px;
          background: #f44336;
          color: #fff;
          text-align: center;
        }

        .capture-main {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          background: #000;
          position: relative;
        }

        .camera-view,
        .preview-view {
          width: 100%;
          height: 100%;
          position: relative;
        }

        .camera-video,
        .preview-image {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }

        .guide-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
        }

        .guide-frame {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 80%;
          max-width: 400px;
          aspect-ratio: 3/4;
          border: 2px dashed rgba(255, 255, 255, 0.6);
        }

        .guide-corner {
          position: absolute;
          width: 20px;
          height: 20px;
          border: 3px solid #4caf50;
        }

        .guide-corner.top-left {
          top: -2px;
          left: -2px;
          border-right: none;
          border-bottom: none;
        }

        .guide-corner.top-right {
          top: -2px;
          right: -2px;
          border-left: none;
          border-bottom: none;
        }

        .guide-corner.bottom-left {
          bottom: -2px;
          left: -2px;
          border-right: none;
          border-top: none;
        }

        .guide-corner.bottom-right {
          bottom: -2px;
          right: -2px;
          border-left: none;
          border-top: none;
        }

        .guide-text {
          position: absolute;
          bottom: 120px;
          left: 0;
          right: 0;
          text-align: center;
          color: #fff;
          padding: 0 20px;
          pointer-events: auto;
        }

        .guide-text p {
          margin: 0 0 12px 0;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        }

        .btn-dismiss-guide {
          background: rgba(0, 0, 0, 0.6);
          border: 1px solid rgba(255, 255, 255, 0.3);
          color: #fff;
          padding: 8px 16px;
          border-radius: 20px;
          cursor: pointer;
          font-size: 14px;
        }

        .thumbnails {
          display: flex;
          gap: 8px;
          padding: 12px 16px;
          background: rgba(0, 0, 0, 0.8);
          overflow-x: auto;
        }

        .thumbnail {
          position: relative;
          flex-shrink: 0;
          width: 80px;
          height: 80px;
          border-radius: 8px;
          overflow: hidden;
          border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .thumbnail img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .btn-delete-thumbnail {
          position: absolute;
          top: 4px;
          right: 4px;
          background: rgba(0, 0, 0, 0.8);
          border: none;
          color: #fff;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          font-size: 12px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .capture-controls {
          padding: 24px;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 24px;
        }

        .btn-complete {
          background: rgba(76, 175, 80, 0.8);
          border: none;
          color: #fff;
          padding: 12px 24px;
          border-radius: 24px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-complete:hover {
          background: rgba(76, 175, 80, 1);
        }

        .btn-complete:disabled {
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

        .spacer {
          width: 120px;
        }

        .btn-retake,
        .btn-save {
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

        .btn-save {
          background: #4caf50;
          color: #fff;
        }

        .btn-save:hover {
          background: #45a049;
        }

        .capture-hints {
          padding: 12px 16px;
          background: rgba(0, 0, 0, 0.8);
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .hint-item {
          display: flex;
          align-items: center;
          gap: 8px;
          color: rgba(255, 255, 255, 0.7);
          font-size: 13px;
          margin-bottom: 4px;
        }

        .hint-item:last-child {
          margin-bottom: 0;
        }

        .hint-icon {
          font-size: 16px;
        }

        .hint-text {
          flex: 1;
        }
      `}</style>
    </div>
  );
};

export default RecipePhotoCapture;

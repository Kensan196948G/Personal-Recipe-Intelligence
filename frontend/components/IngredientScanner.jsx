/**
 * IngredientScanner - 食材画像スキャナーコンポーネント
 *
 * カメラ撮影 / ファイルアップロードから食材を認識
 */

import React, { useState, useRef, useEffect } from 'react';
import './IngredientScanner.css';

const IngredientScanner = () => {
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [recognitionResults, setRecognitionResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIngredients, setSelectedIngredients] = useState([]);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamRef = useRef(null);

  // カメラ起動
  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }  // 背面カメラ優先
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setError('カメラへのアクセスに失敗しました。ファイルアップロードをご利用ください。');
    }
  };

  // カメラ停止
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  // 写真撮影
  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // キャンバスサイズをビデオに合わせる
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // 画像を描画
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Base64変換
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(imageData);

    // カメラ停止
    stopCamera();

    // 認識実行
    recognizeImage(imageData);
  };

  // ファイルアップロード
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const imageData = e.target.result;
      setCapturedImage(imageData);
      recognizeImage(imageData);
    };
    reader.readAsDataURL(file);
  };

  // 画像認識実行
  const recognizeImage = async (imageData) => {
    setLoading(true);
    setError(null);
    setRecognitionResults([]);

    try {
      // Base64のプレフィックス除去
      const base64Data = imageData.split(',')[1];

      const response = await fetch('/api/v1/ai/image/recognize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_base64: base64Data,
          max_results: 10
        })
      });

      const result = await response.json();

      if (result.status === 'ok' && result.data) {
        setRecognitionResults(result.data);
      } else {
        setError(result.error || '認識に失敗しました');
      }
    } catch (err) {
      console.error('Recognition error:', err);
      setError('認識処理中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  // 食材選択トグル
  const toggleIngredientSelection = (ingredientId) => {
    setSelectedIngredients(prev => {
      if (prev.includes(ingredientId)) {
        return prev.filter(id => id !== ingredientId);
      } else {
        return [...prev, ingredientId];
      }
    });
  };

  // レシピ検索へ
  const searchRecipesByIngredients = () => {
    if (selectedIngredients.length === 0) {
      alert('食材を選択してください');
      return;
    }

    // 選択された食材の日本語名を取得
    const selectedNames = recognitionResults
      .filter(r => selectedIngredients.includes(r.ingredient_id))
      .map(r => r.name);

    // レシピ検索ページへ遷移（クエリパラメータ付き）
    window.location.href = `/recipes?ingredients=${encodeURIComponent(selectedNames.join(','))}`;
  };

  // リセット
  const reset = () => {
    setCapturedImage(null);
    setRecognitionResults([]);
    setSelectedIngredients([]);
    setError(null);
  };

  // クリーンアップ
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="ingredient-scanner">
      <div className="scanner-header">
        <h2>食材スキャナー</h2>
        <p>カメラで撮影、または画像をアップロードして食材を認識します</p>
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠</span>
          {error}
        </div>
      )}

      {/* カメラビュー / 撮影画像 */}
      <div className="camera-container">
        {!capturedImage && !cameraActive && (
          <div className="camera-placeholder">
            <div className="placeholder-icon">📷</div>
            <p>カメラを起動するか、画像をアップロードしてください</p>
            <div className="action-buttons">
              <button onClick={startCamera} className="btn-primary">
                カメラ起動
              </button>
              <button onClick={() => fileInputRef.current?.click()} className="btn-secondary">
                ファイル選択
              </button>
            </div>
          </div>
        )}

        {cameraActive && (
          <div className="camera-view">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="video-preview"
            />
            <div className="camera-controls">
              <button onClick={capturePhoto} className="btn-capture">
                撮影
              </button>
              <button onClick={stopCamera} className="btn-cancel">
                キャンセル
              </button>
            </div>
          </div>
        )}

        {capturedImage && (
          <div className="captured-image">
            <img src={capturedImage} alt="Captured" />
            <button onClick={reset} className="btn-reset">
              再撮影
            </button>
          </div>
        )}

        {/* 隠しファイル入力 */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
        />

        {/* 隠しキャンバス（撮影用） */}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>

      {/* ローディング */}
      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>画像を認識中...</p>
        </div>
      )}

      {/* 認識結果 */}
      {recognitionResults.length > 0 && !loading && (
        <div className="recognition-results">
          <h3>認識された食材</h3>
          <p className="results-hint">レシピ検索に使用する食材を選択してください</p>

          <div className="results-list">
            {recognitionResults.map((result) => (
              <div
                key={result.ingredient_id}
                className={`result-item ${selectedIngredients.includes(result.ingredient_id) ? 'selected' : ''}`}
                onClick={() => toggleIngredientSelection(result.ingredient_id)}
              >
                <div className="result-info">
                  <div className="result-name">
                    <strong>{result.name}</strong>
                    <span className="result-name-en">{result.name_en}</span>
                  </div>
                  <div className="result-meta">
                    <span className="result-category">{result.category}</span>
                    <span className="result-confidence">
                      信頼度: {(result.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="result-keywords">
                    {result.keywords.map((kw, idx) => (
                      <span key={idx} className="keyword-tag">{kw}</span>
                    ))}
                  </div>
                </div>
                <div className="result-checkbox">
                  {selectedIngredients.includes(result.ingredient_id) ? '✓' : ''}
                </div>
              </div>
            ))}
          </div>

          {/* レシピ検索ボタン */}
          <div className="search-action">
            <button
              onClick={searchRecipesByIngredients}
              className="btn-search-recipes"
              disabled={selectedIngredients.length === 0}
            >
              選択した食材でレシピ検索 ({selectedIngredients.length}件)
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default IngredientScanner;

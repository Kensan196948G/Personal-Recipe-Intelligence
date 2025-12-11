/**
 * 外部レシピインポートコンポーネント
 *
 * URLからレシピをインポートする機能を提供
 */

import React, { useState } from 'react';

const ExternalRecipeImport = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);
  const [importSuccess, setImportSuccess] = useState(false);
  const [supportedSites, setSupportedSites] = useState([]);

  // 対応サイト一覧を取得
  const fetchSupportedSites = async () => {
    try {
      const response = await fetch('/api/v1/external/supported-sites');
      const data = await response.json();
      if (data.status === 'ok') {
        setSupportedSites(data.data);
      }
    } catch (err) {
      console.error('Failed to fetch supported sites:', err);
    }
  };

  // コンポーネントマウント時に対応サイトを取得
  React.useEffect(() => {
    fetchSupportedSites();
  }, []);

  // プレビュー取得
  const handlePreview = async () => {
    if (!url.trim()) {
      setError('URLを入力してください');
      return;
    }

    setLoading(true);
    setError(null);
    setPreview(null);
    setImportSuccess(false);

    try {
      const response = await fetch('/api/v1/external/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.status === 'ok' && data.data) {
        setPreview(data.data);
      } else {
        setError(data.error || 'プレビューの取得に失敗しました');
      }
    } catch (err) {
      setError('プレビューの取得に失敗しました: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // インポート実行
  const handleImport = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/external/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.status === 'ok') {
        setImportSuccess(true);
        setPreview(null);
        setUrl('');
        // 成功通知を表示
        setTimeout(() => setImportSuccess(false), 5000);
      } else {
        setError(data.error || 'インポートに失敗しました');
      }
    } catch (err) {
      setError('インポートに失敗しました: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // キャンセル
  const handleCancel = () => {
    setPreview(null);
    setError(null);
  };

  return (
    <div className="external-recipe-import">
      <h2>外部レシピをインポート</h2>

      {/* URL入力フォーム */}
      <div className="import-form">
        <div className="input-group">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="レシピページのURLを入力してください"
            disabled={loading || !!preview}
            className="url-input"
          />
          <button
            onClick={handlePreview}
            disabled={loading || !!preview}
            className="btn-preview"
          >
            {loading ? '読込中...' : 'プレビュー'}
          </button>
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}

        {/* 成功メッセージ */}
        {importSuccess && (
          <div className="success-message">
            <span className="success-icon">✓</span>
            レシピをインポートしました
          </div>
        )}
      </div>

      {/* プレビュー表示 */}
      {preview && (
        <div className="recipe-preview">
          <h3>プレビュー</h3>

          <div className="preview-content">
            {preview.image_url && (
              <div className="preview-image">
                <img src={preview.image_url} alt={preview.title} />
              </div>
            )}

            <div className="preview-details">
              <h4>{preview.title}</h4>

              {preview.description && (
                <p className="description">{preview.description}</p>
              )}

              <div className="meta-info">
                {preview.cooking_time && (
                  <span className="meta-item">
                    <span className="meta-icon">⏱</span>
                    {preview.cooking_time}
                  </span>
                )}

                {preview.servings && (
                  <span className="meta-item">
                    <span className="meta-icon">👥</span>
                    {preview.servings}
                  </span>
                )}

                {preview.ingredient_count && (
                  <span className="meta-item">
                    <span className="meta-icon">🥕</span>
                    材料 {preview.ingredient_count}個
                  </span>
                )}

                {preview.step_count && (
                  <span className="meta-item">
                    <span className="meta-icon">📝</span>
                    手順 {preview.step_count}個
                  </span>
                )}
              </div>

              {preview.author && (
                <p className="author">作成者: {preview.author}</p>
              )}

              <p className="source-url">
                <a href={preview.source_url} target="_blank" rel="noopener noreferrer">
                  元のページを開く
                </a>
              </p>
            </div>
          </div>

          <div className="preview-actions">
            <button
              onClick={handleImport}
              disabled={loading}
              className="btn-import"
            >
              {loading ? 'インポート中...' : 'インポート'}
            </button>
            <button
              onClick={handleCancel}
              disabled={loading}
              className="btn-cancel"
            >
              キャンセル
            </button>
          </div>
        </div>
      )}

      {/* 対応サイト一覧 */}
      {supportedSites.length > 0 && !preview && (
        <div className="supported-sites">
          <h3>対応サイト</h3>
          <div className="sites-list">
            {supportedSites.map((site, index) => (
              <div key={index} className="site-item">
                <span className="site-icon">{site.icon}</span>
                <span className="site-name">{site.name}</span>
                <span className="site-domain">{site.domain}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .external-recipe-import {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }

        h2 {
          font-size: 24px;
          margin-bottom: 20px;
          color: #333;
        }

        h3 {
          font-size: 20px;
          margin-bottom: 15px;
          color: #555;
        }

        .import-form {
          margin-bottom: 30px;
        }

        .input-group {
          display: flex;
          gap: 10px;
          margin-bottom: 10px;
        }

        .url-input {
          flex: 1;
          padding: 12px;
          font-size: 14px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .url-input:focus {
          outline: none;
          border-color: #4CAF50;
        }

        .url-input:disabled {
          background-color: #f5f5f5;
          cursor: not-allowed;
        }

        .btn-preview,
        .btn-import,
        .btn-cancel {
          padding: 12px 24px;
          font-size: 14px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .btn-preview {
          background-color: #2196F3;
          color: white;
        }

        .btn-preview:hover:not(:disabled) {
          background-color: #1976D2;
        }

        .btn-preview:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .error-message {
          padding: 12px;
          background-color: #ffebee;
          border: 1px solid #ef5350;
          border-radius: 4px;
          color: #c62828;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .error-icon {
          font-size: 18px;
        }

        .success-message {
          padding: 12px;
          background-color: #e8f5e9;
          border: 1px solid #4CAF50;
          border-radius: 4px;
          color: #2e7d32;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .success-icon {
          font-size: 18px;
        }

        .recipe-preview {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 20px;
          background-color: #fff;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .preview-content {
          display: flex;
          gap: 20px;
          margin-bottom: 20px;
        }

        .preview-image {
          flex: 0 0 200px;
        }

        .preview-image img {
          width: 100%;
          border-radius: 8px;
          object-fit: cover;
        }

        .preview-details {
          flex: 1;
        }

        .preview-details h4 {
          font-size: 18px;
          margin-bottom: 10px;
          color: #333;
        }

        .description {
          font-size: 14px;
          color: #666;
          margin-bottom: 15px;
          line-height: 1.5;
        }

        .meta-info {
          display: flex;
          flex-wrap: wrap;
          gap: 15px;
          margin-bottom: 15px;
        }

        .meta-item {
          display: flex;
          align-items: center;
          gap: 5px;
          font-size: 14px;
          color: #555;
        }

        .meta-icon {
          font-size: 16px;
        }

        .author {
          font-size: 14px;
          color: #666;
          margin-bottom: 10px;
        }

        .source-url a {
          font-size: 14px;
          color: #2196F3;
          text-decoration: none;
        }

        .source-url a:hover {
          text-decoration: underline;
        }

        .preview-actions {
          display: flex;
          gap: 10px;
          justify-content: flex-end;
        }

        .btn-import {
          background-color: #4CAF50;
          color: white;
        }

        .btn-import:hover:not(:disabled) {
          background-color: #45a049;
        }

        .btn-import:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .btn-cancel {
          background-color: #f44336;
          color: white;
        }

        .btn-cancel:hover:not(:disabled) {
          background-color: #da190b;
        }

        .btn-cancel:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .supported-sites {
          margin-top: 30px;
          padding-top: 30px;
          border-top: 1px solid #ddd;
        }

        .sites-list {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 15px;
        }

        .site-item {
          padding: 15px;
          border: 1px solid #ddd;
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 5px;
          background-color: #f9f9f9;
        }

        .site-icon {
          font-size: 32px;
        }

        .site-name {
          font-weight: bold;
          font-size: 14px;
          color: #333;
        }

        .site-domain {
          font-size: 12px;
          color: #666;
        }

        @media (max-width: 600px) {
          .preview-content {
            flex-direction: column;
          }

          .preview-image {
            flex: 0 0 auto;
          }

          .sites-list {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default ExternalRecipeImport;

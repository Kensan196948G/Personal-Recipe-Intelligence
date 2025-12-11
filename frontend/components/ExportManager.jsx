/**
 * エクスポート管理コンポーネント
 *
 * 複数フォーマットでのエクスポート、レシピブック生成、買い物リスト、栄養レポート、バックアップ機能を提供
 */

import React, { useState, useEffect } from 'react';

const ExportManager = ({ selectedRecipeIds = [] }) => {
  const [exportType, setExportType] = useState('recipes');
  const [format, setFormat] = useState('json');
  const [supportedFormats, setSupportedFormats] = useState({});
  const [backups, setBackups] = useState([]);
  const [options, setOptions] = useState({
    indent: 2,
    ensure_ascii: false,
    title: 'レシピブック',
    theme: 'default'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadSupportedFormats();
    if (exportType === 'restore') {
      loadBackups();
    }
  }, [exportType]);

  // 対応フォーマットを読み込み
  const loadSupportedFormats = async () => {
    try {
      const response = await fetch('/api/v1/export/formats');
      const data = await response.json();
      setSupportedFormats(data);
    } catch (err) {
      console.error('Failed to load supported formats:', err);
    }
  };

  // バックアップ一覧を読み込み
  const loadBackups = async () => {
    try {
      const response = await fetch('/api/v1/export/backups');
      const result = await response.json();
      if (result.status === 'ok') {
        setBackups(result.data.backups);
      }
    } catch (err) {
      console.error('Failed to load backups:', err);
    }
  };

  // エクスポート実行
  const handleExport = async () => {
    if (exportType !== 'backup' && selectedRecipeIds.length === 0) {
      setError('エクスポート対象のレシピを選択してください');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      let endpoint = '';
      let requestBody = {};

      switch (exportType) {
        case 'recipes':
          endpoint = '/api/v1/export/recipes';
          requestBody = {
            recipe_ids: selectedRecipeIds,
            format: format,
            options: options
          };
          break;

        case 'recipe-book':
          endpoint = '/api/v1/export/recipe-book';
          requestBody = {
            recipe_ids: selectedRecipeIds,
            title: options.title,
            theme: options.theme,
            options: options
          };
          break;

        case 'shopping-list':
          endpoint = '/api/v1/export/shopping-list';
          requestBody = {
            recipe_ids: selectedRecipeIds,
            format: format,
            options: options
          };
          break;

        case 'nutrition-report':
          endpoint = '/api/v1/export/nutrition-report';
          requestBody = {
            recipe_ids: selectedRecipeIds,
            format: format,
            options: options
          };
          break;

        case 'backup':
          endpoint = '/api/v1/export/backup';
          requestBody = {
            metadata: {
              note: options.backupNote || ''
            }
          };
          break;

        default:
          throw new Error('Unknown export type');
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Export failed');
      }

      // バックアップの場合はJSON、それ以外はバイナリ
      if (exportType === 'backup') {
        const result = await response.json();
        setSuccess(`バックアップを作成しました: ${result.data.backup_file}`);
        loadBackups();
      } else {
        // ファイルをダウンロード
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // ファイル名を取得
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'export';
        if (contentDisposition) {
          const matches = /filename="(.+)"/.exec(contentDisposition);
          if (matches && matches[1]) {
            filename = matches[1];
          }
        }

        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        setSuccess('エクスポートが完了しました');
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // リストア実行
  const handleRestore = async (backupFile) => {
    if (!confirm('バックアップからリストアしますか？現在のデータは上書きされます。')) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/v1/export/restore', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          backup_file: backupFile
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Restore failed');
      }

      const result = await response.json();
      setSuccess(`${result.data.restored_recipe_count}件のレシピをリストアしました`);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // フォーマット選択肢
  const getFormatOptions = () => {
    switch (exportType) {
      case 'recipes':
        return Object.entries(supportedFormats).map(([key, info]) => (
          <option key={key} value={key}>{info.name}</option>
        ));

      case 'shopping-list':
        return [
          <option key="markdown" value="markdown">Markdown</option>,
          <option key="json" value="json">JSON</option>
        ];

      case 'nutrition-report':
        return [
          <option key="json" value="json">JSON</option>,
          <option key="csv" value="csv">CSV</option>
        ];

      default:
        return null;
    }
  };

  return (
    <div className="export-manager">
      <style>{`
        .export-manager {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }

        .export-section {
          background: white;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .export-section h2 {
          margin-top: 0;
          margin-bottom: 15px;
          color: #333;
          font-size: 18px;
        }

        .form-group {
          margin-bottom: 15px;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: 500;
          color: #555;
        }

        .form-group select,
        .form-group input[type="text"],
        .form-group input[type="number"],
        .form-group textarea {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .form-group textarea {
          min-height: 60px;
          resize: vertical;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 15px;
        }

        .button-group {
          display: flex;
          gap: 10px;
          margin-top: 20px;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: background-color 0.2s;
        }

        .btn-primary {
          background-color: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background-color: #0056b3;
        }

        .btn-primary:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .alert {
          padding: 12px;
          border-radius: 4px;
          margin-bottom: 15px;
        }

        .alert-error {
          background-color: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }

        .alert-success {
          background-color: #d4edda;
          color: #155724;
          border: 1px solid #c3e6cb;
        }

        .info-text {
          font-size: 13px;
          color: #666;
          margin-top: 5px;
        }

        .backup-list {
          list-style: none;
          padding: 0;
          margin: 15px 0 0 0;
        }

        .backup-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          margin-bottom: 10px;
        }

        .backup-info {
          flex: 1;
        }

        .backup-filename {
          font-weight: 500;
          color: #333;
        }

        .backup-meta {
          font-size: 12px;
          color: #666;
          margin-top: 4px;
        }

        .btn-small {
          padding: 6px 12px;
          font-size: 12px;
        }

        .btn-secondary {
          background-color: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background-color: #545b62;
        }
      `}</style>

      <div className="export-section">
        <h2>エクスポート</h2>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="form-group">
          <label>エクスポートタイプ</label>
          <select value={exportType} onChange={(e) => setExportType(e.target.value)}>
            <option value="recipes">レシピエクスポート</option>
            <option value="recipe-book">レシピブック生成 (PDF)</option>
            <option value="shopping-list">買い物リスト</option>
            <option value="nutrition-report">栄養レポート</option>
            <option value="backup">フルバックアップ</option>
            <option value="restore">バックアップからリストア</option>
          </select>
        </div>

        {exportType !== 'backup' && exportType !== 'restore' && exportType !== 'recipe-book' && (
          <div className="form-group">
            <label>フォーマット</label>
            <select value={format} onChange={(e) => setFormat(e.target.value)}>
              {getFormatOptions()}
            </select>
          </div>
        )}

        {exportType === 'recipe-book' && (
          <>
            <div className="form-group">
              <label>レシピブックタイトル</label>
              <input
                type="text"
                value={options.title}
                onChange={(e) => setOptions({...options, title: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>テーマ</label>
              <select
                value={options.theme}
                onChange={(e) => setOptions({...options, theme: e.target.value})}
              >
                <option value="default">デフォルト</option>
                <option value="elegant">エレガント</option>
                <option value="modern">モダン</option>
              </select>
            </div>
          </>
        )}

        {exportType === 'backup' && (
          <div className="form-group">
            <label>バックアップメモ（任意）</label>
            <textarea
              value={options.backupNote || ''}
              onChange={(e) => setOptions({...options, backupNote: e.target.value})}
              placeholder="このバックアップの説明を入力..."
            />
          </div>
        )}

        {exportType === 'restore' && (
          <div className="form-group">
            <label>バックアップ一覧</label>
            {backups.length === 0 ? (
              <p className="info-text">バックアップがありません</p>
            ) : (
              <ul className="backup-list">
                {backups.map((backup, index) => (
                  <li key={index} className="backup-item">
                    <div className="backup-info">
                      <div className="backup-filename">{backup.filename}</div>
                      <div className="backup-meta">
                        作成日時: {new Date(backup.created_at).toLocaleString('ja-JP')} |
                        レシピ数: {backup.recipe_count}件 |
                        サイズ: {(backup.size_bytes / 1024).toFixed(1)} KB
                      </div>
                    </div>
                    <button
                      className="btn btn-secondary btn-small"
                      onClick={() => handleRestore(backup.file)}
                      disabled={loading}
                    >
                      リストア
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {exportType !== 'restore' && (
          <>
            {selectedRecipeIds.length > 0 && exportType !== 'backup' && (
              <p className="info-text">
                選択中: {selectedRecipeIds.length}件のレシピ
              </p>
            )}

            <div className="button-group">
              <button
                className="btn btn-primary"
                onClick={handleExport}
                disabled={loading || (exportType !== 'backup' && selectedRecipeIds.length === 0)}
              >
                {loading ? 'エクスポート中...' : 'エクスポート実行'}
              </button>
            </div>
          </>
        )}
      </div>

      <div className="export-section">
        <h2>対応フォーマット</h2>
        <ul style={{ paddingLeft: '20px' }}>
          {Object.entries(supportedFormats).map(([key, info]) => (
            <li key={key}>
              <strong>{info.name}</strong> - {info.mime}
            </li>
          ))}
        </ul>
      </div>

      <div className="export-section">
        <h2>使い方</h2>
        <ol style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
          <li>エクスポートタイプを選択します</li>
          <li>必要に応じてフォーマットやオプションを設定します</li>
          <li>レシピ一覧で対象レシピを選択します（バックアップ以外）</li>
          <li>「エクスポート実行」ボタンをクリックします</li>
          <li>ファイルが自動的にダウンロードされます</li>
        </ol>
        <p className="info-text">
          <strong>レシピブック:</strong> 複数レシピを1つのPDFにまとめます（日本語対応）<br/>
          <strong>買い物リスト:</strong> 選択したレシピの材料をまとめたリストを生成します<br/>
          <strong>栄養レポート:</strong> レシピの栄養情報を集計します<br/>
          <strong>バックアップ:</strong> 全レシピデータをJSONファイルに保存します
        </p>
      </div>
    </div>
  );
};

export default ExportManager;

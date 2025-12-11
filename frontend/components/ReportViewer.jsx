/**
 * レポートビューアコンポーネント
 *
 * レポートのプレビュー、PDF/HTML/Markdownダウンロード、期間選択、履歴一覧を提供する。
 */

import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ReportViewer = ({ userId = 'user_001' }) => {
  // State
  const [reportType, setReportType] = useState('weekly');
  const [reportData, setReportData] = useState(null);
  const [reportHistory, setReportHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // カスタムレポート用
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');

  // 週次・月次オフセット
  const [weekOffset, setWeekOffset] = useState(0);
  const [monthOffset, setMonthOffset] = useState(0);

  // HTMLプレビュー
  const [htmlPreview, setHtmlPreview] = useState('');

  /**
   * レポート履歴を取得
   */
  const fetchReportHistory = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/report/history?user_id=${userId}&limit=20`
      );

      if (!response.ok) {
        throw new Error('レポート履歴の取得に失敗しました');
      }

      const result = await response.json();
      setReportHistory(result.data || []);
    } catch (err) {
      console.error('レポート履歴取得エラー:', err);
    }
  };

  /**
   * レポートを生成
   */
  const generateReport = async () => {
    setLoading(true);
    setError(null);
    setReportData(null);
    setHtmlPreview('');

    try {
      let url = '';

      if (reportType === 'weekly') {
        url = `${API_BASE_URL}/api/v1/report/weekly?user_id=${userId}&week_offset=${weekOffset}`;
      } else if (reportType === 'monthly') {
        url = `${API_BASE_URL}/api/v1/report/monthly?user_id=${userId}&month_offset=${monthOffset}`;
      } else if (reportType === 'custom') {
        if (!customStartDate || !customEndDate) {
          throw new Error('カスタムレポートには開始日と終了日が必要です');
        }

        const response = await fetch(`${API_BASE_URL}/api/v1/report/custom`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            start_date: customStartDate,
            end_date: customEndDate,
          }),
        });

        if (!response.ok) {
          throw new Error('レポート生成に失敗しました');
        }

        const result = await response.json();
        setReportData(result.data);
        await fetchReportHistory();
        return;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('レポート生成に失敗しました');
      }

      const result = await response.json();
      setReportData(result.data);
      await fetchReportHistory();
    } catch (err) {
      setError(err.message);
      console.error('レポート生成エラー:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * HTML プレビューを取得
   */
  const loadHtmlPreview = async () => {
    if (!reportData) return;

    try {
      let url = '';

      if (reportType === 'weekly') {
        url = `${API_BASE_URL}/api/v1/report/generate/html?user_id=${userId}&report_type=weekly&week_offset=${weekOffset}`;
      } else if (reportType === 'monthly') {
        url = `${API_BASE_URL}/api/v1/report/generate/html?user_id=${userId}&report_type=monthly&month_offset=${monthOffset}`;
      } else if (reportType === 'custom') {
        url = `${API_BASE_URL}/api/v1/report/generate/html?user_id=${userId}&report_type=custom&start_date=${customStartDate}&end_date=${customEndDate}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('HTMLプレビュー取得に失敗しました');
      }

      const html = await response.text();
      setHtmlPreview(html);
    } catch (err) {
      console.error('HTMLプレビューエラー:', err);
    }
  };

  /**
   * PDF をダウンロード
   */
  const downloadPdf = async () => {
    try {
      let url = '';

      if (reportType === 'weekly') {
        url = `${API_BASE_URL}/api/v1/report/generate/pdf?user_id=${userId}&report_type=weekly&week_offset=${weekOffset}`;
      } else if (reportType === 'monthly') {
        url = `${API_BASE_URL}/api/v1/report/generate/pdf?user_id=${userId}&report_type=monthly&month_offset=${monthOffset}`;
      } else if (reportType === 'custom') {
        url = `${API_BASE_URL}/api/v1/report/generate/pdf?user_id=${userId}&report_type=custom&start_date=${customStartDate}&end_date=${customEndDate}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('PDF生成に失敗しました');
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `report_${reportType}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      setError(err.message);
      console.error('PDFダウンロードエラー:', err);
    }
  };

  /**
   * Markdown をダウンロード
   */
  const downloadMarkdown = async () => {
    try {
      let url = '';

      if (reportType === 'weekly') {
        url = `${API_BASE_URL}/api/v1/report/generate/markdown?user_id=${userId}&report_type=weekly&week_offset=${weekOffset}`;
      } else if (reportType === 'monthly') {
        url = `${API_BASE_URL}/api/v1/report/generate/markdown?user_id=${userId}&report_type=monthly&month_offset=${monthOffset}`;
      } else if (reportType === 'custom') {
        url = `${API_BASE_URL}/api/v1/report/generate/markdown?user_id=${userId}&report_type=custom&start_date=${customStartDate}&end_date=${customEndDate}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Markdown生成に失敗しました');
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `report_${reportType}_${new Date().toISOString().split('T')[0]}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      setError(err.message);
      console.error('Markdownダウンロードエラー:', err);
    }
  };

  // 初回ロード時にレポート履歴を取得
  useEffect(() => {
    fetchReportHistory();
  }, [userId]);

  // レポートデータが更新されたらHTMLプレビューを取得
  useEffect(() => {
    if (reportData) {
      loadHtmlPreview();
    }
  }, [reportData]);

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>レポート生成</h1>

      {/* レポートタイプ選択 */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>レポートタイプ</h2>
        <div style={styles.buttonGroup}>
          <button
            style={{
              ...styles.typeButton,
              ...(reportType === 'weekly' ? styles.typeButtonActive : {}),
            }}
            onClick={() => setReportType('weekly')}
          >
            週次レポート
          </button>
          <button
            style={{
              ...styles.typeButton,
              ...(reportType === 'monthly' ? styles.typeButtonActive : {}),
            }}
            onClick={() => setReportType('monthly')}
          >
            月次レポート
          </button>
          <button
            style={{
              ...styles.typeButton,
              ...(reportType === 'custom' ? styles.typeButtonActive : {}),
            }}
            onClick={() => setReportType('custom')}
          >
            カスタム期間
          </button>
        </div>
      </div>

      {/* 期間選択 */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>期間設定</h2>

        {reportType === 'weekly' && (
          <div style={styles.inputGroup}>
            <label style={styles.label}>週オフセット（0=今週、-1=先週）:</label>
            <input
              type="number"
              value={weekOffset}
              onChange={(e) => setWeekOffset(parseInt(e.target.value) || 0)}
              style={styles.input}
            />
          </div>
        )}

        {reportType === 'monthly' && (
          <div style={styles.inputGroup}>
            <label style={styles.label}>月オフセット（0=今月、-1=先月）:</label>
            <input
              type="number"
              value={monthOffset}
              onChange={(e) => setMonthOffset(parseInt(e.target.value) || 0)}
              style={styles.input}
            />
          </div>
        )}

        {reportType === 'custom' && (
          <div>
            <div style={styles.inputGroup}>
              <label style={styles.label}>開始日:</label>
              <input
                type="date"
                value={customStartDate}
                onChange={(e) => setCustomStartDate(e.target.value)}
                style={styles.input}
              />
            </div>
            <div style={styles.inputGroup}>
              <label style={styles.label}>終了日:</label>
              <input
                type="date"
                value={customEndDate}
                onChange={(e) => setCustomEndDate(e.target.value)}
                style={styles.input}
              />
            </div>
          </div>
        )}
      </div>

      {/* 生成ボタン */}
      <div style={styles.section}>
        <button onClick={generateReport} disabled={loading} style={styles.generateButton}>
          {loading ? 'レポート生成中...' : 'レポート生成'}
        </button>
      </div>

      {/* エラー表示 */}
      {error && (
        <div style={styles.error}>
          <strong>エラー:</strong> {error}
        </div>
      )}

      {/* レポート表示 */}
      {reportData && (
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>レポート内容</h2>

          {/* ダウンロードボタン */}
          <div style={styles.downloadButtons}>
            <button onClick={downloadPdf} style={styles.downloadButton}>
              PDF ダウンロード
            </button>
            <button onClick={downloadMarkdown} style={styles.downloadButton}>
              Markdown ダウンロード
            </button>
          </div>

          {/* レポート情報 */}
          <div style={styles.reportInfo}>
            <p>
              <strong>レポートID:</strong> {reportData.report_id}
            </p>
            <p>
              <strong>期間:</strong> {reportData.start_date} 〜 {reportData.end_date}
            </p>
            <p>
              <strong>生成日時:</strong> {reportData.generated_at}
            </p>
          </div>

          {/* HTMLプレビュー */}
          {htmlPreview && (
            <div style={styles.preview}>
              <h3 style={styles.previewTitle}>プレビュー</h3>
              <iframe
                srcDoc={htmlPreview}
                style={styles.iframe}
                title="レポートプレビュー"
              />
            </div>
          )}
        </div>
      )}

      {/* レポート履歴 */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>レポート履歴</h2>
        {reportHistory.length === 0 ? (
          <p style={styles.noData}>レポート履歴がありません</p>
        ) : (
          <div style={styles.historyList}>
            {reportHistory.map((report) => (
              <div key={report.report_id} style={styles.historyItem}>
                <div style={styles.historyInfo}>
                  <strong>
                    {report.report_type === 'weekly'
                      ? '週次'
                      : report.report_type === 'monthly'
                      ? '月次'
                      : 'カスタム'}
                  </strong>
                  <span style={styles.historyDate}>
                    {report.start_date} 〜 {report.end_date}
                  </span>
                </div>
                <div style={styles.historyMeta}>
                  生成日時: {new Date(report.generated_at).toLocaleString('ja-JP')}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// スタイル定義
const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  title: {
    fontSize: '2em',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#333',
  },
  section: {
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  sectionTitle: {
    fontSize: '1.5em',
    fontWeight: 'bold',
    marginBottom: '15px',
    color: '#667eea',
    borderBottom: '2px solid #667eea',
    paddingBottom: '10px',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap',
  },
  typeButton: {
    padding: '10px 20px',
    fontSize: '1em',
    border: '2px solid #667eea',
    borderRadius: '5px',
    backgroundColor: '#fff',
    color: '#667eea',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  typeButtonActive: {
    backgroundColor: '#667eea',
    color: '#fff',
  },
  inputGroup: {
    marginBottom: '15px',
  },
  label: {
    display: 'block',
    marginBottom: '5px',
    fontWeight: 'bold',
    color: '#555',
  },
  input: {
    width: '100%',
    maxWidth: '300px',
    padding: '10px',
    fontSize: '1em',
    border: '1px solid #ddd',
    borderRadius: '5px',
  },
  generateButton: {
    padding: '12px 30px',
    fontSize: '1.1em',
    fontWeight: 'bold',
    backgroundColor: '#667eea',
    color: '#fff',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  error: {
    padding: '15px',
    backgroundColor: '#ffe6e6',
    color: '#d8000c',
    borderRadius: '5px',
    marginBottom: '20px',
  },
  downloadButtons: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
    flexWrap: 'wrap',
  },
  downloadButton: {
    padding: '10px 20px',
    fontSize: '1em',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  reportInfo: {
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px',
    marginBottom: '20px',
  },
  preview: {
    marginTop: '20px',
  },
  previewTitle: {
    fontSize: '1.2em',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#555',
  },
  iframe: {
    width: '100%',
    height: '600px',
    border: '1px solid #ddd',
    borderRadius: '5px',
  },
  historyList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  historyItem: {
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px',
    borderLeft: '4px solid #667eea',
  },
  historyInfo: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '5px',
  },
  historyDate: {
    color: '#666',
  },
  historyMeta: {
    fontSize: '0.9em',
    color: '#888',
  },
  noData: {
    textAlign: 'center',
    color: '#999',
    padding: '20px',
  },
};

export default ReportViewer;

/**
 * ShareRecipe Component
 * レシピ共有コンポーネント
 */

import React, { useState, useEffect } from 'react';
import './ShareRecipe.css';

const ShareRecipe = ({ recipeId, ownerId, onClose }) => {
  const [shareLink, setShareLink] = useState('');
  const [shareId, setShareId] = useState('');
  const [permission, setPermission] = useState('view_only');
  const [expiresInDays, setExpiresInDays] = useState(7);
  const [sharedWith, setSharedWith] = useState('');
  const [myShares, setMyShares] = useState([]);
  const [sharedWithMe, setSharedWithMe] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('create');

  const API_BASE = '/api/v1/sharing';

  useEffect(() => {
    if (activeTab === 'my-shares') {
      loadMyShares();
    } else if (activeTab === 'shared-with-me') {
      loadSharedWithMe();
    }
  }, [activeTab]);

  const loadMyShares = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/my-shares?owner_id=${ownerId}`);
      if (response.ok) {
        const data = await response.json();
        setMyShares(data.shares);
      }
    } catch (err) {
      setError('共有リストの読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const loadSharedWithMe = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/shared-with-me?user_id=${ownerId}`);
      if (response.ok) {
        const data = await response.json();
        setSharedWithMe(data.shares);
      }
    } catch (err) {
      setError('共有リストの読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const createShareLink = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const sharedWithList = sharedWith
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      const response = await fetch(`${API_BASE}/create-link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipe_id: recipeId,
          owner_id: ownerId,
          permission,
          expires_in_days: expiresInDays,
          shared_with: sharedWithList.length > 0 ? sharedWithList : null,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const fullLink = `${window.location.origin}${data.share_link}`;
        setShareLink(fullLink);
        setShareId(data.share_id);
        setSuccess('共有リンクを作成しました');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || '共有リンクの作成に失敗しました');
      }
    } catch (err) {
      setError('共有リンクの作成に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareLink);
      setSuccess('リンクをコピーしました');
    } catch (err) {
      setError('コピーに失敗しました');
    }
  };

  const shareToSNS = (platform) => {
    const encodedLink = encodeURIComponent(shareLink);
    const text = encodeURIComponent('レシピを共有します');
    let url = '';

    switch (platform) {
      case 'twitter':
        url = `https://twitter.com/intent/tweet?text=${text}&url=${encodedLink}`;
        break;
      case 'facebook':
        url = `https://www.facebook.com/sharer/sharer.php?u=${encodedLink}`;
        break;
      case 'line':
        url = `https://line.me/R/msg/text/?${text}%0A${encodedLink}`;
        break;
      default:
        return;
    }

    window.open(url, '_blank', 'width=600,height=400');
  };

  const revokeShare = async (shareIdToRevoke) => {
    if (!confirm('この共有を解除しますか？')) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/${shareIdToRevoke}?user_id=${ownerId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setSuccess('共有を解除しました');
        loadMyShares();
      } else {
        setError('共有の解除に失敗しました');
      }
    } catch (err) {
      setError('共有の解除に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '無期限';
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP');
  };

  const isExpired = (expiresAt) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  return (
    <div className="share-recipe-modal">
      <div className="share-recipe-content">
        <div className="share-recipe-header">
          <h2>レシピを共有</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="share-recipe-tabs">
          <button
            className={`tab ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => setActiveTab('create')}
          >
            新規共有
          </button>
          <button
            className={`tab ${activeTab === 'my-shares' ? 'active' : ''}`}
            onClick={() => setActiveTab('my-shares')}
          >
            共有中のレシピ
          </button>
          <button
            className={`tab ${activeTab === 'shared-with-me' ? 'active' : ''}`}
            onClick={() => setActiveTab('shared-with-me')}
          >
            共有されたレシピ
          </button>
        </div>

        <div className="share-recipe-body">
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          {activeTab === 'create' && (
            <div className="create-share-tab">
              <div className="form-group">
                <label htmlFor="permission">権限設定</label>
                <select
                  id="permission"
                  value={permission}
                  onChange={(e) => setPermission(e.target.value)}
                  disabled={loading}
                >
                  <option value="view_only">閲覧のみ</option>
                  <option value="edit">編集可能</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="expires">有効期限</label>
                <select
                  id="expires"
                  value={expiresInDays}
                  onChange={(e) => setExpiresInDays(parseInt(e.target.value))}
                  disabled={loading}
                >
                  <option value="1">1日</option>
                  <option value="7">7日</option>
                  <option value="30">30日</option>
                  <option value="90">90日</option>
                  <option value="0">無期限</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="shared-with">
                  共有相手（任意、カンマ区切りでメールアドレスまたはユーザーIDを入力）
                </label>
                <input
                  id="shared-with"
                  type="text"
                  value={sharedWith}
                  onChange={(e) => setSharedWith(e.target.value)}
                  placeholder="user@example.com, user123"
                  disabled={loading}
                />
              </div>

              <button
                className="create-link-button"
                onClick={createShareLink}
                disabled={loading}
              >
                {loading ? '作成中...' : '共有リンクを作成'}
              </button>

              {shareLink && (
                <div className="share-link-section">
                  <h3>共有リンク</h3>
                  <div className="link-display">
                    <input type="text" value={shareLink} readOnly />
                    <button onClick={copyToClipboard}>コピー</button>
                  </div>

                  <div className="sns-share-buttons">
                    <h4>SNSで共有</h4>
                    <button
                      className="sns-button twitter"
                      onClick={() => shareToSNS('twitter')}
                    >
                      Twitter
                    </button>
                    <button
                      className="sns-button facebook"
                      onClick={() => shareToSNS('facebook')}
                    >
                      Facebook
                    </button>
                    <button
                      className="sns-button line"
                      onClick={() => shareToSNS('line')}
                    >
                      LINE
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'my-shares' && (
            <div className="my-shares-tab">
              {loading ? (
                <div className="loading">読み込み中...</div>
              ) : myShares.length === 0 ? (
                <div className="no-data">共有中のレシピはありません</div>
              ) : (
                <div className="shares-list">
                  {myShares.map((share) => (
                    <div
                      key={share.share_id}
                      className={`share-item ${
                        isExpired(share.expires_at) ? 'expired' : ''
                      }`}
                    >
                      <div className="share-info">
                        <div className="share-recipe-id">
                          レシピID: {share.recipe_id}
                        </div>
                        <div className="share-permission">
                          権限: {share.permission === 'view_only' ? '閲覧のみ' : '編集可能'}
                        </div>
                        <div className="share-expires">
                          有効期限: {formatDate(share.expires_at)}
                        </div>
                        <div className="share-access">
                          アクセス数: {share.access_count}
                        </div>
                        {share.shared_with && share.shared_with.length > 0 && (
                          <div className="share-with">
                            共有相手: {share.shared_with.join(', ')}
                          </div>
                        )}
                      </div>
                      <div className="share-actions">
                        <button
                          className="copy-button"
                          onClick={() => {
                            const link = `${window.location.origin}${share.share_link}`;
                            navigator.clipboard.writeText(link);
                            setSuccess('リンクをコピーしました');
                          }}
                        >
                          リンクをコピー
                        </button>
                        <button
                          className="revoke-button"
                          onClick={() => revokeShare(share.share_id)}
                        >
                          解除
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'shared-with-me' && (
            <div className="shared-with-me-tab">
              {loading ? (
                <div className="loading">読み込み中...</div>
              ) : sharedWithMe.length === 0 ? (
                <div className="no-data">共有されたレシピはありません</div>
              ) : (
                <div className="shares-list">
                  {sharedWithMe.map((share) => (
                    <div key={share.share_id} className="share-item">
                      <div className="share-info">
                        <div className="share-recipe-id">
                          レシピID: {share.recipe_id}
                        </div>
                        <div className="share-owner">
                          共有者: {share.owner_id}
                        </div>
                        <div className="share-permission">
                          権限: {share.permission === 'view_only' ? '閲覧のみ' : '編集可能'}
                        </div>
                        <div className="share-expires">
                          有効期限: {formatDate(share.expires_at)}
                        </div>
                      </div>
                      <div className="share-actions">
                        <button
                          className="view-button"
                          onClick={() => {
                            window.location.href = `/recipes/${share.recipe_id}`;
                          }}
                        >
                          レシピを見る
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShareRecipe;

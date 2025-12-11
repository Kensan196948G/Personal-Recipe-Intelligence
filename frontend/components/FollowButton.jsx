/**
 * FollowButton - フォローボタンコンポーネント
 */

import React, { useState, useEffect } from 'react';

const FollowButton = ({ userId, initialStatus = null, onStatusChange = null }) => {
  const [status, setStatus] = useState(initialStatus);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // フォロー状態を取得
  useEffect(() => {
    if (!initialStatus && userId) {
      fetchFollowStatus();
    }
  }, [userId]);

  const fetchFollowStatus = async () => {
    try {
      const response = await fetch(`/api/v1/follow/status/${userId}`);
      const result = await response.json();

      if (result.status === 'ok') {
        setStatus(result.data);
      } else {
        setError(result.error || 'フォロー状態の取得に失敗しました');
      }
    } catch (err) {
      console.error('Follow status fetch error:', err);
      setError('フォロー状態の取得に失敗しました');
    }
  };

  const handleFollow = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/follow/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (result.status === 'ok') {
        // フォロー状態を更新
        await fetchFollowStatus();
        if (onStatusChange) {
          onStatusChange(true);
        }
      } else {
        setError(result.error || 'フォローに失敗しました');
      }
    } catch (err) {
      console.error('Follow error:', err);
      setError('フォローに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleUnfollow = async () => {
    if (!confirm('フォローを解除しますか?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/follow/${userId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (result.status === 'ok') {
        // フォロー状態を更新
        await fetchFollowStatus();
        if (onStatusChange) {
          onStatusChange(false);
        }
      } else {
        setError(result.error || 'フォロー解除に失敗しました');
      }
    } catch (err) {
      console.error('Unfollow error:', err);
      setError('フォロー解除に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  if (!status) {
    return <div className="follow-button-loading">読み込み中...</div>;
  }

  return (
    <div className="follow-button-container">
      {status.is_following ? (
        <button
          className={`follow-button following ${status.is_mutual ? 'mutual' : ''}`}
          onClick={handleUnfollow}
          disabled={loading}
        >
          {loading ? '処理中...' : status.is_mutual ? '相互フォロー中' : 'フォロー中'}
        </button>
      ) : (
        <button
          className="follow-button"
          onClick={handleFollow}
          disabled={loading}
        >
          {loading ? '処理中...' : status.is_follower ? 'フォローバック' : 'フォロー'}
        </button>
      )}

      {status.is_mutual && (
        <span className="mutual-badge" title="相互フォロー">
          ⭐
        </span>
      )}

      <div className="follow-stats">
        <span className="stat-item">
          <strong>{status.follower_count}</strong> フォロワー
        </span>
        <span className="stat-item">
          <strong>{status.following_count}</strong> フォロー中
        </span>
      </div>

      {error && <div className="follow-error">{error}</div>}

      <style jsx>{`
        .follow-button-container {
          display: flex;
          flex-direction: column;
          gap: 8px;
          align-items: flex-start;
        }

        .follow-button {
          padding: 8px 16px;
          border: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          background-color: #1da1f2;
          color: white;
        }

        .follow-button:hover:not(:disabled) {
          background-color: #1a8cd8;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(29, 161, 242, 0.3);
        }

        .follow-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .follow-button.following {
          background-color: #f5f5f5;
          color: #333;
          border: 1px solid #ddd;
        }

        .follow-button.following:hover:not(:disabled) {
          background-color: #fee;
          color: #e00;
          border-color: #e00;
        }

        .follow-button.following:hover:not(:disabled)::after {
          content: 'フォロー解除';
          position: absolute;
        }

        .follow-button.following.mutual {
          background-color: #fff3e0;
          border-color: #ffb74d;
          color: #e65100;
        }

        .follow-button.following.mutual:hover:not(:disabled) {
          background-color: #fee;
          border-color: #e00;
          color: #e00;
        }

        .follow-button-loading {
          padding: 8px 16px;
          color: #999;
          font-size: 14px;
        }

        .mutual-badge {
          display: inline-block;
          margin-left: 6px;
          font-size: 16px;
        }

        .follow-stats {
          display: flex;
          gap: 16px;
          font-size: 14px;
          color: #666;
        }

        .stat-item strong {
          color: #333;
          margin-right: 4px;
        }

        .follow-error {
          padding: 8px;
          background-color: #fee;
          color: #c00;
          border-radius: 4px;
          font-size: 13px;
        }
      `}</style>
    </div>
  );
};

export default FollowButton;

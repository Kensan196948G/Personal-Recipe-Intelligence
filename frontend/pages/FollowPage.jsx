/**
 * FollowPage - フォロー管理ページ
 */

import React, { useState } from 'react';
import UserList from '../components/UserList';

const FollowPage = () => {
  const [activeTab, setActiveTab] = useState('feed');

  return (
    <div className="follow-page">
      <div className="page-header">
        <h1>フォロー</h1>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'feed' ? 'active' : ''}`}
          onClick={() => setActiveTab('feed')}
        >
          フィード
        </button>
        <button
          className={`tab ${activeTab === 'followers' ? 'active' : ''}`}
          onClick={() => setActiveTab('followers')}
        >
          フォロワー
        </button>
        <button
          className={`tab ${activeTab === 'following' ? 'active' : ''}`}
          onClick={() => setActiveTab('following')}
        >
          フォロー中
        </button>
        <button
          className={`tab ${activeTab === 'suggestions' ? 'active' : ''}`}
          onClick={() => setActiveTab('suggestions')}
        >
          おすすめ
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'feed' && <FollowFeed />}
        {activeTab === 'followers' && <UserList type="followers" />}
        {activeTab === 'following' && <UserList type="following" />}
        {activeTab === 'suggestions' && <UserList type="suggestions" />}
      </div>

      <style jsx>{`
        .follow-page {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }

        .page-header {
          margin-bottom: 24px;
        }

        .page-header h1 {
          font-size: 32px;
          font-weight: 700;
          color: #333;
        }

        .tabs {
          display: flex;
          gap: 8px;
          border-bottom: 2px solid #e1e8ed;
          margin-bottom: 24px;
        }

        .tab {
          padding: 12px 24px;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          font-size: 15px;
          font-weight: 600;
          color: #666;
          cursor: pointer;
          transition: all 0.2s;
          margin-bottom: -2px;
        }

        .tab:hover {
          color: #1da1f2;
        }

        .tab.active {
          color: #1da1f2;
          border-bottom-color: #1da1f2;
        }

        .tab-content {
          min-height: 400px;
        }
      `}</style>
    </div>
  );
};

const FollowFeed = () => {
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/follow/feed?limit=20');
      const result = await response.json();

      if (result.status === 'ok') {
        setFeed(result.data || []);
      } else {
        setError(result.error || 'フィードの取得に失敗しました');
      }
    } catch (err) {
      console.error('Feed fetch error:', err);
      setError('フィードの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="feed-loading">
        <div className="spinner"></div>
        <p>読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="feed-error">
        <p>{error}</p>
        <button onClick={fetchFeed}>再試行</button>
      </div>
    );
  }

  if (feed.length === 0) {
    return (
      <div className="feed-empty">
        <p>フォロー中のユーザーの新着レシピがありません</p>
        <p>おすすめユーザーをフォローしてみましょう！</p>
      </div>
    );
  }

  return (
    <div className="follow-feed">
      <h2>フォロー中の新着レシピ</h2>
      <div className="recipe-list">
        {feed.map((recipe) => (
          <div key={recipe.id} className="recipe-card">
            <div className="recipe-header">
              {recipe.user && (
                <div className="user-info">
                  <div className="avatar">
                    {recipe.user.avatar_url ? (
                      <img src={recipe.user.avatar_url} alt={recipe.user.display_name} />
                    ) : (
                      <div className="avatar-placeholder">
                        {(recipe.user.display_name || recipe.user.username || '?')[0].toUpperCase()}
                      </div>
                    )}
                  </div>
                  <div>
                    <div className="display-name">{recipe.user.display_name}</div>
                    <div className="username">@{recipe.user.username}</div>
                  </div>
                </div>
              )}
              <div className="recipe-date">
                {new Date(recipe.created_at).toLocaleDateString('ja-JP')}
              </div>
            </div>

            <h3 className="recipe-title">{recipe.title}</h3>
            {recipe.description && (
              <p className="recipe-description">{recipe.description}</p>
            )}

            {recipe.tags && recipe.tags.length > 0 && (
              <div className="recipe-tags">
                {recipe.tags.map((tag, index) => (
                  <span key={index} className="tag">
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <style jsx>{`
        .follow-feed h2 {
          font-size: 20px;
          font-weight: 700;
          margin-bottom: 20px;
          color: #333;
        }

        .feed-loading,
        .feed-error,
        .feed-empty {
          text-align: center;
          padding: 60px 20px;
          color: #666;
        }

        .spinner {
          width: 40px;
          height: 40px;
          margin: 0 auto 16px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #1da1f2;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }

        .feed-error button {
          margin-top: 16px;
          padding: 8px 24px;
          background-color: #1da1f2;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }

        .recipe-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .recipe-card {
          padding: 20px;
          background: white;
          border: 1px solid #e1e8ed;
          border-radius: 12px;
          transition: all 0.2s ease;
        }

        .recipe-card:hover {
          border-color: #1da1f2;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .recipe-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .user-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .avatar img,
        .avatar-placeholder {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          object-fit: cover;
        }

        .avatar-placeholder {
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          font-size: 18px;
          font-weight: 700;
        }

        .display-name {
          font-size: 15px;
          font-weight: 700;
          color: #333;
        }

        .username {
          font-size: 13px;
          color: #666;
        }

        .recipe-date {
          font-size: 13px;
          color: #999;
        }

        .recipe-title {
          font-size: 18px;
          font-weight: 700;
          color: #333;
          margin-bottom: 8px;
        }

        .recipe-description {
          font-size: 14px;
          color: #666;
          line-height: 1.5;
          margin-bottom: 12px;
        }

        .recipe-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .tag {
          padding: 4px 12px;
          background-color: #f0f8ff;
          color: #1da1f2;
          font-size: 13px;
          border-radius: 12px;
        }
      `}</style>
    </div>
  );
};

export default FollowPage;

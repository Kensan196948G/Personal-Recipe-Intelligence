/**
 * UserList - ユーザーリストコンポーネント
 * フォロワー/フォロー中/おすすめユーザー一覧表示
 */

import React, { useState, useEffect } from 'react';
import FollowButton from './FollowButton';

const UserList = ({ type = 'followers', userId = null, limit = 20 }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [metadata, setMetadata] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, [type, userId, limit]);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);

    try {
      let endpoint = '';
      switch (type) {
        case 'followers':
          endpoint = `/api/v1/follow/followers${userId ? `?user_id=${userId}` : ''}`;
          break;
        case 'following':
          endpoint = `/api/v1/follow/following${userId ? `?user_id=${userId}` : ''}`;
          break;
        case 'suggestions':
          endpoint = `/api/v1/follow/suggestions?limit=${limit}`;
          break;
        default:
          throw new Error('Invalid type');
      }

      const response = await fetch(endpoint);
      const result = await response.json();

      if (result.status === 'ok') {
        if (type === 'suggestions') {
          setUsers(result.data || []);
        } else {
          setUsers(result.data[type] || []);
          setMetadata({
            total: result.data.total,
            limit: result.data.limit,
            offset: result.data.offset,
          });
        }
      } else {
        setError(result.error || 'ユーザーの取得に失敗しました');
      }
    } catch (err) {
      console.error('User list fetch error:', err);
      setError('ユーザーの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter((user) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      user.username?.toLowerCase().includes(query) ||
      user.display_name?.toLowerCase().includes(query) ||
      user.bio?.toLowerCase().includes(query)
    );
  });

  const getTitle = () => {
    switch (type) {
      case 'followers':
        return 'フォロワー';
      case 'following':
        return 'フォロー中';
      case 'suggestions':
        return 'おすすめユーザー';
      default:
        return 'ユーザー';
    }
  };

  const handleFollowStatusChange = () => {
    // フォロー状態が変わったらリストを再取得
    fetchUsers();
  };

  if (loading) {
    return (
      <div className="user-list-loading">
        <div className="spinner"></div>
        <p>読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-list-error">
        <p>{error}</p>
        <button onClick={fetchUsers}>再試行</button>
      </div>
    );
  }

  return (
    <div className="user-list-container">
      <div className="user-list-header">
        <h2>
          {getTitle()}
          {metadata && <span className="count">({metadata.total})</span>}
        </h2>
        <div className="search-box">
          <input
            type="text"
            placeholder="ユーザーを検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {filteredUsers.length === 0 ? (
        <div className="empty-state">
          <p>{searchQuery ? '検索結果がありません' : 'ユーザーがいません'}</p>
        </div>
      ) : (
        <div className="user-list">
          {filteredUsers.map((user) => (
            <div key={user.id} className="user-card">
              <div className="user-avatar">
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt={user.display_name} />
                ) : (
                  <div className="avatar-placeholder">
                    {(user.display_name || user.username || '?')[0].toUpperCase()}
                  </div>
                )}
              </div>

              <div className="user-info">
                <div className="user-name-row">
                  <h3>{user.display_name || user.username}</h3>
                  {user.is_mutual && (
                    <span className="mutual-badge" title="相互フォロー">
                      ⭐
                    </span>
                  )}
                </div>
                <p className="username">@{user.username}</p>
                {user.bio && <p className="bio">{user.bio}</p>}

                <div className="user-stats">
                  {user.recipe_count !== undefined && (
                    <span className="stat">
                      レシピ: <strong>{user.recipe_count}</strong>
                    </span>
                  )}
                  {user.common_friends !== undefined && (
                    <span className="stat">
                      共通の友達: <strong>{user.common_friends}</strong>
                    </span>
                  )}
                </div>
              </div>

              <div className="user-actions">
                <FollowButton
                  userId={user.id}
                  onStatusChange={handleFollowStatusChange}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {metadata && metadata.total > filteredUsers.length && (
        <div className="load-more">
          <button onClick={fetchUsers}>さらに読み込む</button>
        </div>
      )}

      <style jsx>{`
        .user-list-container {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }

        .user-list-header {
          margin-bottom: 24px;
        }

        .user-list-header h2 {
          font-size: 24px;
          font-weight: 700;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .count {
          font-size: 18px;
          color: #666;
          font-weight: 400;
        }

        .search-box input {
          width: 100%;
          padding: 10px 16px;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 14px;
          transition: border-color 0.2s;
        }

        .search-box input:focus {
          outline: none;
          border-color: #1da1f2;
          box-shadow: 0 0 0 3px rgba(29, 161, 242, 0.1);
        }

        .user-list-loading,
        .user-list-error {
          text-align: center;
          padding: 60px 20px;
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

        .user-list-error button {
          margin-top: 16px;
          padding: 8px 24px;
          background-color: #1da1f2;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: #666;
        }

        .user-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .user-card {
          display: flex;
          gap: 16px;
          padding: 16px;
          background: white;
          border: 1px solid #e1e8ed;
          border-radius: 12px;
          transition: all 0.2s ease;
        }

        .user-card:hover {
          border-color: #1da1f2;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .user-avatar {
          flex-shrink: 0;
        }

        .user-avatar img,
        .avatar-placeholder {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          object-fit: cover;
        }

        .avatar-placeholder {
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          font-size: 24px;
          font-weight: 700;
        }

        .user-info {
          flex: 1;
          min-width: 0;
        }

        .user-name-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .user-info h3 {
          font-size: 16px;
          font-weight: 700;
          margin: 0 0 4px 0;
          color: #333;
        }

        .username {
          font-size: 14px;
          color: #666;
          margin: 0 0 8px 0;
        }

        .bio {
          font-size: 14px;
          color: #333;
          margin: 0 0 8px 0;
          line-height: 1.5;
        }

        .user-stats {
          display: flex;
          gap: 16px;
          font-size: 13px;
          color: #666;
        }

        .stat strong {
          color: #333;
        }

        .mutual-badge {
          font-size: 16px;
        }

        .user-actions {
          flex-shrink: 0;
          display: flex;
          align-items: center;
        }

        .load-more {
          margin-top: 24px;
          text-align: center;
        }

        .load-more button {
          padding: 10px 32px;
          background-color: #f5f5f5;
          color: #333;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .load-more button:hover {
          background-color: #e8e8e8;
          border-color: #ccc;
        }

        @media (max-width: 640px) {
          .user-card {
            flex-direction: column;
          }

          .user-actions {
            align-self: flex-start;
          }
        }
      `}</style>
    </div>
  );
};

export default UserList;

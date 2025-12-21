/**
 * CollectionManager component for Personal Recipe Intelligence.
 */

import React, { useState, useEffect } from 'react';
import CollectionCard from './CollectionCard.jsx';

/**
 * Collection manager component.
 *
 * @param {Object} props - Component props
 * @param {string} props.apiBaseUrl - API base URL
 * @param {string} props.authToken - Authentication token
 */
const CollectionManager = ({ apiBaseUrl, authToken }) => {
  const [collections, setCollections] = useState([]);
  const [publicCollections, setPublicCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [activeTab, setActiveTab] = useState('mine'); // 'mine' or 'public'
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingCollection, setEditingCollection] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    visibility: 'private',
    tags: ''
  });

  /**
   * Fetch user's collections.
   */
  const fetchCollections = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/collection`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch collections: ${response.status}`);
      }

      const result = await response.json();
      setCollections(result.data || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching collections:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch public collections.
   */
  const fetchPublicCollections = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/collection/public?limit=50&offset=0`);

      if (!response.ok) {
        throw new Error(`Failed to fetch public collections: ${response.status}`);
      }

      const result = await response.json();
      setPublicCollections(result.data || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching public collections:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create or update collection.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        name: formData.name,
        description: formData.description || null,
        visibility: formData.visibility,
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(Boolean) : []
      };

      const url = editingCollection
        ? `${apiBaseUrl}/api/v1/collection/${editingCollection.id}`
        : `${apiBaseUrl}/api/v1/collection`;

      const method = editingCollection ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || 'Failed to save collection');
      }

      // Reset form and refresh
      setFormData({ name: '', description: '', visibility: 'private', tags: '' });
      setShowCreateForm(false);
      setEditingCollection(null);
      await fetchCollections();
    } catch (err) {
      setError(err.message);
      console.error('Error saving collection:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Delete collection.
   */
  const handleDelete = async (collectionId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/collection/${collectionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete collection');
      }

      await fetchCollections();
    } catch (err) {
      setError(err.message);
      console.error('Error deleting collection:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Copy collection.
   */
  const handleCopy = async (collectionId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/collection/${collectionId}/copy`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });

      if (!response.ok) {
        throw new Error('Failed to copy collection');
      }

      await fetchCollections();
      setActiveTab('mine');
    } catch (err) {
      setError(err.message);
      console.error('Error copying collection:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Open edit form.
   */
  const handleEdit = (collection) => {
    setEditingCollection(collection);
    setFormData({
      name: collection.name,
      description: collection.description || '',
      visibility: collection.visibility,
      tags: collection.tags.join(', ')
    });
    setShowCreateForm(true);
  };

  /**
   * Cancel form.
   */
  const handleCancel = () => {
    setFormData({ name: '', description: '', visibility: 'private', tags: '' });
    setShowCreateForm(false);
    setEditingCollection(null);
  };

  /**
   * Handle collection click.
   */
  const handleCollectionClick = (collection) => {
    console.log('Collection clicked:', collection);
    // TODO: Navigate to collection detail view
  };

  // Initial load
  useEffect(() => {
    if (activeTab === 'mine') {
      fetchCollections();
    } else {
      fetchPublicCollections();
    }
  }, [activeTab]);

  const displayCollections = activeTab === 'mine' ? collections : publicCollections;

  return (
    <div className="collection-manager">
      <div className="collection-manager-header">
        <h2>コレクション管理</h2>

        <div className="collection-manager-controls">
          {/* Tab switcher */}
          <div className="collection-manager-tabs">
            <button
              className={`tab-btn ${activeTab === 'mine' ? 'active' : ''}`}
              onClick={() => setActiveTab('mine')}
            >
              マイコレクション
            </button>
            <button
              className={`tab-btn ${activeTab === 'public' ? 'active' : ''}`}
              onClick={() => setActiveTab('public')}
            >
              公開コレクション
            </button>
          </div>

          {/* View mode toggle */}
          <div className="view-mode-toggle">
            <button
              className={`view-mode-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
              title="グリッド表示"
              aria-label="グリッド表示"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <rect x="3" y="3" width="7" height="7" />
                <rect x="14" y="3" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" />
                <rect x="14" y="14" width="7" height="7" />
              </svg>
            </button>
            <button
              className={`view-mode-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
              title="リスト表示"
              aria-label="リスト表示"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="8" y1="6" x2="21" y2="6" strokeWidth="2" />
                <line x1="8" y1="12" x2="21" y2="12" strokeWidth="2" />
                <line x1="8" y1="18" x2="21" y2="18" strokeWidth="2" />
                <line x1="3" y1="6" x2="3.01" y2="6" strokeWidth="2" />
                <line x1="3" y1="12" x2="3.01" y2="12" strokeWidth="2" />
                <line x1="3" y1="18" x2="3.01" y2="18" strokeWidth="2" />
              </svg>
            </button>
          </div>

          {/* Create button */}
          {activeTab === 'mine' && (
            <button
              className="create-collection-btn"
              onClick={() => setShowCreateForm(!showCreateForm)}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="5" x2="12" y2="19" strokeWidth="2" />
                <line x1="5" y1="12" x2="19" y2="12" strokeWidth="2" />
              </svg>
              新規作成
            </button>
          )}
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="collection-manager-error">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
          {error}
        </div>
      )}

      {/* Create/Edit form */}
      {showCreateForm && (
        <form className="collection-form" onSubmit={handleSubmit}>
          <h3>{editingCollection ? 'コレクション編集' : '新規コレクション'}</h3>

          <div className="form-group">
            <label htmlFor="name">名前 *</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="例: お気に入りの和食"
              required
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">説明</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="コレクションの説明"
              maxLength={500}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label htmlFor="visibility">公開設定</label>
            <select
              id="visibility"
              value={formData.visibility}
              onChange={(e) => setFormData({ ...formData, visibility: e.target.value })}
            >
              <option value="private">非公開</option>
              <option value="public">公開</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="tags">タグ（カンマ区切り）</label>
            <input
              id="tags"
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="例: 和食, 簡単, ヘルシー"
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? '保存中...' : editingCollection ? '更新' : '作成'}
            </button>
            <button type="button" className="cancel-btn" onClick={handleCancel}>
              キャンセル
            </button>
          </div>
        </form>
      )}

      {/* Collections grid/list */}
      {loading && !showCreateForm ? (
        <div className="collection-manager-loading">読み込み中...</div>
      ) : displayCollections.length === 0 ? (
        <div className="collection-manager-empty">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="3" y="3" width="18" height="18" rx="2" strokeWidth="2" />
            <line x1="9" y1="9" x2="15" y2="9" strokeWidth="2" />
            <line x1="9" y1="13" x2="15" y2="13" strokeWidth="2" />
          </svg>
          <p>
            {activeTab === 'mine'
              ? 'コレクションがありません。新規作成してください。'
              : '公開されているコレクションがありません。'}
          </p>
        </div>
      ) : (
        <div className={`collections-${viewMode}`}>
          {displayCollections.map((collection) => (
            <CollectionCard
              key={collection.id}
              collection={collection}
              onClick={handleCollectionClick}
              onDelete={activeTab === 'mine' ? handleDelete : undefined}
              onEdit={activeTab === 'mine' ? handleEdit : undefined}
              showActions={activeTab === 'mine'}
            />
          ))}
        </div>
      )}

      {/* Copy button for public collections */}
      {activeTab === 'public' && displayCollections.length > 0 && (
        <div className="collection-manager-hint">
          公開コレクションをクリックすると詳細が見られます。
          コピーして自分のコレクションとして使用できます。
        </div>
      )}
    </div>
  );
};

export default CollectionManager;

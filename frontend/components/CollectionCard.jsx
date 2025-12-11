/**
 * CollectionCard component for Personal Recipe Intelligence.
 */

import React from 'react';

/**
 * Collection card component.
 *
 * @param {Object} props - Component props
 * @param {Object} props.collection - Collection data
 * @param {Function} props.onClick - Click handler
 * @param {Function} props.onDelete - Delete handler
 * @param {Function} props.onEdit - Edit handler
 * @param {boolean} props.showActions - Show action buttons
 */
const CollectionCard = ({
  collection,
  onClick,
  onDelete,
  onEdit,
  showActions = true
}) => {
  const {
    id,
    name,
    description,
    recipe_count,
    visibility,
    is_default,
    thumbnail_url,
    tags = []
  } = collection;

  const handleCardClick = (e) => {
    // Don't trigger onClick if clicking action buttons
    if (e.target.closest('.collection-card-actions')) {
      return;
    }
    onClick?.(collection);
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (window.confirm(`「${name}」を削除しますか?`)) {
      onDelete?.(id);
    }
  };

  const handleEdit = (e) => {
    e.stopPropagation();
    onEdit?.(collection);
  };

  return (
    <div
      className="collection-card"
      onClick={handleCardClick}
      role="button"
      tabIndex={0}
      onKeyPress={(e) => e.key === 'Enter' && handleCardClick(e)}
    >
      {/* Thumbnail */}
      <div className="collection-card-thumbnail">
        {thumbnail_url ? (
          <img src={thumbnail_url} alt={name} loading="lazy" />
        ) : (
          <div className="collection-card-thumbnail-placeholder">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" strokeWidth="2" />
              <line x1="9" y1="9" x2="15" y2="9" strokeWidth="2" />
              <line x1="9" y1="13" x2="15" y2="13" strokeWidth="2" />
              <line x1="9" y1="17" x2="13" y2="17" strokeWidth="2" />
            </svg>
          </div>
        )}

        {/* Visibility badge */}
        {visibility === 'public' && (
          <div className="collection-card-badge collection-card-badge-public">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
            公開
          </div>
        )}

        {/* Default badge */}
        {is_default && (
          <div className="collection-card-badge collection-card-badge-default">
            デフォルト
          </div>
        )}
      </div>

      {/* Content */}
      <div className="collection-card-content">
        <h3 className="collection-card-title">{name}</h3>

        {description && (
          <p className="collection-card-description">{description}</p>
        )}

        <div className="collection-card-meta">
          <span className="collection-card-recipe-count">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="7" height="7" strokeWidth="2" />
              <rect x="14" y="3" width="7" height="7" strokeWidth="2" />
              <rect x="3" y="14" width="7" height="7" strokeWidth="2" />
              <rect x="14" y="14" width="7" height="7" strokeWidth="2" />
            </svg>
            {recipe_count || 0} レシピ
          </span>
        </div>

        {/* Tags */}
        {tags.length > 0 && (
          <div className="collection-card-tags">
            {tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="collection-card-tag">
                {tag}
              </span>
            ))}
            {tags.length > 3 && (
              <span className="collection-card-tag-more">
                +{tags.length - 3}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      {showActions && !is_default && (
        <div className="collection-card-actions">
          <button
            className="collection-card-action-btn collection-card-edit-btn"
            onClick={handleEdit}
            title="編集"
            aria-label="編集"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" strokeWidth="2" strokeLinecap="round" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <button
            className="collection-card-action-btn collection-card-delete-btn"
            onClick={handleDelete}
            title="削除"
            aria-label="削除"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

export default CollectionCard;

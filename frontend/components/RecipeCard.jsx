/**
 * RecipeCard.jsx
 * Personal Recipe Intelligence
 * レシピカードのレスポンシブ表示コンポーネント
 * - グリッド/リスト切り替え
 * - スワイプジェスチャー
 * - タッチ最適化
 */

import React, { useState, useRef, useEffect } from 'react';

/**
 * レシピカードコンポーネント
 * @param {Object} props - コンポーネントプロパティ
 * @param {Object} props.recipe - レシピデータ
 * @param {string} props.viewMode - 表示モード ('grid' | 'list')
 * @param {Function} props.onView - 閲覧ハンドラー
 * @param {Function} props.onEdit - 編集ハンドラー
 * @param {Function} props.onDelete - 削除ハンドラー
 */
const RecipeCard = ({
  recipe,
  viewMode = 'grid',
  onView,
  onEdit,
  onDelete,
}) => {
  const [isSwipeMenuOpen, setIsSwipeMenuOpen] = useState(false);
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);
  const cardRef = useRef(null);

  // スワイプの最小距離（px）
  const minSwipeDistance = 50;

  // タッチ開始
  const handleTouchStart = (e) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  // タッチ移動
  const handleTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  // タッチ終了
  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return;

    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe) {
      setIsSwipeMenuOpen(true);
    } else if (isRightSwipe) {
      setIsSwipeMenuOpen(false);
    }
  };

  // 外部クリックでメニューを閉じる
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (cardRef.current && !cardRef.current.contains(e.target)) {
        setIsSwipeMenuOpen(false);
      }
    };

    if (isSwipeMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('touchstart', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, [isSwipeMenuOpen]);

  // アクションハンドラー
  const handleAction = (action) => {
    setIsSwipeMenuOpen(false);
    if (action === 'view' && onView) {
      onView(recipe);
    } else if (action === 'edit' && onEdit) {
      onEdit(recipe);
    } else if (action === 'delete' && onDelete) {
      onDelete(recipe);
    }
  };

  // デフォルト画像URL
  const defaultImage = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="sans-serif" font-size="20"%3ENo Image%3C/text%3E%3C/svg%3E';

  return (
    <article
      ref={cardRef}
      className={`recipe-card ${viewMode} ${isSwipeMenuOpen ? 'menu-open' : ''}`}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <div className="card-content">
        {/* 画像セクション */}
        <div className="card-image-wrapper">
          <img
            src={recipe.image || defaultImage}
            alt={recipe.title || 'レシピ画像'}
            className="card-image"
            loading="lazy"
          />
          {recipe.tags && recipe.tags.length > 0 && (
            <div className="card-tags">
              {recipe.tags.slice(0, 3).map((tag, index) => (
                <span key={index} className="card-tag">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* コンテンツセクション */}
        <div className="card-body">
          <h3 className="card-title">{recipe.title || '無題のレシピ'}</h3>

          {recipe.description && (
            <p className="card-description">{recipe.description}</p>
          )}

          <div className="card-meta">
            {recipe.cookTime && (
              <div className="meta-item">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M8 4V8L11 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
                <span>{recipe.cookTime}分</span>
              </div>
            )}

            {recipe.servings && (
              <div className="meta-item">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M8 8C9.65685 8 11 6.65685 11 5C11 3.34315 9.65685 2 8 2C6.34315 2 5 3.34315 5 5C5 6.65685 6.34315 8 8 8Z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                  <path
                    d="M3 14C3 11.2386 5.23858 9 8 9C10.7614 9 13 11.2386 13 14"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                </svg>
                <span>{recipe.servings}人分</span>
              </div>
            )}

            {recipe.difficulty && (
              <div className="meta-item">
                <span className={`difficulty difficulty-${recipe.difficulty}`}>
                  {recipe.difficulty === 'easy' && '簡単'}
                  {recipe.difficulty === 'medium' && '普通'}
                  {recipe.difficulty === 'hard' && '難しい'}
                </span>
              </div>
            )}
          </div>

          {/* アクションボタン（デスクトップ） */}
          <div className="card-actions desktop-actions">
            <button
              onClick={() => handleAction('view')}
              className="btn btn-primary btn-sm"
              aria-label="レシピを見る"
            >
              見る
            </button>
            <button
              onClick={() => handleAction('edit')}
              className="btn btn-outline btn-sm"
              aria-label="レシピを編集"
            >
              編集
            </button>
            <button
              onClick={() => handleAction('delete')}
              className="btn btn-outline btn-sm btn-danger"
              aria-label="レシピを削除"
            >
              削除
            </button>
          </div>
        </div>
      </div>

      {/* スワイプメニュー（モバイル） */}
      <div className="swipe-menu">
        <button
          onClick={() => handleAction('edit')}
          className="swipe-action swipe-edit"
          aria-label="編集"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M18.5 2.5C18.8978 2.10217 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10217 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10217 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span>編集</span>
        </button>
        <button
          onClick={() => handleAction('delete')}
          className="swipe-action swipe-delete"
          aria-label="削除"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M3 6H5H21"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span>削除</span>
        </button>
      </div>

      <style jsx>{`
        /* ========================================
           Recipe Card Base
           ======================================== */
        .recipe-card {
          position: relative;
          display: flex;
          background-color: var(--color-background, #ffffff);
          border-radius: 0.75rem;
          overflow: hidden;
          box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1));
          transition: all var(--transition-base, 0.25s ease-in-out);
        }

        .recipe-card:hover {
          box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1));
          transform: translateY(-2px);
        }

        .card-content {
          flex: 1;
          display: flex;
          transition: transform var(--transition-base, 0.25s ease-in-out);
        }

        .recipe-card.menu-open .card-content {
          transform: translateX(-160px);
        }

        /* ========================================
           Grid View
           ======================================== */
        .recipe-card.grid {
          flex-direction: column;
        }

        .recipe-card.grid .card-content {
          flex-direction: column;
        }

        .recipe-card.grid .card-image-wrapper {
          position: relative;
          width: 100%;
          padding-top: 75%;
          overflow: hidden;
        }

        .recipe-card.grid .card-image {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        /* ========================================
           List View
           ======================================== */
        .recipe-card.list {
          flex-direction: row;
        }

        .recipe-card.list .card-content {
          flex-direction: row;
        }

        .recipe-card.list .card-image-wrapper {
          position: relative;
          width: 120px;
          flex-shrink: 0;
          overflow: hidden;
        }

        .recipe-card.list .card-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .recipe-card.list .card-body {
          flex: 1;
        }

        /* ========================================
           Card Components
           ======================================== */
        .card-tags {
          position: absolute;
          top: 0.5rem;
          left: 0.5rem;
          display: flex;
          flex-wrap: wrap;
          gap: 0.25rem;
        }

        .card-tag {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          background-color: rgba(255, 255, 255, 0.95);
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 500;
          color: var(--color-text, #1f2937);
          box-shadow: var(--shadow-sm, 0 1px 2px 0 rgba(0, 0, 0, 0.05));
        }

        .card-body {
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .card-title {
          margin: 0;
          font-size: 1.125rem;
          font-weight: 600;
          line-height: 1.4;
          color: var(--color-text, #1f2937);
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .card-description {
          margin: 0;
          font-size: 0.875rem;
          line-height: 1.5;
          color: var(--color-text-secondary, #6b7280);
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .card-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          margin-top: auto;
        }

        .meta-item {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.875rem;
          color: var(--color-text-secondary, #6b7280);
        }

        .difficulty {
          padding: 0.125rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .difficulty-easy {
          background-color: #d1fae5;
          color: #065f46;
        }

        .difficulty-medium {
          background-color: #fef3c7;
          color: #92400e;
        }

        .difficulty-hard {
          background-color: #fee2e2;
          color: #991b1b;
        }

        /* ========================================
           Actions
           ======================================== */
        .card-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }

        .desktop-actions {
          display: none;
        }

        .btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 0.5rem 1rem;
          font-size: 0.875rem;
          font-weight: 500;
          border-radius: 0.375rem;
          border: none;
          cursor: pointer;
          transition: all var(--transition-fast, 0.15s ease-in-out);
        }

        .btn-sm {
          padding: 0.375rem 0.75rem;
          font-size: 0.8125rem;
        }

        .btn-primary {
          background-color: var(--color-primary, #4f46e5);
          color: white;
        }

        .btn-primary:hover {
          background-color: #4338ca;
        }

        .btn-outline {
          background-color: transparent;
          border: 1.5px solid var(--color-border, #e5e7eb);
          color: var(--color-text, #1f2937);
        }

        .btn-outline:hover {
          background-color: var(--color-surface, #f9fafb);
        }

        .btn-danger {
          color: var(--color-error, #ef4444);
          border-color: var(--color-error, #ef4444);
        }

        .btn-danger:hover {
          background-color: #fee2e2;
        }

        /* ========================================
           Swipe Menu
           ======================================== */
        .swipe-menu {
          position: absolute;
          top: 0;
          right: 0;
          bottom: 0;
          width: 160px;
          display: flex;
          transform: translateX(100%);
        }

        .swipe-action {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 0.25rem;
          border: none;
          color: white;
          font-size: 0.75rem;
          font-weight: 500;
          cursor: pointer;
          transition: opacity var(--transition-fast, 0.15s ease-in-out);
        }

        .swipe-action:active {
          opacity: 0.8;
        }

        .swipe-edit {
          background-color: var(--color-secondary, #06b6d4);
        }

        .swipe-delete {
          background-color: var(--color-error, #ef4444);
        }

        /* ========================================
           Responsive Styles
           ======================================== */
        @media (min-width: 768px) {
          .desktop-actions {
            display: flex;
          }

          .swipe-menu {
            display: none;
          }

          .recipe-card.list .card-image-wrapper {
            width: 200px;
          }

          .card-title {
            font-size: 1.25rem;
          }
        }

        @media (min-width: 1024px) {
          .recipe-card.list .card-image-wrapper {
            width: 240px;
          }
        }
      `}</style>
    </article>
  );
};

export default RecipeCard;

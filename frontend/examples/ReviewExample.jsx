/**
 * Example usage of RecipeReviews component
 * レビューコンポーネントの使用例
 */

import React, { useState } from 'react';
import RecipeReviews from '../components/RecipeReviews';

/**
 * レシピ詳細ページの例
 */
const RecipeDetailPage = () => {
  const [recipeId] = useState('recipe_001');

  return (
    <div className="recipe-detail-page">
      <div className="recipe-header">
        <h1>美味しいカレーライス</h1>
        <p className="recipe-description">
          スパイスの効いた本格的なカレーライスのレシピです。
        </p>
      </div>

      <div className="recipe-content">
        <section className="recipe-ingredients">
          <h2>材料（4人分）</h2>
          <ul>
            <li>鶏もも肉 400g</li>
            <li>玉ねぎ 2個</li>
            <li>じゃがいも 3個</li>
            <li>にんじん 1本</li>
            <li>カレールー 1箱</li>
          </ul>
        </section>

        <section className="recipe-steps">
          <h2>作り方</h2>
          <ol>
            <li>野菜を一口大に切る</li>
            <li>鍋で鶏肉を炒める</li>
            <li>野菜を加えて炒める</li>
            <li>水を加えて煮込む</li>
            <li>カレールーを加えて完成</li>
          </ol>
        </section>
      </div>

      {/* レビューセクション */}
      <section className="recipe-reviews-section">
        <RecipeReviews recipeId={recipeId} />
      </section>
    </div>
  );
};

/**
 * レシピカードでの評価表示例
 */
const RecipeCard = ({ recipe }) => {
  return (
    <div className="recipe-card">
      <img src={recipe.image} alt={recipe.title} />
      <h3>{recipe.title}</h3>
      <div className="recipe-rating">
        <span className="star">★</span>
        <span className="rating-value">{recipe.averageRating.toFixed(1)}</span>
        <span className="review-count">({recipe.reviewCount})</span>
      </div>
      <button onClick={() => window.location.href = `/recipe/${recipe.id}`}>
        レシピを見る
      </button>
    </div>
  );
};

/**
 * レシピリストでの評価表示例
 */
const RecipeList = () => {
  const [recipes] = useState([
    {
      id: 'recipe_001',
      title: '美味しいカレーライス',
      image: '/images/curry.jpg',
      averageRating: 4.5,
      reviewCount: 20
    },
    {
      id: 'recipe_002',
      title: 'チョコレートケーキ',
      image: '/images/cake.jpg',
      averageRating: 4.8,
      reviewCount: 35
    },
    {
      id: 'recipe_003',
      title: 'ペペロンチーノ',
      image: '/images/pasta.jpg',
      averageRating: 4.2,
      reviewCount: 15
    }
  ]);

  return (
    <div className="recipe-list">
      <h1>人気のレシピ</h1>
      <div className="recipe-grid">
        {recipes.map(recipe => (
          <RecipeCard key={recipe.id} recipe={recipe} />
        ))}
      </div>
    </div>
  );
};

/**
 * ユーザープロフィールでのレビュー一覧例
 */
const UserProfile = ({ userId }) => {
  const [reviews, setReviews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  React.useEffect(() => {
    fetchUserReviews();
  }, [userId]);

  const fetchUserReviews = async () => {
    try {
      const response = await fetch(
        `/api/v1/review/user/${userId}`,
        {
          headers: {
            'Authorization': `Bearer ${userId}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setReviews(data.data.reviews);
      }
    } catch (error) {
      console.error('Failed to fetch user reviews:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div>読み込み中...</div>;
  }

  return (
    <div className="user-profile">
      <h2>あなたのレビュー</h2>
      {reviews.length === 0 ? (
        <p>まだレビューがありません</p>
      ) : (
        <div className="user-reviews-list">
          {reviews.map(review => (
            <div key={review.id} className="user-review-item">
              <div className="review-header">
                <h3>レシピID: {review.recipe_id}</h3>
                <span className="review-rating">{'★'.repeat(review.rating)}</span>
              </div>
              <p className="review-comment">{review.comment}</p>
              <div className="review-meta">
                <span>{new Date(review.created_at).toLocaleDateString('ja-JP')}</span>
                <span>{review.helpful_count} helpful</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * モーダルでのレビュー表示例
 */
const ReviewModal = ({ recipeId, isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h2>レビューと評価</h2>
        <RecipeReviews recipeId={recipeId} />
      </div>
    </div>
  );
};

/**
 * 簡易評価表示ウィジェット
 */
const RatingWidget = ({ recipeId }) => {
  const [summary, setSummary] = useState(null);

  React.useEffect(() => {
    fetchSummary();
  }, [recipeId]);

  const fetchSummary = async () => {
    try {
      const response = await fetch(`/api/v1/review/recipe/${recipeId}/summary`);
      if (response.ok) {
        const data = await response.json();
        setSummary(data.data.summary);
      }
    } catch (error) {
      console.error('Failed to fetch rating summary:', error);
    }
  };

  if (!summary) return null;

  return (
    <div className="rating-widget">
      <div className="rating-stars">
        {[1, 2, 3, 4, 5].map(star => (
          <span
            key={star}
            className={star <= summary.average_rating ? 'star filled' : 'star'}
          >
            ★
          </span>
        ))}
      </div>
      <span className="rating-value">{summary.average_rating.toFixed(1)}</span>
      <span className="review-count">({summary.total_reviews}件)</span>
    </div>
  );
};

/**
 * スタイル例（CSS-in-JS）
 */
const styles = `
  .recipe-detail-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  .recipe-reviews-section {
    margin-top: 60px;
    padding-top: 40px;
    border-top: 2px solid #e0e0e0;
  }

  .recipe-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 16px;
    transition: transform 0.2s;
  }

  .recipe-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }

  .recipe-rating {
    display: flex;
    align-items: center;
    gap: 4px;
    margin: 8px 0;
  }

  .star {
    color: #ffd700;
    font-size: 18px;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 8px;
    padding: 20px;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
  }

  .modal-close {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
  }

  .rating-widget {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f5f5f5;
    border-radius: 20px;
  }
`;

// エクスポート
export default RecipeDetailPage;
export {
  RecipeCard,
  RecipeList,
  UserProfile,
  ReviewModal,
  RatingWidget,
  styles
};

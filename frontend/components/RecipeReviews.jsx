/**
 * Recipe Reviews Component for Personal Recipe Intelligence
 * レシピレビュー・評価コンポーネント
 */

import React, { useState, useEffect } from 'react';
import './RecipeReviews.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * 星評価入力コンポーネント
 */
const StarRating = ({ rating, onRatingChange, readonly = false }) => {
  const [hoverRating, setHoverRating] = useState(0);

  const handleClick = (value) => {
    if (!readonly && onRatingChange) {
      onRatingChange(value);
    }
  };

  const handleMouseEnter = (value) => {
    if (!readonly) {
      setHoverRating(value);
    }
  };

  const handleMouseLeave = () => {
    if (!readonly) {
      setHoverRating(0);
    }
  };

  const displayRating = hoverRating || rating;

  return (
    <div className={`star-rating ${readonly ? 'readonly' : 'interactive'}`}>
      {[1, 2, 3, 4, 5].map((value) => (
        <span
          key={value}
          className={`star ${value <= displayRating ? 'filled' : ''}`}
          onClick={() => handleClick(value)}
          onMouseEnter={() => handleMouseEnter(value)}
          onMouseLeave={handleMouseLeave}
        >
          ★
        </span>
      ))}
    </div>
  );
};

/**
 * 評価サマリーコンポーネント
 */
const RatingSummary = ({ summary }) => {
  if (!summary || summary.total_reviews === 0) {
    return (
      <div className="rating-summary">
        <p className="no-reviews">まだレビューがありません</p>
      </div>
    );
  }

  const { average_rating, total_reviews, rating_distribution } = summary;

  return (
    <div className="rating-summary">
      <div className="average-rating">
        <span className="rating-value">{average_rating.toFixed(1)}</span>
        <StarRating rating={average_rating} readonly={true} />
        <span className="total-reviews">{total_reviews}件のレビュー</span>
      </div>
      <div className="rating-distribution">
        {[5, 4, 3, 2, 1].map((star) => {
          const count = rating_distribution[star] || 0;
          const percentage = total_reviews > 0 ? (count / total_reviews) * 100 : 0;
          return (
            <div key={star} className="distribution-row">
              <span className="star-label">{star}★</span>
              <div className="distribution-bar">
                <div
                  className="distribution-fill"
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <span className="distribution-count">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/**
 * レビュー投稿フォームコンポーネント
 */
const ReviewForm = ({ recipeId, onReviewSubmitted }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const userId = localStorage.getItem('userId') || 'anonymous';
      const response = await fetch(`${API_BASE_URL}/api/v1/review/recipe/${recipeId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userId}`
        },
        body: JSON.stringify({ rating, comment })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'レビューの投稿に失敗しました');
      }

      // 成功
      setRating(5);
      setComment('');
      if (onReviewSubmitted) {
        onReviewSubmitted();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="review-form">
      <h3>レビューを投稿</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>評価</label>
          <StarRating rating={rating} onRatingChange={setRating} />
        </div>
        <div className="form-group">
          <label>コメント</label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="レシピの感想を書いてください"
            rows={5}
            maxLength={2000}
            required
          />
          <span className="char-count">{comment.length}/2000</span>
        </div>
        {error && <div className="error-message">{error}</div>}
        <button type="submit" disabled={isSubmitting || !comment.trim()}>
          {isSubmitting ? '投稿中...' : 'レビューを投稿'}
        </button>
      </form>
    </div>
  );
};

/**
 * レビューアイテムコンポーネント
 */
const ReviewItem = ({ review, onHelpfulClick, currentUserId }) => {
  const [isHelpful, setIsHelpful] = useState(review.is_helpful);
  const [helpfulCount, setHelpfulCount] = useState(review.helpful_count);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleHelpfulClick = async () => {
    if (isProcessing) return;
    setIsProcessing(true);

    try {
      const newHelpfulState = !isHelpful;
      const response = await fetch(
        `${API_BASE_URL}/api/v1/review/${review.id}/helpful`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${currentUserId}`
          },
          body: JSON.stringify({ helpful: newHelpfulState })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update helpful status');
      }

      const data = await response.json();
      setIsHelpful(newHelpfulState);
      setHelpfulCount(data.data.review.helpful_count);

      if (onHelpfulClick) {
        onHelpfulClick();
      }
    } catch (err) {
      console.error('Failed to mark helpful:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="review-item">
      <div className="review-header">
        <div className="review-user">
          <span className="user-id">{review.user_id}</span>
          <StarRating rating={review.rating} readonly={true} />
        </div>
        <span className="review-date">{formatDate(review.created_at)}</span>
      </div>
      <div className="review-content">
        <p>{review.comment}</p>
      </div>
      <div className="review-footer">
        <button
          className={`helpful-button ${isHelpful ? 'active' : ''}`}
          onClick={handleHelpfulClick}
          disabled={isProcessing}
        >
          👍 役に立った ({helpfulCount})
        </button>
        {review.updated_at && (
          <span className="updated-label">編集済み</span>
        )}
      </div>
    </div>
  );
};

/**
 * レビューリストコンポーネント
 */
const ReviewList = ({ reviews, sortBy, onSortChange, currentUserId, onHelpfulClick }) => {
  return (
    <div className="review-list">
      <div className="review-list-header">
        <h3>レビュー一覧</h3>
        <select value={sortBy} onChange={(e) => onSortChange(e.target.value)}>
          <option value="recent">新着順</option>
          <option value="rating">評価順</option>
          <option value="helpful">役に立った順</option>
        </select>
      </div>
      {reviews.length === 0 ? (
        <p className="no-reviews">レビューがありません</p>
      ) : (
        <div className="reviews">
          {reviews.map((review) => (
            <ReviewItem
              key={review.id}
              review={review}
              currentUserId={currentUserId}
              onHelpfulClick={onHelpfulClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * メインのレシピレビューコンポーネント
 */
const RecipeReviews = ({ recipeId }) => {
  const [reviews, setReviews] = useState([]);
  const [summary, setSummary] = useState(null);
  const [sortBy, setSortBy] = useState('recent');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUserId] = useState(localStorage.getItem('userId') || 'anonymous');

  const fetchReviews = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/review/recipe/${recipeId}?sort_by=${sortBy}`,
        {
          headers: {
            'Authorization': `Bearer ${currentUserId}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch reviews');
      }

      const data = await response.json();
      setReviews(data.data.reviews);
      setSummary(data.data.summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, [recipeId, sortBy]);

  const handleReviewSubmitted = () => {
    fetchReviews();
  };

  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
  };

  const handleHelpfulClick = () => {
    // レビューリストを再取得してhelpful_countを更新
    fetchReviews();
  };

  if (isLoading) {
    return <div className="recipe-reviews loading">読み込み中...</div>;
  }

  if (error) {
    return <div className="recipe-reviews error">エラー: {error}</div>;
  }

  return (
    <div className="recipe-reviews">
      <RatingSummary summary={summary} />
      <ReviewForm recipeId={recipeId} onReviewSubmitted={handleReviewSubmitted} />
      <ReviewList
        reviews={reviews}
        sortBy={sortBy}
        onSortChange={handleSortChange}
        currentUserId={currentUserId}
        onHelpfulClick={handleHelpfulClick}
      />
    </div>
  );
};

export default RecipeReviews;

/**
 * レシピ推薦カードコンポーネント
 *
 * AI推薦レシピを表示
 * - 推薦理由の表示
 * - マッチ度スコア表示
 * - フィードバックボタン
 */

import React, { useState } from "react";
import PropTypes from "prop-types";

const RecommendationCard = ({
  recommendation,
  onInterested,
  onNotInterested,
  onViewRecipe,
}) => {
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const { recipe, reason, match_percentage } = recommendation;

  const handleInterested = () => {
    if (onInterested) {
      onInterested(recipe.id);
    }
    setFeedbackSubmitted(true);
  };

  const handleNotInterested = () => {
    if (onNotInterested) {
      onNotInterested(recipe.id);
    }
    setFeedbackSubmitted(true);
  };

  const handleViewRecipe = () => {
    if (onViewRecipe) {
      onViewRecipe(recipe.id);
    }
  };

  const getMatchColor = (percentage) => {
    if (percentage >= 80) return "text-green-600";
    if (percentage >= 60) return "text-blue-600";
    if (percentage >= 40) return "text-yellow-600";
    return "text-gray-600";
  };

  const getMatchBadgeColor = (percentage) => {
    if (percentage >= 80) return "bg-green-100 text-green-800";
    if (percentage >= 60) return "bg-blue-100 text-blue-800";
    if (percentage >= 40) return "bg-yellow-100 text-yellow-800";
    return "bg-gray-100 text-gray-800";
  };

  return (
    <div className="recommendation-card bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden">
      {/* マッチ度バッジ */}
      <div className="relative">
        <div className="absolute top-2 right-2 z-10">
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${getMatchBadgeColor(
              match_percentage
            )}`}
          >
            {match_percentage}% マッチ
          </span>
        </div>

        {/* レシピ画像（ダミー） */}
        <div className="w-full h-48 bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
          <span className="text-4xl">{getCategoryEmoji(recipe.category)}</span>
        </div>
      </div>

      {/* カード本体 */}
      <div className="p-4">
        {/* レシピタイトル */}
        <h3
          className="text-xl font-bold text-gray-800 mb-2 cursor-pointer hover:text-blue-600"
          onClick={handleViewRecipe}
        >
          {recipe.title}
        </h3>

        {/* カテゴリ・タグ */}
        <div className="flex flex-wrap gap-2 mb-3">
          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
            {recipe.category}
          </span>
          {recipe.tags?.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* 推薦理由 */}
        <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <p className="text-sm font-semibold text-blue-800 mb-1">
                おすすめの理由
              </p>
              <p className="text-sm text-blue-700">{reason}</p>
            </div>
          </div>
        </div>

        {/* レシピ情報 */}
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm text-gray-600">
          <div className="flex items-center">
            <svg
              className="w-4 h-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{recipe.cooking_time}分</span>
          </div>
          <div className="flex items-center">
            <svg
              className="w-4 h-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{getDifficultyText(recipe.difficulty)}</span>
          </div>
        </div>

        {/* 主要食材 */}
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-1">主な食材:</p>
          <p className="text-sm text-gray-700">
            {recipe.ingredients
              ?.slice(0, 4)
              .map((ing) => ing.name)
              .join("、")}
            {recipe.ingredients?.length > 4 && "..."}
          </p>
        </div>

        {/* フィードバックボタン */}
        {!feedbackSubmitted ? (
          <div className="flex gap-2">
            <button
              onClick={handleInterested}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 font-semibold text-sm"
            >
              興味あり
            </button>
            <button
              onClick={handleNotInterested}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200 font-semibold text-sm"
            >
              興味なし
            </button>
          </div>
        ) : (
          <div className="text-center py-2 text-sm text-green-600 font-semibold">
            フィードバックありがとうございます
          </div>
        )}
      </div>
    </div>
  );
};

RecommendationCard.propTypes = {
  recommendation: PropTypes.shape({
    recipe: PropTypes.shape({
      id: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      category: PropTypes.string,
      tags: PropTypes.arrayOf(PropTypes.string),
      cooking_time: PropTypes.number,
      difficulty: PropTypes.string,
      ingredients: PropTypes.arrayOf(
        PropTypes.shape({
          name: PropTypes.string,
          amount: PropTypes.string,
        })
      ),
    }).isRequired,
    reason: PropTypes.string.isRequired,
    match_percentage: PropTypes.number.isRequired,
  }).isRequired,
  onInterested: PropTypes.func,
  onNotInterested: PropTypes.func,
  onViewRecipe: PropTypes.func,
};

RecommendationCard.defaultProps = {
  onInterested: null,
  onNotInterested: null,
  onViewRecipe: null,
};

// ヘルパー関数
const getCategoryEmoji = (category) => {
  const emojiMap = {
    主菜: "🍖",
    副菜: "🥗",
    主食: "🍚",
    汁物: "🍲",
    デザート: "🍰",
    その他: "🍽️",
  };
  return emojiMap[category] || "🍽️";
};

const getDifficultyText = (difficulty) => {
  const textMap = {
    easy: "簡単",
    medium: "普通",
    hard: "難しい",
  };
  return textMap[difficulty] || "不明";
};

export default RecommendationCard;

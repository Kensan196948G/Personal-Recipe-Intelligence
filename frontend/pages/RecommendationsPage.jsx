/**
 * レシピ推薦ページ
 *
 * AI推薦レシピの表示・フィードバック
 */

import React, { useState, useEffect } from "react";
import RecommendationCard from "../components/RecommendationCard";

const RecommendationsPage = () => {
  const [userId, setUserId] = useState("user_001");
  const [recommendations, setRecommendations] = useState([]);
  const [trendingRecipes, setTrendingRecipes] = useState([]);
  const [userPreferences, setUserPreferences] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("personalized");
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRecommendations();
    loadUserPreferences();
  }, [userId]);

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      // パーソナライズ推薦を取得
      const response = await fetch(
        `/api/v1/ai/recommend?user_id=${userId}&limit=10`
      );
      const data = await response.json();

      if (data.status === "ok") {
        setRecommendations(data.data.recommendations || []);
      } else {
        throw new Error(data.error || "推薦取得に失敗しました");
      }

      // トレンドレシピを取得
      const trendResponse = await fetch(
        "/api/v1/ai/recommend/trending?limit=10"
      );
      const trendData = await trendResponse.json();

      if (trendData.status === "ok") {
        setTrendingRecipes(trendData.data.trending_recipes || []);
      }
    } catch (err) {
      setError(err.message);
      console.error("推薦取得エラー:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadUserPreferences = async () => {
    try {
      const response = await fetch(`/api/v1/ai/preferences?user_id=${userId}`);
      const data = await response.json();

      if (data.status === "ok") {
        setUserPreferences(data.data);
      }
    } catch (err) {
      console.error("嗜好取得エラー:", err);
    }
  };

  const handleInterested = async (recipeId) => {
    try {
      await fetch("/api/v1/ai/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          recipe_id: recipeId,
          feedback_type: "interested",
        }),
      });

      // 行動記録
      await fetch("/api/v1/ai/activity", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          recipe_id: recipeId,
          activity_type: "favorited",
        }),
      });
    } catch (err) {
      console.error("フィードバックエラー:", err);
    }
  };

  const handleNotInterested = async (recipeId) => {
    try {
      await fetch("/api/v1/ai/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          recipe_id: recipeId,
          feedback_type: "not_interested",
        }),
      });

      // 推薦から削除
      setRecommendations((prev) =>
        prev.filter((rec) => rec.recipe.id !== recipeId)
      );
    } catch (err) {
      console.error("フィードバックエラー:", err);
    }
  };

  const handleViewRecipe = async (recipeId) => {
    try {
      // 閲覧記録
      await fetch("/api/v1/ai/activity", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          recipe_id: recipeId,
          activity_type: "viewed",
        }),
      });

      // レシピ詳細ページへ遷移（実装は後で）
      console.log("レシピ詳細へ:", recipeId);
    } catch (err) {
      console.error("閲覧記録エラー:", err);
    }
  };

  const renderPreferences = () => {
    if (!userPreferences) return null;

    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          あなたの好み分析
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 好きな食材 */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">好きな食材</h4>
            <div className="space-y-1">
              {userPreferences.favorite_ingredients.slice(0, 5).map((item) => (
                <div
                  key={item.name}
                  className="flex justify-between text-sm text-gray-600"
                >
                  <span>{item.name}</span>
                  <span className="text-blue-600">{item.count}回</span>
                </div>
              ))}
            </div>
          </div>

          {/* 好きなカテゴリ */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">
              好きなカテゴリ
            </h4>
            <div className="space-y-1">
              {userPreferences.favorite_categories.map((item) => (
                <div
                  key={item.name}
                  className="flex justify-between text-sm text-gray-600"
                >
                  <span>{item.name}</span>
                  <span className="text-blue-600">{item.count}回</span>
                </div>
              ))}
            </div>
          </div>

          {/* 好きなタグ */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">好きなタグ</h4>
            <div className="flex flex-wrap gap-2">
              {userPreferences.favorite_tags.slice(0, 8).map((item) => (
                <span
                  key={item.name}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                >
                  {item.name}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* 統計情報 */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">
                {userPreferences.total_activities}
              </p>
              <p className="text-sm text-gray-600">総活動数</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">
                {userPreferences.cooking_frequency}
              </p>
              <p className="text-sm text-gray-600">月間調理回数</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-600">
                {userPreferences.average_cooking_time}分
              </p>
              <p className="text-sm text-gray-600">平均調理時間</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">
                {userPreferences.preferred_difficulty === "easy"
                  ? "簡単"
                  : userPreferences.preferred_difficulty === "medium"
                  ? "普通"
                  : "難しい"}
              </p>
              <p className="text-sm text-gray-600">好みの難易度</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            AI レシピ推薦
          </h1>
          <p className="text-gray-600">
            あなたの好みに合わせたレシピをおすすめします
          </p>
        </div>

        {/* 嗜好分析 */}
        {renderPreferences()}

        {/* タブ */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-4">
              <button
                onClick={() => setActiveTab("personalized")}
                className={`px-4 py-2 border-b-2 font-semibold transition-colors ${
                  activeTab === "personalized"
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-600 hover:text-gray-800"
                }`}
              >
                あなたへのおすすめ
              </button>
              <button
                onClick={() => setActiveTab("trending")}
                className={`px-4 py-2 border-b-2 font-semibold transition-colors ${
                  activeTab === "trending"
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-600 hover:text-gray-800"
                }`}
              >
                人気のレシピ
              </button>
            </nav>
          </div>
        </div>

        {/* エラー表示 */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* ローディング */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">推薦を生成中...</p>
          </div>
        )}

        {/* レシピカード */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activeTab === "personalized" &&
              recommendations.map((recommendation, index) => (
                <RecommendationCard
                  key={index}
                  recommendation={recommendation}
                  onInterested={handleInterested}
                  onNotInterested={handleNotInterested}
                  onViewRecipe={handleViewRecipe}
                />
              ))}

            {activeTab === "trending" &&
              trendingRecipes.map((recommendation, index) => (
                <RecommendationCard
                  key={index}
                  recommendation={recommendation}
                  onInterested={handleInterested}
                  onNotInterested={handleNotInterested}
                  onViewRecipe={handleViewRecipe}
                />
              ))}
          </div>
        )}

        {/* 空の状態 */}
        {!loading &&
          activeTab === "personalized" &&
          recommendations.length === 0 && (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              <h3 className="mt-4 text-lg font-semibold text-gray-700">
                推薦レシピがありません
              </h3>
              <p className="mt-2 text-gray-600">
                レシピを閲覧・お気に入りすると、おすすめが表示されます
              </p>
            </div>
          )}
      </div>
    </div>
  );
};

export default RecommendationsPage;

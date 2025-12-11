"""
レシピ推薦AIサービス

ハイブリッド推薦アルゴリズムを実装:
- 協調フィルタリング（類似ユーザーの好み）
- コンテンツベースフィルタリング（食材・カテゴリの類似性）
- スコアリング・ランキング
- 多様性確保
"""

import json
import math
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class RecommendationAIService:
  """レシピ推薦AIサービス"""

  def __init__(self, data_dir: str = "data"):
    self.data_dir = Path(data_dir)
    self.data_dir.mkdir(exist_ok=True)

    self.user_activity_file = self.data_dir / "user_activity.json"
    self.preferences_file = self.data_dir / "user_preferences.json"
    self.feedback_file = self.data_dir / "recommendation_feedback.json"

    self.user_activities = self._load_json(self.user_activity_file, {})
    self.user_preferences = self._load_json(self.preferences_file, {})
    self.feedback_data = self._load_json(self.feedback_file, {})

  def _load_json(self, file_path: Path, default: dict) -> dict:
    """JSONファイル読み込み"""
    if file_path.exists():
      try:
        with open(file_path, "r", encoding="utf-8") as f:
          return json.load(f)
      except Exception:
        return default
    return default

  def _save_json(self, file_path: Path, data: dict) -> None:
    """JSONファイル保存"""
    with open(file_path, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)

  def record_activity(
    self,
    user_id: str,
    recipe_id: str,
    activity_type: str,
    metadata: Optional[Dict] = None,
  ) -> None:
    """
    ユーザー行動を記録

    activity_type: viewed, cooked, rated, favorited, dismissed
    """
    if user_id not in self.user_activities:
      self.user_activities[user_id] = []

    activity = {
      "recipe_id": recipe_id,
      "activity_type": activity_type,
      "timestamp": datetime.utcnow().isoformat(),
      "metadata": metadata or {},
    }

    self.user_activities[user_id].append(activity)
    self._save_json(self.user_activity_file, self.user_activities)

  def get_personalized_recommendations(
    self, user_id: str, recipes: List[Dict], limit: int = 10
  ) -> List[Dict]:
    """
    パーソナライズ推薦を生成

    ハイブリッドアルゴリズム:
    - 協調フィルタリング（30%）
    - コンテンツベースフィルタリング（50%）
    - トレンドスコア（10%）
    - 多様性ペナルティ（10%）
    """
    if not recipes:
      return []

    # ユーザーの行動履歴を取得
    user_history = self._get_user_history(user_id)
    if not user_history:
      # 新規ユーザーにはトレンド推薦
      return self.get_trending_recommendations(recipes, limit)

    # 各レシピのスコアを計算
    scored_recipes = []
    for recipe in recipes:
      recipe_id = recipe.get("id", "")

      # 既に閲覧済み・却下済みは除外
      if self._is_already_interacted(user_id, recipe_id):
        continue

      # スコア計算
      collab_score = self._calculate_collaborative_score(
        user_id, recipe_id, recipes
      )
      content_score = self._calculate_content_score(
        user_id, recipe, user_history, recipes
      )
      trend_score = self._calculate_trend_score(recipe_id)
      diversity_penalty = self._calculate_diversity_penalty(
        recipe, user_history
      )

      # 重み付け合計
      total_score = (
        collab_score * 0.3
        + content_score * 0.5
        + trend_score * 0.1
        - diversity_penalty * 0.1
      )

      scored_recipes.append(
        {
          "recipe": recipe,
          "score": total_score,
          "reason": self._generate_recommendation_reason(
            recipe, collab_score, content_score, trend_score
          ),
          "match_percentage": min(int(total_score * 100), 100),
        }
      )

    # スコア順にソート
    scored_recipes.sort(key=lambda x: x["score"], reverse=True)

    # 多様性を確保（同じカテゴリが連続しないように）
    diverse_recommendations = self._ensure_diversity(scored_recipes, limit)

    return diverse_recommendations

  def get_similar_recipes(
    self, recipe_id: str, recipes: List[Dict], limit: int = 5
  ) -> List[Dict]:
    """類似レシピを取得（コンテンツベース）"""
    target_recipe = next(
      (r for r in recipes if r.get("id") == recipe_id), None
    )
    if not target_recipe:
      return []

    similar_recipes = []
    for recipe in recipes:
      if recipe.get("id") == recipe_id:
        continue

      similarity = self._calculate_recipe_similarity(target_recipe, recipe)
      similar_recipes.append(
        {
          "recipe": recipe,
          "similarity": similarity,
          "match_percentage": int(similarity * 100),
        }
      )

    similar_recipes.sort(key=lambda x: x["similarity"], reverse=True)
    return similar_recipes[:limit]

  def get_trending_recommendations(
    self, recipes: List[Dict], limit: int = 10
  ) -> List[Dict]:
    """トレンドレシピを取得"""
    trending = []
    for recipe in recipes:
      recipe_id = recipe.get("id", "")
      trend_score = self._calculate_trend_score(recipe_id)

      trending.append(
        {
          "recipe": recipe,
          "score": trend_score,
          "reason": "最近人気のレシピです",
          "match_percentage": int(trend_score * 100),
        }
      )

    trending.sort(key=lambda x: x["score"], reverse=True)
    return trending[:limit]

  def submit_feedback(
    self, user_id: str, recipe_id: str, feedback_type: str, metadata: Optional[Dict] = None
  ) -> None:
    """
    推薦フィードバックを記録

    feedback_type: interested, not_interested, favorited, cooked
    """
    if user_id not in self.feedback_data:
      self.feedback_data[user_id] = []

    feedback = {
      "recipe_id": recipe_id,
      "feedback_type": feedback_type,
      "timestamp": datetime.utcnow().isoformat(),
      "metadata": metadata or {},
    }

    self.feedback_data[user_id].append(feedback)
    self._save_json(self.feedback_file, self.feedback_data)

    # ユーザー行動としても記録
    self.record_activity(user_id, recipe_id, feedback_type, metadata)

  def get_user_preferences(self, user_id: str, recipes: List[Dict]) -> Dict:
    """ユーザー嗜好分析結果を取得"""
    user_history = self._get_user_history(user_id)

    if not user_history:
      return {
        "user_id": user_id,
        "total_activities": 0,
        "favorite_ingredients": [],
        "favorite_categories": [],
        "favorite_tags": [],
        "cooking_frequency": 0,
        "average_cooking_time": 0,
        "preferred_difficulty": "unknown",
      }

    # 頻出食材を抽出
    ingredient_counter = defaultdict(int)
    category_counter = defaultdict(int)
    tag_counter = defaultdict(int)
    cooking_times = []
    difficulty_counter = defaultdict(int)

    for activity in user_history:
      recipe = next(
        (r for r in recipes if r.get("id") == activity["recipe_id"]), None
      )
      if not recipe:
        continue

      # 食材カウント
      for ingredient in recipe.get("ingredients", []):
        name = ingredient.get("name", "").lower()
        if name:
          ingredient_counter[name] += 1

      # カテゴリカウント
      category = recipe.get("category", "")
      if category:
        category_counter[category] += 1

      # タグカウント
      for tag in recipe.get("tags", []):
        tag_counter[tag] += 1

      # 調理時間
      cook_time = recipe.get("cooking_time", 0)
      if cook_time:
        cooking_times.append(cook_time)

      # 難易度
      difficulty = recipe.get("difficulty", "")
      if difficulty:
        difficulty_counter[difficulty] += 1

    # トップ要素を抽出
    favorite_ingredients = sorted(
      ingredient_counter.items(), key=lambda x: x[1], reverse=True
    )[:10]
    favorite_categories = sorted(
      category_counter.items(), key=lambda x: x[1], reverse=True
    )[:5]
    favorite_tags = sorted(
      tag_counter.items(), key=lambda x: x[1], reverse=True
    )[:10]

    # 平均調理時間
    avg_cooking_time = (
      sum(cooking_times) / len(cooking_times) if cooking_times else 0
    )

    # 好みの難易度
    preferred_difficulty = (
      max(difficulty_counter.items(), key=lambda x: x[1])[0]
      if difficulty_counter
      else "unknown"
    )

    # 料理頻度（直近30日）
    recent_cooked = [
      a
      for a in user_history
      if a["activity_type"] == "cooked"
      and self._is_recent(a["timestamp"], days=30)
    ]

    return {
      "user_id": user_id,
      "total_activities": len(user_history),
      "favorite_ingredients": [
        {"name": name, "count": count} for name, count in favorite_ingredients
      ],
      "favorite_categories": [
        {"name": name, "count": count} for name, count in favorite_categories
      ],
      "favorite_tags": [
        {"name": name, "count": count} for name, count in favorite_tags
      ],
      "cooking_frequency": len(recent_cooked),
      "average_cooking_time": int(avg_cooking_time),
      "preferred_difficulty": preferred_difficulty,
    }

  def _get_user_history(self, user_id: str) -> List[Dict]:
    """ユーザー行動履歴を取得"""
    return self.user_activities.get(user_id, [])

  def _is_already_interacted(self, user_id: str, recipe_id: str) -> bool:
    """既に閲覧済み・却下済みかチェック"""
    user_history = self._get_user_history(user_id)

    # 直近の行動をチェック（30日以内）
    recent_interactions = [
      a
      for a in user_history
      if a["recipe_id"] == recipe_id and self._is_recent(a["timestamp"], days=30)
    ]

    # 却下済みは除外
    dismissed = any(
      a["activity_type"] == "not_interested" for a in recent_interactions
    )

    return dismissed

  def _is_recent(self, timestamp_str: str, days: int = 30) -> bool:
    """指定日数以内かチェック"""
    try:
      timestamp = datetime.fromisoformat(timestamp_str)
      return datetime.utcnow() - timestamp <= timedelta(days=days)
    except Exception:
      return False

  def _calculate_collaborative_score(
    self, user_id: str, recipe_id: str, recipes: List[Dict]
  ) -> float:
    """協調フィルタリングスコア計算"""
    # 類似ユーザーを見つける
    similar_users = self._find_similar_users(user_id)

    if not similar_users:
      return 0.0

    # 類似ユーザーがこのレシピをどう評価したか
    total_score = 0.0
    total_weight = 0.0

    for similar_user_id, similarity in similar_users:
      user_rating = self._get_user_rating_for_recipe(
        similar_user_id, recipe_id
      )
      if user_rating > 0:
        total_score += user_rating * similarity
        total_weight += similarity

    if total_weight == 0:
      return 0.0

    return total_score / total_weight

  def _find_similar_users(
    self, user_id: str, top_n: int = 5
  ) -> List[Tuple[str, float]]:
    """類似ユーザーを見つける"""
    user_history = self._get_user_history(user_id)
    user_recipes = set(a["recipe_id"] for a in user_history)

    if not user_recipes:
      return []

    similar_users = []
    for other_user_id in self.user_activities:
      if other_user_id == user_id:
        continue

      other_history = self._get_user_history(other_user_id)
      other_recipes = set(a["recipe_id"] for a in other_history)

      # Jaccard類似度
      intersection = user_recipes & other_recipes
      union = user_recipes | other_recipes

      if union:
        similarity = len(intersection) / len(union)
        if similarity > 0:
          similar_users.append((other_user_id, similarity))

    similar_users.sort(key=lambda x: x[1], reverse=True)
    return similar_users[:top_n]

  def _get_user_rating_for_recipe(self, user_id: str, recipe_id: str) -> float:
    """ユーザーのレシピに対する暗黙的評価"""
    user_history = self._get_user_history(user_id)

    recipe_activities = [
      a for a in user_history if a["recipe_id"] == recipe_id
    ]

    if not recipe_activities:
      return 0.0

    # 行動タイプごとにスコア付与
    score = 0.0
    for activity in recipe_activities:
      activity_type = activity["activity_type"]
      if activity_type == "cooked":
        score += 1.0
      elif activity_type == "favorited":
        score += 0.8
      elif activity_type == "rated":
        # メタデータに評価が含まれている場合
        rating = activity.get("metadata", {}).get("rating", 0)
        score += rating / 5.0  # 5段階評価を0-1に正規化
      elif activity_type == "viewed":
        score += 0.1
      elif activity_type == "not_interested":
        score -= 0.5

    return max(0.0, min(1.0, score))  # 0-1の範囲にクリップ

  def _calculate_content_score(
    self, user_id: str, recipe: Dict, user_history: List[Dict], recipes: List[Dict]
  ) -> float:
    """コンテンツベースフィルタリングスコア計算"""
    if not user_history:
      return 0.0

    # ユーザーが好んだレシピの特徴を抽出
    liked_recipes = []
    for activity in user_history:
      if activity["activity_type"] in ["cooked", "favorited", "rated"]:
        recipe_obj = next(
          (r for r in recipes if r.get("id") == activity["recipe_id"]), None
        )
        if recipe_obj:
          liked_recipes.append(recipe_obj)

    if not liked_recipes:
      return 0.0

    # 各レシピとの類似度を計算し、平均を取る
    similarities = [
      self._calculate_recipe_similarity(recipe, liked_recipe)
      for liked_recipe in liked_recipes
    ]

    return sum(similarities) / len(similarities) if similarities else 0.0

  def _calculate_recipe_similarity(
    self, recipe1: Dict, recipe2: Dict
  ) -> float:
    """2つのレシピの類似度を計算（コサイン類似度風）"""
    # 特徴ベクトルを作成
    features1 = self._extract_recipe_features(recipe1)
    features2 = self._extract_recipe_features(recipe2)

    # コサイン類似度
    return self._cosine_similarity(features1, features2)

  def _extract_recipe_features(self, recipe: Dict) -> Dict[str, float]:
    """レシピから特徴ベクトルを抽出"""
    features = {}

    # 食材（TF-IDF風の重み付け）
    for ingredient in recipe.get("ingredients", []):
      name = ingredient.get("name", "").lower()
      if name:
        # 主要食材として重み付け
        features[f"ingredient:{name}"] = 1.0

    # カテゴリ
    category = recipe.get("category", "")
    if category:
      features[f"category:{category}"] = 2.0  # カテゴリは重要

    # タグ
    for tag in recipe.get("tags", []):
      features[f"tag:{tag}"] = 1.5

    # 調理時間（範囲でグループ化）
    cook_time = recipe.get("cooking_time", 0)
    if cook_time <= 15:
      features["time:quick"] = 1.0
    elif cook_time <= 30:
      features["time:medium"] = 1.0
    else:
      features["time:long"] = 1.0

    # 難易度
    difficulty = recipe.get("difficulty", "")
    if difficulty:
      features[f"difficulty:{difficulty}"] = 1.0

    return features

  def _cosine_similarity(
    self, features1: Dict[str, float], features2: Dict[str, float]
  ) -> float:
    """コサイン類似度計算"""
    # 共通の特徴を抽出
    common_features = set(features1.keys()) & set(features2.keys())

    if not common_features:
      return 0.0

    # 内積
    dot_product = sum(
      features1[f] * features2[f] for f in common_features
    )

    # ノルム
    norm1 = math.sqrt(sum(v ** 2 for v in features1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in features2.values()))

    if norm1 == 0 or norm2 == 0:
      return 0.0

    return dot_product / (norm1 * norm2)

  def _calculate_trend_score(self, recipe_id: str) -> float:
    """トレンドスコア計算（直近の人気度）"""
    # 全ユーザーの直近30日のアクティビティをカウント
    recent_activities = 0
    total_users = 0

    for user_id, activities in self.user_activities.items():
      total_users += 1
      recent_recipe_activities = [
        a
        for a in activities
        if a["recipe_id"] == recipe_id
        and self._is_recent(a["timestamp"], days=30)
      ]
      recent_activities += len(recent_recipe_activities)

    # 正規化（最大1.0）
    if total_users == 0:
      return 0.0

    # ユーザー数で正規化
    normalized_score = recent_activities / max(total_users, 1)
    return min(normalized_score, 1.0)

  def _calculate_diversity_penalty(
    self, recipe: Dict, user_history: List[Dict]
  ) -> float:
    """多様性ペナルティ計算（似たレシピばかり推薦しない）"""
    # 直近の閲覧履歴から同じカテゴリの頻度をチェック
    category = recipe.get("category", "")
    if not category:
      return 0.0

    recent_history = [
      a for a in user_history if self._is_recent(a["timestamp"], days=7)
    ]

    if not recent_history:
      return 0.0

    # 同じカテゴリの割合
    same_category_count = sum(
      1 for a in recent_history if a.get("category") == category
    )

    penalty = same_category_count / len(recent_history)
    return penalty

  def _generate_recommendation_reason(
    self, recipe: Dict, collab_score: float, content_score: float, trend_score: float
  ) -> str:
    """推薦理由を生成"""
    reasons = []

    if content_score > 0.7:
      reasons.append("あなたの好みに合っています")
    elif content_score > 0.5:
      reasons.append("似た料理をお気に入りにしています")

    if collab_score > 0.7:
      reasons.append("似た嗜好のユーザーに人気です")

    if trend_score > 0.5:
      reasons.append("最近人気急上昇中です")

    # タグベースの理由
    tags = recipe.get("tags", [])
    if "簡単" in tags:
      reasons.append("簡単に作れます")
    if "時短" in tags:
      reasons.append("短時間で調理できます")
    if "ヘルシー" in tags:
      reasons.append("ヘルシーなレシピです")

    if not reasons:
      reasons.append("おすすめのレシピです")

    return "、".join(reasons[:3])  # 最大3つまで

  def _ensure_diversity(
    self, scored_recipes: List[Dict], limit: int
  ) -> List[Dict]:
    """推薦結果の多様性を確保"""
    if len(scored_recipes) <= limit:
      return scored_recipes

    diverse_list = []
    category_counts = defaultdict(int)

    for item in scored_recipes:
      if len(diverse_list) >= limit:
        break

      recipe = item["recipe"]
      category = recipe.get("category", "unknown")

      # 同じカテゴリが3つ以上連続しないように
      if category_counts[category] < 3:
        diverse_list.append(item)
        category_counts[category] += 1

    # まだ足りない場合は残りから追加
    if len(diverse_list) < limit:
      for item in scored_recipes:
        if item not in diverse_list:
          diverse_list.append(item)
          if len(diverse_list) >= limit:
            break

    return diverse_list

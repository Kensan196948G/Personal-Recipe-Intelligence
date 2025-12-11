"""
季節・時間帯に応じたレシピ推薦サービス

このモジュールは以下の機能を提供します：
- 季節に合ったレシピ推薦
- 時間帯に応じたレシピ推薦（朝食/昼食/夕食/夜食）
- 旬の食材を使ったレシピ推薦
- 気温に応じたレシピ推薦
"""

from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class Season(str, Enum):
    """季節の列挙型"""

    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class MealTime(str, Enum):
    """食事時間の列挙型"""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    LATE_NIGHT = "late_night"


# 季節ごとの旬の食材データ
SEASONAL_INGREDIENTS: Dict[str, List[str]] = {
    "spring": [
        "たけのこ",
        "菜の花",
        "新玉ねぎ",
        "新じゃがいも",
        "春キャベツ",
        "アスパラガス",
        "そらまめ",
        "さやえんどう",
        "いちご",
        "たらの芽",
    ],
    "summer": [
        "トマト",
        "きゅうり",
        "なす",
        "ピーマン",
        "ゴーヤ",
        "オクラ",
        "枝豆",
        "とうもろこし",
        "すいか",
        "ししとう",
    ],
    "autumn": [
        "さつまいも",
        "きのこ",
        "栗",
        "かぼちゃ",
        "さんま",
        "さといも",
        "ぎんなん",
        "柿",
        "なし",
        "ぶどう",
    ],
    "winter": [
        "白菜",
        "大根",
        "ほうれん草",
        "ねぎ",
        "小松菜",
        "春菊",
        "れんこん",
        "ごぼう",
        "みかん",
        "ブロッコリー",
    ],
}

# 時間帯ごとの推奨料理タグ
MEAL_TIME_TAGS: Dict[str, List[str]] = {
    "breakfast": [
        "朝食",
        "簡単",
        "時短",
        "ご飯",
        "パン",
        "和食",
        "洋食",
        "卵料理",
        "サラダ",
    ],
    "lunch": [
        "昼食",
        "ランチ",
        "丼",
        "麺類",
        "パスタ",
        "カレー",
        "定食",
        "お弁当",
    ],
    "dinner": [
        "夕食",
        "ディナー",
        "メイン",
        "おかず",
        "鍋",
        "煮物",
        "焼き物",
        "炒め物",
    ],
    "late_night": [
        "夜食",
        "軽食",
        "簡単",
        "スープ",
        "おにぎり",
        "麺類",
        "ヘルシー",
    ],
}

# 気温に応じた料理カテゴリ
TEMPERATURE_CATEGORIES: Dict[str, List[str]] = {
    "hot": ["冷たい", "冷製", "サラダ", "そうめん", "冷やし", "アイス"],
    "warm": ["温かい", "煮物", "鍋", "スープ", "シチュー", "グラタン"],
}


class SeasonalService:
    """季節・時間帯に応じたレシピ推薦サービスクラス"""

    def __init__(self, recipe_data: Optional[List[Dict]] = None):
        """
        初期化

        Args:
            recipe_data: レシピデータのリスト（テスト用）
        """
        self.recipe_data = recipe_data or []

    def get_current_season(self, date: Optional[datetime] = None) -> Season:
        """
        現在の季節を取得

        Args:
            date: 判定する日時（Noneの場合は現在時刻）

        Returns:
            Season: 現在の季節
        """
        if date is None:
            date = datetime.now()

        month = date.month

        if 3 <= month <= 5:
            return Season.SPRING
        elif 6 <= month <= 8:
            return Season.SUMMER
        elif 9 <= month <= 11:
            return Season.AUTUMN
        else:
            return Season.WINTER

    def get_current_meal_time(self, time: Optional[datetime] = None) -> MealTime:
        """
        現在の食事時間を取得

        Args:
            time: 判定する時刻（Noneの場合は現在時刻）

        Returns:
            MealTime: 現在の食事時間
        """
        if time is None:
            time = datetime.now()

        hour = time.hour

        if 5 <= hour < 10:
            return MealTime.BREAKFAST
        elif 10 <= hour < 15:
            return MealTime.LUNCH
        elif 15 <= hour < 22:
            return MealTime.DINNER
        else:
            return MealTime.LATE_NIGHT

    def get_seasonal_ingredients(self, season: Optional[Season] = None) -> List[str]:
        """
        指定された季節の旬の食材を取得

        Args:
            season: 季節（Noneの場合は現在の季節）

        Returns:
            List[str]: 旬の食材リスト
        """
        if season is None:
            season = self.get_current_season()

        return SEASONAL_INGREDIENTS.get(season.value, [])

    def recommend_by_season(
        self, season: Optional[Season] = None, limit: int = 10
    ) -> List[Dict]:
        """
        季節に応じたレシピ推薦

        Args:
            season: 季節（Noneの場合は現在の季節）
            limit: 取得する最大件数

        Returns:
            List[Dict]: 推薦レシピリスト
        """
        if season is None:
            season = self.get_current_season()

        seasonal_ingredients = self.get_seasonal_ingredients(season)
        recommended_recipes = []

        for recipe in self.recipe_data:
            ingredients = recipe.get("ingredients", [])
            score = 0

            # 材料が文字列リストの場合
            if isinstance(ingredients, list):
                for ingredient in ingredients:
                    if isinstance(ingredient, str):
                        for seasonal_ing in seasonal_ingredients:
                            if seasonal_ing in ingredient:
                                score += 1
                                break
                    elif isinstance(ingredient, dict):
                        ingredient_name = ingredient.get("name", "")
                        for seasonal_ing in seasonal_ingredients:
                            if seasonal_ing in ingredient_name:
                                score += 1
                                break

            if score > 0:
                recipe_with_score = recipe.copy()
                recipe_with_score["season_score"] = score
                recommended_recipes.append(recipe_with_score)

        # スコア順にソート
        recommended_recipes.sort(key=lambda x: x["season_score"], reverse=True)

        return recommended_recipes[:limit]

    def recommend_by_meal_time(
        self, meal_time: Optional[MealTime] = None, limit: int = 10
    ) -> List[Dict]:
        """
        時間帯に応じたレシピ推薦

        Args:
            meal_time: 食事時間（Noneの場合は現在の時間帯）
            limit: 取得する最大件数

        Returns:
            List[Dict]: 推薦レシピリスト
        """
        if meal_time is None:
            meal_time = self.get_current_meal_time()

        meal_tags = MEAL_TIME_TAGS.get(meal_time.value, [])
        recommended_recipes = []

        for recipe in self.recipe_data:
            tags = recipe.get("tags", [])
            score = 0

            for tag in tags:
                if tag in meal_tags:
                    score += 1

            if score > 0:
                recipe_with_score = recipe.copy()
                recipe_with_score["meal_time_score"] = score
                recommended_recipes.append(recipe_with_score)

        # スコア順にソート
        recommended_recipes.sort(key=lambda x: x["meal_time_score"], reverse=True)

        return recommended_recipes[:limit]

    def recommend_by_temperature(
        self, temperature: float, limit: int = 10
    ) -> List[Dict]:
        """
        気温に応じたレシピ推薦

        Args:
            temperature: 気温（摂氏）
            limit: 取得する最大件数

        Returns:
            List[Dict]: 推薦レシピリスト
        """
        # 25度以上なら冷たい料理、それ以下なら温かい料理
        category = "hot" if temperature >= 25 else "warm"
        category_tags = TEMPERATURE_CATEGORIES.get(category, [])
        recommended_recipes = []

        for recipe in self.recipe_data:
            tags = recipe.get("tags", [])
            title = recipe.get("title", "")
            description = recipe.get("description", "")
            score = 0

            # タグ、タイトル、説明文から判定
            for cat_tag in category_tags:
                if cat_tag in tags:
                    score += 2
                if cat_tag in title:
                    score += 1
                if cat_tag in description:
                    score += 1

            if score > 0:
                recipe_with_score = recipe.copy()
                recipe_with_score["temperature_score"] = score
                recipe_with_score["recommended_category"] = category
                recommended_recipes.append(recipe_with_score)

        # スコア順にソート
        recommended_recipes.sort(key=lambda x: x["temperature_score"], reverse=True)

        return recommended_recipes[:limit]

    def recommend_comprehensive(
        self,
        season: Optional[Season] = None,
        meal_time: Optional[MealTime] = None,
        temperature: Optional[float] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        総合的なレシピ推薦（季節・時間帯・気温を考慮）

        Args:
            season: 季節（Noneの場合は現在の季節）
            meal_time: 食事時間（Noneの場合は現在の時間帯）
            temperature: 気温（Noneの場合は考慮しない）
            limit: 取得する最大件数

        Returns:
            List[Dict]: 推薦レシピリスト
        """
        if season is None:
            season = self.get_current_season()
        if meal_time is None:
            meal_time = self.get_current_meal_time()

        seasonal_ingredients = self.get_seasonal_ingredients(season)
        meal_tags = MEAL_TIME_TAGS.get(meal_time.value, [])

        recommended_recipes = []

        for recipe in self.recipe_data:
            ingredients = recipe.get("ingredients", [])
            tags = recipe.get("tags", [])
            title = recipe.get("title", "")
            description = recipe.get("description", "")
            total_score = 0

            # 季節スコア
            season_score = 0
            if isinstance(ingredients, list):
                for ingredient in ingredients:
                    if isinstance(ingredient, str):
                        for seasonal_ing in seasonal_ingredients:
                            if seasonal_ing in ingredient:
                                season_score += 1
                                break
                    elif isinstance(ingredient, dict):
                        ingredient_name = ingredient.get("name", "")
                        for seasonal_ing in seasonal_ingredients:
                            if seasonal_ing in ingredient_name:
                                season_score += 1
                                break

            # 時間帯スコア
            meal_time_score = sum(1 for tag in tags if tag in meal_tags)

            # 気温スコア
            temperature_score = 0
            if temperature is not None:
                category = "hot" if temperature >= 25 else "warm"
                category_tags = TEMPERATURE_CATEGORIES.get(category, [])
                for cat_tag in category_tags:
                    if cat_tag in tags:
                        temperature_score += 2
                    if cat_tag in title:
                        temperature_score += 1
                    if cat_tag in description:
                        temperature_score += 1

            # 総合スコア計算（重み付け）
            total_score = (season_score * 3) + (meal_time_score * 2) + temperature_score

            if total_score > 0:
                recipe_with_score = recipe.copy()
                recipe_with_score["total_score"] = total_score
                recipe_with_score["season_score"] = season_score
                recipe_with_score["meal_time_score"] = meal_time_score
                recipe_with_score["temperature_score"] = temperature_score
                recommended_recipes.append(recipe_with_score)

        # スコア順にソート
        recommended_recipes.sort(key=lambda x: x["total_score"], reverse=True)

        return recommended_recipes[:limit]

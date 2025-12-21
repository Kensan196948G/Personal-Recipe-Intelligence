"""
レシピ推薦サービス

材料ベースのレシピ推薦システムを提供する。
"""

from typing import List, Dict, Any, Set
from dataclasses import dataclass


@dataclass
class RecommendationResult:
    """推薦結果"""

    recipe: Dict[str, Any]
    match_score: float
    matched_ingredients: List[str]
    missing_ingredients: List[str]
    match_percentage: float


class IngredientNormalizer:
    """材料名正規化クラス"""

    # 正規化マッピング
    NORMALIZATION_MAP = {
        "玉ねぎ": "たまねぎ",
        "玉葱": "たまねぎ",
        "タマネギ": "たまねぎ",
        "人参": "にんじん",
        "ニンジン": "にんじん",
        "じゃが芋": "じゃがいも",
        "ジャガイモ": "じゃがいも",
        "ジャガ芋": "じゃがいも",
        "馬鈴薯": "じゃがいも",
        "トマト": "とまと",
        "茄子": "なす",
        "ナス": "なす",
        "きゅうり": "きゅうり",
        "キュウリ": "きゅうり",
        "胡瓜": "きゅうり",
    }

    # 調味料リスト（低スコア）
    SEASONINGS = {
        "塩",
        "砂糖",
        "醤油",
        "しょうゆ",
        "味噌",
        "みそ",
        "酢",
        "油",
        "サラダ油",
        "オリーブオイル",
        "ごま油",
        "こしょう",
        "胡椒",
        "みりん",
        "料理酒",
        "酒",
        "だし",
        "出汁",
        "鶏がらスープの素",
        "コンソメ",
        "ブイヨン",
        "ケチャップ",
        "マヨネーズ",
        "ソース",
        "ウスターソース",
        "中濃ソース",
        "バター",
        "マーガリン",
    }

    @classmethod
    def normalize(cls, ingredient: str) -> str:
        """
        材料名を正規化する

        Args:
          ingredient: 材料名

        Returns:
          正規化された材料名
        """
        # 空白を削除
        normalized = ingredient.strip()

        # 全角英数字を半角に変換
        normalized = cls._zen_to_han(normalized)

        # マッピングに存在する場合は変換
        if normalized in cls.NORMALIZATION_MAP:
            normalized = cls.NORMALIZATION_MAP[normalized]

        # 小文字化（英語の場合）
        normalized = normalized.lower()

        return normalized

    @classmethod
    def is_seasoning(cls, ingredient: str) -> bool:
        """
        調味料かどうかを判定

        Args:
          ingredient: 材料名

        Returns:
          調味料の場合True
        """
        normalized = cls.normalize(ingredient)
        return normalized in cls.SEASONINGS

    @staticmethod
    def _zen_to_han(text: str) -> str:
        """全角英数字を半角に変換"""
        return text.translate(
            str.maketrans(
                "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
                "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            )
        )


class RecommendationService:
    """レシピ推薦サービス"""

    # スコアリングの重み
    MAIN_INGREDIENT_WEIGHT = 1.0
    SEASONING_WEIGHT = 0.3

    def __init__(self, recipes: List[Dict[str, Any]]):
        """
        Args:
          recipes: レシピリスト
        """
        self.recipes = recipes
        self.normalizer = IngredientNormalizer()

    def recommend_by_ingredients(
        self,
        available_ingredients: List[str],
        min_score: float = 0.5,
        max_results: int = 10,
    ) -> List[RecommendationResult]:
        """
        指定した材料から作れるレシピを推薦

        Args:
          available_ingredients: 利用可能な材料リスト
          min_score: 最小マッチスコア（0.0〜1.0）
          max_results: 最大結果数

        Returns:
          推薦結果リスト（スコア降順）
        """
        # 材料を正規化
        normalized_available = {
            self.normalizer.normalize(ing) for ing in available_ingredients
        }

        results: List[RecommendationResult] = []

        for recipe in self.recipes:
            # レシピの材料を取得
            recipe_ingredients = self._extract_recipe_ingredients(recipe)

            if not recipe_ingredients:
                continue

            # マッチング計算
            result = self._calculate_match(
                recipe=recipe,
                recipe_ingredients=recipe_ingredients,
                available_ingredients=normalized_available,
            )

            # スコアが基準以上なら追加
            if result.match_score >= min_score:
                results.append(result)

        # スコア降順でソート
        results.sort(key=lambda x: x.match_score, reverse=True)

        return results[:max_results]

    def recommend_similar(
        self, target_recipe_id: str, max_results: int = 5
    ) -> List[RecommendationResult]:
        """
        類似レシピを推薦

        Args:
          target_recipe_id: 対象レシピID
          max_results: 最大結果数

        Returns:
          推薦結果リスト（類似度降順）
        """
        # 対象レシピを検索
        target_recipe = None
        for recipe in self.recipes:
            if recipe.get("id") == target_recipe_id:
                target_recipe = recipe
                break

        if not target_recipe:
            return []

        # 対象レシピの材料を取得
        target_ingredients = self._extract_recipe_ingredients(target_recipe)

        if not target_ingredients:
            return []

        # 正規化された材料セット
        normalized_target = {
            self.normalizer.normalize(ing) for ing in target_ingredients
        }

        results: List[RecommendationResult] = []

        for recipe in self.recipes:
            # 同じレシピはスキップ
            if recipe.get("id") == target_recipe_id:
                continue

            # レシピの材料を取得
            recipe_ingredients = self._extract_recipe_ingredients(recipe)

            if not recipe_ingredients:
                continue

            # マッチング計算
            result = self._calculate_match(
                recipe=recipe,
                recipe_ingredients=recipe_ingredients,
                available_ingredients=normalized_target,
            )

            results.append(result)

        # スコア降順でソート
        results.sort(key=lambda x: x.match_score, reverse=True)

        return results[:max_results]

    def what_can_i_make(
        self, available_ingredients: List[str], allow_missing: int = 2
    ) -> List[RecommendationResult]:
        """
        手持ち材料で作れるレシピを検索

        Args:
          available_ingredients: 手持ち材料リスト
          allow_missing: 許容する不足材料数

        Returns:
          推薦結果リスト（不足材料数昇順、スコア降順）
        """
        # 材料を正規化
        normalized_available = {
            self.normalizer.normalize(ing) for ing in available_ingredients
        }

        results: List[RecommendationResult] = []

        for recipe in self.recipes:
            # レシピの材料を取得
            recipe_ingredients = self._extract_recipe_ingredients(recipe)

            if not recipe_ingredients:
                continue

            # マッチング計算
            result = self._calculate_match(
                recipe=recipe,
                recipe_ingredients=recipe_ingredients,
                available_ingredients=normalized_available,
            )

            # 不足材料が許容範囲内なら追加
            if len(result.missing_ingredients) <= allow_missing:
                results.append(result)

        # 不足材料数昇順、スコア降順でソート
        results.sort(key=lambda x: (len(x.missing_ingredients), -x.match_score))

        return results

    def _extract_recipe_ingredients(self, recipe: Dict[str, Any]) -> List[str]:
        """
        レシピから材料リストを抽出

        Args:
          recipe: レシピデータ

        Returns:
          材料リスト
        """
        ingredients = []

        # レシピ構造に応じて材料を抽出
        if "ingredients" in recipe:
            ingredient_data = recipe["ingredients"]

            # リスト形式の場合
            if isinstance(ingredient_data, list):
                for item in ingredient_data:
                    if isinstance(item, str):
                        ingredients.append(item)
                    elif isinstance(item, dict) and "name" in item:
                        ingredients.append(item["name"])

            # 辞書形式の場合
            elif isinstance(ingredient_data, dict):
                for key, value in ingredient_data.items():
                    if isinstance(value, str):
                        ingredients.append(key)

        return ingredients

    def _calculate_match(
        self,
        recipe: Dict[str, Any],
        recipe_ingredients: List[str],
        available_ingredients: Set[str],
    ) -> RecommendationResult:
        """
        材料のマッチングスコアを計算

        Args:
          recipe: レシピデータ
          recipe_ingredients: レシピの材料リスト
          available_ingredients: 利用可能な材料セット（正規化済み）

        Returns:
          推薦結果
        """
        matched_ingredients: List[str] = []
        missing_ingredients: List[str] = []

        total_weight = 0.0
        matched_weight = 0.0

        for ingredient in recipe_ingredients:
            normalized = self.normalizer.normalize(ingredient)

            # 重み付け
            weight = (
                self.SEASONING_WEIGHT
                if self.normalizer.is_seasoning(normalized)
                else self.MAIN_INGREDIENT_WEIGHT
            )

            total_weight += weight

            if normalized in available_ingredients:
                matched_ingredients.append(ingredient)
                matched_weight += weight
            else:
                missing_ingredients.append(ingredient)

        # スコア計算
        match_score = matched_weight / total_weight if total_weight > 0 else 0.0

        # パーセンテージ計算
        match_percentage = (
            len(matched_ingredients) / len(recipe_ingredients) * 100
            if recipe_ingredients
            else 0.0
        )

        return RecommendationResult(
            recipe=recipe,
            match_score=round(match_score, 2),
            matched_ingredients=matched_ingredients,
            missing_ingredients=missing_ingredients,
            match_percentage=round(match_percentage, 1),
        )

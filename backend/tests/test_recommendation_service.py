"""
レシピ推薦サービスのテスト
"""

import pytest
from backend.services.recommendation_service import (
    RecommendationService,
    IngredientNormalizer,
)


# テスト用レシピデータ
TEST_RECIPES = [
    {
        "id": "test_001",
        "name": "カレーライス",
        "ingredients": [
            {"name": "たまねぎ", "amount": "2個"},
            {"name": "にんじん", "amount": "1本"},
            {"name": "じゃがいも", "amount": "3個"},
            {"name": "豚肉", "amount": "300g"},
            {"name": "カレールー", "amount": "1箱"},
            {"name": "サラダ油", "amount": "大さじ1"},
        ],
        "tags": ["洋食"],
    },
    {
        "id": "test_002",
        "name": "肉じゃが",
        "ingredients": [
            {"name": "じゃがいも", "amount": "4個"},
            {"name": "たまねぎ", "amount": "1個"},
            {"name": "にんじん", "amount": "1本"},
            {"name": "牛肉", "amount": "200g"},
            {"name": "醤油", "amount": "大さじ3"},
            {"name": "砂糖", "amount": "大さじ2"},
        ],
        "tags": ["和食"],
    },
    {
        "id": "test_003",
        "name": "野菜サラダ",
        "ingredients": [
            {"name": "レタス", "amount": "1/2個"},
            {"name": "とまと", "amount": "2個"},
            {"name": "きゅうり", "amount": "1本"},
            {"name": "塩", "amount": "少々"},
            {"name": "オリーブオイル", "amount": "大さじ1"},
        ],
        "tags": ["サラダ"],
    },
]


class TestIngredientNormalizer:
    """IngredientNormalizer のテスト"""

    def test_normalize_basic(self):
        """基本的な正規化のテスト"""
        assert IngredientNormalizer.normalize("玉ねぎ") == "たまねぎ"
        assert IngredientNormalizer.normalize("玉葱") == "たまねぎ"
        assert IngredientNormalizer.normalize("タマネギ") == "たまねぎ"

    def test_normalize_carrot(self):
        """にんじんの正規化"""
        assert IngredientNormalizer.normalize("人参") == "にんじん"
        assert IngredientNormalizer.normalize("ニンジン") == "にんじん"
        assert IngredientNormalizer.normalize("にんじん") == "にんじん"

    def test_normalize_potato(self):
        """じゃがいもの正規化"""
        assert IngredientNormalizer.normalize("じゃが芋") == "じゃがいも"
        assert IngredientNormalizer.normalize("ジャガイモ") == "じゃがいも"
        assert IngredientNormalizer.normalize("馬鈴薯") == "じゃがいも"

    def test_normalize_whitespace(self):
        """空白の処理"""
        assert IngredientNormalizer.normalize("  たまねぎ  ") == "たまねぎ"
        assert IngredientNormalizer.normalize(" にんじん ") == "にんじん"

    def test_is_seasoning(self):
        """調味料判定のテスト"""
        assert IngredientNormalizer.is_seasoning("塩") is True
        assert IngredientNormalizer.is_seasoning("砂糖") is True
        assert IngredientNormalizer.is_seasoning("醤油") is True
        assert IngredientNormalizer.is_seasoning("サラダ油") is True

        assert IngredientNormalizer.is_seasoning("たまねぎ") is False
        assert IngredientNormalizer.is_seasoning("にんじん") is False
        assert IngredientNormalizer.is_seasoning("豚肉") is False


class TestRecommendationService:
    """RecommendationService のテスト"""

    @pytest.fixture
    def service(self):
        """サービスインスタンスを作成"""
        return RecommendationService(recipes=TEST_RECIPES)

    def test_recommend_by_ingredients_perfect_match(self, service):
        """完全一致のテスト"""
        available = [
            "たまねぎ",
            "にんじん",
            "じゃがいも",
            "豚肉",
            "カレールー",
            "サラダ油",
        ]
        results = service.recommend_by_ingredients(available, min_score=0.0)

        assert len(results) > 0
        # カレーライスが最上位にくるはず
        assert results[0].recipe["id"] == "test_001"
        assert results[0].match_score > 0.9

    def test_recommend_by_ingredients_partial_match(self, service):
        """部分一致のテスト"""
        available = ["たまねぎ", "にんじん", "じゃがいも"]
        results = service.recommend_by_ingredients(available, min_score=0.0)

        # カレーライス（test_001）と肉じゃが（test_002）がマッチするはず
        assert len(results) >= 1
        # 一致する材料があるレシピが返される
        for result in results:
            if result.match_score > 0:
                assert len(result.matched_ingredients) > 0

    def test_recommend_by_ingredients_min_score_filter(self, service):
        """最小スコアフィルタのテスト"""
        available = ["たまねぎ"]
        results_low = service.recommend_by_ingredients(available, min_score=0.0)
        results_high = service.recommend_by_ingredients(available, min_score=0.8)

        # 低いスコアでは結果が多い
        assert len(results_low) >= len(results_high)

    def test_recommend_by_ingredients_max_results(self, service):
        """最大結果数のテスト"""
        available = ["たまねぎ", "にんじん"]
        results = service.recommend_by_ingredients(available, max_results=1)

        assert len(results) <= 1

    def test_recommend_by_ingredients_normalization(self, service):
        """正規化が機能するかテスト"""
        # 正規化前の材料名を使用
        available = ["玉ねぎ", "人参", "じゃが芋"]
        results = service.recommend_by_ingredients(available, min_score=0.0)

        assert len(results) > 0
        # 正規化されて一致するはず

    def test_recommend_similar(self, service):
        """類似レシピ推薦のテスト"""
        results = service.recommend_similar("test_001", max_results=5)

        assert len(results) > 0
        # カレーライス自身は含まれない
        for result in results:
            assert result.recipe["id"] != "test_001"

    def test_recommend_similar_not_found(self, service):
        """存在しないレシピIDのテスト"""
        results = service.recommend_similar("invalid_id", max_results=5)
        assert len(results) == 0

    def test_what_can_i_make_no_missing(self, service):
        """不足材料なしで作れるレシピ検索"""
        available = ["レタス", "とまと", "きゅうり", "塩", "オリーブオイル"]
        results = service.what_can_i_make(available, allow_missing=0)

        assert len(results) > 0
        # 野菜サラダが含まれるはず
        salad_found = False
        for result in results:
            if result.recipe["id"] == "test_003":
                salad_found = True
                assert len(result.missing_ingredients) == 0
                break

        assert salad_found is True

    def test_what_can_i_make_with_missing(self, service):
        """不足材料ありで作れるレシピ検索"""
        available = ["たまねぎ", "にんじん"]
        results = service.what_can_i_make(available, allow_missing=5)

        assert len(results) > 0
        # 不足材料数でソートされているはず
        for i in range(len(results) - 1):
            assert len(results[i].missing_ingredients) <= len(
                results[i + 1].missing_ingredients
            )

    def test_extract_recipe_ingredients(self, service):
        """材料抽出のテスト"""
        ingredients = service._extract_recipe_ingredients(TEST_RECIPES[0])
        assert len(ingredients) == 6
        assert "たまねぎ" in ingredients

    def test_calculate_match(self, service):
        """マッチング計算のテスト"""
        recipe = TEST_RECIPES[0]
        recipe_ingredients = ["たまねぎ", "にんじん", "じゃがいも", "豚肉"]
        available = {"たまねぎ", "にんじん"}

        result = service._calculate_match(recipe, recipe_ingredients, available)

        assert result.recipe == recipe
        assert len(result.matched_ingredients) == 2
        assert len(result.missing_ingredients) == 2
        assert 0.0 <= result.match_score <= 1.0
        assert 0.0 <= result.match_percentage <= 100.0

    def test_seasoning_weight(self, service):
        """調味料の重み付けテスト"""
        # 主材料のみ
        recipe1 = {
            "id": "weight_test_1",
            "name": "テスト1",
            "ingredients": [
                {"name": "たまねぎ", "amount": "1個"},
                {"name": "にんじん", "amount": "1本"},
            ],
        }

        # 調味料を含む
        recipe2 = {
            "id": "weight_test_2",
            "name": "テスト2",
            "ingredients": [
                {"name": "たまねぎ", "amount": "1個"},
                {"name": "塩", "amount": "少々"},
            ],
        }

        service_test = RecommendationService([recipe1, recipe2])
        available = ["たまねぎ"]

        results = service_test.recommend_by_ingredients(available, min_score=0.0)

        # 調味料を含むレシピの方がスコアが高くなるはず
        recipe2_result = next(r for r in results if r.recipe["id"] == "weight_test_2")
        assert recipe2_result.match_score > 0.5

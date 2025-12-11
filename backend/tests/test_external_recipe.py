"""
外部レシピサービスのテスト
"""

import pytest
from bs4 import BeautifulSoup

from backend.services.external_recipe_service import (
    ExternalRecipeService,
    RecipeData,
)
from backend.services.recipe_parsers.cookpad_parser import CookpadParser
from backend.services.recipe_parsers.kurashiru_parser import KurashiruParser
from backend.services.recipe_parsers.delish_kitchen_parser import DelishKitchenParser
from backend.services.recipe_parsers.generic_recipe_parser import GenericRecipeParser


class TestRecipeData:
    """RecipeData クラスのテスト"""

    def test_init_basic(self):
        """基本的な初期化"""
        data = RecipeData(
            title="テストレシピ",
            ingredients=[{"name": "玉ねぎ", "amount": "1", "unit": "個"}],
            steps=["手順1", "手順2"],
        )

        assert data.title == "テストレシピ"
        assert len(data.ingredients) == 1
        assert len(data.steps) == 2
        assert data.tags == []

    def test_normalize_ingredients_katakana(self):
        """カタカナをひらがなに正規化"""
        data = RecipeData(
            title="テスト",
            ingredients=[{"name": "タマネギ", "amount": "1", "unit": "個"}],
            steps=["手順1"],
        )

        assert data.ingredients[0]["name"] == "たまねぎ"

    def test_to_dict(self):
        """辞書形式への変換"""
        data = RecipeData(
            title="テストレシピ",
            ingredients=[{"name": "玉ねぎ", "amount": "1", "unit": "個"}],
            steps=["手順1"],
            description="説明",
            servings="2人分",
            cooking_time="30分",
            image_url="https://example.com/image.jpg",
            source_url="https://example.com/recipe",
            tags=["和食"],
            author="作者名",
        )

        result = data.to_dict()

        assert result["title"] == "テストレシピ"
        assert result["description"] == "説明"
        assert result["servings"] == "2人分"
        assert result["cooking_time"] == "30分"
        assert result["image_url"] == "https://example.com/image.jpg"
        assert result["source_url"] == "https://example.com/recipe"
        assert result["tags"] == ["和食"]
        assert result["author"] == "作者名"


class TestCookpadParser:
    """Cookpad パーサーのテスト"""

    def test_can_parse(self):
        """URL判定"""
        parser = CookpadParser()
        assert parser.can_parse("https://cookpad.com/recipe/123")
        assert parser.can_parse("https://www.cookpad.com/recipe/123")
        assert not parser.can_parse("https://kurashiru.com/recipe/123")

    @pytest.mark.asyncio
    async def test_parse_json_ld(self):
        """JSON-LDからのパース"""
        parser = CookpadParser()
        html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@type": "Recipe",
          "name": "美味しいカレー",
          "description": "簡単カレー",
          "recipeIngredient": ["玉ねぎ 1個", "人参 1本"],
          "recipeInstructions": [
            {"@type": "HowToStep", "text": "玉ねぎを切る"},
            {"@type": "HowToStep", "text": "煮込む"}
          ],
          "totalTime": "PT30M",
          "recipeYield": "4人分",
          "image": "https://example.com/image.jpg",
          "author": {"@type": "Person", "name": "料理人"}
        }
        </script>
      </head>
    </html>
    """

        result = await parser.parse(html, "https://cookpad.com/recipe/123")

        assert result.title == "美味しいカレー"
        assert result.description == "簡単カレー"
        assert len(result.ingredients) == 2
        assert result.ingredients[0]["name"] == "玉ねぎ"
        assert result.ingredients[0]["amount"] == "1"
        assert result.ingredients[0]["unit"] == "個"
        assert len(result.steps) == 2
        assert result.cooking_time == "30分"
        assert result.servings == "4人分"
        assert result.image_url == "https://example.com/image.jpg"
        assert result.author == "料理人"

    def test_parse_ingredient(self):
        """材料テキストのパース"""
        parser = CookpadParser()

        result = parser._parse_ingredient("玉ねぎ 1個")
        assert result["name"] == "玉ねぎ"
        assert result["amount"] == "1"
        assert result["unit"] == "個"

        result = parser._parse_ingredient("砂糖 大さじ2")
        assert result["name"] == "砂糖"
        assert result["amount"] == "2"
        assert result["unit"] == "大さじ"

        result = parser._parse_ingredient("塩 適量")
        assert result["name"] == "塩"
        assert result["amount"] == ""
        assert result["unit"] == "適量"

    def test_parse_duration(self):
        """時間のパース"""
        parser = CookpadParser()

        assert parser._parse_duration("PT30M") == "30分"
        assert parser._parse_duration("PT1H") == "1時間"
        assert parser._parse_duration("") == ""


class TestKurashiruParser:
    """クラシル パーサーのテスト"""

    def test_can_parse(self):
        """URL判定"""
        parser = KurashiruParser()
        assert parser.can_parse("https://kurashiru.com/recipe/123")
        assert parser.can_parse("https://www.kurashiru.com/recipe/123")
        assert not parser.can_parse("https://cookpad.com/recipe/123")

    def test_parse_duration_complex(self):
        """複雑な時間のパース"""
        parser = KurashiruParser()

        assert parser._parse_duration("PT1H30M") == "1時間30分"
        assert parser._parse_duration("PT45M") == "45分"
        assert parser._parse_duration("PT2H") == "2時間"


class TestDelishKitchenParser:
    """DELISH KITCHEN パーサーのテスト"""

    def test_can_parse(self):
        """URL判定"""
        parser = DelishKitchenParser()
        assert parser.can_parse("https://delishkitchen.tv/recipe/123")
        assert parser.can_parse("https://www.delishkitchen.tv/recipe/123")
        assert not parser.can_parse("https://cookpad.com/recipe/123")

    def test_parse_ingredient_with_units(self):
        """単位付き材料のパース"""
        parser = DelishKitchenParser()

        result = parser._parse_ingredient("鶏もも肉 300g")
        assert result["name"] == "鶏もも肉"
        assert result["amount"] == "300"
        assert result["unit"] == "g"

        result = parser._parse_ingredient("水 200ml")
        assert result["name"] == "水"
        assert result["amount"] == "200"
        assert result["unit"] == "ml"


class TestGenericRecipeParser:
    """汎用パーサーのテスト"""

    def test_can_parse(self):
        """常に True を返す"""
        parser = GenericRecipeParser()
        assert parser.can_parse("https://any-site.com/recipe")

    @pytest.mark.asyncio
    async def test_parse_json_ld_with_graph(self):
        """@graph 形式の JSON-LD をパース"""
        parser = GenericRecipeParser()
        html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@graph": [
            {"@type": "WebSite"},
            {
              "@type": "Recipe",
              "name": "汎用レシピ",
              "recipeIngredient": ["材料1", "材料2"],
              "recipeInstructions": "手順を説明"
            }
          ]
        }
        </script>
      </head>
    </html>
    """

        result = await parser.parse(html, "https://example.com/recipe")

        assert result.title == "汎用レシピ"
        assert len(result.ingredients) == 2
        assert len(result.steps) == 1

    def test_extract_title(self):
        """タイトル抽出"""
        parser = GenericRecipeParser()
        html = "<html><head><title>テストレシピ</title></head></html>"
        soup = BeautifulSoup(html, "html.parser")

        title = parser._extract_title(soup)
        assert title == "テストレシピ"

    def test_extract_title_from_h1(self):
        """h1からタイトル抽出"""
        parser = GenericRecipeParser()
        html = "<html><body><h1>メインタイトル</h1></body></html>"
        soup = BeautifulSoup(html, "html.parser")

        title = parser._extract_title(soup)
        assert title == "メインタイトル"

    def test_extract_title_from_og(self):
        """OGタグからタイトル抽出"""
        parser = GenericRecipeParser()
        html = """
    <html>
      <head>
        <meta property="og:title" content="OGタイトル">
      </head>
    </html>
    """
        soup = BeautifulSoup(html, "html.parser")

        title = parser._extract_title(soup)
        assert title == "OGタイトル"


class TestExternalRecipeService:
    """ExternalRecipeService のテスト"""

    def test_init(self):
        """初期化"""
        service = ExternalRecipeService()
        assert len(service.parsers) > 0

    def test_get_parser_cookpad(self):
        """Cookpad パーサーを取得"""
        service = ExternalRecipeService()
        parser = service.get_parser("https://cookpad.com/recipe/123")
        assert isinstance(parser, CookpadParser)

    def test_get_parser_kurashiru(self):
        """クラシル パーサーを取得"""
        service = ExternalRecipeService()
        parser = service.get_parser("https://kurashiru.com/recipe/123")
        assert isinstance(parser, KurashiruParser)

    def test_get_parser_delish_kitchen(self):
        """DELISH KITCHEN パーサーを取得"""
        service = ExternalRecipeService()
        parser = service.get_parser("https://delishkitchen.tv/recipe/123")
        assert isinstance(parser, DelishKitchenParser)

    def test_get_parser_generic(self):
        """汎用パーサーを取得（フォールバック）"""
        service = ExternalRecipeService()
        parser = service.get_parser("https://unknown-site.com/recipe")
        assert isinstance(parser, GenericRecipeParser)

    def test_validate_url(self):
        """URL検証"""
        service = ExternalRecipeService()

        assert service.validate_url("https://example.com/recipe")
        assert service.validate_url("http://example.com/recipe")
        assert not service.validate_url("not-a-url")
        assert not service.validate_url("")

    def test_get_supported_sites(self):
        """対応サイト一覧を取得"""
        service = ExternalRecipeService()
        sites = service.get_supported_sites()

        assert len(sites) > 0
        assert all("name" in site for site in sites)
        assert all("domain" in site for site in sites)

    @pytest.mark.asyncio
    async def test_import_recipe_success(self):
        """レシピインポート成功"""
        service = ExternalRecipeService()
        html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@type": "Recipe",
          "name": "テストレシピ",
          "recipeIngredient": ["材料1"],
          "recipeInstructions": "手順1"
        }
        </script>
      </head>
    </html>
    """

        result = await service.import_recipe("https://cookpad.com/recipe/123", html)

        assert result.title == "テストレシピ"
        assert len(result.ingredients) == 1
        assert len(result.steps) == 1

    @pytest.mark.asyncio
    async def test_import_recipe_unsupported_url(self):
        """サポートされていないURLでエラー"""
        service = ExternalRecipeService()
        service.parsers = []  # すべてのパーサーを削除

        with pytest.raises(ValueError, match="Unsupported URL"):
            await service.import_recipe("https://example.com", "<html></html>")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
外部レシピサービス

レシピサイトからのデータ取得と正規化を行う
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class RecipeData:
    """レシピデータの標準化クラス"""

    def __init__(
        self,
        title: str,
        ingredients: List[Dict[str, Any]],
        steps: List[str],
        description: Optional[str] = None,
        servings: Optional[str] = None,
        cooking_time: Optional[str] = None,
        image_url: Optional[str] = None,
        source_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
    ):
        self.title = title
        self.ingredients = self._normalize_ingredients(ingredients)
        self.steps = steps
        self.description = description
        self.servings = servings
        self.cooking_time = cooking_time
        self.image_url = image_url
        self.source_url = source_url
        self.tags = tags or []
        self.author = author

    def _normalize_ingredients(
        self, ingredients: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """材料名を正規化"""
        normalized = []
        for ingredient in ingredients:
            name = ingredient.get("name", "")
            # カタカナをひらがなに統一
            name = self._katakana_to_hiragana(name)
            normalized.append(
                {
                    "name": name,
                    "amount": ingredient.get("amount", ""),
                    "unit": ingredient.get("unit", ""),
                }
            )
        return normalized

    @staticmethod
    def _katakana_to_hiragana(text: str) -> str:
        """カタカナをひらがなに変換"""
        result = []
        for char in text:
            code = ord(char)
            if 0x30A1 <= code <= 0x30F6:  # カタカナ範囲
                result.append(chr(code - 0x60))
            else:
                result.append(char)
        return "".join(result)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "title": self.title,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "description": self.description,
            "servings": self.servings,
            "cooking_time": self.cooking_time,
            "image_url": self.image_url,
            "source_url": self.source_url,
            "tags": self.tags,
            "author": self.author,
        }


class RecipeParser(ABC):
    """レシピパーサー基底クラス"""

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def can_parse(self, url: str) -> bool:
        """このパーサーが対応できるURLか判定"""
        pass

    @abstractmethod
    async def parse(self, html: str, url: str) -> RecipeData:
        """HTMLからレシピデータを抽出"""
        pass

    def extract_domain(self, url: str) -> str:
        """URLからドメイン名を抽出"""
        parsed = urlparse(url)
        return parsed.netloc.lower()


class ExternalRecipeService:
    """外部レシピサービス管理クラス"""

    def __init__(self):
        self.parsers: List[RecipeParser] = []
        self._register_parsers()

    def _register_parsers(self):
        """パーサーを登録"""
        from backend.services.recipe_parsers.cookpad_parser import CookpadParser
        from backend.services.recipe_parsers.kurashiru_parser import KurashiruParser
        from backend.services.recipe_parsers.delish_kitchen_parser import (
            DelishKitchenParser,
        )
        from backend.services.recipe_parsers.generic_recipe_parser import (
            GenericRecipeParser,
        )

        self.parsers = [
            CookpadParser(),
            KurashiruParser(),
            DelishKitchenParser(),
            GenericRecipeParser(),  # 最後にフォールバック
        ]

    def get_parser(self, url: str) -> Optional[RecipeParser]:
        """URLに適したパーサーを取得"""
        for parser in self.parsers:
            if parser.can_parse(url):
                logger.info(f"Parser selected: {parser.name} for URL: {url}")
                return parser
        logger.warning(f"No parser found for URL: {url}")
        return None

    async def import_recipe(self, url: str, html: str) -> RecipeData:
        """URLからレシピをインポート"""
        parser = self.get_parser(url)
        if not parser:
            raise ValueError(f"Unsupported URL: {url}")

        try:
            recipe_data = await parser.parse(html, url)
            logger.info(f"Successfully parsed recipe: {recipe_data.title}")
            return recipe_data
        except Exception as e:
            logger.error(f"Failed to parse recipe from {url}: {str(e)}", exc_info=True)
            raise

    def get_supported_sites(self) -> List[Dict[str, str]]:
        """対応サイト一覧を取得"""
        sites = []
        for parser in self.parsers:
            if hasattr(parser, "site_info"):
                sites.append(parser.site_info())
        return sites

    def validate_url(self, url: str) -> bool:
        """URLの妥当性を検証"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

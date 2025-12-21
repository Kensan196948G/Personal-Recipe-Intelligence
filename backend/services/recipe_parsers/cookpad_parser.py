"""
Cookpad パーサー

Cookpad レシピページからデータを抽出
"""

import re
import json
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import logging

from backend.services.external_recipe_service import RecipeParser, RecipeData

logger = logging.getLogger(__name__)


class CookpadParser(RecipeParser):
    """Cookpad レシピパーサー"""

    def can_parse(self, url: str) -> bool:
        """Cookpad URLか判定"""
        domain = self.extract_domain(url)
        return "cookpad.com" in domain

    async def parse(self, html: str, url: str) -> RecipeData:
        """Cookpad HTMLを解析"""
        soup = BeautifulSoup(html, "html.parser")

        # JSON-LD から構造化データを取得
        recipe_data = self._extract_json_ld(soup)
        if recipe_data:
            return self._parse_json_ld(recipe_data, url)

        # フォールバック: HTML から直接抽出
        return self._parse_html(soup, url)

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """JSON-LD 構造化データを抽出"""
        try:
            script_tag = soup.find("script", type="application/ld+json")
            if script_tag:
                data = json.loads(script_tag.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") == "Recipe":
                            return item
                elif data.get("@type") == "Recipe":
                    return data
        except Exception as e:
            logger.warning(f"Failed to extract JSON-LD: {e}")
        return None

    def _parse_json_ld(self, data: Dict[str, Any], url: str) -> RecipeData:
        """JSON-LD データから RecipeData を生成"""
        # 材料を解析
        ingredients = []
        for ingredient_text in data.get("recipeIngredient", []):
            parsed = self._parse_ingredient(ingredient_text)
            ingredients.append(parsed)

        # 手順を解析
        steps = []
        instructions = data.get("recipeInstructions", [])
        if isinstance(instructions, list):
            for step in instructions:
                if isinstance(step, dict):
                    steps.append(step.get("text", ""))
                else:
                    steps.append(str(step))
        elif isinstance(instructions, str):
            steps = [instructions]

        # 調理時間を解析
        cooking_time = self._parse_duration(data.get("totalTime", ""))

        return RecipeData(
            title=data.get("name", ""),
            ingredients=ingredients,
            steps=steps,
            description=data.get("description", ""),
            servings=str(data.get("recipeYield", "")),
            cooking_time=cooking_time,
            image_url=self._extract_image_url(data.get("image")),
            source_url=url,
            tags=data.get("keywords", "").split(",") if data.get("keywords") else [],
            author=self._extract_author(data.get("author")),
        )

    def _parse_html(self, soup: BeautifulSoup, url: str) -> RecipeData:
        """HTML から直接レシピデータを抽出"""
        # タイトル
        title_tag = soup.find("h1", class_="recipe-title")
        title = title_tag.get_text(strip=True) if title_tag else "無題のレシピ"

        # 材料
        ingredients = []
        ingredient_list = soup.find("div", id="ingredients_list")
        if ingredient_list:
            for item in ingredient_list.find_all("div", class_="ingredient_row"):
                name_tag = item.find("div", class_="ingredient_name")
                amount_tag = item.find("div", class_="ingredient_quantity")
                if name_tag:
                    ingredients.append(
                        {
                            "name": name_tag.get_text(strip=True),
                            "amount": (
                                amount_tag.get_text(strip=True) if amount_tag else ""
                            ),
                            "unit": "",
                        }
                    )

        # 手順
        steps = []
        steps_list = soup.find("div", id="steps")
        if steps_list:
            for step in steps_list.find_all("div", class_="step"):
                step_text = step.find("p")
                if step_text:
                    steps.append(step_text.get_text(strip=True))

        # 画像
        image_url = None
        image_tag = soup.find("img", id="main_photo")
        if image_tag:
            image_url = image_tag.get("src")

        # 説明
        description_tag = soup.find("div", id="description")
        description = description_tag.get_text(strip=True) if description_tag else None

        return RecipeData(
            title=title,
            ingredients=ingredients,
            steps=steps,
            description=description,
            image_url=image_url,
            source_url=url,
            tags=["cookpad"],
        )

    def _parse_ingredient(self, text: str) -> Dict[str, str]:
        """材料テキストを解析"""
        # 例: "玉ねぎ 1個", "砂糖 大さじ2"
        match = re.match(r"^(.+?)\s+(.+)$", text.strip())
        if match:
            name = match.group(1)
            amount_text = match.group(2)

            # 単位を抽出
            unit_match = re.search(
                r"(個|本|枚|g|kg|ml|cc|カップ|大さじ|小さじ|適量)", amount_text
            )
            if unit_match:
                unit = unit_match.group(1)
                amount = amount_text.replace(unit, "").strip()
            else:
                unit = ""
                amount = amount_text

            return {"name": name, "amount": amount, "unit": unit}
        else:
            return {"name": text, "amount": "", "unit": ""}

    def _parse_duration(self, duration: str) -> str:
        """ISO 8601 duration を分に変換"""
        # 例: PT30M -> 30分
        if not duration:
            return ""

        match = re.search(r"PT(\d+)M", duration)
        if match:
            return f"{match.group(1)}分"

        match = re.search(r"PT(\d+)H", duration)
        if match:
            return f"{match.group(1)}時間"

        return duration

    def _extract_image_url(self, image_data: Any) -> Optional[str]:
        """画像URLを抽出"""
        if isinstance(image_data, str):
            return image_data
        elif isinstance(image_data, dict):
            return image_data.get("url")
        elif isinstance(image_data, list) and len(image_data) > 0:
            return (
                image_data[0]
                if isinstance(image_data[0], str)
                else image_data[0].get("url")
            )
        return None

    def _extract_author(self, author_data: Any) -> Optional[str]:
        """著者名を抽出"""
        if isinstance(author_data, str):
            return author_data
        elif isinstance(author_data, dict):
            return author_data.get("name")
        return None

    def site_info(self) -> Dict[str, str]:
        """サイト情報を返す"""
        return {
            "name": "Cookpad",
            "domain": "cookpad.com",
            "icon": "🍳",
        }

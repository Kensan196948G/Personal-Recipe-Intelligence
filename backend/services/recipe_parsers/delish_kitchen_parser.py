"""
DELISH KITCHEN パーサー

DELISH KITCHEN レシピページからデータを抽出
"""

import re
import json
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import logging

from backend.services.external_recipe_service import RecipeParser, RecipeData

logger = logging.getLogger(__name__)


class DelishKitchenParser(RecipeParser):
    """DELISH KITCHEN レシピパーサー"""

    def can_parse(self, url: str) -> bool:
        """DELISH KITCHEN URLか判定"""
        domain = self.extract_domain(url)
        return "delishkitchen.tv" in domain

    async def parse(self, html: str, url: str) -> RecipeData:
        """DELISH KITCHEN HTMLを解析"""
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
            scripts = soup.find_all("script", type="application/ld+json")
            for script_tag in scripts:
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
                    # HowToStep 形式
                    text = step.get("text") or step.get("name", "")
                    if text:
                        steps.append(text)
                else:
                    steps.append(str(step))
        elif isinstance(instructions, str):
            steps = [instructions]

        # 調理時間
        cook_time = self._parse_duration(data.get("cookTime", ""))
        prep_time = self._parse_duration(data.get("prepTime", ""))
        total_time = self._parse_duration(data.get("totalTime", ""))

        cooking_time = total_time or (
            f"{prep_time} + {cook_time}" if prep_time and cook_time else cook_time
        )

        # カテゴリー・キーワード
        tags = []
        if data.get("recipeCategory"):
            tags.append(data["recipeCategory"])
        if data.get("keywords"):
            keywords = data["keywords"]
            if isinstance(keywords, str):
                tags.extend([k.strip() for k in keywords.split(",")])
            elif isinstance(keywords, list):
                tags.extend(keywords)

        return RecipeData(
            title=data.get("name", ""),
            ingredients=ingredients,
            steps=steps,
            description=data.get("description", ""),
            servings=str(data.get("recipeYield", "")),
            cooking_time=cooking_time,
            image_url=self._extract_image_url(data.get("image")),
            source_url=url,
            tags=tags,
            author=self._extract_author(data.get("author")),
        )

    def _parse_html(self, soup: BeautifulSoup, url: str) -> RecipeData:
        """HTML から直接レシピデータを抽出"""
        # タイトル
        title_tag = soup.find("h1", class_="recipe-title") or soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "無題のレシピ"

        # 材料
        ingredients = []
        ingredient_section = soup.find("div", class_="ingredients") or soup.find(
            "section", class_="recipe-ingredients"
        )
        if ingredient_section:
            for item in ingredient_section.find_all("li"):
                text = item.get_text(strip=True)
                parsed = self._parse_ingredient(text)
                ingredients.append(parsed)

        # 手順
        steps = []
        steps_section = soup.find("div", class_="recipe-steps") or soup.find(
            "section", class_="instructions"
        )
        if steps_section:
            for step in steps_section.find_all("li"):
                step_text = step.get_text(strip=True)
                # 手順番号を削除
                step_text = re.sub(r"^\d+\.\s*", "", step_text)
                steps.append(step_text)

        # 画像
        image_url = None
        image_tag = soup.find("img", class_="recipe-image") or soup.find(
            "meta", property="og:image"
        )
        if image_tag:
            image_url = image_tag.get("src") or image_tag.get("content")

        # 説明
        description_tag = soup.find("p", class_="description") or soup.find(
            "meta", property="og:description"
        )
        description = None
        if description_tag:
            description = (
                description_tag.get_text(strip=True)
                if hasattr(description_tag, "get_text")
                else description_tag.get("content")
            )

        return RecipeData(
            title=title,
            ingredients=ingredients,
            steps=steps,
            description=description,
            image_url=image_url,
            source_url=url,
            tags=["delish-kitchen"],
        )

    def _parse_ingredient(self, text: str) -> Dict[str, str]:
        """材料テキストを解析"""
        # 例: "玉ねぎ 1個", "砂糖 大さじ2", "塩 少々"
        match = re.match(r"^(.+?)\s+(.+)$", text.strip())
        if match:
            name = match.group(1)
            amount_text = match.group(2)

            # 単位を抽出
            unit_match = re.search(
                r"(個|本|枚|片|切れ|g|kg|ml|L|dl|cc|カップ|大さじ|小さじ|適量|少々|ひとつまみ)",
                amount_text,
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
        if not duration:
            return ""

        # PT30M -> 30分
        match = re.search(r"PT(\d+)M", duration)
        if match:
            return f"{match.group(1)}分"

        # PT1H -> 1時間
        match = re.search(r"PT(\d+)H", duration)
        if match:
            return f"{match.group(1)}時間"

        # PT1H30M -> 1時間30分
        match = re.search(r"PT(\d+)H(\d+)M", duration)
        if match:
            return f"{match.group(1)}時間{match.group(2)}分"

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
            "name": "DELISH KITCHEN",
            "domain": "delishkitchen.tv",
            "icon": "🍽️",
        }

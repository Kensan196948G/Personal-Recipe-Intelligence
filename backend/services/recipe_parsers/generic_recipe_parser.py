"""
汎用レシピパーサー

Schema.org Recipe 構造化データに対応した汎用パーサー
"""

import re
import json
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import logging

from backend.services.external_recipe_service import RecipeParser, RecipeData

logger = logging.getLogger(__name__)


class GenericRecipeParser(RecipeParser):
    """汎用レシピパーサー（Schema.org Recipe 対応）"""

    def can_parse(self, url: str) -> bool:
        """常に True を返す（フォールバックパーサー）"""
        return True

    async def parse(self, html: str, url: str) -> RecipeData:
        """HTMLを解析してレシピデータを抽出"""
        soup = BeautifulSoup(html, "html.parser")

        # JSON-LD から構造化データを取得
        recipe_data = self._extract_json_ld(soup)
        if recipe_data:
            logger.info(f"Found Schema.org Recipe data in {url}")
            return self._parse_json_ld(recipe_data, url)

        # マイクロデータから抽出を試みる
        recipe_data = self._extract_microdata(soup)
        if recipe_data:
            logger.info(f"Found microdata Recipe data in {url}")
            return self._parse_json_ld(recipe_data, url)

        # フォールバック: ヒューリスティック解析
        logger.warning(f"No structured data found, using heuristic parsing for {url}")
        return self._parse_heuristic(soup, url)

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """JSON-LD 構造化データを抽出"""
        try:
            scripts = soup.find_all("script", type="application/ld+json")
            for script_tag in scripts:
                if not script_tag.string:
                    continue

                data = json.loads(script_tag.string)

                # Recipe タイプを探す
                if isinstance(data, list):
                    for item in data:
                        if self._is_recipe_type(item):
                            return item
                elif self._is_recipe_type(data):
                    return data
                # @graph 形式
                elif data.get("@graph"):
                    for item in data["@graph"]:
                        if self._is_recipe_type(item):
                            return item
        except Exception as e:
            logger.warning(f"Failed to extract JSON-LD: {e}")
        return None

    def _is_recipe_type(self, data: Dict[str, Any]) -> bool:
        """Recipe タイプか判定"""
        type_val = data.get("@type", "")
        if isinstance(type_val, str):
            return type_val == "Recipe"
        elif isinstance(type_val, list):
            return "Recipe" in type_val
        return False

    def _extract_microdata(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """マイクロデータから Recipe を抽出"""
        try:
            recipe_tag = soup.find(attrs={"itemtype": re.compile(r".*Recipe")})
            if not recipe_tag:
                return None

            data = {}

            # name
            name_tag = recipe_tag.find(attrs={"itemprop": "name"})
            if name_tag:
                data["name"] = name_tag.get_text(strip=True)

            # description
            desc_tag = recipe_tag.find(attrs={"itemprop": "description"})
            if desc_tag:
                data["description"] = desc_tag.get_text(strip=True)

            # image
            image_tag = recipe_tag.find(attrs={"itemprop": "image"})
            if image_tag:
                data["image"] = image_tag.get("src") or image_tag.get("content")

            # recipeIngredient
            ingredients = []
            for ingredient_tag in recipe_tag.find_all(
                attrs={"itemprop": "recipeIngredient"}
            ):
                ingredients.append(ingredient_tag.get_text(strip=True))
            if ingredients:
                data["recipeIngredient"] = ingredients

            # recipeInstructions
            instructions = []
            for step_tag in recipe_tag.find_all(
                attrs={"itemprop": "recipeInstructions"}
            ):
                instructions.append(step_tag.get_text(strip=True))
            if instructions:
                data["recipeInstructions"] = instructions

            # recipeYield
            yield_tag = recipe_tag.find(attrs={"itemprop": "recipeYield"})
            if yield_tag:
                data["recipeYield"] = yield_tag.get_text(strip=True)

            return data if data else None
        except Exception as e:
            logger.warning(f"Failed to extract microdata: {e}")
        return None

    def _parse_json_ld(self, data: Dict[str, Any], url: str) -> RecipeData:
        """構造化データから RecipeData を生成"""
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
                    # HowToStep / HowToSection
                    if step.get("@type") == "HowToSection":
                        for item in step.get("itemListElement", []):
                            text = item.get("text", "")
                            if text:
                                steps.append(text)
                    else:
                        text = step.get("text", "")
                        if text:
                            steps.append(text)
                else:
                    steps.append(str(step))
        elif isinstance(instructions, str):
            # 改行で分割
            steps = [s.strip() for s in instructions.split("\n") if s.strip()]

        # 調理時間
        cook_time = self._parse_duration(data.get("cookTime", ""))
        prep_time = self._parse_duration(data.get("prepTime", ""))
        total_time = self._parse_duration(data.get("totalTime", ""))

        cooking_time = total_time or (
            f"{prep_time} + {cook_time}" if prep_time and cook_time else cook_time
        )

        # タグ
        tags = []
        if data.get("recipeCategory"):
            category = data["recipeCategory"]
            if isinstance(category, list):
                tags.extend(category)
            else:
                tags.append(category)
        if data.get("recipeCuisine"):
            cuisine = data["recipeCuisine"]
            if isinstance(cuisine, list):
                tags.extend(cuisine)
            else:
                tags.append(cuisine)
        if data.get("keywords"):
            keywords = data["keywords"]
            if isinstance(keywords, str):
                tags.extend([k.strip() for k in keywords.split(",")])
            elif isinstance(keywords, list):
                tags.extend(keywords)

        return RecipeData(
            title=data.get("name", "無題のレシピ"),
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

    def _parse_heuristic(self, soup: BeautifulSoup, url: str) -> RecipeData:
        """ヒューリスティック解析（フォールバック）"""
        # タイトル
        title = self._extract_title(soup)

        # 説明
        description = self._extract_description(soup)

        # 画像
        image_url = self._extract_image(soup)

        # 材料（ヒューリスティック）
        ingredients = self._extract_ingredients_heuristic(soup)

        # 手順（ヒューリスティック）
        steps = self._extract_steps_heuristic(soup)

        return RecipeData(
            title=title,
            ingredients=ingredients,
            steps=steps,
            description=description,
            image_url=image_url,
            source_url=url,
            tags=["imported"],
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """タイトルを抽出"""
        # h1 タグ
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        # og:title
        og_title = soup.find("meta", property="og:title")
        if og_title:
            return og_title.get("content", "無題のレシピ")

        # title タグ
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        return "無題のレシピ"

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """説明を抽出"""
        # og:description
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            return og_desc.get("content")

        # meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            return meta_desc.get("content")

        return None

    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """画像URLを抽出"""
        # og:image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            return og_image.get("content")

        # 最初の大きい画像
        images = soup.find_all("img")
        for img in images:
            src = img.get("src")
            if src and not any(
                x in src.lower() for x in ["icon", "logo", "avatar", "banner"]
            ):
                return src

        return None

    def _extract_ingredients_heuristic(
        self, soup: BeautifulSoup
    ) -> List[Dict[str, str]]:
        """ヒューリスティックに材料を抽出"""
        ingredients = []

        # "材料" "ingredients" などのキーワードを含むセクションを探す
        keywords = ["材料", "ingredients", "ingredient", "材"]
        for keyword in keywords:
            sections = soup.find_all(
                ["div", "section", "ul"],
                class_=re.compile(keyword, re.IGNORECASE),
            )
            sections.extend(
                soup.find_all(
                    ["div", "section", "ul"], id=re.compile(keyword, re.IGNORECASE)
                )
            )

            for section in sections:
                items = section.find_all("li")
                if not items:
                    items = section.find_all("p")

                for item in items:
                    text = item.get_text(strip=True)
                    if text and len(text) < 100:  # 長すぎるものは除外
                        parsed = self._parse_ingredient(text)
                        if parsed not in ingredients:
                            ingredients.append(parsed)

                if ingredients:
                    break

        return ingredients

    def _extract_steps_heuristic(self, soup: BeautifulSoup) -> List[str]:
        """ヒューリスティックに手順を抽出"""
        steps = []

        # "作り方" "手順" "directions" などのキーワードを含むセクションを探す
        keywords = [
            "作り方",
            "手順",
            "directions",
            "instructions",
            "steps",
            "procedure",
        ]
        for keyword in keywords:
            sections = soup.find_all(
                ["div", "section", "ol"],
                class_=re.compile(keyword, re.IGNORECASE),
            )
            sections.extend(
                soup.find_all(
                    ["div", "section", "ol"], id=re.compile(keyword, re.IGNORECASE)
                )
            )

            for section in sections:
                items = section.find_all("li")
                if not items:
                    items = section.find_all("p")

                for item in items:
                    text = item.get_text(strip=True)
                    # 手順番号を削除
                    text = re.sub(r"^\d+\.\s*", "", text)
                    text = re.sub(r"^手順\s*\d+\s*", "", text)
                    if text and len(text) > 10:  # 短すぎるものは除外
                        steps.append(text)

                if steps:
                    break

        return steps

    def _parse_ingredient(self, text: str) -> Dict[str, str]:
        """材料テキストを解析"""
        # 例: "玉ねぎ 1個", "砂糖 大さじ2"
        match = re.match(r"^(.+?)\s+(.+)$", text.strip())
        if match:
            name = match.group(1)
            amount_text = match.group(2)

            # 単位を抽出
            unit_match = re.search(
                r"(個|本|枚|片|切れ|粒|g|kg|mg|ml|L|dl|cc|カップ|大さじ|小さじ|適量|少々|ひとつまみ)",
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
            "name": "Generic (Schema.org)",
            "domain": "*",
            "icon": "🌐",
        }

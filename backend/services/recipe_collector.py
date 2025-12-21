"""
Recipe Collector Service - 海外レシピ自動収集パイプライン
Spoonacular API → DeepL翻訳 → 正規化 → DB保存
"""

import os
import re
import logging
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from backend.models.recipe import Recipe, Ingredient, Step, Tag, RecipeTag
from backend.services.spoonacular_client import SpoonacularClient
from backend.services.deepl_translator import DeepLTranslator
from backend.services.image_download_service import ImageDownloadService

logger = logging.getLogger(__name__)


# 単位変換テーブル（US → メトリック）
UNIT_CONVERSIONS = {
    "cup": {"to": "ml", "factor": 240},
    "cups": {"to": "ml", "factor": 240},
    "tablespoon": {"to": "ml", "factor": 15},
    "tablespoons": {"to": "ml", "factor": 15},
    "tbsp": {"to": "ml", "factor": 15},
    "teaspoon": {"to": "ml", "factor": 5},
    "teaspoons": {"to": "ml", "factor": 5},
    "tsp": {"to": "ml", "factor": 5},
    "ounce": {"to": "g", "factor": 28.35},
    "ounces": {"to": "g", "factor": 28.35},
    "oz": {"to": "g", "factor": 28.35},
    "pound": {"to": "g", "factor": 453.6},
    "pounds": {"to": "g", "factor": 453.6},
    "lb": {"to": "g", "factor": 453.6},
    "lbs": {"to": "g", "factor": 453.6},
    "fluid ounce": {"to": "ml", "factor": 29.57},
    "fluid ounces": {"to": "ml", "factor": 29.57},
    "fl oz": {"to": "ml", "factor": 29.57},
    "pint": {"to": "ml", "factor": 473},
    "pints": {"to": "ml", "factor": 473},
    "quart": {"to": "ml", "factor": 946},
    "quarts": {"to": "ml", "factor": 946},
    "gallon": {"to": "l", "factor": 3.785},
    "gallons": {"to": "l", "factor": 3.785},
}

# 日本語単位マッピング
UNIT_JP_MAPPING = {
    "ml": "ml",
    "l": "L",
    "g": "g",
    "kg": "kg",
    "個": "個",
    "本": "本",
    "枚": "枚",
    "束": "束",
    "片": "片",
    "かけ": "かけ",
    "適量": "適量",
    "少々": "少々",
}


class RecipeCollector:
    """海外レシピ自動収集サービス"""

    def __init__(
        self,
        spoonacular_key: Optional[str] = None,
        deepl_key: Optional[str] = None,
        skip_translation: bool = False,
    ):
        self.spoonacular = SpoonacularClient(api_key=spoonacular_key)
        self.skip_translation = skip_translation
        self._translation_cache: dict[str, str] = {}
        self._translation_available = False

        # DeepL翻訳を試みる（キーがあれば）
        if deepl_key and not skip_translation:
            try:
                self.translator = DeepLTranslator(api_key=deepl_key)
                self._translation_available = True
            except Exception as e:
                logger.warning(f"DeepL translator initialization failed: {e}")
                self.translator = None
        else:
            self.translator = None

        # 画像ダウンロードサービス
        self.image_service = ImageDownloadService()

    def _translate_cached(self, text: str) -> str:
        """キャッシュを使った翻訳（翻訳不可の場合は原文を返す）"""
        if not text or not text.strip():
            return ""
        if not self._translation_available or not self.translator:
            return text
        if text in self._translation_cache:
            return self._translation_cache[text]
        try:
            translated = self.translator.translate(text, target_lang="JA", source_lang="EN")
            self._translation_cache[text] = translated
            return translated
        except Exception as e:
            logger.warning(f"Translation failed, using original: {e}")
            self._translation_available = False  # 以降は翻訳をスキップ
            return text

    def _translate_batch_cached(self, texts: list[str]) -> list[str]:
        """バッチ翻訳（キャッシュ対応、翻訳不可の場合は原文を返す）"""
        # 翻訳が利用不可の場合は原文をそのまま返す
        if not self._translation_available or not self.translator:
            return [t if t else "" for t in texts]

        # キャッシュにないものだけ翻訳
        to_translate = []
        indices = []
        results = [""] * len(texts)

        for i, text in enumerate(texts):
            if not text or not text.strip():
                results[i] = ""
            elif text in self._translation_cache:
                results[i] = self._translation_cache[text]
            else:
                to_translate.append(text)
                indices.append(i)

        if to_translate:
            try:
                translated = self.translator.translate_batch(
                    to_translate, target_lang="JA", source_lang="EN"
                )
                for idx, trans in zip(indices, translated):
                    self._translation_cache[texts[idx]] = trans
                    results[idx] = trans
            except Exception as e:
                logger.warning(f"Batch translation failed, using originals: {e}")
                self._translation_available = False  # 以降は翻訳をスキップ
                for idx, orig in zip(indices, to_translate):
                    results[idx] = orig

        return results

    def convert_unit(self, amount: float, unit: str) -> tuple[float, str]:
        """US単位をメトリック単位に変換"""
        unit_lower = unit.lower().strip()
        if unit_lower in UNIT_CONVERSIONS:
            conv = UNIT_CONVERSIONS[unit_lower]
            return round(amount * conv["factor"], 1), conv["to"]
        return amount, unit

    def normalize_ingredient_name(self, name: str) -> str:
        """材料名を正規化"""
        # 小文字化、余分な空白除去
        normalized = name.strip().lower()
        # 複数形の簡易正規化（英語）
        if normalized.endswith("ies"):
            normalized = normalized[:-3] + "y"
        elif normalized.endswith("es") and not normalized.endswith("ses"):
            normalized = normalized[:-2]
        elif normalized.endswith("s") and not normalized.endswith("ss"):
            normalized = normalized[:-1]
        return normalized

    def cleanse_ingredient(self, ingredient: dict) -> dict:
        """材料データをクレンジング"""
        name = ingredient.get("name", "")
        amount = ingredient.get("amount")
        unit = ingredient.get("unit", "")

        # 単位変換
        if amount and unit:
            amount, unit = self.convert_unit(float(amount), unit)

        # 名前正規化
        name_normalized = self.normalize_ingredient_name(name)

        return {
            "name": name,
            "name_normalized": name_normalized,
            "amount": amount,
            "unit": unit,
            "original_text": ingredient.get("original_text", ""),
        }

    def cleanse_step(self, step: dict) -> dict:
        """手順データをクレンジング"""
        description = step.get("description", "")
        # HTMLタグ除去
        description = re.sub(r"<[^>]+>", "", description)
        # 余分な空白除去
        description = " ".join(description.split())

        return {
            "description": description,
            "order": step.get("number", step.get("order", 1)),
        }

    def translate_recipe(self, recipe_data: dict) -> dict:
        """レシピデータを日本語に翻訳"""
        original = recipe_data.get("original_data", {})

        # タイトルと説明を翻訳
        title_en = original.get("title", "")
        summary_en = original.get("summary", "")

        # HTMLタグ除去（summaryにはHTMLが含まれることがある）
        summary_en = re.sub(r"<[^>]+>", "", summary_en)

        # バッチで翻訳
        title_ja, summary_ja = self._translate_batch_cached([title_en, summary_en])

        # 材料を翻訳
        ingredients = recipe_data.get("ingredients", [])
        ingredient_names = [ing.get("name", "") for ing in ingredients]
        ingredient_names_ja = self._translate_batch_cached(ingredient_names)

        translated_ingredients = []
        for ing, name_ja in zip(ingredients, ingredient_names_ja):
            cleansed = self.cleanse_ingredient(ing)
            cleansed["name"] = name_ja if name_ja else cleansed["name"]
            # 正規化名も日本語で再生成
            cleansed["name_normalized"] = self.normalize_ingredient_name(name_ja) if name_ja else cleansed["name_normalized"]
            translated_ingredients.append(cleansed)

        # 手順を翻訳
        steps = recipe_data.get("steps", [])
        step_descriptions = [step.get("description", "") for step in steps]
        step_descriptions_ja = self._translate_batch_cached(step_descriptions)

        translated_steps = []
        for step, desc_ja in zip(steps, step_descriptions_ja):
            cleansed = self.cleanse_step(step)
            cleansed["description"] = desc_ja if desc_ja else cleansed["description"]
            translated_steps.append(cleansed)

        # 料理ジャンル・タイプを翻訳（タグ用）
        cuisines = original.get("cuisines", [])
        dish_types = original.get("dish_types", [])
        diets = original.get("diets", [])
        all_tags = cuisines + dish_types + diets
        tags_ja = self._translate_batch_cached(all_tags) if all_tags else []

        return {
            "title": title_ja,
            "description": summary_ja[:500] if summary_ja else None,  # 長すぎる場合は切り詰め
            "servings": original.get("servings"),
            "prep_time_minutes": original.get("prep_time_minutes"),
            "cook_time_minutes": original.get("cook_time_minutes"),
            "source_url": recipe_data.get("source_url", ""),
            "source_type": "spoonacular",
            "image_url": original.get("image"),  # 画像URLを追加
            "ingredients": translated_ingredients,
            "steps": translated_steps,
            "tags": tags_ja,
            "source_id": recipe_data.get("source_id"),
        }

    async def save_recipe(self, session: Session, recipe_data: dict) -> dict:
        """レシピをデータベースに保存し、ID・タイトルを返す"""
        # 重複チェック（source_id で）
        source_id = recipe_data.get("source_id")
        if source_id:
            existing = session.exec(
                select(Recipe).where(
                    Recipe.source_url.contains(f"spoonacular.com")
                    if recipe_data.get("source_url")
                    else Recipe.title == recipe_data["title"]
                )
            ).first()
            if existing:
                logger.info(f"Recipe already exists: {recipe_data['title']}")
                return {"id": existing.id, "title": existing.title}

        # レシピ作成
        recipe = Recipe(
            title=recipe_data["title"],
            description=recipe_data.get("description"),
            servings=recipe_data.get("servings"),
            prep_time_minutes=recipe_data.get("prep_time_minutes"),
            cook_time_minutes=recipe_data.get("cook_time_minutes"),
            source_url=recipe_data.get("source_url"),
            source_type=recipe_data.get("source_type", "spoonacular"),
            source_id=recipe_data.get("source_id"),  # 外部APIのレシピID
            image_url=recipe_data.get("image_url"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(recipe)
        session.flush()  # IDを取得

        # 画像URLがあればダウンロードして保存（エラー時も処理を継続）
        image_url = recipe_data.get("image_url")
        if image_url:
            try:
                image_path = await self.image_service.download_and_save(
                    image_url, recipe.id
                )
                if image_path:
                    recipe.image_path = image_path
                    logger.info(f"Image saved for recipe {recipe.id}: {image_path}")
                else:
                    logger.warning(f"Failed to download image for recipe {recipe.id}")
            except Exception as e:
                logger.error(f"Error downloading image for recipe {recipe.id}: {e}")
                # 画像取得失敗でもレシピ保存は継続

        # 材料追加
        for i, ing_data in enumerate(recipe_data.get("ingredients", [])):
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=ing_data["name"],
                name_normalized=ing_data.get("name_normalized", ing_data["name"]),
                amount=ing_data.get("amount"),
                unit=ing_data.get("unit"),
                order=i,
            )
            session.add(ingredient)

        # 手順追加
        for step_data in recipe_data.get("steps", []):
            step = Step(
                recipe_id=recipe.id,
                description=step_data["description"],
                order=step_data.get("order", 1),
            )
            session.add(step)

        # タグ追加
        for tag_name in recipe_data.get("tags", []):
            if not tag_name or not tag_name.strip():
                continue
            # 既存タグを検索または作成
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()

            # レシピ-タグ関連
            recipe_tag = RecipeTag(recipe_id=recipe.id, tag_id=tag.id)
            session.add(recipe_tag)

        # コミット前にIDとタイトルを保存
        recipe_id = recipe.id
        recipe_title = recipe.title

        session.commit()
        logger.info(f"Saved recipe: {recipe_title} (ID: {recipe_id})")
        return {"id": recipe_id, "title": recipe_title}

    async def collect_random_recipes(
        self,
        session: Session,
        count: int = 5,
        tags: Optional[str] = None,
    ) -> list[dict]:
        """ランダムなレシピを収集して保存（ID・タイトルのリストを返す）"""
        logger.info(f"Collecting {count} random recipes...")

        # Spoonacularからレシピ取得
        raw_recipes = self.spoonacular.get_random_recipes(number=count, tags=tags)
        logger.info(f"Fetched {len(raw_recipes)} recipes from Spoonacular")

        saved_recipes = []
        for raw in raw_recipes:
            try:
                # データ抽出
                extracted = self.spoonacular.extract_recipe_data(raw)

                # 翻訳・正規化
                translated = self.translate_recipe(extracted)

                # 保存（辞書を返す）
                recipe_info = await self.save_recipe(session, translated)
                saved_recipes.append(recipe_info)

            except Exception as e:
                logger.error(f"Failed to process recipe: {raw.get('title', 'unknown')} - {e}")
                continue

        logger.info(f"Successfully saved {len(saved_recipes)} recipes")
        return saved_recipes

    async def collect_recipes_by_search(
        self,
        session: Session,
        query: str,
        count: int = 5,
        cuisine: Optional[str] = None,
    ) -> list[dict]:
        """検索でレシピを収集（ID・タイトルのリストを返す）"""
        logger.info(f"Searching recipes for: {query}")

        # 検索
        search_results = self.spoonacular.search_recipes(
            query=query,
            number=count,
            cuisine=cuisine,
        )

        saved_recipes = []
        for result in search_results:
            try:
                # 詳細情報を取得（検索結果には全情報が含まれない場合がある）
                recipe_id = result.get("id")
                if not recipe_id:
                    continue

                raw = self.spoonacular.get_recipe_information(recipe_id)
                extracted = self.spoonacular.extract_recipe_data(raw)
                translated = self.translate_recipe(extracted)
                recipe_info = await self.save_recipe(session, translated)
                saved_recipes.append(recipe_info)

            except Exception as e:
                logger.error(f"Failed to process recipe: {result.get('title', 'unknown')} - {e}")
                continue

        return saved_recipes

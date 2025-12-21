"""
Translation service for Personal Recipe Intelligence.

This module provides translation functionality using DeepL API with caching support.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import deepl

from backend.translation.models import (
    Language,
    RecipeTranslationResult,
    TranslationResult,
)

logger = logging.getLogger(__name__)


class TranslationCache:
    """In-memory cache for translations."""

    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize translation cache.

        Args:
          ttl_minutes: Time-to-live for cache entries in minutes
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def _generate_key(
        self, text: str, target_lang: str, source_lang: Optional[str] = None
    ) -> str:
        """
        Generate cache key from translation parameters.

        Args:
          text: Text to translate
          target_lang: Target language
          source_lang: Source language (optional)

        Returns:
          Cache key string
        """
        key_str = f"{text}|{target_lang}|{source_lang or 'auto'}"
        return hashlib.md5(key_str.encode("utf-8")).hexdigest()

    def get(
        self, text: str, target_lang: str, source_lang: Optional[str] = None
    ) -> Optional[str]:
        """
        Get cached translation if available and not expired.

        Args:
          text: Original text
          target_lang: Target language
          source_lang: Source language (optional)

        Returns:
          Cached translation or None
        """
        key = self._generate_key(text, target_lang, source_lang)
        entry = self._cache.get(key)

        if entry is None:
            return None

        if datetime.now() - entry["timestamp"] > self._ttl:
            del self._cache[key]
            return None

        return entry["translation"]

    def set(
        self,
        text: str,
        target_lang: str,
        translation: str,
        source_lang: Optional[str] = None,
    ) -> None:
        """
        Store translation in cache.

        Args:
          text: Original text
          target_lang: Target language
          translation: Translated text
          source_lang: Source language (optional)
        """
        key = self._generate_key(text, target_lang, source_lang)
        self._cache[key] = {
            "translation": translation,
            "timestamp": datetime.now(),
        }

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def get_size(self) -> int:
        """
        Get current cache size.

        Returns:
          Number of cached entries
        """
        return len(self._cache)


class TranslationService:
    """Service for translating text using DeepL API."""

    def __init__(self, api_key: str, cache_ttl_minutes: int = 60):
        """
        Initialize translation service.

        Args:
          api_key: DeepL API key
          cache_ttl_minutes: Cache TTL in minutes

        Raises:
          ValueError: If API key is empty
        """
        if not api_key:
            raise ValueError("DeepL API key is required")

        try:
            self._translator = deepl.Translator(api_key)
            self._cache = TranslationCache(ttl_minutes=cache_ttl_minutes)
            logger.info("Translation service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DeepL translator: {str(e)}")
            raise

    def translate(
        self,
        text: str,
        target_lang: Language,
        source_lang: Optional[Language] = None,
        use_cache: bool = True,
    ) -> TranslationResult:
        """
        Translate text to target language.

        Args:
          text: Text to translate
          target_lang: Target language
          source_lang: Source language (auto-detect if None)
          use_cache: Whether to use cache

        Returns:
          TranslationResult with translated text

        Raises:
          Exception: If translation fails
        """
        if not text or not text.strip():
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_lang=source_lang.value if source_lang else "auto",
                target_lang=target_lang.value,
                cached=False,
            )

        # Check cache first
        if use_cache:
            cached = self._cache.get(
                text,
                target_lang.value,
                source_lang.value if source_lang else None,
            )
            if cached:
                logger.debug(f"Cache hit for translation: {text[:50]}...")
                return TranslationResult(
                    original_text=text,
                    translated_text=cached,
                    source_lang=source_lang.value if source_lang else "auto",
                    target_lang=target_lang.value,
                    cached=True,
                )

        # Perform translation
        try:
            result = self._translator.translate_text(
                text,
                target_lang=target_lang.value,
                source_lang=source_lang.value if source_lang else None,
            )

            translated_text = result.text
            detected_source_lang = result.detected_source_lang

            # Store in cache
            if use_cache:
                self._cache.set(
                    text,
                    target_lang.value,
                    translated_text,
                    source_lang.value if source_lang else None,
                )

            logger.info(
                f"Translated text from {detected_source_lang} to {target_lang.value}: "
                f"{text[:50]}... -> {translated_text[:50]}..."
            )

            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_lang=detected_source_lang,
                target_lang=target_lang.value,
                cached=False,
            )

        except deepl.DeepLException as e:
            logger.error(f"DeepL API error: {str(e)}")
            raise Exception(f"Translation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during translation: {str(e)}")
            raise

    def translate_batch(
        self,
        texts: List[str],
        target_lang: Language,
        source_lang: Optional[Language] = None,
        use_cache: bool = True,
    ) -> List[TranslationResult]:
        """
        Translate multiple texts to target language.

        Args:
          texts: List of texts to translate
          target_lang: Target language
          source_lang: Source language (auto-detect if None)
          use_cache: Whether to use cache

        Returns:
          List of TranslationResult

        Raises:
          Exception: If translation fails
        """
        results = []
        uncached_texts = []
        uncached_indices = []

        # Check cache for each text
        for idx, text in enumerate(texts):
            if not text or not text.strip():
                results.append(
                    TranslationResult(
                        original_text=text,
                        translated_text=text,
                        source_lang=source_lang.value if source_lang else "auto",
                        target_lang=target_lang.value,
                        cached=False,
                    )
                )
                continue

            if use_cache:
                cached = self._cache.get(
                    text,
                    target_lang.value,
                    source_lang.value if source_lang else None,
                )
                if cached:
                    results.append(
                        TranslationResult(
                            original_text=text,
                            translated_text=cached,
                            source_lang=source_lang.value if source_lang else "auto",
                            target_lang=target_lang.value,
                            cached=True,
                        )
                    )
                    continue

            # Mark for batch translation
            uncached_texts.append(text)
            uncached_indices.append(idx)
            results.append(None)  # Placeholder

        # Translate uncached texts in batch
        if uncached_texts:
            try:
                batch_results = self._translator.translate_text(
                    uncached_texts,
                    target_lang=target_lang.value,
                    source_lang=source_lang.value if source_lang else None,
                )

                # Handle single result vs list
                if not isinstance(batch_results, list):
                    batch_results = [batch_results]

                for idx, result in zip(uncached_indices, batch_results):
                    original_text = texts[idx]
                    translated_text = result.text
                    detected_source_lang = result.detected_source_lang

                    # Store in cache
                    if use_cache:
                        self._cache.set(
                            original_text,
                            target_lang.value,
                            translated_text,
                            source_lang.value if source_lang else None,
                        )

                    results[idx] = TranslationResult(
                        original_text=original_text,
                        translated_text=translated_text,
                        source_lang=detected_source_lang,
                        target_lang=target_lang.value,
                        cached=False,
                    )

                logger.info(
                    f"Batch translated {len(uncached_texts)} texts to {target_lang.value}"
                )

            except deepl.DeepLException as e:
                logger.error(f"DeepL API error during batch translation: {str(e)}")
                raise Exception(f"Batch translation failed: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error during batch translation: {str(e)}")
                raise

        return results

    def translate_recipe(
        self,
        recipe_data: Dict[str, Any],
        target_lang: Language,
        use_cache: bool = True,
    ) -> RecipeTranslationResult:
        """
        Translate all text fields in a recipe.

        Args:
          recipe_data: Recipe dictionary with fields to translate
          target_lang: Target language
          use_cache: Whether to use cache

        Returns:
          RecipeTranslationResult with translated fields

        Raises:
          Exception: If translation fails
        """
        recipe_id = recipe_data.get("id", "unknown")
        cached_count = 0

        try:
            # Prepare texts for batch translation
            texts_to_translate = []
            text_types = []

            # Title
            if recipe_data.get("title"):
                texts_to_translate.append(recipe_data["title"])
                text_types.append("title")

            # Description
            if recipe_data.get("description"):
                texts_to_translate.append(recipe_data["description"])
                text_types.append("description")

            # Ingredients
            ingredients = recipe_data.get("ingredients", [])
            for ingredient in ingredients:
                if isinstance(ingredient, str):
                    texts_to_translate.append(ingredient)
                    text_types.append("ingredient")
                elif isinstance(ingredient, dict) and ingredient.get("name"):
                    texts_to_translate.append(ingredient["name"])
                    text_types.append("ingredient")

            # Steps
            steps = recipe_data.get("steps", [])
            for step in steps:
                if isinstance(step, str):
                    texts_to_translate.append(step)
                    text_types.append("step")
                elif isinstance(step, dict) and step.get("instruction"):
                    texts_to_translate.append(step["instruction"])
                    text_types.append("step")

            # Batch translate all texts
            if not texts_to_translate:
                logger.warning(f"No translatable content found in recipe {recipe_id}")
                return RecipeTranslationResult(
                    recipe_id=recipe_id,
                    target_lang=target_lang.value,
                )

            translation_results = self.translate_batch(
                texts_to_translate,
                target_lang=target_lang,
                use_cache=use_cache,
            )

            # Extract results by type
            result_dict = {
                "title": None,
                "description": None,
                "ingredients": [],
                "steps": [],
            }

            for text_type, result in zip(text_types, translation_results):
                if result.cached:
                    cached_count += 1

                if text_type == "title":
                    result_dict["title"] = result.translated_text
                elif text_type == "description":
                    result_dict["description"] = result.translated_text
                elif text_type == "ingredient":
                    result_dict["ingredients"].append(result.translated_text)
                elif text_type == "step":
                    result_dict["steps"].append(result.translated_text)

            logger.info(
                f"Translated recipe {recipe_id} to {target_lang.value} "
                f"({cached_count}/{len(translation_results)} from cache)"
            )

            return RecipeTranslationResult(
                recipe_id=recipe_id,
                target_lang=target_lang.value,
                title=result_dict["title"],
                description=result_dict["description"],
                ingredients=result_dict["ingredients"],
                steps=result_dict["steps"],
                cached_count=cached_count,
            )

        except Exception as e:
            logger.error(f"Failed to translate recipe {recipe_id}: {str(e)}")
            raise

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
          Dictionary with cache stats
        """
        return {
            "size": self._cache.get_size(),
        }

    def clear_cache(self) -> None:
        """Clear translation cache."""
        self._cache.clear()
        logger.info("Translation cache cleared")

    def check_usage(self) -> Dict[str, Any]:
        """
        Check DeepL API usage statistics.

        Returns:
          Dictionary with usage information

        Raises:
          Exception: If usage check fails
        """
        try:
            usage = self._translator.get_usage()
            return {
                "character_count": usage.character.count,
                "character_limit": usage.character.limit,
                "character_usage_percent": (
                    (usage.character.count / usage.character.limit * 100)
                    if usage.character.limit
                    else 0
                ),
            }
        except deepl.DeepLException as e:
            logger.error(f"Failed to check DeepL usage: {str(e)}")
            raise Exception(f"Usage check failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error checking usage: {str(e)}")
            raise

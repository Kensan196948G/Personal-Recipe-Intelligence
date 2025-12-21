"""
Tests for translation service.

This module contains unit tests for the translation service.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from backend.translation.models import (
    Language,
)
from backend.translation.service import TranslationCache, TranslationService


class TestTranslationCache:
    """Test cases for TranslationCache."""

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = TranslationCache(ttl_minutes=30)
        assert cache.get_size() == 0

    def test_cache_set_and_get(self):
        """Test setting and getting cache entries."""
        cache = TranslationCache()
        cache.set("Hello", "JA", "こんにちは")
        result = cache.get("Hello", "JA")
        assert result == "こんにちは"

    def test_cache_miss(self):
        """Test cache miss."""
        cache = TranslationCache()
        result = cache.get("Hello", "JA")
        assert result is None

    def test_cache_expiration(self):
        """Test cache entry expiration."""
        cache = TranslationCache(ttl_minutes=0)
        cache.set("Hello", "JA", "こんにちは")
        # Simulate time passing
        cache._cache[list(cache._cache.keys())[0]][
            "timestamp"
        ] = datetime.now() - timedelta(minutes=1)
        result = cache.get("Hello", "JA")
        assert result is None

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = TranslationCache()
        cache.set("Hello", "JA", "こんにちは")
        cache.set("Goodbye", "JA", "さようなら")
        assert cache.get_size() == 2
        cache.clear()
        assert cache.get_size() == 0

    def test_cache_key_generation(self):
        """Test cache key is different for different parameters."""
        cache = TranslationCache()
        cache.set("Hello", "JA", "こんにちは")
        cache.set("Hello", "EN-US", "Hello")
        assert cache.get("Hello", "JA") == "こんにちは"
        assert cache.get("Hello", "EN-US") == "Hello"


class TestTranslationService:
    """Test cases for TranslationService."""

    @patch("backend.translation.service.deepl.Translator")
    def test_service_initialization(self, mock_translator):
        """Test service initialization."""
        service = TranslationService("test_api_key")
        assert service is not None
        mock_translator.assert_called_once_with("test_api_key")

    @patch("backend.translation.service.deepl.Translator")
    def test_service_initialization_empty_key(self, mock_translator):
        """Test service initialization with empty API key."""
        with pytest.raises(ValueError):
            TranslationService("")

    @patch("backend.translation.service.deepl.Translator")
    def test_translate_success(self, mock_translator):
        """Test successful translation."""
        # Mock DeepL response
        mock_result = Mock()
        mock_result.text = "こんにちは"
        mock_result.detected_source_lang = "EN"
        mock_translator_instance = Mock()
        mock_translator_instance.translate_text.return_value = mock_result
        mock_translator.return_value = mock_translator_instance

        service = TranslationService("test_api_key")
        result = service.translate("Hello", Language.JA, use_cache=False)

        assert result.original_text == "Hello"
        assert result.translated_text == "こんにちは"
        assert result.source_lang == "EN"
        assert result.target_lang == "JA"
        assert result.cached is False

    @patch("backend.translation.service.deepl.Translator")
    def test_translate_empty_text(self, mock_translator):
        """Test translation of empty text."""
        service = TranslationService("test_api_key")
        result = service.translate("", Language.JA)

        assert result.original_text == ""
        assert result.translated_text == ""

    @patch("backend.translation.service.deepl.Translator")
    def test_translate_with_cache(self, mock_translator):
        """Test translation with cache."""
        mock_result = Mock()
        mock_result.text = "こんにちは"
        mock_result.detected_source_lang = "EN"
        mock_translator_instance = Mock()
        mock_translator_instance.translate_text.return_value = mock_result
        mock_translator.return_value = mock_translator_instance

        service = TranslationService("test_api_key")

        # First call - should use API
        result1 = service.translate("Hello", Language.JA, use_cache=True)
        assert result1.cached is False

        # Second call - should use cache
        result2 = service.translate("Hello", Language.JA, use_cache=True)
        assert result2.cached is True
        assert result2.translated_text == "こんにちは"

        # API should only be called once
        mock_translator_instance.translate_text.assert_called_once()

    @patch("backend.translation.service.deepl.Translator")
    def test_translate_batch(self, mock_translator):
        """Test batch translation."""
        mock_results = [
            Mock(text="こんにちは", detected_source_lang="EN"),
            Mock(text="さようなら", detected_source_lang="EN"),
        ]
        mock_translator_instance = Mock()
        mock_translator_instance.translate_text.return_value = mock_results
        mock_translator.return_value = mock_translator_instance

        service = TranslationService("test_api_key")
        results = service.translate_batch(
            ["Hello", "Goodbye"], Language.JA, use_cache=False
        )

        assert len(results) == 2
        assert results[0].translated_text == "こんにちは"
        assert results[1].translated_text == "さようなら"

    @patch("backend.translation.service.deepl.Translator")
    def test_translate_recipe(self, mock_translator):
        """Test recipe translation."""
        mock_results = [
            Mock(text="チキンカレー", detected_source_lang="EN"),
            Mock(text="美味しいカレーのレシピ", detected_source_lang="EN"),
            Mock(text="鶏肉", detected_source_lang="EN"),
            Mock(text="玉ねぎ", detected_source_lang="EN"),
            Mock(text="材料を切る", detected_source_lang="EN"),
            Mock(text="煮込む", detected_source_lang="EN"),
        ]
        mock_translator_instance = Mock()
        mock_translator_instance.translate_text.return_value = mock_results
        mock_translator.return_value = mock_translator_instance

        service = TranslationService("test_api_key")

        recipe_data = {
            "id": "recipe_001",
            "title": "Chicken Curry",
            "description": "Delicious curry recipe",
            "ingredients": ["Chicken", "Onion"],
            "steps": ["Cut ingredients", "Simmer"],
        }

        result = service.translate_recipe(recipe_data, Language.JA, use_cache=False)

        assert result.recipe_id == "recipe_001"
        assert result.title == "チキンカレー"
        assert result.description == "美味しいカレーのレシピ"
        assert len(result.ingredients) == 2
        assert len(result.steps) == 2

    @patch("backend.translation.service.deepl.Translator")
    def test_get_cache_stats(self, mock_translator):
        """Test cache statistics."""
        service = TranslationService("test_api_key")
        stats = service.get_cache_stats()
        assert "size" in stats
        assert stats["size"] == 0

    @patch("backend.translation.service.deepl.Translator")
    def test_clear_cache(self, mock_translator):
        """Test cache clearing."""
        mock_result = Mock()
        mock_result.text = "こんにちは"
        mock_result.detected_source_lang = "EN"
        mock_translator_instance = Mock()
        mock_translator_instance.translate_text.return_value = mock_result
        mock_translator.return_value = mock_translator_instance

        service = TranslationService("test_api_key")
        service.translate("Hello", Language.JA, use_cache=True)

        stats = service.get_cache_stats()
        assert stats["size"] > 0

        service.clear_cache()
        stats = service.get_cache_stats()
        assert stats["size"] == 0

    @patch("backend.translation.service.deepl.Translator")
    def test_check_usage(self, mock_translator):
        """Test usage checking."""
        mock_usage = Mock()
        mock_usage.character.count = 1000
        mock_usage.character.limit = 500000
        mock_translator_instance = Mock()
        mock_translator_instance.get_usage.return_value = mock_usage
        mock_translator.return_value = mock_translator_instance

        service = TranslationService("test_api_key")
        usage = service.check_usage()

        assert usage["character_count"] == 1000
        assert usage["character_limit"] == 500000
        assert usage["character_usage_percent"] == 0.2

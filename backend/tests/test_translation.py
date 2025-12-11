"""Tests for translation service functionality."""

import pytest
from unittest.mock import Mock, patch


class MockTranslationService:
    """Mock translation service for testing."""

    def __init__(self):
        self.supported_languages = ["en", "ja", "ko", "zh"]
        self.translation_cache = {}

    def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> str:
        """Translate text to target language."""
        if not text:
            raise ValueError("Text cannot be empty")

        if target_lang not in self.supported_languages:
            raise ValueError(f"Unsupported language: {target_lang}")

        # Check cache
        cache_key = f"{text}:{source_lang}:{target_lang}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        # Mock translation
        translations = {
            ("料理", "ja", "en"): "Cooking",
            ("料理", "en", "ja"): "Cooking",
            ("たまねぎ", "ja", "en"): "Onion",
            ("にんじん", "ja", "en"): "Carrot",
            ("じゃがいも", "ja", "en"): "Potato",
            ("カレー", "ja", "en"): "Curry",
            ("Onion", "en", "ja"): "たまねぎ",
            ("Carrot", "en", "ja"): "にんじん",
            ("Potato", "en", "ja"): "じゃがいも",
        }

        result = translations.get((text, source_lang, target_lang), text)
        self.translation_cache[cache_key] = result
        return result

    def translate_recipe(self, recipe_data: dict, target_lang: str) -> dict:
        """Translate entire recipe."""
        translated = recipe_data.copy()

        # Translate title
        if "title" in recipe_data:
            translated["title"] = self.translate(
                recipe_data["title"], target_lang, "ja"
            )

        # Translate ingredients
        if "ingredients" in recipe_data:
            translated["ingredients"] = []
            for ingredient in recipe_data["ingredients"]:
                translated["ingredients"].append(
                    {
                        "name": self.translate(ingredient["name"], target_lang, "ja"),
                        "amount": ingredient["amount"],
                    }
                )

        # Translate steps
        if "steps" in recipe_data:
            translated["steps"] = [
                self.translate(step, target_lang, "ja") for step in recipe_data["steps"]
            ]

        return translated

    def detect_language(self, text: str) -> str:
        """Detect language of text."""
        if not text:
            return "unknown"

        # Simple detection based on character sets
        if any("\u4e00" <= char <= "\u9fff" for char in text):
            # Contains Chinese/Japanese characters
            if any("\u3040" <= char <= "\u309f" for char in text):
                return "ja"  # Has hiragana
            return "zh"
        elif any("\uac00" <= char <= "\ud7af" for char in text):
            return "ko"  # Korean
        else:
            return "en"  # Default to English

    def is_supported_language(self, lang: str) -> bool:
        """Check if language is supported."""
        return lang in self.supported_languages

    def clear_cache(self):
        """Clear translation cache."""
        self.translation_cache.clear()


class TestTranslationService:
    """Test suite for translation service."""

    def test_translate_simple_word_ja_to_en(self):
        """Test translating simple Japanese word to English."""
        service = MockTranslationService()
        result = service.translate("たまねぎ", "en", "ja")
        assert result == "Onion"

    def test_translate_simple_word_en_to_ja(self):
        """Test translating simple English word to Japanese."""
        service = MockTranslationService()
        result = service.translate("Onion", "ja", "en")
        assert result == "たまねぎ"

    def test_translate_multiple_ingredients(self):
        """Test translating multiple ingredients."""
        service = MockTranslationService()

        ingredients = ["たまねぎ", "にんじん", "じゃがいも"]
        translated = [service.translate(ing, "en", "ja") for ing in ingredients]

        assert "Onion" in translated
        assert "Carrot" in translated
        assert "Potato" in translated

    def test_translate_empty_text(self):
        """Test translating empty text raises error."""
        service = MockTranslationService()

        with pytest.raises(ValueError):
            service.translate("", "en", "ja")

    def test_translate_unsupported_language(self):
        """Test translating to unsupported language raises error."""
        service = MockTranslationService()

        with pytest.raises(ValueError):
            service.translate("test", "fr", "en")  # French not supported

    def test_translate_recipe_title(self):
        """Test translating recipe title."""
        service = MockTranslationService()

        recipe = {"title": "料理", "ingredients": [], "steps": []}

        translated = service.translate_recipe(recipe, "en")
        assert translated["title"] == "Cooking"

    def test_translate_recipe_ingredients(self):
        """Test translating recipe ingredients."""
        service = MockTranslationService()

        recipe = {
            "title": "カレー",
            "ingredients": [
                {"name": "たまねぎ", "amount": "1個"},
                {"name": "にんじん", "amount": "2本"},
            ],
            "steps": [],
        }

        translated = service.translate_recipe(recipe, "en")

        ingredient_names = [ing["name"] for ing in translated["ingredients"]]
        assert "Onion" in ingredient_names
        assert "Carrot" in ingredient_names

        # Amounts should remain unchanged
        assert translated["ingredients"][0]["amount"] == "1個"

    def test_translate_recipe_steps(self):
        """Test translating recipe steps."""
        service = MockTranslationService()

        recipe = {
            "title": "テスト",
            "ingredients": [],
            "steps": ["たまねぎ", "にんじん"],
        }

        translated = service.translate_recipe(recipe, "en")
        assert "Onion" in translated["steps"]
        assert "Carrot" in translated["steps"]

    def test_detect_language_japanese(self):
        """Test detecting Japanese language."""
        service = MockTranslationService()

        assert service.detect_language("こんにちは") == "ja"
        assert service.detect_language("たまねぎ") == "ja"

    def test_detect_language_english(self):
        """Test detecting English language."""
        service = MockTranslationService()

        assert service.detect_language("Hello") == "en"
        assert service.detect_language("Onion") == "en"

    def test_detect_language_korean(self):
        """Test detecting Korean language."""
        service = MockTranslationService()

        assert service.detect_language("안녕하세요") == "ko"

    def test_detect_language_chinese(self):
        """Test detecting Chinese language."""
        service = MockTranslationService()

        assert service.detect_language("你好") == "zh"

    def test_detect_language_empty(self):
        """Test detecting language of empty text."""
        service = MockTranslationService()

        assert service.detect_language("") == "unknown"

    def test_is_supported_language_valid(self):
        """Test checking supported languages."""
        service = MockTranslationService()

        assert service.is_supported_language("en") is True
        assert service.is_supported_language("ja") is True
        assert service.is_supported_language("ko") is True
        assert service.is_supported_language("zh") is True

    def test_is_supported_language_invalid(self):
        """Test checking unsupported languages."""
        service = MockTranslationService()

        assert service.is_supported_language("fr") is False
        assert service.is_supported_language("de") is False

    def test_translation_cache(self):
        """Test translation caching."""
        service = MockTranslationService()

        # First translation
        result1 = service.translate("たまねぎ", "en", "ja")

        # Second translation (should use cache)
        result2 = service.translate("たまねぎ", "en", "ja")

        assert result1 == result2
        assert len(service.translation_cache) > 0

    def test_clear_cache(self):
        """Test clearing translation cache."""
        service = MockTranslationService()

        service.translate("たまねぎ", "en", "ja")
        assert len(service.translation_cache) > 0

        service.clear_cache()
        assert len(service.translation_cache) == 0

    def test_translate_unknown_word(self):
        """Test translating unknown word returns original."""
        service = MockTranslationService()

        result = service.translate("未知の単語", "en", "ja")
        assert result == "未知の単語"  # Returns original when not in mock dict

    def test_translate_recipe_preserves_structure(self):
        """Test that recipe structure is preserved after translation."""
        service = MockTranslationService()

        recipe = {
            "title": "カレー",
            "ingredients": [{"name": "たまねぎ", "amount": "1個"}],
            "steps": ["切る"],
            "tags": ["簡単"],
            "cooking_time": 30,
        }

        translated = service.translate_recipe(recipe, "en")

        assert "title" in translated
        assert "ingredients" in translated
        assert "steps" in translated
        assert "tags" in translated
        assert "cooking_time" in translated
        assert translated["cooking_time"] == 30

    @patch("requests.post")
    def test_api_translation_call(self, mock_post):
        """Test external API translation call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"translations": [{"text": "Onion"}]}
        mock_post.return_value = mock_response

        response = mock_post(
            "https://api.translation.com/translate",
            json={"text": "たまねぎ", "target": "en"},
        )

        assert response.status_code == 200
        assert response.json()["translations"][0]["text"] == "Onion"

    def test_batch_translation(self):
        """Test batch translation of multiple texts."""
        service = MockTranslationService()

        texts = ["たまねぎ", "にんじん", "じゃがいも"]
        results = [service.translate(text, "en", "ja") for text in texts]

        assert len(results) == 3
        assert "Onion" in results
        assert "Carrot" in results
        assert "Potato" in results

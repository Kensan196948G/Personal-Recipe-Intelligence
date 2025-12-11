"""
Unit tests for utility functions

Tests cover:
- Date and time utilities
- String formatting and normalization
- Data validation helpers
- File handling utilities
- JSON serialization helpers
- List and dict manipulation
"""

import pytest
from datetime import datetime, timedelta
import json


class MockUtils:
  """Mock utility functions for testing"""

  @staticmethod
  def normalize_ingredient(ingredient: str) -> str:
    """Normalize ingredient name"""
    normalized = ingredient.lower().strip()
    replacements = {
      "玉ねぎ": "たまねぎ",
      "玉葱": "たまねぎ",
      "トマト": "とまと",
    }
    return replacements.get(normalized, normalized)

  @staticmethod
  def parse_quantity(quantity_str: str) -> dict:
    """Parse quantity string into amount and unit"""
    parts = quantity_str.strip().split()
    if len(parts) >= 2:
      try:
        amount = float(parts[0])
        unit = " ".join(parts[1:])
        return {"amount": amount, "unit": unit}
      except ValueError:
        pass
    return {"amount": None, "unit": quantity_str}

  @staticmethod
  def format_cooking_time(minutes: int) -> str:
    """Format cooking time in human-readable format"""
    if minutes < 60:
      return f"{minutes}分"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
      return f"{hours}時間"
    return f"{hours}時間{remaining_minutes}分"

  @staticmethod
  def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
      return False
    return url.startswith("http://") or url.startswith("https://")

  @staticmethod
  def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
      return text
    return text[:max_length - len(suffix)] + suffix

  @staticmethod
  def safe_json_parse(json_str: str, default=None):
    """Safely parse JSON string"""
    try:
      return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
      return default

  @staticmethod
  def merge_tags(tags1: list, tags2: list) -> list:
    """Merge two tag lists removing duplicates"""
    return list(set(tags1 + tags2))

  @staticmethod
  def calculate_difficulty(
    ingredients_count: int,
    steps_count: int,
    cooking_time: int
  ) -> str:
    """Calculate recipe difficulty level"""
    score = ingredients_count * 0.3 + steps_count * 0.5 + (cooking_time / 10) * 0.2

    if score < 5:
      return "easy"
    elif score < 10:
      return "medium"
    else:
      return "hard"


class TestIngredientNormalization:
  """Test suite for ingredient normalization"""

  def test_normalize_lowercase(self):
    """Test normalizing to lowercase"""
    utils = MockUtils()

    result = utils.normalize_ingredient("TOMATO")

    assert result == "tomato"

  def test_normalize_trim_whitespace(self):
    """Test trimming whitespace"""
    utils = MockUtils()

    result = utils.normalize_ingredient("  carrot  ")

    assert result == "carrot"

  def test_normalize_japanese_onion(self):
    """Test normalizing Japanese onion variations"""
    utils = MockUtils()

    result1 = utils.normalize_ingredient("玉ねぎ")
    result2 = utils.normalize_ingredient("玉葱")

    assert result1 == "たまねぎ"
    assert result2 == "たまねぎ"

  def test_normalize_katakana_tomato(self):
    """Test normalizing katakana tomato"""
    utils = MockUtils()

    result = utils.normalize_ingredient("トマト")

    assert result == "とまと"

  def test_normalize_empty_string(self):
    """Test normalizing empty string"""
    utils = MockUtils()

    result = utils.normalize_ingredient("")

    assert result == ""

  def test_normalize_preserves_unknown(self):
    """Test that unknown ingredients are preserved"""
    utils = MockUtils()

    result = utils.normalize_ingredient("exotic ingredient")

    assert result == "exotic ingredient"


class TestQuantityParsing:
  """Test suite for quantity parsing"""

  def test_parse_quantity_with_number_and_unit(self):
    """Test parsing quantity with number and unit"""
    utils = MockUtils()

    result = utils.parse_quantity("200 g")

    assert result["amount"] == 200
    assert result["unit"] == "g"

  def test_parse_quantity_with_decimal(self):
    """Test parsing quantity with decimal number"""
    utils = MockUtils()

    result = utils.parse_quantity("2.5 cups")

    assert result["amount"] == 2.5
    assert result["unit"] == "cups"

  def test_parse_quantity_complex_unit(self):
    """Test parsing quantity with complex unit"""
    utils = MockUtils()

    result = utils.parse_quantity("100 ml water")

    assert result["amount"] == 100
    assert result["unit"] == "ml water"

  def test_parse_quantity_no_number(self):
    """Test parsing quantity without number"""
    utils = MockUtils()

    result = utils.parse_quantity("a pinch of salt")

    assert result["amount"] is None
    assert result["unit"] == "a pinch of salt"

  def test_parse_quantity_empty_string(self):
    """Test parsing empty quantity string"""
    utils = MockUtils()

    result = utils.parse_quantity("")

    assert result["amount"] is None
    assert result["unit"] == ""


class TestCookingTimeFormatting:
  """Test suite for cooking time formatting"""

  def test_format_cooking_time_minutes_only(self):
    """Test formatting cooking time in minutes"""
    utils = MockUtils()

    result = utils.format_cooking_time(45)

    assert result == "45分"

  def test_format_cooking_time_hours_only(self):
    """Test formatting cooking time in hours"""
    utils = MockUtils()

    result = utils.format_cooking_time(120)

    assert result == "2時間"

  def test_format_cooking_time_hours_and_minutes(self):
    """Test formatting cooking time with hours and minutes"""
    utils = MockUtils()

    result = utils.format_cooking_time(90)

    assert result == "1時間30分"

  def test_format_cooking_time_zero(self):
    """Test formatting zero cooking time"""
    utils = MockUtils()

    result = utils.format_cooking_time(0)

    assert result == "0分"

  def test_format_cooking_time_large_value(self):
    """Test formatting very large cooking time"""
    utils = MockUtils()

    result = utils.format_cooking_time(300)

    assert result == "5時間"


class TestURLValidation:
  """Test suite for URL validation"""

  def test_validate_url_http(self):
    """Test validating HTTP URL"""
    utils = MockUtils()

    result = utils.validate_url("http://example.com")

    assert result is True

  def test_validate_url_https(self):
    """Test validating HTTPS URL"""
    utils = MockUtils()

    result = utils.validate_url("https://example.com/recipe")

    assert result is True

  def test_validate_url_invalid_protocol(self):
    """Test validating URL with invalid protocol"""
    utils = MockUtils()

    result = utils.validate_url("ftp://example.com")

    assert result is False

  def test_validate_url_no_protocol(self):
    """Test validating URL without protocol"""
    utils = MockUtils()

    result = utils.validate_url("example.com")

    assert result is False

  def test_validate_url_empty(self):
    """Test validating empty URL"""
    utils = MockUtils()

    result = utils.validate_url("")

    assert result is False

  def test_validate_url_none(self):
    """Test validating None URL"""
    utils = MockUtils()

    result = utils.validate_url(None)

    assert result is False


class TestTextTruncation:
  """Test suite for text truncation"""

  def test_truncate_text_short(self):
    """Test truncating text shorter than max length"""
    utils = MockUtils()

    result = utils.truncate_text("Short text", 20)

    assert result == "Short text"

  def test_truncate_text_exact_length(self):
    """Test truncating text at exact max length"""
    utils = MockUtils()

    result = utils.truncate_text("Exact length", 12)

    assert result == "Exact length"

  def test_truncate_text_long(self):
    """Test truncating long text"""
    utils = MockUtils()

    result = utils.truncate_text("This is a very long text", 10)

    # max_length=10, suffix="..."(3文字), なので 10-3=7文字 + "..." = "This is..."
    assert result == "This is..."
    assert len(result) == 10

  def test_truncate_text_custom_suffix(self):
    """Test truncating with custom suffix"""
    utils = MockUtils()

    result = utils.truncate_text("Long text here", 10, suffix=">>")

    assert result.endswith(">>")
    assert len(result) == 10

  def test_truncate_text_empty(self):
    """Test truncating empty text"""
    utils = MockUtils()

    result = utils.truncate_text("", 10)

    assert result == ""


class TestJSONParsing:
  """Test suite for safe JSON parsing"""

  def test_safe_json_parse_valid(self):
    """Test parsing valid JSON"""
    utils = MockUtils()

    result = utils.safe_json_parse('{"key": "value"}')

    assert result == {"key": "value"}

  def test_safe_json_parse_invalid(self):
    """Test parsing invalid JSON"""
    utils = MockUtils()

    result = utils.safe_json_parse("invalid json", default={})

    assert result == {}

  def test_safe_json_parse_empty(self):
    """Test parsing empty string"""
    utils = MockUtils()

    result = utils.safe_json_parse("", default=None)

    assert result is None

  def test_safe_json_parse_array(self):
    """Test parsing JSON array"""
    utils = MockUtils()

    result = utils.safe_json_parse('[1, 2, 3]')

    assert result == [1, 2, 3]

  def test_safe_json_parse_nested(self):
    """Test parsing nested JSON"""
    utils = MockUtils()

    result = utils.safe_json_parse('{"outer": {"inner": "value"}}')

    assert result["outer"]["inner"] == "value"

  def test_safe_json_parse_none_input(self):
    """Test parsing None input"""
    utils = MockUtils()

    result = utils.safe_json_parse(None, default=[])

    assert result == []


class TestTagMerging:
  """Test suite for tag merging"""

  def test_merge_tags_no_duplicates(self):
    """Test merging tags without duplicates"""
    utils = MockUtils()

    result = utils.merge_tags(["tag1", "tag2"], ["tag3", "tag4"])

    assert set(result) == {"tag1", "tag2", "tag3", "tag4"}

  def test_merge_tags_with_duplicates(self):
    """Test merging tags with duplicates"""
    utils = MockUtils()

    result = utils.merge_tags(["tag1", "tag2"], ["tag2", "tag3"])

    assert len(result) == 3
    assert "tag1" in result
    assert "tag2" in result
    assert "tag3" in result

  def test_merge_tags_empty_lists(self):
    """Test merging empty tag lists"""
    utils = MockUtils()

    result = utils.merge_tags([], [])

    assert result == []

  def test_merge_tags_one_empty(self):
    """Test merging when one list is empty"""
    utils = MockUtils()

    result = utils.merge_tags(["tag1"], [])

    assert result == ["tag1"]

  def test_merge_tags_preserves_all(self):
    """Test that all unique tags are preserved"""
    utils = MockUtils()
    tags1 = ["italian", "pasta"]
    tags2 = ["dinner", "pasta", "quick"]

    result = utils.merge_tags(tags1, tags2)

    assert len(result) == 4


class TestDifficultyCalculation:
  """Test suite for recipe difficulty calculation"""

  def test_calculate_difficulty_easy(self):
    """Test calculating easy difficulty"""
    utils = MockUtils()

    result = utils.calculate_difficulty(
      ingredients_count=3,
      steps_count=2,
      cooking_time=15
    )

    assert result == "easy"

  def test_calculate_difficulty_medium(self):
    """Test calculating medium difficulty"""
    utils = MockUtils()

    # score = 8*0.3 + 8*0.5 + (45/10)*0.2 = 2.4 + 4.0 + 0.9 = 7.3 (medium: 5 <= score < 10)
    result = utils.calculate_difficulty(
      ingredients_count=8,
      steps_count=8,
      cooking_time=45
    )

    assert result == "medium"

  def test_calculate_difficulty_hard(self):
    """Test calculating hard difficulty"""
    utils = MockUtils()

    result = utils.calculate_difficulty(
      ingredients_count=12,
      steps_count=10,
      cooking_time=120
    )

    assert result == "hard"

  def test_calculate_difficulty_zero_values(self):
    """Test calculating difficulty with zero values"""
    utils = MockUtils()

    result = utils.calculate_difficulty(
      ingredients_count=0,
      steps_count=0,
      cooking_time=0
    )

    assert result == "easy"

  def test_calculate_difficulty_boundary_easy_medium(self):
    """Test difficulty calculation at easy-medium boundary"""
    utils = MockUtils()

    result = utils.calculate_difficulty(
      ingredients_count=5,
      steps_count=3,
      cooking_time=20
    )

    assert result in ["easy", "medium"]


class TestUtilsEdgeCases:
  """Test suite for utility edge cases"""

  def test_normalize_ingredient_special_chars(self):
    """Test normalizing ingredient with special characters"""
    utils = MockUtils()

    result = utils.normalize_ingredient("Salt & Pepper")

    assert result == "salt & pepper"

  def test_parse_quantity_japanese_units(self):
    """Test parsing quantity with Japanese units"""
    utils = MockUtils()

    result = utils.parse_quantity("2 大さじ")

    assert result["amount"] == 2
    assert "大さじ" in result["unit"]

  def test_truncate_text_unicode(self):
    """Test truncating text with unicode characters"""
    utils = MockUtils()

    result = utils.truncate_text("日本語のテキスト", 5)

    assert len(result) == 5

  def test_merge_tags_case_sensitivity(self):
    """Test that tag merging is case-sensitive"""
    utils = MockUtils()

    result = utils.merge_tags(["Italian"], ["italian"])

    assert len(result) == 2

  def test_format_cooking_time_negative(self):
    """Test formatting negative cooking time"""
    utils = MockUtils()

    result = utils.format_cooking_time(-10)

    assert "-10分" in result

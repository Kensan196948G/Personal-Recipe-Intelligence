"""
Ingredient Normalizer Service for Personal Recipe Intelligence.

This module provides functionality to normalize ingredient names, quantities,
and units to ensure consistency across recipe data.
"""

import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass
class NormalizedIngredient:
  """Normalized ingredient data structure."""

  name: str
  quantity: Optional[Decimal]
  unit: Optional[str]
  original_text: str
  note: Optional[str] = None


class IngredientNormalizer:
  """
  Service for normalizing ingredient names, quantities, and units.

  Handles Japanese ingredient name variations, synonym mapping,
  quantity parsing (including fractions), and unit standardization.
  """

  def __init__(self, mappings_path: Optional[str] = None):
    """
    Initialize the normalizer with ingredient mappings.

    Args:
      mappings_path: Path to the ingredient_mappings.json file.
                     Defaults to config/ingredient_mappings.json
    """
    if mappings_path is None:
      base_dir = Path(__file__).parent.parent.parent
      mappings_path = base_dir / "config" / "ingredient_mappings.json"

    self.mappings_path = Path(mappings_path)
    self._load_mappings()

  def _load_mappings(self) -> None:
    """Load ingredient mappings from JSON file."""
    try:
      with open(self.mappings_path, "r", encoding="utf-8") as f:
        data = json.load(f)

      self.ingredient_synonyms: Dict[str, str] = data.get("ingredient_synonyms", {})
      self.unit_synonyms: Dict[str, str] = data.get("unit_synonyms", {})
      self.quantity_keywords: Dict[str, str] = data.get("quantity_keywords", {})

    except FileNotFoundError:
      raise FileNotFoundError(
        f"Ingredient mappings file not found: {self.mappings_path}"
      )
    except json.JSONDecodeError as e:
      raise ValueError(f"Invalid JSON in mappings file: {e}")

  def normalize_ingredient_name(self, name: str) -> str:
    """
    Normalize ingredient name to canonical form.

    Args:
      name: Original ingredient name

    Returns:
      Normalized ingredient name
    """
    # Remove extra whitespace
    name = name.strip()

    # Convert to hiragana if possible (simple katakana to hiragana)
    normalized = self._katakana_to_hiragana(name)

    # Look up synonym mapping
    if normalized in self.ingredient_synonyms:
      return self.ingredient_synonyms[normalized]

    # Try case-insensitive lookup
    name_lower = normalized.lower()
    for key, value in self.ingredient_synonyms.items():
      if key.lower() == name_lower:
        return value

    # Return normalized version if no mapping found
    return normalized

  def normalize_unit(self, unit: str) -> str:
    """
    Normalize measurement unit.

    Args:
      unit: Original unit string

    Returns:
      Normalized unit
    """
    # Remove extra whitespace
    unit = unit.strip()

    # Look up unit synonym mapping
    if unit in self.unit_synonyms:
      return self.unit_synonyms[unit]

    # Try case-insensitive lookup
    unit_lower = unit.lower()
    for key, value in self.unit_synonyms.items():
      if key.lower() == unit_lower:
        return value

    # Return original if no mapping found
    return unit

  def parse_quantity(self, quantity_str: str) -> Tuple[Optional[Decimal], Optional[str]]:
    """
    Parse quantity string into numeric value and note.

    Handles fractions (1/2, 2/3), decimals, ranges, and keywords (少々, 適量).

    Args:
      quantity_str: Quantity string to parse

    Returns:
      Tuple of (quantity as Decimal or None, note/keyword)
    """
    quantity_str = quantity_str.strip()

    # Check for quantity keywords (少々, 適量, etc.)
    for keyword in self.quantity_keywords.keys():
      if keyword in quantity_str:
        return (None, self.quantity_keywords[keyword])

    # Handle fractions (1/2, 2/3, etc.)
    fraction_pattern = r"(\d+)\s*/\s*(\d+)"
    fraction_match = re.search(fraction_pattern, quantity_str)
    if fraction_match:
      numerator = Decimal(fraction_match.group(1))
      denominator = Decimal(fraction_match.group(2))
      if denominator != 0:
        quantity = numerator / denominator

        # Check for mixed numbers (e.g., "1と1/2" or "1 1/2")
        prefix_pattern = r"(\d+)\s*[と＋+]?\s*\d+\s*/\s*\d+"
        prefix_match = re.search(prefix_pattern, quantity_str)
        if prefix_match:
          whole_number = Decimal(prefix_match.group(1))
          quantity += whole_number

        return (quantity, None)

    # Handle decimal numbers
    decimal_pattern = r"(\d+\.?\d*)"
    decimal_match = re.search(decimal_pattern, quantity_str)
    if decimal_match:
      try:
        quantity = Decimal(decimal_match.group(1))
        return (quantity, None)
      except InvalidOperation:
        pass

    # Handle range (e.g., "2-3", "2〜3")
    range_pattern = r"(\d+\.?\d*)\s*[-〜～]\s*(\d+\.?\d*)"
    range_match = re.search(range_pattern, quantity_str)
    if range_match:
      try:
        min_val = Decimal(range_match.group(1))
        max_val = Decimal(range_match.group(2))
        avg_val = (min_val + max_val) / 2
        return (avg_val, f"range: {min_val}-{max_val}")
      except InvalidOperation:
        pass

    # Could not parse - return as note
    return (None, quantity_str)

  def normalize(self, ingredient_text: str) -> NormalizedIngredient:
    """
    Normalize a full ingredient text string.

    Parses ingredient name, quantity, and unit from a single string.

    Args:
      ingredient_text: Full ingredient text (e.g., "玉ねぎ 1/2個", "醤油 大さじ2")

    Returns:
      NormalizedIngredient object
    """
    original_text = ingredient_text.strip()

    # Pattern: ingredient name followed by quantity and unit
    # Examples: "玉ねぎ 1個", "醤油 大さじ2", "塩 少々"
    pattern = r"^([^\d]+?)\s*(\d+\.?\d*(?:/\d+)?(?:[と＋+]\d+\.?\d*(?:/\d+)?)?|少々|適量|ひとつまみ|ひとかけ|お好み|適宜)?\s*(.+)?$"

    match = re.match(pattern, original_text)

    if match:
      name_part = match.group(1).strip() if match.group(1) else original_text
      quantity_part = match.group(2).strip() if match.group(2) else None
      unit_part = match.group(3).strip() if match.group(3) else None

      # Normalize name
      normalized_name = self.normalize_ingredient_name(name_part)

      # Parse quantity
      quantity = None
      note = None
      if quantity_part:
        quantity, note = self.parse_quantity(quantity_part)

      # Normalize unit
      normalized_unit = None
      if unit_part:
        normalized_unit = self.normalize_unit(unit_part)

      return NormalizedIngredient(
        name=normalized_name,
        quantity=quantity,
        unit=normalized_unit,
        original_text=original_text,
        note=note,
      )

    # Fallback: treat entire text as ingredient name
    return NormalizedIngredient(
      name=self.normalize_ingredient_name(original_text),
      quantity=None,
      unit=None,
      original_text=original_text,
      note=None,
    )

  def normalize_batch(self, ingredients: list[str]) -> list[NormalizedIngredient]:
    """
    Normalize a batch of ingredient strings.

    Args:
      ingredients: List of ingredient text strings

    Returns:
      List of NormalizedIngredient objects
    """
    return [self.normalize(ingredient) for ingredient in ingredients]

  def to_dict(self, normalized: NormalizedIngredient) -> Dict[str, Any]:
    """
    Convert NormalizedIngredient to dictionary.

    Args:
      normalized: NormalizedIngredient object

    Returns:
      Dictionary representation
    """
    return {
      "name": normalized.name,
      "quantity": str(normalized.quantity) if normalized.quantity else None,
      "unit": normalized.unit,
      "original_text": normalized.original_text,
      "note": normalized.note,
    }

  @staticmethod
  def _katakana_to_hiragana(text: str) -> str:
    """
    Convert katakana to hiragana (simple conversion).

    Args:
      text: Input text

    Returns:
      Text with katakana converted to hiragana
    """
    result = []
    for char in text:
      code = ord(char)
      # Katakana range: 0x30A0 - 0x30FF
      # Hiragana range: 0x3040 - 0x309F
      if 0x30A0 <= code <= 0x30FF:
        # Convert katakana to hiragana by subtracting offset
        hiragana_code = code - 0x60
        if 0x3040 <= hiragana_code <= 0x309F:
          result.append(chr(hiragana_code))
        else:
          result.append(char)
      else:
        result.append(char)

    return "".join(result)


# Example usage
if __name__ == "__main__":
  normalizer = IngredientNormalizer()

  # Test cases
  test_ingredients = [
    "玉ねぎ 1/2個",
    "醤油 大さじ2",
    "塩 少々",
    "豚バラ肉 200g",
    "ニンジン 1本",
    "小麦粉 適量",
    "牛乳 200ml",
    "砂糖 大さじ1と1/2",
  ]

  print("Ingredient Normalization Test:\n")
  for ingredient in test_ingredients:
    normalized = normalizer.normalize(ingredient)
    print(f"Original: {ingredient}")
    print(f"  Name: {normalized.name}")
    print(f"  Quantity: {normalized.quantity}")
    print(f"  Unit: {normalized.unit}")
    print(f"  Note: {normalized.note}")
    print()

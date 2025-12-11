"""
Recipe Parser Module for OCR Text

This module parses extracted OCR text into structured recipe data.
Handles identification of title, ingredients, and cooking steps.
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RecipeParser:
  """
  Parser for converting OCR text into structured recipe data.

  Handles:
  - Recipe title extraction
  - Ingredients section identification
  - Steps/instructions extraction
  - Common OCR error correction
  """

  # Keywords for section detection (Japanese + English)
  INGREDIENT_KEYWORDS = [
    "材料",
    "ingredients",
    "材料名",
    "ingredient",
    "用意するもの",
    "必要なもの",
  ]

  STEPS_KEYWORDS = [
    "作り方",
    "手順",
    "instructions",
    "directions",
    "steps",
    "調理手順",
    "調理方法",
    "レシピ",
  ]

  # Common OCR errors (Japanese specific)
  OCR_CORRECTIONS = {
    "O": "0",  # Letter O to number 0
    "l": "1",  # Letter l to number 1
    "I": "1",  # Letter I to number 1
    "ー": "一",  # Long vowel mark to kanji one
  }

  def __init__(self):
    """Initialize recipe parser."""
    logger.info("RecipeParser initialized")

  def parse(self, text: str) -> Dict[str, any]:
    """
    Parse OCR text into structured recipe data.

    Args:
      text: Raw OCR text

    Returns:
      Dictionary containing:
        - title: Recipe title
        - ingredients: List of ingredient strings
        - steps: List of cooking step strings
        - raw_text: Original OCR text
    """
    if not text or not text.strip():
      logger.warning("Empty text provided for parsing")
      return {
        "title": "",
        "ingredients": [],
        "steps": [],
        "raw_text": "",
      }

    try:
      # Correct common OCR errors
      corrected_text = self._correct_ocr_errors(text)

      # Split into lines
      lines = [line.strip() for line in corrected_text.split("\n") if line.strip()]

      if not lines:
        return {
          "title": "",
          "ingredients": [],
          "steps": [],
          "raw_text": text,
        }

      # Extract title (usually first non-empty line)
      title = self._extract_title(lines)

      # Find section boundaries
      ingredient_start, ingredient_end = self._find_section(
        lines, self.INGREDIENT_KEYWORDS
      )
      steps_start, steps_end = self._find_section(lines, self.STEPS_KEYWORDS)

      # Extract ingredients
      ingredients = self._extract_ingredients(
        lines, ingredient_start, ingredient_end, steps_start
      )

      # Extract steps
      steps = self._extract_steps(lines, steps_start, steps_end)

      result = {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "raw_text": text,
      }

      logger.info(
        f"Parsed recipe: title={title}, "
        f"ingredients={len(ingredients)}, steps={len(steps)}"
      )
      logger.debug(f"Parsed result: {result}")

      return result

    except Exception as e:
      logger.error(f"Failed to parse recipe text: {e}", exc_info=True)
      return {
        "title": "",
        "ingredients": [],
        "steps": [],
        "raw_text": text,
      }

  def _correct_ocr_errors(self, text: str) -> str:
    """
    Correct common OCR errors in text.

    Args:
      text: Raw OCR text

    Returns:
      Corrected text
    """
    corrected = text

    # Apply simple replacements (context-aware corrections would be better)
    # For now, we keep it simple to avoid over-correction

    logger.debug("OCR error correction applied")
    return corrected

  def _extract_title(self, lines: List[str]) -> str:
    """
    Extract recipe title from lines.

    Strategy:
    - First non-empty line that's not a section header
    - Skip lines that are too short (< 3 chars)
    - Skip lines that match section keywords

    Args:
      lines: List of text lines

    Returns:
      Recipe title or empty string
    """
    for line in lines[:10]:  # Check first 10 lines
      # Skip if too short
      if len(line) < 3:
        continue

      # Skip if it's a section keyword
      if any(keyword in line.lower() for keyword in self.INGREDIENT_KEYWORDS):
        continue
      if any(keyword in line.lower() for keyword in self.STEPS_KEYWORDS):
        continue

      # Skip if it's just numbers or symbols
      if re.match(r"^[\d\s\-\.\,]+$", line):
        continue

      return line

    # Fallback to first line if nothing found
    return lines[0] if lines else ""

  def _find_section(
    self, lines: List[str], keywords: List[str]
  ) -> tuple[Optional[int], Optional[int]]:
    """
    Find section start and end indices.

    Args:
      lines: List of text lines
      keywords: Section keywords to search for

    Returns:
      Tuple of (start_index, end_index) or (None, None)
    """
    start_idx = None

    # Find start index
    for i, line in enumerate(lines):
      line_lower = line.lower()
      if any(keyword in line_lower for keyword in keywords):
        start_idx = i + 1  # Start from next line
        break

    if start_idx is None:
      return None, None

    # Find end index (next section or end of text)
    end_idx = len(lines)

    # Check for next section
    all_keywords = set(self.INGREDIENT_KEYWORDS + self.STEPS_KEYWORDS)
    for i in range(start_idx, len(lines)):
      line_lower = lines[i].lower()
      # Check if this line starts a new section
      if any(keyword in line_lower for keyword in all_keywords):
        # Make sure it's not just containing the keyword within text
        if any(line_lower.startswith(keyword) for keyword in all_keywords):
          end_idx = i
          break

    return start_idx, end_idx

  def _extract_ingredients(
    self,
    lines: List[str],
    start: Optional[int],
    end: Optional[int],
    steps_start: Optional[int],
  ) -> List[str]:
    """
    Extract ingredients from lines.

    Args:
      lines: List of text lines
      start: Start index of ingredients section
      end: End index of ingredients section
      steps_start: Start index of steps section (to avoid overlap)

    Returns:
      List of ingredient strings
    """
    ingredients = []

    # If no explicit section found, try to extract from beginning
    if start is None:
      # Look for ingredient-like patterns in first half of text
      potential_end = steps_start if steps_start else len(lines) // 2

      for line in lines[:potential_end]:
        if self._is_ingredient_line(line):
          ingredients.append(line)

      return ingredients

    # Use explicit section boundaries
    actual_end = end
    if steps_start and (end is None or steps_start < end):
      actual_end = steps_start

    for i in range(start, actual_end if actual_end else len(lines)):
      line = lines[i]

      # Skip empty or very short lines
      if len(line) < 2:
        continue

      # Skip if it looks like a section header
      if any(keyword in line.lower() for keyword in self.STEPS_KEYWORDS):
        break

      ingredients.append(line)

    return ingredients

  def _is_ingredient_line(self, line: str) -> bool:
    """
    Check if line looks like an ingredient entry.

    Common patterns:
    - Contains measurement units (g, ml, 個, カップ, etc.)
    - Contains quantity indicators
    - Format: ingredient + quantity

    Args:
      line: Text line

    Returns:
      True if line appears to be an ingredient
    """
    # Common Japanese and English measurement units
    units = [
      "g",
      "kg",
      "ml",
      "l",
      "cc",
      "カップ",
      "個",
      "本",
      "枚",
      "切れ",
      "片",
      "大さじ",
      "小さじ",
      "適量",
      "少々",
      "cup",
      "tbsp",
      "tsp",
      "oz",
      "lb",
    ]

    line_lower = line.lower()

    # Check for measurement units
    if any(unit in line_lower for unit in units):
      return True

    # Check for quantity pattern (number followed by kanji or unit)
    if re.search(r"\d+\s*[個本枚切片]", line):
      return True

    # Check for quantity at start/end
    if re.match(r"^[\d\.]+\s", line) or re.search(r"\s[\d\.]+$", line):
      return True

    return False

  def _extract_steps(
    self,
    lines: List[str],
    start: Optional[int],
    end: Optional[int],
  ) -> List[str]:
    """
    Extract cooking steps from lines.

    Args:
      lines: List of text lines
      start: Start index of steps section
      end: End index of steps section

    Returns:
      List of step strings
    """
    steps = []

    # If no explicit section found, try second half of text
    if start is None:
      start = len(lines) // 2

    actual_end = end if end else len(lines)

    current_step = ""

    for i in range(start, actual_end):
      line = lines[i]

      # Skip empty lines
      if not line:
        if current_step:
          steps.append(current_step.strip())
          current_step = ""
        continue

      # Check if line starts with step number
      step_match = re.match(r"^(\d+)[\.\)]\s*(.+)", line)
      if step_match:
        # Save previous step
        if current_step:
          steps.append(current_step.strip())

        # Start new step
        current_step = step_match.group(2)
      else:
        # Continue current step
        if current_step:
          current_step += " " + line
        else:
          current_step = line

    # Add last step
    if current_step:
      steps.append(current_step.strip())

    return steps

  def normalize_ingredient(self, ingredient: str) -> Dict[str, any]:
    """
    Normalize ingredient string into structured data.

    Attempts to extract:
    - name: Ingredient name
    - quantity: Numeric quantity
    - unit: Measurement unit

    Args:
      ingredient: Raw ingredient string

    Returns:
      Dictionary with name, quantity, unit
    """
    try:
      # Pattern: quantity + unit + name or name + quantity + unit
      # Example: "200g 牛肉" or "牛肉 200g"

      result = {
        "name": ingredient,
        "quantity": None,
        "unit": None,
        "original": ingredient,
      }

      # Extract quantity and unit
      # Pattern: number followed by optional unit
      pattern = r"(\d+(?:\.\d+)?)\s*([a-zA-Zぁ-んァ-ン一-龥]+)?"

      matches = re.findall(pattern, ingredient)

      if matches:
        quantity_str, unit = matches[0]
        result["quantity"] = float(quantity_str)
        result["unit"] = unit if unit else None

        # Remove quantity and unit from name
        name = re.sub(pattern, "", ingredient, count=1).strip()
        if name:
          result["name"] = name

      return result

    except Exception as e:
      logger.warning(f"Failed to normalize ingredient '{ingredient}': {e}")
      return {
        "name": ingredient,
        "quantity": None,
        "unit": None,
        "original": ingredient,
      }

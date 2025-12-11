"""
Recipe parser module for extracting structured recipe data from HTML.

This module provides utilities for parsing recipe information including:
- Title and description
- Ingredients with amounts and units
- Cooking steps
- Metadata (servings, prep time, cook time)
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class RecipeParser:
    """Parser for extracting structured recipe data from HTML."""

    # Common ingredient amount patterns
    AMOUNT_PATTERN = re.compile(
        r"(\d+(?:\.\d+)?(?:/\d+)?)\s*([a-zA-Zぁ-んァ-ヶー]+)?", re.UNICODE
    )

    # Time pattern (e.g., "30分", "1時間", "30 minutes")
    TIME_PATTERN = re.compile(r"(\d+)\s*(?:時間|分|hour|min|minute|hr)", re.IGNORECASE)

    @staticmethod
    def normalize_ingredient(name: str) -> str:
        """
        Normalize ingredient name according to PRI rules.

        Args:
          name: Raw ingredient name

        Returns:
          Normalized ingredient name
        """
        # Remove extra whitespace
        name = " ".join(name.split())

        # Common normalizations (玉ねぎ→たまねぎ)
        normalizations = {
            "玉ねぎ": "たまねぎ",
            "玉葱": "たまねぎ",
            "タマネギ": "たまねぎ",
            "人参": "にんじん",
            "ニンジン": "にんじん",
            "じゃが芋": "じゃがいも",
            "ジャガイモ": "じゃがいも",
            "馬鈴薯": "じゃがいも",
            "胡椒": "こしょう",
            "コショウ": "こしょう",
            "胡瓜": "きゅうり",
            "キュウリ": "きゅうり",
        }

        for old, new in normalizations.items():
            name = name.replace(old, new)

        return name

    @staticmethod
    def parse_amount(amount_str: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Parse amount string into numeric value and unit.

        Args:
          amount_str: Amount string (e.g., "200g", "1/2カップ")

        Returns:
          Tuple of (amount, unit)
        """
        if not amount_str or amount_str.strip() == "":
            return None, None

        amount_str = amount_str.strip()
        match = RecipeParser.AMOUNT_PATTERN.search(amount_str)

        if not match:
            return None, amount_str

        amount_part = match.group(1)
        unit = match.group(2) if match.group(2) else None

        # Handle fractions (e.g., "1/2")
        if "/" in amount_part:
            parts = amount_part.split("/")
            try:
                amount = float(parts[0]) / float(parts[1])
            except (ValueError, ZeroDivisionError):
                return None, amount_str
        else:
            try:
                amount = float(amount_part)
            except ValueError:
                return None, amount_str

        return amount, unit

    @staticmethod
    def parse_time(time_str: str) -> Optional[int]:
        """
        Parse time string into minutes.

        Args:
          time_str: Time string (e.g., "30分", "1時間30分")

        Returns:
          Time in minutes, or None if parsing fails
        """
        if not time_str:
            return None

        total_minutes = 0
        matches = RecipeParser.TIME_PATTERN.findall(time_str)

        for value, unit in matches:
            try:
                num = int(value)
                if "時間" in unit or "hour" in unit.lower() or "hr" in unit.lower():
                    total_minutes += num * 60
                else:
                    total_minutes += num
            except ValueError:
                continue

        return total_minutes if total_minutes > 0 else None

    @staticmethod
    def extract_schema_org_recipe(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Extract recipe data from schema.org JSON-LD.

        Args:
          soup: BeautifulSoup object

        Returns:
          Dictionary containing recipe data, or None if not found
        """
        import json

        # Find JSON-LD script tags
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)

                # Handle both single object and array
                if isinstance(data, list):
                    data = next(
                        (item for item in data if item.get("@type") == "Recipe"), None
                    )
                    if not data:
                        continue
                elif data.get("@type") != "Recipe":
                    continue

                # Extract recipe information
                recipe = {
                    "title": data.get("name"),
                    "description": data.get("description"),
                    "ingredients": [],
                    "steps": [],
                    "servings": None,
                    "prep_time": None,
                    "cook_time": None,
                    "source_url": None,
                }

                # Parse ingredients
                ingredients_raw = data.get("recipeIngredient", [])
                for ing in ingredients_raw:
                    if isinstance(ing, str):
                        amount, unit = RecipeParser.parse_amount(ing)
                        # Try to extract ingredient name
                        name = re.sub(RecipeParser.AMOUNT_PATTERN, "", ing).strip()
                        name = RecipeParser.normalize_ingredient(name)

                        recipe["ingredients"].append(
                            {
                                "name": name,
                                "amount": amount,
                                "unit": unit,
                                "raw": ing,
                            }
                        )

                # Parse instructions
                instructions = data.get("recipeInstructions", [])
                if isinstance(instructions, list):
                    for idx, step in enumerate(instructions, 1):
                        if isinstance(step, dict):
                            text = step.get("text", "")
                        else:
                            text = str(step)
                        recipe["steps"].append(
                            {
                                "order": idx,
                                "instruction": text.strip(),
                            }
                        )
                elif isinstance(instructions, str):
                    # Split by newlines or periods
                    steps = re.split(r"\n|。", instructions)
                    for idx, step in enumerate(steps, 1):
                        if step.strip():
                            recipe["steps"].append(
                                {
                                    "order": idx,
                                    "instruction": step.strip(),
                                }
                            )

                # Parse servings
                yield_val = data.get("recipeYield")
                if yield_val:
                    if isinstance(yield_val, (int, float)):
                        recipe["servings"] = int(yield_val)
                    elif isinstance(yield_val, str):
                        match = re.search(r"(\d+)", yield_val)
                        if match:
                            recipe["servings"] = int(match.group(1))

                # Parse times (ISO 8601 duration format)
                prep_time = data.get("prepTime")
                if prep_time:
                    recipe["prep_time"] = RecipeParser._parse_iso_duration(prep_time)

                cook_time = data.get("cookTime")
                if cook_time:
                    recipe["cook_time"] = RecipeParser._parse_iso_duration(cook_time)

                return recipe

            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                logger.debug(f"Failed to parse JSON-LD: {e}")
                continue

        return None

    @staticmethod
    def _parse_iso_duration(duration: str) -> Optional[int]:
        """
        Parse ISO 8601 duration to minutes.

        Args:
          duration: ISO 8601 duration string (e.g., "PT30M", "PT1H30M")

        Returns:
          Duration in minutes, or None if parsing fails
        """
        if not duration or not duration.startswith("PT"):
            return None

        total_minutes = 0
        duration = duration[2:]  # Remove "PT"

        # Extract hours
        hour_match = re.search(r"(\d+)H", duration)
        if hour_match:
            total_minutes += int(hour_match.group(1)) * 60

        # Extract minutes
        min_match = re.search(r"(\d+)M", duration)
        if min_match:
            total_minutes += int(min_match.group(1))

        return total_minutes if total_minutes > 0 else None

    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        """
        Clean and normalize text content.

        Args:
          text: Raw text

        Returns:
          Cleaned text, or None if empty
        """
        if not text:
            return None

        # Remove extra whitespace
        text = " ".join(text.split())

        # Remove common artifacts
        text = text.replace("\xa0", " ")
        text = text.strip()

        return text if text else None

    @staticmethod
    def build_recipe_dict(
        title: Optional[str] = None,
        description: Optional[str] = None,
        ingredients: Optional[List[Dict[str, Any]]] = None,
        steps: Optional[List[Dict[str, Any]]] = None,
        servings: Optional[int] = None,
        prep_time: Optional[int] = None,
        cook_time: Optional[int] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build a standardized recipe dictionary.

        Args:
          title: Recipe title
          description: Recipe description
          ingredients: List of ingredient dictionaries
          steps: List of step dictionaries
          servings: Number of servings
          prep_time: Prep time in minutes
          cook_time: Cook time in minutes
          source_url: Source URL
          metadata: Additional metadata

        Returns:
          Standardized recipe dictionary
        """
        return {
            "title": RecipeParser.clean_text(title),
            "description": RecipeParser.clean_text(description),
            "ingredients": ingredients or [],
            "steps": steps or [],
            "servings": servings,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "source_url": source_url,
            "metadata": metadata or {},
        }

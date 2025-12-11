"""
Generic scraper for extracting recipes from any website.

This scraper attempts to extract recipe data using:
1. schema.org/Recipe structured data (JSON-LD)
2. Common HTML patterns
3. Heuristic-based extraction
"""

import logging
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from backend.scraper.base import BaseScraper, ParseError
from backend.scraper.parser import RecipeParser

logger = logging.getLogger(__name__)


class GenericScraper(BaseScraper):
    """Generic scraper that works with any recipe website."""

    # Common CSS selectors for recipe elements
    TITLE_SELECTORS = [
        "h1.recipe-title",
        "h1[itemprop='name']",
        "h1.entry-title",
        ".recipe-title",
        "h1",
    ]

    DESCRIPTION_SELECTORS = [
        ".recipe-description",
        "[itemprop='description']",
        ".entry-summary",
        "meta[name='description']",
    ]

    INGREDIENTS_SELECTORS = [
        ".ingredients",
        "[itemprop='recipeIngredient']",
        ".ingredient-list",
        ".recipe-ingredients",
    ]

    STEPS_SELECTORS = [
        ".instructions",
        "[itemprop='recipeInstructions']",
        ".recipe-steps",
        ".directions",
    ]

    async def scrape(self, url: str) -> Dict[str, Any]:
        """
        Scrape recipe from any URL.

        Args:
          url: Recipe URL

        Returns:
          Dictionary containing recipe data

        Raises:
          ParseError: If parsing fails
        """
        html = await self.fetch_html(url)
        soup = self.parse_html(html)

        # Try schema.org first (most reliable)
        recipe = RecipeParser.extract_schema_org_recipe(soup)
        if recipe:
            recipe["source_url"] = url
            logger.info(f"Extracted recipe using schema.org: {recipe['title']}")
            return recipe

        # Fallback to heuristic-based extraction
        return self._parse_generic(soup, url)

    def _parse_generic(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Parse recipe using generic patterns.

        Args:
          soup: BeautifulSoup object
          url: Source URL

        Returns:
          Dictionary containing recipe data

        Raises:
          ParseError: If critical elements are missing
        """
        # Extract title
        title = self._extract_by_selectors(soup, self.TITLE_SELECTORS)
        if not title:
            raise ParseError("Failed to extract recipe title")

        # Extract description
        description = self._extract_by_selectors(soup, self.DESCRIPTION_SELECTORS)

        # Extract servings
        servings = self._extract_servings(soup)

        # Extract times
        prep_time = self._extract_time(soup, "prep")
        cook_time = self._extract_time(soup, "cook")

        # Extract ingredients
        ingredients = self._extract_ingredients(soup)

        # Extract steps
        steps = self._extract_steps(soup)

        recipe = RecipeParser.build_recipe_dict(
            title=title,
            description=description,
            ingredients=ingredients,
            steps=steps,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            source_url=url,
            metadata={"scraper": "generic"},
        )

        logger.info(f"Extracted recipe using generic scraper: {title}")
        return recipe

    def _extract_by_selectors(
        self,
        soup: BeautifulSoup,
        selectors: List[str],
    ) -> Optional[str]:
        """
        Extract text using a list of CSS selectors.

        Args:
          soup: BeautifulSoup object
          selectors: List of CSS selectors to try

        Returns:
          Extracted text, or None if not found
        """
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == "meta":
                    return elem.get("content")
                text = elem.get_text(strip=True)
                if text:
                    return text
        return None

    def _extract_servings(self, soup: BeautifulSoup) -> Optional[int]:
        """
        Extract servings information.

        Args:
          soup: BeautifulSoup object

        Returns:
          Number of servings, or None if not found
        """
        # Try common selectors
        servings_selectors = [
            "[itemprop='recipeYield']",
            ".recipe-yield",
            ".servings",
        ]

        for selector in servings_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                match = re.search(r"(\d+)", text)
                if match:
                    return int(match.group(1))

        # Heuristic search
        for text in soup.stripped_strings:
            if any(
                keyword in text.lower()
                for keyword in ["servings", "serves", "人分", "人前"]
            ):
                match = re.search(r"(\d+)", text)
                if match:
                    return int(match.group(1))

        return None

    def _extract_time(self, soup: BeautifulSoup, time_type: str) -> Optional[int]:
        """
        Extract prep or cook time.

        Args:
          soup: BeautifulSoup object
          time_type: "prep" or "cook"

        Returns:
          Time in minutes, or None if not found
        """
        itemprop = "prepTime" if time_type == "prep" else "cookTime"
        keywords = (
            ["prep time", "preparation"]
            if time_type == "prep"
            else ["cook time", "cooking"]
        )
        keywords_ja = (
            ["下準備", "準備時間"] if time_type == "prep" else ["調理時間", "加熱時間"]
        )

        # Try itemprop
        elem = soup.find(attrs={"itemprop": itemprop})
        if elem:
            # Check for datetime attribute (ISO 8601)
            datetime_attr = elem.get("datetime")
            if datetime_attr:
                return RecipeParser._parse_iso_duration(datetime_attr)

            text = elem.get_text(strip=True)
            return RecipeParser.parse_time(text)

        # Try common selectors
        for keyword in keywords + keywords_ja:
            elem = soup.find(
                string=lambda text: text and keyword.lower() in text.lower()
            )
            if elem:
                parent = elem.parent
                if parent:
                    text = parent.get_text(strip=True)
                    time = RecipeParser.parse_time(text)
                    if time:
                        return time

        return None

    def _extract_ingredients(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract ingredients list.

        Args:
          soup: BeautifulSoup object

        Returns:
          List of ingredient dictionaries
        """
        ingredients = []

        # Try to find ingredients container
        container = None
        for selector in self.INGREDIENTS_SELECTORS:
            container = soup.select_one(selector)
            if container:
                break

        if not container:
            # Heuristic search
            for heading in soup.find_all(["h2", "h3", "h4"]):
                heading_text = heading.get_text(strip=True).lower()
                if any(keyword in heading_text for keyword in ["ingredients", "材料"]):
                    # Get next sibling or parent's next sibling
                    container = heading.find_next_sibling(["ul", "ol", "div"])
                    if container:
                        break

        if not container:
            logger.warning("Could not find ingredients container")
            return ingredients

        # Extract ingredients from container
        # Try list items first
        items = container.find_all("li")
        if not items:
            # Try divs or paragraphs
            items = container.find_all(["div", "p"])

        for item in items:
            # Skip if item has nested lists (likely a category header)
            if item.find(["ul", "ol"]):
                continue

            text = item.get_text(strip=True)
            if not text or len(text) < 2:
                continue

            # Try to parse amount and name
            amount, unit = RecipeParser.parse_amount(text)

            # Remove amount part to get name
            name = re.sub(RecipeParser.AMOUNT_PATTERN, "", text).strip()

            # Skip if name is too short or looks like a header
            if len(name) < 2 or name.endswith(":"):
                continue

            name = RecipeParser.normalize_ingredient(name)

            ingredients.append(
                {
                    "name": name,
                    "amount": amount,
                    "unit": unit,
                    "raw": text,
                }
            )

        return ingredients

    def _extract_steps(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract cooking steps.

        Args:
          soup: BeautifulSoup object

        Returns:
          List of step dictionaries
        """
        steps = []

        # Try to find steps container
        container = None
        for selector in self.STEPS_SELECTORS:
            container = soup.select_one(selector)
            if container:
                break

        if not container:
            # Heuristic search
            for heading in soup.find_all(["h2", "h3", "h4"]):
                heading_text = heading.get_text(strip=True).lower()
                if any(
                    keyword in heading_text
                    for keyword in [
                        "instructions",
                        "directions",
                        "steps",
                        "作り方",
                        "手順",
                    ]
                ):
                    # Get next sibling or parent's next sibling
                    container = heading.find_next_sibling(["ol", "ul", "div"])
                    if container:
                        break

        if not container:
            logger.warning("Could not find steps container")
            return steps

        # Extract steps from container
        # Try ordered list items first (most common)
        items = container.find_all("li")
        if not items:
            # Try divs or paragraphs
            items = container.find_all(["div", "p"])

        for idx, item in enumerate(items, 1):
            # Skip if item has nested lists
            if item.find(["ul", "ol"]):
                continue

            instruction = item.get_text(strip=True)

            # Skip empty or very short instructions
            if not instruction or len(instruction) < 5:
                continue

            # Skip if it looks like a header
            if instruction.endswith(":") and len(instruction) < 30:
                continue

            steps.append(
                {
                    "order": idx,
                    "instruction": instruction,
                }
            )

        return steps

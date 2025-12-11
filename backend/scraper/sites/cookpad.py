"""
Cookpad scraper for extracting recipes from cookpad.com.

Cookpad is one of Japan's largest recipe sharing platforms.
"""

import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from backend.scraper.base import BaseScraper, ParseError
from backend.scraper.parser import RecipeParser

logger = logging.getLogger(__name__)


class CookpadScraper(BaseScraper):
    """Scraper for Cookpad recipe pages."""

    async def scrape(self, url: str) -> Dict[str, Any]:
        """
        Scrape recipe from Cookpad URL.

        Args:
          url: Cookpad recipe URL

        Returns:
          Dictionary containing recipe data

        Raises:
          ParseError: If parsing fails
        """
        html = await self.fetch_html(url)
        soup = self.parse_html(html)

        # Try schema.org first
        recipe = RecipeParser.extract_schema_org_recipe(soup)
        if recipe:
            recipe["source_url"] = url
            logger.info(
                f"Extracted recipe from Cookpad using schema.org: {recipe['title']}"
            )
            return recipe

        # Fallback to Cookpad-specific parsing
        return self._parse_cookpad_specific(soup, url)

    def _parse_cookpad_specific(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Parse Cookpad-specific HTML structure.

        Args:
          soup: BeautifulSoup object
          url: Source URL

        Returns:
          Dictionary containing recipe data

        Raises:
          ParseError: If critical elements are missing
        """
        # Extract title
        title = None
        title_elem = soup.find("h1", class_="recipe-title")
        if not title_elem:
            title_elem = soup.find("h1")
        if title_elem:
            title = title_elem.get_text(strip=True)

        if not title:
            raise ParseError("Failed to extract recipe title from Cookpad")

        # Extract description
        description = None
        desc_elem = soup.find("p", class_="description")
        if not desc_elem:
            desc_elem = soup.find("div", class_="description")
        if desc_elem:
            description = desc_elem.get_text(strip=True)

        # Extract servings
        servings = None
        servings_elem = soup.find("span", class_="yield")
        if not servings_elem:
            servings_elem = soup.find(string=lambda text: text and "人分" in text)
        if servings_elem:
            import re

            servings_text = (
                servings_elem.get_text(strip=True)
                if hasattr(servings_elem, "get_text")
                else str(servings_elem)
            )
            match = re.search(r"(\d+)", servings_text)
            if match:
                servings = int(match.group(1))

        # Extract ingredients
        ingredients = self._extract_cookpad_ingredients(soup)

        # Extract steps
        steps = self._extract_cookpad_steps(soup)

        # Extract times (if available)
        prep_time = None
        cook_time = None

        # Some Cookpad recipes have time info
        time_elem = soup.find("span", class_="cooking-time")
        if time_elem:
            cook_time = RecipeParser.parse_time(time_elem.get_text(strip=True))

        recipe = RecipeParser.build_recipe_dict(
            title=title,
            description=description,
            ingredients=ingredients,
            steps=steps,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            source_url=url,
            metadata={"scraper": "cookpad"},
        )

        logger.info(f"Extracted recipe from Cookpad: {title}")
        return recipe

    def _extract_cookpad_ingredients(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract ingredients from Cookpad HTML.

        Args:
          soup: BeautifulSoup object

        Returns:
          List of ingredient dictionaries
        """
        ingredients = []

        # Find ingredients container
        ingredients_container = soup.find("div", class_="ingredient_list")
        if not ingredients_container:
            ingredients_container = soup.find("div", id="ingredients_list")
        if not ingredients_container:
            logger.warning("Could not find ingredients container")
            return ingredients

        # Find all ingredient items
        ingredient_items = ingredients_container.find_all("li", class_="ingredient")
        if not ingredient_items:
            ingredient_items = ingredients_container.find_all(
                "div", class_="ingredient"
            )

        for item in ingredient_items:
            # Extract name
            name_elem = item.find("span", class_="name")
            if not name_elem:
                name_elem = item.find("div", class_="ingredient_name")

            # Extract amount
            amount_elem = item.find("span", class_="amount")
            if not amount_elem:
                amount_elem = item.find("div", class_="ingredient_quantity")

            if name_elem:
                name = name_elem.get_text(strip=True)
                name = RecipeParser.normalize_ingredient(name)

                amount_str = amount_elem.get_text(strip=True) if amount_elem else ""
                amount, unit = RecipeParser.parse_amount(amount_str)

                ingredients.append(
                    {
                        "name": name,
                        "amount": amount,
                        "unit": unit,
                        "raw": f"{name} {amount_str}".strip(),
                    }
                )

        return ingredients

    def _extract_cookpad_steps(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract cooking steps from Cookpad HTML.

        Args:
          soup: BeautifulSoup object

        Returns:
          List of step dictionaries
        """
        steps = []

        # Find steps container
        steps_container = soup.find("div", class_="steps")
        if not steps_container:
            steps_container = soup.find("ol", class_="steps")
        if not steps_container:
            steps_container = soup.find("div", id="steps")

        if not steps_container:
            logger.warning("Could not find steps container")
            return steps

        # Find all step items
        step_items = steps_container.find_all("li", class_="step")
        if not step_items:
            step_items = steps_container.find_all("div", class_="step")

        for idx, item in enumerate(step_items, 1):
            # Extract step text
            text_elem = item.find("p", class_="step_text")
            if not text_elem:
                text_elem = item.find("div", class_="step_text")
            if not text_elem:
                text_elem = item

            instruction = text_elem.get_text(strip=True)

            if instruction:
                steps.append(
                    {
                        "order": idx,
                        "instruction": instruction,
                    }
                )

        return steps

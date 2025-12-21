"""
Delish Kitchen scraper for extracting recipes from delishkitchen.tv.

Delish Kitchen is a popular Japanese recipe video platform.
"""

import logging
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from backend.scraper.base import BaseScraper, ParseError
from backend.scraper.parser import RecipeParser

logger = logging.getLogger(__name__)


class DelishKitchenScraper(BaseScraper):
    """Scraper for Delish Kitchen recipe pages."""

    async def scrape(self, url: str) -> Dict[str, Any]:
        """
        Scrape recipe from Delish Kitchen URL.

        Args:
          url: Delish Kitchen recipe URL

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
                f"Extracted recipe from Delish Kitchen using schema.org: {recipe['title']}"
            )
            return recipe

        # Fallback to Delish Kitchen-specific parsing
        return self._parse_delish_kitchen_specific(soup, url)

    def _parse_delish_kitchen_specific(
        self, soup: BeautifulSoup, url: str
    ) -> Dict[str, Any]:
        """
        Parse Delish Kitchen-specific HTML structure.

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
            title_elem = soup.find("h1", {"data-testid": "recipe-title"})
        if not title_elem:
            title_elem = soup.find("h1")
        if title_elem:
            title = title_elem.get_text(strip=True)

        if not title:
            raise ParseError("Failed to extract recipe title from Delish Kitchen")

        # Extract description
        description = None
        desc_elem = soup.find("p", class_="recipe-description")
        if not desc_elem:
            desc_elem = soup.find("div", class_="description")
        if not desc_elem:
            desc_elem = soup.find("meta", {"name": "description"})
            if desc_elem:
                description = desc_elem.get("content")
        if desc_elem and not description:
            description = desc_elem.get_text(strip=True)

        # Extract servings
        servings = None
        servings_elem = soup.find("span", class_="servings")
        if not servings_elem:
            servings_elem = soup.find(
                string=lambda text: text and ("人前" in text or "人分" in text)
            )
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
        ingredients = self._extract_delish_kitchen_ingredients(soup)

        # Extract steps
        steps = self._extract_delish_kitchen_steps(soup)

        # Extract times
        prep_time = self._extract_time(soup, "prep")
        cook_time = self._extract_time(soup, "cook")

        recipe = RecipeParser.build_recipe_dict(
            title=title,
            description=description,
            ingredients=ingredients,
            steps=steps,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            source_url=url,
            metadata={"scraper": "delish_kitchen"},
        )

        logger.info(f"Extracted recipe from Delish Kitchen: {title}")
        return recipe

    def _extract_delish_kitchen_ingredients(
        self, soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
        """
        Extract ingredients from Delish Kitchen HTML.

        Args:
          soup: BeautifulSoup object

        Returns:
          List of ingredient dictionaries
        """
        ingredients = []

        # Find ingredients container
        ingredients_container = soup.find("div", class_="ingredients")
        if not ingredients_container:
            ingredients_container = soup.find("ul", class_="ingredient-list")
        if not ingredients_container:
            ingredients_container = soup.find("div", {"data-testid": "ingredients"})

        if not ingredients_container:
            logger.warning("Could not find ingredients container")
            return ingredients

        # Find all ingredient items
        ingredient_items = ingredients_container.find_all("li")
        if not ingredient_items:
            ingredient_items = ingredients_container.find_all(
                "div", class_="ingredient-item"
            )

        for item in ingredient_items:
            # Try different patterns for name and amount
            name_elem = item.find("span", class_="ingredient-name")
            amount_elem = item.find("span", class_="ingredient-amount")

            if not name_elem:
                # Alternative pattern: name and amount in separate divs
                name_elem = item.find("div", class_="name")
                amount_elem = item.find("div", class_="amount")

            if not name_elem:
                # Fallback: parse entire text
                text = item.get_text(strip=True)
                if text:
                    # Try to split by common separators
                    parts = text.split("…")
                    if len(parts) == 2:
                        name = parts[0].strip()
                        amount_str = parts[1].strip()
                    else:
                        # Use regex to separate amount from name
                        import re

                        match = re.match(r"^([^0-9]+)(.+)$", text)
                        if match:
                            name = match.group(1).strip()
                            amount_str = match.group(2).strip()
                        else:
                            name = text
                            amount_str = ""
            else:
                name = name_elem.get_text(strip=True)
                amount_str = amount_elem.get_text(strip=True) if amount_elem else ""

            if name:
                name = RecipeParser.normalize_ingredient(name)
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

    def _extract_delish_kitchen_steps(
        self, soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
        """
        Extract cooking steps from Delish Kitchen HTML.

        Args:
          soup: BeautifulSoup object

        Returns:
          List of step dictionaries
        """
        steps = []

        # Find steps container
        steps_container = soup.find("div", class_="steps")
        if not steps_container:
            steps_container = soup.find("ol", class_="recipe-steps")
        if not steps_container:
            steps_container = soup.find("div", {"data-testid": "steps"})

        if not steps_container:
            logger.warning("Could not find steps container")
            return steps

        # Find all step items
        step_items = steps_container.find_all("li")
        if not step_items:
            step_items = steps_container.find_all("div", class_="step")

        for idx, item in enumerate(step_items, 1):
            # Extract step text
            text_elem = item.find("p")
            if not text_elem:
                text_elem = item.find("div", class_="step-text")
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

    def _extract_time(self, soup: BeautifulSoup, time_type: str) -> Optional[int]:
        """
        Extract prep or cook time from Delish Kitchen HTML.

        Args:
          soup: BeautifulSoup object
          time_type: "prep" or "cook"

        Returns:
          Time in minutes, or None if not found
        """
        time_elem = None

        if time_type == "prep":
            time_elem = soup.find("span", class_="prep-time")
            if not time_elem:
                time_elem = soup.find(string=lambda text: text and "下準備" in text)
        elif time_type == "cook":
            time_elem = soup.find("span", class_="cook-time")
            if not time_elem:
                time_elem = soup.find(string=lambda text: text and "調理時間" in text)

        if time_elem:
            time_text = (
                time_elem.get_text(strip=True)
                if hasattr(time_elem, "get_text")
                else str(time_elem)
            )
            return RecipeParser.parse_time(time_text)

        return None

"""
Enhanced search service for Personal Recipe Intelligence.

Provides:
- Fuzzy search for recipe titles (あいまい検索)
- Search by ingredients (材料検索)
- Combined search (title + ingredients)
- Search ranking/scoring
- Partial match support
"""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Optional

from sqlmodel import Session, select

from backend.models.recipe import Ingredient, Recipe


@dataclass
class SearchResult:
    """Search result with relevance score."""

    recipe: Recipe
    score: float
    match_type: str  # 'title', 'ingredient', 'combined'
    matched_terms: List[str]


class SearchService:
    """Enhanced search service for recipes."""

    def __init__(self, session: Session):
        """
        Initialize search service.

        Args:
          session: Database session
        """
        self.session = session
        self.fuzzy_threshold = 0.6  # Minimum similarity ratio for fuzzy matches

    def fuzzy_search(
        self,
        query: str,
        limit: int = 20,
        threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Fuzzy search for recipe titles.

        Supports:
        - Exact matches (highest score)
        - Partial matches
        - Similar text (using sequence matching)
        - Japanese text

        Args:
          query: Search query
          limit: Maximum number of results
          threshold: Minimum similarity threshold (default: 0.6)

        Returns:
          List of SearchResult sorted by relevance
        """
        if threshold is None:
            threshold = self.fuzzy_threshold

        query_normalized = self._normalize_text(query)
        results: List[SearchResult] = []

        # Fetch all recipes
        statement = select(Recipe)
        recipes = self.session.exec(statement).all()

        for recipe in recipes:
            title_normalized = self._normalize_text(recipe.title)
            score = self._calculate_title_score(query_normalized, title_normalized)

            if score >= threshold:
                results.append(
                    SearchResult(
                        recipe=recipe,
                        score=score,
                        match_type="title",
                        matched_terms=[query],
                    )
                )

        # Sort by score (descending)
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def search_by_ingredients(
        self,
        ingredient_names: List[str],
        match_all: bool = False,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Search recipes by ingredients.

        Args:
          ingredient_names: List of ingredient names to search
          match_all: If True, recipe must contain ALL ingredients.
                     If False, recipe must contain ANY ingredient.
          limit: Maximum number of results

        Returns:
          List of SearchResult sorted by number of matching ingredients
        """
        if not ingredient_names:
            return []

        normalized_names = [self._normalize_text(name) for name in ingredient_names]
        results: List[SearchResult] = []

        # Fetch all recipes with their ingredients
        statement = select(Recipe)
        recipes = self.session.exec(statement).all()

        for recipe in recipes:
            matched_ingredients = []
            recipe_ingredients = self._get_recipe_ingredients(recipe.id)

            for query_ingredient in normalized_names:
                for recipe_ingredient in recipe_ingredients:
                    ingredient_normalized = self._normalize_text(recipe_ingredient)
                    if self._is_ingredient_match(
                        query_ingredient, ingredient_normalized
                    ):
                        matched_ingredients.append(recipe_ingredient)
                        break

            # Check if recipe meets criteria
            if match_all:
                if len(matched_ingredients) == len(ingredient_names):
                    score = 1.0
                else:
                    continue  # Skip this recipe
            else:
                if not matched_ingredients:
                    continue  # Skip if no matches
                score = len(matched_ingredients) / len(ingredient_names)

            results.append(
                SearchResult(
                    recipe=recipe,
                    score=score,
                    match_type="ingredient",
                    matched_terms=matched_ingredients,
                )
            )

        # Sort by score (descending), then by number of matched ingredients
        results.sort(key=lambda x: (x.score, len(x.matched_terms)), reverse=True)
        return results[:limit]

    def combined_search(
        self,
        title_query: Optional[str] = None,
        ingredient_names: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Combined search by title and ingredients.

        Combines scores from both title and ingredient matches.

        Args:
          title_query: Recipe title search query
          ingredient_names: List of ingredient names
          limit: Maximum number of results

        Returns:
          List of SearchResult sorted by combined relevance
        """
        if not title_query and not ingredient_names:
            return []

        # Store recipes with their combined scores
        recipe_scores: Dict[int, SearchResult] = {}

        # Title search
        if title_query:
            title_results = self.fuzzy_search(title_query, limit=100)
            for result in title_results:
                recipe_scores[result.recipe.id] = SearchResult(
                    recipe=result.recipe,
                    score=result.score * 0.6,  # Title weight: 60%
                    match_type="combined",
                    matched_terms=result.matched_terms,
                )

        # Ingredient search
        if ingredient_names:
            ingredient_results = self.search_by_ingredients(
                ingredient_names, match_all=False, limit=100
            )
            for result in ingredient_results:
                if result.recipe.id in recipe_scores:
                    # Combine scores
                    existing = recipe_scores[result.recipe.id]
                    existing.score += result.score * 0.4  # Ingredient weight: 40%
                    existing.matched_terms.extend(result.matched_terms)
                else:
                    recipe_scores[result.recipe.id] = SearchResult(
                        recipe=result.recipe,
                        score=result.score * 0.4,
                        match_type="combined",
                        matched_terms=result.matched_terms,
                    )

        # Convert to list and sort
        results = list(recipe_scores.values())
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def advanced_search(
        self,
        query: Optional[str] = None,
        ingredients: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Advanced search with multiple criteria.

        Args:
          query: General search query (searches in title and description)
          ingredients: Required ingredients
          tags: Recipe tags
          limit: Maximum number of results

        Returns:
          List of SearchResult sorted by relevance
        """
        results: Dict[int, SearchResult] = {}

        # Base query results
        if query or ingredients:
            combined_results = self.combined_search(
                title_query=query, ingredient_names=ingredients, limit=100
            )
            for result in combined_results:
                results[result.recipe.id] = result

        # Filter by tags if specified
        if tags:
            if not results:
                # If no previous results, search all recipes
                statement = select(Recipe)
                all_recipes = self.session.exec(statement).all()
                for recipe in all_recipes:
                    results[recipe.id] = SearchResult(
                        recipe=recipe,
                        score=0.0,
                        match_type="tag",
                        matched_terms=[],
                    )

            # Filter and score by tags
            normalized_tags = [self._normalize_text(tag) for tag in tags]
            filtered_results = {}

            for recipe_id, result in results.items():
                recipe_tags = self._get_recipe_tags(result.recipe.id)
                matched_tags = []

                for query_tag in normalized_tags:
                    for recipe_tag in recipe_tags:
                        if self._normalize_text(recipe_tag) == query_tag:
                            matched_tags.append(recipe_tag)
                            break

                if matched_tags:
                    tag_score = len(matched_tags) / len(normalized_tags)
                    result.score += tag_score * 0.3  # Tag weight: 30%
                    result.matched_terms.extend(matched_tags)
                    filtered_results[recipe_id] = result

            results = filtered_results

        # Convert to list and sort
        final_results = list(results.values())
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results[:limit]

    # Private helper methods

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.

        - Converts to lowercase
        - Removes extra whitespace
        - Handles Japanese text properly

        Args:
          text: Input text

        Returns:
          Normalized text
        """
        if not text:
            return ""

        # Convert to lowercase (works with ASCII, Japanese stays as-is)
        normalized = text.lower()

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def _calculate_title_score(self, query: str, title: str) -> float:
        """
        Calculate similarity score between query and title.

        Scoring logic:
        - Exact match: 1.0
        - Title contains query: 0.9
        - Query contains title: 0.85
        - Fuzzy match: SequenceMatcher ratio

        Args:
          query: Normalized query
          title: Normalized title

        Returns:
          Similarity score (0.0 to 1.0)
        """
        if not query or not title:
            return 0.0

        # Exact match
        if query == title:
            return 1.0

        # Title contains query (partial match)
        if query in title:
            return 0.9

        # Query contains title
        if title in query:
            return 0.85

        # Fuzzy match using sequence matcher
        ratio = SequenceMatcher(None, query, title).ratio()
        return ratio

    def _is_ingredient_match(self, query: str, ingredient: str) -> bool:
        """
        Check if ingredient matches query.

        Supports:
        - Exact match
        - Partial match (ingredient contains query or vice versa)

        Args:
          query: Normalized query ingredient
          ingredient: Normalized recipe ingredient

        Returns:
          True if match, False otherwise
        """
        if not query or not ingredient:
            return False

        # Exact match
        if query == ingredient:
            return True

        # Partial match
        if query in ingredient or ingredient in query:
            return True

        return False

    def _get_recipe_ingredients(self, recipe_id: int) -> List[str]:
        """
        Get all ingredient names for a recipe.

        Args:
          recipe_id: Recipe ID

        Returns:
          List of ingredient names
        """
        statement = select(Ingredient).where(Ingredient.recipe_id == recipe_id)
        ingredients = self.session.exec(statement).all()
        return [ing.name for ing in ingredients if ing.name]

    def _get_recipe_tags(self, recipe_id: int) -> List[str]:
        """
        Get all tags for a recipe.

        Args:
          recipe_id: Recipe ID

        Returns:
          List of tag names
        """
        # Fetch recipe
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe or not recipe.tags:
            return []

        # Parse tags (assuming comma-separated or similar format)
        if isinstance(recipe.tags, str):
            return [tag.strip() for tag in recipe.tags.split(",") if tag.strip()]
        elif isinstance(recipe.tags, list):
            return recipe.tags

        return []

"""
Recipe service for Personal Recipe Intelligence.

Provides CRUD operations and search functionality for recipes.
"""

from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from backend.models.recipe import Ingredient, Recipe
from backend.services.search_service import SearchResult, SearchService


class RecipeService:
    """Service for managing recipes."""

    def __init__(self, session: Session):
        """
        Initialize recipe service.

        Args:
          session: Database session
        """
        self.session = session
        self.search_service = SearchService(session)

    # CRUD Operations

    def create_recipe(self, recipe_data: Dict[str, Any]) -> Recipe:
        """
        Create a new recipe.

        Args:
          recipe_data: Recipe data dictionary

        Returns:
          Created Recipe instance
        """
        recipe = Recipe(**recipe_data)
        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """
        Get recipe by ID.

        Args:
          recipe_id: Recipe ID

        Returns:
          Recipe instance or None if not found
        """
        return self.session.get(Recipe, recipe_id)

    def get_all_recipes(self, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """
        Get all recipes with pagination.

        Args:
          skip: Number of records to skip
          limit: Maximum number of records to return

        Returns:
          List of Recipe instances
        """
        statement = select(Recipe).offset(skip).limit(limit)
        recipes = self.session.exec(statement).all()
        return list(recipes)

    def update_recipe(
        self, recipe_id: int, recipe_data: Dict[str, Any]
    ) -> Optional[Recipe]:
        """
        Update an existing recipe.

        Args:
          recipe_id: Recipe ID
          recipe_data: Updated recipe data

        Returns:
          Updated Recipe instance or None if not found
        """
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe:
            return None

        for key, value in recipe_data.items():
            setattr(recipe, key, value)

        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def delete_recipe(self, recipe_id: int) -> bool:
        """
        Delete a recipe.

        Args:
          recipe_id: Recipe ID

        Returns:
          True if deleted, False if not found
        """
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe:
            return False

        self.session.delete(recipe)
        self.session.commit()
        return True

    # Search Methods

    def fuzzy_search(
        self,
        query: str,
        limit: int = 20,
        threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Fuzzy search for recipe titles (あいまい検索).

        Supports:
        - Exact matches
        - Partial matches
        - Similar text matching
        - Japanese text

        Args:
          query: Search query
          limit: Maximum number of results
          threshold: Minimum similarity threshold (0.0 to 1.0)

        Returns:
          List of SearchResult sorted by relevance

        Examples:
          >>> service.fuzzy_search("カレー")
          [SearchResult(recipe=<Recipe: カレーライス>, score=0.95, ...)]

          >>> service.fuzzy_search("chicken", limit=10)
          [SearchResult(recipe=<Recipe: Chicken Curry>, score=0.9, ...)]
        """
        return self.search_service.fuzzy_search(
            query=query, limit=limit, threshold=threshold
        )

    def search_by_ingredients(
        self,
        ingredient_names: List[str],
        match_all: bool = False,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Search recipes by ingredients (材料検索).

        Args:
          ingredient_names: List of ingredient names to search
          match_all: If True, recipe must contain ALL ingredients.
                     If False, recipe must contain ANY ingredient.
          limit: Maximum number of results

        Returns:
          List of SearchResult sorted by number of matching ingredients

        Examples:
          >>> service.search_by_ingredients(["玉ねぎ", "にんじん"])
          [SearchResult(recipe=<Recipe: カレー>, score=1.0, matched_terms=['玉ねぎ', 'にんじん'])]

          >>> service.search_by_ingredients(["chicken", "tomato"], match_all=True)
          [SearchResult(recipe=<Recipe: Chicken Stew>, score=1.0, ...)]
        """
        return self.search_service.search_by_ingredients(
            ingredient_names=ingredient_names, match_all=match_all, limit=limit
        )

    def combined_search(
        self,
        title_query: Optional[str] = None,
        ingredient_names: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Combined search by title and ingredients.

        Combines scores from both title (60% weight) and ingredient (40% weight) matches.

        Args:
          title_query: Recipe title search query
          ingredient_names: List of ingredient names
          limit: Maximum number of results

        Returns:
          List of SearchResult sorted by combined relevance

        Examples:
          >>> service.combined_search(title_query="カレー", ingredient_names=["じゃがいも"])
          [SearchResult(recipe=<Recipe: カレーライス>, score=0.95, ...)]
        """
        return self.search_service.combined_search(
            title_query=title_query, ingredient_names=ingredient_names, limit=limit
        )

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
          query: General search query (searches in title)
          ingredients: Required ingredients
          tags: Recipe tags
          limit: Maximum number of results

        Returns:
          List of SearchResult sorted by relevance

        Examples:
          >>> service.advanced_search(
          ...   query="カレー",
          ...   ingredients=["じゃがいも"],
          ...   tags=["和食", "簡単"]
          ... )
          [SearchResult(recipe=<Recipe: カレーライス>, score=0.98, ...)]
        """
        return self.search_service.advanced_search(
            query=query, ingredients=ingredients, tags=tags, limit=limit
        )

    def search_recipes(self, query: str, limit: int = 20) -> List[Recipe]:
        """
        Simple search for recipes (backward compatibility).

        Searches in recipe title using fuzzy matching.

        Args:
          query: Search query
          limit: Maximum number of results

        Returns:
          List of Recipe instances
        """
        results = self.fuzzy_search(query=query, limit=limit)
        return [result.recipe for result in results]

    # Ingredient Management

    def add_ingredient(
        self, recipe_id: int, ingredient_data: Dict[str, Any]
    ) -> Optional[Ingredient]:
        """
        Add ingredient to a recipe.

        Args:
          recipe_id: Recipe ID
          ingredient_data: Ingredient data dictionary

        Returns:
          Created Ingredient instance or None if recipe not found
        """
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe:
            return None

        ingredient = Ingredient(recipe_id=recipe_id, **ingredient_data)
        self.session.add(ingredient)
        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient

    def get_recipe_ingredients(self, recipe_id: int) -> List[Ingredient]:
        """
        Get all ingredients for a recipe.

        Args:
          recipe_id: Recipe ID

        Returns:
          List of Ingredient instances
        """
        statement = select(Ingredient).where(Ingredient.recipe_id == recipe_id)
        ingredients = self.session.exec(statement).all()
        return list(ingredients)

    def update_ingredient(
        self, ingredient_id: int, ingredient_data: Dict[str, Any]
    ) -> Optional[Ingredient]:
        """
        Update an ingredient.

        Args:
          ingredient_id: Ingredient ID
          ingredient_data: Updated ingredient data

        Returns:
          Updated Ingredient instance or None if not found
        """
        ingredient = self.session.get(Ingredient, ingredient_id)
        if not ingredient:
            return None

        for key, value in ingredient_data.items():
            setattr(ingredient, key, value)

        self.session.add(ingredient)
        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient

    def delete_ingredient(self, ingredient_id: int) -> bool:
        """
        Delete an ingredient.

        Args:
          ingredient_id: Ingredient ID

        Returns:
          True if deleted, False if not found
        """
        ingredient = self.session.get(Ingredient, ingredient_id)
        if not ingredient:
            return False

        self.session.delete(ingredient)
        self.session.commit()
        return True

    # Utility Methods

    def get_recipes_by_tag(self, tag: str, limit: int = 20) -> List[Recipe]:
        """
        Get recipes by tag.

        Args:
          tag: Tag to search for
          limit: Maximum number of results

        Returns:
          List of Recipe instances
        """
        statement = select(Recipe).where(Recipe.tags.contains(tag)).limit(limit)
        recipes = self.session.exec(statement).all()
        return list(recipes)

    def get_recipe_count(self) -> int:
        """
        Get total number of recipes.

        Returns:
          Number of recipes
        """
        statement = select(Recipe)
        recipes = self.session.exec(statement).all()
        return len(list(recipes))

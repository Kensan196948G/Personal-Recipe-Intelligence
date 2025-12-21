# Models Module
from sqlmodel import SQLModel

# SQLModel uses SQLModel as base class
Base = SQLModel

from .recipe import Recipe, RecipeBase, Ingredient, IngredientBase, Tag, RecipeTag, Step, StepBase
from .shopping_list import (
    ShoppingList,
    ShoppingListBase,
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListRead,
    ShoppingListItem,
    ShoppingListItemBase,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListItemRead,
)

__all__ = [
    "Base",
    "SQLModel",
    "Recipe",
    "RecipeBase",
    "Ingredient",
    "IngredientBase",
    "Tag",
    "RecipeTag",
    "Step",
    "StepBase",
    "ShoppingList",
    "ShoppingListBase",
    "ShoppingListCreate",
    "ShoppingListUpdate",
    "ShoppingListRead",
    "ShoppingListItem",
    "ShoppingListItemBase",
    "ShoppingListItemCreate",
    "ShoppingListItemUpdate",
    "ShoppingListItemRead",
]

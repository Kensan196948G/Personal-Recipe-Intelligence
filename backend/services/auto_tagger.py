"""
Auto-tagging service for Personal Recipe Intelligence.

This module analyzes recipe data and suggests relevant tags based on:
- Cuisine type (和食, 洋食, 中華, etc.)
- Meal type (朝食, 昼食, 夕食, デザート)
- Cooking method (炒め物, 煮物, 焼き物, 揚げ物)
- Main ingredient (肉, 魚, 野菜)
- Dietary preferences (ベジタリアン, ヘルシー)
- And more

Uses keyword matching against configurable rules defined in config/tag_rules.json.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set


class AutoTagger:
  """
  Auto-tagging service for recipe analysis.

  Analyzes recipe titles, descriptions, and ingredients to suggest
  relevant tags based on keyword matching rules.
  """

  def __init__(self, rules_path: Optional[str] = None):
    """
    Initialize the AutoTagger with tag rules.

    Args:
      rules_path: Path to tag_rules.json file. If None, uses default path.
    """
    if rules_path is None:
      # Default path relative to project root
      project_root = Path(__file__).parent.parent.parent
      rules_path = project_root / "config" / "tag_rules.json"

    self.rules_path = Path(rules_path)
    self.rules: Dict[str, Dict[str, List[str]]] = {}
    self._load_rules()

  def _load_rules(self) -> None:
    """Load tag rules from JSON configuration file."""
    try:
      with open(self.rules_path, "r", encoding="utf-8") as f:
        self.rules = json.load(f)
    except FileNotFoundError:
      raise FileNotFoundError(
        f"Tag rules file not found at {self.rules_path}. "
        "Please ensure config/tag_rules.json exists."
      )
    except json.JSONDecodeError as e:
      raise ValueError(f"Invalid JSON in tag rules file: {e}")

  def _normalize_text(self, text: str) -> str:
    """
    Normalize text for keyword matching.

    Args:
      text: Input text to normalize

    Returns:
      Normalized text (lowercase, whitespace normalized)
    """
    if not text:
      return ""

    # Convert to lowercase (for English)
    text = text.lower()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text

  def _match_keywords(
    self,
    text: str,
    keywords: List[str],
    case_sensitive: bool = False
  ) -> bool:
    """
    Check if any keyword matches in the text.

    Args:
      text: Text to search in
      keywords: List of keywords to match
      case_sensitive: Whether to perform case-sensitive matching

    Returns:
      True if any keyword found, False otherwise
    """
    if not text or not keywords:
      return False

    search_text = text if case_sensitive else self._normalize_text(text)

    for keyword in keywords:
      search_keyword = keyword if case_sensitive else self._normalize_text(keyword)
      if search_keyword in search_text:
        return True

    return False

  def suggest_tags(
    self,
    title: str = "",
    description: str = "",
    ingredients: Optional[List[str]] = None,
    instructions: Optional[List[str]] = None,
    max_tags: Optional[int] = None
  ) -> List[str]:
    """
    Suggest tags for a recipe based on its content.

    Args:
      title: Recipe title
      description: Recipe description
      ingredients: List of ingredient names or full ingredient strings
      instructions: List of cooking instructions
      max_tags: Maximum number of tags to return (None = no limit)

    Returns:
      List of suggested tag names, sorted by relevance
    """
    suggested_tags: Set[str] = set()

    # Combine all text for analysis
    all_text = " ".join(filter(None, [
      title,
      description,
      " ".join(ingredients or []),
      " ".join(instructions or [])
    ]))

    if not all_text.strip():
      return []

    # Analyze each category in the rules
    for category, tag_mapping in self.rules.items():
      for tag_name, keywords in tag_mapping.items():
        if self._match_keywords(all_text, keywords):
          suggested_tags.add(tag_name)

    # Convert to sorted list for consistent output
    result = sorted(suggested_tags)

    # Apply max_tags limit if specified
    if max_tags is not None and max_tags > 0:
      result = result[:max_tags]

    return result

  def suggest_tags_by_category(
    self,
    title: str = "",
    description: str = "",
    ingredients: Optional[List[str]] = None,
    instructions: Optional[List[str]] = None
  ) -> Dict[str, List[str]]:
    """
    Suggest tags grouped by category.

    Args:
      title: Recipe title
      description: Recipe description
      ingredients: List of ingredient names or full ingredient strings
      instructions: List of cooking instructions

    Returns:
      Dictionary mapping category names to lists of suggested tags
    """
    categorized_tags: Dict[str, List[str]] = {}

    # Combine all text for analysis
    all_text = " ".join(filter(None, [
      title,
      description,
      " ".join(ingredients or []),
      " ".join(instructions or [])
    ]))

    if not all_text.strip():
      return categorized_tags

    # Analyze each category
    for category, tag_mapping in self.rules.items():
      category_tags = []

      for tag_name, keywords in tag_mapping.items():
        if self._match_keywords(all_text, keywords):
          category_tags.append(tag_name)

      if category_tags:
        categorized_tags[category] = sorted(category_tags)

    return categorized_tags

  def get_all_tags(self) -> List[str]:
    """
    Get all possible tags defined in the rules.

    Returns:
      Sorted list of all tag names
    """
    all_tags = set()

    for tag_mapping in self.rules.values():
      all_tags.update(tag_mapping.keys())

    return sorted(all_tags)

  def get_tags_by_category(self, category: str) -> List[str]:
    """
    Get all tags for a specific category.

    Args:
      category: Category name (e.g., 'cuisine_type', 'meal_type')

    Returns:
      List of tag names in the category
    """
    if category not in self.rules:
      return []

    return sorted(self.rules[category].keys())

  def get_categories(self) -> List[str]:
    """
    Get all available tag categories.

    Returns:
      List of category names
    """
    return sorted(self.rules.keys())

  def add_custom_rule(
    self,
    category: str,
    tag_name: str,
    keywords: List[str]
  ) -> None:
    """
    Add a custom tagging rule at runtime.

    Args:
      category: Category name
      tag_name: Tag name to assign
      keywords: List of keywords that trigger this tag
    """
    if category not in self.rules:
      self.rules[category] = {}

    self.rules[category][tag_name] = keywords

  def reload_rules(self) -> None:
    """
    Reload tag rules from the configuration file.

    Useful if the rules file has been updated externally.
    """
    self._load_rules()


# Convenience function for quick tag suggestion
def suggest_recipe_tags(
  title: str = "",
  description: str = "",
  ingredients: Optional[List[str]] = None,
  instructions: Optional[List[str]] = None,
  max_tags: Optional[int] = None,
  rules_path: Optional[str] = None
) -> List[str]:
  """
  Quick function to suggest tags for a recipe.

  Args:
    title: Recipe title
    description: Recipe description
    ingredients: List of ingredient names
    instructions: List of cooking instructions
    max_tags: Maximum number of tags to return
    rules_path: Custom path to tag rules file

  Returns:
    List of suggested tag names
  """
  tagger = AutoTagger(rules_path=rules_path)
  return tagger.suggest_tags(
    title=title,
    description=description,
    ingredients=ingredients,
    instructions=instructions,
    max_tags=max_tags
  )

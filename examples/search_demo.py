"""
Search functionality demonstration script.

Demonstrates the usage of fuzzy search, ingredient search,
and combined search in Personal Recipe Intelligence.
"""

from sqlmodel import Session, create_engine, SQLModel
from backend.models.recipe import Recipe, Ingredient
from backend.services import RecipeService, SearchService


def create_sample_data(session: Session) -> None:
  """
  Create sample recipes for demonstration.

  Args:
    session: Database session
  """
  print("Creating sample recipes...")

  # Recipe 1: カレーライス
  recipe1 = Recipe(
    title="カレーライス",
    description="基本的なカレーライスのレシピです。野菜と肉を炒めて煮込むだけの簡単料理。",
    tags="和食,簡単,人気",
  )
  session.add(recipe1)
  session.commit()
  session.refresh(recipe1)

  ingredients1 = [
    Ingredient(recipe_id=recipe1.id, name="玉ねぎ", quantity="2個"),
    Ingredient(recipe_id=recipe1.id, name="にんじん", quantity="1本"),
    Ingredient(recipe_id=recipe1.id, name="じゃがいも", quantity="3個"),
    Ingredient(recipe_id=recipe1.id, name="豚肉", quantity="300g"),
    Ingredient(recipe_id=recipe1.id, name="カレールー", quantity="1箱"),
  ]
  for ing in ingredients1:
    session.add(ing)

  # Recipe 2: チキンカレー
  recipe2 = Recipe(
    title="チキンカレー",
    description="鶏肉を使ったスパイシーなカレー。トマトベースでヘルシー。",
    tags="洋食,簡単,スパイシー",
  )
  session.add(recipe2)
  session.commit()
  session.refresh(recipe2)

  ingredients2 = [
    Ingredient(recipe_id=recipe2.id, name="鶏もも肉", quantity="400g"),
    Ingredient(recipe_id=recipe2.id, name="玉ねぎ", quantity="2個"),
    Ingredient(recipe_id=recipe2.id, name="トマト", quantity="3個"),
    Ingredient(recipe_id=recipe2.id, name="にんにく", quantity="2片"),
    Ingredient(recipe_id=recipe2.id, name="カレー粉", quantity="大さじ3"),
  ]
  for ing in ingredients2:
    session.add(ing)

  # Recipe 3: ポテトサラダ
  recipe3 = Recipe(
    title="ポテトサラダ",
    description="定番のポテトサラダ。お弁当にもぴったり。",
    tags="和食,簡単,サラダ",
  )
  session.add(recipe3)
  session.commit()
  session.refresh(recipe3)

  ingredients3 = [
    Ingredient(recipe_id=recipe3.id, name="じゃがいも", quantity="5個"),
    Ingredient(recipe_id=recipe3.id, name="にんじん", quantity="1本"),
    Ingredient(recipe_id=recipe3.id, name="きゅうり", quantity="1本"),
    Ingredient(recipe_id=recipe3.id, name="ハム", quantity="4枚"),
    Ingredient(recipe_id=recipe3.id, name="マヨネーズ", quantity="大さじ4"),
  ]
  for ing in ingredients3:
    session.add(ing)

  # Recipe 4: トマトパスタ
  recipe4 = Recipe(
    title="トマトパスタ",
    description="シンプルなトマトソースのパスタ。",
    tags="洋食,簡単,パスタ",
  )
  session.add(recipe4)
  session.commit()
  session.refresh(recipe4)

  ingredients4 = [
    Ingredient(recipe_id=recipe4.id, name="パスタ", quantity="200g"),
    Ingredient(recipe_id=recipe4.id, name="トマト缶", quantity="1缶"),
    Ingredient(recipe_id=recipe4.id, name="にんにく", quantity="2片"),
    Ingredient(recipe_id=recipe4.id, name="オリーブオイル", quantity="大さじ2"),
    Ingredient(recipe_id=recipe4.id, name="バジル", quantity="適量"),
  ]
  for ing in ingredients4:
    session.add(ing)

  # Recipe 5: 肉じゃが
  recipe5 = Recipe(
    title="肉じゃが",
    description="和食の定番、甘辛い煮物。",
    tags="和食,煮物,人気",
  )
  session.add(recipe5)
  session.commit()
  session.refresh(recipe5)

  ingredients5 = [
    Ingredient(recipe_id=recipe5.id, name="牛肉", quantity="200g"),
    Ingredient(recipe_id=recipe5.id, name="じゃがいも", quantity="4個"),
    Ingredient(recipe_id=recipe5.id, name="玉ねぎ", quantity="1個"),
    Ingredient(recipe_id=recipe5.id, name="にんじん", quantity="1本"),
    Ingredient(recipe_id=recipe5.id, name="しらたき", quantity="1袋"),
  ]
  for ing in ingredients5:
    session.add(ing)

  session.commit()
  print("Sample recipes created successfully!\n")


def demo_fuzzy_search(service: RecipeService) -> None:
  """
  Demonstrate fuzzy search functionality.

  Args:
    service: Recipe service instance
  """
  print("=" * 60)
  print("1. FUZZY SEARCH DEMO (あいまい検索)")
  print("=" * 60)

  queries = ["カレー", "パスタ", "ポテト", "肉"]

  for query in queries:
    print(f"\nQuery: '{query}'")
    print("-" * 40)
    results = service.fuzzy_search(query, limit=5)

    if results:
      for i, result in enumerate(results, 1):
        print(
          f"{i}. {result.recipe.title} (スコア: {result.score:.2f})"
        )
    else:
      print("No results found.")

  # Custom threshold example
  print(f"\n\nQuery: 'カレー' (threshold=0.85)")
  print("-" * 40)
  results = service.fuzzy_search("カレー", threshold=0.85)
  for i, result in enumerate(results, 1):
    print(f"{i}. {result.recipe.title} (スコア: {result.score:.2f})")


def demo_ingredient_search(service: RecipeService) -> None:
  """
  Demonstrate ingredient search functionality.

  Args:
    service: Recipe service instance
  """
  print("\n\n" + "=" * 60)
  print("2. INGREDIENT SEARCH DEMO (材料検索)")
  print("=" * 60)

  # Single ingredient
  print(f"\nSearch: じゃがいも")
  print("-" * 40)
  results = service.search_by_ingredients(["じゃがいも"])
  for i, result in enumerate(results, 1):
    print(
      f"{i}. {result.recipe.title} (マッチ: {', '.join(result.matched_terms)})"
    )

  # Multiple ingredients (OR)
  print(f"\n\nSearch: 玉ねぎ OR にんじん (いずれか)")
  print("-" * 40)
  results = service.search_by_ingredients(
    ["玉ねぎ", "にんじん"], match_all=False
  )
  for i, result in enumerate(results, 1):
    print(
      f"{i}. {result.recipe.title} (マッチ: {', '.join(result.matched_terms)}, スコア: {result.score:.2f})"
    )

  # Multiple ingredients (AND)
  print(f"\n\nSearch: 玉ねぎ AND にんじん (両方)")
  print("-" * 40)
  results = service.search_by_ingredients(
    ["玉ねぎ", "にんじん"], match_all=True
  )
  for i, result in enumerate(results, 1):
    print(
      f"{i}. {result.recipe.title} (マッチ: {', '.join(result.matched_terms)})"
    )


def demo_combined_search(service: RecipeService) -> None:
  """
  Demonstrate combined search functionality.

  Args:
    service: Recipe service instance
  """
  print("\n\n" + "=" * 60)
  print("3. COMBINED SEARCH DEMO (複合検索)")
  print("=" * 60)

  # Title only
  print(f"\nSearch: title='カレー'")
  print("-" * 40)
  results = service.combined_search(title_query="カレー")
  for i, result in enumerate(results, 1):
    print(f"{i}. {result.recipe.title} (スコア: {result.score:.2f})")

  # Ingredients only
  print(f"\n\nSearch: ingredients=['じゃがいも']")
  print("-" * 40)
  results = service.combined_search(ingredient_names=["じゃがいも"])
  for i, result in enumerate(results, 1):
    print(f"{i}. {result.recipe.title} (スコア: {result.score:.2f})")

  # Both title and ingredients
  print(f"\n\nSearch: title='カレー' + ingredients=['じゃがいも']")
  print("-" * 40)
  results = service.combined_search(
    title_query="カレー", ingredient_names=["じゃがいも"]
  )
  for i, result in enumerate(results, 1):
    print(
      f"{i}. {result.recipe.title} (スコア: {result.score:.2f}, マッチ: {', '.join(result.matched_terms)})"
    )


def demo_advanced_search(service: RecipeService) -> None:
  """
  Demonstrate advanced search functionality.

  Args:
    service: Recipe service instance
  """
  print("\n\n" + "=" * 60)
  print("4. ADVANCED SEARCH DEMO (高度な検索)")
  print("=" * 60)

  # Search by tags only
  print(f"\nSearch: tags=['簡単']")
  print("-" * 40)
  results = service.advanced_search(tags=["簡単"])
  for i, result in enumerate(results, 1):
    print(f"{i}. {result.recipe.title} (タグ: {result.recipe.tags})")

  # Complex search
  print(
    f"\n\nSearch: query='カレー' + ingredients=['玉ねぎ'] + tags=['簡単']"
  )
  print("-" * 40)
  results = service.advanced_search(
    query="カレー", ingredients=["玉ねぎ"], tags=["簡単"]
  )
  for i, result in enumerate(results, 1):
    print(
      f"{i}. {result.recipe.title} (スコア: {result.score:.2f}, タグ: {result.recipe.tags})"
    )


def main():
  """Main demonstration function."""
  print("\n" + "=" * 60)
  print("Personal Recipe Intelligence - Search Demo")
  print("=" * 60 + "\n")

  # Create in-memory database
  engine = create_engine("sqlite:///:memory:")
  SQLModel.metadata.create_all(engine)

  with Session(engine) as session:
    # Create sample data
    create_sample_data(session)

    # Initialize service
    service = RecipeService(session)

    # Run demonstrations
    demo_fuzzy_search(service)
    demo_ingredient_search(service)
    demo_combined_search(service)
    demo_advanced_search(service)

  print("\n\n" + "=" * 60)
  print("Demo completed successfully!")
  print("=" * 60 + "\n")


if __name__ == "__main__":
  main()

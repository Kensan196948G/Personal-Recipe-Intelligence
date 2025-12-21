"""
レシピ自動生成機能の使用例

このスクリプトは、レシピ生成サービスの基本的な使い方を示します。
"""

from backend.services.recipe_generator_service import RecipeGeneratorService
import json


def main():
  """メイン処理"""
  # サービスの初期化
  generator = RecipeGeneratorService(data_dir="data/generator")

  print("=" * 60)
  print("Personal Recipe Intelligence - レシピ自動生成デモ")
  print("=" * 60)
  print()

  # 1. 基本的なレシピ生成
  print("1. 基本的なレシピ生成")
  print("-" * 60)
  recipe1 = generator.generate_recipe(
    ingredients=["鶏肉"],
    category="japanese"
  )
  print(f"レシピ名: {recipe1['name']}")
  print(f"カテゴリ: {recipe1['category']}")
  print(f"調理時間: {recipe1['cooking_time']}分")
  print(f"難易度: {recipe1['difficulty']}")
  print()

  # 2. 複数食材でのレシピ生成
  print("2. 複数食材でのレシピ生成")
  print("-" * 60)
  recipe2 = generator.generate_recipe(
    ingredients=["豚肉", "キャベツ", "玉ねぎ"],
    category="chinese",
    cooking_time=20,
    difficulty="easy"
  )
  print(f"レシピ名: {recipe2['name']}")
  print(f"材料: {len(recipe2['ingredients'])}種類")
  print(f"手順数: {len(recipe2['steps'])}ステップ")
  print()
  print("材料リスト:")
  for ing in recipe2['ingredients'][:5]:
    print(f"  - {ing['name']}: {ing['amount']} {ing['unit']}")
  print()

  # 3. 食材組み合わせ提案
  print("3. 食材組み合わせ提案")
  print("-" * 60)
  suggestions = generator.suggest_ingredient_combinations(
    main_ingredient="鮭",
    count=3
  )
  print(f"「鮭」に合う食材:")
  for suggestion in suggestions:
    seasonal_badge = " [旬]" if suggestion['seasonal'] else ""
    print(f"  - {suggestion['sub']} (相性スコア: {suggestion['compatibility_score']}){seasonal_badge}")
  print()

  # 4. バリエーション生成
  print("4. バリエーション生成")
  print("-" * 60)
  variations = generator.generate_variations(
    base_recipe=recipe1,
    count=2
  )
  print(f"元レシピ「{recipe1['name']}」のバリエーション:")
  for i, variation in enumerate(variations, 1):
    print(f"  {i}. {variation['name']} ({variation['method']})")
  print()

  # 5. レシピ改善
  print("5. レシピ改善")
  print("-" * 60)

  # 味を改善
  improved_taste = generator.improve_recipe(recipe1, focus="taste")
  print(f"【味改善版】")
  print(f"  追加された調味料数: {len(improved_taste['ingredients']) - len(recipe1['ingredients'])}")

  # ヘルシーに改善
  improved_health = generator.improve_recipe(recipe1, focus="health")
  print(f"【ヘルシー版】")
  print(f"  タグ: {improved_health['tags']}")

  # 時短に改善
  improved_speed = generator.improve_recipe(recipe2, focus="speed")
  print(f"【時短版】")
  print(f"  調理時間: {recipe2['cooking_time']}分 → {improved_speed['cooking_time']}分")

  print()

  # 6. 栄養バランス評価
  print("6. 栄養バランス評価")
  print("-" * 60)
  nutrition = generator.get_nutrition_estimate(recipe2)
  print(f"たんぱく質: {'○' if nutrition['has_protein'] else '×'}")
  print(f"野菜: {'○' if nutrition['has_vegetable'] else '×'}")
  print(f"炭水化物: {'○' if nutrition['has_carbohydrate'] else '×'}")
  print(f"バランススコア: {nutrition['balance_score']}%")
  print(f"推奨事項: {nutrition['recommendation']}")
  print()

  # 7. 様々なカテゴリでの生成
  print("7. 様々なカテゴリでの生成")
  print("-" * 60)
  categories = ["japanese", "western", "chinese"]
  for category in categories:
    recipe = generator.generate_recipe(
      ingredients=["鶏肉", "トマト"],
      category=category,
      difficulty="easy"
    )
    print(f"{category.upper():8s}: {recipe['name']}")
  print()

  # 8. 詳細レシピの出力
  print("8. 詳細レシピの出力")
  print("-" * 60)
  detailed_recipe = generator.generate_recipe(
    ingredients=["エビ", "ブロッコリー"],
    category="western",
    use_seasonal=True
  )
  print(f"【{detailed_recipe['name']}】")
  print(f"調理時間: {detailed_recipe['cooking_time']}分 | 難易度: {detailed_recipe['difficulty']} | {detailed_recipe['servings']}人分")
  print()
  print("■ 材料")
  for ing in detailed_recipe['ingredients']:
    print(f"  • {ing['name']:<15s} {ing['amount']} {ing['unit']}")
  print()
  print("■ 作り方")
  for i, step in enumerate(detailed_recipe['steps'], 1):
    print(f"  {i}. {step}")
  print()

  # レシピをJSONファイルに保存
  output_file = "data/generator/example_recipe.json"
  with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(detailed_recipe, f, ensure_ascii=False, indent=2)
  print(f"レシピを保存しました: {output_file}")
  print()

  print("=" * 60)
  print("デモ完了")
  print("=" * 60)


if __name__ == "__main__":
  main()

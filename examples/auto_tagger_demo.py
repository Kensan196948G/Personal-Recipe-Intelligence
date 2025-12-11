#!/usr/bin/env python3
"""
Auto-Tagger Demo Script

Demonstrates the auto-tagging functionality with various recipe examples.
"""

from backend.services.auto_tagger import AutoTagger, suggest_recipe_tags


def print_section(title: str) -> None:
  """Print a section header."""
  print("\n" + "=" * 60)
  print(f"  {title}")
  print("=" * 60)


def demo_basic_usage():
  """Demonstrate basic tag suggestion."""
  print_section("基本的な使い方")

  tagger = AutoTagger()

  # Example 1: 親子丼
  print("\n【レシピ1: 親子丼】")
  tags = tagger.suggest_tags(
    title="親子丼",
    description="鶏肉と卵でとじる定番の丼物",
    ingredients=[
      "鶏もも肉 200g",
      "卵 3個",
      "玉ねぎ 1個",
      "醤油 大さじ2",
      "みりん 大さじ2",
      "だし汁 200ml"
    ],
    instructions=[
      "玉ねぎをスライスする",
      "鶏肉を一口大に切る",
      "だし汁に調味料を加え煮立てる",
      "鶏肉と玉ねぎを煮る",
      "溶き卵でとじる"
    ]
  )
  print(f"提案タグ: {', '.join(tags)}")

  # Example 2: カルボナーラ
  print("\n【レシピ2: カルボナーラ】")
  tags = tagger.suggest_tags(
    title="濃厚カルボナーラ",
    description="クリーミーで美味しいイタリアンパスタ",
    ingredients=[
      "スパゲッティ 200g",
      "ベーコン 100g",
      "卵黄 2個",
      "パルメザンチーズ 50g",
      "生クリーム 100ml"
    ]
  )
  print(f"提案タグ: {', '.join(tags)}")

  # Example 3: 麻婆豆腐
  print("\n【レシピ3: 麻婆豆腐】")
  tags = tagger.suggest_tags(
    title="本格麻婆豆腐",
    description="ピリ辛で美味しい中華の定番料理",
    ingredients=[
      "豆腐 1丁",
      "豚ひき肉 150g",
      "長ねぎ 1本",
      "豆板醤 大さじ1",
      "ごま油 大さじ1"
    ]
  )
  print(f"提案タグ: {', '.join(tags)}")


def demo_categorized_tags():
  """Demonstrate categorized tag suggestion."""
  print_section("カテゴリ別タグ提案")

  tagger = AutoTagger()

  print("\n【レシピ: 鶏の唐揚げ】")
  categorized = tagger.suggest_tags_by_category(
    title="ジューシー唐揚げ",
    description="外はカリッと中はジューシーな定番おかず",
    ingredients=[
      "鶏もも肉 400g",
      "醤油 大さじ2",
      "生姜 1片",
      "にんにく 1片",
      "片栗粉 適量"
    ],
    instructions=[
      "鶏肉を一口大に切る",
      "調味料に漬け込む",
      "片栗粉をまぶす",
      "油で揚げる"
    ]
  )

  for category, tags in categorized.items():
    print(f"\n  {category}:")
    for tag in tags:
      print(f"    - {tag}")


def demo_max_tags():
  """Demonstrate max_tags parameter."""
  print_section("タグ数制限")

  tagger = AutoTagger()

  recipe_title = "野菜たっぷりヘルシー炒め"
  recipe_ingredients = [
    "キャベツ",
    "人参",
    "ピーマン",
    "もやし",
    "豚肉",
    "ごま油",
    "醤油"
  ]

  print(f"\n【レシピ: {recipe_title}】")
  print(f"材料: {', '.join(recipe_ingredients)}")

  print("\n制限なし:")
  tags_unlimited = tagger.suggest_tags(
    title=recipe_title,
    ingredients=recipe_ingredients
  )
  print(f"  {', '.join(tags_unlimited)} (合計{len(tags_unlimited)}個)")

  print("\n最大5個:")
  tags_limited = tagger.suggest_tags(
    title=recipe_title,
    ingredients=recipe_ingredients,
    max_tags=5
  )
  print(f"  {', '.join(tags_limited)} (合計{len(tags_limited)}個)")


def demo_convenience_function():
  """Demonstrate convenience function."""
  print_section("簡易関数の使用")

  print("\n【レシピ: チョコレートケーキ】")
  tags = suggest_recipe_tags(
    title="濃厚チョコレートケーキ",
    description="しっとり美味しいデザート",
    ingredients=["チョコレート", "卵", "砂糖", "バター", "薄力粉"]
  )
  print(f"提案タグ: {', '.join(tags)}")


def demo_utility_methods():
  """Demonstrate utility methods."""
  print_section("ユーティリティメソッド")

  tagger = AutoTagger()

  # Get all categories
  print("\n【利用可能なカテゴリ】")
  categories = tagger.get_categories()
  for cat in categories:
    print(f"  - {cat}")

  # Get tags by category
  print("\n【料理ジャンル (cuisine_type) のタグ一覧】")
  cuisine_tags = tagger.get_tags_by_category("cuisine_type")
  print(f"  {', '.join(cuisine_tags)}")

  # Get all tags
  print("\n【すべてのタグ (最初の20個のみ表示)】")
  all_tags = tagger.get_all_tags()
  print(f"  {', '.join(all_tags[:20])}...")
  print(f"  (合計 {len(all_tags)} 個のタグ)")


def demo_seasonal_recipes():
  """Demonstrate seasonal tag detection."""
  print_section("季節のレシピ検出")

  tagger = AutoTagger()

  recipes = [
    {
      "title": "春キャベツのサラダ",
      "ingredients": ["春キャベツ", "新玉ねぎ", "桜えび"],
      "season": "春"
    },
    {
      "title": "夏野菜カレー",
      "ingredients": ["トマト", "なす", "ピーマン", "ズッキーニ"],
      "season": "夏"
    },
    {
      "title": "秋の味覚の炊き込みご飯",
      "ingredients": ["栗", "しめじ", "さつまいも", "米"],
      "season": "秋"
    },
    {
      "title": "冬の温かい鍋",
      "ingredients": ["白菜", "大根", "ねぎ", "豆腐"],
      "season": "冬"
    }
  ]

  for recipe in recipes:
    print(f"\n【{recipe['title']}】")
    tags = tagger.suggest_tags(
      title=recipe["title"],
      ingredients=recipe["ingredients"]
    )
    seasonal_tags = [tag for tag in tags if tag in ["春", "夏", "秋", "冬"]]
    print(f"  検出された季節タグ: {', '.join(seasonal_tags)}")
    print(f"  全タグ: {', '.join(tags)}")


def demo_dietary_preferences():
  """Demonstrate dietary preference detection."""
  print_section("食事制限・健康タグ")

  tagger = AutoTagger()

  recipes = [
    {
      "title": "ベジタリアン野菜カレー",
      "description": "肉不使用の野菜たっぷりカレー"
    },
    {
      "title": "ヘルシーサラダ",
      "description": "低カロリーでダイエットに最適"
    },
    {
      "title": "高タンパク鶏むねステーキ",
      "description": "鶏むね肉で筋トレ後の食事に"
    },
    {
      "title": "グルテンフリーパン",
      "description": "小麦不使用の米粉パン"
    }
  ]

  for recipe in recipes:
    print(f"\n【{recipe['title']}】")
    tags = tagger.suggest_tags(
      title=recipe["title"],
      description=recipe["description"]
    )
    dietary_tags = [
      tag for tag in tags
      if tag in ["ベジタリアン", "ヴィーガン", "ヘルシー", "グルテンフリー", "高タンパク"]
    ]
    print(f"  食事制限タグ: {', '.join(dietary_tags) if dietary_tags else 'なし'}")


def demo_cooking_time():
  """Demonstrate cooking time detection."""
  print_section("調理時間タグ")

  tagger = AutoTagger()

  recipes = [
    {"title": "5分で完成！簡単サラダ", "time": "5分"},
    {"title": "10分レシピ パスタ", "time": "10分"},
    {"title": "じっくり煮込むビーフシチュー", "time": "1時間以上"}
  ]

  for recipe in recipes:
    print(f"\n【{recipe['title']}】")
    tags = tagger.suggest_tags(title=recipe["title"])
    time_tags = [
      tag for tag in tags
      if "分以内" in tag or "時間以上" in tag
    ]
    print(f"  検出された調理時間タグ: {', '.join(time_tags) if time_tags else 'なし'}")


def main():
  """Run all demos."""
  print("\n")
  print("╔" + "=" * 58 + "╗")
  print("║" + " " * 10 + "Personal Recipe Intelligence" + " " * 20 + "║")
  print("║" + " " * 15 + "Auto-Tagger デモンストレーション" + " " * 11 + "║")
  print("╚" + "=" * 58 + "╝")

  try:
    demo_basic_usage()
    demo_categorized_tags()
    demo_max_tags()
    demo_convenience_function()
    demo_utility_methods()
    demo_seasonal_recipes()
    demo_dietary_preferences()
    demo_cooking_time()

    print_section("デモ完了")
    print("\nすべてのデモが正常に実行されました！")
    print("詳細は docs/auto-tagging.md を参照してください。\n")

  except Exception as e:
    print(f"\nエラーが発生しました: {e}")
    import traceback
    traceback.print_exc()


if __name__ == "__main__":
  main()

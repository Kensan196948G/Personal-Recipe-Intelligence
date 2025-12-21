"""
栄養計算機能の使用例

このスクリプトは栄養計算機能の実装例を示します。
"""

from backend.services.nutrition_service import NutritionService


def example_1_simple_calculation():
    """例1: シンプルな栄養計算"""
    print("=" * 60)
    print("例1: シンプルな栄養計算")
    print("=" * 60)

    service = NutritionService()

    # レシピの材料
    ingredients = [
        {"name": "白米", "amount": "150g"},
        {"name": "鶏むね肉", "amount": "100g"},
        {"name": "ブロッコリー", "amount": "80g"},
    ]

    # 1人前の栄養計算
    result = service.calculate_recipe_nutrition(ingredients, servings=1)

    print("\n【レシピ】")
    for ing in ingredients:
        print(f"  - {ing['name']}: {ing['amount']}")

    print("\n【1人前の栄養価】")
    per_serving = result["per_serving"]
    print(f"  カロリー: {per_serving['calories']} kcal")
    print(f"  タンパク質: {per_serving['protein']} g")
    print(f"  脂質: {per_serving['fat']} g")
    print(f"  炭水化物: {per_serving['carbohydrates']} g")
    print(f"  食物繊維: {per_serving['fiber']} g")

    # サマリー情報
    summary = service.get_nutrition_summary(result)
    print("\n【栄養分析】")
    print(f"  カロリーレベル: {summary['calorie_level']}")
    print(f"  PFCバランス: {summary['pfc_balance']}")
    print()


def example_2_multi_serving():
    """例2: 複数人前の計算"""
    print("=" * 60)
    print("例2: 複数人前の計算")
    print("=" * 60)

    service = NutritionService()

    # 4人前のレシピ
    ingredients = [
        {"name": "白米", "amount": "600g"},
        {"name": "鶏もも肉", "amount": "400g"},
        {"name": "玉ねぎ", "amount": "2個"},
        {"name": "にんじん", "amount": "1個"},
    ]

    result = service.calculate_recipe_nutrition(ingredients, servings=4)

    print("\n【レシピ（4人前）】")
    for ing in ingredients:
        print(f"  - {ing['name']}: {ing['amount']}")

    print("\n【合計栄養価】")
    total = result["total"]
    print(f"  カロリー: {total['calories']} kcal")
    print(f"  タンパク質: {total['protein']} g")

    print("\n【1人前の栄養価】")
    per_serving = result["per_serving"]
    print(f"  カロリー: {per_serving['calories']} kcal")
    print(f"  タンパク質: {per_serving['protein']} g")
    print()


def example_3_detailed_breakdown():
    """例3: 材料ごとの詳細分析"""
    print("=" * 60)
    print("例3: 材料ごとの詳細分析")
    print("=" * 60)

    service = NutritionService()

    ingredients = [
        {"name": "豚バラ肉", "amount": "200g"},
        {"name": "キャベツ", "amount": "300g"},
        {"name": "もやし", "amount": "150g"},  # 未登録材料
    ]

    result = service.calculate_recipe_nutrition(ingredients, servings=2)

    print("\n【材料ごとの栄養価】")
    for item in result["ingredients_breakdown"]:
        if item["found"]:
            print(f"\n  {item['ingredient']} ({item['amount']})")
            print(f"    カロリー: {item['calories']} kcal")
            print(f"    タンパク質: {item['protein']} g")
            print(f"    脂質: {item['fat']} g")
        else:
            print(f"\n  {item['ingredient']} ({item['amount']})")
            print("    ⚠ 栄養データが見つかりません")

    print("\n【集計】")
    print(f"  登録材料: {result['found_ingredients']}/{result['total_ingredients']}")
    print()


def example_4_ingredient_search():
    """例4: 材料検索"""
    print("=" * 60)
    print("例4: 材料検索")
    print("=" * 60)

    service = NutritionService()

    # 鶏肉を検索
    print("\n【「鶏」で検索】")
    results = service.search_ingredients("鶏")
    for item in results[:3]:  # 上位3件
        print(f"  - {item['name']}: {item['calories']} kcal/100g")

    # 野菜を検索
    print("\n【「キャベツ」で検索】")
    results = service.search_ingredients("キャベツ")
    for item in results:
        print(f"  - {item['name']}: {item['calories']} kcal/100g")
    print()


def example_5_various_units():
    """例5: 様々な単位の計算"""
    print("=" * 60)
    print("例5: 様々な単位の計算")
    print("=" * 60)

    service = NutritionService()

    ingredients = [
        {"name": "醤油", "amount": "大さじ2"},
        {"name": "砂糖", "amount": "小さじ1"},
        {"name": "サラダ油", "amount": "大さじ1"},
        {"name": "卵", "amount": "2個"},
    ]

    result = service.calculate_recipe_nutrition(ingredients, servings=1)

    print("\n【材料と換算】")
    for item in result["ingredients_breakdown"]:
        if item["found"]:
            print(
                f"  {item['ingredient']} {item['amount']} → {item['amount_g']}g / {item['calories']} kcal"
            )

    print("\n【合計カロリー】")
    print(f"  {result['total']['calories']} kcal")
    print()


def example_6_balanced_meal():
    """例6: バランスの良い食事"""
    print("=" * 60)
    print("例6: バランスの良い食事の分析")
    print("=" * 60)

    service = NutritionService()

    # 理想的な食事例
    ingredients = [
        {"name": "白米", "amount": "150g"},
        {"name": "サーモン", "amount": "100g"},
        {"name": "ブロッコリー", "amount": "100g"},
        {"name": "トマト", "amount": "50g"},
        {"name": "豆腐", "amount": "100g"},
    ]

    result = service.calculate_recipe_nutrition(ingredients, servings=1)
    summary = service.get_nutrition_summary(result)

    print("\n【バランスの良い食事】")
    for ing in ingredients:
        print(f"  - {ing['name']}: {ing['amount']}")

    print("\n【栄養価】")
    per_serving = result["per_serving"]
    print(f"  カロリー: {per_serving['calories']} kcal")
    print(f"  タンパク質: {per_serving['protein']} g")
    print(f"  脂質: {per_serving['fat']} g")
    print(f"  炭水化物: {per_serving['carbohydrates']} g")
    print(f"  食物繊維: {per_serving['fiber']} g")

    print("\n【PFCバランス】")
    print(f"  {summary['pfc_balance']}")
    print(f"  タンパク質: {summary['protein_ratio']}%")
    print(f"  脂質: {summary['fat_ratio']}%")
    print(f"  炭水化物: {summary['carb_ratio']}%")

    print("\n【評価】")
    print(f"  カロリーレベル: {summary['calorie_level']}")

    # 理想的なPFCバランスとの比較
    ideal_p = 20.0
    ideal_f = 25.0
    ideal_c = 55.0

    p_diff = abs(summary["protein_ratio"] - ideal_p)
    f_diff = abs(summary["fat_ratio"] - ideal_f)
    c_diff = abs(summary["carb_ratio"] - ideal_c)

    if p_diff < 5 and f_diff < 5 and c_diff < 5:
        print("  ✓ 理想的なPFCバランスです！")
    else:
        print("  △ PFCバランスを調整すると良いでしょう")
    print()


def example_7_comparison():
    """例7: レシピの比較"""
    print("=" * 60)
    print("例7: レシピの比較")
    print("=" * 60)

    service = NutritionService()

    # レシピA: 高タンパク・低脂質
    recipe_a = [
        {"name": "白米", "amount": "150g"},
        {"name": "鶏むね肉", "amount": "150g"},
        {"name": "ブロッコリー", "amount": "100g"},
    ]

    # レシピB: 高カロリー
    recipe_b = [
        {"name": "白米", "amount": "150g"},
        {"name": "豚バラ肉", "amount": "150g"},
        {"name": "キャベツ", "amount": "100g"},
    ]

    result_a = service.calculate_recipe_nutrition(recipe_a, servings=1)
    result_b = service.calculate_recipe_nutrition(recipe_b, servings=1)

    summary_a = service.get_nutrition_summary(result_a)
    summary_b = service.get_nutrition_summary(result_b)

    print("\n【レシピA: ヘルシー】")
    print(f"  カロリー: {result_a['per_serving']['calories']} kcal")
    print(f"  タンパク質: {result_a['per_serving']['protein']} g")
    print(f"  脂質: {result_a['per_serving']['fat']} g")
    print(f"  PFC: {summary_a['pfc_balance']}")

    print("\n【レシピB: 高カロリー】")
    print(f"  カロリー: {result_b['per_serving']['calories']} kcal")
    print(f"  タンパク質: {result_b['per_serving']['protein']} g")
    print(f"  脂質: {result_b['per_serving']['fat']} g")
    print(f"  PFC: {summary_b['pfc_balance']}")

    print("\n【比較】")
    cal_diff = result_b["per_serving"]["calories"] - result_a["per_serving"]["calories"]
    fat_diff = result_b["per_serving"]["fat"] - result_a["per_serving"]["fat"]
    print(f"  カロリー差: +{cal_diff} kcal")
    print(f"  脂質差: +{fat_diff} g")
    print()


def main():
    """すべての例を実行"""
    print("\n栄養計算機能の使用例\n")

    example_1_simple_calculation()
    example_2_multi_serving()
    example_3_detailed_breakdown()
    example_4_ingredient_search()
    example_5_various_units()
    example_6_balanced_meal()
    example_7_comparison()

    print("=" * 60)
    print("すべての例を実行しました")
    print("=" * 60)


if __name__ == "__main__":
    main()

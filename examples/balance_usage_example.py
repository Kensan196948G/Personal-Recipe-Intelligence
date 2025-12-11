"""
食事バランス可視化機能の使用例

BalanceService と API の使い方を示すサンプルコード
"""

from backend.services.balance_service import BalanceService
import json


def example_1_pfc_balance():
  """例1: PFCバランスの計算"""
  print("=" * 60)
  print("例1: PFCバランスの計算")
  print("=" * 60)

  # レシピの栄養データ
  nutrition = {
    "protein": 25,   # タンパク質 25g
    "fat": 20,       # 脂質 20g
    "carbs": 85      # 炭水化物 85g
  }

  # PFCバランスを計算
  result = BalanceService.calculate_pfc_balance(nutrition)

  print(f"\n【PFC比率】")
  print(f"  タンパク質: {result['protein_ratio']:.1%} ({result['protein_cal']:.1f}kcal)")
  print(f"  脂質:       {result['fat_ratio']:.1%} ({result['fat_cal']:.1f}kcal)")
  print(f"  炭水化物:   {result['carbs_ratio']:.1%} ({result['carbs_cal']:.1f}kcal)")
  print(f"\n【評価】")
  print(f"  総カロリー: {result['total_cal']:.1f}kcal")
  print(f"  バランススコア: {result['balance_score']:.1f}/100")
  print(f"  バランス: {'良好' if result['is_balanced'] else '要改善'}")
  print(f"\n【アドバイス】")
  for rec in result['recommendations']:
    print(f"  - {rec}")

  print(f"\n【円グラフデータ】")
  print(json.dumps(result['pie_chart_data'], indent=2, ensure_ascii=False))


def example_2_daily_balance():
  """例2: 1日の食事バランス評価"""
  print("\n\n" + "=" * 60)
  print("例2: 1日の食事バランス評価")
  print("=" * 60)

  # 1日3食のデータ
  meals = [
    # 朝食
    {
      "calories": 450,
      "protein": 15,
      "fat": 12,
      "carbs": 70,
      "fiber": 4,
      "salt": 1.5
    },
    # 昼食
    {
      "calories": 750,
      "protein": 28,
      "fat": 25,
      "carbs": 95,
      "fiber": 7,
      "salt": 3.0
    },
    # 夕食
    {
      "calories": 650,
      "protein": 22,
      "fat": 18,
      "carbs": 85,
      "fiber": 6,
      "salt": 2.5
    }
  ]

  # 1日のバランスを評価
  result = BalanceService.evaluate_daily_balance(meals)

  print(f"\n【合計摂取量】")
  print(f"  カロリー:   {result['total']['calories']:.0f} kcal")
  print(f"  タンパク質: {result['total']['protein']:.1f} g")
  print(f"  脂質:       {result['total']['fat']:.1f} g")
  print(f"  炭水化物:   {result['total']['carbs']:.1f} g")
  print(f"  食物繊維:   {result['total']['fiber']:.1f} g")
  print(f"  塩分:       {result['total']['salt']:.1f} g")

  print(f"\n【充足率（対 1日の基準値）】")
  for nutrient, percent in result['fulfillment'].items():
    status = "✓" if 80 <= percent <= 120 else "!"
    print(f"  {status} {nutrient:10s}: {percent:5.1f}%")

  print(f"\n【評価】")
  print(f"  総合スコア: {result['overall_score']:.1f}/100")
  print(f"  評価レベル: {result['evaluation_level']}")

  print(f"\n【アドバイス】")
  for rec in result['recommendations']:
    print(f"  - {rec}")


def example_3_nutrition_score():
  """例3: 栄養バランススコアの算出"""
  print("\n\n" + "=" * 60)
  print("例3: 栄養バランススコアの算出")
  print("=" * 60)

  # レシピの栄養データ
  nutrition = {
    "calories": 650,
    "protein": 25,
    "fat": 20,
    "carbs": 85,
    "fiber": 5,
    "salt": 2.5
  }

  # スコアを計算
  result = BalanceService.calculate_nutrition_score(nutrition)

  print(f"\n【総合評価】")
  print(f"  総合スコア: {result['overall_score']:.1f}/100")
  print(f"  PFCスコア:  {result['pfc_score']:.1f}/100")
  print(f"  評価:       {result['evaluation']}")
  print(f"  健康的:     {'はい' if result['is_healthy'] else 'いいえ'}")

  print(f"\n【栄養素別スコア】")
  for nutrient, score in result['nutrient_scores'].items():
    print(f"  {nutrient:10s}: {score:5.1f}/100")


def example_4_recipe_evaluation():
  """例4: レシピのバランス評価（完全版）"""
  print("\n\n" + "=" * 60)
  print("例4: レシピのバランス評価（完全版）")
  print("=" * 60)

  # レシピの栄養データ
  nutrition = {
    "calories": 650,
    "protein": 25,
    "fat": 20,
    "carbs": 85,
    "fiber": 5,
    "salt": 2.5
  }

  # 完全な評価を取得
  result = BalanceService.get_recipe_balance_evaluation(nutrition)

  print(f"\n【栄養情報】")
  for key, value in result['nutrition'].items():
    print(f"  {key:10s}: {value}")

  print(f"\n【PFCバランス】")
  pfc = result['pfc_balance']
  print(f"  タンパク質比率: {pfc['protein_ratio']:.1%}")
  print(f"  脂質比率:       {pfc['fat_ratio']:.1%}")
  print(f"  炭水化物比率:   {pfc['carbs_ratio']:.1%}")
  print(f"  バランススコア: {pfc['balance_score']:.1f}/100")

  print(f"\n【総合スコア】")
  score = result['score']
  print(f"  総合スコア: {score['overall_score']:.1f}/100")
  print(f"  評価:       {score['evaluation']}")

  print(f"\n【1日の基準値に対する割合】")
  for nutrient, percent in result['daily_reference_percentage'].items():
    print(f"  {nutrient:10s}: {percent:5.1f}%")


def example_5_compare_recipes():
  """例5: 複数レシピの比較"""
  print("\n\n" + "=" * 60)
  print("例5: 複数レシピの比較")
  print("=" * 60)

  # 3つのレシピ
  recipes = [
    {
      "name": "ハンバーグ定食",
      "nutrition": {
        "calories": 850,
        "protein": 30,
        "fat": 40,
        "carbs": 90,
        "fiber": 4,
        "salt": 3.5
      }
    },
    {
      "name": "焼き魚定食",
      "nutrition": {
        "calories": 650,
        "protein": 28,
        "fat": 18,
        "carbs": 85,
        "fiber": 6,
        "salt": 2.5
      }
    },
    {
      "name": "野菜炒め定食",
      "nutrition": {
        "calories": 600,
        "protein": 20,
        "fat": 22,
        "carbs": 75,
        "fiber": 8,
        "salt": 2.8
      }
    }
  ]

  # 各レシピのスコアを計算
  results = []
  for recipe in recipes:
    score = BalanceService.calculate_nutrition_score(recipe['nutrition'])
    results.append({
      "name": recipe['name'],
      "score": score['overall_score'],
      "evaluation": score['evaluation']
    })

  # スコア順にソート
  results.sort(key=lambda x: x['score'], reverse=True)

  print(f"\n【レシピ比較（スコア順）】")
  for i, result in enumerate(results, 1):
    print(f"  {i}位: {result['name']:15s} - {result['score']:.1f}点 ({result['evaluation']})")


def example_6_ideal_vs_poor():
  """例6: 理想的な食事 vs バランスの悪い食事"""
  print("\n\n" + "=" * 60)
  print("例6: 理想的な食事 vs バランスの悪い食事")
  print("=" * 60)

  # 理想的な食事
  ideal_nutrition = {
    "calories": 670,
    "protein": 20,   # 15%
    "fat": 18,       # 24%
    "carbs": 100,    # 60%
    "fiber": 7,
    "salt": 2.5
  }

  # バランスの悪い食事（高脂質、低食物繊維、高塩分）
  poor_nutrition = {
    "calories": 900,
    "protein": 15,   # 低タンパク
    "fat": 50,       # 高脂質
    "carbs": 80,
    "fiber": 2,      # 低食物繊維
    "salt": 5.0      # 高塩分
  }

  # 評価
  ideal_score = BalanceService.calculate_nutrition_score(ideal_nutrition)
  poor_score = BalanceService.calculate_nutrition_score(poor_nutrition)

  print(f"\n【理想的な食事】")
  print(f"  総合スコア: {ideal_score['overall_score']:.1f}/100")
  print(f"  評価:       {ideal_score['evaluation']}")
  print(f"  健康的:     {'はい' if ideal_score['is_healthy'] else 'いいえ'}")

  print(f"\n【バランスの悪い食事】")
  print(f"  総合スコア: {poor_score['overall_score']:.1f}/100")
  print(f"  評価:       {poor_score['evaluation']}")
  print(f"  健康的:     {'はい' if poor_score['is_healthy'] else 'いいえ'}")

  print(f"\n【スコア差】")
  print(f"  差分: {ideal_score['overall_score'] - poor_score['overall_score']:.1f}点")


def example_7_api_usage():
  """例7: API使用例（疑似コード）"""
  print("\n\n" + "=" * 60)
  print("例7: API使用例（curl コマンド）")
  print("=" * 60)

  print("""
# 1. レシピのバランス評価取得
curl -X GET http://localhost:8000/api/v1/balance/1

# 2. 1日の食事バランス評価
curl -X POST http://localhost:8000/api/v1/balance/daily \\
  -H "Content-Type: application/json" \\
  -d '{
    "meals": [
      {"calories": 650, "protein": 20, "fat": 18, "carbs": 100, "fiber": 5, "salt": 2.5},
      {"calories": 700, "protein": 22, "fat": 20, "carbs": 105, "fiber": 6, "salt": 2.5}
    ],
    "target_date": "2025-12-11"
  }'

# 3. PFCバランス取得
curl -X GET http://localhost:8000/api/v1/balance/pfc/1

# 4. バランススコア計算
curl -X POST http://localhost:8000/api/v1/balance/score \\
  -H "Content-Type: application/json" \\
  -d '{
    "nutrition": {
      "calories": 650,
      "protein": 25,
      "fat": 20,
      "carbs": 85,
      "fiber": 5,
      "salt": 2.5
    }
  }'

# 5. 食事摂取基準取得
curl -X GET http://localhost:8000/api/v1/balance/reference

# 6. レシピ比較
curl -X POST http://localhost:8000/api/v1/balance/compare \\
  -H "Content-Type: application/json" \\
  -d '[
    {"calories": 650, "protein": 25, "fat": 20, "carbs": 85, "fiber": 5, "salt": 2.5},
    {"calories": 800, "protein": 30, "fat": 35, "carbs": 90, "fiber": 4, "salt": 3.5}
  ]'
  """)


def main():
  """すべての例を実行"""
  example_1_pfc_balance()
  example_2_daily_balance()
  example_3_nutrition_score()
  example_4_recipe_evaluation()
  example_5_compare_recipes()
  example_6_ideal_vs_poor()
  example_7_api_usage()

  print("\n\n" + "=" * 60)
  print("すべての例を実行しました")
  print("=" * 60)


if __name__ == "__main__":
  main()

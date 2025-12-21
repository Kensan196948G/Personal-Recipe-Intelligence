"""
栄養士AI相談機能の使用例

このスクリプトは、栄養士AI相談機能の基本的な使い方を示します。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.nutrition_advisor_service import NutritionAdvisorService


def print_separator(title=""):
  """セパレーターを表示"""
  print("\n" + "=" * 60)
  if title:
    print(f"  {title}")
    print("=" * 60)
  print()


def example_basic_chat():
  """基本的なチャット例"""
  print_separator("基本的なチャット")

  advisor = NutritionAdvisorService(data_dir="data/examples")
  user_id = "example-user-1"

  # 挨拶
  result = advisor.chat(user_id=user_id, message="こんにちは")
  print(f"ユーザー: こんにちは")
  print(f"AI: {result['message']['content']}")
  print()

  # タンパク質に関する質問
  result = advisor.chat(user_id=user_id, message="タンパク質について教えてください")
  print(f"ユーザー: タンパク質について教えてください")
  print(f"AI: {result['message']['content']}")
  if result["message"]["tips"]:
    print("\nポイント:")
    for tip in result["message"]["tips"]:
      print(f"  - {tip}")
  print()


def example_meal_analysis():
  """食事分析の例"""
  print_separator("食事分析")

  advisor = NutritionAdvisorService(data_dir="data/examples")
  user_id = "example-user-2"

  # 食事データ
  meal_data = {
    "meal_type": "lunch",
    "items": [
      {"recipe_id": "recipe-001", "servings": 1},
      {"recipe_id": "recipe-002", "servings": 1},
    ],
  }

  # 分析実行
  analysis = advisor.analyze_meal(user_id=user_id, meal_data=meal_data)

  print(f"食事タイプ: {analysis['meal_type']}")
  print(f"\n栄養情報:")
  print(f"  カロリー: {analysis['nutrition']['calories']} kcal")
  print(f"  タンパク質: {analysis['nutrition']['protein']} g")
  print(f"  炭水化物: {analysis['nutrition']['carbohydrates']} g")
  print(f"  脂質: {analysis['nutrition']['fat']} g")
  print(f"\nスコア: {analysis['score']}点")
  print(f"\nアドバイス:")
  for advice in analysis["advice"]:
    print(f"  - {advice}")
  print()


def example_meal_plan():
  """食事プラン提案の例"""
  print_separator("食事プラン提案")

  advisor = NutritionAdvisorService(data_dir="data/examples")
  user_id = "example-user-3"

  # 減量目標でプラン生成
  preferences = {"target_calories": 1800, "goals": ["weight_loss"]}

  plan = advisor.generate_meal_plan(user_id=user_id, preferences=preferences)

  print(f"目標カロリー: {plan['target_calories']} kcal")
  print(f"目標タンパク質: {plan['target_protein']:.1f} g")
  print(f"目標炭水化物: {plan['target_carbs']:.1f} g")
  print(f"目標脂質: {plan['target_fat']:.1f} g")

  print("\n【朝食】")
  print(f"目標カロリー: {plan['meals']['breakfast']['target_calories']:.0f} kcal")
  print("提案メニュー:")
  for i, suggestion in enumerate(plan["meals"]["breakfast"]["suggestions"], 1):
    print(f"  {i}. {suggestion}")

  print("\n【昼食】")
  print(f"目標カロリー: {plan['meals']['lunch']['target_calories']:.0f} kcal")
  print("提案メニュー:")
  for i, suggestion in enumerate(plan["meals"]["lunch"]["suggestions"], 1):
    print(f"  {i}. {suggestion}")

  print("\n【夕食】")
  print(f"目標カロリー: {plan['meals']['dinner']['target_calories']:.0f} kcal")
  print("提案メニュー:")
  for i, suggestion in enumerate(plan["meals"]["dinner"]["suggestions"], 1):
    print(f"  {i}. {suggestion}")

  print("\n【間食】")
  print(f"目標カロリー: {plan['meals']['snacks']['target_calories']:.0f} kcal")
  print("提案メニュー:")
  for i, suggestion in enumerate(plan["meals"]["snacks"]["suggestions"], 1):
    print(f"  {i}. {suggestion}")

  print("\n【水分補給】")
  print(f"目標: {plan['hydration']['target_water']} ml/日")
  for tip in plan["hydration"]["tips"]:
    print(f"  - {tip}")

  print("\n【全般的なアドバイス】")
  for advice in plan["general_advice"]:
    print(f"  - {advice}")
  print()


def example_daily_tip():
  """今日のワンポイントの例"""
  print_separator("今日のワンポイント")

  advisor = NutritionAdvisorService(data_dir="data/examples")

  tip = advisor.get_daily_tip()

  print(f"日付: {tip['date']}")
  print(f"タイトル: {tip['title']}")
  print(f"\n{tip['content']}")

  if tip["tips"]:
    print("\nポイント:")
    for point in tip["tips"]:
      print(f"  - {point}")
  print()


def example_user_profile():
  """ユーザープロファイル管理の例"""
  print_separator("ユーザープロファイル管理")

  advisor = NutritionAdvisorService(data_dir="data/examples")
  user_id = "example-user-4"

  # プロファイル更新
  print("プロファイルを設定...")
  profile_updates = {
    "preferences": {"favorite_foods": ["fish", "vegetables"], "dislike_foods": ["liver"]},
    "goals": ["weight_loss", "muscle_gain"],
    "restrictions": ["allergy"],
  }

  profile = advisor.update_user_profile(
    user_id=user_id, profile_updates=profile_updates
  )

  print(f"目標: {', '.join(profile['goals'])}")
  print(f"制限事項: {', '.join(profile['restrictions'])}")
  print(f"好きな食材: {', '.join(profile['preferences']['favorite_foods'])}")
  print()

  # パーソナライズされたチャット
  print("パーソナライズされた応答を取得...")
  result = advisor.chat(user_id=user_id, message="炭水化物について教えてください")
  print(f"\nユーザー: 炭水化物について教えてください")
  print(f"AI: {result['message']['content']}")
  print()


def example_chat_history():
  """チャット履歴管理の例"""
  print_separator("チャット履歴管理")

  advisor = NutritionAdvisorService(data_dir="data/examples")
  user_id = "example-user-5"

  # 複数のメッセージを送信
  messages = [
    "こんにちは",
    "タンパク質について教えてください",
    "ダイエットのコツは？",
  ]

  print("複数のメッセージを送信...")
  for msg in messages:
    advisor.chat(user_id=user_id, message=msg)
    print(f"  - {msg}")
  print()

  # 履歴取得
  print("チャット履歴を取得...")
  history = advisor.get_chat_history(user_id=user_id, limit=10)

  print(f"総メッセージ数: {history['total']}")
  print(f"\n最近の会話:")
  for msg in history["history"][:4]:  # 最新4件のみ表示
    role = "ユーザー" if msg["role"] == "user" else "AI"
    content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
    print(f"  {role}: {content}")
  print()


def example_quick_actions():
  """クイックアクションの例"""
  print_separator("クイックアクション")

  advisor = NutritionAdvisorService(data_dir="data/examples")

  print("利用可能なクイックアクション:")
  for action in advisor.quick_actions:
    print(f"  [{action['id']}] {action['label']}")
    print(f"      → {action['message']}")
  print()


def example_context_aware_chat():
  """コンテキスト考慮チャットの例"""
  print_separator("コンテキスト考慮チャット")

  advisor = NutritionAdvisorService(data_dir="data/examples")
  user_id = "example-user-6"

  # コンテキスト情報付きでチャット
  context = {
    "current_meal": "breakfast",
    "time_of_day": "morning",
    "recent_activity": "exercise",
  }

  result = advisor.chat(
    user_id=user_id,
    message="運動後に何を食べればいいですか？",
    context=context,
  )

  print(f"コンテキスト: {context}")
  print(f"\nユーザー: 運動後に何を食べればいいですか？")
  print(f"AI: {result['message']['content']}")
  if result["message"]["tips"]:
    print("\nポイント:")
    for tip in result["message"]["tips"]:
      print(f"  - {tip}")
  print()


def main():
  """メイン関数"""
  print("\n")
  print("╔" + "═" * 58 + "╗")
  print("║" + " " * 10 + "栄養士AI相談機能 使用例" + " " * 23 + "║")
  print("╚" + "═" * 58 + "╝")

  try:
    # 各例を実行
    example_basic_chat()
    example_meal_analysis()
    example_meal_plan()
    example_daily_tip()
    example_user_profile()
    example_chat_history()
    example_quick_actions()
    example_context_aware_chat()

    print_separator()
    print("すべての例が正常に実行されました！")
    print()

  except Exception as e:
    print(f"\nエラーが発生しました: {e}")
    import traceback

    traceback.print_exc()


if __name__ == "__main__":
  main()

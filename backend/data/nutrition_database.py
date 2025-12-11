"""
栄養データベース

日本食品標準成分表2020年版（八訂）をベースにした栄養素データ
単位: 100gあたり（特記がない限り）
"""

from typing import Dict, Any

NUTRITION_DATA: Dict[str, Dict[str, Any]] = {
  # 穀類
  "白米": {
    "calories": 168,
    "protein": 2.5,
    "fat": 0.3,
    "carbs": 37.1,
    "fiber": 0.3,
    "unit": "100g"
  },
  "玄米": {
    "calories": 165,
    "protein": 2.8,
    "fat": 1.0,
    "carbs": 35.6,
    "fiber": 1.4,
    "unit": "100g"
  },
  "食パン": {
    "calories": 264,
    "protein": 9.3,
    "fat": 4.4,
    "carbs": 46.7,
    "fiber": 2.3,
    "unit": "100g"
  },
  "うどん": {
    "calories": 105,
    "protein": 2.6,
    "fat": 0.4,
    "carbs": 21.6,
    "fiber": 0.8,
    "unit": "100g"
  },
  "そば": {
    "calories": 132,
    "protein": 4.8,
    "fat": 1.0,
    "carbs": 26.0,
    "fiber": 2.0,
    "unit": "100g"
  },
  "パスタ": {
    "calories": 149,
    "protein": 5.8,
    "fat": 0.9,
    "carbs": 30.3,
    "fiber": 1.5,
    "unit": "100g"
  },

  # 肉類
  "鶏もも肉": {
    "calories": 200,
    "protein": 16.2,
    "fat": 14.0,
    "carbs": 0,
    "fiber": 0,
    "unit": "100g"
  },
  "鶏むね肉": {
    "calories": 108,
    "protein": 22.3,
    "fat": 1.5,
    "carbs": 0,
    "fiber": 0,
    "unit": "100g"
  },
  "豚バラ肉": {
    "calories": 386,
    "protein": 14.2,
    "fat": 34.6,
    "carbs": 0.1,
    "fiber": 0,
    "unit": "100g"
  },
  "豚ロース肉": {
    "calories": 263,
    "protein": 19.3,
    "fat": 19.2,
    "carbs": 0.2,
    "fiber": 0,
    "unit": "100g"
  },
  "牛もも肉": {
    "calories": 182,
    "protein": 21.2,
    "fat": 9.6,
    "carbs": 0.5,
    "fiber": 0,
    "unit": "100g"
  },
  "牛バラ肉": {
    "calories": 371,
    "protein": 14.4,
    "fat": 32.9,
    "carbs": 0.3,
    "fiber": 0,
    "unit": "100g"
  },
  "ひき肉": {
    "calories": 209,
    "protein": 19.0,
    "fat": 15.1,
    "carbs": 0.3,
    "fiber": 0,
    "unit": "100g"
  },

  # 魚介類
  "サーモン": {
    "calories": 138,
    "protein": 22.3,
    "fat": 4.5,
    "carbs": 0.1,
    "fiber": 0,
    "unit": "100g"
  },
  "まぐろ": {
    "calories": 125,
    "protein": 26.4,
    "fat": 1.4,
    "carbs": 0.1,
    "fiber": 0,
    "unit": "100g"
  },
  "さば": {
    "calories": 202,
    "protein": 20.7,
    "fat": 12.1,
    "carbs": 0.3,
    "fiber": 0,
    "unit": "100g"
  },
  "いわし": {
    "calories": 169,
    "protein": 19.8,
    "fat": 9.2,
    "carbs": 0.2,
    "fiber": 0,
    "unit": "100g"
  },
  "えび": {
    "calories": 82,
    "protein": 18.4,
    "fat": 0.3,
    "carbs": 0.1,
    "fiber": 0,
    "unit": "100g"
  },
  "いか": {
    "calories": 76,
    "protein": 17.9,
    "fat": 0.8,
    "carbs": 0.1,
    "fiber": 0,
    "unit": "100g"
  },

  # 野菜類
  "玉ねぎ": {
    "calories": 37,
    "protein": 1.0,
    "fat": 0.1,
    "carbs": 8.8,
    "fiber": 1.6,
    "unit": "100g"
  },
  "たまねぎ": {
    "calories": 37,
    "protein": 1.0,
    "fat": 0.1,
    "carbs": 8.8,
    "fiber": 1.6,
    "unit": "100g"
  },
  "にんじん": {
    "calories": 39,
    "protein": 0.6,
    "fat": 0.2,
    "carbs": 9.3,
    "fiber": 2.8,
    "unit": "100g"
  },
  "じゃがいも": {
    "calories": 76,
    "protein": 1.6,
    "fat": 0.1,
    "carbs": 17.6,
    "fiber": 1.3,
    "unit": "100g"
  },
  "トマト": {
    "calories": 19,
    "protein": 0.7,
    "fat": 0.1,
    "carbs": 4.7,
    "fiber": 1.0,
    "unit": "100g"
  },
  "きゅうり": {
    "calories": 14,
    "protein": 1.0,
    "fat": 0.1,
    "carbs": 3.0,
    "fiber": 1.1,
    "unit": "100g"
  },
  "レタス": {
    "calories": 12,
    "protein": 0.6,
    "fat": 0.1,
    "carbs": 2.8,
    "fiber": 1.1,
    "unit": "100g"
  },
  "キャベツ": {
    "calories": 23,
    "protein": 1.3,
    "fat": 0.2,
    "carbs": 5.2,
    "fiber": 1.8,
    "unit": "100g"
  },
  "ブロッコリー": {
    "calories": 33,
    "protein": 4.3,
    "fat": 0.5,
    "carbs": 5.2,
    "fiber": 4.4,
    "unit": "100g"
  },
  "ほうれん草": {
    "calories": 20,
    "protein": 2.2,
    "fat": 0.4,
    "carbs": 3.1,
    "fiber": 2.8,
    "unit": "100g"
  },
  "なす": {
    "calories": 22,
    "protein": 1.1,
    "fat": 0.1,
    "carbs": 5.1,
    "fiber": 2.2,
    "unit": "100g"
  },
  "ピーマン": {
    "calories": 22,
    "protein": 0.9,
    "fat": 0.2,
    "carbs": 5.1,
    "fiber": 2.3,
    "unit": "100g"
  },

  # きのこ類
  "しめじ": {
    "calories": 18,
    "protein": 2.7,
    "fat": 0.4,
    "carbs": 3.7,
    "fiber": 3.0,
    "unit": "100g"
  },
  "えのき": {
    "calories": 22,
    "protein": 2.7,
    "fat": 0.2,
    "carbs": 7.6,
    "fiber": 3.9,
    "unit": "100g"
  },
  "しいたけ": {
    "calories": 19,
    "protein": 3.0,
    "fat": 0.3,
    "carbs": 4.9,
    "fiber": 4.2,
    "unit": "100g"
  },

  # 卵・乳製品
  "卵": {
    "calories": 151,
    "protein": 12.3,
    "fat": 10.3,
    "carbs": 0.3,
    "fiber": 0,
    "unit": "100g"
  },
  "牛乳": {
    "calories": 67,
    "protein": 3.3,
    "fat": 3.8,
    "carbs": 4.8,
    "fiber": 0,
    "unit": "100ml"
  },
  "ヨーグルト": {
    "calories": 62,
    "protein": 3.6,
    "fat": 3.0,
    "carbs": 4.9,
    "fiber": 0,
    "unit": "100g"
  },
  "チーズ": {
    "calories": 339,
    "protein": 22.7,
    "fat": 26.0,
    "carbs": 1.3,
    "fiber": 0,
    "unit": "100g"
  },
  "バター": {
    "calories": 745,
    "protein": 0.6,
    "fat": 81.0,
    "carbs": 0.2,
    "fiber": 0,
    "unit": "100g"
  },

  # 豆類
  "豆腐": {
    "calories": 72,
    "protein": 6.6,
    "fat": 4.2,
    "carbs": 1.6,
    "fiber": 0.4,
    "unit": "100g"
  },
  "納豆": {
    "calories": 200,
    "protein": 16.5,
    "fat": 10.0,
    "carbs": 12.1,
    "fiber": 6.7,
    "unit": "100g"
  },
  "油揚げ": {
    "calories": 386,
    "protein": 18.6,
    "fat": 33.1,
    "carbs": 1.4,
    "fiber": 1.1,
    "unit": "100g"
  },

  # 調味料
  "醤油": {
    "calories": 71,
    "protein": 7.7,
    "fat": 0,
    "carbs": 10.1,
    "fiber": 0,
    "unit": "100ml"
  },
  "味噌": {
    "calories": 192,
    "protein": 12.5,
    "fat": 6.0,
    "carbs": 21.9,
    "fiber": 4.3,
    "unit": "100g"
  },
  "砂糖": {
    "calories": 384,
    "protein": 0,
    "fat": 0,
    "carbs": 99.2,
    "fiber": 0,
    "unit": "100g"
  },
  "塩": {
    "calories": 0,
    "protein": 0,
    "fat": 0,
    "carbs": 0,
    "fiber": 0,
    "unit": "100g"
  },
  "サラダ油": {
    "calories": 921,
    "protein": 0,
    "fat": 100.0,
    "carbs": 0,
    "fiber": 0,
    "unit": "100ml"
  },
  "ごま油": {
    "calories": 921,
    "protein": 0,
    "fat": 100.0,
    "carbs": 0,
    "fiber": 0,
    "unit": "100ml"
  },
  "オリーブオイル": {
    "calories": 921,
    "protein": 0,
    "fat": 100.0,
    "carbs": 0,
    "fiber": 0,
    "unit": "100ml"
  },
  "みりん": {
    "calories": 241,
    "protein": 0.3,
    "fat": 0,
    "carbs": 43.2,
    "fiber": 0,
    "unit": "100ml"
  },
  "酒": {
    "calories": 107,
    "protein": 0.4,
    "fat": 0,
    "carbs": 4.9,
    "fiber": 0,
    "unit": "100ml"
  },
}


def get_ingredient_nutrition(ingredient_name: str) -> Dict[str, Any] | None:
  """
  材料名から栄養情報を取得

  Args:
    ingredient_name: 材料名

  Returns:
    栄養情報の辞書、見つからない場合はNone
  """
  # 正規化（空白除去、小文字化）
  normalized_name = ingredient_name.strip()

  # 完全一致
  if normalized_name in NUTRITION_DATA:
    return NUTRITION_DATA[normalized_name]

  # 部分一致（材料名に含まれる場合）
  for key, value in NUTRITION_DATA.items():
    if key in normalized_name or normalized_name in key:
      return value

  return None


def list_all_ingredients() -> list[str]:
  """
  登録されている全材料名を取得

  Returns:
    材料名のリスト
  """
  return list(NUTRITION_DATA.keys())

"""
レシピ自動生成サービス

テンプレートベースでレシピを生成し、将来的なLLM統合の基盤を提供する。
"""

import random
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path


class RecipeGeneratorService:
  """レシピ自動生成サービス"""

  def __init__(self, data_dir: str = "data/generator"):
    """
    初期化

    Args:
      data_dir: データディレクトリパス
    """
    self.data_dir = Path(data_dir)
    self.data_dir.mkdir(parents=True, exist_ok=True)

    # テンプレートとデータの読み込み
    self._load_templates()
    self._load_ingredient_data()
    self._load_cooking_methods()

  def _load_templates(self) -> None:
    """レシピテンプレートの読み込み"""
    self.templates = {
      "japanese": {
        "stir_fry": {
          "name": "{main}の炒め物",
          "steps": [
            "{main}を一口大に切る",
            "{sub}を薄切りにする",
            "フライパンに油を熱し、{main}を炒める",
            "{sub}を加えてさらに炒める",
            "醤油、みりん、砂糖で味付けする",
            "器に盛り付けて完成"
          ],
          "base_ingredients": ["醤油", "みりん", "砂糖", "サラダ油"],
          "cooking_time": 15,
          "difficulty": "easy"
        },
        "simmered": {
          "name": "{main}の煮物",
          "steps": [
            "{main}を食べやすい大きさに切る",
            "{sub}も同様に切る",
            "鍋に出汁を入れて火にかける",
            "{main}と{sub}を加える",
            "醤油、みりん、砂糖で味付けし、落し蓋をして煮る",
            "具材が柔らかくなったら完成"
          ],
          "base_ingredients": ["出汁", "醤油", "みりん", "砂糖"],
          "cooking_time": 30,
          "difficulty": "medium"
        },
        "soup": {
          "name": "{main}の味噌汁",
          "steps": [
            "{main}を適当な大きさに切る",
            "{sub}も食べやすく切る",
            "鍋に出汁を入れて火にかける",
            "{main}と{sub}を加えて煮る",
            "味噌を溶き入れる",
            "器に盛り付けて完成"
          ],
          "base_ingredients": ["出汁", "味噌"],
          "cooking_time": 10,
          "difficulty": "easy"
        },
        "grilled": {
          "name": "{main}の照り焼き",
          "steps": [
            "{main}を食べやすい大きさに切る",
            "醤油、みりん、砂糖、酒でタレを作る",
            "フライパンに油を熱し、{main}を焼く",
            "両面に焼き色がついたらタレを加える",
            "タレを絡めながら照りが出るまで焼く",
            "器に盛り付けて完成"
          ],
          "base_ingredients": ["醤油", "みりん", "砂糖", "酒", "サラダ油"],
          "cooking_time": 20,
          "difficulty": "medium"
        }
      },
      "western": {
        "saute": {
          "name": "{main}のソテー",
          "steps": [
            "{main}に塩コショウで下味をつける",
            "{sub}を食べやすく切る",
            "フライパンにバターを熱し、{main}を焼く",
            "両面に焼き色がついたら{sub}を加える",
            "白ワインを加えて蒸し焼きにする",
            "器に盛り付けて完成"
          ],
          "base_ingredients": ["塩", "コショウ", "バター", "白ワイン"],
          "cooking_time": 20,
          "difficulty": "medium"
        },
        "pasta": {
          "name": "{main}のパスタ",
          "steps": [
            "パスタを茹で始める",
            "{main}を一口大に切る",
            "{sub}を薄切りにする",
            "フライパンにオリーブオイルを熱し、ニンニクを炒める",
            "{main}と{sub}を加えて炒める",
            "茹で上がったパスタを加えて混ぜ合わせる",
            "塩コショウで味を整えて完成"
          ],
          "base_ingredients": ["パスタ", "オリーブオイル", "ニンニク", "塩", "コショウ"],
          "cooking_time": 25,
          "difficulty": "medium"
        },
        "salad": {
          "name": "{main}のサラダ",
          "steps": [
            "{main}を食べやすい大きさに切る",
            "{sub}も同様に切る",
            "野菜を洗って水気を切る",
            "ボウルに野菜と{main}、{sub}を入れる",
            "ドレッシングで和える",
            "器に盛り付けて完成"
          ],
          "base_ingredients": ["レタス", "トマト", "オリーブオイル", "酢", "塩", "コショウ"],
          "cooking_time": 10,
          "difficulty": "easy"
        },
        "stew": {
          "name": "{main}のシチュー",
          "steps": [
            "{main}を一口大に切る",
            "{sub}も食べやすく切る",
            "鍋にバターを熱し、{main}を炒める",
            "{sub}を加えて炒める",
            "水を加えて煮込む",
            "ルーを加えてとろみがつくまで煮る",
            "器に盛り付けて完成"
          ],
          "base_ingredients": ["バター", "小麦粉", "牛乳", "コンソメ"],
          "cooking_time": 40,
          "difficulty": "medium"
        }
      },
      "chinese": {
        "stir_fry": {
          "name": "{main}の中華炒め",
          "steps": [
            "{main}を一口大に切る",
            "{sub}を薄切りにする",
            "中華鍋に油を熱し、ニンニクと生姜を炒める",
            "{main}を加えて強火で炒める",
            "{sub}を加えてさらに炒める",
            "醤油、オイスターソース、酒で味付けする",
            "水溶き片栗粉でとろみをつけて完成"
          ],
          "base_ingredients": ["ごま油", "ニンニク", "生姜", "醤油", "オイスターソース", "酒", "片栗粉"],
          "cooking_time": 15,
          "difficulty": "medium"
        },
        "sweet_sour": {
          "name": "{main}の酢豚風",
          "steps": [
            "{main}を一口大に切って片栗粉をまぶす",
            "{sub}を食べやすく切る",
            "{main}を油で揚げる",
            "別のフライパンで{sub}を炒める",
            "酢、砂糖、ケチャップ、醤油で甘酢を作る",
            "{main}と{sub}を加えて絡める",
            "器に盛り付けて完成"
          ],
          "base_ingredients": ["片栗粉", "酢", "砂糖", "ケチャップ", "醤油", "サラダ油"],
          "cooking_time": 25,
          "difficulty": "hard"
        },
        "soup": {
          "name": "{main}の中華スープ",
          "steps": [
            "{main}を薄切りにする",
            "{sub}も食べやすく切る",
            "鍋に水と鶏ガラスープの素を入れて火にかける",
            "{main}と{sub}を加えて煮る",
            "醤油、塩、コショウで味を整える",
            "溶き卵を回し入れる",
            "ごま油を垂らして完成"
          ],
          "base_ingredients": ["鶏ガラスープの素", "醤油", "塩", "コショウ", "卵", "ごま油"],
          "cooking_time": 15,
          "difficulty": "easy"
        }
      }
    }

  def _load_ingredient_data(self) -> None:
    """食材データの読み込み"""
    self.ingredient_categories = {
      "meat": ["鶏肉", "豚肉", "牛肉", "ひき肉"],
      "seafood": ["鮭", "エビ", "イカ", "タラ", "サバ"],
      "vegetable": ["玉ねぎ", "にんじん", "キャベツ", "ピーマン", "なす", "トマト", "ほうれん草", "ブロッコリー"],
      "mushroom": ["しめじ", "えのき", "しいたけ", "エリンギ"],
      "tofu": ["豆腐", "厚揚げ", "油揚げ"]
    }

    # 食材の相性マトリックス
    self.ingredient_compatibility = {
      "鶏肉": ["玉ねぎ", "にんじん", "ピーマン", "しめじ", "トマト"],
      "豚肉": ["キャベツ", "玉ねぎ", "にんじん", "ピーマン", "なす"],
      "牛肉": ["玉ねぎ", "にんじん", "ピーマン", "ブロッコリー"],
      "鮭": ["玉ねぎ", "しめじ", "ほうれん草", "トマト"],
      "エビ": ["ブロッコリー", "アスパラガス", "トマト", "ピーマン"],
      "豆腐": ["ほうれん草", "しめじ", "玉ねぎ", "にんじん"]
    }

    # 季節の食材
    self.seasonal_ingredients = {
      "spring": ["アスパラガス", "春キャベツ", "新玉ねぎ", "筍"],
      "summer": ["トマト", "なす", "ピーマン", "ズッキーニ", "オクラ"],
      "autumn": ["さつまいも", "かぼちゃ", "しめじ", "まいたけ", "栗"],
      "winter": ["白菜", "大根", "ほうれん草", "ブロッコリー", "ねぎ"]
    }

  def _load_cooking_methods(self) -> None:
    """調理方法データの読み込み"""
    self.cooking_methods = {
      "japanese": ["stir_fry", "simmered", "soup", "grilled"],
      "western": ["saute", "pasta", "salad", "stew"],
      "chinese": ["stir_fry", "sweet_sour", "soup"]
    }

  def _get_current_season(self) -> str:
    """現在の季節を取得"""
    month = datetime.now().month
    if 3 <= month <= 5:
      return "spring"
    elif 6 <= month <= 8:
      return "summer"
    elif 9 <= month <= 11:
      return "autumn"
    else:
      return "winter"

  def generate_recipe(
    self,
    ingredients: List[str],
    category: str = "japanese",
    cooking_time: Optional[int] = None,
    difficulty: Optional[str] = None,
    use_seasonal: bool = True
  ) -> Dict[str, Any]:
    """
    レシピを生成

    Args:
      ingredients: 使用する食材リスト
      category: 料理カテゴリ (japanese/western/chinese)
      cooking_time: 調理時間（分）
      difficulty: 難易度 (easy/medium/hard)
      use_seasonal: 季節の食材を活用するか

    Returns:
      生成されたレシピ
    """
    if not ingredients:
      raise ValueError("食材を最低1つ指定してください")

    if category not in self.templates:
      raise ValueError(f"無効なカテゴリ: {category}")

    # メイン食材とサブ食材を決定
    main_ingredient = ingredients[0]
    sub_ingredients = ingredients[1:] if len(ingredients) > 1 else []

    # 相性の良い食材を追加提案
    if main_ingredient in self.ingredient_compatibility and not sub_ingredients:
      compatible = self.ingredient_compatibility[main_ingredient]
      sub_ingredients = [random.choice(compatible)]

    # 季節の食材を追加
    if use_seasonal:
      season = self._get_current_season()
      seasonal_items = self.seasonal_ingredients.get(season, [])
      for item in seasonal_items[:2]:
        if item not in ingredients and item not in sub_ingredients:
          sub_ingredients.append(item)
          break

    # テンプレートを選択
    available_methods = self.cooking_methods[category]
    if difficulty:
      available_methods = [
        m for m in available_methods
        if self.templates[category][m]["difficulty"] == difficulty
      ]

    if cooking_time:
      available_methods = [
        m for m in available_methods
        if self.templates[category][m]["cooking_time"] <= cooking_time
      ]

    if not available_methods:
      available_methods = self.cooking_methods[category]

    method = random.choice(available_methods)
    template = self.templates[category][method]

    # レシピを生成
    recipe_name = template["name"].format(main=main_ingredient)
    steps = []
    for step in template["steps"]:
      formatted_step = step.replace("{main}", main_ingredient)
      if sub_ingredients:
        formatted_step = formatted_step.replace("{sub}", sub_ingredients[0])
      steps.append(formatted_step)

    # 材料リストを作成
    all_ingredients = [main_ingredient] + sub_ingredients + template["base_ingredients"]

    recipe = {
      "id": f"generated_{datetime.now().strftime('%Y%m%d%H%M%S')}",
      "name": recipe_name,
      "category": category,
      "cooking_time": template["cooking_time"],
      "difficulty": template["difficulty"],
      "ingredients": [
        {"name": ing, "amount": "適量", "unit": ""} for ing in all_ingredients
      ],
      "steps": steps,
      "servings": 2,
      "tags": [category, template["difficulty"], main_ingredient],
      "generated_at": datetime.now().isoformat(),
      "method": method
    }

    return recipe

  def generate_variations(
    self,
    base_recipe: Dict[str, Any],
    count: int = 3
  ) -> List[Dict[str, Any]]:
    """
    既存レシピのバリエーションを生成

    Args:
      base_recipe: 元となるレシピ
      count: 生成する数

    Returns:
      バリエーションレシピのリスト
    """
    variations = []
    category = base_recipe.get("category", "japanese")
    main_ingredient = base_recipe["ingredients"][0]["name"] if base_recipe.get("ingredients") else "食材"

    # 異なる調理方法でバリエーションを生成
    available_methods = self.cooking_methods.get(category, [])

    for i in range(min(count, len(available_methods))):
      method = available_methods[i]
      template = self.templates[category][method]

      # 食材リストを取得
      ingredients = [ing["name"] for ing in base_recipe.get("ingredients", [])][:3]

      variation = {
        "id": f"variation_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
        "name": template["name"].format(main=main_ingredient),
        "category": category,
        "cooking_time": template["cooking_time"],
        "difficulty": template["difficulty"],
        "ingredients": base_recipe.get("ingredients", []),
        "steps": [
          step.replace("{main}", main_ingredient).replace(
            "{sub}", ingredients[1] if len(ingredients) > 1 else "野菜"
          )
          for step in template["steps"]
        ],
        "servings": base_recipe.get("servings", 2),
        "tags": [category, template["difficulty"], "バリエーション"],
        "generated_at": datetime.now().isoformat(),
        "based_on": base_recipe.get("id"),
        "method": method
      }

      variations.append(variation)

    return variations

  def suggest_ingredient_combinations(
    self,
    main_ingredient: str,
    count: int = 5
  ) -> List[Dict[str, Any]]:
    """
    食材の組み合わせを提案

    Args:
      main_ingredient: メイン食材
      count: 提案数

    Returns:
      組み合わせ提案のリスト
    """
    suggestions = []

    # 相性の良い食材を取得
    compatible = self.ingredient_compatibility.get(main_ingredient, [])

    if not compatible:
      # カテゴリから適当に選択
      all_ingredients = []
      for items in self.ingredient_categories.values():
        all_ingredients.extend(items)
      compatible = random.sample(all_ingredients, min(5, len(all_ingredients)))

    # 季節の食材を追加
    season = self._get_current_season()
    seasonal = self.seasonal_ingredients.get(season, [])

    for i in range(min(count, len(compatible))):
      sub_ingredient = compatible[i]
      suggestion = {
        "main": main_ingredient,
        "sub": sub_ingredient,
        "compatibility_score": random.randint(70, 95),
        "seasonal": sub_ingredient in seasonal,
        "recommended_categories": ["japanese", "western", "chinese"]
      }
      suggestions.append(suggestion)

    return suggestions

  def improve_recipe(
    self,
    recipe: Dict[str, Any],
    focus: str = "taste"
  ) -> Dict[str, Any]:
    """
    既存レシピを改善

    Args:
      recipe: 改善対象のレシピ
      focus: 改善の焦点 (taste/health/speed/cost)

    Returns:
      改善されたレシピ
    """
    improved = recipe.copy()

    if focus == "taste":
      # 味を改善するための調味料追加
      additional_seasonings = {
        "japanese": ["みりん", "出汁", "生姜"],
        "western": ["ハーブ", "ワイン", "バター"],
        "chinese": ["オイスターソース", "ごま油", "豆板醤"]
      }
      category = recipe.get("category", "japanese")
      seasonings = additional_seasonings.get(category, [])

      for seasoning in seasonings[:2]:
        if not any(ing["name"] == seasoning for ing in improved.get("ingredients", [])):
          improved.setdefault("ingredients", []).append({
            "name": seasoning,
            "amount": "少々",
            "unit": ""
          })

      improved["tags"] = improved.get("tags", []) + ["味改善版"]

    elif focus == "health":
      # 健康的な調理方法に変更
      improved["tags"] = improved.get("tags", []) + ["ヘルシー版"]
      # 油の使用量を減らす提案
      steps = improved.get("steps", [])
      improved["steps"] = [
        step.replace("油で揚げる", "オーブンで焼く").replace("多めの油", "少量の油")
        for step in steps
      ]

    elif focus == "speed":
      # 調理時間を短縮
      improved["cooking_time"] = max(10, improved.get("cooking_time", 30) - 10)
      improved["tags"] = improved.get("tags", []) + ["時短版"]

    elif focus == "cost":
      # コストを抑える提案
      improved["tags"] = improved.get("tags", []) + ["節約版"]

    improved["improved_at"] = datetime.now().isoformat()
    improved["improvement_focus"] = focus

    return improved

  def get_nutrition_estimate(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
    """
    栄養バランスの概算を取得

    Args:
      recipe: レシピ

    Returns:
      栄養情報の概算
    """
    # 簡易的な栄養バランス推定
    ingredients = recipe.get("ingredients", [])

    has_protein = any(
      ing["name"] in ["鶏肉", "豚肉", "牛肉", "鮭", "エビ", "豆腐"]
      for ing in ingredients
    )
    has_vegetable = any(
      ing["name"] in ["玉ねぎ", "にんじん", "キャベツ", "ピーマン", "ほうれん草"]
      for ing in ingredients
    )
    has_carb = any(
      ing["name"] in ["ご飯", "パスタ", "パン", "じゃがいも"]
      for ing in ingredients
    )

    balance_score = sum([has_protein, has_vegetable, has_carb]) / 3 * 100

    return {
      "has_protein": has_protein,
      "has_vegetable": has_vegetable,
      "has_carbohydrate": has_carb,
      "balance_score": round(balance_score, 1),
      "recommendation": "バランスが良い" if balance_score > 66 else "野菜を追加するとより良い"
    }

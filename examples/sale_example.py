"""
特売情報連携機能のサンプルコード

実際の使用例を示します。
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.sale_service import (
  SaleService,
  SaleItem,
  SaleCategory,
)
from backend.services.flyer_parser import FlyerParser


def example_1_basic_usage():
  """例1: 基本的な使い方"""
  print("=== 例1: 基本的な使い方 ===\n")

  service = SaleService()

  # 特売商品を追加
  now = datetime.now()
  sale_items = [
    SaleItem(
      id="item-001",
      store_name="イオン",
      product_name="たまねぎ",
      price=98.0,
      original_price=150.0,
      unit="個",
      category=SaleCategory.VEGETABLE,
      valid_from=now,
      valid_until=now + timedelta(days=3),
    ),
    SaleItem(
      id="item-002",
      store_name="西友",
      product_name="たまねぎ",
      price=120.0,
      original_price=150.0,
      unit="個",
      category=SaleCategory.VEGETABLE,
      valid_from=now,
      valid_until=now + timedelta(days=2),
    ),
    SaleItem(
      id="item-003",
      store_name="イオン",
      product_name="豚バラ肉",
      price=198.0,
      original_price=298.0,
      unit="100g",
      category=SaleCategory.MEAT,
      valid_from=now,
      valid_until=now + timedelta(days=1),
    ),
  ]

  for item in sale_items:
    service.add_sale_item(item)
    print(
      f"追加: {item.store_name} - {item.product_name} ¥{item.price} "
      f"({item.discount_rate}% OFF)"
    )

  print(f"\n合計 {len(service.sale_items)} 件の特売情報を追加しました\n")


def example_2_price_comparison():
  """例2: 価格比較"""
  print("=== 例2: 価格比較 ===\n")

  service = SaleService()
  now = datetime.now()

  # 複数店舗の同じ商品を追加
  stores_data = [
    ("イオン", 98.0, 150.0),
    ("西友", 120.0, 150.0),
    ("ライフ", 108.0, 150.0),
  ]

  for store, price, original in stores_data:
    service.add_sale_item(
      SaleItem(
        id=f"onion-{store}",
        store_name=store,
        product_name="たまねぎ",
        price=price,
        original_price=original,
        unit="個",
        category=SaleCategory.VEGETABLE,
        valid_from=now,
        valid_until=now + timedelta(days=3),
      )
    )

  # 価格比較
  comparison = service.compare_prices("たまねぎ")

  print("【たまねぎの価格比較】")
  for i, item in enumerate(comparison, 1):
    print(
      f"{i}. {item['store_name']}: ¥{item['price']} "
      f"({item['discount_rate']}% OFF)"
    )

  print(f"\n最安値: {comparison[0]['store_name']} ¥{comparison[0]['price']}\n")


def example_3_recipe_cost_estimate():
  """例3: レシピ材料費見積もり"""
  print("=== 例3: レシピ材料費見積もり ===\n")

  service = SaleService()
  now = datetime.now()

  # 特売情報を追加
  sale_data = [
    ("たまねぎ", 98.0, SaleCategory.VEGETABLE),
    ("にんじん", 158.0, SaleCategory.VEGETABLE),
    ("豚肉", 198.0, SaleCategory.MEAT),
  ]

  for name, price, category in sale_data:
    service.add_sale_item(
      SaleItem(
        id=f"item-{name}",
        store_name="イオン",
        product_name=name,
        price=price,
        unit="個",
        category=category,
        valid_from=now,
        valid_until=now + timedelta(days=3),
      )
    )

  # 肉じゃがの材料費見積もり
  ingredients = ["たまねぎ", "にんじん", "豚肉", "じゃがいも"]

  print("【肉じゃがの材料費見積もり】")
  estimate = service.get_recipe_cost_estimate(ingredients)

  print(f"材料数: {estimate['ingredients_count']}種類")
  print(f"特売利用: {estimate['available_on_sale']}種類")
  print(f"カバー率: {estimate['coverage_rate']}%")
  print(f"合計金額: ¥{estimate['total_cost']}")

  print("\n【詳細】")
  for item in estimate["items"]:
    if item["on_sale"]:
      print(
        f"✓ {item['ingredient']}: ¥{item['price']} ({item['store']})"
      )
    else:
      print(f"✗ {item['ingredient']}: 特売なし")

  print()


def example_4_flyer_parsing():
  """例4: チラシパース"""
  print("=== 例4: チラシパース ===\n")

  parser = FlyerParser()
  service = SaleService()

  # サンプルOCRテキスト（実際のチラシを模擬）
  ocr_text = """
  イオン 今週の大特価

  【野菜コーナー】
  国産たまねぎ 98円
  新鮮にんじん 3本 158円
  キャベツ 1玉 128円

  【お肉コーナー】
  豚バラ肉 100g 198円
  国産鶏もも肉 100g 88円

  【乳製品コーナー】
  牛乳 1L 168円
  """

  print("【OCRテキスト】")
  print(ocr_text)
  print("\n【パース結果】")

  # 店舗名抽出
  store_name = parser.extract_store_name(ocr_text)
  print(f"店舗名: {store_name}")

  # 商品情報抽出
  products = parser.parse_ocr_result(ocr_text, store_name)
  print(f"\n抽出された商品数: {len(products)}件")

  # 検証
  validated = parser.validate_parsed_products(products, min_confidence=0.5)
  print(f"検証後: {len(validated)}件\n")

  # SaleItem生成
  sale_items = parser.create_sale_items(validated, store_name, valid_days=3)

  print("【特売商品リスト】")
  for item in sale_items:
    print(
      f"- {item.product_name}: ¥{item.price} / {item.unit} "
      f"[{item.category.value}]"
    )
    service.add_sale_item(item)

  print(f"\n合計 {len(sale_items)} 件を登録しました\n")


def example_5_recommendations():
  """例5: レシピ推薦"""
  print("=== 例5: 特売食材を使ったレシピ推薦 ===\n")

  service = SaleService()
  now = datetime.now()

  # 特売情報追加
  sale_data = [
    ("たまねぎ", 98.0, SaleCategory.VEGETABLE, 34.7),
    ("にんじん", 158.0, SaleCategory.VEGETABLE, 20.0),
    ("豚肉", 198.0, SaleCategory.MEAT, 33.6),
    ("キャベツ", 128.0, SaleCategory.VEGETABLE, 15.0),
  ]

  for name, price, category, discount in sale_data:
    item = SaleItem(
      id=f"sale-{name}",
      store_name="イオン",
      product_name=name,
      price=price,
      original_price=price / (1 - discount / 100),
      unit="個",
      category=category,
      valid_from=now,
      valid_until=now + timedelta(days=3),
    )
    service.add_sale_item(item)

  # サンプルレシピ
  recipes = [
    {
      "name": "肉じゃが",
      "ingredients": ["たまねぎ", "にんじん", "豚肉", "じゃがいも"],
    },
    {
      "name": "野菜炒め",
      "ingredients": ["キャベツ", "にんじん", "豚肉"],
    },
    {
      "name": "カレー",
      "ingredients": ["たまねぎ", "にんじん", "牛肉", "じゃがいも"],
    },
  ]

  print("【特売食材を使ったレシピ推薦】\n")

  for recipe in recipes:
    recommendations = service.get_ingredient_recommendations(
      recipe["ingredients"]
    )

    if recommendations:
      estimate = service.get_recipe_cost_estimate(recipe["ingredients"])

      print(f"◆ {recipe['name']}")
      print(
        f"  特売材料: {len(recommendations)} / "
        f"{len(recipe['ingredients'])}種類"
      )
      print(f"  見積金額: ¥{estimate['total_cost']}")

      print("  特売中:")
      for item in recommendations[:3]:  # 上位3つ
        print(
          f"    - {item.product_name} ¥{item.price} "
          f"({item.discount_rate}% OFF)"
        )
      print()


def example_6_statistics():
  """例6: 統計情報"""
  print("=== 例6: 統計情報 ===\n")

  service = SaleService()
  now = datetime.now()

  # ランダムな特売情報を追加
  import random

  stores = ["イオン", "西友", "ライフ"]
  products = [
    ("たまねぎ", SaleCategory.VEGETABLE),
    ("にんじん", SaleCategory.VEGETABLE),
    ("豚肉", SaleCategory.MEAT),
    ("鶏肉", SaleCategory.MEAT),
    ("牛乳", SaleCategory.DAIRY),
    ("卵", SaleCategory.DAIRY),
  ]

  for i in range(20):
    store = random.choice(stores)
    product, category = random.choice(products)
    price = random.randint(80, 300)
    original_price = price * random.uniform(1.2, 1.5)

    service.add_sale_item(
      SaleItem(
        id=f"random-{i}",
        store_name=store,
        product_name=f"{product}_{i}",
        price=float(price),
        original_price=original_price,
        unit="個",
        category=category,
        valid_from=now,
        valid_until=now + timedelta(days=random.randint(1, 5)),
      )
    )

  # 統計取得
  stats = service.get_statistics()

  print("【特売情報統計】")
  print(f"有効な特売: {stats['total_active_sales']}件")
  print(f"平均割引率: {stats['average_discount_rate']}%")

  print("\n【カテゴリ別】")
  for category, count in stats["categories"].items():
    print(f"  {category}: {count}件")

  print("\n【店舗別】")
  for store, count in stats["stores"].items():
    print(f"  {store}: {count}件")

  print()


def main():
  """メイン関数"""
  examples = [
    ("基本的な使い方", example_1_basic_usage),
    ("価格比較", example_2_price_comparison),
    ("レシピ材料費見積もり", example_3_recipe_cost_estimate),
    ("チラシパース", example_4_flyer_parsing),
    ("レシピ推薦", example_5_recommendations),
    ("統計情報", example_6_statistics),
  ]

  print("\n" + "=" * 60)
  print("Personal Recipe Intelligence - 特売情報連携機能サンプル")
  print("=" * 60 + "\n")

  for i, (title, func) in enumerate(examples, 1):
    print(f"\n{'=' * 60}")
    print(f"{i}. {title}")
    print("=" * 60 + "\n")

    try:
      func()
    except Exception as e:
      print(f"エラー: {e}\n")

    if i < len(examples):
      input("Enterキーを押して次の例に進む...")
      print("\n")

  print("=" * 60)
  print("すべてのサンプルが完了しました")
  print("=" * 60 + "\n")


if __name__ == "__main__":
  main()

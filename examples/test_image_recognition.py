"""
画像認識サービス使用例
"""

import base64
from pathlib import Path

from PIL import Image

from backend.services.image_recognition_service import get_image_recognition_service


def create_sample_image():
  """サンプル画像作成"""
  img = Image.new("RGB", (800, 600), color=(255, 100, 100))
  img_path = Path("data/uploads/images/sample.jpg")
  img_path.parent.mkdir(parents=True, exist_ok=True)
  img.save(img_path)
  return img_path


def example_1_recognize_from_file():
  """例1: ファイルから認識"""
  print("\n=== 例1: ファイルから認識 ===")

  # サンプル画像作成
  img_path = create_sample_image()

  # サービス取得
  service = get_image_recognition_service(mode="mock")

  # 認識実行
  results = service.recognize_from_file(img_path, max_results=5)

  # 結果表示
  print(f"\n認識結果（上位5件）:")
  for i, result in enumerate(results, 1):
    print(
      f"{i}. {result['name']} ({result['name_en']}) - "
      f"信頼度: {result['confidence']*100:.1f}% - "
      f"カテゴリ: {result['category']}"
    )


def example_2_recognize_from_base64():
  """例2: Base64から認識"""
  print("\n=== 例2: Base64から認識 ===")

  # サンプル画像作成
  img = Image.new("RGB", (800, 600), color=(100, 255, 100))

  # Base64エンコード
  import io

  buffer = io.BytesIO()
  img.save(buffer, format="JPEG")
  buffer.seek(0)
  base64_data = base64.b64encode(buffer.read()).decode("utf-8")

  # サービス取得
  service = get_image_recognition_service(mode="mock")

  # 認識実行
  results = service.recognize_from_base64(base64_data, max_results=3)

  # 結果表示
  print(f"\n認識結果（上位3件）:")
  for i, result in enumerate(results, 1):
    print(
      f"{i}. {result['name']} - "
      f"信頼度: {result['confidence']*100:.1f}% - "
      f"キーワード: {', '.join(result['keywords'])}"
    )


def example_3_search_ingredients():
  """例3: 食材検索"""
  print("\n=== 例3: 食材検索 ===")

  service = get_image_recognition_service(mode="mock")

  # 日本語検索
  print("\n「トマト」で検索:")
  results = service.search_ingredients("トマト")
  for result in results:
    print(f"  - {result['name']} ({result['category']})")

  # カテゴリフィルター
  print("\n「野菜」カテゴリで検索:")
  results = service.search_ingredients("", category="野菜")
  print(f"  野菜は全{len(results)}種類見つかりました")
  for result in results[:5]:  # 上位5件のみ表示
    print(f"  - {result['name']}")


def example_4_get_categories():
  """例4: カテゴリ一覧取得"""
  print("\n=== 例4: カテゴリ一覧取得 ===")

  service = get_image_recognition_service(mode="mock")
  categories = service.get_categories()

  print(f"\n全{len(categories)}カテゴリ:")
  for category in categories:
    # 各カテゴリの食材数を取得
    ingredients = service.search_ingredients("", category=category)
    print(f"  - {category}: {len(ingredients)}種類")


def example_5_ingredient_detail():
  """例5: 食材詳細情報取得"""
  print("\n=== 例5: 食材詳細情報取得 ===")

  service = get_image_recognition_service(mode="mock")

  # トマトの情報取得
  ingredient_id = "tomato"
  info = service.get_ingredient_info(ingredient_id)

  if info:
    print(f"\n食材ID: {info['ingredient_id']}")
    print(f"名前: {info['name']}")
    print(f"英語名: {info['name_en']}")
    print(f"カテゴリ: {info['category']}")
    print(f"キーワード: {', '.join(info['keywords'])}")


def example_6_cache_demo():
  """例6: キャッシュ動作確認"""
  print("\n=== 例6: キャッシュ動作確認 ===")

  # サンプル画像作成
  img_path = create_sample_image()
  service = get_image_recognition_service(mode="mock")

  # 1回目の認識
  print("\n1回目の認識（キャッシュなし）:")
  import time

  start = time.time()
  results1 = service.recognize_from_file(img_path, max_results=5)
  time1 = time.time() - start
  print(f"処理時間: {time1*1000:.2f}ms")
  print(f"認識結果: {results1[0]['name']}")

  # 2回目の認識（キャッシュヒット）
  print("\n2回目の認識（キャッシュヒット）:")
  start = time.time()
  results2 = service.recognize_from_file(img_path, max_results=5)
  time2 = time.time() - start
  print(f"処理時間: {time2*1000:.2f}ms")
  print(f"認識結果: {results2[0]['name']}")

  # 結果比較
  print(f"\n結果が一致: {results1 == results2}")
  print(f"高速化: {time1/time2:.1f}倍")


def example_7_multiple_recognition():
  """例7: 複数画像の一括認識"""
  print("\n=== 例7: 複数画像の一括認識 ===")

  service = get_image_recognition_service(mode="mock")
  colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
  color_names = ["赤", "緑", "青"]

  for color, color_name in zip(colors, color_names):
    # 画像作成
    img = Image.new("RGB", (800, 600), color=color)
    img_path = Path(f"data/uploads/images/sample_{color_name}.jpg")
    img.save(img_path)

    # 認識
    results = service.recognize_from_file(img_path, max_results=3)

    print(f"\n{color_name}色画像の認識結果:")
    for result in results:
      print(f"  - {result['name']} ({result['confidence']*100:.0f}%)")


def main():
  """すべての例を実行"""
  print("=" * 60)
  print("画像認識サービス 使用例デモ")
  print("=" * 60)

  example_1_recognize_from_file()
  example_2_recognize_from_base64()
  example_3_search_ingredients()
  example_4_get_categories()
  example_5_ingredient_detail()
  example_6_cache_demo()
  example_7_multiple_recognition()

  print("\n" + "=" * 60)
  print("デモ完了")
  print("=" * 60)


if __name__ == "__main__":
  main()

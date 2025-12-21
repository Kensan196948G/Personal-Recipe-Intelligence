#!/usr/bin/env python3
"""
Recipe Service 統合の検証スクリプト
"""

import os
import sys

BASE_DIR = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"


def check_file_exists(filepath, description):
  """ファイル存在確認"""
  exists = os.path.exists(filepath)
  status = "✓" if exists else "✗"
  print(f"  {status} {description}")
  return exists


def check_file_not_exists(filepath, description):
  """ファイル非存在確認"""
  exists = os.path.exists(filepath)
  status = "✓" if not exists else "✗"
  print(f"  {status} {description}")
  return not exists


def verify_imports():
  """インポート検証"""
  print("\n4. インポート検証")
  print("-" * 80)

  sys.path.insert(0, BASE_DIR)

  try:
    from backend.models.recipe import Recipe

    print("  ✓ Recipe モデルのインポート成功")
  except ImportError as e:
    print(f"  ✗ Recipe モデルのインポート失敗: {e}")
    return False

  try:
    from backend.repositories.recipe_repository import RecipeRepository

    print("  ✓ RecipeRepository のインポート成功")
  except ImportError as e:
    print(f"  ✗ RecipeRepository のインポート失敗: {e}")
    return False

  try:
    from backend.services.recipe_service import RecipeService

    print("  ✓ RecipeService のインポート成功")
  except ImportError as e:
    print(f"  ✗ RecipeService のインポート失敗: {e}")
    return False

  return True


def verify_service_methods():
  """サービスメソッド検証"""
  print("\n5. RecipeService メソッド検証")
  print("-" * 80)

  sys.path.insert(0, BASE_DIR)

  try:
    from backend.services.recipe_service import RecipeService

    service = RecipeService

    required_methods = [
      "create_recipe",
      "get_recipe",
      "get_all_recipes",
      "update_recipe",
      "delete_recipe",
      "search_recipes",
      "get_recipes_by_tag",
      "get_all_tags",
      "parse_recipe_from_url",
      "parse_recipe_from_image",
      "get_recipe_count",
      "get_statistics",
      "bulk_create_recipes",
      "bulk_delete_recipes",
      "export_recipe_to_json",
      "import_recipe_from_json",
    ]

    all_ok = True
    for method in required_methods:
      if hasattr(service, method):
        print(f"  ✓ {method}")
      else:
        print(f"  ✗ {method} - NOT FOUND")
        all_ok = False

    return all_ok

  except Exception as e:
    print(f"  ✗ エラー: {e}")
    return False


def main():
  """メイン処理"""
  print("=" * 100)
  print("Recipe Service 統合検証")
  print("=" * 100)

  # 1. ディレクトリ構造確認
  print("\n1. ディレクトリ構造確認")
  print("-" * 80)

  dirs = [
    (os.path.join(BASE_DIR, "backend"), "backend/"),
    (os.path.join(BASE_DIR, "backend", "models"), "backend/models/"),
    (os.path.join(BASE_DIR, "backend", "repositories"), "backend/repositories/"),
    (os.path.join(BASE_DIR, "backend", "services"), "backend/services/"),
    (os.path.join(BASE_DIR, "backend", "parsers"), "backend/parsers/"),
    (os.path.join(BASE_DIR, "backend", "tests"), "backend/tests/"),
  ]

  all_dirs_ok = all(check_file_exists(d[0], d[1]) for d in dirs)

  # 2. 必須ファイル確認
  print("\n2. 必須ファイル確認")
  print("-" * 80)

  files = [
    (os.path.join(BASE_DIR, "backend", "models", "recipe.py"), "Recipe モデル"),
    (
      os.path.join(BASE_DIR, "backend", "repositories", "recipe_repository.py"),
      "RecipeRepository",
    ),
    (os.path.join(BASE_DIR, "backend", "services", "recipe_service.py"), "RecipeService"),
    (os.path.join(BASE_DIR, "backend", "parsers", "web_parser.py"), "WebRecipeParser"),
    (os.path.join(BASE_DIR, "backend", "parsers", "ocr_parser.py"), "OCRRecipeParser"),
    (
      os.path.join(BASE_DIR, "backend", "tests", "test_recipe_service.py"),
      "RecipeService テスト",
    ),
  ]

  all_files_ok = all(check_file_exists(f[0], f[1]) for f in files)

  # 3. 削除確認
  print("\n3. recipe_service_new.py 削除確認")
  print("-" * 80)

  removed_ok = check_file_not_exists(
    os.path.join(BASE_DIR, "backend", "services", "recipe_service_new.py"),
    "recipe_service_new.py が削除されている",
  )

  # 4. インポート検証
  imports_ok = verify_imports()

  # 5. メソッド検証
  methods_ok = verify_service_methods()

  # 結果サマリー
  print("\n" + "=" * 100)
  print("検証結果サマリー")
  print("=" * 100)

  results = [
    ("ディレクトリ構造", all_dirs_ok),
    ("必須ファイル", all_files_ok),
    ("recipe_service_new.py 削除", removed_ok),
    ("インポート", imports_ok),
    ("メソッド", methods_ok),
  ]

  all_ok = all(r[1] for r in results)

  for name, ok in results:
    status = "✓ OK" if ok else "✗ FAILED"
    print(f"  {status}  {name}")

  print("\n" + "=" * 100)

  if all_ok:
    print("すべての検証に合格しました")
    print("\n次のステップ:")
    print("  python3 -m pytest backend/tests/test_recipe_service.py -v")
    return 0
  else:
    print("一部の検証に失敗しました")
    print("\n対処方法:")
    print("  python3 initialize_backend.py")
    print("  python3 merge_recipe_services.py")
    return 1


if __name__ == "__main__":
  sys.exit(main())

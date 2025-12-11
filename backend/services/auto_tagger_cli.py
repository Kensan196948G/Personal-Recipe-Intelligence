#!/usr/bin/env python3
"""
Auto-Tagger CLI Tool

Command-line interface for testing the auto-tagging functionality.

Usage:
  python backend/services/auto_tagger_cli.py --title "親子丼"
  python backend/services/auto_tagger_cli.py --title "カレーライス" --ingredients "じゃがいも,人参,玉ねぎ"
  python backend/services/auto_tagger_cli.py --interactive
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.auto_tagger import AutoTagger  # noqa: E402


def print_banner():
  """Print CLI banner."""
  print("\n" + "=" * 60)
  print("  Personal Recipe Intelligence - Auto-Tagger CLI")
  print("=" * 60 + "\n")


def print_tags(tags: List[str], title: str = "提案タグ"):
  """
  Print tags in a formatted way.

  Args:
    tags: List of tag names
    title: Section title
  """
  if not tags:
    print(f"{title}: (なし)")
    return

  print(f"{title}:")
  for i, tag in enumerate(tags, 1):
    print(f"  {i}. {tag}")


def print_categorized_tags(categorized: dict):
  """
  Print categorized tags.

  Args:
    categorized: Dictionary of category -> tags
  """
  if not categorized:
    print("カテゴリ別タグ: (なし)")
    return

  print("\nカテゴリ別タグ:")
  for category, tags in categorized.items():
    print(f"\n  [{category}]")
    for tag in tags:
      print(f"    - {tag}")


def interactive_mode(tagger: AutoTagger):
  """
  Interactive mode for testing tag suggestions.

  Args:
    tagger: AutoTagger instance
  """
  print("対話モード（終了するには 'quit' または 'exit' を入力）\n")

  while True:
    print("-" * 60)

    # Get title
    title = input("レシピ名: ").strip()
    if title.lower() in ["quit", "exit", "q"]:
      print("\n終了します。")
      break

    if not title:
      print("レシピ名を入力してください。\n")
      continue

    # Get description
    description = input("説明（任意、Enter でスキップ）: ").strip()

    # Get ingredients
    ingredients_input = input("材料（カンマ区切り、任意）: ").strip()
    ingredients = None
    if ingredients_input:
      ingredients = [ing.strip() for ing in ingredients_input.split(",")]

    # Get instructions
    instructions_input = input("手順（カンマ区切り、任意）: ").strip()
    instructions = None
    if instructions_input:
      instructions = [inst.strip() for inst in instructions_input.split(",")]

    # Suggest tags
    print("\n処理中...\n")

    tags = tagger.suggest_tags(
      title=title,
      description=description,
      ingredients=ingredients,
      instructions=instructions
    )

    categorized = tagger.suggest_tags_by_category(
      title=title,
      description=description,
      ingredients=ingredients,
      instructions=instructions
    )

    # Display results
    print_tags(tags)
    print_categorized_tags(categorized)
    print()


def batch_mode(tagger: AutoTagger, json_file: str):
  """
  Batch processing mode from JSON file.

  Args:
    tagger: AutoTagger instance
    json_file: Path to JSON file with recipes

  Expected JSON format:
  [
    {
      "title": "Recipe name",
      "description": "Description (optional)",
      "ingredients": ["ingredient1", "ingredient2"],
      "instructions": ["step1", "step2"]
    }
  ]
  """
  try:
    with open(json_file, "r", encoding="utf-8") as f:
      recipes = json.load(f)

    if not isinstance(recipes, list):
      print("エラー: JSONファイルはレシピの配列である必要があります。")
      return

    print(f"\n{len(recipes)} 件のレシピを処理します...\n")

    results = []

    for i, recipe in enumerate(recipes, 1):
      title = recipe.get("title", "")
      if not title:
        print(f"警告: レシピ#{i} にタイトルがありません。スキップします。")
        continue

      print(f"[{i}/{len(recipes)}] {title}")

      tags = tagger.suggest_tags(
        title=title,
        description=recipe.get("description", ""),
        ingredients=recipe.get("ingredients"),
        instructions=recipe.get("instructions")
      )

      results.append({
        "title": title,
        "suggested_tags": tags
      })

      print(f"  タグ: {', '.join(tags)}\n")

    # Save results
    output_file = Path(json_file).stem + "_tagged.json"
    with open(output_file, "w", encoding="utf-8") as f:
      json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n結果を {output_file} に保存しました。")

  except FileNotFoundError:
    print(f"エラー: ファイル '{json_file}' が見つかりません。")
  except json.JSONDecodeError as e:
    print(f"エラー: JSONの解析に失敗しました: {e}")
  except Exception as e:
    print(f"エラー: {e}")


def list_info(tagger: AutoTagger, args):
  """
  List available tags and categories.

  Args:
    tagger: AutoTagger instance
    args: Command-line arguments
  """
  if args.list_categories:
    print("利用可能なカテゴリ:\n")
    categories = tagger.get_categories()
    for i, cat in enumerate(categories, 1):
      print(f"  {i}. {cat}")

  if args.list_tags:
    if args.category:
      tags = tagger.get_tags_by_category(args.category)
      print(f"\nカテゴリ '{args.category}' のタグ:\n")
    else:
      tags = tagger.get_all_tags()
      print("\n利用可能なすべてのタグ:\n")

    for i, tag in enumerate(tags, 1):
      print(f"  {i}. {tag}")

    print(f"\n合計: {len(tags)} 個")


def main():
  """Main CLI entry point."""
  parser = argparse.ArgumentParser(
    description="Personal Recipe Intelligence - Auto-Tagger CLI",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
使用例:
  # 基本的な使用
  %(prog)s --title "親子丼"

  # 材料を指定
  %(prog)s --title "カレー" --ingredients "じゃがいも,人参,玉ねぎ"

  # 詳細情報を含む
  %(prog)s --title "パスタ" --description "トマトソース" --ingredients "パスタ,トマト"

  # カテゴリ別に表示
  %(prog)s --title "鶏の照り焼き" --categorized

  # 対話モード
  %(prog)s --interactive

  # バッチ処理
  %(prog)s --batch recipes.json

  # タグ一覧を表示
  %(prog)s --list-tags

  # カテゴリ一覧を表示
  %(prog)s --list-categories
    """
  )

  # Recipe input options
  parser.add_argument(
    "--title", "-t",
    type=str,
    help="レシピのタイトル"
  )
  parser.add_argument(
    "--description", "-d",
    type=str,
    help="レシピの説明"
  )
  parser.add_argument(
    "--ingredients", "-i",
    type=str,
    help="材料（カンマ区切り）"
  )
  parser.add_argument(
    "--instructions", "-s",
    type=str,
    help="手順（カンマ区切り）"
  )
  parser.add_argument(
    "--max-tags", "-m",
    type=int,
    help="最大タグ数"
  )

  # Output options
  parser.add_argument(
    "--categorized", "-c",
    action="store_true",
    help="カテゴリ別にタグを表示"
  )
  parser.add_argument(
    "--json", "-j",
    action="store_true",
    help="JSON形式で出力"
  )

  # Mode options
  parser.add_argument(
    "--interactive",
    action="store_true",
    help="対話モードで実行"
  )
  parser.add_argument(
    "--batch", "-b",
    type=str,
    metavar="FILE",
    help="JSONファイルからバッチ処理"
  )

  # Info options
  parser.add_argument(
    "--list-tags",
    action="store_true",
    help="利用可能なタグ一覧を表示"
  )
  parser.add_argument(
    "--list-categories",
    action="store_true",
    help="カテゴリ一覧を表示"
  )
  parser.add_argument(
    "--category",
    type=str,
    help="特定カテゴリのタグを表示（--list-tagsと併用）"
  )

  # Custom rules file
  parser.add_argument(
    "--rules",
    type=str,
    help="カスタムルールファイルのパス"
  )

  args = parser.parse_args()

  print_banner()

  # Initialize tagger
  try:
    tagger = AutoTagger(rules_path=args.rules)
  except Exception as e:
    print(f"エラー: Auto-Tagger の初期化に失敗しました: {e}")
    return 1

  # Handle different modes
  if args.interactive:
    interactive_mode(tagger)
    return 0

  if args.batch:
    batch_mode(tagger, args.batch)
    return 0

  if args.list_tags or args.list_categories:
    list_info(tagger, args)
    return 0

  if not args.title:
    parser.print_help()
    return 1

  # Process single recipe
  ingredients = None
  if args.ingredients:
    ingredients = [ing.strip() for ing in args.ingredients.split(",")]

  instructions = None
  if args.instructions:
    instructions = [inst.strip() for inst in args.instructions.split(",")]

  # Suggest tags
  if args.categorized:
    categorized = tagger.suggest_tags_by_category(
      title=args.title,
      description=args.description or "",
      ingredients=ingredients,
      instructions=instructions
    )

    if args.json:
      print(json.dumps(categorized, ensure_ascii=False, indent=2))
    else:
      print(f"レシピ: {args.title}\n")
      print_categorized_tags(categorized)
  else:
    tags = tagger.suggest_tags(
      title=args.title,
      description=args.description or "",
      ingredients=ingredients,
      instructions=instructions,
      max_tags=args.max_tags
    )

    if args.json:
      print(json.dumps({"tags": tags}, ensure_ascii=False, indent=2))
    else:
      print(f"レシピ: {args.title}\n")
      print_tags(tags)

  print()
  return 0


if __name__ == "__main__":
  sys.exit(main())

#!/usr/bin/env python3
"""
recipe_service.py と recipe_service_new.py を統合するスクリプト

使用方法:
  python merge_recipe_services.py
"""

import os
import sys
from datetime import datetime

BASE_DIR = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
SERVICES_DIR = os.path.join(BASE_DIR, "backend", "services")
OUTPUT_FILE = os.path.join(SERVICES_DIR, "recipe_service_merged.py")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")


def read_file(filepath):
  """ファイルを読み取る"""
  if not os.path.exists(filepath):
    return None
  with open(filepath, "r", encoding="utf-8") as f:
    return f.read()


def write_file(filepath, content):
  """ファイルを書き込む"""
  os.makedirs(os.path.dirname(filepath), exist_ok=True)
  with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)


def backup_file(filepath):
  """ファイルをバックアップ"""
  if not os.path.exists(filepath):
    return None

  os.makedirs(BACKUP_DIR, exist_ok=True)
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = os.path.basename(filepath)
  backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}.bak")

  content = read_file(filepath)
  write_file(backup_path, content)
  print(f"  ✓ Backup created: {backup_path}")
  return backup_path


def create_merged_service():
  """統合版の RecipeService を生成"""
  return '''"""
Recipe Service - 統合版
レシピの CRUD 操作、検索、解析処理を提供するサービス層
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json

from backend.models.recipe import Recipe
from backend.repositories.recipe_repository import RecipeRepository
from backend.parsers.web_parser import WebRecipeParser
from backend.parsers.ocr_parser import OCRRecipeParser

logger = logging.getLogger(__name__)


class RecipeService:
  """
  レシピ管理のビジネスロジックを提供するサービスクラス
  """

  def __init__(self, repository: Optional[RecipeRepository] = None):
    """
    RecipeService の初期化

    Args:
        repository: RecipeRepository インスタンス（省略時は新規作成）
    """
    self.repository = repository or RecipeRepository()
    self.web_parser = WebRecipeParser()
    self.ocr_parser = OCRRecipeParser()

  # ========================================
  # CRUD 操作
  # ========================================

  def create_recipe(self, recipe_data: Dict[str, Any]) -> Recipe:
    """
    新しいレシピを作成

    Args:
        recipe_data: レシピデータ（辞書形式）

    Returns:
        Recipe: 作成されたレシピオブジェクト

    Raises:
        ValueError: バリデーションエラー
    """
    try:
      # 必須フィールドのバリデーション
      if not recipe_data.get("title"):
        raise ValueError("タイトルは必須です")

      # Recipe オブジェクトの生成
      recipe = Recipe(
        title=recipe_data["title"],
        description=recipe_data.get("description", ""),
        ingredients=recipe_data.get("ingredients", []),
        steps=recipe_data.get("steps", []),
        tags=recipe_data.get("tags", []),
        source_url=recipe_data.get("source_url"),
        image_path=recipe_data.get("image_path"),
        cooking_time=recipe_data.get("cooking_time"),
        servings=recipe_data.get("servings"),
        difficulty=recipe_data.get("difficulty"),
      )

      # DB への保存
      saved_recipe = self.repository.create(recipe)
      logger.info(f"レシピを作成しました: ID={saved_recipe.id}, Title={saved_recipe.title}")

      return saved_recipe

    except Exception as e:
      logger.error(f"レシピ作成エラー: {str(e)}")
      raise

  def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
    """
    指定 ID のレシピを取得

    Args:
        recipe_id: レシピ ID

    Returns:
        Recipe | None: レシピオブジェクト（存在しない場合は None）
    """
    try:
      recipe = self.repository.get_by_id(recipe_id)
      if recipe:
        logger.debug(f"レシピを取得しました: ID={recipe_id}")
      else:
        logger.warning(f"レシピが見つかりません: ID={recipe_id}")
      return recipe

    except Exception as e:
      logger.error(f"レシピ取得エラー: ID={recipe_id}, Error={str(e)}")
      raise

  def get_all_recipes(
    self, limit: int = 100, offset: int = 0, order_by: str = "created_at"
  ) -> List[Recipe]:
    """
    すべてのレシピを取得（ページング対応）

    Args:
        limit: 取得件数上限
        offset: オフセット
        order_by: ソート順（created_at / updated_at / title）

    Returns:
        List[Recipe]: レシピリスト
    """
    try:
      recipes = self.repository.get_all(limit=limit, offset=offset, order_by=order_by)
      logger.debug(f"レシピリストを取得: 件数={len(recipes)}")
      return recipes

    except Exception as e:
      logger.error(f"レシピリスト取得エラー: {str(e)}")
      raise

  def update_recipe(self, recipe_id: int, update_data: Dict[str, Any]) -> Optional[Recipe]:
    """
    レシピ情報を更新

    Args:
        recipe_id: レシピ ID
        update_data: 更新データ（辞書形式）

    Returns:
        Recipe | None: 更新後のレシピ（存在しない場合は None）
    """
    try:
      recipe = self.repository.get_by_id(recipe_id)
      if not recipe:
        logger.warning(f"更新対象のレシピが見つかりません: ID={recipe_id}")
        return None

      # 更新可能フィールドのみ反映
      allowed_fields = [
        "title",
        "description",
        "ingredients",
        "steps",
        "tags",
        "source_url",
        "image_path",
        "cooking_time",
        "servings",
        "difficulty",
      ]

      for field in allowed_fields:
        if field in update_data:
          setattr(recipe, field, update_data[field])

      recipe.updated_at = datetime.now()

      updated_recipe = self.repository.update(recipe)
      logger.info(f"レシピを更新しました: ID={recipe_id}")

      return updated_recipe

    except Exception as e:
      logger.error(f"レシピ更新エラー: ID={recipe_id}, Error={str(e)}")
      raise

  def delete_recipe(self, recipe_id: int) -> bool:
    """
    レシピを削除

    Args:
        recipe_id: レシピ ID

    Returns:
        bool: 削除成功時 True、失敗時 False
    """
    try:
      result = self.repository.delete(recipe_id)
      if result:
        logger.info(f"レシピを削除しました: ID={recipe_id}")
      else:
        logger.warning(f"削除対象のレシピが見つかりません: ID={recipe_id}")
      return result

    except Exception as e:
      logger.error(f"レシピ削除エラー: ID={recipe_id}, Error={str(e)}")
      raise

  # ========================================
  # 検索機能
  # ========================================

  def search_recipes(
    self,
    keyword: Optional[str] = None,
    tags: Optional[List[str]] = None,
    ingredients: Optional[List[str]] = None,
    limit: int = 100,
    offset: int = 0,
  ) -> List[Recipe]:
    """
    レシピを検索（キーワード、タグ、材料で絞り込み）

    Args:
        keyword: キーワード（タイトル・説明文で部分一致）
        tags: タグリスト（AND 検索）
        ingredients: 材料リスト（AND 検索）
        limit: 取得件数上限
        offset: オフセット

    Returns:
        List[Recipe]: 検索結果のレシピリスト
    """
    try:
      recipes = self.repository.search(
        keyword=keyword, tags=tags, ingredients=ingredients, limit=limit, offset=offset
      )
      logger.debug(f"レシピ検索実行: 検索結果={len(recipes)}件")
      return recipes

    except Exception as e:
      logger.error(f"レシピ検索エラー: {str(e)}")
      raise

  def get_recipes_by_tag(self, tag: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
    """
    指定タグを持つレシピを取得

    Args:
        tag: タグ名
        limit: 取得件数上限
        offset: オフセット

    Returns:
        List[Recipe]: レシピリスト
    """
    try:
      recipes = self.repository.get_by_tag(tag, limit=limit, offset=offset)
      logger.debug(f"タグ検索: tag={tag}, 結果={len(recipes)}件")
      return recipes

    except Exception as e:
      logger.error(f"タグ検索エラー: tag={tag}, Error={str(e)}")
      raise

  def get_all_tags(self) -> List[str]:
    """
    すべてのタグを取得（重複なし）

    Returns:
        List[str]: タグリスト
    """
    try:
      tags = self.repository.get_all_tags()
      logger.debug(f"タグ一覧を取得: {len(tags)}件")
      return tags

    except Exception as e:
      logger.error(f"タグ一覧取得エラー: {str(e)}")
      raise

  # ========================================
  # レシピ解析（Web / OCR）
  # ========================================

  def parse_recipe_from_url(self, url: str, save: bool = True) -> Recipe:
    """
    Web URL からレシピを解析・抽出

    Args:
        url: レシピページの URL
        save: True の場合、DB に保存する

    Returns:
        Recipe: 解析されたレシピオブジェクト

    Raises:
        ValueError: URL 解析に失敗した場合
    """
    try:
      logger.info(f"Web レシピ解析開始: URL={url}")

      # Web パーサーで解析
      recipe_data = self.web_parser.parse(url)

      if not recipe_data or not recipe_data.get("title"):
        raise ValueError(f"URL からレシピを抽出できませんでした: {url}")

      # Recipe オブジェクト化
      recipe = Recipe(
        title=recipe_data["title"],
        description=recipe_data.get("description", ""),
        ingredients=recipe_data.get("ingredients", []),
        steps=recipe_data.get("steps", []),
        tags=recipe_data.get("tags", []),
        source_url=url,
        image_path=recipe_data.get("image_path"),
        cooking_time=recipe_data.get("cooking_time"),
        servings=recipe_data.get("servings"),
        difficulty=recipe_data.get("difficulty"),
      )

      # 保存オプションが有効な場合
      if save:
        recipe = self.repository.create(recipe)
        logger.info(f"Web レシピを保存しました: ID={recipe.id}, URL={url}")

      return recipe

    except Exception as e:
      logger.error(f"Web レシピ解析エラー: URL={url}, Error={str(e)}")
      raise

  def parse_recipe_from_image(self, image_path: str, save: bool = True) -> Recipe:
    """
    画像（OCR）からレシピを解析・抽出

    Args:
        image_path: 画像ファイルパス
        save: True の場合、DB に保存する

    Returns:
        Recipe: 解析されたレシピオブジェクト

    Raises:
        ValueError: OCR 解析に失敗した場合
    """
    try:
      logger.info(f"OCR レシピ解析開始: Image={image_path}")

      # OCR パーサーで解析
      recipe_data = self.ocr_parser.parse(image_path)

      if not recipe_data or not recipe_data.get("title"):
        raise ValueError(f"画像からレシピを抽出できませんでした: {image_path}")

      # Recipe オブジェクト化
      recipe = Recipe(
        title=recipe_data["title"],
        description=recipe_data.get("description", ""),
        ingredients=recipe_data.get("ingredients", []),
        steps=recipe_data.get("steps", []),
        tags=recipe_data.get("tags", []),
        image_path=image_path,
        cooking_time=recipe_data.get("cooking_time"),
        servings=recipe_data.get("servings"),
        difficulty=recipe_data.get("difficulty"),
      )

      # 保存オプションが有効な場合
      if save:
        recipe = self.repository.create(recipe)
        logger.info(f"OCR レシピを保存しました: ID={recipe.id}, Image={image_path}")

      return recipe

    except Exception as e:
      logger.error(f"OCR レシピ解析エラー: Image={image_path}, Error={str(e)}")
      raise

  # ========================================
  # 統計情報
  # ========================================

  def get_recipe_count(self) -> int:
    """
    レシピ総数を取得

    Returns:
        int: レシピ総数
    """
    try:
      count = self.repository.count()
      logger.debug(f"レシピ総数: {count}")
      return count

    except Exception as e:
      logger.error(f"レシピ総数取得エラー: {str(e)}")
      raise

  def get_statistics(self) -> Dict[str, Any]:
    """
    レシピ統計情報を取得

    Returns:
        Dict[str, Any]: 統計情報
            - total_recipes: 総レシピ数
            - total_tags: 総タグ数
            - recipes_with_images: 画像付きレシピ数
            - recipes_with_source: ソース URL 付きレシピ数
    """
    try:
      total_recipes = self.repository.count()
      all_tags = self.repository.get_all_tags()
      all_recipes = self.repository.get_all(limit=10000)

      recipes_with_images = sum(1 for r in all_recipes if r.image_path)
      recipes_with_source = sum(1 for r in all_recipes if r.source_url)

      stats = {
        "total_recipes": total_recipes,
        "total_tags": len(all_tags),
        "recipes_with_images": recipes_with_images,
        "recipes_with_source": recipes_with_source,
      }

      logger.debug(f"統計情報: {json.dumps(stats, ensure_ascii=False)}")
      return stats

    except Exception as e:
      logger.error(f"統計情報取得エラー: {str(e)}")
      raise

  # ========================================
  # バッチ操作
  # ========================================

  def bulk_create_recipes(self, recipes_data: List[Dict[str, Any]]) -> List[Recipe]:
    """
    複数レシピを一括作成

    Args:
        recipes_data: レシピデータのリスト

    Returns:
        List[Recipe]: 作成されたレシピのリスト
    """
    created_recipes = []

    for recipe_data in recipes_data:
      try:
        recipe = self.create_recipe(recipe_data)
        created_recipes.append(recipe)
      except Exception as e:
        logger.error(f"一括作成エラー: {recipe_data.get('title', 'Unknown')}, {str(e)}")
        continue

    logger.info(f"一括作成完了: {len(created_recipes)}/{len(recipes_data)} 件")
    return created_recipes

  def bulk_delete_recipes(self, recipe_ids: List[int]) -> int:
    """
    複数レシピを一括削除

    Args:
        recipe_ids: 削除対象のレシピ ID リスト

    Returns:
        int: 削除成功件数
    """
    deleted_count = 0

    for recipe_id in recipe_ids:
      try:
        if self.delete_recipe(recipe_id):
          deleted_count += 1
      except Exception as e:
        logger.error(f"一括削除エラー: ID={recipe_id}, {str(e)}")
        continue

    logger.info(f"一括削除完了: {deleted_count}/{len(recipe_ids)} 件")
    return deleted_count

  # ========================================
  # ユーティリティ
  # ========================================

  def export_recipe_to_json(self, recipe_id: int) -> Optional[str]:
    """
    レシピを JSON 形式でエクスポート

    Args:
        recipe_id: レシピ ID

    Returns:
        str | None: JSON 文字列（存在しない場合は None）
    """
    try:
      recipe = self.repository.get_by_id(recipe_id)
      if not recipe:
        return None

      recipe_dict = {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
        "steps": recipe.steps,
        "tags": recipe.tags,
        "source_url": recipe.source_url,
        "image_path": recipe.image_path,
        "cooking_time": recipe.cooking_time,
        "servings": recipe.servings,
        "difficulty": recipe.difficulty,
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None,
      }

      return json.dumps(recipe_dict, ensure_ascii=False, indent=2)

    except Exception as e:
      logger.error(f"JSON エクスポートエラー: ID={recipe_id}, {str(e)}")
      raise

  def import_recipe_from_json(self, json_str: str) -> Recipe:
    """
    JSON 形式からレシピをインポート

    Args:
        json_str: レシピの JSON 文字列

    Returns:
        Recipe: インポートされたレシピオブジェクト

    Raises:
        ValueError: JSON パースエラー
    """
    try:
      recipe_data = json.loads(json_str)

      # 不要なフィールドを除去
      recipe_data.pop("id", None)
      recipe_data.pop("created_at", None)
      recipe_data.pop("updated_at", None)

      return self.create_recipe(recipe_data)

    except json.JSONDecodeError as e:
      logger.error(f"JSON パースエラー: {str(e)}")
      raise ValueError(f"無効な JSON 形式です: {str(e)}")
    except Exception as e:
      logger.error(f"JSON インポートエラー: {str(e)}")
      raise
'''


def main():
  """メイン処理"""
  print("=" * 100)
  print("Recipe Service 統合スクリプト")
  print("=" * 100)

  # ディレクトリ確認
  if not os.path.exists(SERVICES_DIR):
    print(f"\nError: Services directory not found: {SERVICES_DIR}")
    print("Creating directory...")
    os.makedirs(SERVICES_DIR, exist_ok=True)

  # 既存ファイルの確認
  recipe_service_path = os.path.join(SERVICES_DIR, "recipe_service.py")
  recipe_service_new_path = os.path.join(SERVICES_DIR, "recipe_service_new.py")

  print(f"\n1. Checking existing files:")
  print(f"   recipe_service.py: {'EXISTS' if os.path.exists(recipe_service_path) else 'NOT FOUND'}")
  print(f"   recipe_service_new.py: {'EXISTS' if os.path.exists(recipe_service_new_path) else 'NOT FOUND'}")

  # 既存ファイルが存在する場合はバックアップ
  print(f"\n2. Creating backups:")
  if os.path.exists(recipe_service_path):
    backup_file(recipe_service_path)
  else:
    print("   - recipe_service.py not found (no backup needed)")

  if os.path.exists(recipe_service_new_path):
    backup_file(recipe_service_new_path)
  else:
    print("   - recipe_service_new.py not found (no backup needed)")

  # 統合版を生成
  print(f"\n3. Creating merged version:")
  merged_content = create_merged_service()
  write_file(OUTPUT_FILE, merged_content)
  print(f"   ✓ Created: {OUTPUT_FILE}")

  # recipe_service.py を置き換え
  print(f"\n4. Replacing recipe_service.py:")
  write_file(recipe_service_path, merged_content)
  print(f"   ✓ Updated: {recipe_service_path}")

  # recipe_service_new.py を削除（存在する場合）
  if os.path.exists(recipe_service_new_path):
    print(f"\n5. Removing recipe_service_new.py:")
    os.remove(recipe_service_new_path)
    print(f"   ✓ Deleted: {recipe_service_new_path}")
  else:
    print(f"\n5. recipe_service_new.py not found (no deletion needed)")

  # __init__.py を更新
  print(f"\n6. Updating __init__.py:")
  init_content = '''"""
Services パッケージ
ビジネスロジック層を提供
"""

from backend.services.recipe_service import RecipeService

__all__ = ["RecipeService"]
'''
  init_path = os.path.join(SERVICES_DIR, "__init__.py")
  write_file(init_path, init_content)
  print(f"   ✓ Updated: {init_path}")

  # 完了メッセージ
  print(f"\n{'=' * 100}")
  print("統合完了")
  print(f"{'=' * 100}")
  print(f"\n統合されたファイル: {recipe_service_path}")
  print(f"バックアップ場所: {BACKUP_DIR}")
  print(f"\n次のステップ:")
  print(f"  1. インポート文を確認・更新")
  print(f"  2. テストを実行: pytest backend/tests/")
  print(f"  3. 動作確認後、バックアップを削除")


if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"\nError: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

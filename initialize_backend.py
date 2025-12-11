#!/usr/bin/env python3
"""
Backend 完全初期化スクリプト
Recipe Service および依存ファイルを生成
"""

import os
from datetime import datetime

BASE_DIR = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"


def ensure_dir(path):
  """ディレクトリを作成"""
  os.makedirs(path, exist_ok=True)
  print(f"  ✓ Created: {path}")


def write_file(filepath, content):
  """ファイルを作成"""
  os.makedirs(os.path.dirname(filepath), exist_ok=True)
  with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
  print(f"  ✓ Created: {filepath}")


def init_backend_structure():
  """Backend ディレクトリ構造を初期化"""
  print("\n1. ディレクトリ構造作成")
  print("-" * 80)

  dirs = [
    os.path.join(BASE_DIR, "backend"),
    os.path.join(BASE_DIR, "backend", "models"),
    os.path.join(BASE_DIR, "backend", "repositories"),
    os.path.join(BASE_DIR, "backend", "services"),
    os.path.join(BASE_DIR, "backend", "parsers"),
    os.path.join(BASE_DIR, "backend", "api"),
    os.path.join(BASE_DIR, "backend", "tests"),
    os.path.join(BASE_DIR, "backups"),
    os.path.join(BASE_DIR, "data"),
    os.path.join(BASE_DIR, "logs"),
  ]

  for d in dirs:
    ensure_dir(d)


def create_recipe_model():
  """Recipe Model を作成"""
  content = '''"""
Recipe Model
レシピデータモデル
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Recipe:
  """レシピデータモデル"""

  title: str
  description: str = ""
  ingredients: List[str] = field(default_factory=list)
  steps: List[str] = field(default_factory=list)
  tags: List[str] = field(default_factory=list)
  source_url: Optional[str] = None
  image_path: Optional[str] = None
  cooking_time: Optional[int] = None  # 分単位
  servings: Optional[int] = None  # 人数
  difficulty: Optional[str] = None  # easy / medium / hard
  id: Optional[int] = None
  created_at: Optional[datetime] = None
  updated_at: Optional[datetime] = None

  def __post_init__(self):
    """初期化後の処理"""
    if self.created_at is None:
      self.created_at = datetime.now()
    if self.updated_at is None:
      self.updated_at = datetime.now()

  def to_dict(self):
    """辞書形式に変換"""
    return {
      "id": self.id,
      "title": self.title,
      "description": self.description,
      "ingredients": self.ingredients,
      "steps": self.steps,
      "tags": self.tags,
      "source_url": self.source_url,
      "image_path": self.image_path,
      "cooking_time": self.cooking_time,
      "servings": self.servings,
      "difficulty": self.difficulty,
      "created_at": self.created_at.isoformat() if self.created_at else None,
      "updated_at": self.updated_at.isoformat() if self.updated_at else None,
    }

  @classmethod
  def from_dict(cls, data: dict):
    """辞書からインスタンスを生成"""
    return cls(
      id=data.get("id"),
      title=data["title"],
      description=data.get("description", ""),
      ingredients=data.get("ingredients", []),
      steps=data.get("steps", []),
      tags=data.get("tags", []),
      source_url=data.get("source_url"),
      image_path=data.get("image_path"),
      cooking_time=data.get("cooking_time"),
      servings=data.get("servings"),
      difficulty=data.get("difficulty"),
      created_at=data.get("created_at"),
      updated_at=data.get("updated_at"),
    )
'''

  filepath = os.path.join(BASE_DIR, "backend", "models", "recipe.py")
  write_file(filepath, content)


def create_recipe_repository():
  """Recipe Repository を作成"""
  content = '''"""
Recipe Repository
レシピデータのデータアクセス層（SQLite）
"""

import sqlite3
import json
from typing import List, Optional
from datetime import datetime

from backend.models.recipe import Recipe


class RecipeRepository:
  """レシピリポジトリ（SQLite）"""

  def __init__(self, db_path: str = None):
    """初期化"""
    if db_path is None:
      import os
      base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
      db_path = os.path.join(base_dir, "data", "recipes.db")

    self.db_path = db_path
    self._init_db()

  def _init_db(self):
    """DB 初期化"""
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute("""
      CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        ingredients TEXT,
        steps TEXT,
        tags TEXT,
        source_url TEXT,
        image_path TEXT,
        cooking_time INTEGER,
        servings INTEGER,
        difficulty TEXT,
        created_at TEXT,
        updated_at TEXT
      )
    """)

    conn.commit()
    conn.close()

  def _get_connection(self):
    """DB 接続を取得"""
    return sqlite3.connect(self.db_path)

  def create(self, recipe: Recipe) -> Recipe:
    """レシピを作成"""
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
      INSERT INTO recipes
      (title, description, ingredients, steps, tags, source_url, image_path,
       cooking_time, servings, difficulty, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
        recipe.title,
        recipe.description,
        json.dumps(recipe.ingredients, ensure_ascii=False),
        json.dumps(recipe.steps, ensure_ascii=False),
        json.dumps(recipe.tags, ensure_ascii=False),
        recipe.source_url,
        recipe.image_path,
        recipe.cooking_time,
        recipe.servings,
        recipe.difficulty,
        recipe.created_at.isoformat() if recipe.created_at else None,
        recipe.updated_at.isoformat() if recipe.updated_at else None,
      ),
    )

    recipe.id = cursor.lastrowid
    conn.commit()
    conn.close()

    return recipe

  def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
    """ID でレシピを取得"""
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
      return self._row_to_recipe(row)
    return None

  def get_all(self, limit: int = 100, offset: int = 0, order_by: str = "created_at") -> List[Recipe]:
    """全レシピを取得"""
    conn = self._get_connection()
    cursor = conn.cursor()

    query = f"SELECT * FROM recipes ORDER BY {order_by} DESC LIMIT ? OFFSET ?"
    cursor.execute(query, (limit, offset))
    rows = cursor.fetchall()
    conn.close()

    return [self._row_to_recipe(row) for row in rows]

  def update(self, recipe: Recipe) -> Recipe:
    """レシピを更新"""
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
      UPDATE recipes SET
        title = ?, description = ?, ingredients = ?, steps = ?, tags = ?,
        source_url = ?, image_path = ?, cooking_time = ?, servings = ?,
        difficulty = ?, updated_at = ?
      WHERE id = ?
    """,
      (
        recipe.title,
        recipe.description,
        json.dumps(recipe.ingredients, ensure_ascii=False),
        json.dumps(recipe.steps, ensure_ascii=False),
        json.dumps(recipe.tags, ensure_ascii=False),
        recipe.source_url,
        recipe.image_path,
        recipe.cooking_time,
        recipe.servings,
        recipe.difficulty,
        datetime.now().isoformat(),
        recipe.id,
      ),
    )

    conn.commit()
    conn.close()

    return recipe

  def delete(self, recipe_id: int) -> bool:
    """レシピを削除"""
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted

  def search(
    self,
    keyword: Optional[str] = None,
    tags: Optional[List[str]] = None,
    ingredients: Optional[List[str]] = None,
    limit: int = 100,
    offset: int = 0,
  ) -> List[Recipe]:
    """レシピを検索"""
    conn = self._get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM recipes WHERE 1=1"
    params = []

    if keyword:
      query += " AND (title LIKE ? OR description LIKE ?)"
      params.extend([f"%{keyword}%", f"%{keyword}%"])

    if tags:
      for tag in tags:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")

    if ingredients:
      for ingredient in ingredients:
        query += " AND ingredients LIKE ?"
        params.append(f"%{ingredient}%")

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [self._row_to_recipe(row) for row in rows]

  def get_by_tag(self, tag: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
    """タグでレシピを取得"""
    return self.search(tags=[tag], limit=limit, offset=offset)

  def get_all_tags(self) -> List[str]:
    """全タグを取得"""
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT tags FROM recipes WHERE tags IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    all_tags = set()
    for row in rows:
      try:
        tags = json.loads(row[0])
        all_tags.update(tags)
      except:
        pass

    return sorted(list(all_tags))

  def count(self) -> int:
    """レシピ総数を取得"""
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]
    conn.close()

    return count

  def _row_to_recipe(self, row) -> Recipe:
    """DB 行を Recipe オブジェクトに変換"""
    return Recipe(
      id=row[0],
      title=row[1],
      description=row[2] or "",
      ingredients=json.loads(row[3]) if row[3] else [],
      steps=json.loads(row[4]) if row[4] else [],
      tags=json.loads(row[5]) if row[5] else [],
      source_url=row[6],
      image_path=row[7],
      cooking_time=row[8],
      servings=row[9],
      difficulty=row[10],
      created_at=datetime.fromisoformat(row[11]) if row[11] else None,
      updated_at=datetime.fromisoformat(row[12]) if row[12] else None,
    )
'''

  filepath = os.path.join(BASE_DIR, "backend", "repositories", "recipe_repository.py")
  write_file(filepath, content)


def create_parsers():
  """Parser クラスを作成"""
  # Web Parser
  web_parser_content = '''"""
Web Recipe Parser
Web ページからレシピを抽出
"""

from typing import Dict, Any


class WebRecipeParser:
  """Web レシピパーサー"""

  def parse(self, url: str) -> Dict[str, Any]:
    """
    URL からレシピを解析

    Args:
        url: レシピページの URL

    Returns:
        Dict[str, Any]: レシピデータ
    """
    # TODO: 実装（Browser MCP / Puppeteer MCP を使用）
    raise NotImplementedError("Web パーサーは未実装です")
'''

  ocr_parser_content = '''"""
OCR Recipe Parser
画像からレシピを抽出
"""

from typing import Dict, Any


class OCRRecipeParser:
  """OCR レシピパーサー"""

  def parse(self, image_path: str) -> Dict[str, Any]:
    """
    画像からレシピを解析

    Args:
        image_path: 画像ファイルパス

    Returns:
        Dict[str, Any]: レシピデータ
    """
    # TODO: 実装（OCR ライブラリを使用）
    raise NotImplementedError("OCR パーサーは未実装です")
'''

  write_file(os.path.join(BASE_DIR, "backend", "parsers", "web_parser.py"), web_parser_content)
  write_file(os.path.join(BASE_DIR, "backend", "parsers", "ocr_parser.py"), ocr_parser_content)


def create_init_files():
  """__init__.py ファイルを作成"""
  backend_init = '''"""
Personal Recipe Intelligence - Backend Package
"""

__version__ = "0.1.0"
'''

  models_init = '''"""
Models パッケージ
"""

from backend.models.recipe import Recipe

__all__ = ["Recipe"]
'''

  repositories_init = '''"""
Repositories パッケージ
"""

from backend.repositories.recipe_repository import RecipeRepository

__all__ = ["RecipeRepository"]
'''

  services_init = '''"""
Services パッケージ
"""

from backend.services.recipe_service import RecipeService

__all__ = ["RecipeService"]
'''

  parsers_init = '''"""
Parsers パッケージ
"""

from backend.parsers.web_parser import WebRecipeParser
from backend.parsers.ocr_parser import OCRRecipeParser

__all__ = ["WebRecipeParser", "OCRRecipeParser"]
'''

  write_file(os.path.join(BASE_DIR, "backend", "__init__.py"), backend_init)
  write_file(os.path.join(BASE_DIR, "backend", "models", "__init__.py"), models_init)
  write_file(os.path.join(BASE_DIR, "backend", "repositories", "__init__.py"), repositories_init)
  write_file(os.path.join(BASE_DIR, "backend", "services", "__init__.py"), services_init)
  write_file(os.path.join(BASE_DIR, "backend", "parsers", "__init__.py"), parsers_init)


def main():
  """メイン処理"""
  print("=" * 100)
  print("Backend 完全初期化")
  print("=" * 100)

  # ディレクトリ構造作成
  init_backend_structure()

  # モデル作成
  print("\n2. モデル作成")
  print("-" * 80)
  create_recipe_model()

  # リポジトリ作成
  print("\n3. リポジトリ作成")
  print("-" * 80)
  create_recipe_repository()

  # パーサー作成
  print("\n4. パーサー作成")
  print("-" * 80)
  create_parsers()

  # __init__.py 作成
  print("\n5. __init__.py 作成")
  print("-" * 80)
  create_init_files()

  print("\n" + "=" * 100)
  print("初期化完了")
  print("=" * 100)
  print("\n次のステップ: merge_recipe_services.py を実行")


if __name__ == "__main__":
  main()

"""
Recipe Repository

SQLite データベースを使用したレシピの永続化層
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from pathlib import Path


class RecipeRepository:
    """レシピデータのリポジトリクラス"""

    def __init__(self, db_path: str = "data/recipes.db"):
        """
        初期化

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_db()

    def _ensure_db_directory(self):
        """データベースディレクトリが存在することを確認"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_db(self):
        """データベーステーブルを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT,
                    ingredients_json TEXT,
                    steps_json TEXT,
                    tags TEXT,
                    cook_time INTEGER,
                    servings INTEGER,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def create(self, recipe: Dict[str, Any]) -> int:
        """
        レシピを作成

        Args:
            recipe: レシピデータ

        Returns:
            作成されたレシピのID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO recipes (title, url, ingredients_json, steps_json, tags, cook_time, servings, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    recipe.get("title", ""),
                    recipe.get("url", ""),
                    json.dumps(recipe.get("ingredients", []), ensure_ascii=False),
                    json.dumps(recipe.get("steps", []), ensure_ascii=False),
                    ",".join(recipe.get("tags", [])),
                    recipe.get("cook_time"),
                    recipe.get("servings"),
                    recipe.get("source", "manual"),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        IDでレシピを取得

        Args:
            recipe_id: レシピID

        Returns:
            レシピデータまたはNone
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        レシピ一覧を取得

        Args:
            limit: 取得件数
            offset: オフセット
            search: 検索文字列
            tags: タグフィルター

        Returns:
            レシピリスト
        """
        query = "SELECT * FROM recipes WHERE 1=1"
        params = []

        if search:
            query += " AND (title LIKE ? OR ingredients_json LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def update(self, recipe_id: int, recipe: Dict[str, Any]) -> bool:
        """
        レシピを更新

        Args:
            recipe_id: レシピID
            recipe: 更新データ

        Returns:
            更新成功かどうか
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE recipes SET
                    title = ?,
                    url = ?,
                    ingredients_json = ?,
                    steps_json = ?,
                    tags = ?,
                    cook_time = ?,
                    servings = ?,
                    source = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (
                    recipe.get("title", ""),
                    recipe.get("url", ""),
                    json.dumps(recipe.get("ingredients", []), ensure_ascii=False),
                    json.dumps(recipe.get("steps", []), ensure_ascii=False),
                    ",".join(recipe.get("tags", [])),
                    recipe.get("cook_time"),
                    recipe.get("servings"),
                    recipe.get("source", "manual"),
                    recipe_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, recipe_id: int) -> bool:
        """
        レシピを削除

        Args:
            recipe_id: レシピID

        Returns:
            削除成功かどうか
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM recipes WHERE id = ?", (recipe_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """SQLite行を辞書に変換"""
        data = dict(row)
        if data.get("ingredients_json"):
            data["ingredients"] = json.loads(data["ingredients_json"])
            del data["ingredients_json"]
        if data.get("steps_json"):
            data["steps"] = json.loads(data["steps_json"])
            del data["steps_json"]
        if data.get("tags"):
            data["tags"] = data["tags"].split(",") if data["tags"] else []
        return data

    def count(self, search: Optional[str] = None, tags: Optional[List[str]] = None) -> int:
        """
        レシピ数をカウント

        Args:
            search: 検索文字列
            tags: タグフィルター

        Returns:
            レシピ数
        """
        query = "SELECT COUNT(*) FROM recipes WHERE 1=1"
        params = []

        if search:
            query += " AND (title LIKE ? OR ingredients_json LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]

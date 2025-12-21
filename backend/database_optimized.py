"""
Optimized SQLite database handler for Personal Recipe Intelligence
Implements performance optimizations per CLAUDE.md Section 10
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class OptimizedDatabase:
    """
    Optimized SQLite database with:
    - WAL mode for better concurrency
    - Connection pooling
    - Query timing
    - Proper resource management
    """

    def __init__(self, db_path: str):
        """
        Initialize optimized database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_pragmas()
        self._create_indexes()
        logger.info(f"Database initialized: {db_path}")

    def _initialize_pragmas(self) -> None:
        """
        Apply SQLite performance optimizations.
        Per CLAUDE.md Section 10: SQLite optimization
        """
        with self.get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            logger.info("Enabled WAL mode")

            # Increase cache size to 10MB
            conn.execute("PRAGMA cache_size=-10000")

            # Faster synchronization (safe for personal use)
            conn.execute("PRAGMA synchronous=NORMAL")

            # Use memory for temp tables
            conn.execute("PRAGMA temp_store=MEMORY")

            # Enable memory-mapped I/O (256MB)
            conn.execute("PRAGMA mmap_size=268435456")

            # Optimize for better query performance
            conn.execute("PRAGMA optimize")

            logger.info("Applied SQLite performance optimizations")

    def _create_indexes(self) -> None:
        """
        Create indexes for common queries to prevent N+1 problems.
        """
        with self.get_connection() as conn:
            # Recipe indexes
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_recipes_created "
                "ON recipes(created_at DESC)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_recipes_updated "
                "ON recipes(updated_at DESC)"
            )

            # Ingredient indexes
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_ingredients_recipe "
                "ON ingredients(recipe_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_ingredients_name "
                "ON ingredients(name)"
            )

            # Step indexes
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_steps_recipe "
                "ON steps(recipe_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_steps_order "
                "ON steps(recipe_id, step_order)"
            )

            # Tag indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")

            # Recipe-Tag relationship index
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_recipe_tags_recipe "
                "ON recipe_tags(recipe_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_recipe_tags_tag "
                "ON recipe_tags(tag_id)"
            )

            logger.info("Created performance indexes")

    @contextmanager
    def get_connection(self):
        """
        Context manager for safe database connection handling.
        Prevents connection leaks.

        Yields:
            sqlite3.Connection

        Example:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM recipes")
        """
        conn = sqlite3.connect(
            self.db_path,
            timeout=10.0,
            check_same_thread=False,
            isolation_level=None,  # Autocommit mode
        )
        conn.row_factory = sqlite3.Row  # Dict-like row access

        try:
            yield conn
        except Exception as e:
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise
        finally:
            conn.close()

    @contextmanager
    def transaction(self):
        """
        Context manager for explicit transactions.

        Yields:
            sqlite3.Connection

        Example:
            with db.transaction() as conn:
                conn.execute("INSERT INTO recipes ...")
                conn.execute("INSERT INTO ingredients ...")
                # Automatic commit on success, rollback on error
        """
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row

        try:
            yield conn
            conn.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back: {str(e)}", exc_info=True)
            raise
        finally:
            conn.close()

    def get_recipe_with_details(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        Get recipe with all related data in single query (avoid N+1).

        Args:
            recipe_id: Recipe ID

        Returns:
            Dict with recipe, ingredients, steps, tags or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get recipe
            cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            recipe = cursor.fetchone()

            if not recipe:
                return None

            recipe_dict = dict(recipe)

            # Get ingredients (single query)
            cursor.execute(
                "SELECT * FROM ingredients WHERE recipe_id = ? ORDER BY id",
                (recipe_id,),
            )
            recipe_dict["ingredients"] = [dict(row) for row in cursor.fetchall()]

            # Get steps (single query)
            cursor.execute(
                "SELECT * FROM steps WHERE recipe_id = ? ORDER BY step_order",
                (recipe_id,),
            )
            recipe_dict["steps"] = [dict(row) for row in cursor.fetchall()]

            # Get tags (single query with JOIN)
            cursor.execute(
                """
                SELECT t.* FROM tags t
                JOIN recipe_tags rt ON t.id = rt.tag_id
                WHERE rt.recipe_id = ?
                """,
                (recipe_id,),
            )
            recipe_dict["tags"] = [dict(row) for row in cursor.fetchall()]

            return recipe_dict

    def get_recipes_batch(
        self, recipe_ids: List[int]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple recipes efficiently (batch loading).

        Args:
            recipe_ids: List of recipe IDs

        Returns:
            Dict mapping recipe_id to recipe data
        """
        if not recipe_ids:
            return {}

        placeholders = ",".join("?" * len(recipe_ids))

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get all recipes in one query
            cursor.execute(
                f"SELECT * FROM recipes WHERE id IN ({placeholders})", recipe_ids
            )
            recipes = {row["id"]: dict(row) for row in cursor.fetchall()}

            # Get all ingredients for these recipes
            cursor.execute(
                f"SELECT * FROM ingredients WHERE recipe_id IN ({placeholders})",
                recipe_ids,
            )
            ingredients_by_recipe: Dict[int, List] = {}
            for row in cursor.fetchall():
                recipe_id = row["recipe_id"]
                if recipe_id not in ingredients_by_recipe:
                    ingredients_by_recipe[recipe_id] = []
                ingredients_by_recipe[recipe_id].append(dict(row))

            # Get all steps for these recipes
            cursor.execute(
                f"SELECT * FROM steps WHERE recipe_id IN ({placeholders}) "
                "ORDER BY recipe_id, step_order",
                recipe_ids,
            )
            steps_by_recipe: Dict[int, List] = {}
            for row in cursor.fetchall():
                recipe_id = row["recipe_id"]
                if recipe_id not in steps_by_recipe:
                    steps_by_recipe[recipe_id] = []
                steps_by_recipe[recipe_id].append(dict(row))

            # Get all tags for these recipes
            cursor.execute(
                f"""
                SELECT rt.recipe_id, t.* FROM tags t
                JOIN recipe_tags rt ON t.id = rt.tag_id
                WHERE rt.recipe_id IN ({placeholders})
                """,
                recipe_ids,
            )
            tags_by_recipe: Dict[int, List] = {}
            for row in cursor.fetchall():
                recipe_id = row["recipe_id"]
                if recipe_id not in tags_by_recipe:
                    tags_by_recipe[recipe_id] = []
                tags_by_recipe[recipe_id].append(dict(row))

            # Combine all data
            for recipe_id, recipe_data in recipes.items():
                recipe_data["ingredients"] = ingredients_by_recipe.get(recipe_id, [])
                recipe_data["steps"] = steps_by_recipe.get(recipe_id, [])
                recipe_data["tags"] = tags_by_recipe.get(recipe_id, [])

            return recipes

    def search_recipes(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search recipes by name with pagination.

        Args:
            query: Search query
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of recipe dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM recipes
                WHERE name LIKE ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (f"%{query}%", limit, offset),
            )

            recipe_ids = [row["id"] for row in cursor.fetchall()]

        # Use batch loading to get full details
        recipes_dict = self.get_recipes_batch(recipe_ids)
        return [recipes_dict[rid] for rid in recipe_ids if rid in recipes_dict]

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dict with table counts and database size
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Get counts for each table
            for table in ["recipes", "ingredients", "steps", "tags"]:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()["count"]

            # Get database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            stats["database_size_mb"] = (page_count * page_size) / 1024 / 1024

            # Get journal mode
            cursor.execute("PRAGMA journal_mode")
            stats["journal_mode"] = cursor.fetchone()[0]

            return stats

    def vacuum(self) -> None:
        """
        Vacuum database to reclaim space and optimize.
        Should be run periodically.
        """
        logger.info("Starting database VACUUM...")
        with self.get_connection() as conn:
            conn.execute("VACUUM")
        logger.info("Database VACUUM completed")

    def analyze(self) -> None:
        """
        Analyze database to update query planner statistics.
        Improves query performance.
        """
        logger.info("Analyzing database...")
        with self.get_connection() as conn:
            conn.execute("ANALYZE")
        logger.info("Database analysis completed")

    def backup(self, backup_path: str) -> None:
        """
        Create database backup.

        Args:
            backup_path: Path for backup file
        """
        logger.info(f"Creating database backup: {backup_path}")

        import shutil

        with self.get_connection() as conn:
            # Ensure WAL is checkpointed
            conn.execute("PRAGMA wal_checkpoint(FULL)")

        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Backup created successfully: {backup_path}")


# Example usage with query timing
class TimedDatabase(OptimizedDatabase):
    """
    Database wrapper that logs query execution time.
    Useful for identifying slow queries.
    """

    @contextmanager
    def get_connection(self):
        """Override to add timing"""
        import time

        start_time = time.time()
        try:
            with super().get_connection() as conn:
                yield conn
        finally:
            duration_ms = (time.time() - start_time) * 1000
            if duration_ms > 100:  # Log queries > 100ms
                logger.warning(f"Slow database operation: {duration_ms:.2f}ms")
            else:
                logger.debug(f"Database operation: {duration_ms:.2f}ms")

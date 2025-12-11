"""Check database indexes and their usage.

This script verifies that indexes are properly created and
provides statistics about their usage.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict


def get_db_path() -> Path:
    """Get database file path."""
    return Path(__file__).parent / "data" / "recipes.db"


def check_indexes(db_path: Path) -> List[Dict[str, str]]:
    """Check all indexes in the database.

    Args:
        db_path: Path to SQLite database

    Returns:
        List of index information dictionaries
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all indexes
    cursor.execute(
        """
        SELECT
            name,
            tbl_name,
            sql
        FROM sqlite_master
        WHERE type = 'index'
        ORDER BY tbl_name, name
    """
    )

    indexes = []
    for row in cursor.fetchall():
        indexes.append(
            {
                "name": row[0],
                "table": row[1],
                "sql": row[2] if row[2] else "AUTO (PRIMARY KEY or UNIQUE)",
            }
        )

    conn.close()
    return indexes


def get_table_info(db_path: Path, table_name: str) -> List[Dict[str, str]]:
    """Get column information for a table.

    Args:
        db_path: Path to SQLite database
        table_name: Name of table

    Returns:
        List of column information dictionaries
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")

    columns = []
    for row in cursor.fetchall():
        columns.append(
            {
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": row[3],
                "default": row[4],
                "pk": row[5],
            }
        )

    conn.close()
    return columns


def analyze_query_plan(db_path: Path, query: str) -> List[str]:
    """Analyze query execution plan.

    Args:
        db_path: Path to SQLite database
        query: SQL query to analyze

    Returns:
        List of execution plan steps
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"EXPLAIN QUERY PLAN {query}")

    plan = []
    for row in cursor.fetchall():
        plan.append(" | ".join(str(x) for x in row))

    conn.close()
    return plan


def main():
    """Main function to check database indexes."""
    db_path = get_db_path()

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        print("Please run migrations first using: ./migrate.sh")
        return

    print("=" * 80)
    print("DATABASE INDEX ANALYSIS")
    print("=" * 80)
    print(f"Database: {db_path}")
    print()

    # Check all indexes
    print("-" * 80)
    print("EXISTING INDEXES")
    print("-" * 80)

    indexes = check_indexes(db_path)

    if not indexes:
        print("No indexes found in database!")
        return

    for idx in indexes:
        print(f"\nIndex: {idx['name']}")
        print(f"  Table: {idx['table']}")
        print(f"  SQL: {idx['sql']}")

    print()
    print(f"Total indexes: {len(indexes)}")

    # Check specific tables
    print()
    print("-" * 80)
    print("TABLE STRUCTURES")
    print("-" * 80)

    for table in ["recipe", "ingredient", "tag", "step"]:
        print(f"\nTable: {table}")
        columns = get_table_info(db_path, table)
        for col in columns:
            pk_marker = " [PK]" if col["pk"] else ""
            nn_marker = " NOT NULL" if col["notnull"] else ""
            print(f"  {col['name']}: {col['type']}{pk_marker}{nn_marker}")

    # Test query plans
    print()
    print("-" * 80)
    print("QUERY EXECUTION PLANS")
    print("-" * 80)

    test_queries = [
        ("Title search", "SELECT * FROM recipe WHERE title LIKE '%test%'"),
        ("Created_at sort", "SELECT * FROM recipe ORDER BY created_at DESC LIMIT 10"),
        (
            "Ingredient name search",
            "SELECT * FROM ingredient WHERE name LIKE '%onion%'",
        ),
        (
            "Normalized search",
            "SELECT * FROM ingredient WHERE name_normalized = 'onion'",
        ),
        ("Tag lookup", "SELECT * FROM tag WHERE name = 'japanese'"),
        (
            "Composite query",
            "SELECT * FROM recipe WHERE created_at > '2025-01-01' ORDER BY created_at, title",
        ),
    ]

    for name, query in test_queries:
        print(f"\n{name}:")
        print(f"  Query: {query}")
        print("  Plan:")
        plan = analyze_query_plan(db_path, query)
        for step in plan:
            print(f"    {step}")

    print()
    print("=" * 80)
    print("INDEX CHECK COMPLETE")
    print("=" * 80)

    # Summary
    print("\nIndex Summary:")
    index_by_table = {}
    for idx in indexes:
        table = idx["table"]
        if table not in index_by_table:
            index_by_table[table] = []
        index_by_table[table].append(idx["name"])

    for table, idx_list in sorted(index_by_table.items()):
        print(f"  {table}: {len(idx_list)} indexes")
        for idx_name in idx_list:
            print(f"    - {idx_name}")


if __name__ == "__main__":
    main()

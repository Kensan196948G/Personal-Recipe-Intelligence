#!/usr/bin/env python3
"""
Performance audit script for Personal Recipe Intelligence
Scans codebase for common performance anti-patterns

Run: python scripts/performance_audit.py
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


class PerformanceAuditor:
    """Audit codebase for performance issues"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.backend_path = self.base_path / "backend"
        self.issues: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)

    def audit_all(self) -> Dict[str, List]:
        """Run all audits"""
        print("=" * 70)
        print("PERFORMANCE AUDIT - Personal Recipe Intelligence")
        print("=" * 70)

        self.audit_async_blocking()
        self.audit_database_queries()
        self.audit_resource_leaks()
        self.audit_file_operations()
        self.audit_imports()

        return self.issues

    def audit_async_blocking(self) -> None:
        """Check for blocking operations in async code"""
        print("\n[1] Auditing async/await patterns...")

        if not self.backend_path.exists():
            print(f"  ⚠ Backend path not found: {self.backend_path}")
            return

        for py_file in self.backend_path.rglob("*.py"):
            with open(py_file, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                # Skip if no async code
                if "async def" not in content:
                    continue

                for i, line in enumerate(lines, 1):
                    # Check for blocking HTTP requests
                    if "import requests" in line:
                        self.issues["async_blocking"].append(
                            (str(py_file), i, "Using blocking 'requests' module")
                        )

                    # Check for time.sleep in async context
                    if re.search(r"(?<!await\s)time\.sleep\s*\(", line):
                        self.issues["async_blocking"].append(
                            (str(py_file), i, "Using blocking time.sleep()")
                        )

                    # Check for sync file operations
                    if (
                        re.search(r"(?<!await\s)open\s*\(", line)
                        and "aiofiles" not in content
                        and "async def" in content[:content.index(line) + len(line)]
                    ):
                        self.issues["async_blocking"].append(
                            (str(py_file), i, "Blocking file operation in async code")
                        )

                    # Check for sync JSON operations
                    if "json.load(" in line or "json.dump(" in line:
                        self.issues["async_blocking"].append(
                            (
                                str(py_file),
                                i,
                                "Blocking JSON operation (consider async)",
                            )
                        )

        count = len(self.issues["async_blocking"])
        if count == 0:
            print("  ✓ No blocking operations in async code")
        else:
            print(f"  ⚠ Found {count} potential blocking operations")

    def audit_database_queries(self) -> None:
        """Check for N+1 query patterns"""
        print("\n[2] Auditing database query patterns...")

        if not self.backend_path.exists():
            print(f"  ⚠ Backend path not found: {self.backend_path}")
            return

        for py_file in self.backend_path.rglob("*.py"):
            with open(py_file, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                in_loop = False
                loop_line = 0

                for i, line in enumerate(lines, 1):
                    # Detect loop start
                    if re.search(r"for\s+\w+\s+in\s+", line):
                        in_loop = True
                        loop_line = i

                    # Detect query in loop (potential N+1)
                    if in_loop and re.search(
                        r"\.(query|filter|get|execute)\s*\(", line
                    ):
                        self.issues["n_plus_one"].append(
                            (
                                str(py_file),
                                i,
                                f"Query inside loop (started at line {loop_line})",
                            )
                        )

                    # Reset on function/class definition or unindented line
                    if (
                        line.strip()
                        and not line[0].isspace()
                        or re.search(r"^\s*(def|class|async def)\s+", line)
                    ):
                        in_loop = False

                # Check for missing eager loading
                if ".query(" in content and "joinedload" not in content:
                    if ".all()" in content or ".filter(" in content:
                        self.issues["missing_eager_load"].append(
                            (
                                str(py_file),
                                0,
                                "Using query() without joinedload (potential N+1)",
                            )
                        )

        n1_count = len(self.issues["n_plus_one"])
        eager_count = len(self.issues["missing_eager_load"])

        if n1_count == 0 and eager_count == 0:
            print("  ✓ No obvious N+1 query patterns")
        else:
            print(f"  ⚠ Found {n1_count} potential N+1 queries")
            print(f"  ⚠ Found {eager_count} queries without eager loading")

    def audit_resource_leaks(self) -> None:
        """Check for resource management issues"""
        print("\n[3] Auditing resource management...")

        if not self.backend_path.exists():
            print(f"  ⚠ Backend path not found: {self.backend_path}")
            return

        for py_file in self.backend_path.rglob("*.py"):
            with open(py_file, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    # File operations without context manager
                    if re.search(r"\w+\s*=\s*open\s*\(", line) and "with" not in line:
                        self.issues["resource_leak"].append(
                            (str(py_file), i, "File opened without context manager")
                        )

                    # Database connections without context manager
                    if (
                        re.search(r"\w+\s*=\s*.*\.connect\s*\(", line)
                        and "with" not in line
                    ):
                        self.issues["resource_leak"].append(
                            (
                                str(py_file),
                                i,
                                "Database connection without context manager",
                            )
                        )

                    # Image operations without context manager
                    if (
                        re.search(r"\w+\s*=\s*Image\.open\s*\(", line)
                        and "with" not in line
                    ):
                        self.issues["resource_leak"].append(
                            (str(py_file), i, "Image opened without context manager")
                        )

        count = len(self.issues["resource_leak"])
        if count == 0:
            print("  ✓ No obvious resource leaks")
        else:
            print(f"  ⚠ Found {count} potential resource leaks")

    def audit_file_operations(self) -> None:
        """Check for inefficient file operations"""
        print("\n[4] Auditing file I/O operations...")

        if not self.backend_path.exists():
            print(f"  ⚠ Backend path not found: {self.backend_path}")
            return

        for py_file in self.backend_path.rglob("*.py"):
            with open(py_file, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    # Large file reads
                    if ".readlines()" in line or ".read()" in line:
                        # Check if in a loop (inefficient)
                        recent_lines = lines[max(0, i - 10) : i]
                        if any(
                            re.search(r"for\s+\w+\s+in\s+", recent_line)
                            for recent_line in recent_lines
                        ):
                            self.issues["inefficient_io"].append(
                                (
                                    str(py_file),
                                    i,
                                    "File read operation in loop (inefficient)",
                                )
                            )

                    # Multiple file opens in loop
                    if "for " in content:
                        loop_sections = content.split("for ")
                        for section in loop_sections[1:]:
                            if section.count("open(") > 1:
                                self.issues["inefficient_io"].append(
                                    (
                                        str(py_file),
                                        0,
                                        "Multiple file opens in loop",
                                    )
                                )
                                break

        count = len(self.issues["inefficient_io"])
        if count == 0:
            print("  ✓ No obviously inefficient file I/O")
        else:
            print(f"  ⚠ Found {count} potentially inefficient file operations")

    def audit_imports(self) -> None:
        """Check for suboptimal library choices"""
        print("\n[5] Auditing library imports...")

        if not self.backend_path.exists():
            print(f"  ⚠ Backend path not found: {self.backend_path}")
            return

        for py_file in self.backend_path.rglob("*.py"):
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

                # Check for sync requests in async project
                if "import requests" in content and "async def" in content:
                    self.issues["suboptimal_imports"].append(
                        (
                            str(py_file),
                            0,
                            "Using 'requests' in async code (use aiohttp)",
                        )
                    )

                # Check for missing aiofiles
                if "async def" in content and "open(" in content:
                    if "import aiofiles" not in content:
                        self.issues["suboptimal_imports"].append(
                            (
                                str(py_file),
                                0,
                                "Missing 'aiofiles' for async file operations",
                            )
                        )

        count = len(self.issues["suboptimal_imports"])
        if count == 0:
            print("  ✓ No suboptimal library choices")
        else:
            print(f"  ⚠ Found {count} suboptimal library choices")

    def print_detailed_report(self) -> None:
        """Print detailed issue report"""
        print("\n" + "=" * 70)
        print("DETAILED ISSUE REPORT")
        print("=" * 70)

        categories = {
            "async_blocking": "Blocking Operations in Async Code",
            "n_plus_one": "Potential N+1 Query Problems",
            "missing_eager_load": "Missing Eager Loading",
            "resource_leak": "Resource Leak Risks",
            "inefficient_io": "Inefficient File I/O",
            "suboptimal_imports": "Suboptimal Library Imports",
        }

        total_issues = 0

        for category, title in categories.items():
            issues = self.issues[category]
            if not issues:
                continue

            print(f"\n{title}:")
            print("-" * 70)

            for file_path, line_num, description in issues:
                if line_num > 0:
                    print(f"  {file_path}:{line_num}")
                else:
                    print(f"  {file_path}")
                print(f"    → {description}")
                total_issues += 1

        print("\n" + "=" * 70)
        print(f"TOTAL ISSUES FOUND: {total_issues}")
        print("=" * 70)

        if total_issues == 0:
            print("\n✓ No performance issues detected!")
        else:
            print("\n⚠ Review and fix issues for optimal performance")
            print("  Target: API response time < 200ms (per CLAUDE.md)")

    def generate_recommendations(self) -> None:
        """Generate actionable recommendations"""
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)

        if self.issues["async_blocking"]:
            print("\n[1] Fix Blocking Operations in Async Code:")
            print("  - Replace 'requests' with 'aiohttp'")
            print("  - Replace 'time.sleep()' with 'await asyncio.sleep()'")
            print("  - Use 'aiofiles' for file operations")
            print("  - Use thread pools for CPU-bound operations")

        if self.issues["n_plus_one"] or self.issues["missing_eager_load"]:
            print("\n[2] Optimize Database Queries:")
            print("  - Use joinedload() or selectinload() for relationships")
            print("  - Batch load related data instead of individual queries")
            print("  - Move queries outside loops where possible")

        if self.issues["resource_leak"]:
            print("\n[3] Fix Resource Management:")
            print("  - Always use 'with' statements for file/connection handling")
            print("  - Add try/finally blocks for cleanup")
            print("  - Use context managers for browser/MCP operations")

        if self.issues["inefficient_io"]:
            print("\n[4] Optimize File Operations:")
            print("  - Stream large files instead of loading entirely")
            print("  - Batch file operations to reduce open/close overhead")
            print("  - Use async file I/O where beneficial")

        print("\n[Priority Actions]:")
        print("  1. Run: python scripts/performance_audit.py > audit_report.txt")
        print("  2. Fix CRITICAL issues (blocking in async, N+1 queries)")
        print("  3. Add performance monitoring middleware")
        print("  4. Enable SQLite WAL mode and indexes")
        print("  5. Implement lightweight caching")


def main():
    """Main entry point"""
    auditor = PerformanceAuditor()
    auditor.audit_all()
    auditor.print_detailed_report()
    auditor.generate_recommendations()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test Needs Analyzer for Personal Recipe Intelligence
Scans the codebase and generates specific test recommendations
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

PROJECT_ROOT = Path("/mnt/Linux-ExHDD/Personal-Recipe-Intelligence")


class TestNeedsAnalyzer:
    """Analyzes codebase to identify specific testing needs"""

    def __init__(self):
        self.python_files: List[Path] = []
        self.js_files: List[Path] = []
        self.functions: Dict[str, List[str]] = defaultdict(list)
        self.classes: Dict[str, List[str]] = defaultdict(list)
        self.api_routes: List[Dict] = []
        self.test_files: Set[Path] = set()

    def scan_codebase(self):
        """Scan codebase for Python and JavaScript files"""
        print("Scanning codebase...")

        # Scan backend Python files
        backend_dir = PROJECT_ROOT / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                if (
                    "__pycache__" not in str(py_file)
                    and "test" not in py_file.name
                    and py_file.name != "__init__.py"
                ):
                    self.python_files.append(py_file)

        # Scan src Python files
        src_dir = PROJECT_ROOT / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                if (
                    "__pycache__" not in str(py_file)
                    and "test" not in py_file.name
                    and py_file.name != "__init__.py"
                ):
                    self.python_files.append(py_file)

        # Scan frontend JavaScript files
        frontend_dir = PROJECT_ROOT / "frontend" / "src"
        if frontend_dir.exists():
            for ext in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
                for js_file in frontend_dir.rglob(ext):
                    if "node_modules" not in str(js_file) and "test" not in js_file.name:
                        self.js_files.append(js_file)

        # Find existing test files
        for pattern in ["test_*.py", "*_test.py", "*.test.js", "*.test.ts"]:
            for test_file in PROJECT_ROOT.rglob(pattern):
                if "__pycache__" not in str(test_file):
                    self.test_files.add(test_file)

        print(f"Found {len(self.python_files)} Python files")
        print(f"Found {len(self.js_files)} JavaScript/TypeScript files")
        print(f"Found {len(self.test_files)} test files")

    def analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze a Python file to extract functions, classes, and routes"""
        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = file_path.relative_to(PROJECT_ROOT)

            analysis = {
                "file": str(rel_path),
                "functions": [],
                "classes": [],
                "routes": [],
                "imports": [],
                "complexity": "medium",
            }

            # Find functions
            functions = re.findall(r"^def (\w+)\(", content, re.MULTILINE)
            analysis["functions"] = [f for f in functions if not f.startswith("_")]

            # Find classes
            classes = re.findall(r"^class (\w+)", content, re.MULTILINE)
            analysis["classes"] = classes

            # Find API routes (FastAPI, Flask)
            routes = re.findall(
                r'@(?:app|router|api)\.(get|post|put|delete|patch)\(["\']([^"\']+)',
                content,
            )
            analysis["routes"] = [
                {"method": method.upper(), "path": path} for method, path in routes
            ]

            # Find imports
            imports = re.findall(r"^import (\w+)|^from ([\w.]+)", content, re.MULTILINE)
            analysis["imports"] = [i[0] or i[1] for i in imports]

            # Estimate complexity
            lines = len(content.splitlines())
            if lines > 200:
                analysis["complexity"] = "high"
            elif lines < 50:
                analysis["complexity"] = "low"

            return analysis

        except Exception as e:
            return {"file": str(file_path), "error": str(e)}

    def analyze_js_file(self, file_path: Path) -> Dict:
        """Analyze a JavaScript/TypeScript file"""
        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = file_path.relative_to(PROJECT_ROOT)

            analysis = {
                "file": str(rel_path),
                "functions": [],
                "components": [],
                "exports": [],
                "imports": [],
            }

            # Find function declarations
            functions = re.findall(
                r"(?:function|const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(", content
            )
            analysis["functions"] = functions

            # Find React components
            components = re.findall(r"(?:function|const)\s+(\w+)\s*=.*?(?:=>|{)", content)
            # Filter for PascalCase (likely components)
            analysis["components"] = [c for c in components if c[0].isupper()]

            # Find exports
            exports = re.findall(r"export\s+(?:default\s+)?(?:function|const|class)\s+(\w+)", content)
            analysis["exports"] = exports

            return analysis

        except Exception as e:
            return {"file": str(file_path), "error": str(e)}

    def generate_recommendations(self) -> str:
        """Generate specific test recommendations based on analysis"""
        report = []
        report.append("# SPECIFIC TEST RECOMMENDATIONS")
        report.append("# Based on Codebase Analysis\n")
        report.append(f"Project: Personal Recipe Intelligence")
        report.append(f"Date: 2025-12-11\n")

        # Summary
        report.append("\n## SUMMARY")
        report.append(f"\n- Python files analyzed: {len(self.python_files)}")
        report.append(f"- JavaScript files analyzed: {len(self.js_files)}")
        report.append(f"- Existing test files: {len(self.test_files)}")

        total_functions = 0
        total_classes = 0
        total_routes = 0

        # Analyze Python files
        python_analyses = []
        for py_file in self.python_files:
            analysis = self.analyze_python_file(py_file)
            if "error" not in analysis:
                python_analyses.append(analysis)
                total_functions += len(analysis.get("functions", []))
                total_classes += len(analysis.get("classes", []))
                total_routes += len(analysis.get("routes", []))

        report.append(f"- Total functions found: {total_functions}")
        report.append(f"- Total classes found: {total_classes}")
        report.append(f"- Total API routes found: {total_routes}")

        # Python file recommendations
        if python_analyses:
            report.append("\n\n## PYTHON FILES NEEDING TESTS\n")

            for analysis in sorted(python_analyses, key=lambda x: len(x.get("functions", [])), reverse=True):
                if "error" in analysis:
                    continue

                file_name = analysis["file"]
                functions = analysis.get("functions", [])
                classes = analysis.get("classes", [])
                routes = analysis.get("routes", [])
                complexity = analysis.get("complexity", "medium")

                if not functions and not classes and not routes:
                    continue

                report.append(f"\n### {file_name}")
                report.append(f"Complexity: {complexity.upper()}")

                if classes:
                    report.append(f"\nClasses ({len(classes)}):")
                    for cls in classes:
                        report.append(f"  - {cls}")
                        report.append(f"    → Recommended test: test_{cls.lower()}.py")

                if functions:
                    report.append(f"\nFunctions ({len(functions)}):")
                    for func in functions[:10]:  # Show first 10
                        report.append(f"  - {func}()")
                        report.append(f"    → Test: test_{func}()")
                    if len(functions) > 10:
                        report.append(f"  ... and {len(functions) - 10} more functions")

                if routes:
                    report.append(f"\nAPI Routes ({len(routes)}):")
                    for route in routes:
                        report.append(f"  - {route['method']} {route['path']}")
                        report.append(f"    → Test: test_{route['method'].lower()}_{route['path'].replace('/', '_')}()")

                # Generate test file recommendation
                test_file = self._recommend_test_file(file_name)
                report.append(f"\nRecommended test file: {test_file}")
                report.append(f"Priority: {self._calculate_priority(complexity, len(functions), len(classes), len(routes))}")

        # JavaScript file recommendations
        js_analyses = []
        for js_file in self.js_files:
            analysis = self.analyze_js_file(js_file)
            if "error" not in analysis:
                js_analyses.append(analysis)

        if js_analyses:
            report.append("\n\n## JAVASCRIPT/TYPESCRIPT FILES NEEDING TESTS\n")

            for analysis in js_analyses:
                if "error" in analysis:
                    continue

                file_name = analysis["file"]
                components = analysis.get("components", [])
                functions = analysis.get("functions", [])

                if not components and not functions:
                    continue

                report.append(f"\n### {file_name}")

                if components:
                    report.append(f"\nComponents ({len(components)}):")
                    for comp in components:
                        report.append(f"  - {comp}")
                        report.append(f"    → Test: {comp}.test.js")

                if functions:
                    report.append(f"\nFunctions ({len(functions)}):")
                    for func in functions[:5]:
                        report.append(f"  - {func}()")

                test_file = file_name.replace(".jsx", ".test.js").replace(".tsx", ".test.ts").replace(".js", ".test.js").replace(".ts", ".test.ts")
                report.append(f"\nRecommended test file: {test_file}")

        # Priority recommendations
        report.append("\n\n## PRIORITY TEST IMPLEMENTATION ORDER\n")

        priorities = self._generate_priority_list(python_analyses)

        report.append("\n### Phase 1: CRITICAL (Implement First)")
        for item in priorities["critical"]:
            report.append(f"  {item}")

        report.append("\n### Phase 2: HIGH (Implement Second)")
        for item in priorities["high"]:
            report.append(f"  {item}")

        report.append("\n### Phase 3: MEDIUM (Implement Third)")
        for item in priorities["medium"]:
            report.append(f"  {item}")

        # Test file templates
        report.append("\n\n## SUGGESTED TEST FILE STRUCTURE\n")

        if python_analyses:
            sample = python_analyses[0]
            test_file = self._recommend_test_file(sample["file"])
            report.append(f"\nExample test file: {test_file}")
            report.append("\n```python")
            report.append(self._generate_test_template(sample))
            report.append("```")

        return "\n".join(report)

    def _recommend_test_file(self, source_file: str) -> str:
        """Recommend test file path for a source file"""
        path = Path(source_file)

        if "backend" in str(path):
            test_name = f"test_{path.stem}.py"
            return f"backend/tests/{test_name}"
        elif "src" in str(path):
            test_name = f"test_{path.stem}.py"
            return f"tests/{test_name}"
        else:
            test_name = f"test_{path.stem}.py"
            return f"tests/{test_name}"

    def _calculate_priority(self, complexity: str, func_count: int, class_count: int, route_count: int) -> str:
        """Calculate test priority based on file characteristics"""
        score = 0

        # Routes are critical (API endpoints)
        if route_count > 0:
            score += 10

        # Database-related are critical
        # Parser-related are critical
        # (Would check file name/path here)

        # Complexity matters
        if complexity == "high":
            score += 5
        elif complexity == "medium":
            score += 2

        # Number of functions
        if func_count > 10:
            score += 3
        elif func_count > 5:
            score += 2

        # Classes typically need testing
        if class_count > 0:
            score += 3

        if score >= 10:
            return "CRITICAL"
        elif score >= 5:
            return "HIGH"
        else:
            return "MEDIUM"

    def _generate_priority_list(self, analyses: List[Dict]) -> Dict[str, List[str]]:
        """Generate prioritized list of files to test"""
        priorities = {"critical": [], "high": [], "medium": []}

        for analysis in analyses:
            file_name = analysis["file"]
            functions = analysis.get("functions", [])
            classes = analysis.get("classes", [])
            routes = analysis.get("routes", [])
            complexity = analysis.get("complexity", "medium")

            priority = self._calculate_priority(complexity, len(functions), len(classes), len(routes))
            test_file = self._recommend_test_file(file_name)

            item = f"- [ ] {file_name} → {test_file} ({len(functions)} functions, {len(classes)} classes, {len(routes)} routes)"

            if priority == "CRITICAL":
                priorities["critical"].append(item)
            elif priority == "HIGH":
                priorities["high"].append(item)
            else:
                priorities["medium"].append(item)

        return priorities

    def _generate_test_template(self, analysis: Dict) -> str:
        """Generate a test template for a file"""
        lines = []
        lines.append('"""')
        lines.append(f'Tests for {analysis["file"]}')
        lines.append('"""')
        lines.append("import pytest")
        lines.append("")

        # If there are classes
        if analysis.get("classes"):
            for cls in analysis["classes"][:1]:  # Just show first class
                lines.append(f"class Test{cls}:")
                lines.append(f'    """Test suite for {cls}"""')
                lines.append("")
                lines.append("    def test_initialization(self):")
                lines.append(f'        """Test {cls} can be instantiated"""')
                lines.append("        # TODO: Implement test")
                lines.append("        pass")
                lines.append("")

        # If there are functions
        if analysis.get("functions"):
            for func in analysis["functions"][:3]:  # Show first 3
                lines.append(f"def test_{func}():")
                lines.append(f'    """Test {func}() function"""')
                lines.append("    # TODO: Implement test")
                lines.append("    pass")
                lines.append("")

        return "\n".join(lines)


def main():
    """Main execution"""
    print("=" * 80)
    print("Personal Recipe Intelligence - Test Needs Analyzer")
    print("=" * 80)
    print()

    analyzer = TestNeedsAnalyzer()

    # Scan codebase
    analyzer.scan_codebase()
    print()

    # Generate recommendations
    print("Generating recommendations...")
    report = analyzer.generate_recommendations()

    # Save report
    output_file = PROJECT_ROOT / "TEST_NEEDS_ANALYSIS.txt"
    output_file.write_text(report, encoding="utf-8")

    print(f"\n✓ Report saved to: {output_file}")
    print()

    # Print report
    print("=" * 80)
    print(report)
    print("=" * 80)

    # Summary
    print("\n\nNEXT STEPS:")
    print("1. Review TEST_NEEDS_ANALYSIS.txt for specific recommendations")
    print("2. Follow TESTING_QUICK_START.md to set up test infrastructure")
    print("3. Use TEST_TEMPLATES.md for copy-paste test examples")
    print("4. Implement tests in priority order (Critical → High → Medium)")
    print()


if __name__ == "__main__":
    main()

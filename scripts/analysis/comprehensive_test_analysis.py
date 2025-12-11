#!/usr/bin/env python3
"""
Comprehensive Test Suite Analysis for Personal Recipe Intelligence
Generates detailed report on test coverage, gaps, and recommendations
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set
import re

PROJECT_ROOT = Path("/mnt/Linux-ExHDD/Personal-Recipe-Intelligence")

class TestAnalyzer:
    def __init__(self):
        self.test_files: List[Path] = []
        self.source_files: Dict[str, List[Path]] = {"backend": [], "frontend": []}
        self.test_coverage_map: Dict[str, List[str]] = {}
        self.untested_modules: List[Path] = []

    def find_test_files(self) -> List[Path]:
        """Find all test files in the project"""
        test_patterns = ["test_*.py", "*_test.py", "*.test.js", "*.test.ts"]
        found = []

        for pattern in test_patterns:
            if ".py" in pattern:
                found.extend(PROJECT_ROOT.rglob(pattern))
            else:
                found.extend(PROJECT_ROOT.rglob(pattern))

        self.test_files = [f for f in found if "__pycache__" not in str(f)]
        return self.test_files

    def find_source_files(self):
        """Find all source files that should have tests"""
        # Backend Python files
        backend_dir = PROJECT_ROOT / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                if "__pycache__" not in str(py_file) and "test" not in py_file.name:
                    self.source_files["backend"].append(py_file)

        # Frontend JS/TS files
        frontend_dir = PROJECT_ROOT / "frontend"
        if frontend_dir.exists():
            for ext in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
                for file in frontend_dir.rglob(ext):
                    if "node_modules" not in str(file) and "test" not in file.name:
                        self.source_files["frontend"].append(file)

    def analyze_test_content(self, test_file: Path) -> Dict:
        """Analyze test file content to extract test cases"""
        try:
            content = test_file.read_text(encoding='utf-8')

            analysis = {
                "file": str(test_file.relative_to(PROJECT_ROOT)),
                "test_functions": [],
                "imports": [],
                "mocks_used": False,
                "async_tests": False,
                "fixtures": []
            }

            # Python tests
            if test_file.suffix == ".py":
                analysis["test_functions"] = re.findall(r'def (test_\w+)', content)
                analysis["imports"] = re.findall(r'^import (\w+)|^from ([\w.]+)', content, re.MULTILINE)
                analysis["mocks_used"] = "mock" in content.lower() or "Mock" in content
                analysis["async_tests"] = "async def test" in content
                analysis["fixtures"] = re.findall(r'@pytest\.fixture', content)

            # JavaScript/TypeScript tests
            elif test_file.suffix in [".js", ".ts"]:
                analysis["test_functions"] = re.findall(r'(?:test|it)\(["\'](.+?)["\']', content)
                analysis["imports"] = re.findall(r'import .+ from ["\'](.+?)["\']', content)
                analysis["mocks_used"] = "mock" in content.lower() or "jest.mock" in content
                analysis["async_tests"] = "async" in content

            return analysis

        except Exception as e:
            return {"file": str(test_file), "error": str(e)}

    def identify_untested_modules(self):
        """Identify source files without corresponding tests"""
        tested_modules = set()

        # Extract module names from test files
        for test_file in self.test_files:
            # For test_module.py, the module is module.py
            name = test_file.stem
            if name.startswith("test_"):
                tested_modules.add(name[5:])
            elif name.endswith("_test"):
                tested_modules.add(name[:-5])
            elif ".test" in name:
                tested_modules.add(name.split(".test")[0])

        # Check which source files don't have tests
        for category, files in self.source_files.items():
            for source_file in files:
                module_name = source_file.stem
                if module_name not in tested_modules and module_name != "__init__":
                    self.untested_modules.append(source_file)

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        report = []
        report.append("# TEST SUITE ANALYSIS REPORT")
        report.append("# Personal Recipe Intelligence Project")
        report.append(f"# Generated: 2025-12-11\n")

        # 1. Test File Inventory
        report.append("\n## 1. TEST FILE INVENTORY")
        report.append(f"\nTotal test files found: {len(self.test_files)}\n")

        if self.test_files:
            report.append("### Test Files:")
            for tf in sorted(self.test_files):
                rel_path = tf.relative_to(PROJECT_ROOT)
                report.append(f"  - {rel_path}")
        else:
            report.append("  WARNING: No test files found!")

        # 2. Source File Inventory
        report.append("\n\n## 2. SOURCE FILE INVENTORY")
        report.append(f"\nBackend Python files: {len(self.source_files['backend'])}")
        report.append(f"Frontend JS/TS files: {len(self.source_files['frontend'])}")

        # 3. Test Content Analysis
        report.append("\n\n## 3. TEST CONTENT ANALYSIS\n")
        for test_file in self.test_files:
            analysis = self.analyze_test_content(test_file)
            report.append(f"\n### {analysis.get('file', 'Unknown')}")
            if "error" in analysis:
                report.append(f"  ERROR: {analysis['error']}")
            else:
                report.append(f"  Test functions: {len(analysis.get('test_functions', []))}")
                if analysis.get('test_functions'):
                    for func in analysis['test_functions'][:5]:  # Show first 5
                        report.append(f"    - {func}")
                    if len(analysis['test_functions']) > 5:
                        report.append(f"    ... and {len(analysis['test_functions']) - 5} more")
                report.append(f"  Uses mocks: {analysis.get('mocks_used', False)}")
                report.append(f"  Async tests: {analysis.get('async_tests', False)}")
                report.append(f"  Fixtures: {len(analysis.get('fixtures', []))}")

        # 4. Untested Modules
        report.append("\n\n## 4. UNTESTED MODULES")
        report.append(f"\nTotal untested modules: {len(self.untested_modules)}\n")

        if self.untested_modules:
            report.append("### Modules without tests:")
            for module in sorted(self.untested_modules):
                rel_path = module.relative_to(PROJECT_ROOT)
                report.append(f"  - {rel_path}")
        else:
            report.append("  All modules have corresponding tests!")

        # 5. Directory Structure
        report.append("\n\n## 5. DIRECTORY STRUCTURE ANALYSIS")

        tests_dir = PROJECT_ROOT / "tests"
        backend_tests = PROJECT_ROOT / "backend" / "tests"
        frontend_tests = PROJECT_ROOT / "frontend" / "tests"

        report.append(f"\n/tests/ exists: {tests_dir.exists()}")
        report.append(f"/backend/tests/ exists: {backend_tests.exists()}")
        report.append(f"/frontend/tests/ exists: {frontend_tests.exists()}")

        # 6. Recommendations
        report.append("\n\n## 6. RECOMMENDATIONS\n")

        recommendations = []

        if len(self.test_files) == 0:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Foundation",
                "title": "Create test infrastructure",
                "description": "No tests exist. Create tests/, backend/tests/, and frontend/tests/ directories"
            })

        if len(self.untested_modules) > 0:
            recommendations.append({
                "priority": "HIGH",
                "category": "Coverage",
                "title": f"Add tests for {len(self.untested_modules)} untested modules",
                "description": "Create unit tests for all untested source files"
            })

        if not (PROJECT_ROOT / "pytest.ini").exists():
            recommendations.append({
                "priority": "HIGH",
                "category": "Configuration",
                "title": "Create pytest.ini",
                "description": "Configure pytest with coverage settings"
            })

        # Check for common test types
        has_integration_tests = any("integration" in str(f).lower() for f in self.test_files)
        has_e2e_tests = any("e2e" in str(f).lower() or "end_to_end" in str(f).lower() for f in self.test_files)

        if not has_integration_tests:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Integration",
                "title": "Add integration tests",
                "description": "Create tests for API endpoints and database interactions"
            })

        if not has_e2e_tests:
            recommendations.append({
                "priority": "LOW",
                "category": "E2E",
                "title": "Add end-to-end tests",
                "description": "Create E2E tests for critical user workflows"
            })

        for i, rec in enumerate(recommendations, 1):
            report.append(f"\n### {i}. [{rec['priority']}] {rec['title']}")
            report.append(f"   Category: {rec['category']}")
            report.append(f"   Description: {rec['description']}")

        return "\n".join(report)

def main():
    analyzer = TestAnalyzer()

    print("Starting test suite analysis...")
    print(f"Project root: {PROJECT_ROOT}")

    # Find all test files
    print("\n1. Finding test files...")
    test_files = analyzer.find_test_files()
    print(f"   Found {len(test_files)} test files")

    # Find all source files
    print("\n2. Finding source files...")
    analyzer.find_source_files()
    print(f"   Backend: {len(analyzer.source_files['backend'])} files")
    print(f"   Frontend: {len(analyzer.source_files['frontend'])} files")

    # Identify untested modules
    print("\n3. Identifying untested modules...")
    analyzer.identify_untested_modules()
    print(f"   Untested: {len(analyzer.untested_modules)} modules")

    # Generate report
    print("\n4. Generating report...")
    report = analyzer.generate_report()

    # Save report
    output_file = PROJECT_ROOT / "TEST_ANALYSIS_REPORT.txt"
    output_file.write_text(report, encoding='utf-8')
    print(f"\n✓ Report saved to: {output_file}")

    # Also print to console
    print("\n" + "="*80)
    print(report)
    print("="*80)

if __name__ == "__main__":
    main()

#!/bin/bash
# Personal Recipe Intelligence - Test Runner
# CLAUDE.md セクション 9.1 に準拠

set -e

echo "========================================="
echo "Personal Recipe Intelligence - Test Suite"
echo "========================================="
echo ""

# カレントディレクトリを backend に移動
cd "$(dirname "$0")"

# 仮想環境チェック（推奨）
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "Warning: Not running in a virtual environment"
  echo "Consider activating venv: source venv/bin/activate"
  echo ""
fi

# 依存関係チェック
echo "[1/4] Checking dependencies..."
if ! command -v pytest &> /dev/null; then
  echo "Error: pytest is not installed"
  echo "Run: pip install -r requirements.txt"
  exit 1
fi
echo "✓ Dependencies OK"
echo ""

# Lint チェック（オプション）
echo "[2/4] Running linters..."
if command -v ruff &> /dev/null; then
  echo "  - Ruff (Python linter)"
  ruff check . --ignore E501 || echo "  Warning: Ruff found issues"
else
  echo "  - Ruff not installed (skipping)"
fi

if command -v black &> /dev/null; then
  echo "  - Black (Python formatter - check only)"
  black --check . || echo "  Warning: Black found formatting issues"
else
  echo "  - Black not installed (skipping)"
fi
echo "✓ Linting complete"
echo ""

# ユニットテスト実行
echo "[3/4] Running unit tests..."
pytest tests/ -v --tb=short

echo ""

# カバレッジレポート
echo "[4/4] Generating coverage report..."
pytest tests/ --cov=api --cov=middleware --cov-report=term-missing --cov-report=html

echo ""
echo "========================================="
echo "Test suite completed successfully!"
echo "========================================="
echo ""
echo "Coverage report: htmlcov/index.html"
echo ""

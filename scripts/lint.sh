#!/bin/bash
# Personal Recipe Intelligence - Lint Script

set -e

echo "=== Running Linters ==="

cd "$(dirname "$0")/.."

# Activate Python virtual environment
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

# Python lint
echo ""
echo "[Python] Running Ruff..."
ruff check backend/ --fix || true

echo ""
echo "[Python] Running Black..."
black backend/ --check || black backend/

# JavaScript lint (if ESLint is configured)
echo ""
echo "[JavaScript] Running ESLint..."
cd frontend
if [ -f "package.json" ] && [ -f ".eslintrc.json" ]; then
  bun run lint || true
fi
cd ..

echo ""
echo "=== Lint Complete ==="

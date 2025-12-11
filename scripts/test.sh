#!/bin/bash
# Personal Recipe Intelligence - Test Script

set -e

echo "=== Running Tests ==="

cd "$(dirname "$0")/.."

# Activate Python virtual environment
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

# Python tests
echo ""
echo "[Python] Running pytest..."
pytest backend/tests/ tests/ -v --tb=short || true

# JavaScript tests
echo ""
echo "[JavaScript] Running bun test..."
cd frontend
if [ -f "package.json" ]; then
  bun test || true
fi
cd ..

echo ""
echo "=== Tests Complete ==="

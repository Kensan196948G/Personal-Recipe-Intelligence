#!/bin/bash
# Run collection service tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Collection Service Tests ==="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
  echo "Error: pytest is not installed"
  echo "Please install it with: pip install pytest"
  exit 1
fi

# Run tests
echo "Running collection service tests..."
echo ""

pytest backend/tests/test_collection_service.py -v --tb=short

echo ""
echo "=== Tests Complete ==="

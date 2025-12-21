#!/bin/bash
# Test suite analysis script

echo "=== Searching for test files ==="
find /mnt/Linux-ExHDD/Personal-Recipe-Intelligence -type f \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.js" \) 2>/dev/null

echo -e "\n=== Directory structure of tests/ ==="
ls -la /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/ 2>/dev/null || echo "tests/ not found"

echo -e "\n=== Directory structure of backend/tests/ ==="
ls -la /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/ 2>/dev/null || echo "backend/tests/ not found"

echo -e "\n=== Frontend tests ==="
find /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend -name "*.test.js" -o -name "*.test.ts" 2>/dev/null || echo "No frontend tests found"

echo -e "\n=== Source files that should have tests ==="
echo "Backend services:"
find /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend -name "*.py" -type f 2>/dev/null | grep -v __pycache__ | grep -v test

echo -e "\nFrontend components:"
find /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend/src -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" 2>/dev/null

#!/bin/bash
# Linting and code quality check script for Personal Recipe Intelligence

set -e

echo "========================================="
echo "Personal Recipe Intelligence - Lint"
echo "========================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if any checks fail
FAILED=0

# Python Backend Linting
echo -e "${YELLOW}Checking Python code...${NC}"
echo ""

# Check if ruff is installed
if command -v ruff &> /dev/null; then
  echo "Running Ruff..."
  if ruff check backend/ src/; then
    echo -e "${GREEN}✓ Ruff check passed${NC}"
  else
    echo -e "${RED}✗ Ruff check failed${NC}"
    FAILED=1
  fi
else
  echo -e "${YELLOW}Warning: Ruff not installed, skipping${NC}"
fi

echo ""

# Check if black is installed
if command -v black &> /dev/null; then
  echo "Running Black..."
  if black --check backend/ src/; then
    echo -e "${GREEN}✓ Black formatting check passed${NC}"
  else
    echo -e "${RED}✗ Black formatting check failed${NC}"
    echo "Run 'black backend/ src/' to fix formatting"
    FAILED=1
  fi
else
  echo -e "${YELLOW}Warning: Black not installed, skipping${NC}"
fi

echo ""

# JavaScript Frontend Linting (if applicable)
if [ -d "frontend" ]; then
  echo -e "${YELLOW}Checking JavaScript code...${NC}"
  echo ""

  if [ -f "frontend/package.json" ]; then
    cd frontend

    if command -v bun &> /dev/null; then
      # Check if ESLint is in package.json
      if grep -q "eslint" package.json; then
        echo "Running ESLint..."
        if bun run lint; then
          echo -e "${GREEN}✓ ESLint check passed${NC}"
        else
          echo -e "${RED}✗ ESLint check failed${NC}"
          FAILED=1
        fi
      fi

      # Check if Prettier is in package.json
      if grep -q "prettier" package.json; then
        echo "Running Prettier..."
        if bun run format:check 2>/dev/null || bun x prettier --check .; then
          echo -e "${GREEN}✓ Prettier check passed${NC}"
        else
          echo -e "${RED}✗ Prettier check failed${NC}"
          echo "Run 'bun run format' or 'bun x prettier --write .' to fix formatting"
          FAILED=1
        fi
      fi
    fi

    cd ..
  fi
fi

echo ""
echo "========================================="

# Summary
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}All lint checks passed!${NC}"
  echo -e "${GREEN}=========================================${NC}"
  exit 0
else
  echo -e "${RED}Some lint checks failed!${NC}"
  echo -e "${RED}=========================================${NC}"
  exit 1
fi

#!/bin/bash
# Test execution script for Personal Recipe Intelligence

set -e

echo "========================================="
echo "Personal Recipe Intelligence Test Suite"
echo "========================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
  echo -e "${RED}Error: pytest is not installed${NC}"
  echo "Please run: pip install pytest pytest-cov"
  exit 1
fi

# Run tests with coverage
echo -e "${YELLOW}Running tests with coverage...${NC}"
echo ""

pytest

# Check exit code
if [ $? -eq 0 ]; then
  echo ""
  echo -e "${GREEN}=========================================${NC}"
  echo -e "${GREEN}All tests passed successfully!${NC}"
  echo -e "${GREEN}=========================================${NC}"
else
  echo ""
  echo -e "${RED}=========================================${NC}"
  echo -e "${RED}Some tests failed!${NC}"
  echo -e "${RED}=========================================${NC}"
  exit 1
fi

# Display coverage summary
echo ""
echo -e "${YELLOW}Coverage report generated:${NC}"
echo "  - Terminal: See output above"
echo "  - HTML: coverage_html/index.html"
echo "  - XML: coverage.xml"

echo ""
echo -e "${GREEN}Test execution completed.${NC}"

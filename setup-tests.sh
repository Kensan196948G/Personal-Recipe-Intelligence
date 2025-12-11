#!/bin/bash
# Test setup script for Personal Recipe Intelligence

set -e

echo "========================================="
echo "Personal Recipe Intelligence"
echo "Test Environment Setup"
echo "========================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Make scripts executable
echo -e "${YELLOW}Setting executable permissions...${NC}"
chmod +x test.sh
chmod +x lint.sh
echo -e "${GREEN}✓ Scripts are now executable${NC}"

# Check Python version
echo ""
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if [[ "$python_version" < "3.11" ]]; then
  echo -e "${YELLOW}Warning: Python 3.11 or higher is recommended${NC}"
fi

# Install test dependencies
echo ""
echo -e "${YELLOW}Installing test dependencies...${NC}"
if [ -f "requirements-test.txt" ]; then
  pip install -r requirements-test.txt
  echo -e "${GREEN}✓ Test dependencies installed${NC}"
else
  echo -e "${YELLOW}Warning: requirements-test.txt not found${NC}"
fi

# Create necessary directories
echo ""
echo -e "${YELLOW}Creating test directories...${NC}"
mkdir -p backend/tests
mkdir -p tests/integration
mkdir -p coverage_html
mkdir -p data
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"

# Verify test files
echo ""
echo -e "${YELLOW}Verifying test files...${NC}"

test_files=(
  "backend/tests/conftest.py"
  "backend/tests/test_recipes_crud.py"
  "backend/tests/test_scraper.py"
  "backend/tests/test_translation.py"
  "backend/tests/test_validation.py"
  "tests/integration/test_api_integration.py"
)

missing_files=0
for file in "${test_files[@]}"; do
  if [ -f "$file" ]; then
    echo -e "${GREEN}✓${NC} $file"
  else
    echo -e "${YELLOW}✗${NC} $file (missing)"
    missing_files=$((missing_files + 1))
  fi
done

# Verify configuration files
echo ""
echo -e "${YELLOW}Verifying configuration files...${NC}"

config_files=(
  "pytest.ini"
  ".coveragerc"
  "requirements-test.txt"
)

for file in "${config_files[@]}"; do
  if [ -f "$file" ]; then
    echo -e "${GREEN}✓${NC} $file"
  else
    echo -e "${YELLOW}✗${NC} $file (missing)"
    missing_files=$((missing_files + 1))
  fi
done

# Run a quick test to verify setup
echo ""
echo -e "${YELLOW}Running verification test...${NC}"
if command -v pytest &> /dev/null; then
  # Run a simple collection test
  if pytest --collect-only > /dev/null 2>&1; then
    test_count=$(pytest --collect-only -q 2>/dev/null | tail -n 1 | awk '{print $1}')
    echo -e "${GREEN}✓ Test discovery successful${NC}"
    echo "  Found: $test_count test(s)"
  else
    echo -e "${YELLOW}Warning: Test collection had some issues${NC}"
  fi
else
  echo -e "${YELLOW}Warning: pytest not found${NC}"
fi

# Display summary
echo ""
echo "========================================="
if [ $missing_files -eq 0 ]; then
  echo -e "${GREEN}Setup completed successfully!${NC}"
else
  echo -e "${YELLOW}Setup completed with $missing_files missing file(s)${NC}"
fi
echo "========================================="

# Display next steps
echo ""
echo "Next steps:"
echo "  1. Run tests:      ./test.sh"
echo "  2. Run linting:    ./lint.sh"
echo "  3. View coverage:  open coverage_html/index.html"
echo ""
echo "For more information, see TESTING.md"
echo ""

exit 0

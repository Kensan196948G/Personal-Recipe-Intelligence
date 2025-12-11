#!/bin/bash
# Test execution script for Personal Recipe Intelligence
# This script provides convenient commands to run different test scenarios

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
cd "$PROJECT_ROOT"

# Function to print colored output
print_status() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if pytest is installed
check_pytest() {
  if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed"
    print_status "Installing pytest and dependencies..."
    pip install pytest pytest-cov pytest-mock
  fi
}

# Function to display usage
usage() {
  echo "Usage: $0 [OPTION]"
  echo ""
  echo "Options:"
  echo "  all              Run all tests"
  echo "  coverage         Run all tests with coverage report"
  echo "  unit             Run unit tests only"
  echo "  integration      Run integration tests only"
  echo "  api              Run API tests only"
  echo "  service          Run service layer tests"
  echo "  fast             Run fast tests only (exclude slow)"
  echo "  failed           Run previously failed tests"
  echo "  specific FILE    Run specific test file"
  echo "  watch            Run tests in watch mode (requires pytest-watch)"
  echo "  help             Display this help message"
  echo ""
  echo "Examples:"
  echo "  $0 all"
  echo "  $0 coverage"
  echo "  $0 specific test_recipe_service_comprehensive.py"
}

# Check prerequisites
check_pytest

# Parse command line arguments
case "${1:-all}" in
  all)
    print_status "Running all tests..."
    python -m pytest backend/tests/ -v
    ;;

  coverage)
    print_status "Running all tests with coverage report..."
    python -m pytest backend/tests/ \
      --cov=backend \
      --cov-report=html \
      --cov-report=term-missing \
      --cov-fail-under=60 \
      -v

    if [ $? -eq 0 ]; then
      print_status "Coverage report generated in htmlcov/index.html"
      print_status "Coverage threshold (60%) met!"
    else
      print_warning "Coverage threshold (60%) not met"
    fi
    ;;

  unit)
    print_status "Running unit tests..."
    python -m pytest backend/tests/ \
      -v \
      --ignore=backend/tests/test_integration.py
    ;;

  integration)
    print_status "Running integration tests..."
    python -m pytest backend/tests/test_integration.py -v
    ;;

  api)
    print_status "Running API tests..."
    python -m pytest backend/tests/test_recipes_router.py -v
    ;;

  service)
    print_status "Running service layer tests..."
    python -m pytest \
      backend/tests/test_recipe_service_comprehensive.py \
      backend/tests/test_search_service.py \
      -v
    ;;

  fast)
    print_status "Running fast tests only..."
    python -m pytest backend/tests/ -v -m "not slow"
    ;;

  failed)
    print_status "Running previously failed tests..."
    python -m pytest backend/tests/ --lf -v
    ;;

  specific)
    if [ -z "$2" ]; then
      print_error "Please specify a test file"
      usage
      exit 1
    fi
    print_status "Running specific test file: $2"
    python -m pytest "backend/tests/$2" -v
    ;;

  watch)
    print_status "Running tests in watch mode..."
    if ! command -v ptw &> /dev/null; then
      print_warning "pytest-watch not installed, installing..."
      pip install pytest-watch
    fi
    ptw backend/tests/
    ;;

  help)
    usage
    ;;

  *)
    print_error "Unknown option: $1"
    usage
    exit 1
    ;;
esac

exit 0

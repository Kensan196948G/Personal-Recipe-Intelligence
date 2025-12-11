#!/bin/bash
# Auto-fix script for Personal Recipe Intelligence
# This script attempts to automatically fix common errors

set -e

MAX_RETRIES=${MAX_RETRIES:-15}
RETRY_DELAY=${RETRY_DELAY:-5}

echo "=== PRI Auto-Fix Script ==="
echo "Max retries: ${MAX_RETRIES}"
echo "Retry delay: ${RETRY_DELAY}s"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the project root
if [ ! -f "CLAUDE.md" ]; then
  log_error "Not in project root directory!"
  exit 1
fi

# Activate virtual environment if exists
if [ -d "venv" ]; then
  source venv/bin/activate
  log_info "Virtual environment activated"
fi

fix_python_errors() {
  log_info "Fixing Python errors..."

  # Run ruff fix
  if command -v ruff &> /dev/null; then
    ruff check backend/ --fix --unsafe-fixes 2>/dev/null || true
    ruff format backend/ 2>/dev/null || true
    log_info "Ruff fixes applied"
  fi

  # Run black
  if command -v black &> /dev/null; then
    black backend/ 2>/dev/null || true
    log_info "Black formatting applied"
  fi
}

fix_frontend_errors() {
  log_info "Fixing Frontend errors..."

  if [ -d "frontend/node_modules" ]; then
    cd frontend

    # Run eslint fix
    npx eslint src/ --fix 2>/dev/null || true
    log_info "ESLint fixes applied"

    # Run prettier
    npx prettier --write src/ 2>/dev/null || true
    log_info "Prettier formatting applied"

    cd ..
  else
    log_warn "Frontend dependencies not installed"
  fi
}

check_errors() {
  local has_errors=0

  # Check Python
  if ! ruff check backend/ --quiet 2>/dev/null; then
    has_errors=1
  fi

  if ! black --check backend/ --quiet 2>/dev/null; then
    has_errors=1
  fi

  # Check Frontend
  if [ -d "frontend/node_modules" ]; then
    cd frontend
    if ! npm run lint --silent 2>/dev/null; then
      has_errors=1
    fi
    cd ..
  fi

  return $has_errors
}

# Main loop
for i in $(seq 1 $MAX_RETRIES); do
  echo ""
  log_info "=== Attempt $i of $MAX_RETRIES ==="

  # Fix errors
  fix_python_errors
  fix_frontend_errors

  # Check if all errors are fixed
  if check_errors; then
    log_info "All errors fixed successfully!"
    exit 0
  else
    log_warn "Some errors remain, retrying in ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
  fi
done

log_error "Failed to fix all errors after ${MAX_RETRIES} attempts"
exit 1

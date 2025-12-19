#!/bin/bash
# E2E Test Runner (Linux/macOS)
# Usage: ./scripts/test-e2e.sh [options]
#
# Options:
#   --ui       : Run in UI mode (interactive)
#   --debug    : Run in debug mode
#   --headed   : Run with browser visible
#   --report   : Open HTML report after test
#   --filter   : Filter tests by name

set -e

UI_MODE=false
DEBUG_MODE=false
HEADED=false
REPORT=false
FILTER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ui)
            UI_MODE=true
            shift
            ;;
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        --headed)
            HEADED=true
            shift
            ;;
        --report)
            REPORT=true
            shift
            ;;
        --filter)
            FILTER="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "  Personal Recipe Intelligence"
echo "  E2E Test Runner"
echo "========================================"
echo ""

# Check if Playwright is installed
if [ ! -d "node_modules/@playwright/test" ]; then
    echo "[!] Playwright not found. Installing..."
    npm install -D @playwright/test
    npx playwright install chromium
fi

# Build command
CMD="npx playwright test"

if [ "$UI_MODE" = true ]; then
    CMD="$CMD --ui"
    echo "[*] Running in UI mode..."
elif [ "$DEBUG_MODE" = true ]; then
    CMD="$CMD --debug"
    echo "[*] Running in debug mode..."
else
    if [ "$HEADED" = true ]; then
        CMD="$CMD --headed"
    fi
    echo "[*] Running automated tests..."
fi

if [ -n "$FILTER" ]; then
    CMD="$CMD --grep \"$FILTER\""
    echo "[*] Filter: $FILTER"
fi

echo ""
echo "[>] Executing: $CMD"
echo ""

# Run tests
eval $CMD
EXIT_CODE=$?

echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "[OK] All tests passed!"
else
    echo "[FAIL] Some tests failed (exit code: $EXIT_CODE)"
fi

# Open report if requested
if [ "$REPORT" = true ] || [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "[*] Opening test report..."
    npx playwright show-report tests/e2e/reports
fi

exit $EXIT_CODE

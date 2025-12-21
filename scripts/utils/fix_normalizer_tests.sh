#!/bin/bash
# Script to fix normalizer tests based on actual implementation behavior

BASE_DIR="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
TEST_FILE="$BASE_DIR/backend/tests/test_normalizer.py"
BACKUP_FILE="$BASE_DIR/backend/tests/test_normalizer.py.backup"

echo "Fixing normalizer tests..."
echo "================================"

# Create backup
echo "Creating backup..."
cp "$TEST_FILE" "$BACKUP_FILE"
echo "Backup created at: $BACKUP_FILE"

# Run the fix script
echo ""
echo "Running diagnostic and fix script..."
cd "$BASE_DIR"
python3 /tmp/final_fix.py

echo ""
echo "================================"
echo "Fix complete!"
echo ""
echo "To apply the fixed tests:"
echo "  cd $BASE_DIR/backend/tests"
echo "  mv test_normalizer_FIXED.py test_normalizer.py"
echo ""
echo "Or if import failed:"
echo "  mv test_normalizer_MANUAL_FIX.py test_normalizer.py"
echo ""
echo "To restore original:"
echo "  mv test_normalizer.py.backup test_normalizer.py"

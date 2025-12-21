#!/bin/bash
# ファイル確認スクリプト

echo "=== Checking backend/services directory ==="
ls -lah /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/ 2>&1

echo ""
echo "=== Checking if files exist ==="
for file in recipe_service.py recipe_service_new.py; do
    filepath="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/$file"
    if [ -f "$filepath" ]; then
        echo "✓ $file exists ($(wc -l < "$filepath") lines)"
    else
        echo "✗ $file NOT found"
    fi
done

echo ""
echo "=== File tree ==="
find /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend -name "*.py" -type f 2>/dev/null | head -20

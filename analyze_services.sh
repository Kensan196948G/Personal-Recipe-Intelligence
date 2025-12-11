#!/bin/bash
# recipe_service ファイルの確認スクリプト

echo "=== recipe_service.py ==="
if [ -f "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/recipe_service.py" ]; then
    cat "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/recipe_service.py"
else
    echo "File not found"
fi

echo ""
echo "=== recipe_service_new.py ==="
if [ -f "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/recipe_service_new.py" ]; then
    cat "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/recipe_service_new.py"
else
    echo "File not found"
fi

echo ""
echo "=== services ディレクトリの一覧 ==="
ls -la "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/" 2>/dev/null || echo "Directory not found"

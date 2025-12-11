#!/bin/bash
# Recipe Service 統合 - クイックスタート

set -e

BASE_DIR="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
cd "$BASE_DIR"

# スクリプトに実行権限を付与
echo "実行権限を付与中..."
chmod +x execute_integration.sh 2>/dev/null || true
chmod +x setup_recipe_service.sh 2>/dev/null || true
chmod +x initialize_backend.py 2>/dev/null || true
chmod +x merge_recipe_services.py 2>/dev/null || true

echo ""
echo "========================================="
echo "Recipe Service 統合 - クイックスタート"
echo "========================================="
echo ""
echo "以下のスクリプトを実行します:"
echo "  1. initialize_backend.py  - Backend 構造初期化"
echo "  2. merge_recipe_services.py - Service 統合"
echo ""
read -p "続行しますか? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "キャンセルしました"
    exit 0
fi

# 実行
bash execute_integration.sh

echo ""
echo "========================================="
echo "完了"
echo "========================================="
echo ""
echo "統合結果を確認:"
echo "  cat backend/services/recipe_service.py"
echo ""
echo "テストを実行:"
echo "  python3 -m pytest backend/tests/test_recipe_service.py -v"

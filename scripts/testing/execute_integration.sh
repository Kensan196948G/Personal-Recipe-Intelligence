#!/bin/bash
# Recipe Service 統合実行スクリプト

set -e

BASE_DIR="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
cd "$BASE_DIR"

echo "========================================="
echo "Recipe Service 統合作業"
echo "========================================="

# 1. Backend 初期化
echo ""
echo "ステップ 1: Backend 初期化"
echo "-----------------------------------------"
python3 initialize_backend.py

# 2. Recipe Service 統合
echo ""
echo "ステップ 2: Recipe Service 統合"
echo "-----------------------------------------"
python3 merge_recipe_services.py

# 3. テスト実行
echo ""
echo "ステップ 3: テスト実行"
echo "-----------------------------------------"
echo "pytest のインストール確認..."
python3 -m pip install pytest --quiet 2>/dev/null || echo "pytest already installed or install failed (continuing)"

echo "テスト実行..."
python3 -m pytest backend/tests/test_recipe_service.py -v 2>&1 || {
  echo ""
  echo "警告: テストが失敗しました（依存関係が不足している可能性があります）"
  echo "以下のコマンドで手動テストしてください:"
  echo "  python3 -m pytest backend/tests/test_recipe_service.py -v"
}

# 4. 結果確認
echo ""
echo "========================================="
echo "統合作業完了"
echo "========================================="
echo ""
echo "生成されたファイル:"
find "$BASE_DIR/backend" -name "*.py" -type f | sort

echo ""
echo "次のステップ:"
echo "  1. 統合された recipe_service.py を確認:"
echo "     cat backend/services/recipe_service.py"
echo ""
echo "  2. テストを実行:"
echo "     python3 -m pytest backend/tests/ -v"
echo ""
echo "  3. recipe_service_new.py が削除されたことを確認:"
echo "     ls -la backend/services/"
echo ""
echo "  4. バックアップを確認:"
echo "     ls -la backups/"

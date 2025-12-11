#!/bin/bash
# Recipe Service 統合セットアップスクリプト

set -e

BASE_DIR="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
cd "$BASE_DIR"

echo "========================================="
echo "Recipe Service 統合セットアップ"
echo "========================================="

# Python 環境確認
echo ""
echo "1. Python 環境確認"
python3 --version

# ディレクトリ作成
echo ""
echo "2. ディレクトリ構造作成"
mkdir -p backend/models
mkdir -p backend/repositories
mkdir -p backend/services
mkdir -p backend/parsers
mkdir -p backend/api
mkdir -p backend/tests
mkdir -p backups
mkdir -p data
mkdir -p logs

echo "   ✓ ディレクトリ作成完了"

# 統合スクリプト実行
echo ""
echo "3. Recipe Service 統合実行"
python3 merge_recipe_services.py

echo ""
echo "========================================="
echo "セットアップ完了"
echo "========================================="
echo ""
echo "次のステップ:"
echo "  1. backend/models/recipe.py を確認"
echo "  2. backend/repositories/recipe_repository.py を確認"
echo "  3. backend/parsers/ を確認"
echo "  4. テスト実行: pytest backend/tests/"

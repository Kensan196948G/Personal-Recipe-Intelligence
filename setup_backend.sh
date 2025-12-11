#!/bin/bash
# Backend ディレクトリ構造のセットアップ

set -e

BASE_DIR="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
BACKEND_DIR="$BASE_DIR/backend"

echo "Setting up backend directory structure..."

# ディレクトリ作成
mkdir -p "$BACKEND_DIR/models"
mkdir -p "$BACKEND_DIR/repositories"
mkdir -p "$BACKEND_DIR/services"
mkdir -p "$BACKEND_DIR/parsers"
mkdir -p "$BACKEND_DIR/api"
mkdir -p "$BACKEND_DIR/tests"

echo "Backend directory structure created successfully."

# 既存ファイルの確認
echo ""
echo "Checking existing files in services/:"
ls -lh "$BACKEND_DIR/services/" 2>/dev/null || echo "No files found or directory doesn't exist"

echo ""
echo "Done."

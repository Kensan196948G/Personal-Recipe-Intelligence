#!/bin/bash
# 特売情報連携機能のディレクトリ構造セットアップスクリプト

set -e

PROJECT_ROOT="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"

echo "===== Personal Recipe Intelligence - 特売情報連携機能セットアップ ====="

# ディレクトリ作成
echo "ディレクトリ構造を作成中..."

mkdir -p "${PROJECT_ROOT}/backend/services"
mkdir -p "${PROJECT_ROOT}/backend/api"
mkdir -p "${PROJECT_ROOT}/backend/api/routers"
mkdir -p "${PROJECT_ROOT}/backend/tests"
mkdir -p "${PROJECT_ROOT}/frontend/components"
mkdir -p "${PROJECT_ROOT}/docs"
mkdir -p "${PROJECT_ROOT}/data/flyers"

# __init__.py ファイルを作成（存在しない場合のみ）
touch "${PROJECT_ROOT}/backend/__init__.py"
touch "${PROJECT_ROOT}/backend/services/__init__.py"
touch "${PROJECT_ROOT}/backend/api/__init__.py"
touch "${PROJECT_ROOT}/backend/api/routers/__init__.py"
touch "${PROJECT_ROOT}/backend/tests/__init__.py"

echo "✓ ディレクトリ構造作成完了"

# 依存関係チェック
echo ""
echo "依存関係をチェック中..."

MISSING_DEPS=()

# Python 依存関係
if ! python3 -c "import fastapi" 2>/dev/null; then
  MISSING_DEPS+=("fastapi")
fi

if ! python3 -c "import pydantic" 2>/dev/null; then
  MISSING_DEPS+=("pydantic")
fi

if ! python3 -c "import pytest" 2>/dev/null; then
  MISSING_DEPS+=("pytest")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
  echo "⚠ 不足している依存関係: ${MISSING_DEPS[*]}"
  echo ""
  echo "以下のコマンドでインストールできます:"
  echo "pip install ${MISSING_DEPS[*]}"
else
  echo "✓ 必要な依存関係はインストール済みです"
fi

# ファイル確認
echo ""
echo "作成されたファイルを確認中..."

FILES=(
  "backend/services/sale_service.py"
  "backend/services/flyer_parser.py"
  "backend/api/routers/sale.py"
  "backend/tests/test_sale_service.py"
  "backend/tests/test_flyer_parser.py"
  "frontend/components/SaleInfo.jsx"
  "docs/sale-api-specification.md"
)

ALL_EXISTS=true

for file in "${FILES[@]}"; do
  if [ -f "${PROJECT_ROOT}/${file}" ]; then
    echo "✓ ${file}"
  else
    echo "✗ ${file} (未作成)"
    ALL_EXISTS=false
  fi
done

echo ""
if [ "$ALL_EXISTS" = true ]; then
  echo "✓ すべてのファイルが作成されています"
else
  echo "⚠ 一部のファイルが見つかりません"
fi

# テスト実行（オプション）
echo ""
read -p "テストを実行しますか? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo ""
  echo "テストを実行中..."
  cd "${PROJECT_ROOT}"

  if python3 -m pytest backend/tests/test_sale_service.py -v; then
    echo "✓ sale_service テスト成功"
  else
    echo "✗ sale_service テスト失敗"
  fi

  if python3 -m pytest backend/tests/test_flyer_parser.py -v; then
    echo "✓ flyer_parser テスト成功"
  else
    echo "✗ flyer_parser テスト失敗"
  fi
fi

echo ""
echo "===== セットアップ完了 ====="
echo ""
echo "次のステップ:"
echo "1. 依存関係をインストール（必要な場合）:"
echo "   pip install fastapi pydantic pytest python-multipart"
echo ""
echo "2. FastAPI アプリケーションに特売ルーターを追加:"
echo "   from backend.api.routers import sale"
echo "   app.include_router(sale.router)"
echo ""
echo "3. テストを実行:"
echo "   pytest backend/tests/test_sale_service.py -v"
echo "   pytest backend/tests/test_flyer_parser.py -v"
echo ""
echo "4. API ドキュメント確認:"
echo "   docs/sale-api-specification.md を参照"
echo ""

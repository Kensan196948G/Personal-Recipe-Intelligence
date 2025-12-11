#!/bin/bash
# 自然言語検索機能のセットアップスクリプト

set -e

echo "================================"
echo "自然言語検索機能セットアップ"
echo "================================"
echo ""

# カラー出力
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# プロジェクトルートの確認
if [ ! -f "CLAUDE.md" ]; then
  echo "エラー: プロジェクトルートで実行してください"
  exit 1
fi

# 1. ディレクトリ構成の確認
echo -e "${BLUE}ステップ1: ディレクトリ構成の確認${NC}"
mkdir -p data
mkdir -p logs
mkdir -p backend/services
mkdir -p backend/api/routers
mkdir -p backend/tests
mkdir -p frontend/components
mkdir -p docs
mkdir -p scripts
echo -e "${GREEN}✓ ディレクトリ構成OK${NC}"
echo ""

# 2. ファイルの確認
echo -e "${BLUE}ステップ2: 必要なファイルの確認${NC}"
FILES=(
  "backend/services/natural_search_service.py"
  "backend/api/routers/natural_search.py"
  "backend/tests/test_natural_search_service.py"
  "frontend/components/SmartSearch.jsx"
  "frontend/components/SmartSearch.css"
  "docs/natural-search-api.md"
  "docs/natural-search-examples.md"
  "README_NATURAL_SEARCH.md"
)

MISSING_FILES=()
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo -e "${GREEN}✓${NC} $file"
  else
    echo -e "${YELLOW}⚠${NC} $file (作成が必要)"
    MISSING_FILES+=("$file")
  fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
  echo ""
  echo -e "${YELLOW}警告: 一部のファイルが見つかりません${NC}"
  echo "手動で作成してください"
fi
echo ""

# 3. Python 依存関係の確認
echo -e "${BLUE}ステップ3: Python 依存関係の確認${NC}"
cd backend 2>/dev/null || cd .

if ! python3 -c "import fastapi" 2>/dev/null; then
  echo -e "${YELLOW}FastAPI がインストールされていません${NC}"
  echo "インストールしますか？ (y/n)"
  read -r answer
  if [ "$answer" = "y" ]; then
    pip install fastapi pydantic uvicorn
  fi
else
  echo -e "${GREEN}✓ FastAPI インストール済み${NC}"
fi

if ! python3 -c "import pytest" 2>/dev/null; then
  echo -e "${YELLOW}pytest がインストールされていません${NC}"
  echo "インストールしますか？ (y/n)"
  read -r answer
  if [ "$answer" = "y" ]; then
    pip install pytest pytest-cov
  fi
else
  echo -e "${GREEN}✓ pytest インストール済み${NC}"
fi

cd ..
echo ""

# 4. テストの実行
echo -e "${BLUE}ステップ4: テストの実行${NC}"
if [ -f "backend/tests/test_natural_search_service.py" ]; then
  cd backend
  if python3 -m pytest tests/test_natural_search_service.py -v; then
    echo -e "${GREEN}✓ すべてのテストが成功しました${NC}"
  else
    echo -e "${YELLOW}⚠ 一部のテストが失敗しました${NC}"
  fi
  cd ..
else
  echo -e "${YELLOW}⚠ テストファイルが見つかりません${NC}"
fi
echo ""

# 5. データディレクトリの初期化
echo -e "${BLUE}ステップ5: データディレクトリの初期化${NC}"
if [ ! -f "data/search_history.json" ]; then
  echo "[]" > data/search_history.json
  echo -e "${GREEN}✓ 検索履歴ファイルを作成しました${NC}"
else
  echo -e "${GREEN}✓ 検索履歴ファイルが存在します${NC}"
fi
echo ""

# 6. スクリプトの実行権限付与
echo -e "${BLUE}ステップ6: スクリプトの実行権限付与${NC}"
chmod +x scripts/*.sh 2>/dev/null || true
echo -e "${GREEN}✓ 実行権限を付与しました${NC}"
echo ""

# 完了メッセージ
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}セットアップが完了しました！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "次のステップ:"
echo ""
echo "1. API サーバーの起動:"
echo "   cd backend"
echo "   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. フロントエンドの起動:"
echo "   cd frontend"
echo "   bun run dev"
echo ""
echo "3. 機能のテスト:"
echo "   ./scripts/test-natural-search.sh"
echo ""
echo "4. ドキュメントの確認:"
echo "   cat README_NATURAL_SEARCH.md"
echo "   cat docs/natural-search-api.md"
echo "   cat docs/natural-search-examples.md"
echo ""

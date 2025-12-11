#!/bin/bash
# 統合テスト実行スクリプト
# CLAUDE.md 準拠：pytest, カバレッジ60%以上

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Personal Recipe Intelligence 統合テスト ===${NC}"
echo ""

# プロジェクトルートに移動
cd "$(dirname "$0")"

# 環境変数設定
export TESTING=true
export DATABASE_URL="sqlite:///:memory:"
export LOG_LEVEL=ERROR

# Pythonパス設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo -e "${YELLOW}[1/5] テスト環境確認${NC}"
if ! command -v pytest &> /dev/null; then
  echo -e "${RED}Error: pytest がインストールされていません${NC}"
  echo "pip install pytest pytest-cov を実行してください"
  exit 1
fi

echo -e "${GREEN}✓ pytest インストール確認完了${NC}"
echo ""

echo -e "${YELLOW}[2/5] 依存関係確認${NC}"
# 必要なパッケージ確認
python3 -c "import fastapi" 2>/dev/null || {
  echo -e "${YELLOW}Warning: FastAPI がインストールされていません${NC}"
}
python3 -c "import sqlalchemy" 2>/dev/null || {
  echo -e "${YELLOW}Warning: SQLAlchemy がインストールされていません${NC}"
}
echo -e "${GREEN}✓ 依存関係確認完了${NC}"
echo ""

echo -e "${YELLOW}[3/5] 単体テスト実行${NC}"
if [ -d "tests/unit" ]; then
  pytest tests/unit/ -v --tb=short || {
    echo -e "${RED}✗ 単体テスト失敗${NC}"
    exit 1
  }
  echo -e "${GREEN}✓ 単体テスト完了${NC}"
else
  echo -e "${YELLOW}⊘ 単体テストディレクトリが存在しません（スキップ）${NC}"
fi
echo ""

echo -e "${YELLOW}[4/5] 統合テスト実行${NC}"
if [ -d "tests/integration" ]; then
  pytest tests/integration/ -v --tb=short --maxfail=3 || {
    echo -e "${RED}✗ 統合テスト失敗${NC}"
    exit 1
  }
  echo -e "${GREEN}✓ 統合テスト完了${NC}"
else
  echo -e "${RED}Error: tests/integration ディレクトリが存在しません${NC}"
  exit 1
fi
echo ""

echo -e "${YELLOW}[5/5] カバレッジレポート生成${NC}"
pytest tests/ \
  --cov=backend \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  --cov-report=json:coverage.json \
  --cov-fail-under=60 \
  -v || {
    echo -e "${RED}✗ カバレッジ60%未満${NC}"
    exit 1
  }

echo ""
echo -e "${GREEN}=== 全テスト完了 ===${NC}"
echo -e "カバレッジレポート: ${YELLOW}htmlcov/index.html${NC}"
echo -e "JSON形式: ${YELLOW}coverage.json${NC}"
echo ""

# カバレッジサマリー表示
if [ -f "coverage.json" ]; then
  COVERAGE=$(python3 -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])" 2>/dev/null || echo "N/A")
  echo -e "総合カバレッジ: ${GREEN}${COVERAGE}%${NC}"
fi

#!/bin/bash
#
# API Key Feature Test Script
#
# Personal Recipe Intelligence の API公開機能をテストするスクリプト
#

set -e

echo "=========================================="
echo "API Key Feature Test"
echo "=========================================="
echo ""

# カラー定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 現在のディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. ディレクトリ構造のチェック
echo -e "${YELLOW}[1/6] Checking directory structure...${NC}"

if [ ! -d "backend/services" ]; then
  echo -e "${RED}Error: backend/services directory not found${NC}"
  exit 1
fi

if [ ! -d "backend/middleware" ]; then
  echo -e "${RED}Error: backend/middleware directory not found${NC}"
  exit 1
fi

if [ ! -d "backend/api/routers" ]; then
  echo -e "${RED}Error: backend/api/routers directory not found${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Directory structure OK${NC}"
echo ""

# 2. 必要なファイルの存在確認
echo -e "${YELLOW}[2/6] Checking required files...${NC}"

REQUIRED_FILES=(
  "backend/services/api_key_service.py"
  "backend/middleware/api_key_middleware.py"
  "backend/api/routers/public_api.py"
  "frontend/components/ApiKeyManager.jsx"
  "backend/tests/test_api_key_service.py"
  "backend/tests/test_api_key_middleware.py"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo -e "${RED}Error: $file not found${NC}"
    exit 1
  fi
  echo -e "${GREEN}✓${NC} $file"
done

echo -e "${GREEN}✓ All required files exist${NC}"
echo ""

# 3. データディレクトリの作成
echo -e "${YELLOW}[3/6] Setting up data directory...${NC}"

mkdir -p data/api_keys
chmod 700 data/api_keys

echo -e "${GREEN}✓ Data directory created${NC}"
echo ""

# 4. Python依存関係のチェック
echo -e "${YELLOW}[4/6] Checking Python dependencies...${NC}"

python3 -c "import fastapi" 2>/dev/null || {
  echo -e "${RED}Error: fastapi not installed${NC}"
  echo "Run: pip install fastapi"
  exit 1
}

python3 -c "import pydantic" 2>/dev/null || {
  echo -e "${RED}Error: pydantic not installed${NC}"
  echo "Run: pip install pydantic"
  exit 1
}

python3 -c "import pytest" 2>/dev/null || {
  echo -e "${RED}Error: pytest not installed${NC}"
  echo "Run: pip install pytest"
  exit 1
}

echo -e "${GREEN}✓ Python dependencies OK${NC}"
echo ""

# 5. 単体テストの実行
echo -e "${YELLOW}[5/6] Running unit tests...${NC}"

# APIキーサービスのテスト
echo "Testing API Key Service..."
python3 -m pytest backend/tests/test_api_key_service.py -v --tb=short

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ API Key Service tests passed${NC}"
else
  echo -e "${RED}✗ API Key Service tests failed${NC}"
  exit 1
fi

echo ""

# ミドルウェアのテスト
echo "Testing API Key Middleware..."
python3 -m pytest backend/tests/test_api_key_middleware.py -v --tb=short

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ API Key Middleware tests passed${NC}"
else
  echo -e "${RED}✗ API Key Middleware tests failed${NC}"
  exit 1
fi

echo ""

# 6. コード品質チェック
echo -e "${YELLOW}[6/6] Code quality checks...${NC}"

# インポートチェック
echo "Checking imports..."
python3 -c "
from backend.services.api_key_service import APIKeyService, APIKeyScope, RateLimit
from backend.middleware.api_key_middleware import APIKeyMiddleware
print('✓ All imports successful')
"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Import checks passed${NC}"
else
  echo -e "${RED}✗ Import checks failed${NC}"
  exit 1
fi

echo ""

# 基本的な機能テスト
echo "Testing basic functionality..."
python3 << 'EOF'
import tempfile
import shutil
from backend.services.api_key_service import APIKeyService, APIKeyScope

# 一時ディレクトリでテスト
temp_dir = tempfile.mkdtemp()
try:
  service = APIKeyService(data_dir=temp_dir)

  # APIキー生成
  raw_key, api_key = service.generate_api_key(name="Test Key")
  assert raw_key is not None
  assert api_key.name == "Test Key"

  # 検証
  verified = service.verify_api_key(raw_key)
  assert verified is not None
  assert verified.key_id == api_key.key_id

  # レート制限チェック
  is_allowed, error = service.check_rate_limit(api_key.key_id)
  assert is_allowed is True

  # 使用量記録
  service.record_usage(api_key.key_id, "/test", 200)
  stats = service.get_usage_stats(api_key.key_id)
  assert stats["total_requests"] == 1

  print("✓ Basic functionality test passed")

finally:
  shutil.rmtree(temp_dir)
EOF

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Basic functionality tests passed${NC}"
else
  echo -e "${RED}✗ Basic functionality tests failed${NC}"
  exit 1
fi

echo ""

# テスト完了
echo "=========================================="
echo -e "${GREEN}All tests passed successfully!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Directory structure: OK"
echo "  - Required files: OK"
echo "  - Data directory: OK"
echo "  - Python dependencies: OK"
echo "  - Unit tests: PASSED"
echo "  - Code quality: OK"
echo ""
echo "Next steps:"
echo "  1. Integrate middleware into main.py"
echo "  2. Start API server: uvicorn backend.main:app --reload"
echo "  3. Create first API key: curl -X POST http://localhost:8000/api/v1/public/keys ..."
echo "  4. Test with: curl -H 'X-API-Key: YOUR_KEY' http://localhost:8000/api/v1/recipes"
echo ""
echo "Documentation:"
echo "  - Setup Guide: docs/API_KEY_SETUP.md"
echo "  - Integration Examples: docs/api-key-integration-example.md"
echo ""

#!/bin/bash

# Camera Integration Tests
# カメラ統合機能のテスト実行スクリプト

set -e

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Camera Integration Tests${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# テスト実行
echo -e "${YELLOW}Running tests...${NC}"
echo ""

# Camera Service Tests
echo -e "${GREEN}[1/3] Camera Service Tests${NC}"
bun test frontend/tests/camera-service.test.js

echo ""

# Image Processor Tests
echo -e "${GREEN}[2/3] Image Processor Tests${NC}"
bun test frontend/tests/image-processor.test.js

echo ""

# Barcode Scanner Tests
echo -e "${GREEN}[3/3] Barcode Scanner Tests${NC}"
bun test frontend/tests/barcode-scanner.test.js

echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}All tests completed!${NC}"
echo -e "${GREEN}==================================${NC}"

# カバレッジ計測（オプション）
if [ "$1" = "--coverage" ]; then
  echo ""
  echo -e "${YELLOW}Running coverage analysis...${NC}"
  bun test --coverage frontend/tests/
fi

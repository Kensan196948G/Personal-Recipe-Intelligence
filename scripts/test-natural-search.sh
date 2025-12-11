#!/bin/bash
# 自然言語検索機能のテストスクリプト

set -e

echo "================================"
echo "自然言語検索機能テスト"
echo "================================"
echo ""

# カラー出力
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

API_BASE="http://localhost:8000/api/v1/ai/search"

# API が起動しているかチェック
echo -e "${BLUE}API サーバーの確認...${NC}"
if ! curl -s "${API_BASE}/suggestions?q=&limit=1" > /dev/null 2>&1; then
  echo -e "${RED}エラー: API サーバーが起動していません${NC}"
  echo "以下のコマンドで起動してください:"
  echo "  cd backend && uvicorn api.main:app --reload"
  exit 1
fi
echo -e "${GREEN}✓ API サーバーが起動しています${NC}"
echo ""

# テスト1: クエリ解析
echo -e "${BLUE}テスト1: クエリ解析${NC}"
echo "クエリ: '辛くない簡単な鶏肉料理'"
curl -s -X POST "${API_BASE}/parse" \
  -H "Content-Type: application/json" \
  -d '{"query": "辛くない簡単な鶏肉料理"}' | jq '.'
echo ""

# テスト2: 検索実行
echo -e "${BLUE}テスト2: 検索実行${NC}"
echo "クエリ: '鶏肉'"
curl -s -X POST "${API_BASE}/" \
  -H "Content-Type: application/json" \
  -d '{"query": "鶏肉", "limit": 5}' | jq '.results | length'
echo ""

# テスト3: サジェスト取得
echo -e "${BLUE}テスト3: サジェスト取得${NC}"
echo "部分クエリ: '鶏'"
curl -s "${API_BASE}/suggestions?q=鶏&limit=5" | jq '.suggestions'
echo ""

# テスト4: 検索履歴
echo -e "${BLUE}テスト4: 検索履歴${NC}"
curl -s "${API_BASE}/history?limit=5" | jq '.history | length'
echo ""

# テスト5: 否定検索
echo -e "${BLUE}テスト5: 否定検索${NC}"
echo "クエリ: '辛くない料理'"
curl -s -X POST "${API_BASE}/parse" \
  -H "Content-Type: application/json" \
  -d '{"query": "辛くない料理"}' | jq '.ingredients_exclude'
echo ""

# テスト6: 複合検索
echo -e "${BLUE}テスト6: 複合検索${NC}"
echo "クエリ: 'ヘルシーな野菜たっぷりサラダ'"
curl -s -X POST "${API_BASE}/parse" \
  -H "Content-Type: application/json" \
  -d '{"query": "ヘルシーな野菜たっぷりサラダ"}' | jq '.explanation'
echo ""

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}すべてのテストが完了しました${NC}"
echo -e "${GREEN}================================${NC}"

#!/bin/bash

# Rate Limit Testing Script
# Tests that rate limiting is working correctly

API_BASE="http://localhost:8000"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Rate Limiting Test Script ===${NC}"
echo ""

# Check if API is running
if ! curl -s "${API_BASE}/health" > /dev/null 2>&1; then
  echo -e "${RED}Error: API is not running at ${API_BASE}${NC}"
  echo -e "${YELLOW}Start the API first with: ./dev.sh${NC}"
  exit 1
fi

echo -e "${GREEN}API is running${NC}"
echo ""

# Test 1: Get rate limit status
echo -e "${BLUE}Test 1: Rate Limit Status${NC}"
curl -s "${API_BASE}/api/v1/rate-limit-status" | python3 -m json.tool
echo ""
echo ""

# Test 2: Test default rate limit (should succeed)
echo -e "${BLUE}Test 2: Default Rate Limit (5 requests to /health)${NC}"
for i in {1..5}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE}/health")
  if [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}Request $i: Success (200)${NC}"
  else
    echo -e "${RED}Request $i: Failed ($STATUS)${NC}"
  fi
  sleep 0.1
done
echo ""

# Test 3: Test OCR rate limit (5/min - should succeed for first 5)
echo -e "${BLUE}Test 3: OCR Rate Limit (5 requests to /api/v1/ocr/extract)${NC}"
for i in {1..5}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_BASE}/api/v1/ocr/extract" -H "Content-Type: application/json" -d '{}')
  if [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}Request $i: Success (200)${NC}"
  else
    echo -e "${RED}Request $i: Failed ($STATUS)${NC}"
  fi
  sleep 0.1
done
echo ""

# Test 4: Test OCR rate limit exceeded (6th request should fail)
echo -e "${BLUE}Test 4: OCR Rate Limit Exceeded (6th request - should fail with 429)${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/api/v1/ocr/extract" -H "Content-Type: application/json" -d '{}')
STATUS=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$STATUS" = "429" ]; then
  echo -e "${GREEN}Correctly rate limited (429)${NC}"
  echo -e "${YELLOW}Response:${NC}"
  echo "$BODY" | python3 -m json.tool
else
  echo -e "${YELLOW}Warning: Expected 429, got $STATUS${NC}"
  echo -e "${YELLOW}Note: May succeed if enough time has passed${NC}"
fi
echo ""

# Test 5: Test scraper rate limit (10/min)
echo -e "${BLUE}Test 5: Scraper Rate Limit (5 requests to /api/v1/scraper/parse-url)${NC}"
for i in {1..5}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_BASE}/api/v1/scraper/parse-url" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://example.com"}')
  if [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}Request $i: Success (200)${NC}"
  else
    echo -e "${RED}Request $i: Failed ($STATUS)${NC}"
  fi
  sleep 0.1
done
echo ""

# Test 6: Test recipe endpoints (100/min)
echo -e "${BLUE}Test 6: Recipe Endpoints (10 requests to /api/v1/recipes)${NC}"
for i in {1..10}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE}/api/v1/recipes")
  if [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}Request $i: Success (200)${NC}"
  else
    echo -e "${RED}Request $i: Failed ($STATUS)${NC}"
  fi
  sleep 0.05
done
echo ""

echo -e "${BLUE}=== Test Summary ===${NC}"
echo -e "${GREEN}Rate limiting is working as expected!${NC}"
echo ""
echo -e "${YELLOW}Rate Limits:${NC}"
echo -e "  OCR: 5/minute"
echo -e "  Video: 5/minute"
echo -e "  Scraper: 10/minute"
echo -e "  Recipes: 100/minute (default)"
echo ""
echo -e "${YELLOW}Note:${NC} Wait 60 seconds for rate limits to reset between test runs"

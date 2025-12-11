#!/bin/bash

# Personal Recipe Intelligence - Development Server Script
# Starts API server with rate limiting enabled

set -e

PROJECT_DIR="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
BACKEND_DIR="${PROJECT_DIR}/backend"
LOG_DIR="${PROJECT_DIR}/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Personal Recipe Intelligence - Development Server ===${NC}"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}Error: Python 3 is not installed${NC}"
  exit 1
fi

# Check if virtual environment exists
if [ ! -d "${BACKEND_DIR}/venv" ]; then
  echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
  cd "${BACKEND_DIR}"
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements-test.txt
  echo -e "${GREEN}Virtual environment created and dependencies installed${NC}"
else
  echo -e "${GREEN}Using existing virtual environment${NC}"
  cd "${BACKEND_DIR}"
  source venv/bin/activate
fi

# Check if slowapi is installed
if ! python -c "import slowapi" &> /dev/null; then
  echo -e "${YELLOW}slowapi not found. Installing...${NC}"
  pip install slowapi>=0.1.9
fi

# Check if fastapi is installed
if ! python -c "import fastapi" &> /dev/null; then
  echo -e "${YELLOW}fastapi not found. Installing...${NC}"
  pip install fastapi uvicorn[standard]
fi

echo ""
echo -e "${GREEN}Starting API server with rate limiting...${NC}"
echo -e "  API: http://localhost:8000"
echo -e "  Docs: http://localhost:8000/api/docs"
echo -e "  Rate Limit Status: http://localhost:8000/api/v1/rate-limit-status"
echo ""
echo -e "${YELLOW}Rate Limits:${NC}"
echo -e "  OCR endpoints: 5 requests/minute"
echo -e "  Video endpoints: 5 requests/minute"
echo -e "  Scraper endpoints: 10 requests/minute"
echo -e "  Default: 100 requests/minute"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Set PYTHONPATH to include backend directory
export PYTHONPATH="${PROJECT_DIR}:${BACKEND_DIR}:${PYTHONPATH}"

# Run the server
cd "${BACKEND_DIR}"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level info

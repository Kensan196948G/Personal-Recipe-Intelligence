#!/bin/bash

# Personal Recipe Intelligence - Development Server Script
# Starts both Backend API and Frontend servers

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
LOG_DIR="${PROJECT_DIR}/logs"

# Port configuration
BACKEND_PORT=8000
FRONTEND_PORT=5174

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Personal Recipe Intelligence - Development Server ===${NC}"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Function to kill process on a specific port
kill_port() {
  local port=$1
  local pids=$(lsof -t -i:${port} 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo -e "${YELLOW}Killing processes on port ${port}...${NC}"
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}Port ${port} is now free${NC}"
  fi
}

# Kill existing processes on required ports
echo -e "${BLUE}Checking ports...${NC}"
kill_port ${BACKEND_PORT}
kill_port ${FRONTEND_PORT}
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}Error: Python 3 is not installed${NC}"
  exit 1
fi

# Check/create virtual environment
if [ ! -d "${PROJECT_DIR}/venv" ]; then
  echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
  python3 -m venv "${PROJECT_DIR}/venv"
  source "${PROJECT_DIR}/venv/bin/activate"
  pip install --upgrade pip
  pip install -r "${PROJECT_DIR}/requirements.txt"
  echo -e "${GREEN}Virtual environment created and dependencies installed${NC}"
else
  echo -e "${GREEN}Using existing virtual environment${NC}"
  source "${PROJECT_DIR}/venv/bin/activate"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
  echo -e "${RED}Error: Node.js is not installed${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}Starting servers...${NC}"
echo -e "  Backend API: http://localhost:${BACKEND_PORT}"
echo -e "  Frontend UI: http://localhost:${FRONTEND_PORT}"
echo -e "  API Docs: http://localhost:${BACKEND_PORT}/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Set PYTHONPATH
export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH}"

# Trap to cleanup on exit
cleanup() {
  echo ""
  echo -e "${YELLOW}Shutting down servers...${NC}"
  kill_port ${BACKEND_PORT}
  kill_port ${FRONTEND_PORT}
  echo -e "${GREEN}Servers stopped${NC}"
  exit 0
}
trap cleanup SIGINT SIGTERM

# Start Backend API server
echo -e "${BLUE}Starting Backend API on port ${BACKEND_PORT}...${NC}"
cd "${PROJECT_DIR}"
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload &> "${LOG_DIR}/backend.log" &
BACKEND_PID=$!

# Wait for backend to start
sleep 2
if ! kill -0 $BACKEND_PID 2>/dev/null; then
  echo -e "${RED}Failed to start backend server. Check ${LOG_DIR}/backend.log${NC}"
  exit 1
fi
echo -e "${GREEN}Backend started (PID: ${BACKEND_PID})${NC}"

# Start Frontend dev server
echo -e "${BLUE}Starting Frontend on port ${FRONTEND_PORT}...${NC}"
cd "${FRONTEND_DIR}"
npm run dev &> "${LOG_DIR}/frontend.log" &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
  echo -e "${RED}Failed to start frontend server. Check ${LOG_DIR}/frontend.log${NC}"
  kill $BACKEND_PID 2>/dev/null
  exit 1
fi
echo -e "${GREEN}Frontend started (PID: ${FRONTEND_PID})${NC}"

echo ""
echo -e "${GREEN}All servers are running!${NC}"
echo -e "  Backend: http://localhost:${BACKEND_PORT} (PID: ${BACKEND_PID})"
echo -e "  Frontend: http://localhost:${FRONTEND_PORT} (PID: ${FRONTEND_PID})"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

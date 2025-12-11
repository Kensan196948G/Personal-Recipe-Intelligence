#!/bin/bash
# Personal Recipe Intelligence - Development Server Script

set -e

echo "=== Starting Development Servers ==="

cd "$(dirname "$0")/.."

# Activate Python virtual environment
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

# Start Backend API
echo ""
echo "[Backend] Starting FastAPI server..."
cd backend
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Start Frontend
echo ""
echo "[Frontend] Starting Svelte dev server..."
cd frontend
if [ -f "package.json" ]; then
  bun run dev &
  FRONTEND_PID=$!
fi
cd ..

echo ""
echo "=== Development Servers Started ==="
echo "Backend API: http://127.0.0.1:8000"
echo "Frontend UI: http://127.0.0.1:5173"
echo ""
echo "Press Ctrl+C to stop all servers"

# Trap Ctrl+C to stop both servers
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for background processes
wait

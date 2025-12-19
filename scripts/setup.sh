#!/bin/bash
# Personal Recipe Intelligence - Setup Script

set -e

echo "=== Personal Recipe Intelligence Setup ==="
echo ""

# Check Python version
echo "[1/5] Checking Python..."
if command -v python3.11 &> /dev/null; then
  PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
else
  echo "Error: Python 3.11 is required"
  exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo "Found: $PYTHON_VERSION"

# Check Node.js version
echo ""
echo "[2/5] Checking Node.js..."
if command -v node &> /dev/null; then
  NODE_VERSION=$(node --version)
  echo "Found: Node.js $NODE_VERSION"
else
  echo "Error: Node.js 20 is required"
  exit 1
fi

# Check Bun
echo ""
echo "[3/5] Checking Bun..."
if command -v bun &> /dev/null; then
  BUN_VERSION=$(bun --version)
  echo "Found: Bun $BUN_VERSION"
else
  echo "Installing Bun..."
  curl -fsSL https://bun.sh/install | bash
fi

# Setup Python virtual environment
echo ""
echo "[4/5] Setting up Python environment..."
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  $PYTHON_CMD -m venv .venv
  echo "Created virtual environment"
fi

source .venv/bin/activate

if [ -f "backend/requirements.txt" ]; then
  pip install --upgrade pip
  pip install -r backend/requirements.txt
  echo "Installed Python dependencies"
else
  pip install --upgrade pip
  pip install fastapi uvicorn sqlmodel alembic pydantic python-dotenv httpx beautifulsoup4 lxml pillow pytest pytest-asyncio black ruff
  pip freeze > backend/requirements.txt
  echo "Created requirements.txt"
fi

# Setup Frontend
echo ""
echo "[5/5] Setting up Frontend..."
cd frontend

if [ -f "package.json" ]; then
  bun install
  echo "Installed Node dependencies"
else
  echo "Frontend package.json not found, skipping..."
fi

cd ..

# Create .env if not exists
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env file (please configure)"
fi

# Create data directories
mkdir -p data/db data/images data/json-schema data/backups logs

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run ./scripts/dev.sh to start development servers"

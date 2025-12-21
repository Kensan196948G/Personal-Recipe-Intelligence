#!/bin/bash
# Database setup script for Personal Recipe Intelligence

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Personal Recipe Intelligence - Database Setup"
echo "========================================="

# Check Python version
echo ""
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q sqlalchemy alembic pytest

# Create data directory
echo ""
echo "Creating data directory..."
mkdir -p data
mkdir -p data/backups

# Initialize Alembic (if not already initialized)
if [ ! -d "migrations/versions" ]; then
    echo ""
    echo "Initializing Alembic migrations directory..."
    mkdir -p migrations/versions
fi

# Run migrations
echo ""
echo "Running database migrations..."
chmod +x migrate.sh
./migrate.sh

# Check indexes
echo ""
echo "Checking database indexes..."
python check_indexes.py

# Run performance tests
echo ""
echo "Running performance tests..."
pytest tests/test_performance.py -v -s

echo ""
echo "========================================="
echo "Database setup complete!"
echo "========================================="
echo ""
echo "Database location: $SCRIPT_DIR/data/recipes.db"
echo ""
echo "Next steps:"
echo "  1. Check indexes: python check_indexes.py"
echo "  2. Run tests: pytest tests/test_performance.py -v"
echo "  3. Start using the database!"
echo ""

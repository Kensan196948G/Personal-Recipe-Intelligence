#!/bin/bash
# Migration script for Personal Recipe Intelligence database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Personal Recipe Intelligence - Database Migration"
echo "========================================="

# Ensure data directory exists
mkdir -p data

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "Error: Alembic is not installed. Please run 'pip install alembic'"
    exit 1
fi

# Show current migration status
echo ""
echo "Current migration status:"
alembic current

# Show pending migrations
echo ""
echo "Pending migrations:"
alembic history

# Apply migrations
echo ""
echo "Applying migrations..."
alembic upgrade head

# Show final status
echo ""
echo "Migration complete. Current status:"
alembic current

echo ""
echo "========================================="
echo "Migration completed successfully!"
echo "========================================="

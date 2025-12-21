#!/bin/bash
# Initialize collection data directory and create default collections

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_ROOT/data"
COLLECTIONS_DIR="$DATA_DIR/collections"

echo "=== Collection Initialization ==="
echo ""

# Create directories
echo "Creating directories..."
mkdir -p "$COLLECTIONS_DIR"
mkdir -p "$DATA_DIR/backups"

# Create empty collections file if not exists
COLLECTIONS_FILE="$COLLECTIONS_DIR/collections.json"
if [ ! -f "$COLLECTIONS_FILE" ]; then
  echo "Creating collections.json..."
  echo "[]" > "$COLLECTIONS_FILE"
  echo "Created: $COLLECTIONS_FILE"
else
  echo "Collections file already exists: $COLLECTIONS_FILE"
fi

# Set permissions
chmod 755 "$COLLECTIONS_DIR"
chmod 644 "$COLLECTIONS_FILE"

echo ""
echo "=== Initialization Complete ==="
echo ""
echo "Collection data directory: $COLLECTIONS_DIR"
echo "Collections file: $COLLECTIONS_FILE"
echo ""
echo "You can now use the collection service."
echo ""

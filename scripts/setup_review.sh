#!/bin/bash
# Setup script for review feature
# レビュー機能のセットアップスクリプト

set -e

echo "=== Personal Recipe Intelligence - Review Feature Setup ==="
echo ""

# カレントディレクトリの確認
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"
echo ""

# 1. データディレクトリの作成
echo "1. Creating data directories..."
mkdir -p data/reviews
mkdir -p logs
echo "   ✓ data/reviews created"
echo "   ✓ logs created"
echo ""

# 2. 権限の設定
echo "2. Setting permissions..."
chmod 755 data/reviews
chmod 755 logs
echo "   ✓ Permissions set"
echo ""

# 3. Python依存関係のチェック
echo "3. Checking Python dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
  echo "   ! FastAPI not found, installing..."
  pip install fastapi uvicorn[standard]
fi

if ! python3 -c "import pydantic" 2>/dev/null; then
  echo "   ! Pydantic not found, installing..."
  pip install pydantic
fi

if ! python3 -c "import pytest" 2>/dev/null; then
  echo "   ! pytest not found, installing..."
  pip install pytest pytest-cov
fi

echo "   ✓ All dependencies installed"
echo ""

# 4. ディレクトリ構造の確認
echo "4. Verifying directory structure..."
REQUIRED_DIRS=(
  "backend/models"
  "backend/services"
  "backend/api/routers"
  "backend/tests"
  "frontend/components"
  "frontend/examples"
  "docs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "   ! Creating missing directory: $dir"
    mkdir -p "$dir"
  fi
done

echo "   ✓ Directory structure verified"
echo ""

# 5. ファイルの存在確認
echo "5. Checking required files..."
REQUIRED_FILES=(
  "backend/models/review.py"
  "backend/services/review_service.py"
  "backend/api/routers/review.py"
  "backend/tests/test_review_service.py"
  "backend/tests/test_review_api.py"
  "frontend/components/RecipeReviews.jsx"
  "frontend/components/RecipeReviews.css"
)

ALL_EXISTS=true
for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "   ✓ $file"
  else
    echo "   ✗ $file (missing)"
    ALL_EXISTS=false
  fi
done

if [ "$ALL_EXISTS" = false ]; then
  echo ""
  echo "   ! Some files are missing. Please ensure all files are created."
  exit 1
fi

echo ""

# 6. テストの実行
echo "6. Running tests..."
if pytest backend/tests/test_review_service.py -v --tb=short; then
  echo "   ✓ Service tests passed"
else
  echo "   ✗ Service tests failed"
  exit 1
fi

if pytest backend/tests/test_review_api.py -v --tb=short; then
  echo "   ✓ API tests passed"
else
  echo "   ✗ API tests failed"
  exit 1
fi

echo ""

# 7. サンプルデータの作成（オプション）
echo "7. Creating sample data (optional)..."
read -p "   Create sample reviews? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
  python3 backend/examples/review_example.py
  echo "   ✓ Sample data created"
else
  echo "   ⊘ Skipped"
fi

echo ""

# 8. 設定の確認
echo "8. Configuration summary:"
echo "   Data directory: $PROJECT_ROOT/data/reviews"
echo "   Log directory: $PROJECT_ROOT/logs"
echo "   API endpoint: /api/v1/review"
echo "   Test coverage: $(pytest backend/tests/test_review_*.py --cov=backend.services.review_service --cov=backend.api.routers.review --cov-report=term-missing | grep TOTAL | awk '{print $4}')"
echo ""

# 9. 次のステップの表示
echo "=== Setup completed successfully! ==="
echo ""
echo "Next steps:"
echo "  1. Start the backend API:"
echo "     cd backend && uvicorn api.main:app --reload"
echo ""
echo "  2. Start the frontend (if using React):"
echo "     cd frontend && npm start"
echo ""
echo "  3. Access the API documentation:"
echo "     http://localhost:8000/docs"
echo ""
echo "  4. Run the example:"
echo "     python3 backend/examples/review_example.py"
echo ""
echo "  5. Read the documentation:"
echo "     cat docs/REVIEW_API.md"
echo "     cat docs/REVIEW_FEATURE.md"
echo ""

exit 0

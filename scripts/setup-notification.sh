#!/bin/bash
# Setup script for Push Notification feature
# プッシュ通知機能のセットアップスクリプト

set -e

echo "=========================================="
echo "  Push Notification Setup"
echo "=========================================="
echo ""

# プロジェクトルートディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 1. 依存パッケージのインストール
echo "Step 1: Installing dependencies..."
echo ""

# Python dependencies
if [ -f "backend/requirements-notification.txt" ]; then
  echo "Installing Python packages..."
  pip install -r backend/requirements-notification.txt
  echo "✓ Python packages installed"
else
  echo "⚠ Warning: backend/requirements-notification.txt not found"
fi

echo ""

# 2. VAPIDキーの生成
echo "Step 2: Generating VAPID keys..."
echo ""

if [ -f "config/vapid_private_key.pem" ]; then
  echo "⚠ VAPID keys already exist. Skipping generation."
  echo "  To regenerate, delete config/vapid_private_key.pem and run again."
else
  python scripts/generate_vapid_keys.py
  echo "✓ VAPID keys generated"
fi

echo ""

# 3. .envファイルの設定確認
echo "Step 3: Checking .env configuration..."
echo ""

if [ ! -f ".env" ]; then
  echo "Creating .env file from template..."
  if [ -f ".env.notification.example" ]; then
    cp .env.notification.example .env
    echo "✓ .env file created"
    echo "⚠ Please edit .env file and set VAPID_PUBLIC_KEY and VAPID_CLAIM_EMAIL"
  else
    echo "⚠ Warning: .env.notification.example not found"
  fi
else
  echo "✓ .env file exists"

  # 必要な環境変数が設定されているか確認
  if grep -q "VAPID_PUBLIC_KEY=" .env && grep -q "VAPID_CLAIM_EMAIL=" .env; then
    echo "✓ VAPID configuration found in .env"
  else
    echo "⚠ Warning: VAPID configuration not found in .env"
    echo "  Please add the following to .env:"
    echo ""
    cat .env.notification.example
    echo ""
  fi
fi

echo ""

# 4. .gitignoreの更新
echo "Step 4: Updating .gitignore..."
echo ""

if [ -f ".gitignore" ]; then
  if grep -q "vapid_private_key.pem" .gitignore; then
    echo "✓ .gitignore already contains vapid_private_key.pem"
  else
    echo "config/vapid_private_key.pem" >> .gitignore
    echo "✓ Added vapid_private_key.pem to .gitignore"
  fi
else
  echo "config/vapid_private_key.pem" > .gitignore
  echo "✓ Created .gitignore with vapid_private_key.pem"
fi

echo ""

# 5. 必要なディレクトリの作成
echo "Step 5: Creating required directories..."
echo ""

mkdir -p config
mkdir -p logs
mkdir -p frontend/js
mkdir -p frontend/components

echo "✓ Directories created"
echo ""

# 6. Service Workerの配置確認
echo "Step 6: Checking Service Worker..."
echo ""

if [ -f "frontend/service-worker.js" ]; then
  echo "✓ Service Worker found"
else
  echo "⚠ Warning: frontend/service-worker.js not found"
fi

echo ""

# 7. アイコンファイルの確認
echo "Step 7: Checking notification icons..."
echo ""

if [ ! -f "frontend/icon-192x192.png" ]; then
  echo "⚠ Warning: frontend/icon-192x192.png not found"
  echo "  Please create notification icon (192x192px)"
fi

if [ ! -f "frontend/badge-72x72.png" ]; then
  echo "⚠ Warning: frontend/badge-72x72.png not found"
  echo "  Please create notification badge (72x72px)"
fi

echo ""

# 8. テストの実行（オプション）
echo "Step 8: Running tests (optional)..."
echo ""

read -p "Run tests now? (y/N): " run_tests

if [[ "$run_tests" =~ ^[Yy]$ ]]; then
  echo "Running backend tests..."
  if [ -d "tests" ]; then
    pytest tests/test_notification_service.py -v || true
    pytest tests/test_notification_api.py -v || true
  fi

  echo "Running frontend tests..."
  if [ -d "frontend/tests" ]; then
    cd frontend
    bun test tests/notification-manager.test.js || true
    cd ..
  fi
else
  echo "Skipped tests"
fi

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and set VAPID_PUBLIC_KEY and VAPID_CLAIM_EMAIL"
echo "2. Create notification icons (192x192px and 72x72px)"
echo "3. Start the backend API server"
echo "4. Serve the frontend application"
echo "5. Test push notifications in your browser"
echo ""
echo "For detailed instructions, see:"
echo "  docs/NOTIFICATION_SETUP.md"
echo ""

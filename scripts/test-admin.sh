#!/bin/bash
# 管理者ダッシュボードの統合テストスクリプト

set -e

echo "=========================================="
echo "管理者ダッシュボード 統合テスト"
echo "=========================================="

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# .env から管理者APIキーを読み込み
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "エラー: .env ファイルが見つかりません。"
  exit 1
fi

if [ -z "$ADMIN_API_KEY" ]; then
  echo "エラー: ADMIN_API_KEY が設定されていません。"
  exit 1
fi

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

echo "API Base URL: $API_BASE_URL"
echo "管理者APIキー: ${ADMIN_API_KEY:0:10}..."
echo ""

# バックエンドが起動しているか確認
echo "バックエンドの起動確認中..."
if ! curl -s -f "$API_BASE_URL/health" > /dev/null 2>&1; then
  echo "エラー: バックエンドが起動していません。"
  echo "先に 'cd backend && python -m uvicorn main:app' を実行してください。"
  exit 1
fi
echo "✓ バックエンドが起動しています"
echo ""

# テスト関数
test_endpoint() {
  local name=$1
  local method=$2
  local endpoint=$3
  local data=$4

  echo "テスト: $name"

  if [ "$method" = "GET" ]; then
    response=$(curl -s -w "\n%{http_code}" -X GET \
      -H "Authorization: Bearer $ADMIN_API_KEY" \
      "$API_BASE_URL$endpoint")
  elif [ "$method" = "POST" ]; then
    response=$(curl -s -w "\n%{http_code}" -X POST \
      -H "Authorization: Bearer $ADMIN_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$API_BASE_URL$endpoint")
  elif [ "$method" = "PUT" ]; then
    response=$(curl -s -w "\n%{http_code}" -X PUT \
      -H "Authorization: Bearer $ADMIN_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$API_BASE_URL$endpoint")
  fi

  http_code=$(echo "$response" | tail -n 1)
  body=$(echo "$response" | sed '$d')

  if [ "$http_code" = "200" ]; then
    echo "✓ 成功 (HTTP $http_code)"
    # JSONを整形して表示
    if command -v jq &> /dev/null; then
      echo "$body" | jq -C '.' | head -n 10
    else
      echo "$body" | head -c 200
    fi
  else
    echo "✗ 失敗 (HTTP $http_code)"
    echo "$body"
    return 1
  fi

  echo ""
}

# テスト実行
echo "=========================================="
echo "APIエンドポイントテスト"
echo "=========================================="
echo ""

# 1. システム統計
test_endpoint "システム統計取得" "GET" "/api/v1/admin/stats"

# 2. レシピ統計
test_endpoint "レシピ統計取得 (30日)" "GET" "/api/v1/admin/stats/recipes?days=30"

# 3. ユーザー統計
test_endpoint "ユーザー統計取得 (30日)" "GET" "/api/v1/admin/stats/users?days=30"

# 4. 設定取得
test_endpoint "システム設定取得" "GET" "/api/v1/admin/settings"

# 5. 設定更新
test_endpoint "システム設定更新" "PUT" "/api/v1/admin/settings" \
  '{"site_name": "Test Site", "maintenance_mode": false}'

# 6. ログ取得
test_endpoint "システムログ取得" "GET" "/api/v1/admin/logs?limit=10"

# 7. ヘルスチェック
test_endpoint "ヘルスチェック" "GET" "/api/v1/admin/health"

# 8. キャッシュクリア
test_endpoint "キャッシュクリア" "POST" "/api/v1/admin/cache/clear"

# 認証エラーテスト
echo "=========================================="
echo "認証エラーテスト"
echo "=========================================="
echo ""

echo "テスト: 無効なトークンでのアクセス"
response=$(curl -s -w "\n%{http_code}" -X GET \
  -H "Authorization: Bearer invalid_token" \
  "$API_BASE_URL/api/v1/admin/stats")

http_code=$(echo "$response" | tail -n 1)

if [ "$http_code" = "401" ]; then
  echo "✓ 正しく認証エラーが返されました (HTTP $http_code)"
else
  echo "✗ 予期しないレスポンス (HTTP $http_code)"
fi
echo ""

# Pytestテスト実行
echo "=========================================="
echo "Pytestテスト実行"
echo "=========================================="
echo ""

cd backend
if [ -f tests/test_admin_service.py ]; then
  echo "管理者サービスのユニットテストを実行中..."
  python -m pytest tests/test_admin_service.py -v --tb=short
  echo ""
else
  echo "警告: tests/test_admin_service.py が見つかりません。"
fi
cd ..

# 結果サマリー
echo "=========================================="
echo "テスト完了"
echo "=========================================="
echo ""
echo "すべてのテストが完了しました。"
echo ""
echo "次のステップ:"
echo "1. フロントエンドを起動して手動テスト:"
echo "   cd frontend && npm start"
echo ""
echo "2. ブラウザで http://localhost:3000/admin にアクセス"
echo ""
echo "3. 管理者APIキーでログイン"
echo ""

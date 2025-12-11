#!/bin/bash

###############################################################################
# E2E テスト実行スクリプト（SSH + Ubuntu CLI 環境対応）
# Personal Recipe Intelligence - Playwright E2E Tests
###############################################################################

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# プロジェクトルートディレクトリ
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
BACKEND_DIR="${PROJECT_ROOT}/backend"

# デフォルト設定
BROWSER="${1:-chromium}"
HEADED="${2:-false}"
BACKEND_PORT=8000
FRONTEND_PORT=5173

log_info "E2E テスト環境のセットアップを開始します"
log_info "ブラウザ: ${BROWSER}"
log_info "ヘッドレスモード: $([ "$HEADED" = "true" ] && echo "無効" || echo "有効")"

# 前提条件チェック
log_info "前提条件をチェックしています..."

if ! command -v bun &> /dev/null; then
  log_error "Bun がインストールされていません"
  exit 1
fi

if ! command -v python3 &> /dev/null; then
  log_error "Python3 がインストールされていません"
  exit 1
fi

log_success "前提条件チェック完了"

# フロントエンド依存関係インストール
log_info "フロントエンド依存関係をインストールしています..."
cd "${FRONTEND_DIR}"

if [ ! -d "node_modules" ] || [ ! -d "node_modules/@playwright" ]; then
  bun install
  log_info "Playwright ブラウザをインストールしています..."
  bunx playwright install --with-deps "${BROWSER}"
fi

log_success "フロントエンド依存関係インストール完了"

# バックエンド依存関係インストール
log_info "バックエンド依存関係をインストールしています..."
cd "${BACKEND_DIR}"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

log_success "バックエンド依存関係インストール完了"

# バックエンドサーバー起動
log_info "バックエンドサーバーを起動しています..."
export PYTHONUNBUFFERED=1
export DATABASE_URL="sqlite:///./test_e2e.db"

# 既存のテストDBを削除
rm -f test_e2e.db

# バックエンドサーバーをバックグラウンドで起動
python -m uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT} > "${PROJECT_ROOT}/logs/backend-e2e.log" 2>&1 &
BACKEND_PID=$!

log_info "バックエンドサーバーPID: ${BACKEND_PID}"

# バックエンドサーバーの起動待機
log_info "バックエンドサーバーの起動を待機しています..."
TIMEOUT=30
ELAPSED=0

while ! curl -f http://localhost:${BACKEND_PORT}/health &> /dev/null; do
  if [ ${ELAPSED} -ge ${TIMEOUT} ]; then
    log_error "バックエンドサーバーの起動がタイムアウトしました"
    kill ${BACKEND_PID} 2>/dev/null || true
    exit 1
  fi
  sleep 1
  ELAPSED=$((ELAPSED + 1))
done

log_success "バックエンドサーバー起動完了 (http://localhost:${BACKEND_PORT})"

# クリーンアップ関数
cleanup() {
  log_info "クリーンアップを実行しています..."

  # バックエンドサーバー停止
  if [ -n "${BACKEND_PID}" ]; then
    log_info "バックエンドサーバーを停止しています (PID: ${BACKEND_PID})..."
    kill ${BACKEND_PID} 2>/dev/null || true
    wait ${BACKEND_PID} 2>/dev/null || true
  fi

  # フロントエンドサーバー停止（Playwright が自動管理）

  log_success "クリーンアップ完了"
}

# 終了時にクリーンアップを実行
trap cleanup EXIT INT TERM

# E2E テスト実行
log_info "E2E テストを実行しています..."
cd "${FRONTEND_DIR}"

export CI=true
export BASE_URL="http://localhost:${FRONTEND_PORT}"

if [ "${HEADED}" = "true" ]; then
  # ヘッド付きモード（GUIが必要）
  bun run e2e:headed --project="${BROWSER}"
else
  # ヘッドレスモード（SSH環境推奨）
  bun run e2e --project="${BROWSER}"
fi

TEST_EXIT_CODE=$?

# テスト結果の表示
if [ ${TEST_EXIT_CODE} -eq 0 ]; then
  log_success "E2E テストがすべて成功しました！"

  # レポート生成
  log_info "テストレポートを生成しています..."
  if [ -d "playwright-report" ]; then
    log_info "テストレポート: ${FRONTEND_DIR}/playwright-report/index.html"
    log_info "レポートを表示するには: bun run e2e:report"
  fi
else
  log_error "E2E テストが失敗しました (終了コード: ${TEST_EXIT_CODE})"

  # 失敗時の情報
  if [ -d "test-results" ]; then
    log_warn "スクリーンショット・動画: ${FRONTEND_DIR}/test-results/"
  fi
fi

exit ${TEST_EXIT_CODE}

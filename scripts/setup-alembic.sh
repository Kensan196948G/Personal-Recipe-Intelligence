#!/bin/bash

# ========================================
# Personal Recipe Intelligence
# Alembic Migration Setup Script
# ========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="${PROJECT_ROOT}/.venv"
DATA_DIR="${PROJECT_ROOT}/data"
ALEMBIC_DIR="${PROJECT_ROOT}/alembic"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Alembic Migration Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function: Check command exists
command_exists() {
  command -v "$1" &> /dev/null
}

# Function: Print status
print_status() {
  local status=$1
  local message=$2

  case $status in
    "success")
      echo -e "${GREEN}✓${NC} $message"
      ;;
    "error")
      echo -e "${RED}✗${NC} $message"
      ;;
    "warning")
      echo -e "${YELLOW}⚠${NC} $message"
      ;;
    "info")
      echo -e "${BLUE}ℹ${NC} $message"
      ;;
  esac
}

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/6] 前提条件の確認${NC}"
echo ""

if ! command_exists python3; then
  print_status "error" "Python 3 がインストールされていません"
  exit 1
fi
print_status "success" "Python 3: $(python3 --version)"

if ! command_exists git; then
  print_status "warning" "Git がインストールされていません（推奨）"
else
  print_status "success" "Git: $(git --version)"
fi

echo ""

# Step 2: Check python3-venv
echo -e "${YELLOW}[2/6] python3-venv の確認${NC}"
echo ""

if python3 -m venv --help &> /dev/null; then
  print_status "success" "python3-venv は利用可能です"
else
  print_status "error" "python3-venv がインストールされていません"
  echo ""
  echo -e "${YELLOW}以下のコマンドでインストールしてください:${NC}"
  echo -e "  ${BLUE}sudo apt update${NC}"
  echo -e "  ${BLUE}sudo apt install python3.12-venv${NC}"
  echo ""
  read -p "今すぐインストールしますか? (y/N): " response
  if [[ "$response" =~ ^[Yy]$ ]]; then
    sudo apt update
    sudo apt install python3.12-venv
    print_status "success" "python3-venv をインストールしました"
  else
    print_status "error" "python3-venv なしでは続行できません"
    exit 1
  fi
fi

echo ""

# Step 3: Create/activate virtual environment
echo -e "${YELLOW}[3/6] 仮想環境のセットアップ${NC}"
echo ""

if [ -d "$VENV_DIR" ]; then
  print_status "info" "仮想環境は既に存在します: $VENV_DIR"
else
  print_status "info" "仮想環境を作成中: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
  print_status "success" "仮想環境を作成しました"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
print_status "success" "仮想環境を有効化しました"

echo ""

# Step 4: Install dependencies
echo -e "${YELLOW}[4/6] 依存パッケージのインストール${NC}"
echo ""

print_status "info" "pip を最新版にアップグレード中..."
pip install --upgrade pip --quiet

if [ -f "${PROJECT_ROOT}/backend/requirements.txt" ]; then
  print_status "info" "backend/requirements.txt からインストール中..."
  pip install -r "${PROJECT_ROOT}/backend/requirements.txt" --quiet
  print_status "success" "依存パッケージをインストールしました"
else
  print_status "warning" "requirements.txt が見つかりません"
  print_status "info" "alembicのみをインストールします"
  pip install alembic>=1.13.0 sqlmodel fastapi --quiet
  print_status "success" "最小限のパッケージをインストールしました"
fi

# Verify alembic installation
if python -c "import alembic" &> /dev/null; then
  ALEMBIC_VERSION=$(python -c "import alembic; print(alembic.__version__)")
  print_status "success" "Alembic ${ALEMBIC_VERSION} がインストールされています"
else
  print_status "error" "Alembic のインストールに失敗しました"
  exit 1
fi

echo ""

# Step 5: Check Alembic configuration
echo -e "${YELLOW}[5/6] Alembic設定の確認${NC}"
echo ""

if [ -f "${PROJECT_ROOT}/alembic.ini" ]; then
  print_status "success" "alembic.ini が存在します"
else
  print_status "error" "alembic.ini が見つかりません"
  exit 1
fi

if [ -d "$ALEMBIC_DIR" ]; then
  print_status "success" "alembic/ ディレクトリが存在します"
else
  print_status "error" "alembic/ ディレクトリが見つかりません"
  exit 1
fi

if [ -d "${ALEMBIC_DIR}/versions" ]; then
  VERSION_COUNT=$(ls -1 "${ALEMBIC_DIR}/versions"/*.py 2>/dev/null | wc -l)
  print_status "success" "マイグレーションファイル: ${VERSION_COUNT}件"
else
  print_status "warning" "versions/ ディレクトリが見つかりません"
fi

# Create data directory if not exists
if [ ! -d "$DATA_DIR" ]; then
  mkdir -p "$DATA_DIR"
  print_status "success" "data/ ディレクトリを作成しました"
fi

echo ""

# Step 6: Check migration status
echo -e "${YELLOW}[6/6] マイグレーション状態の確認${NC}"
echo ""

cd "$PROJECT_ROOT"

print_status "info" "現在のマイグレーションバージョンを確認中..."
if alembic current &> /dev/null; then
  CURRENT_VERSION=$(alembic current 2>/dev/null | head -1)
  if [ -n "$CURRENT_VERSION" ]; then
    print_status "success" "現在のバージョン: $CURRENT_VERSION"
  else
    print_status "warning" "データベースにマイグレーション履歴がありません"
    echo ""
    read -p "初期マイグレーションを適用しますか? (y/N): " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
      print_status "info" "マイグレーションを実行中..."
      alembic upgrade head
      print_status "success" "マイグレーションを適用しました"
    else
      print_status "info" "後で 'alembic upgrade head' を実行してください"
    fi
  fi
else
  print_status "warning" "マイグレーション状態を確認できませんでした"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  セットアップ完了！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}次のステップ:${NC}"
echo ""
echo -e "  1. 仮想環境を有効化:"
echo -e "     ${YELLOW}source .venv/bin/activate${NC}"
echo ""
echo -e "  2. マイグレーション状態を確認:"
echo -e "     ${YELLOW}alembic current${NC}"
echo ""
echo -e "  3. マイグレーション履歴を表示:"
echo -e "     ${YELLOW}alembic history${NC}"
echo ""
echo -e "  4. 最新版まで適用:"
echo -e "     ${YELLOW}alembic upgrade head${NC}"
echo ""
echo -e "${BLUE}詳細なドキュメント:${NC}"
echo -e "  docs/04_データベース(database)/マイグレーション運用ガイド(migration-guide).md"
echo ""

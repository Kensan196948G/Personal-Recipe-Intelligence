#!/bin/bash
# Video Module セットアップスクリプト
# YouTube動画レシピ抽出モジュールの依存パッケージをインストール

set -e

echo "=========================================="
echo "Video Module Setup"
echo "=========================================="

# カレントディレクトリ確認
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Project Root: $PROJECT_ROOT"

# Python仮想環境の確認
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Warning: Python仮想環境が有効化されていません"
  echo "仮想環境を有効化してから実行してください:"
  echo "  source venv/bin/activate"
  exit 1
fi

echo "Python仮想環境: $VIRTUAL_ENV"

# 依存パッケージインストール
echo ""
echo "依存パッケージをインストール中..."
pip install -r "$SCRIPT_DIR/requirements-video.txt"

echo ""
echo "=========================================="
echo "Setup完了"
echo "=========================================="
echo ""
echo "テスト実行コマンド:"
echo "  pytest backend/video/tests/ -v"
echo ""
echo "API起動コマンド（例）:"
echo "  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
echo ""

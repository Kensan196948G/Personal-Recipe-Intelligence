#!/bin/bash

# レポート機能セットアップスクリプト
# Personal Recipe Intelligence - Phase 10-4

set -e

PROJECT_ROOT="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
cd "$PROJECT_ROOT"

echo "========================================"
echo "レポート機能セットアップ"
echo "========================================"

# 1. Python 依存関係インストール
echo ""
echo "[1] Python 依存関係インストール..."
cd backend
pip install reportlab==4.0.9
echo "✓ reportlab インストール完了"

# 2. 日本語フォント確認
echo ""
echo "[2] 日本語フォント確認..."
if fc-list | grep -qi "noto"; then
  echo "✓ 日本語フォント（Noto）が見つかりました"
else
  echo "⚠ 日本語フォントが見つかりません"
  echo "  以下のコマンドでインストールしてください:"
  echo "  sudo apt-get update"
  echo "  sudo apt-get install fonts-noto-cjk"
fi

# 3. ディレクトリ作成
echo ""
echo "[3] ディレクトリ作成..."
mkdir -p "$PROJECT_ROOT/data/reports"
mkdir -p "$PROJECT_ROOT/backend/examples"
mkdir -p "$PROJECT_ROOT/frontend/components"
echo "✓ ディレクトリ作成完了"

# 4. テスト実行
echo ""
echo "[4] テスト実行..."
cd "$PROJECT_ROOT/backend"

if [ -f "tests/test_report_service.py" ]; then
  echo "レポートサービステストを実行..."
  pytest tests/test_report_service.py -v --tb=short || {
    echo "⚠ テストに失敗しました（セットアップは続行）"
  }
else
  echo "⚠ テストファイルが見つかりません"
fi

# 5. サンプル実行
echo ""
echo "[5] サンプル実行..."
if [ -f "examples/report_example.py" ]; then
  echo "レポート生成サンプルを実行..."
  python3 examples/report_example.py || {
    echo "⚠ サンプル実行に失敗しました"
  }
else
  echo "⚠ サンプルファイルが見つかりません"
fi

# 6. 完了メッセージ
echo ""
echo "========================================"
echo "セットアップ完了！"
echo "========================================"
echo ""
echo "次のステップ:"
echo "  1. API サーバーを起動:"
echo "     cd $PROJECT_ROOT/backend"
echo "     uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  2. フロントエンドを起動:"
echo "     cd $PROJECT_ROOT/frontend"
echo "     npm start"
echo ""
echo "  3. レポート生成API にアクセス:"
echo "     http://localhost:8000/api/v1/report/weekly?user_id=user_001"
echo ""
echo "  4. API ドキュメント:"
echo "     http://localhost:8000/docs"
echo ""
echo "詳細は docs/REPORT_SETUP.md を参照してください"
echo ""

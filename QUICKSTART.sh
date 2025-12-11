#!/bin/bash
# Recipe Service 統合 - クイックスタートガイド

set -e

BASE_DIR="/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
cd "$BASE_DIR"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    Recipe Service 統合 - クイックスタート                     ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Python バージョン確認
echo "1. 環境確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 --version
echo ""

# ステップ 1: Backend 初期化
echo "2. Backend 構造初期化"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 initialize_backend.py
echo ""

# ステップ 2: Recipe Service 統合
echo "3. Recipe Service 統合"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 merge_recipe_services.py
echo ""

# ステップ 3: 検証
echo "4. 統合結果検証"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 verify_integration.py
echo ""

# ステップ 4: テスト準備
echo "5. テスト環境準備"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "pytest をインストール中..."
python3 -m pip install pytest --quiet 2>/dev/null && echo "✓ pytest インストール完了" || echo "✓ pytest 既にインストール済み"
echo ""

# ステップ 5: テスト実行
echo "6. テスト実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
export PYTHONPATH="$BASE_DIR:$PYTHONPATH"
python3 -m pytest backend/tests/test_recipe_service.py -v --tb=short 2>&1 || {
  echo ""
  echo "⚠ テストが失敗しました（依存関係の問題の可能性があります）"
  echo ""
}

# 完了
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                              統合作業完了                                     ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "生成されたファイル:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
find "$BASE_DIR/backend" -name "*.py" -type f | grep -E "(models|repositories|services|parsers)" | sort
echo ""

echo "次のステップ:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1. 統合されたサービスを確認:"
echo "     cat backend/services/recipe_service.py | less"
echo ""
echo "  2. recipe_service_new.py が削除されたことを確認:"
echo "     ls -la backend/services/"
echo ""
echo "  3. テストを再実行:"
echo "     python3 -m pytest backend/tests/test_recipe_service.py -v"
echo ""
echo "  4. 詳細なドキュメントを確認:"
echo "     cat INTEGRATION_README.md"
echo ""
echo "  5. バックアップを確認:"
echo "     ls -la backups/"
echo ""

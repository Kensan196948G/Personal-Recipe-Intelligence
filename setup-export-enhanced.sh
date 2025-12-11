#!/bin/bash
# エクスポート強化機能セットアップスクリプト

set -e

echo "=========================================="
echo "Personal Recipe Intelligence"
echo "エクスポート強化機能セットアップ"
echo "=========================================="
echo ""

# 必要なディレクトリ作成
echo "1. ディレクトリ作成..."
mkdir -p data/exports
mkdir -p data/backups
echo "  ✓ data/exports"
echo "  ✓ data/backups"
echo ""

# 日本語フォントのインストール確認
echo "2. 日本語フォント確認..."
FONT_INSTALLED=false

if fc-list | grep -qi "noto.*cjk"; then
  echo "  ✓ Noto Sans CJK がインストール済み"
  FONT_INSTALLED=true
elif fc-list | grep -qi "ipa.*gothic"; then
  echo "  ✓ IPAゴシック がインストール済み"
  FONT_INSTALLED=true
fi

if [ "$FONT_INSTALLED" = false ]; then
  echo "  ⚠ 日本語フォントが見つかりません"
  echo ""
  echo "  PDF生成に日本語フォントが必要です。以下のコマンドでインストールしてください："
  echo ""
  echo "    sudo apt-get update"
  echo "    sudo apt-get install -y fonts-noto-cjk fonts-ipafont-gothic"
  echo ""
  read -p "  今すぐインストールしますか？ (y/N): " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  フォントをインストール中..."
    sudo apt-get update
    sudo apt-get install -y fonts-noto-cjk fonts-ipafont-gothic
    echo "  ✓ フォントのインストールが完了しました"
  else
    echo "  ⚠ スキップしました（PDF生成時に日本語が正しく表示されない可能性があります）"
  fi
fi
echo ""

# Python依存関係のインストール
echo "3. Python依存関係インストール..."
if [ ! -f "requirements.txt" ]; then
  echo "  ⚠ requirements.txt が見つかりません"
  echo ""
  echo "  以下のパッケージを手動でインストールしてください："
  echo "    pip install reportlab fastapi pydantic"
else
  echo "  reportlab をインストール中..."
  pip install reportlab
  echo "  ✓ reportlab のインストールが完了しました"
fi
echo ""

# テストデータの作成
echo "4. テストデータ作成..."
cat > data/recipes.json <<'EOF'
[
  {
    "id": "recipe-001",
    "title": "カレーライス",
    "description": "スパイシーな本格カレー",
    "cooking_time_minutes": 45,
    "servings": 4,
    "category": "main",
    "tags": ["カレー", "スパイス"],
    "ingredients": [
      {"name": "玉ねぎ", "amount": "2", "unit": "個"},
      {"name": "じゃがいも", "amount": "3", "unit": "個"},
      {"name": "にんじん", "amount": "1", "unit": "本"},
      {"name": "豚肉", "amount": "300", "unit": "g"}
    ],
    "steps": [
      "野菜を一口大に切る",
      "肉を炒める",
      "野菜を加えて炒める",
      "水を加えて煮込む",
      "カレールーを入れて完成"
    ],
    "created_at": "2025-01-01T10:00:00",
    "nutrition": {
      "calories": 550,
      "protein": 25,
      "fat": 18,
      "carbohydrates": 65
    }
  },
  {
    "id": "recipe-002",
    "title": "パスタカルボナーラ",
    "description": "クリーミーなカルボナーラ",
    "cooking_time_minutes": 20,
    "servings": 2,
    "category": "main",
    "tags": ["パスタ", "イタリアン"],
    "ingredients": [
      {"name": "パスタ", "amount": "200", "unit": "g"},
      {"name": "ベーコン", "amount": "100", "unit": "g"},
      {"name": "卵", "amount": "2", "unit": "個"},
      {"name": "粉チーズ", "amount": "50", "unit": "g"}
    ],
    "steps": [
      "パスタを茹でる",
      "ベーコンを炒める",
      "卵と粉チーズを混ぜる",
      "パスタとベーコンを合わせる",
      "卵液を絡めて完成"
    ],
    "created_at": "2025-01-02T12:00:00",
    "nutrition": {
      "calories": 680,
      "protein": 30,
      "fat": 28,
      "carbohydrates": 75
    }
  }
]
EOF
echo "  ✓ テストレシピデータを作成しました"
echo ""

# APIルーターの登録確認
echo "5. APIルーター登録確認..."
if [ -f "backend/api/main.py" ]; then
  if grep -q "export_enhanced" backend/api/main.py; then
    echo "  ✓ エクスポート強化ルーターは既に登録済みです"
  else
    echo "  ⚠ backend/api/main.py にルーターを登録してください："
    echo ""
    echo "    from backend.api.routers import export_enhanced"
    echo "    app.include_router(export_enhanced.router)"
    echo ""
  fi
else
  echo "  ⚠ backend/api/main.py が見つかりません"
fi
echo ""

# テスト実行
echo "6. テスト実行..."
if command -v pytest &> /dev/null; then
  echo "  テストを実行中..."
  if pytest backend/tests/test_export_enhanced_service.py -v; then
    echo "  ✓ すべてのテストが成功しました"
  else
    echo "  ⚠ 一部のテストが失敗しました"
  fi
else
  echo "  ⚠ pytest がインストールされていません"
  echo "    pip install pytest でインストールしてください"
fi
echo ""

# 完了メッセージ
echo "=========================================="
echo "セットアップが完了しました！"
echo "=========================================="
echo ""
echo "使い方："
echo ""
echo "1. APIサーバーを起動："
echo "   cd backend && uvicorn api.main:app --reload"
echo ""
echo "2. エクスポート実行例："
echo ""
echo "   # JSON形式でエクスポート"
echo "   curl -X POST http://localhost:8000/api/v1/export/recipes \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"recipe_ids\": [\"recipe-001\"], \"format\": \"json\"}' \\"
echo "     -o recipes.json"
echo ""
echo "   # レシピブック生成"
echo "   curl -X POST http://localhost:8000/api/v1/export/recipe-book \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"recipe_ids\": [\"recipe-001\", \"recipe-002\"], \"title\": \"私のレシピ\"}' \\"
echo "     -o recipe_book.pdf"
echo ""
echo "   # 買い物リスト生成"
echo "   curl -X POST http://localhost:8000/api/v1/export/shopping-list \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"recipe_ids\": [\"recipe-001\", \"recipe-002\"], \"format\": \"markdown\"}' \\"
echo "     -o shopping_list.md"
echo ""
echo "   # バックアップ作成"
echo "   curl -X POST http://localhost:8000/api/v1/export/backup \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"metadata\": {\"note\": \"定期バックアップ\"}}'  "
echo ""
echo "詳細は docs/export-enhanced-api.md を参照してください。"
echo ""

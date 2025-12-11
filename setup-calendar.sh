#!/bin/bash

# Personal Recipe Intelligence - カレンダー連携機能セットアップスクリプト

set -e

echo "=========================================="
echo "カレンダー連携機能のセットアップを開始"
echo "=========================================="

# 1. 必要なディレクトリの作成
echo ""
echo "[1/5] ディレクトリ構造を作成中..."
mkdir -p backend/api/routers
mkdir -p backend/services
mkdir -p backend/tests
mkdir -p frontend/components
mkdir -p data
mkdir -p docs

# __init__.py ファイルの作成
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/api/routers/__init__.py
touch backend/services/__init__.py
touch backend/tests/__init__.py

echo "  ✓ ディレクトリ構造を作成しました"

# 2. Python 依存関係のインストール
echo ""
echo "[2/5] Python 依存関係をインストール中..."
if [ -f "requirements.txt" ]; then
  pip install icalendar python-dateutil --quiet
  echo "  ✓ icalendar と python-dateutil をインストールしました"
else
  echo "  ! requirements.txt が見つかりません。手動でインストールしてください："
  echo "    pip install icalendar python-dateutil"
fi

# 3. データディレクトリの初期化
echo ""
echo "[3/5] データディレクトリを初期化中..."
if [ ! -f "data/meal_plans.json" ]; then
  echo "[]" > data/meal_plans.json
  echo "  ✓ data/meal_plans.json を作成しました"
else
  echo "  ✓ data/meal_plans.json は既に存在します"
fi

# レシピサンプルデータの作成（存在しない場合のみ）
if [ ! -f "data/recipes.json" ]; then
  cat > data/recipes.json << 'EOF'
[
  {
    "id": 1,
    "name": "カレーライス",
    "servings": 4,
    "ingredients": [
      {"name": "玉ねぎ", "quantity": 2, "unit": "個", "category": "野菜"},
      {"name": "じゃがいも", "quantity": 3, "unit": "個", "category": "野菜"},
      {"name": "にんじん", "quantity": 1, "unit": "本", "category": "野菜"},
      {"name": "豚肉", "quantity": 300, "unit": "g", "category": "肉"},
      {"name": "カレールー", "quantity": 1, "unit": "箱", "category": "調味料"}
    ],
    "nutrition": {
      "calories": 800,
      "protein": 30,
      "fat": 25,
      "carbs": 100,
      "fiber": 5,
      "salt": 2
    }
  },
  {
    "id": 2,
    "name": "ハンバーグ",
    "servings": 2,
    "ingredients": [
      {"name": "牛ひき肉", "quantity": 300, "unit": "g", "category": "肉"},
      {"name": "玉ねぎ", "quantity": 1, "unit": "個", "category": "野菜"},
      {"name": "卵", "quantity": 1, "unit": "個", "category": "卵"},
      {"name": "パン粉", "quantity": 50, "unit": "g", "category": "その他"}
    ],
    "nutrition": {
      "calories": 600,
      "protein": 40,
      "fat": 35,
      "carbs": 20,
      "fiber": 2,
      "salt": 1.5
    }
  },
  {
    "id": 3,
    "name": "野菜炒め",
    "servings": 2,
    "ingredients": [
      {"name": "キャベツ", "quantity": 0.25, "unit": "玉", "category": "野菜"},
      {"name": "もやし", "quantity": 1, "unit": "袋", "category": "野菜"},
      {"name": "豚バラ肉", "quantity": 150, "unit": "g", "category": "肉"},
      {"name": "しょうゆ", "quantity": 15, "unit": "ml", "category": "調味料"}
    ],
    "nutrition": {
      "calories": 350,
      "protein": 20,
      "fat": 15,
      "carbs": 25,
      "fiber": 4,
      "salt": 2.5
    }
  }
]
EOF
  echo "  ✓ サンプルレシピデータを作成しました"
else
  echo "  ✓ data/recipes.json は既に存在します"
fi

# 4. テストの実行
echo ""
echo "[4/5] テストを実行中..."
if command -v pytest &> /dev/null; then
  if [ -f "backend/tests/test_calendar_service.py" ]; then
    pytest backend/tests/test_calendar_service.py -v --tb=short || echo "  ! 一部のテストが失敗しました"
    pytest backend/tests/test_meal_plan_service.py -v --tb=short || echo "  ! 一部のテストが失敗しました"
  else
    echo "  ! テストファイルが見つかりません"
  fi
else
  echo "  ! pytest がインストールされていません。テストをスキップします"
  echo "    インストール: pip install pytest pytest-asyncio"
fi

# 5. セットアップ完了
echo ""
echo "=========================================="
echo "セットアップが完了しました！"
echo "=========================================="
echo ""
echo "次のステップ:"
echo ""
echo "1. API サーバーを起動:"
echo "   uvicorn backend.main:app --reload"
echo ""
echo "2. フロントエンドを起動:"
echo "   cd frontend && npm run dev"
echo ""
echo "3. カレンダー機能にアクセス:"
echo "   http://localhost:3000/calendar"
echo ""
echo "4. API ドキュメント:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. テストを実行:"
echo "   pytest backend/tests/ -v"
echo ""
echo "詳細なドキュメント: docs/CALENDAR_INTEGRATION.md"
echo ""

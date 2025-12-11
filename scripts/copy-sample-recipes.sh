#!/bin/bash
# サンプルレシピデータをコピーするスクリプト

set -e

echo "================================"
echo "サンプルレシピデータのコピー"
echo "================================"
echo ""

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# プロジェクトルートの確認
if [ ! -f "CLAUDE.md" ]; then
  echo "エラー: プロジェクトルートで実行してください"
  exit 1
fi

# data ディレクトリの作成
mkdir -p data

# サンプルレシピファイルの存在確認
if [ ! -f "data/sample-recipes.json" ]; then
  echo -e "${YELLOW}⚠ data/sample-recipes.json が見つかりません${NC}"
  exit 1
fi

# recipes.json へコピー（バックアップを取る）
if [ -f "data/recipes.json" ]; then
  echo "既存の recipes.json が見つかりました"
  echo "バックアップを作成しますか？ (y/n)"
  read -r answer
  if [ "$answer" = "y" ]; then
    cp data/recipes.json "data/recipes.json.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✓ バックアップを作成しました${NC}"
  fi
fi

# サンプルをコピー
cp data/sample-recipes.json data/recipes.json
echo -e "${GREEN}✓ サンプルレシピを recipes.json にコピーしました${NC}"
echo ""

# レシピ数を表示
recipe_count=$(cat data/recipes.json | jq '.recipes | length')
echo "登録されたレシピ数: ${recipe_count}"
echo ""

echo -e "${GREEN}完了しました！${NC}"
echo ""
echo "次のステップ:"
echo "1. API サーバーを起動してください"
echo "2. 自然言語検索を試してください"
echo ""

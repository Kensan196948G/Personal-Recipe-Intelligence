#!/bin/bash
# 管理者ダッシュボードのセットアップスクリプト

set -e

echo "=========================================="
echo "管理者ダッシュボード セットアップ"
echo "=========================================="

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# データディレクトリ作成
echo "データディレクトリを作成中..."
mkdir -p data
mkdir -p logs

# .env ファイルのチェック
if [ ! -f .env ]; then
  echo "警告: .env ファイルが見つかりません。"
  echo ".env.example をコピーして .env を作成してください。"

  if [ -f .env.example ]; then
    echo ""
    read -p ".env.example から .env を作成しますか？ (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      cp .env.example .env
      echo ".env ファイルを作成しました。"
    fi
  fi
fi

# 管理者APIキーの設定チェック
if [ -f .env ]; then
  if grep -q "ADMIN_API_KEY=your_secure_admin_api_key_here" .env || ! grep -q "ADMIN_API_KEY=" .env; then
    echo ""
    echo "=========================================="
    echo "管理者APIキーの設定"
    echo "=========================================="
    echo ""
    echo "セキュアなランダムキーを生成します..."

    # OpenSSL でランダムキー生成
    if command -v openssl &> /dev/null; then
      ADMIN_KEY=$(openssl rand -hex 32)
      echo "生成されたキー: $ADMIN_KEY"
      echo ""

      # .env に設定
      if grep -q "ADMIN_API_KEY=" .env; then
        # 既存の行を置換
        if [[ "$OSTYPE" == "darwin"* ]]; then
          sed -i '' "s/ADMIN_API_KEY=.*/ADMIN_API_KEY=$ADMIN_KEY/" .env
        else
          sed -i "s/ADMIN_API_KEY=.*/ADMIN_API_KEY=$ADMIN_KEY/" .env
        fi
      else
        # 新規追加
        echo "ADMIN_API_KEY=$ADMIN_KEY" >> .env
      fi

      echo "管理者APIキーを .env に設定しました。"
      echo ""
      echo "このキーを安全に保管してください！"
      echo "管理者ダッシュボードへのログインに必要です。"
      echo ""
    else
      echo "警告: openssl が見つかりません。"
      echo "手動で強力なランダム文字列を生成し、.env の ADMIN_API_KEY に設定してください。"
    fi
  else
    echo "管理者APIキーは既に設定されています。"
  fi
fi

# Python 依存関係のインストール
echo ""
echo "Python 依存関係をインストール中..."
cd backend
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "警告: requirements.txt が見つかりません。"
fi
cd ..

# フロントエンド依存関係のインストール
echo ""
echo "フロントエンド依存関係をインストール中..."
cd frontend
if [ -f package.json ]; then
  if command -v bun &> /dev/null; then
    echo "Bun を使用してインストールします..."
    bun install
  elif command -v npm &> /dev/null; then
    echo "npm を使用してインストールします..."
    npm install
  else
    echo "警告: npm または bun が見つかりません。"
  fi

  # recharts のインストール確認
  if command -v bun &> /dev/null; then
    bun add recharts
  elif command -v npm &> /dev/null; then
    npm install recharts
  fi
else
  echo "警告: package.json が見つかりません。"
fi
cd ..

# データベースのマイグレーション
echo ""
echo "データベースをセットアップ中..."
cd backend
python -c "
from models.database import Base, engine
Base.metadata.create_all(bind=engine)
print('データベースのテーブルを作成しました。')
" 2>/dev/null || echo "警告: データベースの初期化に失敗しました。"
cd ..

# 設定ファイルの初期化
echo ""
echo "管理者設定を初期化中..."
python -c "
from backend.services.admin_service import AdminService
admin_service = AdminService()
settings = admin_service.get_settings()
print('設定ファイルを作成しました: data/settings.json')
" 2>/dev/null || echo "警告: 設定の初期化に失敗しました。"

echo ""
echo "=========================================="
echo "セットアップ完了！"
echo "=========================================="
echo ""
echo "次のステップ:"
echo "1. バックエンドAPIを起動:"
echo "   cd backend && python -m uvicorn main:app --reload"
echo ""
echo "2. フロントエンドを起動:"
echo "   cd frontend && npm start  (または bun start)"
echo ""
echo "3. 管理者ダッシュボードにアクセス:"
echo "   http://localhost:3000/admin"
echo ""
echo "4. .env に設定された ADMIN_API_KEY でログイン"
echo ""
echo "詳細は docs/ADMIN_DASHBOARD.md を参照してください。"
echo ""

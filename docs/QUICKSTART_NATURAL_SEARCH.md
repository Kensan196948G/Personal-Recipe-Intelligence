# クイックスタート - 自然言語検索機能

## 5分で試す自然言語検索

このガイドでは、自然言語検索機能を5分で試せるようにセットアップします。

## 前提条件

- Python 3.11 以上
- Node.js 20 以上 / Bun（推奨）
- Git

## セットアップ手順

### 1. セットアップスクリプトの実行

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# セットアップスクリプトに実行権限を付与
chmod +x scripts/*.sh

# セットアップ実行
./scripts/setup-natural-search.sh
```

これにより以下が自動で実行されます：
- ディレクトリ構成の確認
- ファイルの確認
- Python依存関係のインストール（確認付き）
- テストの実行
- データディレクトリの初期化

### 2. サンプルレシピのコピー

```bash
./scripts/copy-sample-recipes.sh
```

10件のサンプルレシピが `data/recipes.json` にコピーされます。

### 3. API サーバーの起動

```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

別のターミナルウィンドウで実行してください。

### 4. 検索機能のテスト

新しいターミナルで：

```bash
./scripts/test-natural-search.sh
```

これにより以下のテストが自動実行されます：
- クエリ解析
- 検索実行
- サジェスト取得
- 検索履歴
- 否定検索
- 複合検索

## 手動でテストする

### cURL で検索

```bash
# 基本検索
curl -X POST http://localhost:8000/api/v1/ai/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "鶏肉", "limit": 5}'

# 否定検索
curl -X POST http://localhost:8000/api/v1/ai/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "辛くない料理", "limit": 5}'

# 複合検索
curl -X POST http://localhost:8000/api/v1/ai/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "辛くない簡単な鶏肉料理", "limit": 5}'
```

### クエリ解析のみ

```bash
curl -X POST http://localhost:8000/api/v1/ai/search/parse \
  -H "Content-Type: application/json" \
  -d '{"query": "ヘルシーな野菜たっぷりサラダ"}'
```

### サジェスト取得

```bash
curl "http://localhost:8000/api/v1/ai/search/suggestions?q=鶏&limit=5"
```

## 検索クエリの例

試してみるべきクエリ：

### 基本検索
```
鶏肉
トマト
和食
サラダ
```

### 否定検索
```
辛くない料理
豚肉なし
油を使わない
```

### 形容詞検索
```
簡単な料理
ヘルシーなサラダ
時短レシピ
あっさりした料理
```

### 複合検索
```
辛くない簡単な鶏肉料理
ヘルシーな野菜たっぷりサラダ
和食で魚なし
時短でできるパスタ
```

## 期待される出力例

### 基本検索: "鶏肉"

```json
{
  "query": "鶏肉",
  "parsed": {
    "original": "鶏肉",
    "ingredients_include": ["鶏肉"],
    "ingredients_exclude": [],
    "cooking_methods": [],
    "categories": [],
    "adjectives": [],
    "negations": [],
    "keywords": [],
    "explanation": "食材: 鶏肉"
  },
  "results": [
    {
      "id": "recipe-001",
      "title": "鶏の唐揚げ",
      ...
    },
    {
      "id": "recipe-003",
      "title": "チキンカレー",
      ...
    },
    {
      "id": "recipe-010",
      "title": "親子丼",
      ...
    }
  ],
  "total": 3
}
```

### 否定検索: "辛くない料理"

```json
{
  "query": "辛くない料理",
  "parsed": {
    "original": "辛くない料理",
    "ingredients_include": [],
    "ingredients_exclude": ["辛い"],
    "cooking_methods": [],
    "categories": [],
    "adjectives": [],
    "negations": ["辛くない"],
    "keywords": ["料理"],
    "explanation": "除外: 辛い | キーワード: 料理"
  },
  "results": [
    {
      "id": "recipe-001",
      "title": "鶏の唐揚げ",
      ...
    },
    {
      "id": "recipe-004",
      "title": "豚の生姜焼き",
      ...
    }
  ],
  "total": 9
}
```

注: チキンカレー（辛い）は除外されます。

### 複合検索: "辛くない簡単な鶏肉料理"

```json
{
  "query": "辛くない簡単な鶏肉料理",
  "parsed": {
    "original": "辛くない簡単な鶏肉料理",
    "ingredients_include": ["鶏肉"],
    "ingredients_exclude": ["辛い"],
    "cooking_methods": [],
    "categories": [],
    "adjectives": ["簡単"],
    "negations": ["辛くない"],
    "keywords": ["料理"],
    "explanation": "食材: 鶏肉 | 除外: 辛い | 特徴: 簡単 | キーワード: 料理"
  },
  "results": [
    {
      "id": "recipe-010",
      "title": "親子丼",
      ...
    }
  ],
  "total": 1
}
```

## トラブルシューティング

### API サーバーが起動しない

```bash
# ポートが使用中でないか確認
lsof -i :8000

# 別のポートで起動
uvicorn api.main:app --reload --port 8001
```

### テストが失敗する

```bash
# pytest を最新化
pip install --upgrade pytest

# 詳細なエラー表示
pytest tests/test_natural_search_service.py -vv
```

### サンプルレシピが見つからない

```bash
# ファイルの確認
ls -la data/

# 手動でコピー
cp data/sample-recipes.json data/recipes.json
```

### jq コマンドがない

```bash
# Ubuntu/Debian
sudo apt-get install jq

# テストスクリプトを jq なしで実行
# JSON がそのまま表示されます
```

## 次のステップ

1. **フロントエンドの起動**
   ```bash
   cd frontend
   bun run dev
   ```
   ブラウザで `http://localhost:3000` を開いてUIから検索

2. **カスタマイズ**
   - `backend/services/natural_search_service.py` の辞書を編集
   - 同義語を追加
   - スコアリングを調整

3. **本番データの追加**
   - `data/recipes.json` に実際のレシピを追加
   - Web スクレイピング機能と連携
   - OCR 機能と連携

4. **API 統合**
   - `backend/api/main.py` にルーターを登録
   - 認証機能の追加（必要に応じて）

## 参考ドキュメント

- [API ドキュメント](natural-search-api.md)
- [使用例](natural-search-examples.md)
- [詳細 README](../README_NATURAL_SEARCH.md)

## サポート

問題が発生した場合は以下を確認してください：

1. Python バージョン: `python3 --version`
2. 依存関係: `pip list | grep -E "fastapi|pydantic|pytest"`
3. ファイル存在: `ls -la backend/services/natural_search_service.py`
4. ログ: `tail -f logs/*.log`（ログファイルがある場合）

## まとめ

これで自然言語検索機能が動作するはずです！

質問や問題があれば、ドキュメントを参照するか、テストスクリプトの出力を確認してください。

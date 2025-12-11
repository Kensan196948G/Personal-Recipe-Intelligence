# 自然言語検索機能 - README

## 概要

Personal Recipe Intelligence の自然言語検索機能は、日本語の自然な表現でレシピを検索できる機能です。

「辛くない簡単な鶏肉料理」のように話し言葉で検索すると、条件に合ったレシピを自動的に抽出します。

## 機能

### 1. 自然言語解析
- **食材の抽出**: 「鶏肉」「トマト」などを自動検出
- **否定表現の処理**: 「辛くない」「豚肉なし」などを理解
- **調理法の認識**: 「焼く」「揚げる」などを検出
- **カテゴリ分類**: 「和食」「イタリアン」などを認識
- **形容詞の解釈**: 「簡単」「ヘルシー」などを評価

### 2. スマート検索
- **スコアリング**: マッチ度に応じてスコアを計算
- **複合条件対応**: 複数の条件を組み合わせて検索
- **同義語対応**: 「たまねぎ」→「玉ねぎ」など自動変換

### 3. サジェスト機能
- **入力補完**: 入力途中で候補を表示
- **人気検索**: よく検索されるクエリを提案

### 4. 検索履歴
- **履歴保存**: 過去の検索クエリを保存
- **履歴からの再検索**: ワンクリックで過去の検索を再実行

## ファイル構成

```
backend/
├── services/
│   ├── natural_search_service.py  # 自然言語検索サービス
│   └── recipe_service.py          # レシピ管理サービス
├── api/
│   └── routers/
│       └── natural_search.py      # APIルーター
└── tests/
    └── test_natural_search_service.py  # テスト

frontend/
└── components/
    ├── SmartSearch.jsx            # 検索コンポーネント
    └── SmartSearch.css            # スタイル

docs/
├── natural-search-api.md          # API ドキュメント
└── natural-search-examples.md     # 使用例

data/
└── search_history.json            # 検索履歴（自動生成）
```

## セットアップ

### 1. 依存関係のインストール

すでに基本的な依存関係がインストールされている場合は不要です。

```bash
cd backend
pip install fastapi pydantic
```

### 2. API サーバーの起動

```bash
# backend ディレクトリで
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. フロントエンドの起動

```bash
# frontend ディレクトリで
bun run dev
```

### 4. API ルーターの登録

`backend/api/main.py` に以下を追加してください：

```python
from api.routers import natural_search

app.include_router(natural_search.router)
```

## 使い方

### Web UI での使用

1. ブラウザで `http://localhost:3000` を開く
2. スマート検索ページに移動
3. 検索ボックスに自然な日本語を入力
   - 例: 「辛くない簡単な鶏肉料理」
4. 検索結果が表示されます

### API での使用

#### 検索実行

```bash
curl -X POST http://localhost:8000/api/v1/ai/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "辛くない簡単な鶏肉料理", "limit": 20}'
```

#### クエリ解析のみ

```bash
curl -X POST http://localhost:8000/api/v1/ai/search/parse \
  -H "Content-Type: application/json" \
  -d '{"query": "ヘルシーな野菜たっぷりサラダ"}'
```

#### サジェスト取得

```bash
curl http://localhost:8000/api/v1/ai/search/suggestions?q=鶏&limit=5
```

## 検索クエリの例

### 基本検索
- `鶏肉` - 鶏肉を使ったレシピ
- `トマトとパスタ` - トマトとパスタを使ったレシピ
- `和食` - 和食のレシピ

### 否定検索
- `辛くない料理` - 辛くないレシピ
- `豚肉なし` - 豚肉を使わないレシピ
- `油を使わない` - 油不使用のレシピ

### 形容詞検索
- `簡単な料理` - 簡単に作れるレシピ
- `ヘルシーなサラダ` - ヘルシーなサラダ
- `時短レシピ` - 時短でできるレシピ

### 複合検索
- `辛くない簡単な鶏肉料理` - 鶏肉 + 簡単 + 辛くない
- `ヘルシーな野菜たっぷりサラダ` - ヘルシー + 野菜
- `和食で魚なし` - 和食 + 魚を除外

## アーキテクチャ

### 検索フロー

```
1. ユーザー入力
   ↓
2. クエリ正規化（同義語統一、スペース整理）
   ↓
3. 否定表現の抽出（「〇〇ない」パターン）
   ↓
4. 各要素の抽出
   - 食材
   - 調理法
   - カテゴリ
   - 形容詞
   - キーワード
   ↓
5. 検索フィルタ構築
   ↓
6. レシピマッチング & スコアリング
   ↓
7. ソート & 返却
```

### スコアリングアルゴリズム

```python
score = 0

# 食材（含む）: +20点
for ingredient in parsed.ingredients_include:
  if ingredient in recipe_text:
    score += 20.0

# 食材（除く）: -50点
for ingredient in parsed.ingredients_exclude:
  if ingredient in recipe_text:
    score -= 50.0

# 調理法: +15点
for method in parsed.cooking_methods:
  if method in recipe_text:
    score += 15.0

# カテゴリ: +10点
for category in parsed.categories:
  if category in recipe_text:
    score += 10.0

# 形容詞: +8点
for adjective in parsed.adjectives:
  if adjective in recipe_text:
    score += 8.0

# キーワード: +5点
for keyword in parsed.keywords:
  if keyword in recipe_text:
    score += 5.0
```

### データ構造

#### ParsedQuery
```python
@dataclass
class ParsedQuery:
  original: str                    # 元のクエリ
  ingredients_include: List[str]   # 含む食材
  ingredients_exclude: List[str]   # 除外する食材
  cooking_methods: List[str]       # 調理法
  categories: List[str]            # カテゴリ
  adjectives: List[str]            # 形容詞
  negations: List[str]             # 否定表現
  keywords: List[str]              # その他キーワード
```

## テスト

```bash
# テストの実行
cd backend
pytest tests/test_natural_search_service.py -v

# カバレッジ付き
pytest tests/test_natural_search_service.py --cov=services.natural_search_service
```

### テストケース
- クエリ解析（食材、調理法、形容詞、否定表現）
- 検索実行（単純検索、複合検索、否定検索）
- サジェスト機能
- 検索履歴
- エッジケース（特殊文字、長文、Unicode等）

## カスタマイズ

### 辞書の拡張

`backend/services/natural_search_service.py` の `_load_dictionary()` メソッドで辞書を編集できます：

```python
def _load_dictionary(self) -> Dict[str, List[str]]:
  return {
    "ingredients": [
      # ここに新しい食材を追加
      "アボカド", "パクチー", ...
    ],
    "cooking_methods": [
      # ここに新しい調理法を追加
      "低温調理", "圧力調理", ...
    ],
    ...
  }
```

### 同義語の追加

```python
"synonyms": {
  "新しい標準語": ["同義語1", "同義語2", "同義語3"],
  ...
}
```

### スコアリングの調整

`_calculate_match_score()` メソッドでスコアの重み付けを変更できます：

```python
# 食材を重視する場合
for ingredient in parsed.ingredients_include:
  if ingredient.lower() in recipe_text:
    score += 30.0  # 20.0 → 30.0 に変更
```

## パフォーマンス

### 処理速度
- クエリ解析: < 10ms
- 検索実行（1000件）: < 100ms
- サジェスト生成: < 50ms

### メモリ使用量
- サービスインスタンス: < 5MB
- 検索履歴（100件）: < 1MB

## トラブルシューティング

### 検索結果が出ない
1. クエリ解析結果を確認（`/api/v1/ai/search/parse`）
2. データベースにレシピが存在するか確認
3. 検索条件を緩和（否定表現を減らす）

### サジェストが表示されない
1. 検索履歴があるか確認
2. 入力文字数を増やす（最低1文字必要）

### 期待と違う結果
1. 解析結果を確認
2. 辞書に単語が登録されているか確認
3. スコアリングアルゴリズムを調整

## ライセンス

MIT License

## 貢献

Pull Request 歓迎です！

## 今後の改善予定

- [ ] 形態素解析ライブラリの統合（MeCab等）
- [ ] 機械学習ベースのスコアリング
- [ ] 多言語対応
- [ ] 音声検索対応
- [ ] 画像からの検索

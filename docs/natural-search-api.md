# 自然言語検索 API ドキュメント

## 概要
Personal Recipe Intelligence の自然言語検索機能は、日本語の自然な表現でレシピを検索できる機能です。

## エンドポイント

### POST /api/v1/ai/search/
自然言語検索を実行します。

**リクエスト:**
```json
{
  "query": "辛くない簡単な鶏肉料理",
  "limit": 20
}
```

**レスポンス:**
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
      "id": "1",
      "title": "鶏の唐揚げ",
      "description": "サクサクでジューシーな唐揚げ",
      "ingredients": ["鶏もも肉", "しょうゆ", "にんにく"],
      "tags": ["和食", "主菜", "揚げ物"]
    }
  ],
  "total": 5,
  "timestamp": "2025-12-11T10:30:00"
}
```

### POST /api/v1/ai/search/parse
クエリの解析のみを実行します（検索は行いません）。

**リクエスト:**
```json
{
  "query": "ヘルシーな野菜たっぷりサラダ"
}
```

**レスポンス:**
```json
{
  "original": "ヘルシーな野菜たっぷりサラダ",
  "ingredients_include": [],
  "ingredients_exclude": [],
  "cooking_methods": ["サラダ"],
  "categories": ["サラダ"],
  "adjectives": ["ヘルシー"],
  "negations": [],
  "keywords": ["野菜", "たっぷり"],
  "explanation": "調理法: サラダ | カテゴリ: サラダ | 特徴: ヘルシー | キーワード: 野菜, たっぷり"
}
```

### GET /api/v1/ai/search/suggestions
検索サジェストを取得します。

**パラメータ:**
- `q`: 部分クエリ（空の場合は人気検索を返す）
- `limit`: 最大返却数（デフォルト: 10）

**レスポンス:**
```json
{
  "suggestions": [
    "鶏肉",
    "鶏もも肉",
    "鶏むね肉",
    "鶏の唐揚げ"
  ]
}
```

### GET /api/v1/ai/search/history
検索履歴を取得します。

**パラメータ:**
- `limit`: 最大返却数（デフォルト: 20）

**レスポンス:**
```json
{
  "history": [
    {
      "query": "辛くない簡単な鶏肉料理",
      "timestamp": "2025-12-11T10:30:00",
      "parsed": {
        "original": "辛くない簡単な鶏肉料理",
        "ingredients_include": ["鶏肉"],
        "ingredients_exclude": ["辛い"],
        "adjectives": ["簡単"]
      }
    }
  ],
  "total": 1
}
```

### DELETE /api/v1/ai/search/history
検索履歴をクリアします。

**レスポンス:**
```json
{
  "status": "ok",
  "message": "検索履歴をクリアしました"
}
```

## 検索クエリの例

### 基本的な検索
- `鶏肉` - 鶏肉を含むレシピ
- `トマトとパスタ` - トマトとパスタを使ったレシピ
- `和食` - 和食カテゴリのレシピ

### 否定検索
- `辛くない料理` - 辛くないレシピ
- `豚肉なし` - 豚肉を使わないレシピ
- `油を使わない` - 油不使用のレシピ

### 形容詞検索
- `簡単な料理` - 簡単に作れるレシピ
- `ヘルシーなサラダ` - ヘルシーなサラダ
- `時短レシピ` - 時短でできるレシピ

### 複合検索
- `辛くない簡単な鶏肉料理` - 鶏肉を使った辛くない簡単なレシピ
- `ヘルシーな野菜たっぷりサラダ` - 野菜が豊富なヘルシーサラダ
- `和食で魚なし` - 和食で魚を使わないレシピ

## 解析機能

### サポートされる要素

#### 食材
- 野菜: トマト、きゅうり、キャベツ、にんじん等
- 肉類: 豚肉、牛肉、鶏肉、ひき肉等
- 魚介: 鮭、さば、えび、いか等
- その他: 卵、豆腐、チーズ等

#### 調理法
- 焼く、炒める、煮る、茹でる、揚げる、蒸す等

#### カテゴリ
- ジャンル: 和食、洋食、中華、イタリアン等
- 種類: 主菜、副菜、汁物、サラダ等

#### 形容詞
- 味: 辛い、甘い、あっさり、こってり等
- 難易度: 簡単、時短、手軽等
- 健康: ヘルシー、低カロリー、高たんぱく等
- 食感: やわらかい、サクサク、もちもち等

### 同義語対応
以下の単語は自動的に統一されます：
- `たまねぎ` → `玉ねぎ`
- `とり肉` → `鶏肉`
- `にんじん` → `人参`
- `かんたん` → `簡単`

## スコアリング

レシピのマッチスコアは以下の要素で計算されます：
- 食材（含む）: +20点
- 食材（除く）: -50点
- 調理法: +15点
- カテゴリ: +10点
- 形容詞: +8点
- キーワード: +5点

スコアが高い順に結果が返されます。

## 使用例

### cURL
```bash
# 検索実行
curl -X POST http://localhost:8000/api/v1/ai/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "辛くない簡単な鶏肉料理", "limit": 10}'

# クエリ解析のみ
curl -X POST http://localhost:8000/api/v1/ai/search/parse \
  -H "Content-Type: application/json" \
  -d '{"query": "ヘルシーな野菜たっぷりサラダ"}'

# サジェスト取得
curl http://localhost:8000/api/v1/ai/search/suggestions?q=鶏&limit=5

# 履歴取得
curl http://localhost:8000/api/v1/ai/search/history?limit=20
```

### JavaScript (fetch)
```javascript
// 検索実行
const response = await fetch('/api/v1/ai/search/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: '辛くない簡単な鶏肉料理',
    limit: 20
  })
});
const data = await response.json();
console.log(data.results);

// サジェスト取得
const suggestions = await fetch(
  `/api/v1/ai/search/suggestions?q=${encodeURIComponent(query)}`
);
const suggestData = await suggestions.json();
console.log(suggestData.suggestions);
```

## エラーハンドリング

すべてのエンドポイントは以下のエラーレスポンスを返す可能性があります：

```json
{
  "detail": "エラーメッセージ"
}
```

HTTPステータスコード:
- 200: 成功
- 400: 不正なリクエスト
- 500: サーバーエラー

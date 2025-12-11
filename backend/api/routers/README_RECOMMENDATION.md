# レシピ推薦 API ドキュメント

## 概要
材料ベースのレシピ推薦システムを提供するAPIエンドポイント群です。

## エンドポイント一覧

### 1. 材料からレシピ推薦
**POST** `/api/v1/recommend/by-ingredients`

指定した材料から作れるレシピを推薦します。

#### リクエスト
```json
{
  "ingredients": ["たまねぎ", "にんじん", "じゃがいも", "豚肉"],
  "min_score": 0.5,
  "max_results": 10
}
```

**パラメータ:**
- `ingredients` (required): 材料リスト
- `min_score` (optional): 最小マッチスコア (0.0〜1.0、デフォルト: 0.5)
- `max_results` (optional): 最大結果数 (1〜50、デフォルト: 10)

#### レスポンス
```json
{
  "status": "ok",
  "data": {
    "recommendations": [
      {
        "recipe": {
          "id": "recipe_001",
          "name": "カレーライス",
          "ingredients": [...],
          "steps": [...],
          "tags": ["洋食", "定番"]
        },
        "match_score": 0.85,
        "matched_ingredients": ["たまねぎ", "にんじん", "じゃがいも", "豚肉"],
        "missing_ingredients": ["カレールー", "サラダ油"],
        "match_percentage": 66.7
      }
    ],
    "total": 1,
    "query_ingredients": ["たまねぎ", "にんじん", "じゃがいも", "豚肉"]
  },
  "error": null
}
```

---

### 2. 類似レシピ推薦
**GET** `/api/v1/recommend/similar/{recipe_id}`

指定したレシピに類似するレシピを推薦します。

#### パスパラメータ
- `recipe_id`: レシピID

#### クエリパラメータ
- `max_results` (optional): 最大結果数 (1〜20、デフォルト: 5)

#### リクエスト例
```
GET /api/v1/recommend/similar/recipe_001?max_results=5
```

#### レスポンス
```json
{
  "status": "ok",
  "data": {
    "recommendations": [
      {
        "recipe": {
          "id": "recipe_002",
          "name": "肉じゃが",
          "ingredients": [...],
          "steps": [...],
          "tags": ["和食", "定番"]
        },
        "match_score": 0.72,
        "matched_ingredients": ["じゃがいも", "たまねぎ", "にんじん"],
        "missing_ingredients": ["牛肉", "醤油", "砂糖", "みりん"],
        "match_percentage": 50.0
      }
    ],
    "total": 1,
    "target_recipe_id": "recipe_001"
  },
  "error": null
}
```

---

### 3. 手持ち材料で作れるレシピ検索
**POST** `/api/v1/recommend/what-can-i-make`

手持ちの材料で作れるレシピを検索します（不足材料も表示）。

#### リクエスト
```json
{
  "ingredients": ["たまねぎ", "じゃがいも", "にんじん"],
  "allow_missing": 2
}
```

**パラメータ:**
- `ingredients` (required): 手持ち材料リスト
- `allow_missing` (optional): 許容する不足材料数 (0〜10、デフォルト: 2)

#### レスポンス
```json
{
  "status": "ok",
  "data": {
    "recommendations": [
      {
        "recipe": {
          "id": "recipe_005",
          "name": "オニオンスープ",
          "ingredients": [...],
          "steps": [...],
          "tags": ["洋食", "スープ"]
        },
        "match_score": 0.45,
        "matched_ingredients": ["たまねぎ"],
        "missing_ingredients": ["バター", "コンソメ"],
        "match_percentage": 20.0
      }
    ],
    "total": 1,
    "query_ingredients": ["たまねぎ", "じゃがいも", "にんじん"],
    "allow_missing": 2
  },
  "error": null
}
```

---

## スコアリングアルゴリズム

### マッチスコア計算
```
match_score = matched_weight / total_weight
```

**重み付け:**
- 主材料: 1.0
- 調味料: 0.3

### 一致率計算
```
match_percentage = (一致材料数 / 必要材料数) × 100
```

### 材料正規化
以下の材料名は自動的に正規化されます：

| 入力 | 正規化後 |
|------|---------|
| 玉ねぎ, 玉葱, タマネギ | たまねぎ |
| 人参, ニンジン | にんじん |
| じゃが芋, ジャガイモ, 馬鈴薯 | じゃがいも |
| トマト | とまと |
| 茄子, ナス | なす |
| キュウリ, 胡瓜 | きゅうり |

### 調味料リスト
以下は調味料として低スコアで処理されます：
- 塩, 砂糖, 醤油, 味噌, 酢, 油類
- みりん, 料理酒, だし, コンソメ
- ケチャップ, マヨネーズ, ソース類
- バター, マーガリン

---

## エラーレスポンス

### 500 Internal Server Error
```json
{
  "detail": "推薦処理でエラーが発生しました: [エラー内容]"
}
```

---

## 使用例

### cURL
```bash
# 材料からレシピ推薦
curl -X POST "http://localhost:8000/api/v1/recommend/by-ingredients" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["たまねぎ", "にんじん", "じゃがいも"],
    "min_score": 0.5,
    "max_results": 10
  }'

# 類似レシピ推薦
curl -X GET "http://localhost:8000/api/v1/recommend/similar/recipe_001?max_results=5"

# 手持ち材料で作れるレシピ検索
curl -X POST "http://localhost:8000/api/v1/recommend/what-can-i-make" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["たまねぎ", "にんじん"],
    "allow_missing": 2
  }'
```

### Python (requests)
```python
import requests

# 材料からレシピ推薦
response = requests.post(
  "http://localhost:8000/api/v1/recommend/by-ingredients",
  json={
    "ingredients": ["たまねぎ", "にんじん", "じゃがいも"],
    "min_score": 0.5,
    "max_results": 10
  }
)
data = response.json()
print(data["data"]["recommendations"])
```

---

## 今後の拡張予定
- データベース統合（現在はモックデータ）
- タグベースのフィルタリング
- アレルギー情報による除外
- 栄養価情報の追加
- ユーザー嗜好学習

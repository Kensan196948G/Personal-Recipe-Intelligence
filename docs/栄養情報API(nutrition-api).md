# 栄養計算API ドキュメント

Personal Recipe Intelligence の栄養計算機能に関するAPI仕様書

---

## 概要

レシピの材料から自動的にカロリー・栄養素を計算し、1人前あたりの栄養価を提供します。

日本食品標準成分表2020年版（八訂）をベースにした約80種類以上の食材データを搭載。

---

## エンドポイント一覧

### 1. 栄養計算

**POST /api/v1/nutrition/calculate**

材料リストから栄養価を計算します。

#### リクエスト

```json
{
  "ingredients": [
    {"name": "白米", "amount": "200g"},
    {"name": "鶏もも肉", "amount": "150g"},
    {"name": "玉ねぎ", "amount": "1個"}
  ],
  "servings": 2
}
```

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "servings": 2,
    "per_serving": {
      "calories": 450.5,
      "protein": 25.3,
      "fat": 15.2,
      "carbohydrates": 55.8,
      "fiber": 3.2
    },
    "total": {
      "calories": 901.0,
      "protein": 50.6,
      "fat": 30.4,
      "carbohydrates": 111.6,
      "fiber": 6.4
    },
    "ingredients_breakdown": [
      {
        "ingredient": "白米",
        "amount": "200g",
        "amount_g": 200.0,
        "found": true,
        "calories": 336.0,
        "protein": 5.0,
        "fat": 0.6,
        "carbohydrates": 74.2,
        "fiber": 0.6
      },
      {
        "ingredient": "鶏もも肉",
        "amount": "150g",
        "amount_g": 150.0,
        "found": true,
        "calories": 300.0,
        "protein": 24.3,
        "fat": 21.0,
        "carbohydrates": 0.0,
        "fiber": 0.0
      },
      {
        "ingredient": "玉ねぎ",
        "amount": "1個",
        "amount_g": 100.0,
        "found": true,
        "calories": 37.0,
        "protein": 1.0,
        "fat": 0.1,
        "carbohydrates": 8.8,
        "fiber": 1.6
      }
    ],
    "found_ingredients": 3,
    "total_ingredients": 3,
    "summary": {
      "calorie_level": "中カロリー",
      "pfc_balance": "P:22.4% F:30.4% C:47.2%",
      "protein_ratio": 22.4,
      "fat_ratio": 30.4,
      "carb_ratio": 47.2
    }
  },
  "error": null
}
```

---

### 2. 材料の栄養情報取得

**GET /api/v1/nutrition/ingredient/{name}**

指定した材料の栄養情報（100gあたり）を取得します。

#### リクエスト例

```
GET /api/v1/nutrition/ingredient/鶏もも肉
```

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "name": "鶏もも肉",
    "calories": 200,
    "protein": 16.2,
    "fat": 14.0,
    "carbohydrates": 0,
    "fiber": 0,
    "unit": "100g"
  },
  "error": null
}
```

材料が見つからない場合:

```json
{
  "status": "ok",
  "data": null,
  "error": null
}
```

---

### 3. 材料リスト取得

**GET /api/v1/nutrition/ingredients**

登録されている全材料名を取得します。

#### レスポンス

```json
{
  "status": "ok",
  "data": [
    "白米",
    "玄米",
    "鶏もも肉",
    "鶏むね肉",
    "豚バラ肉",
    "玉ねぎ",
    "にんじん",
    ...
  ],
  "error": null
}
```

---

### 4. 材料検索

**GET /api/v1/nutrition/search?q={query}**

材料を部分一致で検索します。

#### リクエスト例

```
GET /api/v1/nutrition/search?q=鶏
```

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "query": "鶏",
    "results": [
      {
        "name": "鶏もも肉",
        "calories": 200,
        "protein": 16.2,
        "fat": 14.0,
        "carbohydrates": 0,
        "fiber": 0,
        "unit": "100g"
      },
      {
        "name": "鶏むね肉",
        "calories": 108,
        "protein": 22.3,
        "fat": 1.5,
        "carbohydrates": 0,
        "fiber": 0,
        "unit": "100g"
      }
    ],
    "count": 2
  },
  "error": null
}
```

---

### 5. レシピIDから栄養取得（未実装）

**GET /api/v1/nutrition/recipe/{recipe_id}**

レシピIDを指定して栄養情報を取得します。

**現在未実装**（Recipeサービスとの統合が必要）

#### レスポンス

```json
{
  "detail": "レシピIDからの栄養取得は未実装です。Recipe サービスとの統合が必要です。"
}
```

---

## 分量の表記ルール

以下の単位に対応しています:

| 単位 | 換算 | 例 |
|------|------|-----|
| g | グラム | 200g |
| kg | キログラム | 0.5kg → 500g |
| ml, cc | ミリリットル | 100ml |
| L | リットル | 1L → 1000ml |
| 大さじ | 15ml | 大さじ1 → 15g |
| 小さじ | 5ml | 小さじ2 → 10g |
| カップ | 200ml | 1カップ → 200g |
| 個, 枚 | 約100g | 2個 → 200g |

---

## 栄養素の説明

### 基本栄養素

- **calories**: カロリー（kcal）
- **protein**: タンパク質（g）
- **fat**: 脂質（g）
- **carbohydrates**: 炭水化物（g）
- **fiber**: 食物繊維（g）

### PFCバランス

タンパク質（Protein）・脂質（Fat）・炭水化物（Carbohydrate）のカロリー比率

- タンパク質: 1g = 4kcal
- 脂質: 1g = 9kcal
- 炭水化物: 1g = 4kcal

理想的なPFCバランス: P:15-20% / F:20-30% / C:50-65%

### カロリーレベル

- **低カロリー**: 300kcal未満
- **中カロリー**: 300-600kcal
- **高カロリー**: 600kcal以上

---

## 使用例

### Python での使用

```python
import requests

# 栄養計算
url = "http://localhost:8001/api/v1/nutrition/calculate"
data = {
    "ingredients": [
        {"name": "白米", "amount": "150g"},
        {"name": "鶏むね肉", "amount": "100g"},
        {"name": "ブロッコリー", "amount": "80g"}
    ],
    "servings": 1
}

response = requests.post(url, json=data)
result = response.json()

print(f"カロリー: {result['data']['per_serving']['calories']} kcal")
print(f"タンパク質: {result['data']['per_serving']['protein']} g")
```

### curl での使用

```bash
# 栄養計算
curl -X POST "http://localhost:8001/api/v1/nutrition/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"name": "白米", "amount": "200g"},
      {"name": "鶏もも肉", "amount": "150g"}
    ],
    "servings": 2
  }'

# 材料情報取得
curl "http://localhost:8001/api/v1/nutrition/ingredient/鶏もも肉"

# 材料検索
curl "http://localhost:8001/api/v1/nutrition/search?q=鶏"

# 全材料リスト
curl "http://localhost:8001/api/v1/nutrition/ingredients"
```

---

## エラーハンドリング

### 成功時

```json
{
  "status": "ok",
  "data": { ... },
  "error": null
}
```

### エラー時

```json
{
  "detail": "エラーメッセージ"
}
```

主なHTTPステータスコード:

- **200**: 成功
- **422**: バリデーションエラー
- **500**: サーバーエラー
- **501**: 未実装

---

## 登録材料カテゴリ

### 穀類
白米、玄米、食パン、うどん、そば、パスタ

### 肉類
鶏もも肉、鶏むね肉、豚バラ肉、豚ロース肉、牛もも肉、牛バラ肉、ひき肉

### 魚介類
サーモン、まぐろ、さば、いわし、えび、いか

### 野菜類
玉ねぎ、にんじん、じゃがいも、トマト、きゅうり、レタス、キャベツ、ブロッコリー、ほうれん草、なす、ピーマン

### きのこ類
しめじ、えのき、しいたけ

### 卵・乳製品
卵、牛乳、ヨーグルト、チーズ、バター

### 豆類
豆腐、納豆、油揚げ

### 調味料
醤油、味噌、砂糖、塩、サラダ油、ごま油、オリーブオイル、みりん、酒

---

## 注意事項

1. **栄養値は目安**: 食材の産地・品種により栄養価は変動します
2. **調理による変化**: 加熱・調理により栄養価が変化する場合があります
3. **未登録材料**: データベースにない材料は栄養価が0として計算されます
4. **分量の推定**: 「個」「枚」などの単位は標準的な重量で換算しています

---

## 今後の拡張予定

- [ ] ビタミン・ミネラルの追加
- [ ] アレルギー情報の追加
- [ ] 食材の季節情報
- [ ] 栄養バランススコア
- [ ] レシピデータベースとの統合
- [ ] カスタム食材の登録機能

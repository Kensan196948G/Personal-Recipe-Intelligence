# 食事履歴 API 仕様書

## 概要

食事履歴機能は、ユーザーの日々の食事記録を管理し、栄養摂取量の分析と傾向把握を提供します。

## エンドポイント一覧

### 1. 食事記録の保存

**POST** `/api/v1/meal-history/record`

食事内容、栄養情報、食材を記録します。

#### リクエストボディ

```json
{
  "user_id": "user123",
  "recipe_id": "recipe456",
  "recipe_name": "チキンカレー",
  "meal_type": "lunch",
  "servings": 2.0,
  "nutrition": {
    "calories": 850.0,
    "protein": 35.0,
    "fat": 28.0,
    "carbohydrates": 95.0,
    "fiber": 8.0,
    "sodium": 1200.0
  },
  "ingredients": ["鶏肉", "玉ねぎ", "にんじん", "じゃがいも", "カレールー"],
  "consumed_at": "2025-12-10T12:30:00"
}
```

#### パラメータ

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| user_id | string | ✓ | ユーザーID |
| recipe_id | string | ✓ | レシピID |
| recipe_name | string | ✓ | レシピ名 |
| meal_type | string | ✓ | 食事タイプ（breakfast/lunch/dinner/snack） |
| servings | float | ✓ | 人前数（> 0） |
| nutrition | object | ✓ | 栄養素情報 |
| ingredients | array | ✓ | 食材リスト |
| consumed_at | string | - | 食事日時（ISO8601形式、省略時は現在時刻） |

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "id": "user123_1702195800.123",
    "consumed_at": "2025-12-10T12:30:00",
    "message": "Meal recorded successfully"
  },
  "error": null
}
```

---

### 2. 日別栄養摂取量の取得

**GET** `/api/v1/meal-history/daily/{date}?user_id={user_id}`

指定日の全食事記録と栄養摂取量を取得します。

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| date | string | ✓ | 日付（YYYY-MM-DD形式） |
| user_id | string | ✓ | ユーザーID（クエリパラメータ） |

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "date": "2025-12-10",
    "total_nutrition": {
      "calories": 2150.0,
      "protein": 85.0,
      "fat": 65.0,
      "carbohydrates": 280.0,
      "fiber": 22.0,
      "sodium": 2100.0
    },
    "meals": [
      {
        "id": "user123_1702188000.123",
        "recipe_name": "和風朝食セット",
        "meal_type": "breakfast",
        "consumed_at": "2025-12-10T07:30:00",
        "nutrition": {
          "calories": 450.0,
          "protein": 18.0,
          "fat": 12.0,
          "carbohydrates": 65.0
        }
      },
      {
        "id": "user123_1702195800.456",
        "recipe_name": "チキンカレー",
        "meal_type": "lunch",
        "consumed_at": "2025-12-10T12:30:00",
        "nutrition": {
          "calories": 850.0,
          "protein": 35.0,
          "fat": 28.0,
          "carbohydrates": 95.0
        }
      }
    ],
    "meal_count": 2
  },
  "error": null
}
```

---

### 3. 週間栄養摂取量の取得

**GET** `/api/v1/meal-history/weekly?user_id={user_id}&start_date={start_date}`

7日分の日別栄養摂取量を取得します。

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| user_id | string | ✓ | ユーザーID |
| start_date | string | - | 開始日（YYYY-MM-DD形式、省略時は今週月曜日） |

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "period": "weekly",
    "start_date": "2025-12-09",
    "end_date": "2025-12-15",
    "daily_data": [
      {
        "date": "2025-12-09",
        "total_nutrition": {
          "calories": 1950.0,
          "protein": 75.0,
          "fat": 58.0
        },
        "meal_count": 3
      },
      {
        "date": "2025-12-10",
        "total_nutrition": {
          "calories": 2150.0,
          "protein": 85.0,
          "fat": 65.0
        },
        "meal_count": 3
      }
    ]
  },
  "error": null
}
```

---

### 4. 月間栄養摂取量の取得

**GET** `/api/v1/meal-history/monthly?user_id={user_id}&year={year}&month={month}`

指定月の日別栄養摂取量を取得します。

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| user_id | string | ✓ | ユーザーID |
| year | int | ✓ | 年（2000-2100） |
| month | int | ✓ | 月（1-12） |

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "period": "monthly",
    "year": 2025,
    "month": 12,
    "daily_data": [
      {
        "date": "2025-12-01",
        "total_nutrition": {
          "calories": 2000.0,
          "protein": 80.0
        },
        "meal_count": 3
      }
    ]
  },
  "error": null
}
```

---

### 5. 食事傾向の分析

**GET** `/api/v1/meal-history/trends?user_id={user_id}&days={days}`

よく食べる食材、時間帯別パターン、栄養バランスを分析します。

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| user_id | string | ✓ | ユーザーID |
| days | int | - | 分析対象日数（デフォルト: 30、最大: 365） |

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "period_days": 30,
    "top_ingredients": [
      {"name": "鶏肉", "count": 15},
      {"name": "玉ねぎ", "count": 12},
      {"name": "にんじん", "count": 10}
    ],
    "meal_time_pattern": {
      "breakfast": 25,
      "lunch": 28,
      "dinner": 27,
      "snack": 5
    },
    "favorite_recipes": [
      {"name": "チキンカレー", "count": 8},
      {"name": "和風朝食セット", "count": 6}
    ],
    "nutrition_balance": {
      "calories": "adequate",
      "protein": "adequate",
      "fat": "excessive",
      "carbohydrates": "adequate",
      "fiber": "insufficient",
      "sodium": "excessive"
    }
  },
  "error": null
}
```

#### 栄養バランス評価

- **excessive**: 目標値の120%以上
- **adequate**: 目標値の80%～120%
- **insufficient**: 目標値の80%未満

---

### 6. 栄養素推移の取得

**GET** `/api/v1/meal-history/nutrition-trend?user_id={user_id}&nutrient={nutrient}&days={days}`

指定栄養素の日別推移データを取得します（グラフ表示用）。

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| user_id | string | ✓ | ユーザーID |
| nutrient | string | ✓ | 栄養素名（calories/protein/fat等） |
| days | int | - | 取得日数（デフォルト: 30、最大: 365） |

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "nutrient_name": "calories",
    "dates": [
      "2025-11-11",
      "2025-11-12",
      "2025-11-13"
    ],
    "values": [1950.0, 2150.0, 1850.0],
    "statistics": {
      "average": 1983.33,
      "std_dev": 152.75,
      "target": 2000.0
    }
  },
  "error": null
}
```

---

### 7. 栄養摂取量サマリーの取得

**GET** `/api/v1/meal-history/summary?user_id={user_id}&start_date={start_date}&end_date={end_date}`

指定期間の合計・平均栄養摂取量を取得します。

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| user_id | string | ✓ | ユーザーID |
| start_date | string | ✓ | 開始日（YYYY-MM-DD形式） |
| end_date | string | ✓ | 終了日（YYYY-MM-DD形式） |

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "period": {
      "start": "2025-12-01",
      "end": "2025-12-10",
      "days": 10
    },
    "total": {
      "calories": 20500.0,
      "protein": 820.0,
      "fat": 620.0
    },
    "average_per_day": {
      "calories": 2050.0,
      "protein": 82.0,
      "fat": 62.0
    },
    "meal_count": 28,
    "targets": {
      "calories": 2000.0,
      "protein": 60.0,
      "fat": 55.0
    }
  },
  "error": null
}
```

---

## エラーレスポンス

全エンドポイント共通のエラーレスポンス形式：

```json
{
  "status": "error",
  "data": null,
  "error": "エラーメッセージ"
}
```

### 共通エラーコード

| HTTPステータス | 説明 |
|--------------|------|
| 400 | Bad Request - 不正なパラメータ |
| 404 | Not Found - リソースが見つからない |
| 500 | Internal Server Error - サーバーエラー |

---

## 使用例

### Python

```python
import requests

# 食事記録
response = requests.post(
  "http://localhost:8001/api/v1/meal-history/record",
  json={
    "user_id": "user123",
    "recipe_id": "recipe456",
    "recipe_name": "チキンカレー",
    "meal_type": "lunch",
    "servings": 2.0,
    "nutrition": {
      "calories": 850.0,
      "protein": 35.0,
      "fat": 28.0,
      "carbohydrates": 95.0
    },
    "ingredients": ["鶏肉", "玉ねぎ", "カレールー"]
  }
)
print(response.json())

# 日別データ取得
response = requests.get(
  "http://localhost:8001/api/v1/meal-history/daily/2025-12-10",
  params={"user_id": "user123"}
)
print(response.json())
```

### JavaScript (fetch)

```javascript
// 食事記録
const recordMeal = async () => {
  const response = await fetch('/api/v1/meal-history/record', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: 'user123',
      recipe_id: 'recipe456',
      recipe_name: 'チキンカレー',
      meal_type: 'lunch',
      servings: 2.0,
      nutrition: {
        calories: 850.0,
        protein: 35.0,
        fat: 28.0,
        carbohydrates: 95.0
      },
      ingredients: ['鶏肉', '玉ねぎ', 'カレールー']
    })
  });

  const data = await response.json();
  console.log(data);
};

// 栄養推移取得
const getTrend = async () => {
  const response = await fetch(
    '/api/v1/meal-history/nutrition-trend?user_id=user123&nutrient=calories&days=30'
  );

  const data = await response.json();
  console.log(data);
};
```

---

## データ保存形式

食事履歴は `data/meal_history.json` に保存されます。

```json
[
  {
    "id": "user123_1702195800.123",
    "user_id": "user123",
    "recipe_id": "recipe456",
    "recipe_name": "チキンカレー",
    "meal_type": "lunch",
    "consumed_at": "2025-12-10T12:30:00",
    "servings": 2.0,
    "nutrition": {
      "calories": 850.0,
      "protein": 35.0,
      "fat": 28.0,
      "carbohydrates": 95.0
    },
    "ingredients": ["鶏肉", "玉ねぎ", "カレールー"],
    "created_at": "2025-12-10T12:30:15.123456"
  }
]
```

---

## 推奨栄養摂取量（成人1日あたり）

| 栄養素 | 目標値 | 単位 |
|-------|--------|------|
| calories | 2000 | kcal |
| protein | 60 | g |
| fat | 55 | g |
| carbohydrates | 300 | g |
| fiber | 20 | g |
| sodium | 2300 | mg |
| calcium | 700 | mg |
| iron | 8 | mg |
| vitamin_c | 100 | mg |

※ 性別・年齢・活動量により異なります。

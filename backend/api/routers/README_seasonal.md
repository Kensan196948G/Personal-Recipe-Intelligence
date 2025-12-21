# 季節・時間帯別レシピ推薦API

Personal Recipe Intelligence の季節・時間帯に応じたレシピ推薦機能のドキュメントです。

## 概要

このAPIは以下の機能を提供します：

- 現在の季節に合ったレシピ推薦
- 時間帯に応じたレシピ推薦（朝食/昼食/夕食/夜食）
- 旬の食材を使ったレシピ推薦
- 気温に応じたレシピ推薦（温かい/冷たい料理）
- 総合的なレシピ推薦（複数条件の組み合わせ）

## エンドポイント

### 1. 季節別推薦

**GET /api/v1/seasonal/now**

現在の季節に合ったレシピを推薦します。

**パラメータ:**
- `limit` (optional): 取得件数（デフォルト: 10、最大: 100）

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "season": "spring",
    "season_name_ja": "春",
    "recommendations": [
      {
        "id": 1,
        "title": "たけのこご飯",
        "description": "春の味覚、たけのこを使った炊き込みご飯",
        "ingredients": [...],
        "tags": ["和食", "ご飯", "春"],
        "season_score": 3
      }
    ],
    "count": 1
  },
  "error": null
}
```

### 2. 時間帯別推薦

**GET /api/v1/seasonal/meal-time**

現在の時間帯に合ったレシピを推薦します。

**パラメータ:**
- `limit` (optional): 取得件数（デフォルト: 10、最大: 100）

**時間帯の判定基準:**
- 朝食 (breakfast): 5:00 - 9:59
- 昼食 (lunch): 10:00 - 14:59
- 夕食 (dinner): 15:00 - 21:59
- 夜食 (late_night): 22:00 - 4:59

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "meal_time": "breakfast",
    "meal_time_name_ja": "朝食",
    "current_time": "2024-12-11 07:30:00",
    "recommendations": [
      {
        "id": 5,
        "title": "卵かけご飯",
        "description": "シンプルで美味しい朝食の定番",
        "tags": ["和食", "朝食", "簡単"],
        "meal_time_score": 2
      }
    ],
    "count": 1
  },
  "error": null
}
```

### 3. 旬の食材レシピ推薦

**GET /api/v1/seasonal/ingredients**

旬の食材を使ったレシピを推薦します。

**パラメータ:**
- `season` (optional): 季節（spring/summer/autumn/winter）
- `limit` (optional): 取得件数（デフォルト: 10、最大: 100）

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "season": "spring",
    "season_name_ja": "春",
    "ingredients": [
      "たけのこ",
      "菜の花",
      "新玉ねぎ",
      "新じゃがいも",
      "春キャベツ",
      "アスパラガス"
    ],
    "recipes": [...],
    "count": 5
  },
  "error": null
}
```

### 4. 気温別推薦

**GET /api/v1/seasonal/temperature**

気温に応じたレシピを推薦します。

**パラメータ:**
- `temperature` (required): 気温（摂氏）
- `limit` (optional): 取得件数（デフォルト: 10、最大: 100）

**判定基準:**
- 25度以上: 冷たい料理推薦
- 25度未満: 温かい料理推薦

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "temperature": 30.0,
    "category": "hot (冷たい料理)",
    "recommendations": [
      {
        "id": 2,
        "title": "冷やし中華",
        "tags": ["冷たい", "夏"],
        "temperature_score": 4,
        "recommended_category": "hot"
      }
    ],
    "count": 1
  },
  "error": null
}
```

### 5. 総合推薦

**GET /api/v1/seasonal/comprehensive**

季節・時間帯・気温を総合的に考慮してレシピを推薦します。

**パラメータ:**
- `season` (optional): 季節（spring/summer/autumn/winter）
- `meal_time` (optional): 食事時間（breakfast/lunch/dinner/late_night）
- `temperature` (optional): 気温（摂氏）
- `limit` (optional): 取得件数（デフォルト: 10、最大: 100）

**スコア計算式:**
```
total_score = (season_score × 3) + (meal_time_score × 2) + temperature_score
```

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "season": "winter (冬)",
    "meal_time": "dinner (夕食)",
    "temperature": 5.0,
    "recommendations": [
      {
        "id": 4,
        "title": "白菜と豚肉の鍋",
        "total_score": 12,
        "season_score": 2,
        "meal_time_score": 1,
        "temperature_score": 4
      }
    ],
    "count": 1
  },
  "error": null
}
```

### 6. 機能情報取得

**GET /api/v1/seasonal/info**

季節推薦機能の現在の状態と利用可能なオプションを取得します。

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "current_season": {
      "value": "winter",
      "name_ja": "冬",
      "ingredients": ["白菜", "大根", "ほうれん草", ...]
    },
    "current_meal_time": {
      "value": "dinner",
      "name_ja": "夕食"
    },
    "current_time": "2024-12-11 18:30:00",
    "available_seasons": ["spring", "summer", "autumn", "winter"],
    "available_meal_times": ["breakfast", "lunch", "dinner", "late_night"]
  },
  "error": null
}
```

## 季節データ

### 春 (Spring)
たけのこ、菜の花、新玉ねぎ、新じゃがいも、春キャベツ、アスパラガス、そらまめ、さやえんどう、いちご、たらの芽

### 夏 (Summer)
トマト、きゅうり、なす、ピーマン、ゴーヤ、オクラ、枝豆、とうもろこし、すいか、ししとう

### 秋 (Autumn)
さつまいも、きのこ、栗、かぼちゃ、さんま、さといも、ぎんなん、柿、なし、ぶどう

### 冬 (Winter)
白菜、大根、ほうれん草、ねぎ、小松菜、春菊、れんこん、ごぼう、みかん、ブロッコリー

## 使用例

### curlでの使用例

```bash
# 現在の季節のおすすめを取得
curl "http://localhost:8000/api/v1/seasonal/now?limit=5"

# 時間帯別のおすすめを取得
curl "http://localhost:8000/api/v1/seasonal/meal-time"

# 春の旬の食材レシピを取得
curl "http://localhost:8000/api/v1/seasonal/ingredients?season=spring"

# 気温30度のおすすめを取得
curl "http://localhost:8000/api/v1/seasonal/temperature?temperature=30"

# 総合推薦を取得
curl "http://localhost:8000/api/v1/seasonal/comprehensive?season=winter&meal_time=dinner&temperature=5"

# 機能情報を取得
curl "http://localhost:8000/api/v1/seasonal/info"
```

### Pythonでの使用例

```python
import requests

base_url = "http://localhost:8000/api/v1/seasonal"

# 現在の季節のおすすめを取得
response = requests.get(f"{base_url}/now", params={"limit": 5})
data = response.json()
print(data)

# 総合推薦を取得
params = {
    "season": "winter",
    "meal_time": "dinner",
    "temperature": 5.0,
    "limit": 10
}
response = requests.get(f"{base_url}/comprehensive", params=params)
data = response.json()
print(data)
```

## エラーハンドリング

APIはエラー時に以下の形式でレスポンスを返します：

```json
{
  "status": "error",
  "data": null,
  "error": "エラーメッセージ"
}
```

### よくあるエラー

- **400 Bad Request**: 無効な季節や食事時間の指定
- **500 Internal Server Error**: サーバー内部エラー

## テスト

```bash
# ユニットテストの実行
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
python -m pytest backend/tests/test_seasonal_service.py -v

# カバレッジ付きテスト
python -m pytest backend/tests/test_seasonal_service.py --cov=backend/services/seasonal_service --cov-report=html
```

## 開発ノート

### アーキテクチャ

```
backend/
├── services/
│   └── seasonal_service.py      # ビジネスロジック
├── api/
│   └── routers/
│       └── seasonal.py          # APIエンドポイント
└── tests/
    └── test_seasonal_service.py # ユニットテスト
```

### データソース

現在はサンプルデータを使用していますが、実際の運用では以下のように変更します：

```python
# データベースからレシピを取得
from backend.database import get_db_session
from backend.models import Recipe

def get_seasonal_service() -> SeasonalService:
    session = get_db_session()
    recipes = session.query(Recipe).all()
    recipe_data = [recipe.to_dict() for recipe in recipes]
    return SeasonalService(recipe_data=recipe_data)
```

### 拡張予定機能

- 地域別の旬の食材データ
- ユーザーの好み学習による推薦精度向上
- 天気情報APIとの連携
- 栄養バランスを考慮した推薦
- アレルギー情報の考慮

## ライセンス

MIT License

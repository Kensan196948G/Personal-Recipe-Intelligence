# カレンダー連携機能 - クイックスタートガイド

Personal Recipe Intelligence のカレンダー連携機能により、献立計画の管理、買い物リストの自動生成、栄養バランスの計算が可能になります。

## 主な機能

1. **献立カレンダー**: 週間/月間表示でレシピを管理
2. **ドラッグ&ドロップ**: 直感的な献立計画の作成
3. **買い物リスト**: 献立から材料を自動集約
4. **栄養バランス**: カロリー・栄養素の自動計算
5. **iCal エクスポート**: Google Calendar などに同期

## セットアップ

### 1. セットアップスクリプトの実行

```bash
chmod +x setup-calendar.sh
./setup-calendar.sh
```

### 2. 手動セットアップ（スクリプトが使えない場合）

```bash
# 依存関係のインストール
pip install icalendar python-dateutil

# ディレクトリ構造の作成
mkdir -p backend/api/routers backend/services backend/tests
mkdir -p frontend/components data docs

# データファイルの初期化
echo "[]" > data/meal_plans.json
```

## クイックスタート

### API の使用

1. **献立計画を作成**

```bash
curl -X POST http://localhost:8000/api/v1/calendar/plans \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-15",
    "meal_type": "昼食",
    "recipe_id": 1,
    "recipe_name": "カレーライス",
    "servings": 2
  }'
```

2. **献立計画を取得**

```bash
curl http://localhost:8000/api/v1/calendar/plans?start_date=2025-12-15&end_date=2025-12-21
```

3. **買い物リストを取得**

```bash
curl "http://localhost:8000/api/v1/calendar/shopping-list?start_date=2025-12-15&end_date=2025-12-21"
```

4. **栄養バランスを取得**

```bash
curl "http://localhost:8000/api/v1/calendar/nutrition?start_date=2025-12-15&end_date=2025-12-21"
```

5. **iCal ファイルをダウンロード**

```bash
curl "http://localhost:8000/api/v1/calendar/export/ical" -o meal_calendar.ics
```

### フロントエンドの使用

```jsx
// App.jsx または main.jsx に追加
import MealCalendar from './components/MealCalendar';

function App() {
  return (
    <div className="App">
      <h1>献立カレンダー</h1>
      <MealCalendar />
    </div>
  );
}
```

## ファイル構成

```
Personal-Recipe-Intelligence/
├── backend/
│   ├── services/
│   │   ├── calendar_service.py       # カレンダーサービス
│   │   └── meal_plan_service.py      # 献立計画サービス
│   ├── api/
│   │   └── routers/
│   │       └── calendar.py           # API ルーター
│   └── tests/
│       ├── test_calendar_service.py  # カレンダーサービステスト
│       └── test_meal_plan_service.py # 献立計画サービステスト
├── frontend/
│   └── components/
│       ├── MealCalendar.jsx          # カレンダーコンポーネント
│       └── MealCalendar.css          # スタイルシート
├── data/
│   ├── meal_plans.json               # 献立計画データ
│   └── recipes.json                  # レシピデータ
├── docs/
│   └── CALENDAR_INTEGRATION.md       # 詳細ドキュメント
├── setup-calendar.sh                 # セットアップスクリプト
└── README_CALENDAR.md                # このファイル
```

## API エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/api/v1/calendar/plans` | 献立計画一覧を取得 |
| POST | `/api/v1/calendar/plans` | 献立計画を作成 |
| PUT | `/api/v1/calendar/plans/{id}` | 献立計画を更新 |
| DELETE | `/api/v1/calendar/plans/{id}` | 献立計画を削除 |
| GET | `/api/v1/calendar/export/ical` | iCal ファイルをエクスポート |
| GET | `/api/v1/calendar/shopping-list` | 買い物リストを取得 |
| GET | `/api/v1/calendar/nutrition` | 栄養バランスを取得 |
| GET | `/api/v1/calendar/weekly-summary` | 週間サマリーを取得 |
| GET | `/api/v1/calendar/week/{date}` | 週間献立を取得 |
| GET | `/api/v1/calendar/month/{year}/{month}` | 月間献立を取得 |

## データモデル

### 献立計画 (MealPlan)

```json
{
  "id": 1,
  "date": "2025-12-15",
  "meal_type": "昼食",
  "recipe_id": 123,
  "recipe_name": "カレーライス",
  "servings": 2,
  "notes": "辛口で作る",
  "created_at": "2025-12-10T10:00:00",
  "updated_at": "2025-12-10T10:00:00"
}
```

### 買い物リストアイテム

```json
{
  "ingredient": "玉ねぎ",
  "total_quantity": 3.0,
  "unit": "個",
  "category": "野菜",
  "recipes": ["カレーライス", "ハンバーグ"]
}
```

### 栄養バランス

```json
{
  "total_calories": 10000,
  "avg_daily_calories": 1428.57,
  "total_protein": 350,
  "total_fat": 280,
  "total_carbs": 1200,
  "days_planned": 7
}
```

## テストの実行

```bash
# 全テストを実行
pytest backend/tests/ -v

# カレンダーサービスのみ
pytest backend/tests/test_calendar_service.py -v

# 献立計画サービスのみ
pytest backend/tests/test_meal_plan_service.py -v

# カバレッジレポート付き
pytest backend/tests/ -v --cov=backend/services --cov-report=html
```

## 使用例

### Python コードからの使用

```python
from backend.services.calendar_service import CalendarService, MealPlanModel
from backend.services.meal_plan_service import MealPlanService
from datetime import date

# サービスの初期化
calendar_service = CalendarService()
meal_plan_service = MealPlanService()

# 献立計画を作成
plan = MealPlanModel(
    date=date(2025, 12, 15),
    meal_type="昼食",
    recipe_id=1,
    recipe_name="カレーライス",
    servings=2
)
created_plan = calendar_service.create_plan(plan)

# 買い物リストを生成
plans = calendar_service.get_plans()
plans_dict = [p.dict() for p in plans]
shopping_list = meal_plan_service.generate_shopping_list(
    plans_dict,
    date(2025, 12, 15),
    date(2025, 12, 21)
)

# iCal エクスポート
ical_content = calendar_service.export_to_ical()
with open("meal_calendar.ics", "w") as f:
    f.write(ical_content)
```

### JavaScript (React) からの使用

```jsx
import { useState, useEffect } from 'react';

function CalendarPage() {
  const [plans, setPlans] = useState([]);

  // 献立計画を取得
  const fetchPlans = async () => {
    const response = await fetch('/api/v1/calendar/plans');
    const result = await response.json();
    if (result.status === 'ok') {
      setPlans(result.data);
    }
  };

  // 献立計画を作成
  const createPlan = async (planData) => {
    const response = await fetch('/api/v1/calendar/plans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(planData)
    });
    const result = await response.json();
    if (result.status === 'ok') {
      await fetchPlans(); // リロード
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  return <MealCalendar plans={plans} onCreate={createPlan} />;
}
```

## トラブルシューティング

### 買い物リストが生成されない

レシピデータに `ingredients` フィールドが含まれているか確認してください：

```json
{
  "id": 1,
  "name": "カレーライス",
  "ingredients": [
    {"name": "玉ねぎ", "quantity": 2, "unit": "個", "category": "野菜"}
  ]
}
```

### 栄養バランスが表示されない

レシピデータに `nutrition` フィールドが含まれているか確認してください：

```json
{
  "id": 1,
  "name": "カレーライス",
  "nutrition": {
    "calories": 800,
    "protein": 30,
    "fat": 25,
    "carbs": 100
  }
}
```

### iCal ファイルが開けない

- ファイル拡張子が `.ics` であることを確認
- 対応アプリケーション（Google Calendar、Outlook、Apple Calendar など）で開く

## カスタマイズ

### 食事タイプのカスタマイズ

`backend/services/calendar_service.py` で食事タイプを追加：

```python
meal_type_order = {
    "朝食": 0,
    "昼食": 1,
    "夕食": 2,
    "間食": 3,
    "夜食": 4  # 追加
}
```

### カテゴリのカスタマイズ

レシピデータの `category` フィールドで材料カテゴリを定義：

```json
{
  "name": "玉ねぎ",
  "quantity": 2,
  "unit": "個",
  "category": "野菜"
}
```

## 今後の機能拡張

- Google Calendar API による双方向同期
- 献立のテンプレート保存
- AI による献立自動提案
- 栄養バランスのグラフ表示
- アレルギー情報の考慮
- 予算管理機能

## 関連ドキュメント

- 詳細な API ドキュメント: `/docs/CALENDAR_INTEGRATION.md`
- プロジェクト全体の README: `/README.md`
- プロジェクト開発ルール: `/CLAUDE.md`

## ライセンス

MIT License

## サポート

問題が発生した場合は、GitHub Issues で報告してください。

# カレンダー連携機能 ドキュメント

## 概要

Personal Recipe Intelligence のカレンダー連携機能は、献立計画の作成・管理、買い物リスト自動生成、栄養バランス計算、iCal エクスポートを提供します。

## 機能一覧

### 1. 献立計画管理

- 日付・食事タイプ（朝食/昼食/夕食/間食）ごとにレシピを割り当て
- 人数調整機能
- メモ機能
- 週間/月間ビュー

### 2. 買い物リスト自動生成

- 指定期間の献立から必要な材料を自動集約
- 人数に応じた数量計算
- カテゴリ別整理

### 3. 栄養バランス計算

- カロリー合計・平均
- タンパク質・脂質・炭水化物の集計
- 週間サマリー

### 4. iCal エクスポート

- 標準 iCalendar 形式でエクスポート
- Google Calendar、Outlook、Apple Calendar に対応
- 期間指定可能

## API エンドポイント

### 献立計画の取得

```
GET /api/v1/calendar/plans
```

**クエリパラメータ:**
- `start_date` (optional): 開始日 (YYYY-MM-DD)
- `end_date` (optional): 終了日 (YYYY-MM-DD)
- `meal_type` (optional): 食事タイプでフィルタ

**レスポンス例:**
```json
{
  "status": "ok",
  "data": [
    {
      "id": 1,
      "date": "2025-12-15",
      "meal_type": "昼食",
      "recipe_id": 123,
      "recipe_name": "カレーライス",
      "servings": 2,
      "notes": null,
      "created_at": "2025-12-10T10:00:00",
      "updated_at": "2025-12-10T10:00:00"
    }
  ],
  "error": null
}
```

### 献立計画の作成

```
POST /api/v1/calendar/plans
```

**リクエストボディ:**
```json
{
  "date": "2025-12-15",
  "meal_type": "昼食",
  "recipe_id": 123,
  "recipe_name": "カレーライス",
  "servings": 2,
  "notes": "辛口で作る"
}
```

### 献立計画の更新

```
PUT /api/v1/calendar/plans/{plan_id}
```

**リクエストボディ:**
```json
{
  "servings": 4,
  "notes": "更新されたメモ"
}
```

### 献立計画の削除

```
DELETE /api/v1/calendar/plans/{plan_id}
```

### iCal エクスポート

```
GET /api/v1/calendar/export/ical
```

**クエリパラメータ:**
- `start_date` (optional): 開始日
- `end_date` (optional): 終了日

**レスポンス:**
- Content-Type: `text/calendar`
- ファイル名: `meal_calendar.ics`

### 買い物リスト取得

```
GET /api/v1/calendar/shopping-list?start_date=2025-12-15&end_date=2025-12-21
```

**レスポンス例:**
```json
{
  "status": "ok",
  "data": [
    {
      "ingredient": "玉ねぎ",
      "total_quantity": 3.0,
      "unit": "個",
      "category": "野菜",
      "recipes": ["カレーライス", "ハンバーグ"]
    }
  ]
}
```

### 栄養バランス取得

```
GET /api/v1/calendar/nutrition?start_date=2025-12-15&end_date=2025-12-21
```

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "total_calories": 10000,
    "avg_daily_calories": 1428.57,
    "total_protein": 350,
    "total_fat": 280,
    "total_carbs": 1200,
    "days_planned": 7
  }
}
```

### 週間サマリー取得

```
GET /api/v1/calendar/weekly-summary?target_date=2025-12-15
```

### 週間献立取得

```
GET /api/v1/calendar/week/2025-12-15
```

### 月間献立取得

```
GET /api/v1/calendar/month/2025/12
```

## フロントエンド使用方法

### MealCalendar コンポーネントの統合

```jsx
import MealCalendar from './components/MealCalendar';

function App() {
  return (
    <div>
      <MealCalendar />
    </div>
  );
}
```

### 機能

1. **カレンダービュー切り替え**
   - 週表示：1週間分の献立を表示
   - 月表示：1ヶ月分の献立を表示

2. **ドラッグ&ドロップ**
   - レシピ一覧からカレンダーにドラッグしてレシピを追加
   - 日付と食事タイプを指定して配置

3. **買い物リスト表示**
   - 週表示時に自動生成される
   - 材料がカテゴリ別に整理される

4. **栄養バランス表示**
   - 週表示時に自動計算される
   - 総カロリー、平均カロリー、三大栄養素を表示

## データ構造

### 献立計画データモデル

```python
class MealPlanModel(BaseModel):
  id: Optional[int] = None
  date: date
  meal_type: str  # 朝食/昼食/夕食/間食
  recipe_id: Optional[int] = None
  recipe_name: str
  servings: int = 1
  notes: Optional[str] = None
  created_at: Optional[datetime] = None
  updated_at: Optional[datetime] = None
```

### レシピデータ要件

買い物リストと栄養計算を正しく動作させるため、レシピデータに以下の構造を含める必要があります：

```json
{
  "id": 1,
  "name": "カレーライス",
  "servings": 4,
  "ingredients": [
    {
      "name": "玉ねぎ",
      "quantity": 2,
      "unit": "個",
      "category": "野菜"
    }
  ],
  "nutrition": {
    "calories": 800,
    "protein": 30,
    "fat": 25,
    "carbs": 100,
    "fiber": 5,
    "salt": 2
  }
}
```

## ファイル構成

```
backend/
├── services/
│   ├── calendar_service.py        # カレンダーサービス
│   └── meal_plan_service.py       # 献立計画サービス
├── api/
│   └── routers/
│       └── calendar.py            # カレンダー API ルーター
└── tests/
    ├── test_calendar_service.py   # カレンダーサービステスト
    └── test_meal_plan_service.py  # 献立計画サービステスト

frontend/
└── components/
    ├── MealCalendar.jsx           # カレンダーコンポーネント
    └── MealCalendar.css           # スタイルシート

data/
└── meal_plans.json                # 献立計画データ（自動生成）
```

## セットアップ

### 1. 依存関係のインストール

```bash
# Python 依存関係
pip install icalendar

# または requirements.txt から
pip install -r requirements.txt
```

### 2. API ルーターの登録

FastAPI アプリケーションにルーターを追加：

```python
from fastapi import FastAPI
from backend.api.routers import calendar

app = FastAPI()
app.include_router(calendar.router)
```

### 3. フロントエンドの起動

```bash
cd frontend
npm install
npm run dev
```

## テストの実行

```bash
# カレンダーサービステスト
pytest backend/tests/test_calendar_service.py -v

# 献立計画サービステスト
pytest backend/tests/test_meal_plan_service.py -v

# 全テスト
pytest backend/tests/ -v --cov=backend/services
```

## Google Calendar 連携準備

`calendar_service.prepare_google_calendar_event()` メソッドを使用して、Google Calendar API 用のイベントデータを準備できます。

### Google Calendar API の設定手順

1. Google Cloud Console でプロジェクトを作成
2. Google Calendar API を有効化
3. OAuth 2.0 クライアント ID を作成
4. `.env` に認証情報を追加

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 実装例（将来の拡張）

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def sync_to_google_calendar(plan: MealPlanModel):
    event = calendar_service.prepare_google_calendar_event(plan)

    service = build('calendar', 'v3', credentials=creds)
    event = service.events().insert(
        calendarId='primary',
        body=event
    ).execute()
```

## トラブルシューティング

### 買い物リストが空になる

- レシピデータに `ingredients` フィールドが含まれているか確認
- 献立計画に `recipe_id` が設定されているか確認
- 日付範囲が正しいか確認

### 栄養バランスが計算されない

- レシピデータに `nutrition` フィールドが含まれているか確認
- 栄養情報が数値型で保存されているか確認

### iCal ファイルが開けない

- ファイル拡張子が `.ics` であることを確認
- ダウンロード時に Content-Type が `text/calendar` であることを確認

## 今後の拡張予定

- [ ] Google Calendar API による双方向同期
- [ ] Outlook Calendar 対応
- [ ] 献立のテンプレート保存機能
- [ ] AI による献立自動提案の改善
- [ ] 栄養バランスの可視化（グラフ表示）
- [ ] アレルギー情報の考慮
- [ ] 予算管理機能

## ライセンス

MIT License

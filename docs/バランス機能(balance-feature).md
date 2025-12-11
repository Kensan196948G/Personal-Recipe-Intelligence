# 食事バランス可視化機能 ドキュメント

## 概要

Personal Recipe Intelligence に実装された食事バランス可視化機能は、レシピや1日の食事の栄養バランスを解析し、視覚的に表示する機能です。

## 主な機能

### 1. PFCバランス計算
- タンパク質（Protein）、脂質（Fat）、炭水化物（Carbohydrate）のカロリー比率を計算
- 日本人の理想比率（P:15%, F:25%, C:60%）との比較
- バランススコア算出（100点満点）
- 改善アドバイスの自動生成

### 2. 1日の食事バランス評価
- 複数の食事を合計し、1日全体のバランスを評価
- 日本人の食事摂取基準との比較
- 各栄養素の充足率計算
- 総合スコアと評価レベルの判定

### 3. 栄養バランススコア
- レシピ単体の栄養バランスを評価
- PFCスコアと栄養素スコアの総合評価
- 健康度判定（is_healthy フラグ）

### 4. グラフ用データ出力
- **円グラフ**: PFC比率の可視化
- **棒グラフ**: 栄養素充足率の表示
- **レーダーチャート**: バランス評価の可視化

## API エンドポイント

### 1. レシピのバランス評価取得

```
GET /api/v1/balance/{recipe_id}
```

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "recipe_id": 1,
    "evaluation": {
      "nutrition": {
        "calories": 650,
        "protein": 25,
        "fat": 20,
        "carbs": 85,
        "fiber": 5,
        "salt": 2.5
      },
      "pfc_balance": {
        "protein_ratio": 0.154,
        "fat_ratio": 0.277,
        "carbs_ratio": 0.569,
        "balance_score": 85.3,
        "is_balanced": true,
        "recommendations": ["理想的なPFCバランスです"],
        "pie_chart_data": [...]
      },
      "score": {
        "overall_score": 82.5,
        "pfc_score": 85.3,
        "evaluation": "good",
        "is_healthy": true
      }
    }
  }
}
```

### 2. 1日の食事バランス評価

```
POST /api/v1/balance/daily
```

**リクエストボディ:**
```json
{
  "meals": [
    {
      "calories": 650,
      "protein": 20,
      "fat": 18,
      "carbs": 100,
      "fiber": 5,
      "salt": 2.5
    },
    {
      "calories": 700,
      "protein": 22,
      "fat": 20,
      "carbs": 105,
      "fiber": 6,
      "salt": 2.5
    }
  ],
  "target_date": "2025-12-11"
}
```

**レスポンス例:**
```json
{
  "status": "ok",
  "data": {
    "target_date": "2025-12-11",
    "meal_count": 2,
    "evaluation": {
      "total": {
        "calories": 1350,
        "protein": 42,
        "fat": 38,
        "carbs": 205,
        "fiber": 11,
        "salt": 5
      },
      "fulfillment": {
        "calories": 67.5,
        "protein": 70.0,
        "fat": 69.1,
        "carbs": 68.3,
        "fiber": 55.0,
        "salt": 66.7
      },
      "overall_score": 72.3,
      "evaluation_level": "good",
      "recommendations": [...],
      "bar_chart_data": [...],
      "radar_chart_data": [...]
    }
  }
}
```

### 3. PFCバランス取得

```
GET /api/v1/balance/pfc/{recipe_id}
```

### 4. バランススコア計算

```
POST /api/v1/balance/score
```

**リクエストボディ:**
```json
{
  "nutrition": {
    "calories": 650,
    "protein": 25,
    "fat": 20,
    "carbs": 85,
    "fiber": 5,
    "salt": 2.5
  }
}
```

### 5. 食事摂取基準取得

```
GET /api/v1/balance/reference
```

### 6. レシピ比較

```
POST /api/v1/balance/compare
```

**リクエストボディ:**
```json
[
  {"calories": 650, "protein": 25, "fat": 20, "carbs": 85, "fiber": 5, "salt": 2.5},
  {"calories": 800, "protein": 30, "fat": 35, "carbs": 90, "fiber": 4, "salt": 3.5}
]
```

## フロントエンドコンポーネント

### 使用例

```jsx
import {
  BalanceDashboard,
  DailyBalanceDashboard,
  PFCPieChart,
  NutritionBarChart,
  BalanceRadarChart,
  BalanceScore
} from './components/BalanceVisualization';
import './styles/balance.css';

// レシピ単体のバランス表示
function RecipePage({ recipeId }) {
  return <BalanceDashboard recipeId={recipeId} />;
}

// 1日の食事バランス表示
function DailyPage({ meals, date }) {
  return <DailyBalanceDashboard meals={meals} targetDate={date} />;
}

// 個別グラフの使用
function CustomView({ pfc_data, bar_data, radar_data, score }) {
  return (
    <div>
      <BalanceScore score={score.overall_score} evaluation={score.evaluation} />
      <PFCPieChart data={pfc_data} />
      <NutritionBarChart data={bar_data} />
      <BalanceRadarChart data={radar_data} />
    </div>
  );
}
```

## 評価基準

### 日本人の食事摂取基準（成人平均）

```python
DAILY_REFERENCE = {
  "calories": 2000,   # kcal
  "protein": 60,      # g
  "fat": 55,          # g
  "carbs": 300,       # g
  "fiber": 20,        # g
  "salt": 7.5         # g
}
```

### PFC理想比率（カロリーベース）

```python
PFC_IDEAL_RATIO = {
  "protein": 0.15,    # 15%
  "fat": 0.25,        # 25%
  "carbs": 0.60       # 60%
}
```

### スコア評価レベル

- **excellent** (90点以上): 優秀なバランス
- **good** (75-89点): 良好なバランス
- **fair** (60-74点): 普通のバランス
- **needs_improvement** (60点未満): 改善が必要

### 充足率の評価

- **80-120%**: 適正範囲（緑）
- **60-79% / 121-140%**: 注意（黄）
- **60%未満 / 140%超**: 要改善（赤）

## テスト

### サービス層のテスト

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pytest backend/tests/test_balance_service.py -v
```

### API層のテスト

```bash
pytest backend/tests/test_balance_api.py -v
```

### カバレッジ確認

```bash
pytest backend/tests/test_balance_*.py --cov=backend/services/balance_service --cov=backend/api/routers/balance --cov-report=html
```

## 実装ファイル

### バックエンド

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/balance_service.py`
  - PFCバランス計算
  - 1日の食事バランス評価
  - スコア算出ロジック

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/api/routers/balance.py`
  - REST API エンドポイント
  - Pydantic バリデーション
  - エラーハンドリング

### テスト

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_balance_service.py`
  - サービス層のユニットテスト
  - 60以上のテストケース

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_balance_api.py`
  - API層の統合テスト
  - リクエスト/レスポンスのバリデーション

### フロントエンド

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend/components/BalanceVisualization.jsx`
  - React コンポーネント
  - PFC円グラフ
  - 栄養充足率棒グラフ
  - レーダーチャート
  - スコア表示

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend/styles/balance.css`
  - スタイルシート
  - レスポンシブデザイン
  - ダークモード対応

## カスタマイズ

### 基準値の変更

```python
# backend/services/balance_service.py の冒頭で変更可能
DAILY_REFERENCE = {
  "calories": 2200,  # 変更例: 活動量が多い場合
  "protein": 70,
  # ...
}
```

### スコア計算ロジックの調整

```python
# BalanceService._calculate_overall_score() メソッドで調整
def _calculate_overall_score(fulfillment: Dict[str, float]) -> float:
  # スコア計算ロジックをカスタマイズ
  pass
```

## 注意事項

1. **モックデータ**: 現在、レシピIDからの栄養データ取得はモック実装です。実際のDB連携が必要です。

2. **個人差**: 食事摂取基準は年齢・性別・活動量によって異なります。現在は成人平均値を使用しています。

3. **塩分**: 塩分は「食塩相当量」として扱っています。

4. **ブラウザ対応**: SVGを使用しているため、IE11以下は非対応です。

## 今後の拡張

- [ ] 年齢・性別・活動量に応じた基準値の自動調整
- [ ] ビタミン・ミネラルの評価追加
- [ ] アレルゲン情報の表示
- [ ] 週間・月間のバランス推移グラフ
- [ ] AI による献立提案
- [ ] PDF レポート出力

## ライセンス

MIT License

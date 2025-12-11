# 食事履歴分析機能 セットアップガイド

## 概要

Phase 10-1 で実装された食事履歴分析機能のセットアップ手順と使用方法を説明します。

## 実装ファイル一覧

### バックエンド

1. **backend/services/meal_history_service.py**
   - 食事履歴管理サービス
   - 栄養摂取量集計
   - 傾向分析ロジック

2. **backend/api/routers/meal_history.py**
   - REST API エンドポイント
   - リクエスト/レスポンスモデル

3. **backend/tests/test_meal_history_service.py**
   - サービスのユニットテスト

### フロントエンド

1. **frontend/components/NutritionTrend.jsx**
   - 栄養推移グラフコンポーネント
   - Recharts を使用した可視化

2. **frontend/pages/MealHistoryPage.jsx**
   - 食事履歴ページ（統合UI）

### ドキュメント

1. **docs/meal-history-api.md**
   - API 仕様書

2. **docs/meal-history-setup.md**
   - 本ファイル

---

## セットアップ手順

### 1. 依存パッケージのインストール

#### Python（バックエンド）

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# 既存の requirements.txt に追加（既にある場合はスキップ）
pip install fastapi uvicorn pydantic
```

#### Node.js（フロントエンド）

```bash
cd frontend

# Recharts グラフライブラリをインストール
bun add recharts

# React関連（未インストールの場合）
bun add react react-dom
```

### 2. ディレクトリ構成の確認

```
personal-recipe-intelligence/
├── backend/
│   ├── api/
│   │   └── routers/
│   │       └── meal_history.py       # ✓ 作成済み
│   ├── services/
│   │   └── meal_history_service.py   # ✓ 作成済み
│   └── tests/
│       └── test_meal_history_service.py  # ✓ 作成済み
├── frontend/
│   ├── components/
│   │   └── NutritionTrend.jsx        # ✓ 作成済み
│   └── pages/
│       └── MealHistoryPage.jsx       # ✓ 作成済み
├── data/                              # 自動生成される
│   └── meal_history.json
└── docs/
    ├── meal-history-api.md           # ✓ 作成済み
    └── meal-history-setup.md         # ✓ 本ファイル
```

### 3. API ルーターの登録

FastAPI アプリケーションにルーターを追加します。

**backend/main.py** または **backend/api/main.py** を編集：

```python
from fastapi import FastAPI
from backend.api.routers import meal_history  # 追加

app = FastAPI(title="Personal Recipe Intelligence API")

# ルーター登録
app.include_router(meal_history.router)  # 追加

@app.get("/")
async def root():
    return {"message": "Personal Recipe Intelligence API"}
```

### 4. APIサーバーの起動

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# Uvicorn で起動
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

起動確認：
```bash
curl http://localhost:8000/api/v1/meal-history/daily/2025-12-10?user_id=test
```

### 5. フロントエンドのビルドと起動

```bash
cd frontend

# 開発サーバー起動
bun run dev

# または本番ビルド
bun run build
bun run preview
```

---

## テストの実行

### 単体テスト

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# pytest 実行
pytest backend/tests/test_meal_history_service.py -v

# カバレッジ計測
pytest backend/tests/test_meal_history_service.py --cov=backend/services --cov-report=html
```

### API テスト（手動）

```bash
# 食事記録
curl -X POST http://localhost:8000/api/v1/meal-history/record \
  -H "Content-Type: application/json" \
  -d '{
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
  }'

# 日別データ取得
curl "http://localhost:8000/api/v1/meal-history/daily/2025-12-10?user_id=user123"

# 傾向分析
curl "http://localhost:8000/api/v1/meal-history/trends?user_id=user123&days=30"

# 栄養推移
curl "http://localhost:8000/api/v1/meal-history/nutrition-trend?user_id=user123&nutrient=calories&days=30"
```

---

## 使用例

### 1. 食事記録を追加

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/meal-history/record",
    json={
        "user_id": "user123",
        "recipe_id": "recipe001",
        "recipe_name": "サラダチキン丼",
        "meal_type": "lunch",
        "servings": 1.0,
        "nutrition": {
            "calories": 450.0,
            "protein": 35.0,
            "fat": 8.0,
            "carbohydrates": 55.0,
            "fiber": 3.5,
            "sodium": 650.0
        },
        "ingredients": ["鶏むね肉", "レタス", "トマト", "ご飯"],
        "consumed_at": "2025-12-10T12:30:00"
    }
)

print(response.json())
```

### 2. 日別栄養摂取量を取得

```python
response = requests.get(
    "http://localhost:8000/api/v1/meal-history/daily/2025-12-10",
    params={"user_id": "user123"}
)

data = response.json()["data"]
print(f"合計カロリー: {data['total_nutrition']['calories']} kcal")
print(f"食事回数: {data['meal_count']}回")
```

### 3. フロントエンドコンポーネントの使用

```jsx
import React from 'react';
import MealHistoryPage from './pages/MealHistoryPage';

function App() {
  return (
    <div>
      <MealHistoryPage />
    </div>
  );
}

export default App;
```

---

## データ構造

### 食事記録（meal_history.json）

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
      "carbohydrates": 95.0,
      "fiber": 8.0,
      "sodium": 1200.0
    },
    "ingredients": ["鶏肉", "玉ねぎ", "にんじん", "カレールー"],
    "created_at": "2025-12-10T12:30:15.123456"
  }
]
```

---

## 機能一覧

### 実装済み機能

- ✓ 食事記録の保存
- ✓ 日別栄養摂取量の取得
- ✓ 週間栄養摂取量の取得
- ✓ 月間栄養摂取量の取得
- ✓ 栄養素推移の取得（グラフ用）
- ✓ 傾向分析（食材、レシピ、食事パターン）
- ✓ 栄養バランス評価
- ✓ 期間別サマリー
- ✓ 栄養推移グラフコンポーネント
- ✓ 統合UIページ

### 今後の拡張候補

- [ ] 複数ユーザー対応の認証機能
- [ ] 栄養目標のカスタマイズ
- [ ] レシピ推薦（栄養バランス最適化）
- [ ] エクスポート機能（CSV/PDF）
- [ ] 画像アップロード（食事写真）
- [ ] カレンダービュー
- [ ] 通知機能（栄養不足アラート）

---

## トラブルシューティング

### 問題: データが保存されない

```bash
# data ディレクトリの権限確認
ls -la data/

# 権限がない場合
chmod 755 data/
```

### 問題: API が 404 を返す

```bash
# ルーターが登録されているか確認
curl http://localhost:8000/docs

# Swagger UI でエンドポイントを確認
```

### 問題: グラフが表示されない

```bash
# Recharts がインストールされているか確認
cd frontend
bun list | grep recharts

# 再インストール
bun add recharts
```

### 問題: テストが失敗する

```bash
# 依存関係を確認
pip list | grep pytest

# pytest をインストール
pip install pytest pytest-cov

# テストを個別実行
pytest backend/tests/test_meal_history_service.py::TestMealHistoryService::test_record_meal_creates_record -v
```

---

## パフォーマンス最適化

### 大量データ対策

現在はJSON ファイルベースですが、データ量が増えた場合：

1. **SQLite へ移行**
   ```python
   # 将来的な実装例
   from sqlalchemy import create_engine
   engine = create_engine('sqlite:///data/meal_history.db')
   ```

2. **インデックスの追加**
   - user_id + consumed_at の複合インデックス

3. **ページネーション**
   - 大量の食事記録を分割取得

---

## セキュリティ考慮事項

1. **ユーザー認証**
   - 現在は user_id をパラメータで受け取る簡易実装
   - 本番環境では JWT トークン認証を推奨

2. **入力検証**
   - Pydantic でバリデーション済み
   - SQL インジェクション対策（SQLite 移行時）

3. **レート制限**
   - 個人用途のため未実装
   - 公開する場合は slowapi などで制限

---

## ライセンス

MIT License

---

## 参考資料

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Recharts Documentation](https://recharts.org/)
- [日本人の食事摂取基準（厚生労働省）](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/eiyou/syokuji_kijyun.html)

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|------|----------|---------|
| 2025-12-11 | 1.0.0 | Phase 10-1 実装完了 |

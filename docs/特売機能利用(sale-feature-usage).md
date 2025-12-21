# 特売情報連携機能 使用ガイド

## 概要

Personal Recipe Intelligence の特売情報連携機能は、スーパーのチラシから特売情報を抽出し、レシピとの連動や価格比較を実現します。

## 機能一覧

### 1. 特売情報管理
- チラシ画像からのOCR抽出
- 商品名・価格・カテゴリの自動分類
- 有効期限管理

### 2. レシピ連動
- 特売食材を使ったレシピ推薦
- 材料費見積もり
- 節約効果の可視化

### 3. 価格比較
- 店舗間の価格比較
- 割引率ランキング
- 最安値店舗の提示

## セットアップ

### 1. 依存関係のインストール

```bash
# Python 依存関係
pip install fastapi pydantic pytest python-multipart

# フロントエンド依存関係（React使用時）
cd frontend
npm install
# または
bun install
```

### 2. ディレクトリ構造の確認

```
personal-recipe-intelligence/
├── backend/
│   ├── services/
│   │   ├── sale_service.py       # 特売情報サービス
│   │   └── flyer_parser.py       # チラシパーサー
│   ├── api/
│   │   └── routers/
│   │       └── sale.py           # APIルーター
│   └── tests/
│       ├── test_sale_service.py  # サービステスト
│       └── test_flyer_parser.py  # パーサーテスト
├── frontend/
│   └── components/
│       └── SaleInfo.jsx          # UIコンポーネント
├── docs/
│   ├── sale-api-specification.md # API仕様書
│   └── sale-feature-usage.md     # 本ファイル
└── data/
    └── flyers/                   # チラシ画像保存先
```

### 3. FastAPIアプリケーションへの統合

```python
# backend/main.py または backend/app.py

from fastapi import FastAPI
from backend.api.routers import sale

app = FastAPI(title="Personal Recipe Intelligence")

# 特売情報ルーターを追加
app.include_router(sale.router)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 使用方法

### Python コードでの使用

#### 1. 特売情報の追加

```python
from backend.services.sale_service import SaleService, SaleItem, SaleCategory
from datetime import datetime, timedelta

service = SaleService()

# 特売商品を追加
sale_item = SaleItem(
  id="sale-001",
  store_name="イオン",
  product_name="たまねぎ",
  price=98.0,
  original_price=150.0,
  unit="個",
  category=SaleCategory.VEGETABLE,
  valid_from=datetime.now(),
  valid_until=datetime.now() + timedelta(days=3),
)

service.add_sale_item(sale_item)
```

#### 2. 特売情報の取得

```python
# すべての有効な特売情報
sales = service.get_active_sales()

# 店舗でフィルタ
sales = service.get_active_sales(store_name="イオン")

# カテゴリでフィルタ
sales = service.get_active_sales(category=SaleCategory.VEGETABLE)

# 割引率でフィルタ
sales = service.get_active_sales(min_discount=30.0)
```

#### 3. 価格比較

```python
# 「たまねぎ」の価格比較
comparison = service.compare_prices("たまねぎ")

for item in comparison:
  print(f"{item['store_name']}: ¥{item['price']} ({item['discount_rate']}% OFF)")
```

#### 4. レシピ材料費見積もり

```python
ingredients = ["たまねぎ", "にんじん", "豚肉", "じゃがいも"]
estimate = service.get_recipe_cost_estimate(ingredients)

print(f"合計金額: ¥{estimate['total_cost']}")
print(f"特売利用率: {estimate['coverage_rate']}%")
```

#### 5. チラシパース

```python
from backend.services.flyer_parser import FlyerParser

parser = FlyerParser()

# OCRテキストからパース
ocr_text = """
イオン 今週の特売
たまねぎ 98円
にんじん 3本 158円
"""

products = parser.parse_ocr_result(ocr_text, "イオン")
sale_items = parser.create_sale_items(products, "イオン", valid_days=3)

for item in sale_items:
  service.add_sale_item(item)
```

### API での使用

#### 1. 特売情報一覧取得

```bash
# すべての特売情報
curl "http://localhost:8000/api/v1/sales"

# 野菜カテゴリのみ
curl "http://localhost:8000/api/v1/sales?category=vegetable"

# 30%以上割引のみ
curl "http://localhost:8000/api/v1/sales?min_discount=30"
```

#### 2. チラシアップロード

```bash
curl -X POST "http://localhost:8000/api/v1/sales/upload" \
  -F "file=@flyer.jpg" \
  -F "store_name=イオン" \
  -F "valid_days=3"
```

#### 3. レシピ推薦

```bash
curl "http://localhost:8000/api/v1/sales/recommendations?max_results=5"
```

#### 4. 価格比較

```bash
curl "http://localhost:8000/api/v1/sales/price-compare?product_name=たまねぎ"
```

### フロントエンド（React）での使用

```jsx
import React from 'react';
import SaleInfo from './components/SaleInfo';

function App() {
  return (
    <div className="App">
      <h1>Personal Recipe Intelligence</h1>
      <SaleInfo />
    </div>
  );
}

export default App;
```

## テスト実行

### 全テスト実行

```bash
# プロジェクトルートで
pytest backend/tests/test_sale_service.py -v
pytest backend/tests/test_flyer_parser.py -v

# または全テスト
pytest backend/tests/ -v
```

### カバレッジ測定

```bash
pytest backend/tests/ --cov=backend/services --cov-report=html
```

## トラブルシューティング

### 問題: OCR精度が低い

**解決策:**
- チラシ画像の解像度を上げる（最低 300dpi 推奨）
- 画像の傾きを補正する
- OCRエンジンの設定を調整する

### 問題: 商品名が正しく分類されない

**解決策:**
- `flyer_parser.py` の `category_keywords` を拡充
- 手動でカテゴリを指定する

```python
parser.classify_category("新商品名")  # 自動分類

# または手動指定
item.category = SaleCategory.VEGETABLE
```

### 問題: 価格が正しく抽出されない

**解決策:**
- `flyer_parser.py` の `price_patterns` に新しいパターンを追加
- OCRテキストの前処理を追加

## ベストプラクティス

### 1. データ品質の維持

```python
# パース結果は必ず検証する
validated = parser.validate_parsed_products(products, min_confidence=0.7)

# 期限切れデータを定期削除
service.clear_expired_sales()
```

### 2. パフォーマンス最適化

```python
# 大量データの場合はバッチ処理
for batch in chunks(sale_items, 100):
  for item in batch:
    service.add_sale_item(item)
```

### 3. エラーハンドリング

```python
try:
  products = parser.parse_ocr_result(ocr_text, store_name)
except Exception as e:
  logger.error(f"パースエラー: {e}")
  # フォールバック処理
```

## 拡張性

### カスタムカテゴリの追加

```python
# SaleCategory に新しいカテゴリを追加
class SaleCategory(str, Enum):
  VEGETABLE = "vegetable"
  # ... 既存のカテゴリ ...
  FROZEN = "frozen"  # 冷凍食品を追加
```

### 独自の材料マッピング

```python
# SaleService の _load_ingredient_mapping をカスタマイズ
custom_mapping = {
  "特殊材料": ["パターン1", "パターン2"],
}
service._ingredient_mapping.update(custom_mapping)
```

## まとめ

特売情報連携機能により、以下が実現できます：

1. チラシから自動的に特売情報を抽出
2. レシピと特売情報を連動させて節約レシピを提案
3. 店舗間の価格比較で最安値を発見
4. 材料費の見積もりで予算管理

詳細は [API仕様書](./sale-api-specification.md) を参照してください。

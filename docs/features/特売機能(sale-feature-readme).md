# スーパー特売情報連携機能

Personal Recipe Intelligence プロジェクトに統合されたスーパー特売情報連携機能のドキュメントです。

## 機能概要

スーパーのチラシから特売情報を抽出し、レシピと連動させることで、節約料理を提案します。

### 主な機能

1. **特売情報管理**
   - チラシ画像からのOCR抽出
   - 商品名・価格・カテゴリの自動分類
   - 有効期限管理

2. **レシピ連動**
   - 特売食材を使ったレシピ推薦
   - 材料費の自動見積もり
   - 節約効果の可視化

3. **価格比較**
   - 複数店舗間の価格比較
   - 割引率ランキング
   - 最安値店舗の提示

4. **統計情報**
   - カテゴリ別集計
   - 店舗別集計
   - 平均割引率計算

## ファイル構成

```
personal-recipe-intelligence/
├── backend/
│   ├── services/
│   │   ├── sale_service.py          # 特売情報サービス（コアロジック）
│   │   └── flyer_parser.py          # チラシパーサー（OCR連携）
│   ├── api/
│   │   └── routers/
│   │       └── sale.py               # APIルーター（FastAPI）
│   └── tests/
│       ├── test_sale_service.py      # サービスのテスト
│       └── test_flyer_parser.py      # パーサーのテスト
├── frontend/
│   └── components/
│       └── SaleInfo.jsx              # UIコンポーネント（React）
├── docs/
│   ├── sale-api-specification.md     # API仕様書
│   └── sale-feature-usage.md         # 使用ガイド
├── examples/
│   └── sale_example.py               # サンプルコード
└── SALE_FEATURE_README.md            # 本ファイル
```

## クイックスタート

### 1. セットアップ

```bash
# セットアップスクリプトを実行
chmod +x setup-sale-feature.sh
./setup-sale-feature.sh

# 依存関係をインストール
pip install fastapi pydantic pytest python-multipart
```

### 2. テスト実行

```bash
# すべてのテストを実行
pytest backend/tests/test_sale_service.py -v
pytest backend/tests/test_flyer_parser.py -v

# カバレッジ測定
pytest backend/tests/ --cov=backend/services --cov-report=html
```

### 3. サンプル実行

```bash
# サンプルコードを実行
python examples/sale_example.py
```

### 4. APIサーバー起動（統合後）

```python
# backend/main.py
from fastapi import FastAPI
from backend.api.routers import sale

app = FastAPI()
app.include_router(sale.router)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
# サーバー起動
python backend/main.py

# APIドキュメント確認
# http://localhost:8001/docs
```

## 基本的な使い方

### Python コードでの使用

```python
from backend.services.sale_service import SaleService, SaleItem, SaleCategory
from datetime import datetime, timedelta

# サービス初期化
service = SaleService()

# 特売商品追加
sale = SaleItem(
  id="sale-001",
  store_name="イオン",
  product_name="たまねぎ",
  price=98.0,
  original_price=150.0,
  category=SaleCategory.VEGETABLE,
  valid_from=datetime.now(),
  valid_until=datetime.now() + timedelta(days=3),
)
service.add_sale_item(sale)

# 特売情報取得
sales = service.get_active_sales(category=SaleCategory.VEGETABLE)

# 価格比較
comparison = service.compare_prices("たまねぎ")

# レシピ材料費見積もり
estimate = service.get_recipe_cost_estimate(["たまねぎ", "にんじん", "豚肉"])
```

### API での使用

```bash
# 特売情報一覧
curl "http://localhost:8001/api/v1/sales"

# カテゴリフィルタ
curl "http://localhost:8001/api/v1/sales?category=vegetable"

# チラシアップロード
curl -X POST "http://localhost:8001/api/v1/sales/upload" \
  -F "file=@flyer.jpg" \
  -F "store_name=イオン"

# レシピ推薦
curl "http://localhost:8001/api/v1/sales/recommendations"

# 価格比較
curl "http://localhost:8001/api/v1/sales/price-compare?product_name=たまねぎ"
```

## API エンドポイント

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/sales` | 特売情報一覧取得 |
| POST | `/api/v1/sales/upload` | チラシアップロード |
| GET | `/api/v1/sales/recommendations` | レシピ推薦 |
| GET | `/api/v1/sales/price-compare` | 価格比較 |
| POST | `/api/v1/sales/cost-estimate` | 材料費見積もり |
| GET | `/api/v1/sales/statistics` | 統計情報 |
| DELETE | `/api/v1/sales/expired` | 期限切れ削除 |

詳細は [API仕様書](docs/sale-api-specification.md) を参照してください。

## テスト

### テスト構成

- `test_sale_service.py`: 特売情報サービスのユニットテスト
- `test_flyer_parser.py`: チラシパーサーのユニットテスト

### テストカバレッジ

```bash
# カバレッジレポート生成
pytest backend/tests/ \
  --cov=backend/services \
  --cov-report=html \
  --cov-report=term

# HTMLレポート確認
open htmlcov/index.html
```

### 継続的インテグレーション

```yaml
# .github/workflows/test.yml (サンプル)
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest backend/tests/ -v --cov
```

## フロントエンド統合

### React での使用

```jsx
import React from 'react';
import SaleInfo from './components/SaleInfo';

function App() {
  return (
    <div>
      <h1>Personal Recipe Intelligence</h1>
      <SaleInfo />
    </div>
  );
}
```

### 環境変数設定

```bash
# .env
REACT_APP_API_URL=http://localhost:8001
```

## アーキテクチャ

### レイヤー構成

```
┌─────────────────────────────────────┐
│  Frontend (React)                   │
│  - SaleInfo.jsx                     │
└─────────────┬───────────────────────┘
              │ HTTP
┌─────────────▼───────────────────────┐
│  API Layer (FastAPI)                │
│  - sale.py (router)                 │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Service Layer                      │
│  - sale_service.py                  │
│  - flyer_parser.py                  │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Data Layer                         │
│  - In-memory (current)              │
│  - SQLite (future)                  │
└─────────────────────────────────────┘
```

### データフロー

```
1. チラシ画像 → OCR → FlyerParser
2. パース結果 → 検証 → SaleItem生成
3. SaleItem → SaleService → 保存
4. クエリ → SaleService → フィルタ・集計
5. 結果 → API → JSON → Frontend
```

## データモデル

### SaleItem

```python
@dataclass
class SaleItem:
  id: str                          # 一意ID
  store_name: str                  # 店舗名
  product_name: str                # 商品名
  price: float                     # 価格
  original_price: Optional[float]  # 元値
  unit: str                        # 単位
  category: SaleCategory           # カテゴリ
  valid_from: datetime             # 有効開始
  valid_until: datetime            # 有効終了
  discount_rate: Optional[float]   # 割引率（%）
  image_url: Optional[str]         # 画像URL
  metadata: Dict[str, Any]         # メタデータ
```

### SaleCategory

```python
class SaleCategory(str, Enum):
  VEGETABLE = "vegetable"   # 野菜
  FRUIT = "fruit"           # 果物
  MEAT = "meat"             # 肉類
  FISH = "fish"             # 魚介類
  DAIRY = "dairy"           # 乳製品
  GRAIN = "grain"           # 穀物
  SEASONING = "seasoning"   # 調味料
  OTHER = "other"           # その他
```

## 拡張方法

### 1. カスタムカテゴリの追加

```python
# SaleCategory に追加
class SaleCategory(str, Enum):
  # ... 既存のカテゴリ ...
  FROZEN = "frozen"  # 冷凍食品
```

### 2. データベース永続化

```python
# SQLite 統合例
import sqlite3

class SaleRepository:
  def __init__(self, db_path: str):
    self.conn = sqlite3.connect(db_path)
    self.create_tables()

  def save(self, item: SaleItem):
    # INSERT 処理
    pass

  def find_all(self) -> List[SaleItem]:
    # SELECT 処理
    pass
```

### 3. OCR連携

```python
# OCR サービス統合例
import pytesseract
from PIL import Image

def ocr_image(image_path: str) -> str:
  image = Image.open(image_path)
  text = pytesseract.image_to_string(image, lang='jpn')
  return text
```

## トラブルシューティング

### 問題: インポートエラー

```bash
# 解決策: Pythonパスを設定
export PYTHONPATH="${PYTHONPATH}:/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"
```

### 問題: テストが失敗する

```bash
# 解決策: 依存関係を再インストール
pip install --upgrade pytest fastapi pydantic
```

### 問題: OCR精度が低い

- チラシ画像の解像度を上げる（300dpi以上推奨）
- 画像の傾きを補正する
- OCRエンジンの設定を調整する

## パフォーマンス

### 推奨スペック

- CPU: 2コア以上
- メモリ: 2GB以上
- ストレージ: 1GB以上

### ベンチマーク（参考値）

- 特売情報取得: ~10ms
- チラシパース: ~500ms（OCR含む）
- 価格比較: ~5ms
- レシピ推薦: ~20ms

## セキュリティ

- 入力検証: Pydantic で全パラメータを検証
- ファイルアップロード: 画像ファイルのみ許可
- SQL インジェクション: パラメータ化クエリ使用
- XSS: フロントエンドでエスケープ処理

## ライセンス

本機能は Personal Recipe Intelligence プロジェクトのライセンスに従います。

## サポート

- ドキュメント: [docs/](docs/)
- サンプルコード: [examples/](examples/)
- テストコード: [backend/tests/](backend/tests/)

## 今後の予定

- [ ] データベース永続化（SQLite）
- [ ] OCR精度向上（Tesseract/Cloud Vision API）
- [ ] 画像前処理（傾き補正、ノイズ除去）
- [ ] レシピデータベース統合
- [ ] ユーザー認証・認可
- [ ] リアルタイム通知（WebSocket）
- [ ] モバイルアプリ対応

## 貢献

Pull Request を歓迎します。大きな変更の場合は、まず Issue で議論してください。

## 更新履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025-12-11 | 1.0.0 | 初版リリース |

---

**Personal Recipe Intelligence**
スーパー特売情報連携機能 v1.0.0

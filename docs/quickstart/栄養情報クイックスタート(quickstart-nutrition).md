# 栄養計算機能 クイックスタートガイド

Personal Recipe Intelligence の栄養計算機能を5分で試せるガイドです。

---

## ステップ1: セットアップ（1分）

```bash
# プロジェクトディレクトリに移動
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# 必要なパッケージをインストール
pip install fastapi uvicorn pydantic

# テスト用パッケージ（オプション）
pip install pytest httpx
```

---

## ステップ2: サーバー起動（30秒）

```bash
# APIサーバーを起動
python backend/main_nutrition_example.py
```

または

```bash
uvicorn backend.main_nutrition_example:app --reload --host 0.0.0.0 --port 8001
```

起動すると以下のメッセージが表示されます:

```
============================================================
Personal Recipe Intelligence - 栄養計算API
============================================================

起動中...

アクセス先:
  - API: http://localhost:8001
  - Swagger UI: http://localhost:8001/docs
  - ReDoc: http://localhost:8001/redoc

停止: Ctrl+C
============================================================
```

---

## ステップ3: APIを試す（2分）

### 方法1: ブラウザで試す（推奨）

1. ブラウザで開く: `http://localhost:8001/docs`
2. **POST /api/v1/nutrition/calculate** をクリック
3. 「Try it out」ボタンをクリック
4. 以下のJSONを入力:

```json
{
  "ingredients": [
    {"name": "白米", "amount": "150g"},
    {"name": "鶏もも肉", "amount": "100g"},
    {"name": "ブロッコリー", "amount": "80g"}
  ],
  "servings": 1
}
```

5. 「Execute」ボタンをクリック
6. レスポンスで栄養価が表示されます

### 方法2: curlで試す

```bash
# 栄養計算
curl -X POST "http://localhost:8001/api/v1/nutrition/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"name": "白米", "amount": "150g"},
      {"name": "鶏もも肉", "amount": "100g"}
    ],
    "servings": 1
  }'

# 材料情報取得
curl "http://localhost:8001/api/v1/nutrition/ingredient/鶏もも肉"

# 材料検索
curl "http://localhost:8001/api/v1/nutrition/search?q=鶏"
```

### 方法3: Pythonで試す

```python
import requests

# 栄養計算
url = "http://localhost:8001/api/v1/nutrition/calculate"
data = {
    "ingredients": [
        {"name": "白米", "amount": "150g"},
        {"name": "鶏むね肉", "amount": "100g"}
    ],
    "servings": 1
}

response = requests.post(url, json=data)
result = response.json()

# 結果表示
per_serving = result['data']['per_serving']
print(f"カロリー: {per_serving['calories']} kcal")
print(f"タンパク質: {per_serving['protein']} g")
```

---

## ステップ4: サンプル実行（1分）

```bash
# 使用例スクリプトを実行
python backend/examples/nutrition_example.py
```

7つの使用例が実行され、以下の内容が確認できます:

1. シンプルな栄養計算
2. 複数人前の計算
3. 材料ごとの詳細分析
4. 材料検索
5. 様々な単位の計算
6. バランスの良い食事の分析
7. レシピの比較

---

## ステップ5: テスト実行（オプション）

```bash
# サービスのテスト
pytest backend/tests/test_nutrition_service.py -v

# APIのテスト
pytest backend/tests/test_nutrition_api.py -v

# カバレッジ測定
pytest backend/tests/ --cov=backend.services.nutrition_service --cov-report=term
```

---

## よく使うエンドポイント

### 1. 栄養計算

```bash
POST /api/v1/nutrition/calculate
```

レシピの材料から栄養価を計算

### 2. 材料情報取得

```bash
GET /api/v1/nutrition/ingredient/{name}
```

特定の材料の栄養情報を取得（100gあたり）

### 3. 材料検索

```bash
GET /api/v1/nutrition/search?q={query}
```

材料を検索

### 4. 全材料リスト

```bash
GET /api/v1/nutrition/ingredients
```

登録されている全材料名を取得

---

## レスポンス例

### 栄養計算のレスポンス

```json
{
  "status": "ok",
  "data": {
    "servings": 1,
    "per_serving": {
      "calories": 449.6,
      "protein": 31.9,
      "fat": 16.1,
      "carbohydrates": 59.8,
      "fiber": 4.8
    },
    "total": {
      "calories": 449.6,
      "protein": 31.9,
      "fat": 16.1,
      "carbohydrates": 59.8,
      "fiber": 4.8
    },
    "ingredients_breakdown": [...],
    "found_ingredients": 3,
    "total_ingredients": 3,
    "summary": {
      "calorie_level": "中カロリー",
      "pfc_balance": "P:28.4% F:32.3% C:39.3%",
      "protein_ratio": 28.4,
      "fat_ratio": 32.3,
      "carb_ratio": 39.3
    }
  },
  "error": null
}
```

---

## 利用可能な材料（一部）

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

**全材料リスト**: `GET /api/v1/nutrition/ingredients` で取得可能

---

## 対応している単位

| 単位 | 例 | 換算 |
|------|-----|------|
| g | 200g | そのまま |
| kg | 0.5kg | 500g |
| ml | 100ml | 100g相当 |
| L | 1L | 1000g相当 |
| 大さじ | 大さじ1 | 15g |
| 小さじ | 小さじ2 | 10g |
| カップ | 1カップ | 200g |
| 個 | 2個 | 200g |

---

## トラブルシューティング

### サーバーが起動しない

```bash
# モジュールが見つからない場合
export PYTHONPATH=/mnt/Linux-ExHDD/Personal-Recipe-Intelligence:$PYTHONPATH

# 依存パッケージを再インストール
pip install --upgrade fastapi uvicorn pydantic
```

### 材料が見つからない

1. 全材料リストで確認: `curl http://localhost:8001/api/v1/nutrition/ingredients`
2. 検索機能を使用: `curl "http://localhost:8001/api/v1/nutrition/search?q=材料名"`
3. 正確な材料名を使用（例: "玉ねぎ" または "たまねぎ"）

### ポート8000が使用中

```bash
# 別のポートで起動
uvicorn backend.main_nutrition_example:app --port 8001
```

---

## 次のステップ

1. **詳細ドキュメント**: `/docs/nutrition_api.md` を参照
2. **カスタマイズ**: `backend/data/nutrition_database.py` に材料を追加
3. **レシピ統合**: Recipe サービスと連携して自動計算
4. **WebUI作成**: フロントエンドから栄養計算APIを呼び出し

---

## サポート

- API仕様: `http://localhost:8001/docs`
- 詳細ドキュメント: `/docs/nutrition_api.md`
- READMEファイル: `/backend/README_NUTRITION.md`
- サンプルコード: `/backend/examples/nutrition_example.py`

---

**これで栄養計算機能が使えるようになりました！**

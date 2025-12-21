# レシピ自動生成機能 仕様書

## 概要

Personal Recipe Intelligence のレシピ自動生成機能は、指定された食材やオプションから自動的にレシピを生成するシステムです。テンプレートベースの生成方式を採用し、将来的なLLM統合の基盤を提供します。

## 主要機能

### 1. レシピ生成
- 指定食材からレシピを自動生成
- 料理カテゴリ選択（和食・洋食・中華）
- 調理時間指定
- 難易度指定
- 季節の食材活用

### 2. バリエーション生成
- 既存レシピから異なる調理方法のバリエーションを生成
- 同じ食材で複数のレシピパターンを提案

### 3. 食材組み合わせ提案
- メイン食材に相性の良い食材を提案
- 季節性を考慮した提案
- 相性スコア付き

### 4. レシピ改善
- 味の改善（調味料追加）
- ヘルシー化（調理方法変更）
- 時短化（調理時間短縮）
- 節約化（コスト削減）

### 5. 栄養バランス評価
- たんぱく質・野菜・炭水化物の有無チェック
- バランススコア算出
- 改善提案

## API エンドポイント

### POST /api/v1/ai/generate
レシピを自動生成

**リクエスト:**
```json
{
  "ingredients": ["鶏肉", "玉ねぎ"],
  "category": "japanese",
  "cooking_time": 20,
  "difficulty": "easy",
  "use_seasonal": true
}
```

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "id": "generated_20251211120000",
    "name": "鶏肉の炒め物",
    "category": "japanese",
    "cooking_time": 15,
    "difficulty": "easy",
    "ingredients": [...],
    "steps": [...],
    "servings": 2,
    "tags": ["japanese", "easy", "鶏肉"],
    "nutrition": {
      "has_protein": true,
      "has_vegetable": true,
      "has_carbohydrate": false,
      "balance_score": 66.7,
      "recommendation": "バランスが良い"
    }
  }
}
```

### POST /api/v1/ai/generate/variations
レシピのバリエーションを生成

**リクエスト:**
```json
{
  "base_recipe": {...},
  "count": 3
}
```

### GET /api/v1/ai/generate/suggestions
食材の組み合わせを提案

**パラメータ:**
- `main_ingredient`: メイン食材
- `count`: 提案数（デフォルト: 5）

**レスポンス:**
```json
{
  "status": "ok",
  "data": [
    {
      "main": "鶏肉",
      "sub": "玉ねぎ",
      "compatibility_score": 85,
      "seasonal": false,
      "recommended_categories": ["japanese", "western", "chinese"]
    }
  ]
}
```

### POST /api/v1/ai/generate/improve
既存レシピを改善

**リクエスト:**
```json
{
  "recipe": {...},
  "focus": "taste"
}
```

**focus の種類:**
- `taste`: 味を改善
- `health`: ヘルシーに改善
- `speed`: 調理時間を短縮
- `cost`: コストを削減

### GET /api/v1/ai/categories
利用可能なカテゴリ情報を取得

### GET /api/v1/ai/ingredients
利用可能な食材リストを取得

## レシピテンプレート

### 和食テンプレート
1. **炒め物（stir_fry）**
   - 調理時間: 15分
   - 難易度: 簡単

2. **煮物（simmered）**
   - 調理時間: 30分
   - 難易度: 普通

3. **味噌汁（soup）**
   - 調理時間: 10分
   - 難易度: 簡単

4. **照り焼き（grilled）**
   - 調理時間: 20分
   - 難易度: 普通

### 洋食テンプレート
1. **ソテー（saute）**
   - 調理時間: 20分
   - 難易度: 普通

2. **パスタ（pasta）**
   - 調理時間: 25分
   - 難易度: 普通

3. **サラダ（salad）**
   - 調理時間: 10分
   - 難易度: 簡単

4. **シチュー（stew）**
   - 調理時間: 40分
   - 難易度: 普通

### 中華テンプレート
1. **中華炒め（stir_fry）**
   - 調理時間: 15分
   - 難易度: 普通

2. **酢豚風（sweet_sour）**
   - 調理時間: 25分
   - 難易度: 難しい

3. **中華スープ（soup）**
   - 調理時間: 15分
   - 難易度: 簡単

## 食材カテゴリ

### 肉類（meat）
- 鶏肉、豚肉、牛肉、ひき肉

### 魚介類（seafood）
- 鮭、エビ、イカ、タラ、サバ

### 野菜（vegetable）
- 玉ねぎ、にんじん、キャベツ、ピーマン、なす、トマト、ほうれん草、ブロッコリー

### きのこ類（mushroom）
- しめじ、えのき、しいたけ、エリンギ

### 豆腐類（tofu）
- 豆腐、厚揚げ、油揚げ

## 食材の相性マトリックス

相性の良い食材の組み合わせをデータベース化しています。

- **鶏肉**: 玉ねぎ、にんじん、ピーマン、しめじ、トマト
- **豚肉**: キャベツ、玉ねぎ、にんじん、ピーマン、なす
- **牛肉**: 玉ねぎ、にんじん、ピーマン、ブロッコリー
- **鮭**: 玉ねぎ、しめじ、ほうれん草、トマト
- **エビ**: ブロッコリー、アスパラガス、トマト、ピーマン
- **豆腐**: ほうれん草、しめじ、玉ねぎ、にんじん

## 季節の食材

### 春（spring）
- アスパラガス、春キャベツ、新玉ねぎ、筍

### 夏（summer）
- トマト、なす、ピーマン、ズッキーニ、オクラ

### 秋（autumn）
- さつまいも、かぼちゃ、しめじ、まいたけ、栗

### 冬（winter）
- 白菜、大根、ほうれん草、ブロッコリー、ねぎ

## レシピ構造

生成されるレシピは以下の構造を持ちます：

```json
{
  "id": "generated_YYYYMMDDHHMMSS",
  "name": "レシピ名",
  "category": "japanese | western | chinese",
  "cooking_time": 15,
  "difficulty": "easy | medium | hard",
  "ingredients": [
    {
      "name": "食材名",
      "amount": "分量",
      "unit": "単位"
    }
  ],
  "steps": [
    "手順1",
    "手順2"
  ],
  "servings": 2,
  "tags": ["タグ1", "タグ2"],
  "generated_at": "ISO8601 timestamp",
  "method": "調理方法",
  "nutrition": {
    "has_protein": true,
    "has_vegetable": true,
    "has_carbohydrate": false,
    "balance_score": 66.7,
    "recommendation": "改善提案"
  }
}
```

## フロントエンド UI

### RecipeGenerator コンポーネント

#### 主要機能
1. **食材入力**
   - テキスト入力＋タグ表示
   - カテゴリ別食材ボタン
   - Enter キーで追加

2. **オプション設定**
   - 料理カテゴリ選択
   - 調理時間指定
   - 難易度選択
   - 季節食材活用チェックボックス

3. **食材組み合わせ提案**
   - メイン食材入力時に自動表示
   - 相性スコア表示
   - 旬バッジ表示

4. **レシピ表示**
   - レシピ名・メタ情報
   - 材料リスト
   - 手順リスト
   - 栄養バランス情報

5. **アクション**
   - 保存ボタン
   - 再生成ボタン
   - 新規作成ボタン
   - 改善ボタン（味・健康・時短・節約）

## 将来の拡張

### LLM 統合準備
現在のテンプレートベース生成は、将来的にLLM（Claude API等）統合の基盤として設計されています。

1. **テンプレート → LLM プロンプト変換**
2. **食材相性データ → LLM コンテキスト提供**
3. **栄養バランス → LLM 評価基準提供**

### 追加機能候補
- レシピのお気に入り登録
- 生成履歴の保存
- ユーザーフィードバックの収集
- レシピ評価システム
- 画像生成（DALL-E等）
- カロリー計算機能
- アレルギー対応フィルタ

## テスト

### サービステスト
- `backend/tests/test_recipe_generator_service.py`
- 50種類以上のテストケース

### APIテスト
- `backend/tests/test_recipe_generator_router.py`
- エンドポイント全機能のテスト

### テストコマンド
```bash
# サービステスト
pytest backend/tests/test_recipe_generator_service.py -v

# APIテスト
pytest backend/tests/test_recipe_generator_router.py -v

# 全テスト
pytest backend/tests/test_recipe_generator* -v
```

## セキュリティ

- 入力検証: Pydantic による厳密なバリデーション
- レート制限: 個人用途のため不要（将来的に検討）
- データ保存: JSON ファイルベース（SQLite 連携可能）

## パフォーマンス

- レシピ生成: < 50ms（テンプレートベース）
- バリエーション生成: < 100ms
- 食材提案: < 10ms
- メモリ使用: 最小限（テンプレートデータのみ）

## 使用例

### 基本的なレシピ生成
```bash
curl -X POST http://localhost:8000/api/v1/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["鶏肉", "玉ねぎ"],
    "category": "japanese",
    "cooking_time": 20,
    "difficulty": "easy"
  }'
```

### 食材提案取得
```bash
curl "http://localhost:8000/api/v1/ai/generate/suggestions?main_ingredient=鶏肉&count=5"
```

### レシピ改善
```bash
curl -X POST http://localhost:8000/api/v1/ai/generate/improve \
  -H "Content-Type: application/json" \
  -d '{
    "recipe": {...},
    "focus": "health"
  }'
```

## トラブルシューティング

### 問題: レシピが生成されない
- 食材が最低1つ指定されているか確認
- カテゴリが正しいか確認（japanese/western/chinese）

### 問題: 提案が表示されない
- メイン食材が正しく入力されているか確認
- API エンドポイントが正しいか確認

### 問題: 改善機能が動作しない
- focus パラメータが正しいか確認（taste/health/speed/cost）
- レシピデータが完全か確認

## 開発者向け情報

### ファイル構成
```
backend/
  services/
    recipe_generator_service.py  # コアロジック
  api/
    routers/
      recipe_generator.py         # APIルーター
  tests/
    test_recipe_generator_service.py  # サービステスト
    test_recipe_generator_router.py   # APIテスト

frontend/
  components/
    RecipeGenerator.jsx          # UIコンポーネント
    RecipeGenerator.css          # スタイル

data/
  generator/                     # 生成データ保存
```

### カスタマイズポイント

1. **テンプレート追加**
   - `_load_templates()` メソッドで新しいテンプレートを追加

2. **食材追加**
   - `_load_ingredient_data()` メソッドで食材を追加

3. **相性データ更新**
   - `ingredient_compatibility` 辞書を更新

4. **季節食材更新**
   - `seasonal_ingredients` 辞書を更新

## ライセンス

MIT License

## 更新履歴

- 2025-12-11: Phase 12-3 - レシピ自動生成機能実装

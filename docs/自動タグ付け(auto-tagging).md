# Auto-Tagging Module

## 概要

Auto-Tagging モジュールは、レシピの内容を自動的に分析し、適切なタグを提案する機能を提供します。

## 機能

### タグカテゴリ

以下のカテゴリでタグを自動提案します：

1. **cuisine_type（料理ジャンル）**
   - 和食、洋食、中華、イタリアン、フレンチ、韓国料理、タイ料理、インド料理、メキシコ料理

2. **meal_type（食事種別）**
   - 朝食、昼食、夕食、デザート、おやつ、お弁当

3. **cooking_method（調理方法）**
   - 炒め物、煮物、焼き物、揚げ物、蒸し物、生、和える、漬ける、茹でる、炊く

4. **main_ingredient（主な材料）**
   - 肉、魚、海鮮、野菜、きのこ、卵、豆腐、大豆製品、米、麺

5. **dietary（食事制限・健康）**
   - ベジタリアン、ヴィーガン、ヘルシー、グルテンフリー、高タンパク

6. **occasion（シーン）**
   - パーティー、おつまみ、お弁当、簡単、本格

7. **season（季節）**
   - 春、夏、秋、冬

8. **taste（味）**
   - 甘い、辛い、酸っぱい、さっぱり、こってり

9. **cooking_time（調理時間）**
   - 5分以内、10分以内、15分以内、30分以内、1時間以上

## 使用方法

### 基本的な使い方

```python
from backend.services.auto_tagger import AutoTagger

# AutoTaggerインスタンスを作成
tagger = AutoTagger()

# レシピからタグを提案
tags = tagger.suggest_tags(
    title="鶏肉の照り焼き",
    description="甘辛いタレが絶品の定番料理",
    ingredients=["鶏もも肉", "醤油", "みりん", "砂糖", "生姜"],
    instructions=["鶏肉を焼く", "タレを絡める"]
)

print(tags)
# 出力例: ['和食', '肉', '焼き物', '甘い', '簡単']
```

### カテゴリ別にタグを取得

```python
# カテゴリごとにタグを分類して取得
categorized_tags = tagger.suggest_tags_by_category(
    title="親子丼",
    ingredients=["鶏肉", "卵", "玉ねぎ", "醤油", "みりん", "だし汁"]
)

print(categorized_tags)
# 出力例:
# {
#     "cuisine_type": ["和食"],
#     "meal_type": ["昼食", "夕食"],
#     "cooking_method": ["煮物"],
#     "main_ingredient": ["肉", "卵"]
# }
```

### 最大タグ数を制限

```python
# 最大5個のタグを取得
tags = tagger.suggest_tags(
    title="野菜炒め",
    ingredients=["キャベツ", "人参", "ピーマン", "豚肉"],
    max_tags=5
)
```

### 簡易関数を使用

```python
from backend.services.auto_tagger import suggest_recipe_tags

# クイックに提案を取得
tags = suggest_recipe_tags(
    title="カレーライス",
    ingredients=["じゃがいも", "人参", "玉ねぎ", "カレールー"]
)
```

## ユーティリティメソッド

### 利用可能なタグ一覧を取得

```python
# すべてのタグを取得
all_tags = tagger.get_all_tags()
print(all_tags)
# ['ヴィーガン', 'ベジタリアン', 'ヘルシー', '中華', '和食', ...]

# カテゴリ一覧を取得
categories = tagger.get_categories()
print(categories)
# ['cuisine_type', 'cooking_method', 'dietary', ...]

# 特定カテゴリのタグを取得
cuisine_tags = tagger.get_tags_by_category("cuisine_type")
print(cuisine_tags)
# ['イタリアン', 'インド料理', 'タイ料理', '中華', '和食', '洋食', ...]
```

## カスタムルールの追加

### ランタイムでルールを追加

```python
# カスタムタグルールを追加
tagger.add_custom_rule(
    category="special_diet",
    tag_name="糖質制限",
    keywords=["糖質オフ", "低糖質", "ロカボ", "糖質制限"]
)

# 追加したルールが適用される
tags = tagger.suggest_tags(title="糖質オフのパン")
print(tags)
# ['糖質制限', ...]
```

### ルールファイルの再読み込み

```python
# tag_rules.json を外部で編集した後、再読み込み
tagger.reload_rules()
```

## 設定ファイル

タグルールは `config/tag_rules.json` に定義されています。

### ファイル構造

```json
{
  "cuisine_type": {
    "和食": ["醤油", "味噌", "だし", "みりん", ...],
    "洋食": ["バター", "チーズ", "クリーム", ...],
    "中華": ["ごま油", "豆板醤", "オイスターソース", ...]
  },
  "meal_type": {
    "朝食": ["トースト", "目玉焼き", ...],
    "デザート": ["ケーキ", "プリン", ...]
  },
  ...
}
```

### ルールのカスタマイズ

`config/tag_rules.json` を編集することで、キーワードやタグを追加・変更できます。

例：
```json
{
  "cuisine_type": {
    "和食": [
      "醤油",
      "味噌",
      "だし",
      "あなたの追加キーワード"
    ]
  }
}
```

## API統合例

### FastAPI エンドポイントでの使用

```python
from fastapi import APIRouter
from backend.services.auto_tagger import AutoTagger

router = APIRouter()
tagger = AutoTagger()

@router.post("/recipes/suggest-tags")
async def suggest_tags(recipe_data: dict):
    """レシピデータからタグを提案"""
    tags = tagger.suggest_tags(
        title=recipe_data.get("title", ""),
        description=recipe_data.get("description", ""),
        ingredients=recipe_data.get("ingredients", []),
        instructions=recipe_data.get("instructions", [])
    )

    return {
        "status": "ok",
        "data": {"suggested_tags": tags},
        "error": None
    }
```

## テスト

テストは `backend/tests/test_auto_tagger.py` に含まれています。

```bash
# テストを実行
pytest backend/tests/test_auto_tagger.py -v

# カバレッジ付きで実行
pytest backend/tests/test_auto_tagger.py --cov=backend.services.auto_tagger
```

## パフォーマンス

- タグ提案は軽量な文字列マッチングで実行されるため高速です
- 通常のレシピ（材料10個、手順5個程度）で **1ms未満** で処理完了
- ルールファイルは初回読み込み時のみパースされ、メモリにキャッシュされます

## 制限事項

- キーワードマッチングは部分一致ベースのため、誤検出の可能性があります
- 日本語の表記ゆれ（例：玉ねぎ／たまねぎ）は個別にキーワードとして登録が必要です
- 高度な意味解析や機械学習は使用していません

## 今後の拡張予定

- [ ] 表記ゆれの自動正規化
- [ ] 信頼度スコアの追加
- [ ] タグの重要度ランキング
- [ ] 複合条件マッチング（AND/OR条件）
- [ ] 学習機能（ユーザーフィードバックからルール改善）

## トラブルシューティング

### ルールファイルが見つからないエラー

```
FileNotFoundError: Tag rules file not found at ...
```

**解決方法**: `config/tag_rules.json` が存在することを確認してください。

### タグが提案されない

**原因**: キーワードがルールに登録されていない可能性があります。

**解決方法**:
1. `config/tag_rules.json` に該当するキーワードを追加
2. `tagger.reload_rules()` で再読み込み

### 予期しないタグが提案される

**原因**: 部分一致により別の意味のキーワードがマッチしている可能性があります。

**解決方法**: ルールファイルのキーワードを見直し、より具体的な表現に変更してください。

## ライセンス

MIT License

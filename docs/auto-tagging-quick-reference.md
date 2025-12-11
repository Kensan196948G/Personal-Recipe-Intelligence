# Auto-Tagging Quick Reference

## インストール不要

Auto-Tagger は標準ライブラリのみを使用しているため、追加のパッケージインストールは不要です。

## 基本的な使い方

### 最小限のコード

```python
from backend.services.auto_tagger import suggest_recipe_tags

tags = suggest_recipe_tags(
    title="鶏の照り焼き",
    ingredients=["鶏肉", "醤油", "みりん"]
)
# => ['和食', '肉', '焼き物', '甘い']
```

### フル機能版

```python
from backend.services.auto_tagger import AutoTagger

tagger = AutoTagger()
tags = tagger.suggest_tags(
    title="親子丼",
    description="鶏肉と卵の定番料理",
    ingredients=["鶏肉", "卵", "玉ねぎ", "醤油", "みりん"],
    instructions=["煮る", "とじる"],
    max_tags=10
)
```

## タグカテゴリ一覧

| カテゴリ | 例 |
|---------|-----|
| `cuisine_type` | 和食、洋食、中華、イタリアン、フレンチ |
| `meal_type` | 朝食、昼食、夕食、デザート、おやつ |
| `cooking_method` | 炒め物、煮物、焼き物、揚げ物、蒸し物 |
| `main_ingredient` | 肉、魚、野菜、卵、豆腐、麺 |
| `dietary` | ベジタリアン、ヘルシー、高タンパク |
| `occasion` | パーティー、おつまみ、簡単、本格 |
| `season` | 春、夏、秋、冬 |
| `taste` | 甘い、辛い、さっぱり、こってり |
| `cooking_time` | 5分以内、10分以内、30分以内 |

## よく使う機能

### カテゴリ別にタグを取得

```python
categorized = tagger.suggest_tags_by_category(
    title="麻婆豆腐",
    ingredients=["豆腐", "豚ひき肉", "豆板醤"]
)
# => {
#     "cuisine_type": ["中華"],
#     "main_ingredient": ["豆腐"],
#     "taste": ["辛い"]
# }
```

### 利用可能なタグを確認

```python
# すべてのカテゴリ
categories = tagger.get_categories()

# 特定カテゴリのタグ
cuisine_tags = tagger.get_tags_by_category("cuisine_type")

# すべてのタグ
all_tags = tagger.get_all_tags()
```

### カスタムルールを追加

```python
tagger.add_custom_rule(
    category="my_category",
    tag_name="糖質制限",
    keywords=["糖質オフ", "低糖質", "ロカボ"]
)
```

## 設定ファイル編集

`config/tag_rules.json` を直接編集してキーワードをカスタマイズできます：

```json
{
  "cuisine_type": {
    "和食": ["醤油", "味噌", "だし", "あなたのキーワード"]
  }
}
```

編集後は再読み込み：

```python
tagger.reload_rules()
```

## API エンドポイント例

```python
from fastapi import APIRouter
from backend.services.auto_tagger import AutoTagger

router = APIRouter()
tagger = AutoTagger()

@router.post("/recipes/suggest-tags")
async def suggest_tags(recipe_data: dict):
    tags = tagger.suggest_tags(
        title=recipe_data.get("title", ""),
        ingredients=recipe_data.get("ingredients", [])
    )
    return {"status": "ok", "data": {"tags": tags}}
```

## テスト実行

```bash
# すべてのテストを実行
pytest backend/tests/test_auto_tagger.py -v

# カバレッジ付き
pytest backend/tests/test_auto_tagger.py --cov=backend.services.auto_tagger

# 特定のテストクラスのみ
pytest backend/tests/test_auto_tagger.py::TestSuggestTags -v
```

## デモスクリプト実行

```bash
# デモを実行
python examples/auto_tagger_demo.py

# API統合例を実行
python examples/api_integration_example.py
```

## トラブルシューティング

### タグが提案されない

1. キーワードが `config/tag_rules.json` に存在するか確認
2. 日本語の表記ゆれ（例：玉ねぎ／たまねぎ）を確認
3. デバッグ用に全テキストを出力：

```python
all_text = f"{title} {description} {' '.join(ingredients)}"
print(f"解析対象テキスト: {all_text}")
```

### ルールファイルが見つからない

プロジェクトルートからの相対パスを確認：

```python
from pathlib import Path
rules_path = Path("config/tag_rules.json")
print(f"ルールファイルパス: {rules_path.absolute()}")
print(f"存在: {rules_path.exists()}")
```

### 予期しないタグが提案される

部分一致によるマッチングのため、より具体的なキーワードに変更：

```json
// 悪い例
"和食": ["酢"]  // 「酢豚」が和食と判定される

// 良い例
"和食": ["酢の物", "甘酢"]
```

## パフォーマンス

- 平均処理時間: **< 1ms** (通常のレシピ)
- メモリ使用量: **< 1MB** (ルールファイル読み込み後)
- 同時実行: 可能（スレッドセーフ）

## ファイル構成

```
Personal-Recipe-Intelligence/
├── backend/
│   ├── services/
│   │   └── auto_tagger.py          # メインモジュール
│   └── tests/
│       └── test_auto_tagger.py     # テスト
├── config/
│   └── tag_rules.json              # タグルール定義
├── docs/
│   ├── auto-tagging.md             # 詳細ドキュメント
│   └── auto-tagging-quick-reference.md  # このファイル
└── examples/
    ├── auto_tagger_demo.py         # デモスクリプト
    └── api_integration_example.py  # API統合例
```

## 次のステップ

1. `examples/auto_tagger_demo.py` を実行してデモを確認
2. `config/tag_rules.json` をプロジェクトに合わせてカスタマイズ
3. API に統合して実際のレシピで試す
4. ユーザーフィードバックを元にルールを改善

## 関連ドキュメント

- [詳細ドキュメント](./auto-tagging.md)
- [API統合例](../examples/api_integration_example.py)
- [テストコード](../backend/tests/test_auto_tagger.py)

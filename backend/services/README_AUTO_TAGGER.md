# Auto-Tagger Service

レシピの内容を自動的に分析し、適切なタグを提案するサービスモジュール。

## ファイル

- `auto_tagger.py` - メインモジュール
- `auto_tagger_cli.py` - コマンドラインツール

## クイックスタート

### Python コードから使用

```python
from backend.services.auto_tagger import AutoTagger

# インスタンス作成
tagger = AutoTagger()

# タグを提案
tags = tagger.suggest_tags(
    title="親子丼",
    ingredients=["鶏肉", "卵", "玉ねぎ", "醤油"]
)

print(tags)
# => ['和食', '肉', '卵', '煮物', '昼食', '夕食']
```

### コマンドラインから使用

```bash
# 基本的な使用
python backend/services/auto_tagger_cli.py --title "親子丼"

# 材料を指定
python backend/services/auto_tagger_cli.py \
  --title "カレー" \
  --ingredients "じゃがいも,人参,玉ねぎ"

# カテゴリ別に表示
python backend/services/auto_tagger_cli.py \
  --title "鶏の照り焼き" \
  --categorized

# 対話モード
python backend/services/auto_tagger_cli.py --interactive

# バッチ処理
python backend/services/auto_tagger_cli.py --batch examples/sample_recipes.json
```

## 主要機能

### タグ提案

```python
tags = tagger.suggest_tags(
    title="麻婆豆腐",
    description="ピリ辛で美味しい",
    ingredients=["豆腐", "豚ひき肉", "豆板醤"],
    instructions=["炒める", "煮込む"],
    max_tags=10
)
```

### カテゴリ別タグ提案

```python
categorized = tagger.suggest_tags_by_category(
    title="カルボナーラ",
    ingredients=["パスタ", "ベーコン", "卵", "チーズ"]
)

# 出力例:
# {
#     "cuisine_type": ["洋食", "イタリアン"],
#     "main_ingredient": ["麺", "卵"],
#     "cooking_method": ["茹でる"],
#     "taste": ["こってり"]
# }
```

### ユーティリティ

```python
# すべてのタグ取得
all_tags = tagger.get_all_tags()

# カテゴリ一覧取得
categories = tagger.get_categories()

# 特定カテゴリのタグ取得
cuisine_tags = tagger.get_tags_by_category("cuisine_type")
```

## タグカテゴリ

| カテゴリ | 説明 | 例 |
|---------|------|-----|
| cuisine_type | 料理ジャンル | 和食、洋食、中華 |
| meal_type | 食事種別 | 朝食、昼食、夕食 |
| cooking_method | 調理方法 | 炒め物、煮物、焼き物 |
| main_ingredient | 主な材料 | 肉、魚、野菜 |
| dietary | 食事制限・健康 | ヘルシー、ベジタリアン |
| occasion | シーン | パーティー、おつまみ |
| season | 季節 | 春、夏、秋、冬 |
| taste | 味 | 甘い、辛い、さっぱり |
| cooking_time | 調理時間 | 5分以内、10分以内 |

## 設定

タグルールは `config/tag_rules.json` で管理されています。

### ルールのカスタマイズ

```json
{
  "cuisine_type": {
    "和食": [
      "醤油",
      "味噌",
      "だし",
      "あなたのキーワード"
    ]
  }
}
```

### カスタムルールの追加（ランタイム）

```python
tagger.add_custom_rule(
    category="custom",
    tag_name="糖質制限",
    keywords=["糖質オフ", "低糖質", "ロカボ"]
)
```

### ルールの再読み込み

```python
tagger.reload_rules()
```

## CLI ツール詳細

### 基本的なコマンド

```bash
# ヘルプを表示
python backend/services/auto_tagger_cli.py --help

# タグ一覧を表示
python backend/services/auto_tagger_cli.py --list-tags

# カテゴリ一覧を表示
python backend/services/auto_tagger_cli.py --list-categories

# 特定カテゴリのタグを表示
python backend/services/auto_tagger_cli.py --list-tags --category cuisine_type
```

### タグ提案

```bash
# 基本
python backend/services/auto_tagger_cli.py --title "親子丼"

# 詳細情報付き
python backend/services/auto_tagger_cli.py \
  --title "カレーライス" \
  --description "スパイシーで美味しい" \
  --ingredients "じゃがいも,人参,玉ねぎ,カレールー"

# タグ数を制限
python backend/services/auto_tagger_cli.py \
  --title "野菜炒め" \
  --max-tags 5

# JSON出力
python backend/services/auto_tagger_cli.py \
  --title "パスタ" \
  --json
```

### 対話モード

```bash
python backend/services/auto_tagger_cli.py --interactive
```

対話モードでは、複数のレシピを順番に入力してタグ提案を受けられます。

### バッチ処理

```bash
# JSONファイルから一括処理
python backend/services/auto_tagger_cli.py --batch examples/sample_recipes.json
```

処理結果は `*_tagged.json` として保存されます。

## テスト

```bash
# すべてのテストを実行
pytest backend/tests/test_auto_tagger.py -v

# カバレッジ付き
pytest backend/tests/test_auto_tagger.py \
  --cov=backend.services.auto_tagger \
  --cov-report=html

# 特定のテストのみ
pytest backend/tests/test_auto_tagger.py::TestSuggestTags -v
```

## デモ

```bash
# デモスクリプトを実行
python examples/auto_tagger_demo.py
```

## API 統合

FastAPI での使用例：

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

詳細は `examples/api_integration_example.py` を参照してください。

## パフォーマンス

- 平均処理時間: **< 1ms**
- メモリ使用量: **< 1MB**
- 同時実行: 可能（スレッドセーフ）

## トラブルシューティング

### タグが提案されない

1. `config/tag_rules.json` にキーワードが存在するか確認
2. 日本語の表記ゆれ（玉ねぎ／たまねぎ）を確認
3. デバッグモードで入力を確認

### ルールファイルが見つからない

```python
from pathlib import Path
rules_path = Path("config/tag_rules.json")
print(f"存在: {rules_path.exists()}")
print(f"絶対パス: {rules_path.absolute()}")
```

## ドキュメント

- [詳細ドキュメント](../../docs/auto-tagging.md)
- [クイックリファレンス](../../docs/auto-tagging-quick-reference.md)
- [実装サマリー](../../IMPLEMENTATION_SUMMARY.md)

## ライセンス

MIT License

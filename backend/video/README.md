# Video Module - YouTube Recipe Extractor

YouTube動画からレシピ情報を抽出するモジュール

## 機能

### 1. YouTube動画メタデータ取得
- 動画タイトル、説明文、チャンネル情報
- サムネイル、動画長、タグ

### 2. 字幕（トランスクリプト）取得
- 自動生成字幕または手動字幕
- 多言語対応（日本語、英語など）
- タイムスタンプ付きテキスト

### 3. レシピ情報抽出
- **材料リスト**: 数量・単位付き
- **手順**: タイムスタンプ付き
- **分量**: 人数分
- **調理時間**: 分単位

### 4. 複数ソースからの抽出
- 字幕テキストから抽出
- 動画説明文から抽出

## ディレクトリ構成

```
backend/video/
├── __init__.py
├── models.py                 # データモデル（Pydantic）
├── youtube_extractor.py      # YouTube動画からレシピ抽出
├── transcript_parser.py      # 字幕解析・レシピ構造化
├── tests/
│   ├── __init__.py
│   ├── test_youtube_extractor.py
│   └── test_transcript_parser.py
└── README.md
```

## 使用方法

### 基本的な使い方

```python
from backend.video.youtube_extractor import YouTubeExtractor

# インスタンス作成
extractor = YouTubeExtractor()

# YouTube URLからレシピ抽出
url = "https://www.youtube.com/watch?v=VIDEO_ID"
recipe = extractor.extract_recipe(url, language="ja")

if recipe:
    print(f"レシピ名: {recipe.recipe_name}")
    print(f"材料数: {len(recipe.ingredients)}")
    print(f"手順数: {len(recipe.steps)}")

    # 材料リスト
    for ingredient in recipe.ingredients:
        print(f"  - {ingredient}")

    # 手順（タイムスタンプ付き）
    for step in recipe.steps:
        print(f"  [{step.timestamp}] {step.step_number}. {step.description}")
```

### API経由での使用

```bash
# レシピ抽出API
curl -X POST http://localhost:8000/api/v1/video/extract \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "language": "ja",
    "extract_from_description": true
  }'
```

### レスポンス例

```json
{
  "status": "ok",
  "data": {
    "video_id": "VIDEO_ID",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "title": "簡単チキンカレーの作り方",
    "channel": "料理チャンネル",
    "recipe_name": "簡単チキンカレー",
    "ingredients": [
      "鶏肉 300g",
      "玉ねぎ 1個",
      "カレールー 1箱"
    ],
    "steps": [
      {
        "step_number": 1,
        "description": "まず鶏肉を一口大に切ります",
        "timestamp": "01:30",
        "timestamp_seconds": 90
      },
      {
        "step_number": 2,
        "description": "次に玉ねぎを炒めます",
        "timestamp": "02:15",
        "timestamp_seconds": 135
      }
    ],
    "servings": "4人分",
    "cooking_time": "30分",
    "has_transcript": true,
    "transcript_language": "ja"
  },
  "error": null
}
```

## 依存パッケージ

```txt
youtube-transcript-api==0.6.1  # 字幕取得
yt-dlp==2023.11.16             # 動画メタデータ取得
pydantic==2.5.0                # データバリデーション
```

## テスト

```bash
# テスト実行
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pytest backend/video/tests/ -v

# カバレッジ付きテスト
pytest backend/video/tests/ --cov=backend.video --cov-report=html
```

## 制限事項

1. **字幕の有無**: 字幕が無効な動画は抽出精度が低下
2. **言語**: 日本語・英語以外の言語は未対応
3. **レート制限**: YouTube APIの制限により、大量リクエストは不可
4. **精度**: 自動生成字幕は誤認識の可能性あり

## パフォーマンス

- 動画メタデータ取得: ~2秒
- 字幕取得: ~1秒
- レシピ解析: ~0.5秒
- **合計処理時間**: 約3〜4秒/動画

## エラーハンドリング

```python
from backend.video.youtube_extractor import YouTubeExtractor

extractor = YouTubeExtractor()

try:
    recipe = extractor.extract_recipe(url)
    if recipe is None:
        print("レシピ抽出に失敗しました")
except Exception as e:
    print(f"エラー: {e}")
```

## ログ

ログは `logs/` ディレクトリに出力されます。

```python
import logging

# ログレベル設定
logging.basicConfig(level=logging.INFO)

# 詳細ログを有効化
logging.getLogger("backend.video").setLevel(logging.DEBUG)
```

## セキュリティ

- YouTube APIキーは不要（公開データのみ使用）
- 動画URLのバリデーション実施
- 機密データのログ出力なし

## 今後の拡張

- [ ] 他の動画プラットフォーム対応（ニコニコ動画、bilibili）
- [ ] AI/LLMによるレシピ精度向上
- [ ] 動画フレーム解析（OCR）
- [ ] レシピデータベースへの自動保存
- [ ] バッチ処理対応

## ライセンス

MIT License

## 作成者

Personal Recipe Intelligence Development Team

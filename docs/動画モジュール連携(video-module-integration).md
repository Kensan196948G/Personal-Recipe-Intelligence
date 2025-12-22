# Video Module 統合ガイド

YouTube動画レシピ抽出モジュールの統合手順

## 目次

1. [セットアップ](#セットアップ)
2. [APIサーバー起動](#apiサーバー起動)
3. [使用例](#使用例)
4. [テスト](#テスト)
5. [トラブルシューティング](#トラブルシューティング)

---

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# Python仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate

# Video moduleの依存パッケージをインストール
pip install -r backend/video/requirements-video.txt

# または全体の依存パッケージをインストール
pip install -r backend/requirements.txt
```

### 2. 環境変数設定（オプション）

```bash
# .envファイルを作成
cp .env.example .env

# 必要に応じて設定を編集
# 現時点ではYouTube APIキーは不要（公開データのみ使用）
```

---

## APIサーバー起動

### 方法1: Uvicornで直接起動

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# 開発モード（リロード有効）
uvicorn backend.main_video_example:app --reload --host 0.0.0.0 --port 8001

# 本番モード
uvicorn backend.main_video_example:app --host 0.0.0.0 --port 8001 --workers 4
```

### 方法2: Pythonスクリプトとして起動

```bash
python backend/main_video_example.py
```

### 起動確認

ブラウザまたはcurlで確認:

```bash
# ヘルスチェック
curl http://localhost:8001/health

# APIドキュメント
# ブラウザで http://localhost:8001/docs を開く
```

---

## 使用例

### 1. コマンドラインからの使用

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# 使用例スクリプトを実行
python backend/video/example_usage.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. API経由での使用

#### リクエスト

```bash
curl -X POST http://localhost:8001/api/v1/video/extract \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "language": "ja",
    "extract_from_description": true
  }'
```

#### レスポンス例

```json
{
  "status": "ok",
  "data": {
    "video_id": "VIDEO_ID",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "title": "簡単チキンカレーの作り方",
    "description": "材料:\n鶏肉 300g\n玉ねぎ 1個\n...",
    "channel": "料理チャンネル",
    "duration": 600,
    "thumbnail_url": "https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg",
    "recipe_name": "簡単チキンカレー",
    "ingredients": [
      "鶏肉 300g",
      "玉ねぎ 1個",
      "にんじん 1本",
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
        "description": "次に玉ねぎとにんじんを炒めます",
        "timestamp": "02:15",
        "timestamp_seconds": 135
      }
    ],
    "servings": "4人分",
    "cooking_time": "30分",
    "tags": ["カレー", "料理", "簡単レシピ"],
    "has_transcript": true,
    "transcript_language": "ja",
    "extracted_at": "2025-12-11T10:30:00Z"
  },
  "error": null
}
```

### 3. Pythonコードからの使用

```python
from backend.video.youtube_extractor import YouTubeExtractor

# インスタンス作成
extractor = YouTubeExtractor()

# レシピ抽出
recipe = extractor.extract_recipe(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    language="ja",
    extract_from_description=True
)

if recipe:
    print(f"レシピ名: {recipe.recipe_name}")
    print(f"材料: {len(recipe.ingredients)}件")
    print(f"手順: {len(recipe.steps)}件")

    # 詳細表示
    for ingredient in recipe.ingredients:
        print(f"  - {ingredient}")

    for step in recipe.steps:
        print(f"  {step.step_number}. [{step.timestamp}] {step.description}")
```

---

## テスト

### 全テスト実行

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# Video moduleのテストのみ実行
pytest backend/video/tests/ -v

# カバレッジ付きテスト
pytest backend/video/tests/ --cov=backend.video --cov-report=html

# カバレッジレポートを表示
# ブラウザで htmlcov/index.html を開く
```

### 個別テスト実行

```bash
# YouTubeExtractorのテストのみ
pytest backend/video/tests/test_youtube_extractor.py -v

# TranscriptParserのテストのみ
pytest backend/video/tests/test_transcript_parser.py -v

# 特定のテストメソッドのみ
pytest backend/video/tests/test_youtube_extractor.py::TestYouTubeExtractor::test_extract_video_id_standard_url -v
```

---

## トラブルシューティング

### 1. 字幕が取得できない

**症状**: `No transcript available for video VIDEO_ID`

**原因**:
- 動画に字幕が有効化されていない
- 動画が非公開または削除されている
- 対象言語の字幕が存在しない

**解決策**:
- 字幕が有効な動画を使用する
- `language` パラメータを変更して試す（例: "en"）
- 動画説明文からの抽出を有効化する

```python
recipe = extractor.extract_recipe(
    url=url,
    language="en",  # 英語字幕を試す
    extract_from_description=True  # 説明文からも抽出
)
```

### 2. 動画メタデータが取得できない

**症状**: `Failed to get video metadata`

**原因**:
- 無効なYouTube URL
- ネットワーク接続エラー
- YouTube側の制限

**解決策**:
- URLが正しいか確認
- インターネット接続を確認
- 時間をおいて再試行

### 3. レシピ情報が抽出されない

**症状**: `ingredients` や `steps` が空のリスト

**原因**:
- 動画内容がレシピではない
- 字幕の内容が不十分
- パースパターンがマッチしない

**解決策**:
- レシピ動画であることを確認
- 動画説明文に材料・手順が記載されているか確認
- ログを確認してパースエラーを調査

```bash
# デバッグログを有効化
export LOG_LEVEL=DEBUG
python backend/video/example_usage.py "URL"
```

### 4. モジュールインポートエラー

**症状**: `ModuleNotFoundError: No module named 'backend.video'`

**原因**:
- Pythonパスが正しく設定されていない
- 依存パッケージがインストールされていない

**解決策**:

```bash
# プロジェクトルートから実行
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence

# PYTHONPATHを設定
export PYTHONPATH=/mnt/Linux-ExHDD/Personal-Recipe-Intelligence:$PYTHONPATH

# または、依存パッケージを再インストール
pip install -r backend/video/requirements-video.txt
```

### 5. API起動エラー

**症状**: `ModuleNotFoundError: No module named 'backend.api.routers'`

**原因**:
- `__init__.py` が不足している
- モジュール構造が正しくない

**解決策**:

```bash
# 必要なディレクトリに __init__.py を作成
touch backend/api/__init__.py
touch backend/api/routers/__init__.py
```

---

## パフォーマンス最適化

### 1. キャッシュの活用

将来的な拡張として、動画メタデータや字幕をキャッシュすることで高速化可能:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_video_metadata(video_id: str):
    return extractor.get_video_metadata(video_id)
```

### 2. 非同期処理

複数の動画を並列処理する場合:

```python
import asyncio

async def extract_multiple_recipes(urls: list[str]):
    tasks = [extract_recipe_async(url) for url in urls]
    return await asyncio.gather(*tasks)
```

---

## セキュリティ

### 入力バリデーション

- すべてのURLは `pydantic` でバリデーション
- 不正なURLは自動的に拒否

### ログマスキング

- 機密情報（APIキー等）はログに出力しない
- CLAUDE.md のセキュリティ要件に準拠

### レート制限

現時点では個人用途のため未実装。将来的に必要に応じて追加。

---

## 今後の拡張

- [ ] データベース統合（SQLite）
- [ ] レシピ自動保存機能
- [ ] バッチ処理対応
- [ ] AI/LLMによる精度向上
- [ ] 他の動画プラットフォーム対応

---

## 参考リンク

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Pydantic](https://docs.pydantic.dev/)

---

## サポート

問題が発生した場合は、プロジェクトのissueトラッカーまでご報告ください。

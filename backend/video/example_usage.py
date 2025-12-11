#!/usr/bin/env python3
"""
YouTube動画レシピ抽出モジュールの使用例
"""

import sys
import logging
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.video.youtube_extractor import YouTubeExtractor  # noqa: E402

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """メイン処理"""

    # YouTube URLの例（実際のURLに置き換えてください）
    # 注意: 実際に存在する料理動画のURLを使用してください

    # YouTubeExtractorインスタンス作成
    extractor = YouTubeExtractor()

    print("=" * 60)
    print("YouTube動画レシピ抽出デモ")
    print("=" * 60)
    print()

    # コマンドライン引数からURLを取得
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        print(f"入力URL: {target_url}")
        print()

        # レシピ抽出
        print("レシピ抽出中...")
        recipe = extractor.extract_recipe(
            url=target_url, language="ja", extract_from_description=True
        )

        if recipe:
            print_recipe(recipe)
            save_recipe_json(recipe, "extracted_recipe.json")
        else:
            print("❌ レシピ抽出に失敗しました")
            print("  - 動画が存在するか確認してください")
            print("  - 字幕が有効になっているか確認してください")

    else:
        print("使用方法:")
        print(f"  python {Path(__file__).name} <YouTube_URL>")
        print()
        print("例:")
        print(
            f"  python {Path(__file__).name} https://www.youtube.com/watch?v=VIDEO_ID"
        )
        print()


def print_recipe(recipe):
    """レシピ情報を整形して表示"""

    print()
    print("=" * 60)
    print("✅ レシピ抽出成功")
    print("=" * 60)
    print()

    # 基本情報
    print(f"📺 動画タイトル: {recipe.title}")
    print(f"🆔 動画ID: {recipe.video_id}")
    if recipe.channel:
        print(f"📢 チャンネル: {recipe.channel}")
    if recipe.duration:
        minutes = recipe.duration // 60
        seconds = recipe.duration % 60
        print(f"⏱️  動画時間: {minutes}分{seconds}秒")
    print()

    # レシピ情報
    if recipe.recipe_name:
        print(f"🍳 レシピ名: {recipe.recipe_name}")
    if recipe.servings:
        print(f"👥 分量: {recipe.servings}")
    if recipe.cooking_time:
        print(f"⏰ 調理時間: {recipe.cooking_time}")
    print()

    # 材料
    if recipe.ingredients:
        print(f"📋 材料（{len(recipe.ingredients)}件）:")
        for i, ingredient in enumerate(recipe.ingredients, 1):
            print(f"  {i}. {ingredient}")
        print()

    # 手順
    if recipe.steps:
        print(f"📝 手順（{len(recipe.steps)}件）:")
        for step in recipe.steps:
            timestamp = f"[{step.timestamp}]" if step.timestamp else ""
            print(f"  {step.step_number}. {timestamp} {step.description}")
        print()

    # メタデータ
    print("ℹ️  メタデータ:")
    print(f"  - 字幕: {'あり' if recipe.has_transcript else 'なし'}")
    if recipe.transcript_language:
        print(f"  - 字幕言語: {recipe.transcript_language}")
    if recipe.tags:
        print(f"  - タグ: {', '.join(recipe.tags[:5])}")
    print()


def save_recipe_json(recipe, filename: str):
    """レシピをJSONファイルに保存"""

    output_path = Path(filename)

    try:
        # PydanticモデルをJSON化
        recipe_json = recipe.model_dump(mode="json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(recipe_json, f, ensure_ascii=False, indent=2)

        print(f"💾 レシピをJSONファイルに保存しました: {output_path.absolute()}")
        print()

    except Exception as e:
        logger.error(f"Failed to save recipe JSON: {e}")


if __name__ == "__main__":
    main()

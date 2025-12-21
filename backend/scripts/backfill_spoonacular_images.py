"""
Spoonacular APIから直接画像を取得するバックフィルスクリプト
source_urlからSpoonacularレシピIDを特定し、画像を取得
"""

import asyncio
import logging
import os
import re
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlmodel import Session, select
from backend.core.database import engine
from backend.core.config import settings
from backend.models.recipe import Recipe
from backend.services.image_download_service import ImageDownloadService
from backend.services.spoonacular_client import SpoonacularClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_english_keywords(title: str) -> str:
    """タイトルから英語キーワードを抽出"""
    # 英単語を抽出
    english_words = re.findall(r'[A-Za-z]+', title)
    if english_words:
        return ' '.join(english_words[:3])  # 最初の3単語

    # 一般的な料理名の日英マッピング
    mappings = {
        'チキン': 'chicken',
        'ビーフ': 'beef',
        'ポーク': 'pork',
        'サーモン': 'salmon',
        'パスタ': 'pasta',
        'スープ': 'soup',
        'サラダ': 'salad',
        'ケーキ': 'cake',
        'ステーキ': 'steak',
        'カレー': 'curry',
        'シチュー': 'stew',
        'グラタン': 'gratin',
        'オムレツ': 'omelette',
        'フライ': 'fried',
        'ロースト': 'roast',
        'グリル': 'grill',
        'ブロッコリー': 'broccoli',
        'トマト': 'tomato',
        'ナス': 'eggplant',
        'ケール': 'kale',
    }

    keywords = []
    for jp, en in mappings.items():
        if jp in title:
            keywords.append(en)

    return ' '.join(keywords[:3]) if keywords else ''


# 画像ステータス定数
IMAGE_STATUS_OK = "ok"
IMAGE_STATUS_NO_SOURCE = "画像ソースなし"
IMAGE_STATUS_API_LIMIT = "API制限到達。後日再取得"


async def fetch_image_from_spoonacular(
    spoonacular: SpoonacularClient,
    recipe: Recipe,
    image_service: ImageDownloadService,
    dry_run: bool = False
) -> tuple[bool, str]:
    """Spoonacular APIからレシピ画像を取得

    Returns:
        tuple[bool, str]: (成功フラグ, ステータスメッセージ)
    """

    # 検索キーワードを生成
    keywords = extract_english_keywords(recipe.title)
    if not keywords:
        # タイトルの最初の部分を使用
        keywords = recipe.title[:15]

    logger.info(f"  検索キーワード: {keywords}")

    try:
        # APIレート制限対策
        time.sleep(1.5)

        # Spoonacular検索
        results = spoonacular.search_recipes(query=keywords, number=3)

        if not results:
            logger.warning(f"  -> 検索結果なし")
            return False, IMAGE_STATUS_NO_SOURCE

        # 画像URLを取得
        image_url = None
        for result in results:
            img = result.get('image')
            if img and 'spoonacular.com' in img:
                image_url = img
                break

        if not image_url:
            # 詳細情報から取得
            recipe_id = results[0].get('id')
            if recipe_id:
                time.sleep(1)
                detail = spoonacular.get_recipe_information(recipe_id)
                image_url = detail.get('image')

        if not image_url:
            logger.warning(f"  -> 画像URL取得不可")
            return False, IMAGE_STATUS_NO_SOURCE

        logger.info(f"  -> 画像URL: {image_url}")

        if dry_run:
            return True, IMAGE_STATUS_OK

        # 画像をダウンロード
        image_path = await image_service.download_and_save(
            url=image_url,
            recipe_id=recipe.id
        )

        if image_path:
            recipe.image_url = image_url
            recipe.image_path = image_path
            recipe.image_status = IMAGE_STATUS_OK
            logger.info(f"  -> 保存: {image_path}")
            return True, IMAGE_STATUS_OK
        else:
            logger.warning(f"  -> ダウンロード失敗")
            return False, IMAGE_STATUS_NO_SOURCE

    except Exception as e:
        error_msg = str(e)
        logger.error(f"  -> エラー: {error_msg}")

        # API制限エラーの判定
        if "402" in error_msg or "Payment Required" in error_msg or "daily points limit" in error_msg.lower():
            return False, IMAGE_STATUS_API_LIMIT

        return False, IMAGE_STATUS_NO_SOURCE


async def backfill_from_spoonacular(dry_run: bool = False, limit: int = None):
    """Spoonacular APIから画像を取得してバックフィル"""

    api_key = settings.spoonacular_api_key or os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        logger.error("SPOONACULAR_API_KEY が設定されていません")
        return 0, 0

    spoonacular = SpoonacularClient(api_key)
    image_service = ImageDownloadService()

    with Session(engine) as session:
        # 画像がないレシピを取得（API制限で失敗したものも再試行対象）
        stmt = select(Recipe).where(
            Recipe.image_path == None,
            Recipe.source_type == "spoonacular",
            # 「画像ソースなし」は永続的失敗なので除外
            (Recipe.image_status == None) | (Recipe.image_status == IMAGE_STATUS_API_LIMIT)
        ).order_by(Recipe.id)

        if limit:
            stmt = stmt.limit(limit)

        recipes = session.exec(stmt).all()

        logger.info(f"処理対象: {len(recipes)}件")

        if dry_run:
            logger.info("=== DRY RUN モード ===")

        success_count = 0
        fail_count = 0

        for recipe in recipes:
            logger.info(f"ID {recipe.id}: {recipe.title[:40]}...")

            success, status = await fetch_image_from_spoonacular(
                spoonacular, recipe, image_service, dry_run
            )

            if success:
                if not dry_run:
                    session.add(recipe)
                success_count += 1
            else:
                # ステータスを設定
                if not dry_run:
                    recipe.image_status = status
                    session.add(recipe)
                fail_count += 1
                logger.info(f"  -> ステータス: {status}")

        if not dry_run:
            session.commit()
            logger.info("コミット完了")

        logger.info(f"=== 完了 ===")
        logger.info(f"成功: {success_count}件")
        logger.info(f"失敗: {fail_count}件")

        return success_count, fail_count


async def main():
    import argparse
    parser = argparse.ArgumentParser(description='Spoonacular APIから画像を取得')
    parser.add_argument('--dry-run', action='store_true', help='実際には変更せず確認のみ')
    parser.add_argument('--limit', type=int, default=None, help='処理数の上限')
    args = parser.parse_args()

    await backfill_from_spoonacular(dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    asyncio.run(main())

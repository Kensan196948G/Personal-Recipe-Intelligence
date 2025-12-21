"""
既存レシピへの画像バックフィルスクリプト
source_urlからOGイメージをスクレイピングして画像を取得
"""

import asyncio
import logging
import os
import re
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlmodel import Session, select
from backend.core.database import engine
from backend.models.recipe import Recipe
from backend.services.image_download_service import ImageDownloadService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def is_valid_recipe_image(url: str) -> bool:
    """レシピ画像として有効かチェック"""
    if not url:
        return False
    skip_patterns = [
        "logo", "icon", "avatar", "placeholder", "button", "static/images",
        "add_recipe", "no-image", "default", "social", "share", "twitter",
        "facebook", "pinterest", "instagram", "gravatar", "profile",
        "widget", "banner", "ad-", "advertisement", "pixel", "tracking",
        "blank", "spacer"
    ]
    url_lower = url.lower()
    return not any(p in url_lower for p in skip_patterns)


def make_absolute_url(src: str, base_url: str) -> str:
    """相対パスを絶対パスに変換"""
    if not src:
        return ""
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}{src}"
    if not src.startswith("http"):
        from urllib.parse import urljoin
        return urljoin(base_url, src)
    return src


async def extract_og_image(url: str) -> str | None:
    """URLからOGイメージを抽出"""
    if not url:
        return None

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # 1. OGイメージを優先
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                img_url = make_absolute_url(og_image["content"], url)
                if is_valid_recipe_image(img_url):
                    return img_url

            # 2. Twitter カード画像
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_image and twitter_image.get("content"):
                img_url = make_absolute_url(twitter_image["content"], url)
                if is_valid_recipe_image(img_url):
                    return img_url

            # 3. Schema.org Recipe image
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    import json
                    data = json.loads(script.string or "")
                    if isinstance(data, dict):
                        if data.get("@type") == "Recipe" and data.get("image"):
                            img = data["image"]
                            if isinstance(img, list):
                                img = img[0]
                            if isinstance(img, dict):
                                img = img.get("url", "")
                            if img and is_valid_recipe_image(img):
                                return make_absolute_url(img, url)
                except:
                    continue

            # 4. レシピページでよくあるCSSセレクター
            recipe_selectors = [
                "img.recipe-image",
                "img.recipe-photo",
                ".recipe-image img",
                ".recipe-photo img",
                ".recipe__image img",
                "[itemtype*='Recipe'] img",
                ".hero-image img",
                ".featured-image img",
                "article img[src*='recipe']",
                "article img[src*='food']",
                ".entry-content img:first-of-type",
                "main img:first-of-type",
            ]
            for selector in recipe_selectors:
                img = soup.select_one(selector)
                if img:
                    src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
                    if src:
                        img_url = make_absolute_url(src, url)
                        if is_valid_recipe_image(img_url):
                            return img_url

            # 5. 大きめの画像を探す（width/height属性がある場合）
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if not src:
                    continue
                # サイズ属性をチェック
                width = img.get("width", "")
                height = img.get("height", "")
                try:
                    w = int(re.sub(r'\D', '', str(width)) or 0)
                    h = int(re.sub(r'\D', '', str(height)) or 0)
                    if w >= 200 and h >= 150:
                        img_url = make_absolute_url(src, url)
                        if is_valid_recipe_image(img_url):
                            return img_url
                except:
                    pass

            # 6. 最後の手段：最初の適切な画像
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if not src:
                    continue
                if re.search(r"\.(jpg|jpeg|png|webp)", src, re.I):
                    img_url = make_absolute_url(src, url)
                    if is_valid_recipe_image(img_url):
                        return img_url

    except Exception as e:
        logger.debug(f"OGイメージ抽出エラー: {e}")
        return None

    return None


async def backfill_recipe_images(dry_run: bool = False, limit: int = None):
    """画像がないレシピに画像を追加（source_urlからスクレイピング）"""

    image_service = ImageDownloadService()

    with Session(engine) as session:
        # 画像がないレシピを取得
        stmt = select(Recipe).where(
            Recipe.image_path == None,
            Recipe.source_url != None  # source_urlがあるもののみ
        ).order_by(Recipe.id.desc())

        if limit:
            stmt = stmt.limit(limit)

        recipes = session.exec(stmt).all()

        logger.info(f"画像なしレシピ: {len(recipes)}件")

        if dry_run:
            logger.info("=== DRY RUN モード ===")

        success_count = 0
        fail_count = 0

        for recipe in recipes:
            try:
                logger.info(f"ID {recipe.id}: {recipe.title[:40]}...")
                logger.info(f"  -> URL: {recipe.source_url[:60]}...")

                # source_urlからOGイメージを取得
                image_url = await extract_og_image(recipe.source_url)

                if not image_url:
                    logger.warning(f"  -> 画像URL取得不可")
                    fail_count += 1
                    continue

                logger.info(f"  -> 画像URL: {image_url[:60]}...")

                if dry_run:
                    success_count += 1
                    continue

                # 画像をダウンロード
                image_path = await image_service.download_and_save(
                    url=image_url,
                    recipe_id=recipe.id
                )

                if image_path:
                    recipe.image_url = image_url
                    recipe.image_path = image_path
                    session.add(recipe)
                    success_count += 1
                    logger.info(f"  -> 保存: {image_path}")
                else:
                    fail_count += 1
                    logger.warning(f"  -> ダウンロード失敗")

                # レート制限対策（0.5秒待機）
                await asyncio.sleep(0.5)

            except Exception as e:
                fail_count += 1
                logger.error(f"ID {recipe.id}: エラー - {e}")

        if not dry_run:
            session.commit()
            logger.info(f"コミット完了")

        logger.info(f"=== 完了 ===")
        logger.info(f"成功: {success_count}件")
        logger.info(f"失敗: {fail_count}件")

        return success_count, fail_count


async def main():
    import argparse
    parser = argparse.ArgumentParser(description='既存レシピに画像を追加')
    parser.add_argument('--dry-run', action='store_true', help='実際には変更せず確認のみ')
    parser.add_argument('--limit', type=int, default=None, help='処理するレシピ数の上限')
    args = parser.parse_args()

    await backfill_recipe_images(dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    asyncio.run(main())

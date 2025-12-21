"""
Image Download Service - 海外レシピ画像ダウンロード機能
URL から画像をダウンロードして保存する
"""

import hashlib
import logging
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class ImageDownloadService:
    """レシピ画像ダウンロードサービス"""

    IMAGES_DIR = "data/images"
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    MAX_SIZE_MB = 10
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
    TIMEOUT_SECONDS = 30

    def __init__(self, save_dir: str = "data/images"):
        """
        Args:
            save_dir: 画像保存ディレクトリ
        """
        self.save_dir = Path(save_dir)
        self.IMAGES_DIR = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def _validate_url(self, url: str) -> bool:
        """URL の妥当性チェック"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    def _get_extension_from_url(self, url: str) -> Optional[str]:
        """URL から拡張子を抽出"""
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1].lower()
        return ext if ext in self.ALLOWED_EXTENSIONS else None

    def _get_extension_from_content_type(self, content_type: str) -> Optional[str]:
        """Content-Type から拡張子を推定"""
        mapping = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        return mapping.get(content_type.lower().split(";")[0].strip())

    def _generate_filename(
        self, recipe_id: int, url: str, extension: str
    ) -> str:
        """ファイル名を生成（recipe_id + URLハッシュ）"""
        # URLをハッシュ化して短いユニークな文字列を生成
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{recipe_id}_{url_hash}{extension}"

    async def download_and_save(
        self, url: str, recipe_id: int
    ) -> Optional[str]:
        """
        画像をダウンロードして保存

        Args:
            url: 画像URL
            recipe_id: レシピID

        Returns:
            保存したファイルパス（相対パス）、失敗時は None
        """
        if not self._validate_url(url):
            logger.warning(f"Invalid URL: {url}")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Content-Lengthによる事前サイズチェック
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > self.MAX_SIZE_BYTES:
                    logger.warning(
                        f"Image too large: {content_length} bytes (max: {self.MAX_SIZE_BYTES})"
                    )
                    return None

                # 実際のコンテンツサイズチェック
                content = response.content
                if len(content) > self.MAX_SIZE_BYTES:
                    logger.warning(
                        f"Image content too large: {len(content)} bytes (max: {self.MAX_SIZE_BYTES})"
                    )
                    return None

                # 拡張子を決定（Content-Type優先、URLからフォールバック）
                content_type = response.headers.get("content-type", "")
                ext = self._get_extension_from_content_type(content_type)

                if not ext:
                    ext = self._get_extension_from_url(url)

                if not ext or ext not in self.ALLOWED_EXTENSIONS:
                    logger.warning(f"Unsupported image format: {content_type} / URL: {url}")
                    return None

                # ファイル名生成
                filename = self._generate_filename(recipe_id, url, ext)
                filepath = self.save_dir / filename

                # ディレクトリトラバーサル対策：絶対パスを確認
                abs_filepath = filepath.resolve()
                abs_save_dir = self.save_dir.resolve()

                if not str(abs_filepath).startswith(str(abs_save_dir)):
                    logger.error(
                        f"Directory traversal detected: {filepath} is outside {self.save_dir}"
                    )
                    return None

                # 保存
                with open(filepath, "wb") as f:
                    f.write(content)

                logger.info(f"Downloaded image: {url} -> {filepath}")
                return str(filepath)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error downloading image {url}: {e.response.status_code}")
            return None
        except httpx.TimeoutException:
            logger.error(f"Timeout downloading image {url}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}", exc_info=True)
            return None

    def get_image_path(self, recipe_id: int) -> Optional[str]:
        """
        レシピIDから画像パスを取得（ディレクトリ内を検索）

        Args:
            recipe_id: レシピID

        Returns:
            画像の相対パス（存在する場合）、None（存在しない場合）
        """
        try:
            # data/images/ 内で recipe_id で始まるファイルを検索
            pattern = f"{recipe_id}_*"

            for filepath in self.save_dir.glob(pattern):
                if filepath.is_file():
                    return str(filepath)

            return None

        except Exception as e:
            logger.error(f"Error getting image path for recipe {recipe_id}: {e}")
            return None

    def delete_image(self, image_path: str) -> bool:
        """
        画像ファイルを削除

        Args:
            image_path: 画像の相対パス

        Returns:
            削除成功: True、失敗: False
        """
        try:
            # ディレクトリトラバーサル対策
            filepath = Path(image_path)
            abs_filepath = filepath.resolve()
            abs_save_dir = self.save_dir.resolve()

            if not str(abs_filepath).startswith(str(abs_save_dir)):
                logger.error(
                    f"Directory traversal detected: {image_path} is outside {self.save_dir}"
                )
                return False

            if abs_filepath.exists():
                abs_filepath.unlink()
                logger.info(f"Image deleted: {image_path}")
                return True
            else:
                logger.warning(f"Image not found: {image_path}")
                return False

        except Exception as e:
            logger.error(f"Error deleting image {image_path}: {e}")
            return False

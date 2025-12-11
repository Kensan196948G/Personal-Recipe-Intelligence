"""
YouTube動画からレシピ情報を抽出するモジュール
"""

import re
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
import yt_dlp

from .models import VideoRecipe
from .transcript_parser import TranscriptParser

logger = logging.getLogger(__name__)


class YouTubeExtractor:
    """YouTube動画からレシピ情報を抽出"""

    def __init__(self):
        """初期化"""
        self.transcript_parser = TranscriptParser()
        self.yt_dlp_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        YouTube URLから動画IDを抽出

        Args:
            url: YouTube動画URL

        Returns:
            動画ID、抽出失敗時はNone
        """
        try:
            # URLパターン: https://www.youtube.com/watch?v=VIDEO_ID
            # または: https://youtu.be/VIDEO_ID
            parsed = urlparse(url)

            if "youtube.com" in parsed.netloc:
                query = parse_qs(parsed.query)
                return query.get("v", [None])[0]
            elif "youtu.be" in parsed.netloc:
                return parsed.path.lstrip("/")

            logger.warning(f"Invalid YouTube URL format: {url}")
            return None

        except Exception as e:
            logger.error(f"Failed to extract video ID from URL: {url}, error: {e}")
            return None

    def get_video_metadata(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        yt-dlpを使用して動画メタデータを取得

        Args:
            video_id: YouTube動画ID

        Returns:
            動画メタデータ、取得失敗時はNone
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"

            with yt_dlp.YoutubeDL(self.yt_dlp_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            return {
                "title": info.get("title"),
                "description": info.get("description"),
                "channel": info.get("channel") or info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail_url": info.get("thumbnail"),
                "upload_date": info.get("upload_date"),
                "view_count": info.get("view_count"),
                "tags": info.get("tags", []),
            }

        except Exception as e:
            logger.error(f"Failed to get video metadata for {video_id}: {e}")
            return None

    def get_transcript(
        self, video_id: str, languages: List[str] = ["ja", "en"]
    ) -> Optional[Dict[str, Any]]:
        """
        動画の字幕（トランスクリプト）を取得

        Args:
            video_id: YouTube動画ID
            languages: 優先言語リスト

        Returns:
            トランスクリプトデータ、取得失敗時はNone
        """
        try:
            # 字幕取得を試行
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # 優先言語で取得を試みる
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    transcript_data = transcript.fetch()

                    return {
                        "language": lang,
                        "data": transcript_data,
                        "is_generated": transcript.is_generated,
                    }
                except NoTranscriptFound:
                    continue

            # 優先言語がない場合、利用可能な最初の字幕を取得
            try:
                transcript = transcript_list.find_generated_transcript(languages)
                transcript_data = transcript.fetch()

                return {
                    "language": transcript.language_code,
                    "data": transcript_data,
                    "is_generated": True,
                }
            except NoTranscriptFound:
                logger.warning(f"No transcript available for video {video_id}")
                return None

        except TranscriptsDisabled:
            logger.warning(f"Transcripts are disabled for video {video_id}")
            return None
        except VideoUnavailable:
            logger.error(f"Video {video_id} is unavailable")
            return None
        except Exception as e:
            logger.error(f"Failed to get transcript for {video_id}: {e}")
            return None

    def extract_ingredients_from_description(self, description: str) -> List[str]:
        """
        動画説明文から材料リストを抽出

        Args:
            description: 動画説明文

        Returns:
            材料リスト
        """
        if not description:
            return []

        ingredients = []

        # 材料セクションを検出（日本語・英語対応）
        patterns = [
            r"(?:材料|Ingredients?)[:：]\s*(.*?)(?:\n\n|作り方|Instructions?|手順|$)",
            r"(?:＜材料＞|【材料】)\s*(.*?)(?:\n\n|＜作り方＞|【作り方】|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                ingredients_text = match.group(1)

                # 各行を材料として抽出（空行・ヘッダー除く）
                for line in ingredients_text.split("\n"):
                    line = line.strip()
                    if line and not re.match(r"^[＜＞【】\-\*]+$", line):
                        # 余分な記号を除去
                        cleaned = re.sub(r"^[・\-\*\+]\s*", "", line)
                        if cleaned:
                            ingredients.append(cleaned)

                break

        return ingredients

    def extract_recipe(
        self, url: str, language: str = "ja", extract_from_description: bool = True
    ) -> Optional[VideoRecipe]:
        """
        YouTube URLからレシピ情報を抽出

        Args:
            url: YouTube動画URL
            language: 優先字幕言語
            extract_from_description: 説明文からもレシピ情報を抽出するか

        Returns:
            抽出されたレシピデータ、失敗時はNone
        """
        try:
            # 動画IDを抽出
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.error("Failed to extract video ID from URL")
                return None

            # メタデータを取得
            metadata = self.get_video_metadata(video_id)
            if not metadata:
                logger.error("Failed to get video metadata")
                return None

            # トランスクリプトを取得
            transcript_info = self.get_transcript(video_id, [language, "en", "ja"])

            # レシピ情報を初期化
            recipe = VideoRecipe(
                video_id=video_id,
                url=url,
                title=metadata.get("title", ""),
                description=metadata.get("description"),
                channel=metadata.get("channel"),
                duration=metadata.get("duration"),
                thumbnail_url=metadata.get("thumbnail_url"),
                recipe_name=metadata.get("title"),
                tags=metadata.get("tags", []),
                extracted_at=datetime.utcnow().isoformat() + "Z",
            )

            # トランスクリプトからレシピ情報を抽出
            if transcript_info:
                recipe.has_transcript = True
                recipe.transcript_language = transcript_info["language"]

                # トランスクリプトテキストを結合
                transcript_text = " ".join([t["text"] for t in transcript_info["data"]])

                # レシピパース
                parsed_recipe = self.transcript_parser.parse_recipe(
                    transcript_text, transcript_info["data"]
                )

                if parsed_recipe.get("ingredients"):
                    recipe.ingredients.extend(parsed_recipe["ingredients"])
                if parsed_recipe.get("steps"):
                    recipe.steps.extend(parsed_recipe["steps"])
                if parsed_recipe.get("servings"):
                    recipe.servings = parsed_recipe["servings"]
                if parsed_recipe.get("cooking_time"):
                    recipe.cooking_time = parsed_recipe["cooking_time"]

            # 説明文からも抽出
            if extract_from_description and metadata.get("description"):
                desc_ingredients = self.extract_ingredients_from_description(
                    metadata["description"]
                )

                # 重複を避けて追加
                for ing in desc_ingredients:
                    if ing not in recipe.ingredients:
                        recipe.ingredients.append(ing)

            logger.info(
                f"Successfully extracted recipe from video {video_id}: "
                f"{len(recipe.ingredients)} ingredients, {len(recipe.steps)} steps"
            )

            return recipe

        except Exception as e:
            logger.error(f"Failed to extract recipe from {url}: {e}", exc_info=True)
            return None

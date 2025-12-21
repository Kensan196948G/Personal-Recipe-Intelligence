"""
YouTubeExtractorのテスト
"""

from unittest.mock import Mock, patch, MagicMock

from backend.video.youtube_extractor import YouTubeExtractor
from backend.video.models import VideoRecipe


class TestYouTubeExtractor:
    """YouTubeExtractorのテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前の初期化"""
        self.extractor = YouTubeExtractor()

    def test_extract_video_id_standard_url(self):
        """標準YouTube URLから動画IDを抽出"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = self.extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_short_url(self):
        """短縮YouTube URLから動画IDを抽出"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = self.extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_with_parameters(self):
        """パラメータ付きURLから動画IDを抽出"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
        video_id = self.extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_invalid_url(self):
        """無効なURLの場合Noneを返す"""
        url = "https://example.com/video"
        video_id = self.extractor.extract_video_id(url)
        assert video_id is None

    @patch("backend.video.youtube_extractor.yt_dlp.YoutubeDL")
    def test_get_video_metadata(self, mock_ydl_class):
        """動画メタデータの取得テスト"""
        # モックの設定
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            "title": "Test Recipe Video",
            "description": "Test description",
            "channel": "Test Channel",
            "duration": 300,
            "thumbnail": "https://example.com/thumb.jpg",
            "tags": ["recipe", "cooking"],
        }

        # テスト実行
        video_id = "test_video_id"
        metadata = self.extractor.get_video_metadata(video_id)

        # 検証
        assert metadata is not None
        assert metadata["title"] == "Test Recipe Video"
        assert metadata["channel"] == "Test Channel"
        assert metadata["duration"] == 300
        assert "recipe" in metadata["tags"]

    def test_extract_ingredients_from_description(self):
        """説明文から材料を抽出"""
        description = """
材料:
・玉ねぎ 1個
・にんじん 2本
・豚肉 300g

作り方:
1. 野菜を切ります
"""
        ingredients = self.extractor.extract_ingredients_from_description(description)

        assert len(ingredients) > 0
        assert any("玉ねぎ" in ing for ing in ingredients)
        assert any("にんじん" in ing for ing in ingredients)

    def test_extract_ingredients_from_description_empty(self):
        """材料セクションがない場合"""
        description = "これは普通の動画説明文です。"
        ingredients = self.extractor.extract_ingredients_from_description(description)

        assert ingredients == []

    @patch("backend.video.youtube_extractor.YouTubeTranscriptApi")
    def test_get_transcript(self, mock_transcript_api):
        """字幕取得のテスト"""
        # モックの設定
        mock_transcript = Mock()
        mock_transcript.language_code = "ja"
        mock_transcript.is_generated = False
        mock_transcript.fetch.return_value = [
            {"text": "こんにちは", "start": 0.0, "duration": 2.0},
            {"text": "今日は料理を作ります", "start": 2.0, "duration": 3.0},
        ]

        mock_transcript_list = Mock()
        mock_transcript_list.find_transcript.return_value = mock_transcript
        mock_transcript_api.list_transcripts.return_value = mock_transcript_list

        # テスト実行
        video_id = "test_video_id"
        transcript_info = self.extractor.get_transcript(video_id)

        # 検証
        assert transcript_info is not None
        assert transcript_info["language"] == "ja"
        assert len(transcript_info["data"]) == 2
        assert transcript_info["data"][0]["text"] == "こんにちは"

    @patch.object(YouTubeExtractor, "get_video_metadata")
    @patch.object(YouTubeExtractor, "get_transcript")
    @patch.object(YouTubeExtractor, "extract_video_id")
    def test_extract_recipe_success(
        self, mock_extract_id, mock_get_transcript, mock_get_metadata
    ):
        """レシピ抽出の正常系テスト"""
        # モックの設定
        mock_extract_id.return_value = "test_video_id"

        mock_get_metadata.return_value = {
            "title": "簡単カレーの作り方",
            "description": "材料:\n玉ねぎ 1個\nカレールー 1箱",
            "channel": "料理チャンネル",
            "duration": 600,
            "thumbnail_url": "https://example.com/thumb.jpg",
            "tags": ["カレー", "料理"],
        }

        mock_get_transcript.return_value = {
            "language": "ja",
            "data": [
                {"text": "まず玉ねぎを切ります", "start": 10.0, "duration": 3.0},
                {"text": "次に炒めます", "start": 13.0, "duration": 2.0},
            ],
            "is_generated": False,
        }

        # テスト実行
        url = "https://www.youtube.com/watch?v=test_video_id"
        recipe = self.extractor.extract_recipe(url)

        # 検証
        assert recipe is not None
        assert isinstance(recipe, VideoRecipe)
        assert recipe.video_id == "test_video_id"
        assert recipe.title == "簡単カレーの作り方"
        assert recipe.has_transcript is True
        assert len(recipe.ingredients) > 0

    @patch.object(YouTubeExtractor, "extract_video_id")
    def test_extract_recipe_invalid_url(self, mock_extract_id):
        """無効なURLでレシピ抽出を試みる"""
        mock_extract_id.return_value = None

        url = "https://invalid-url.com/video"
        recipe = self.extractor.extract_recipe(url)

        assert recipe is None

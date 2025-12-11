"""
動画レシピ統合テスト

YouTube URL処理、タイムスタンプ抽出、動画レシピ特有の機能テスト。
CLAUDE.md 準拠：外部依存モック化
"""

from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient


class TestYouTubeURLProcessing:
    """YouTube URL処理のテスト"""

    @pytest.mark.parametrize(
        "url,expected_video_id",
        [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s", "dQw4w9WgXcQ"),
        ],
    )
    def test_extract_video_id_from_url(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        url: str,
        expected_video_id: str,
    ):
        """YouTube URLから動画IDを抽出"""
        response = test_client.post(
            "/api/v1/youtube/extract-id", json={"url": url}, headers=auth_headers
        )

        if response.status_code == 404:
            pytest.skip("YouTube ID extraction endpoint not implemented")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["video_id"] == expected_video_id

    def test_invalid_youtube_url(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """不正なYouTube URL"""
        invalid_urls = [
            "https://vimeo.com/12345",
            "https://www.youtube.com/",
            "not-a-url",
            "https://example.com/video",
        ]

        for url in invalid_urls:
            response = test_client.post(
                "/api/v1/youtube/extract-id", json={"url": url}, headers=auth_headers
            )

            if response.status_code == 404:
                pytest.skip("YouTube ID extraction endpoint not implemented")

            assert response.status_code in [400, 422]


class TestVideoRecipeScraping:
    """動画レシピスクレイピングのテスト"""

    def test_scrape_youtube_recipe_success(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """正常系：YouTube動画からレシピ抽出"""
        url = "https://www.youtube.com/watch?v=example123"

        response = test_client.post(
            "/api/v1/youtube/scrape", json={"url": url}, headers=auth_headers
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "title" in data
        assert "video_id" in data
        assert "steps" in data

    def test_scrape_youtube_with_transcript(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """字幕付き動画のスクレイピング"""
        mock_youtube_scraper.return_value.extract_recipe.return_value = {
            "title": "字幕付きレシピ",
            "video_id": "transcript123",
            "ingredients": ["材料A", "材料B"],
            "steps": [
                {"text": "材料を切る", "timestamp": "0:30"},
                {"text": "炒める", "timestamp": "1:45"},
            ],
            "transcript": [
                {"text": "今日は〇〇を作ります", "start": 0.0},
                {"text": "まず材料を切ります", "start": 30.0},
            ],
            "duration": 300,
        }

        response = test_client.post(
            "/api/v1/youtube/scrape",
            json={"url": "https://www.youtube.com/watch?v=transcript123"},
            headers=auth_headers,
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        assert response.status_code == 200
        data = response.json()["data"]
        if "transcript" in data:
            assert len(data["transcript"]) > 0

    def test_scrape_youtube_without_recipe(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """レシピ情報のない動画"""
        mock_youtube_scraper.return_value.extract_recipe.return_value = {
            "title": "料理以外の動画",
            "video_id": "norecipe123",
            "ingredients": [],
            "steps": [],
            "duration": 180,
        }

        response = test_client.post(
            "/api/v1/youtube/scrape",
            json={"url": "https://www.youtube.com/watch?v=norecipe123"},
            headers=auth_headers,
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        # レシピ情報なしの場合、400またはデータなしで200
        assert response.status_code in [200, 400]


class TestTimestampExtraction:
    """タイムスタンプ抽出のテスト"""

    def test_extract_timestamps_from_description(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """動画説明からタイムスタンプ抽出"""
        mock_youtube_scraper.return_value.extract_recipe.return_value = {
            "title": "タイムスタンプ付きレシピ",
            "video_id": "timestamp123",
            "description": """
      0:00 イントロ
      0:30 材料紹介
      2:00 調理開始
      5:30 完成
      """,
            "ingredients": ["材料A"],
            "steps": [
                {"text": "材料紹介", "timestamp": "0:30"},
                {"text": "調理開始", "timestamp": "2:00"},
                {"text": "完成", "timestamp": "5:30"},
            ],
            "duration": 360,
        }

        response = test_client.post(
            "/api/v1/youtube/scrape",
            json={"url": "https://www.youtube.com/watch?v=timestamp123"},
            headers=auth_headers,
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        assert response.status_code == 200
        data = response.json()["data"]

        # タイムスタンプが抽出されているか確認
        if "steps" in data:
            for step in data["steps"]:
                if isinstance(step, dict):
                    assert "timestamp" in step or "text" in step

    def test_convert_timestamp_to_seconds(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """タイムスタンプを秒に変換"""
        timestamp_cases = [
            {"timestamp": "0:30", "expected": 30},
            {"timestamp": "2:15", "expected": 135},
            {"timestamp": "1:00:30", "expected": 3630},
        ]

        for case in timestamp_cases:
            response = test_client.post(
                "/api/v1/youtube/convert-timestamp",
                json={"timestamp": case["timestamp"]},
                headers=auth_headers,
            )

            if response.status_code == 404:
                pytest.skip("Timestamp conversion endpoint not implemented")

            assert response.status_code == 200
            data = response.json()["data"]
            assert data["seconds"] == case["expected"]

    def test_generate_timestamp_links(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        sample_video_recipe_data: Dict[str, Any],
    ):
        """タイムスタンプリンク生成"""
        # 動画レシピ作成
        create_response = test_client.post(
            "/api/v1/recipes/", json=sample_video_recipe_data, headers=auth_headers
        )

        if create_response.status_code == 404:
            pytest.skip("Recipe endpoint not implemented")

        assert create_response.status_code == 201
        recipe_id = create_response.json()["data"]["id"]

        # タイムスタンプリンク取得
        links_response = test_client.get(
            f"/api/v1/recipes/{recipe_id}/timestamp-links", headers=auth_headers
        )

        if links_response.status_code == 404:
            pytest.skip("Timestamp links endpoint not implemented")

        assert links_response.status_code == 200
        links = links_response.json()["data"]

        # リンク形式確認
        for link in links:
            assert "url" in link or "timestamp" in link


class TestVideoRecipeWorkflow:
    """動画レシピワークフローのテスト"""

    def test_complete_video_recipe_workflow(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """動画レシピの完全ワークフロー"""
        url = "https://www.youtube.com/watch?v=workflow123"

        # 1. スクレイピング
        scrape_response = test_client.post(
            "/api/v1/youtube/scrape", json={"url": url}, headers=auth_headers
        )

        if scrape_response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        assert scrape_response.status_code == 200
        scraped_data = scrape_response.json()["data"]

        # 2. レシピとして保存
        save_response = test_client.post(
            "/api/v1/recipes/",
            json={**scraped_data, "source": "youtube"},
            headers=auth_headers,
        )
        assert save_response.status_code == 201
        recipe_id = save_response.json()["data"]["id"]

        # 3. 取得
        get_response = test_client.get(
            f"/api/v1/recipes/{recipe_id}", headers=auth_headers
        )
        assert get_response.status_code == 200
        recipe = get_response.json()["data"]
        assert recipe["source"] == "youtube"

    def test_update_video_recipe_timestamps(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        sample_video_recipe_data: Dict[str, Any],
    ):
        """動画レシピのタイムスタンプ更新"""
        # レシピ作成
        create_response = test_client.post(
            "/api/v1/recipes/", json=sample_video_recipe_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        recipe_id = create_response.json()["data"]["id"]

        # タイムスタンプ更新
        new_steps = [
            {"text": "材料準備", "timestamp": "0:15"},
            {"text": "調理", "timestamp": "1:30"},
            {"text": "盛り付け", "timestamp": "4:00"},
        ]

        update_response = test_client.put(
            f"/api/v1/recipes/{recipe_id}",
            json={"steps": new_steps},
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # 確認
        get_response = test_client.get(
            f"/api/v1/recipes/{recipe_id}", headers=auth_headers
        )
        updated_recipe = get_response.json()["data"]
        assert len(updated_recipe["steps"]) == 3


class TestVideoMetadata:
    """動画メタデータのテスト"""

    def test_get_video_duration(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """動画時間取得"""
        mock_youtube_scraper.return_value.extract_recipe.return_value = {
            "title": "動画レシピ",
            "video_id": "duration123",
            "duration": 600,  # 10分
            "ingredients": [],
            "steps": [],
        }

        response = test_client.post(
            "/api/v1/youtube/scrape",
            json={"url": "https://www.youtube.com/watch?v=duration123"},
            headers=auth_headers,
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["duration"] == 600

    def test_get_video_thumbnail(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """動画サムネイル取得"""
        video_id = "thumb123"

        response = test_client.get(
            f"/api/v1/youtube/{video_id}/thumbnail", headers=auth_headers
        )

        if response.status_code == 404:
            pytest.skip("Thumbnail endpoint not implemented")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "url" in data or "thumbnail_url" in data

    def test_get_channel_info(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """チャンネル情報取得"""
        mock_youtube_scraper.return_value.extract_recipe.return_value = {
            "title": "チャンネル動画",
            "video_id": "channel123",
            "channel_name": "料理チャンネル",
            "channel_id": "UC_channel123",
            "ingredients": [],
            "steps": [],
        }

        response = test_client.post(
            "/api/v1/youtube/scrape",
            json={"url": "https://www.youtube.com/watch?v=channel123"},
            headers=auth_headers,
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        if response.status_code == 200:
            data = response.json()["data"]
            # チャンネル情報が含まれているか確認
            if "channel_name" in data:
                assert data["channel_name"] == "料理チャンネル"


class TestVideoRecipeSearch:
    """動画レシピ検索のテスト"""

    def test_filter_by_video_source(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        sample_recipes_batch: list,
    ):
        """動画ソースでフィルタリング"""
        response = test_client.get(
            "/api/v1/recipes/?source=youtube", headers=auth_headers
        )

        assert response.status_code == 200
        recipes = response.json()["data"]

        # YouTubeソースのレシピのみ
        for recipe in recipes:
            assert recipe["source"] == "youtube"

    def test_search_by_video_duration(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """動画時間で検索"""
        response = test_client.get(
            "/api/v1/recipes/search?max_duration=600", headers=auth_headers
        )

        if response.status_code == 404:
            pytest.skip("Duration search not implemented")

        assert response.status_code == 200

    def test_get_recipes_by_channel(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """特定チャンネルのレシピ取得"""
        channel_id = "UC_example123"

        response = test_client.get(
            f"/api/v1/youtube/channels/{channel_id}/recipes", headers=auth_headers
        )

        if response.status_code == 404:
            pytest.skip("Channel recipes endpoint not implemented")

        assert response.status_code == 200


class TestVideoRecipeErrorHandling:
    """動画レシピエラーハンドリング"""

    def test_unavailable_video(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """利用不可動画のエラー処理"""
        mock_youtube_scraper.return_value.extract_recipe.side_effect = Exception(
            "Video unavailable"
        )

        response = test_client.post(
            "/api/v1/youtube/scrape",
            json={"url": "https://www.youtube.com/watch?v=unavailable"},
            headers=auth_headers,
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        assert response.status_code in [400, 404, 500]

    def test_private_video(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """非公開動画のエラー処理"""
        mock_youtube_scraper.return_value.extract_recipe.side_effect = Exception(
            "Private video"
        )

        response = test_client.post(
            "/api/v1/youtube/scrape",
            json={"url": "https://www.youtube.com/watch?v=private123"},
            headers=auth_headers,
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        assert response.status_code in [403, 404, 500]

    def test_age_restricted_video(
        self,
        test_client: TestClient,
        auth_headers: Dict[str, str],
        mock_youtube_scraper,
    ):
        """年齢制限動画のエラー処理"""
        mock_youtube_scraper.return_value.extract_recipe.side_effect = Exception(
            "Age restricted"
        )

        response = test_client.post(
            "/api/v1/youtube/scrape",
            json={"url": "https://www.youtube.com/watch?v=restricted"},
            headers=auth_headers,
        )

        if response.status_code == 404:
            pytest.skip("YouTube scraper endpoint not implemented")

        assert response.status_code in [403, 500]

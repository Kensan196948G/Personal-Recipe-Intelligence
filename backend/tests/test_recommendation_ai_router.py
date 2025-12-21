"""
レシピ推薦AI APIルーターのテスト
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.api.routers.recommendation_ai import router


@pytest.fixture
def app():
    """FastAPIアプリケーション"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """テストクライアント"""
    return TestClient(app)


class TestRecommendationAIRouter:
    """推薦AIルーターテスト"""

    def test_get_personalized_recommendations(self, client):
        """パーソナライズ推薦取得テスト"""
        response = client.get("/api/v1/ai/recommend?user_id=user_001&limit=5")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "data" in data
        assert "recommendations" in data["data"]
        assert "user_id" in data["data"]
        assert data["data"]["user_id"] == "user_001"

    def test_get_personalized_recommendations_without_user_id(self, client):
        """ユーザーIDなしでのリクエスト"""
        response = client.get("/api/v1/ai/recommend")

        assert response.status_code == 422  # Validation error

    def test_get_personalized_recommendations_with_invalid_limit(self, client):
        """無効なlimitパラメータ"""
        response = client.get("/api/v1/ai/recommend?user_id=user_001&limit=100")

        # limitは最大50なので、422エラー
        assert response.status_code == 422

    def test_get_similar_recipes(self, client):
        """類似レシピ取得テスト"""
        response = client.get("/api/v1/ai/recommend/similar/recipe_001?limit=3")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "data" in data
        assert "similar_recipes" in data["data"]
        assert "recipe_id" in data["data"]
        assert data["data"]["recipe_id"] == "recipe_001"

    def test_get_similar_recipes_invalid_id(self, client):
        """無効なレシピIDでの類似レシピ取得"""
        response = client.get("/api/v1/ai/recommend/similar/invalid_id")

        assert response.status_code == 404

    def test_get_trending_recipes(self, client):
        """トレンドレシピ取得テスト"""
        response = client.get("/api/v1/ai/recommend/trending?limit=10")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "data" in data
        assert "trending_recipes" in data["data"]

    def test_submit_feedback(self, client):
        """フィードバック送信テスト"""
        payload = {
            "user_id": "user_001",
            "recipe_id": "recipe_001",
            "feedback_type": "interested",
            "metadata": {"context": "recommendation"},
        }

        response = client.post("/api/v1/ai/feedback", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "data" in data
        assert data["data"]["message"] == "フィードバックを記録しました"
        assert data["data"]["user_id"] == "user_001"
        assert data["data"]["recipe_id"] == "recipe_001"

    def test_submit_feedback_invalid_type(self, client):
        """無効なフィードバックタイプ"""
        payload = {
            "user_id": "user_001",
            "recipe_id": "recipe_001",
            "feedback_type": "invalid_type",
        }

        response = client.post("/api/v1/ai/feedback", json=payload)

        assert response.status_code == 400
        assert "無効なフィードバックタイプ" in response.json()["detail"]

    def test_submit_feedback_missing_fields(self, client):
        """必須フィールド欠落"""
        payload = {
            "user_id": "user_001",
            # recipe_id と feedback_type が欠落
        }

        response = client.post("/api/v1/ai/feedback", json=payload)

        assert response.status_code == 422  # Validation error

    def test_record_activity(self, client):
        """ユーザー行動記録テスト"""
        payload = {
            "user_id": "user_001",
            "recipe_id": "recipe_001",
            "activity_type": "viewed",
            "metadata": {"source": "search"},
        }

        response = client.post("/api/v1/ai/activity", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "data" in data
        assert data["data"]["message"] == "行動を記録しました"
        assert data["data"]["activity_type"] == "viewed"

    def test_record_activity_invalid_type(self, client):
        """無効な行動タイプ"""
        payload = {
            "user_id": "user_001",
            "recipe_id": "recipe_001",
            "activity_type": "invalid_activity",
        }

        response = client.post("/api/v1/ai/activity", json=payload)

        assert response.status_code == 400
        assert "無効な行動タイプ" in response.json()["detail"]

    def test_get_user_preferences(self, client):
        """ユーザー嗜好取得テスト"""
        response = client.get("/api/v1/ai/preferences?user_id=user_001")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "data" in data
        assert "user_id" in data["data"]
        assert "total_activities" in data["data"]
        assert "favorite_ingredients" in data["data"]
        assert "favorite_categories" in data["data"]
        assert "cooking_frequency" in data["data"]

    def test_get_user_preferences_without_user_id(self, client):
        """ユーザーIDなしでの嗜好取得"""
        response = client.get("/api/v1/ai/preferences")

        assert response.status_code == 422  # Validation error

    def test_feedback_all_types(self, client):
        """全フィードバックタイプテスト"""
        valid_types = ["interested", "not_interested", "favorited", "cooked"]

        for feedback_type in valid_types:
            payload = {
                "user_id": "user_001",
                "recipe_id": "recipe_001",
                "feedback_type": feedback_type,
            }

            response = client.post("/api/v1/ai/feedback", json=payload)
            assert response.status_code == 200

    def test_activity_all_types(self, client):
        """全行動タイプテスト"""
        valid_types = ["viewed", "cooked", "rated", "favorited", "dismissed"]

        for activity_type in valid_types:
            payload = {
                "user_id": "user_001",
                "recipe_id": "recipe_001",
                "activity_type": activity_type,
            }

            response = client.post("/api/v1/ai/activity", json=payload)
            assert response.status_code == 200

    def test_recommendations_with_metadata(self, client):
        """メタデータ付きフィードバック"""
        payload = {
            "user_id": "user_001",
            "recipe_id": "recipe_001",
            "feedback_type": "interested",
            "metadata": {
                "source": "recommendation",
                "position": 1,
                "context": "homepage",
            },
        }

        response = client.post("/api/v1/ai/feedback", json=payload)

        assert response.status_code == 200

    def test_activity_with_rating_metadata(self, client):
        """評価メタデータ付き行動記録"""
        payload = {
            "user_id": "user_001",
            "recipe_id": "recipe_001",
            "activity_type": "rated",
            "metadata": {"rating": 5},
        }

        response = client.post("/api/v1/ai/activity", json=payload)

        assert response.status_code == 200

    def test_limit_boundary_values(self, client):
        """limit境界値テスト"""
        # 最小値
        response = client.get("/api/v1/ai/recommend?user_id=user_001&limit=1")
        assert response.status_code == 200

        # 最大値
        response = client.get("/api/v1/ai/recommend?user_id=user_001&limit=50")
        assert response.status_code == 200

        # 範囲外（0）
        response = client.get("/api/v1/ai/recommend?user_id=user_001&limit=0")
        assert response.status_code == 422

        # 範囲外（51）
        response = client.get("/api/v1/ai/recommend?user_id=user_001&limit=51")
        assert response.status_code == 422

    def test_similar_recipes_limit_boundary(self, client):
        """類似レシピのlimit境界値テスト"""
        # 最小値
        response = client.get("/api/v1/ai/recommend/similar/recipe_001?limit=1")
        assert response.status_code == 200

        # 最大値
        response = client.get("/api/v1/ai/recommend/similar/recipe_001?limit=20")
        assert response.status_code == 200

        # 範囲外
        response = client.get("/api/v1/ai/recommend/similar/recipe_001?limit=21")
        assert response.status_code == 422

    def test_response_structure(self, client):
        """レスポンス構造テスト"""
        response = client.get("/api/v1/ai/recommend?user_id=user_001")
        data = response.json()

        # 標準レスポンス構造
        assert "status" in data
        assert data["status"] == "ok"
        assert "data" in data
        assert "error" not in data or data["error"] is None

    def test_error_response_structure(self, client):
        """エラーレスポンス構造テスト"""
        response = client.get("/api/v1/ai/recommend/similar/invalid_id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_concurrent_requests(self, client):
        """同時リクエストテスト"""
        import concurrent.futures

        def make_request():
            return client.get("/api/v1/ai/recommend?user_id=user_001")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]

        # すべて成功するはず
        for response in results:
            assert response.status_code == 200

    def test_recommendation_response_fields(self, client):
        """推薦レスポンスフィールドテスト"""
        response = client.get("/api/v1/ai/recommend?user_id=user_001&limit=1")
        data = response.json()

        if len(data["data"]["recommendations"]) > 0:
            rec = data["data"]["recommendations"][0]

            assert "recipe" in rec
            assert "score" in rec
            assert "reason" in rec
            assert "match_percentage" in rec

            # レシピオブジェクトの構造
            recipe = rec["recipe"]
            assert "id" in recipe
            assert "title" in recipe
            assert "category" in recipe

    def test_preferences_response_fields(self, client):
        """嗜好レスポンスフィールドテスト"""
        response = client.get("/api/v1/ai/preferences?user_id=user_001")
        data = response.json()

        preferences = data["data"]

        required_fields = [
            "user_id",
            "total_activities",
            "favorite_ingredients",
            "favorite_categories",
            "favorite_tags",
            "cooking_frequency",
            "average_cooking_time",
            "preferred_difficulty",
        ]

        for field in required_fields:
            assert field in preferences

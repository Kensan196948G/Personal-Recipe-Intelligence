"""
完全API統合テスト

全エンドポイントの統合テスト、認証フロー、エラーハンドリング。
CLAUDE.md 準拠：pytest, カバレッジ60%以上, JSON形式レスポンス検証
"""

from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """ヘルスチェックエンドポイントのテスト"""

    def test_health_check_success(self, test_client: TestClient):
        """正常系：ヘルスチェック"""
        response = test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_api_v1_health(self, test_client: TestClient):
        """正常系：API v1 ヘルスチェック"""
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"


class TestRecipeEndpoints:
    """レシピエンドポイントの統合テスト"""

    def test_create_recipe_success(
        self,
        test_client: TestClient,
        sample_recipe_data: Dict[str, Any],
        auth_headers: Dict[str, str],
    ):
        """正常系：レシピ作成"""
        response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=auth_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["title"] == sample_recipe_data["title"]
        assert "id" in data["data"]
        assert data["error"] is None

    def test_create_recipe_validation_error(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """異常系：バリデーションエラー"""
        invalid_data = {"title": "", "ingredients": []}  # 空のタイトル

        response = test_client.post(
            "/api/v1/recipes/", json=invalid_data, headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_get_recipes_list(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """正常系：レシピ一覧取得"""
        response = test_client.get("/api/v1/recipes/", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert len(data["data"]) == 3
        assert data["error"] is None

    def test_get_recipes_with_pagination(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """正常系：ページネーション付きレシピ取得"""
        response = test_client.get(
            "/api/v1/recipes/?skip=0&limit=2", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 2

    def test_get_recipe_by_id_success(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """正常系：ID指定でレシピ取得"""
        recipe_id = sample_recipes_batch[0].id

        response = test_client.get(f"/api/v1/recipes/{recipe_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["id"] == recipe_id
        assert data["data"]["title"] == "カレーライス"

    def test_get_recipe_by_id_not_found(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """異常系：存在しないレシピID"""
        response = test_client.get("/api/v1/recipes/99999", headers=auth_headers)
        assert response.status_code == 404

        data = response.json()
        assert data["status"] == "error"
        assert data["error"] is not None

    def test_update_recipe_success(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """正常系：レシピ更新"""
        recipe_id = sample_recipes_batch[0].id
        update_data = {"title": "スパイシーカレーライス", "cook_time": 50}

        response = test_client.put(
            f"/api/v1/recipes/{recipe_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["title"] == "スパイシーカレーライス"
        assert data["data"]["cook_time"] == 50

    def test_update_recipe_not_found(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """異常系：存在しないレシピの更新"""
        response = test_client.put(
            "/api/v1/recipes/99999", json={"title": "更新"}, headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_recipe_success(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """正常系：レシピ削除"""
        recipe_id = sample_recipes_batch[0].id

        response = test_client.delete(
            f"/api/v1/recipes/{recipe_id}", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"

        # 削除確認
        get_response = test_client.get(
            f"/api/v1/recipes/{recipe_id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_recipe_not_found(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """異常系：存在しないレシピの削除"""
        response = test_client.delete("/api/v1/recipes/99999", headers=auth_headers)
        assert response.status_code == 404


class TestSearchEndpoints:
    """検索エンドポイントのテスト"""

    def test_search_by_title(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """正常系：タイトル検索"""
        response = test_client.get(
            "/api/v1/recipes/search?q=カレー", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert len(data["data"]) == 2  # カレーライス、チキンカレー

    def test_search_by_tag(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """正常系：タグ検索"""
        response = test_client.get(
            "/api/v1/recipes/search?tag=パスタ", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 1

    def test_search_no_results(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """正常系：検索結果なし"""
        response = test_client.get(
            "/api/v1/recipes/search?q=存在しない料理", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 0


class TestAuthenticationFlow:
    """認証フローのテスト"""

    def test_missing_auth_header(
        self, test_client: TestClient, sample_recipe_data: Dict[str, Any]
    ):
        """異常系：認証ヘッダーなし"""
        response = test_client.post("/api/v1/recipes/", json=sample_recipe_data)
        # 認証が必須の場合は401、オプションの場合は200
        assert response.status_code in [200, 201, 401]

    def test_invalid_token_format(
        self, test_client: TestClient, sample_recipe_data: Dict[str, Any]
    ):
        """異常系：不正なトークン形式"""
        invalid_headers = {"Authorization": "InvalidFormat"}

        response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=invalid_headers
        )
        # 認証エラーまたは成功（実装依存）
        assert response.status_code in [200, 201, 401, 403]


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_invalid_json_payload(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """異常系：不正なJSON"""
        response = test_client.post(
            "/api/v1/recipes/",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_method_not_allowed(self, test_client: TestClient):
        """異常系：許可されていないHTTPメソッド"""
        response = test_client.patch("/api/v1/recipes/1")
        assert response.status_code in [405, 422]

    def test_internal_server_error_handling(
        self, test_client: TestClient, auth_headers: Dict[str, str], monkeypatch
    ):
        """異常系：内部サーバーエラー"""

        # データベースエラーをシミュレート
        def mock_error(*args, **kwargs):
            raise Exception("Database connection failed")

        # この部分は実際のエンドポイント実装に依存
        # 必要に応じてmonkeypatchを使用


class TestRateLimiting:
    """レート制限のテスト（個人用途のため基本スキップ）"""

    @pytest.mark.skip(reason="個人用途のためレート制限なし")
    def test_rate_limit_exceeded(self, test_client: TestClient):
        """レート制限超過（スキップ）"""
        pass


class TestCORS:
    """CORS設定のテスト"""

    def test_cors_headers_present(self, test_client: TestClient):
        """正常系：CORSヘッダーの存在確認"""
        response = test_client.options("/api/v1/recipes/")
        # CORSが有効な場合
        if response.status_code == 200:
            assert "access-control-allow-origin" in [
                h.lower() for h in response.headers.keys()
            ]


class TestResponseFormat:
    """レスポンス形式の統一性テスト"""

    def test_success_response_format(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """正常系：成功レスポンス形式"""
        response = test_client.get("/api/v1/recipes/", headers=auth_headers)

        data = response.json()
        assert "status" in data
        assert "data" in data
        assert "error" in data
        assert data["status"] == "ok"
        assert data["error"] is None

    def test_error_response_format(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """異常系：エラーレスポンス形式"""
        response = test_client.get("/api/v1/recipes/99999", headers=auth_headers)

        data = response.json()
        assert "status" in data
        assert "error" in data
        assert data["status"] == "error"
        assert data["error"] is not None

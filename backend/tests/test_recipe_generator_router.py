"""
レシピ自動生成 API ルーターのテスト
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.routers.recipe_generator import router
from fastapi import FastAPI


@pytest.fixture
def client():
    """テスト用のFastAPIクライアント"""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestRecipeGeneratorRouter:
    """レシピ自動生成 API ルーターのテスト"""

    def test_generate_recipe(self, client):
        """レシピ生成エンドポイントのテスト"""
        response = client.post(
            "/api/v1/ai/generate",
            json={
                "ingredients": ["鶏肉"],
                "category": "japanese",
                "cooking_time": None,
                "difficulty": None,
                "use_seasonal": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "data" in data
        assert "name" in data["data"]
        assert "ingredients" in data["data"]
        assert "steps" in data["data"]
        assert "nutrition" in data["data"]

    def test_generate_recipe_with_options(self, client):
        """オプション付きレシピ生成のテスト"""
        response = client.post(
            "/api/v1/ai/generate",
            json={
                "ingredients": ["豚肉", "キャベツ"],
                "category": "chinese",
                "cooking_time": 20,
                "difficulty": "easy",
                "use_seasonal": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["category"] == "chinese"
        assert data["data"]["difficulty"] == "easy"
        assert data["data"]["cooking_time"] <= 20

    def test_generate_recipe_no_ingredients(self, client):
        """食材なしでのレシピ生成（エラーケース）"""
        response = client.post(
            "/api/v1/ai/generate", json={"ingredients": [], "category": "japanese"}
        )

        # 空配列はValidationErrorとして422または400を返す
        assert response.status_code in [400, 422]

    def test_generate_recipe_invalid_category(self, client):
        """無効なカテゴリでのレシピ生成（エラーケース）"""
        response = client.post(
            "/api/v1/ai/generate", json={"ingredients": ["鶏肉"], "category": "invalid"}
        )

        assert response.status_code == 400

    def test_generate_variations(self, client):
        """バリエーション生成エンドポイントのテスト"""
        # まずレシピを生成
        base_recipe = {
            "id": "test_001",
            "name": "鶏肉の炒め物",
            "category": "japanese",
            "cooking_time": 15,
            "difficulty": "easy",
            "ingredients": [
                {"name": "鶏肉", "amount": "200g", "unit": ""},
                {"name": "玉ねぎ", "amount": "1個", "unit": ""},
            ],
            "steps": ["手順1", "手順2"],
            "servings": 2,
            "tags": ["japanese"],
        }

        response = client.post(
            "/api/v1/ai/generate/variations",
            json={"base_recipe": base_recipe, "count": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        for variation in data["data"]:
            assert "nutrition" in variation

    def test_get_suggestions(self, client):
        """食材組み合わせ提案エンドポイントのテスト"""
        response = client.get(
            "/api/v1/ai/generate/suggestions",
            params={"main_ingredient": "鶏肉", "count": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        for suggestion in data["data"]:
            assert "main" in suggestion
            assert "sub" in suggestion
            assert "compatibility_score" in suggestion

    def test_get_suggestions_no_ingredient(self, client):
        """食材なしでの提案取得（エラーケース）"""
        response = client.get(
            "/api/v1/ai/generate/suggestions",
            params={"main_ingredient": "", "count": 5},
        )

        assert response.status_code == 400

    def test_improve_recipe(self, client):
        """レシピ改善エンドポイントのテスト"""
        recipe = {
            "id": "test_001",
            "name": "鶏肉の炒め物",
            "category": "japanese",
            "cooking_time": 15,
            "difficulty": "easy",
            "ingredients": [
                {"name": "鶏肉", "amount": "200g", "unit": ""},
                {"name": "玉ねぎ", "amount": "1個", "unit": ""},
            ],
            "steps": ["手順1", "手順2"],
            "servings": 2,
            "tags": ["japanese"],
        }

        response = client.post(
            "/api/v1/ai/generate/improve", json={"recipe": recipe, "focus": "taste"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "data" in data
        assert "improved_at" in data["data"]
        assert "nutrition" in data["data"]

    def test_improve_recipe_health_focus(self, client):
        """レシピ改善（健康）のテスト"""
        recipe = {
            "id": "test_001",
            "name": "鶏肉の炒め物",
            "category": "japanese",
            "cooking_time": 30,
            "difficulty": "easy",
            "ingredients": [{"name": "鶏肉", "amount": "200g", "unit": ""}],
            "steps": ["手順1"],
            "servings": 2,
            "tags": [],
        }

        response = client.post(
            "/api/v1/ai/generate/improve", json={"recipe": recipe, "focus": "health"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["improvement_focus"] == "health"

    def test_improve_recipe_speed_focus(self, client):
        """レシピ改善（時短）のテスト"""
        recipe = {
            "id": "test_001",
            "name": "鶏肉の炒め物",
            "category": "japanese",
            "cooking_time": 30,
            "difficulty": "easy",
            "ingredients": [{"name": "鶏肉", "amount": "200g", "unit": ""}],
            "steps": ["手順1"],
            "servings": 2,
            "tags": [],
        }

        response = client.post(
            "/api/v1/ai/generate/improve", json={"recipe": recipe, "focus": "speed"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["improvement_focus"] == "speed"
        assert data["data"]["cooking_time"] < recipe["cooking_time"]

    def test_improve_recipe_cost_focus(self, client):
        """レシピ改善（節約）のテスト"""
        recipe = {
            "id": "test_001",
            "name": "鶏肉の炒め物",
            "category": "japanese",
            "cooking_time": 30,
            "difficulty": "easy",
            "ingredients": [{"name": "鶏肉", "amount": "200g", "unit": ""}],
            "steps": ["手順1"],
            "servings": 2,
            "tags": [],
        }

        response = client.post(
            "/api/v1/ai/generate/improve", json={"recipe": recipe, "focus": "cost"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["improvement_focus"] == "cost"

    def test_improve_recipe_invalid_focus(self, client):
        """無効な改善焦点でのレシピ改善（エラーケース）"""
        recipe = {
            "id": "test_001",
            "name": "鶏肉の炒め物",
            "category": "japanese",
            "cooking_time": 15,
            "difficulty": "easy",
            "ingredients": [{"name": "鶏肉", "amount": "200g", "unit": ""}],
            "steps": ["手順1"],
            "servings": 2,
            "tags": [],
        }

        response = client.post(
            "/api/v1/ai/generate/improve",
            json={"recipe": recipe, "focus": "invalid_focus"},
        )

        assert response.status_code == 400

    def test_get_categories(self, client):
        """カテゴリ取得エンドポイントのテスト"""
        response = client.get("/api/v1/ai/categories")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "categories" in data["data"]
        assert "difficulties" in data["data"]
        assert "improvement_focuses" in data["data"]

        assert "japanese" in data["data"]["categories"]
        assert "western" in data["data"]["categories"]
        assert "chinese" in data["data"]["categories"]

        assert "easy" in data["data"]["difficulties"]
        assert "medium" in data["data"]["difficulties"]
        assert "hard" in data["data"]["difficulties"]

    def test_get_ingredients(self, client):
        """食材リスト取得エンドポイントのテスト"""
        response = client.get("/api/v1/ai/ingredients")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "meat" in data["data"]
        assert "seafood" in data["data"]
        assert "vegetable" in data["data"]
        assert "mushroom" in data["data"]
        assert "tofu" in data["data"]

        assert isinstance(data["data"]["meat"], list)
        assert len(data["data"]["meat"]) > 0

    def test_request_validation(self, client):
        """リクエストバリデーションのテスト"""
        # cooking_time が範囲外
        response = client.post(
            "/api/v1/ai/generate",
            json={
                "ingredients": ["鶏肉"],
                "category": "japanese",
                "cooking_time": 200,  # 120を超える
            },
        )

        assert response.status_code == 422  # Validation Error

    def test_variations_count_validation(self, client):
        """バリエーション数のバリデーションテスト"""
        base_recipe = {
            "id": "test_001",
            "name": "鶏肉の炒め物",
            "category": "japanese",
            "ingredients": [{"name": "鶏肉", "amount": "200g", "unit": ""}],
            "steps": ["手順1"],
        }

        # count が範囲外
        response = client.post(
            "/api/v1/ai/generate/variations",
            json={
                "base_recipe": base_recipe,
                "count": 15,  # 10を超える
            },
        )

        assert response.status_code == 422  # Validation Error

    def test_response_structure(self, client):
        """レスポンス構造のテスト"""
        response = client.post(
            "/api/v1/ai/generate",
            json={"ingredients": ["鶏肉"], "category": "japanese"},
        )

        assert response.status_code == 200
        data = response.json()

        # レスポンスの基本構造
        assert "status" in data
        assert "data" in data
        assert data.get("error") is None

        # レシピデータの構造
        recipe = data["data"]
        assert "id" in recipe
        assert "name" in recipe
        assert "category" in recipe
        assert "cooking_time" in recipe
        assert "difficulty" in recipe
        assert "ingredients" in recipe
        assert "steps" in recipe
        assert "nutrition" in recipe

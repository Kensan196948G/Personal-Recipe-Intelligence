"""
栄養計算API のテスト
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.api.routers.nutrition import router


@pytest.fixture
def app():
    """FastAPI アプリケーションのフィクスチャ"""
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    """TestClient のフィクスチャ"""
    return TestClient(app)


class TestCalculateNutritionAPI:
    """栄養計算API のテスト"""

    def test_calculate_simple_recipe(self, client):
        """シンプルなレシピの栄養計算"""
        request_data = {
            "ingredients": [
                {"name": "白米", "amount": "200g"},
                {"name": "鶏もも肉", "amount": "100g"},
            ],
            "servings": 1,
        }

        response = client.post("/api/v1/nutrition/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["error"] is None
        assert "data" in data

        result = data["data"]
        assert result["servings"] == 1
        assert result["total_ingredients"] == 2
        assert result["found_ingredients"] == 2
        assert "per_serving" in result
        assert "total" in result
        assert "ingredients_breakdown" in result
        assert "summary" in result

        # 栄養素の確認
        per_serving = result["per_serving"]
        assert per_serving["calories"] > 0
        assert per_serving["protein"] > 0
        assert per_serving["fat"] >= 0
        assert per_serving["carbohydrates"] >= 0

    def test_calculate_multi_serving(self, client):
        """複数人前の計算"""
        request_data = {
            "ingredients": [{"name": "白米", "amount": "400g"}],
            "servings": 2,
        }

        response = client.post("/api/v1/nutrition/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        result = data["data"]
        assert result["servings"] == 2

        # 1人前は合計の半分
        per_serving_cal = result["per_serving"]["calories"]
        total_cal = result["total"]["calories"]
        assert abs(per_serving_cal * 2 - total_cal) < 0.5  # 丸め誤差を考慮

    def test_calculate_with_invalid_data(self, client):
        """不正なデータでのリクエスト"""
        request_data = {
            "ingredients": [],  # 空の材料リスト
            "servings": 1,
        }

        response = client.post("/api/v1/nutrition/calculate", json=request_data)

        # 空でも処理は成功する（栄養価は0）
        assert response.status_code == 200

    def test_calculate_missing_servings(self, client):
        """servings 省略時のデフォルト動作"""
        request_data = {
            "ingredients": [{"name": "白米", "amount": "200g"}],
            # servings を省略
        }

        response = client.post("/api/v1/nutrition/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        result = data["data"]
        assert result["servings"] == 1  # デフォルト値


class TestGetIngredientInfoAPI:
    """材料情報取得API のテスト"""

    def test_get_existing_ingredient(self, client):
        """存在する材料の情報取得"""
        response = client.get("/api/v1/nutrition/ingredient/鶏もも肉")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["error"] is None
        assert data["data"] is not None

        ingredient_data = data["data"]
        assert ingredient_data["name"] == "鶏もも肉"
        assert ingredient_data["calories"] == 200
        assert ingredient_data["protein"] == 16.2
        assert ingredient_data["unit"] == "100g"

    def test_get_non_existing_ingredient(self, client):
        """存在しない材料の情報取得"""
        response = client.get("/api/v1/nutrition/ingredient/存在しない材料")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["data"] is None  # 見つからない場合はNone


class TestListIngredientsAPI:
    """材料リスト取得API のテスト"""

    def test_list_all_ingredients(self, client):
        """全材料リストの取得"""
        response = client.get("/api/v1/nutrition/ingredients")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["error"] is None
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # いくつかの材料が含まれていることを確認
        ingredients = data["data"]
        assert "白米" in ingredients
        assert "鶏もも肉" in ingredients


class TestSearchIngredientsAPI:
    """材料検索API のテスト"""

    def test_search_chicken(self, client):
        """鶏肉の検索"""
        response = client.get("/api/v1/nutrition/search?q=鶏")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["error"] is None

        search_data = data["data"]
        assert search_data["query"] == "鶏"
        assert search_data["count"] >= 2  # 鶏もも肉、鶏むね肉
        assert len(search_data["results"]) >= 2

        # 結果に鶏が含まれていることを確認
        assert any("鶏" in r["name"] for r in search_data["results"])

    def test_search_partial_match(self, client):
        """部分一致検索"""
        response = client.get("/api/v1/nutrition/search?q=たま")

        assert response.status_code == 200
        data = response.json()

        search_data = data["data"]
        assert search_data["count"] >= 1

    def test_search_no_match(self, client):
        """マッチなしの検索"""
        response = client.get("/api/v1/nutrition/search?q=存在しない材料xyz")

        assert response.status_code == 200
        data = response.json()

        search_data = data["data"]
        assert search_data["count"] == 0
        assert len(search_data["results"]) == 0

    def test_search_missing_query(self, client):
        """クエリパラメータなしのリクエスト"""
        response = client.get("/api/v1/nutrition/search")

        # クエリパラメータが必須なのでエラー
        assert response.status_code == 422


class TestGetRecipeNutritionAPI:
    """レシピ栄養取得API のテスト"""

    def test_get_recipe_nutrition_not_implemented(self, client):
        """レシピIDからの栄養取得（未実装）"""
        response = client.get("/api/v1/nutrition/recipe/1")

        # 未実装のため 501 を返す
        assert response.status_code == 501
        data = response.json()
        assert "未実装" in data["detail"]

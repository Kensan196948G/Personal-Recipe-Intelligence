"""
Balance API ルーターのテスト
"""

from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.api.routers.balance import router


# テスト用 FastAPI アプリ
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestRecipeBalanceEndpoint:
    """レシピバランス評価エンドポイントのテスト"""

    def test_get_recipe_balance_success(self):
        """レシピバランス取得成功"""
        response = client.get("/api/v1/balance/1")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "evaluation" in data["data"]
        assert data["data"]["recipe_id"] == 1

    def test_get_recipe_balance_with_large_id(self):
        """大きなIDでのテスト"""
        response = client.get("/api/v1/balance/99999")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestDailyBalanceEndpoint:
    """1日の食事バランス評価エンドポイントのテスト"""

    def test_daily_balance_success(self):
        """1日のバランス評価成功"""
        request_data = {
            "meals": [
                {
                    "calories": 650,
                    "protein": 20,
                    "fat": 18,
                    "carbs": 100,
                    "fiber": 5,
                    "salt": 2.5,
                },
                {
                    "calories": 700,
                    "protein": 22,
                    "fat": 20,
                    "carbs": 105,
                    "fiber": 6,
                    "salt": 2.5,
                },
                {
                    "calories": 650,
                    "protein": 18,
                    "fat": 17,
                    "carbs": 95,
                    "fiber": 5,
                    "salt": 2.5,
                },
            ],
            "target_date": "2025-12-11",
        }

        response = client.post("/api/v1/balance/daily", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["meal_count"] == 3
        assert data["data"]["target_date"] == "2025-12-11"
        assert "evaluation" in data["data"]

    def test_daily_balance_empty_meals(self):
        """空の食事リストでのテスト"""
        request_data = {"meals": []}

        response = client.post("/api/v1/balance/daily", json=request_data)

        assert response.status_code == 400

    def test_daily_balance_without_date(self):
        """日付なしでのテスト"""
        request_data = {
            "meals": [
                {
                    "calories": 650,
                    "protein": 20,
                    "fat": 18,
                    "carbs": 100,
                    "fiber": 5,
                    "salt": 2.5,
                }
            ]
        }

        response = client.post("/api/v1/balance/daily", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "target_date" in data["data"]

    def test_daily_balance_invalid_nutrition(self):
        """不正な栄養データでのテスト"""
        request_data = {
            "meals": [
                {"calories": -100, "protein": 20, "fat": 18, "carbs": 100}  # 負の値
            ]
        }

        response = client.post("/api/v1/balance/daily", json=request_data)

        assert response.status_code == 422  # Validation error


class TestPFCBalanceEndpoint:
    """PFCバランス取得エンドポイントのテスト"""

    def test_get_pfc_balance_success(self):
        """PFCバランス取得成功"""
        response = client.get("/api/v1/balance/pfc/1")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "pfc_balance" in data["data"]
        assert data["data"]["recipe_id"] == 1

        pfc = data["data"]["pfc_balance"]
        assert "protein_ratio" in pfc
        assert "fat_ratio" in pfc
        assert "carbs_ratio" in pfc
        assert "balance_score" in pfc
        assert "pie_chart_data" in pfc


class TestBalanceScoreEndpoint:
    """バランススコア計算エンドポイントのテスト"""

    def test_calculate_score_success(self):
        """スコア計算成功"""
        request_data = {
            "nutrition": {
                "calories": 650,
                "protein": 25,
                "fat": 20,
                "carbs": 85,
                "fiber": 5,
                "salt": 2.5,
            }
        }

        response = client.post("/api/v1/balance/score", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "score" in data["data"]
        assert "nutrition" in data["data"]

        score = data["data"]["score"]
        assert "overall_score" in score
        assert "pfc_score" in score
        assert "is_healthy" in score

    def test_calculate_score_minimal_nutrition(self):
        """最小限の栄養データでのテスト"""
        request_data = {
            "nutrition": {"calories": 100, "protein": 5, "fat": 3, "carbs": 15}
        }

        response = client.post("/api/v1/balance/score", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestReferenceEndpoint:
    """食事摂取基準取得エンドポイントのテスト"""

    def test_get_reference_success(self):
        """基準値取得成功"""
        response = client.get("/api/v1/balance/reference")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "daily_reference" in data["data"]
        assert "pfc_ideal_ratio" in data["data"]

        daily_ref = data["data"]["daily_reference"]
        assert "calories" in daily_ref
        assert "protein" in daily_ref
        assert "fat" in daily_ref
        assert "carbs" in daily_ref

        pfc_ratio = data["data"]["pfc_ideal_ratio"]
        assert "protein" in pfc_ratio
        assert "fat" in pfc_ratio
        assert "carbs" in pfc_ratio


class TestCompareEndpoint:
    """レシピ比較エンドポイントのテスト"""

    def test_compare_recipes_success(self):
        """レシピ比較成功"""
        request_data = [
            {
                "calories": 650,
                "protein": 25,
                "fat": 20,
                "carbs": 85,
                "fiber": 5,
                "salt": 2.5,
            },
            {
                "calories": 800,
                "protein": 30,
                "fat": 35,
                "carbs": 90,
                "fiber": 4,
                "salt": 3.5,
            },
            {
                "calories": 550,
                "protein": 20,
                "fat": 15,
                "carbs": 75,
                "fiber": 6,
                "salt": 2.0,
            },
        ]

        response = client.post("/api/v1/balance/compare", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["count"] == 3
        assert "comparisons" in data["data"]
        assert "best_index" in data["data"]

        # スコア順にソートされているか確認
        comparisons = data["data"]["comparisons"]
        scores = [c["overall_score"] for c in comparisons]
        assert scores == sorted(scores, reverse=True)

    def test_compare_single_recipe(self):
        """1つだけの比較"""
        request_data = [
            {
                "calories": 650,
                "protein": 25,
                "fat": 20,
                "carbs": 85,
                "fiber": 5,
                "salt": 2.5,
            }
        ]

        response = client.post("/api/v1/balance/compare", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["count"] == 1
        assert data["data"]["best_index"] == 0

    def test_compare_empty_list(self):
        """空リストでの比較"""
        request_data = []

        response = client.post("/api/v1/balance/compare", json=request_data)

        assert response.status_code == 400


class TestResponseFormat:
    """レスポンス形式のテスト"""

    def test_standard_response_format(self):
        """標準レスポンス形式の確認"""
        response = client.get("/api/v1/balance/reference")

        assert response.status_code == 200
        data = response.json()

        # 標準フォーマット
        assert "status" in data
        assert "data" in data
        assert "error" in data

        assert data["status"] == "ok"
        assert data["data"] is not None
        assert data["error"] is None

    def test_error_response_format(self):
        """エラーレスポンス形式の確認"""
        # 空の食事リストでエラーを誘発
        response = client.post("/api/v1/balance/daily", json={"meals": []})

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


class TestValidation:
    """入力バリデーションのテスト"""

    def test_negative_values_rejected(self):
        """負の値が拒否されるか"""
        request_data = {
            "nutrition": {"calories": -500, "protein": 20, "fat": 15, "carbs": 80}
        }

        response = client.post("/api/v1/balance/score", json=request_data)

        assert response.status_code == 422

    def test_missing_required_fields(self):
        """必須フィールド欠損"""
        request_data = {
            "nutrition": {
                "calories": 650
                # protein, fat, carbs が欠損
            }
        }

        response = client.post("/api/v1/balance/score", json=request_data)

        assert response.status_code == 422

    def test_extra_fields_ignored(self):
        """追加フィールドが無視されるか"""
        request_data = {
            "nutrition": {
                "calories": 650,
                "protein": 25,
                "fat": 20,
                "carbs": 85,
                "fiber": 5,
                "salt": 2.5,
                "extra_field": "should be ignored",
            }
        }

        response = client.post("/api/v1/balance/score", json=request_data)

        # Extra fields は Pydantic が無視するので成功するはず
        assert response.status_code == 200

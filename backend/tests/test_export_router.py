"""
Export Router API Tests

エクスポート/インポートAPIのテスト
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.api.routers.export import router


# ========================================
# Test App Setup
# ========================================


@pytest.fixture
def app():
    """
    テスト用FastAPIアプリ
    """
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    """
    テストクライアント
    """
    return TestClient(app)


@pytest.fixture
def sample_import_data():
    """
    サンプルインポートデータ
    """
    return {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 1,
        "recipes": [
            {
                "title": "テストレシピ",
                "source_url": "https://example.com/recipe/1",
                "source_type": "web",
                "ingredients": [
                    {"name": "玉ねぎ", "amount": "1", "unit": "個"},
                ],
                "steps": ["玉ねぎを切る", "豚肉を炒める"],
                "cooking_time": 30,
                "servings": 2,
                "tags": ["簡単"],
            }
        ],
    }


# ========================================
# Export Endpoint Tests
# ========================================


def test_export_all_recipes(client):
    """
    全レシピエクスポートAPIのテスト
    """
    response = client.get("/api/v1/export/recipes")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "data" in data
    assert "version" in data["data"]
    assert "recipes" in data["data"]


def test_export_all_recipes_with_download(client):
    """
    ダウンロード形式での全レシピエクスポート
    """
    response = client.get("/api/v1/export/recipes?download=true")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment" in response.headers.get("content-disposition", "")


def test_export_single_recipe(client):
    """
    単一レシピエクスポートAPIのテスト
    """
    recipe_id = 1
    response = client.get(f"/api/v1/export/recipes/{recipe_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data"]["recipe_count"] == 1


def test_export_single_recipe_not_found(client):
    """
    存在しないレシピのエクスポート
    """
    recipe_id = 999
    response = client.get(f"/api/v1/export/recipes/{recipe_id}")

    assert response.status_code == 404


def test_export_single_recipe_with_download(client):
    """
    ダウンロード形式での単一レシピエクスポート
    """
    recipe_id = 1
    response = client.get(f"/api/v1/export/recipes/{recipe_id}?download=true")

    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")


def test_export_batch_recipes(client):
    """
    バッチエクスポートAPIのテスト
    """
    payload = {"recipe_ids": [1]}

    response = client.post("/api/v1/export/recipes/batch", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data"]["recipe_count"] >= 0


def test_export_batch_recipes_empty_list(client):
    """
    空のIDリストでのバッチエクスポート
    """
    payload = {"recipe_ids": []}

    response = client.post("/api/v1/export/recipes/batch", json=payload)

    # Pydanticバリデーションエラー（min_items=1）
    assert response.status_code == 422


def test_export_batch_recipes_with_download(client):
    """
    ダウンロード形式でのバッチエクスポート
    """
    payload = {"recipe_ids": [1]}

    response = client.post("/api/v1/export/recipes/batch?download=true", json=payload)

    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")


# ========================================
# Import Validation Endpoint Tests
# ========================================


def test_validate_import_valid_data(client, sample_import_data):
    """
    正常なインポートデータのバリデーション
    """
    payload = {"data": sample_import_data, "check_duplicates": False}

    response = client.post("/api/v1/import/validate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data"]["is_valid"] is True
    assert data["data"]["valid_recipes"] >= 1


def test_validate_import_invalid_data(client):
    """
    不正なインポートデータのバリデーション
    """
    invalid_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 1,
        "recipes": [
            {
                # titleが欠けている
                "ingredients": [],
                "steps": [],
            }
        ],
    }

    payload = {"data": invalid_data, "check_duplicates": False}

    response = client.post("/api/v1/import/validate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data"]["is_valid"] is False
    assert data["data"]["invalid_recipes"] >= 1


def test_validate_import_no_recipes(client):
    """
    レシピがないデータのバリデーション
    """
    empty_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 0,
        "recipes": [],
    }

    payload = {"data": empty_data, "check_duplicates": False}

    response = client.post("/api/v1/import/validate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data"]["is_valid"] is False


# ========================================
# Import Endpoint Tests
# ========================================


def test_import_recipes_success(client, sample_import_data):
    """
    正常なレシピインポート
    """
    payload = {
        "data": sample_import_data,
        "skip_duplicates": True,
        "overwrite_duplicates": False,
    }

    response = client.post("/api/v1/import/recipes", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data"]["success"] is True
    assert data["data"]["imported_count"] >= 0


def test_import_recipes_validation_failed(client):
    """
    バリデーション失敗時のインポート
    """
    invalid_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 1,
        "recipes": [{"ingredients": [], "steps": []}],  # titleが欠けている
    }

    payload = {
        "data": invalid_data,
        "skip_duplicates": True,
        "overwrite_duplicates": False,
    }

    response = client.post("/api/v1/import/recipes", json=payload)

    assert response.status_code == 200
    data = response.json()

    # バリデーション失敗だがエラーとして返される
    assert data["status"] == "error" or data["data"]["success"] is False


def test_import_recipes_with_overwrite(client, sample_import_data):
    """
    上書きモードでのインポート
    """
    payload = {
        "data": sample_import_data,
        "skip_duplicates": False,
        "overwrite_duplicates": True,
    }

    response = client.post("/api/v1/import/recipes", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"


# ========================================
# File Import Endpoint Tests
# ========================================


def test_import_recipes_from_file(client, sample_import_data):
    """
    ファイルからのレシピインポート
    """
    import json

    file_content = json.dumps(sample_import_data, ensure_ascii=False)

    files = {"file": ("test_recipes.json", file_content, "application/json")}

    response = client.post("/api/v1/import/recipes/file", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data"]["success"] is True


def test_import_recipes_from_file_invalid_json(client):
    """
    不正なJSONファイルのインポート
    """
    invalid_json = "{ invalid json content"

    files = {"file": ("invalid.json", invalid_json, "application/json")}

    response = client.post("/api/v1/import/recipes/file", files=files)

    assert response.status_code == 400


def test_import_recipes_from_file_with_params(client, sample_import_data):
    """
    パラメータ付きファイルインポート
    """
    import json

    file_content = json.dumps(sample_import_data, ensure_ascii=False)

    files = {"file": ("test_recipes.json", file_content, "application/json")}

    response = client.post(
        "/api/v1/import/recipes/file?skip_duplicates=false&overwrite_duplicates=true",
        files=files,
    )

    assert response.status_code == 200


# ========================================
# Health Check Tests
# ========================================


def test_health_check(client):
    """
    ヘルスチェックAPIのテスト
    """
    response = client.get("/api/v1/export/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data"]["service"] == "export-import"
    assert data["data"]["version"] == "1.0"
    assert "endpoints" in data["data"]
    assert len(data["data"]["endpoints"]) >= 6


# ========================================
# Error Handling Tests
# ========================================


def test_export_with_invalid_id_format(client):
    """
    不正なID形式でのエクスポート
    """
    response = client.get("/api/v1/export/recipes/invalid_id")

    assert response.status_code == 422


def test_batch_export_without_payload(client):
    """
    ペイロードなしのバッチエクスポート
    """
    response = client.post("/api/v1/export/recipes/batch")

    assert response.status_code == 422


def test_import_without_payload(client):
    """
    ペイロードなしのインポート
    """
    response = client.post("/api/v1/import/recipes")

    assert response.status_code == 422


# ========================================
# Integration Tests
# ========================================


def test_export_and_import_workflow(client):
    """
    エクスポート→インポートの統合テスト
    """
    # 1. レシピをエクスポート
    export_response = client.get("/api/v1/export/recipes")
    assert export_response.status_code == 200

    exported_data = export_response.json()["data"]

    # 2. バリデーション
    validate_payload = {"data": exported_data, "check_duplicates": False}

    validate_response = client.post("/api/v1/import/validate", json=validate_payload)
    assert validate_response.status_code == 200

    validation_result = validate_response.json()["data"]
    assert validation_result["is_valid"] is True

    # 3. インポート
    import_payload = {
        "data": exported_data,
        "skip_duplicates": True,
        "overwrite_duplicates": False,
    }

    import_response = client.post("/api/v1/import/recipes", json=import_payload)
    assert import_response.status_code == 200

    import_result = import_response.json()["data"]
    assert import_result["success"] is True

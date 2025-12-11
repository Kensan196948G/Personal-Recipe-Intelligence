"""
API Tests
"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


def test_root():
  """ルートエンドポイントのテスト"""
  response = client.get("/")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"


def test_health_check():
  """ヘルスチェックのテスト"""
  response = client.get("/health")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"
  assert data["data"]["service"] == "healthy"


def test_get_recipes():
  """レシピ一覧取得のテスト"""
  response = client.get("/api/v1/recipes")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"
  assert isinstance(data["data"], list)


def test_get_recipe():
  """レシピ詳細取得のテスト"""
  response = client.get("/api/v1/recipes/1")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"
  assert data["data"]["id"] == 1

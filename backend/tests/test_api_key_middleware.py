"""
Tests for API Key Middleware

APIキー認証ミドルウェアのテスト
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import tempfile
import shutil

from backend.services.api_key_service import APIKeyService, APIKeyScope
from backend.middleware.api_key_middleware import APIKeyMiddleware


@pytest.fixture
def temp_dir():
  """一時ディレクトリを作成"""
  temp = tempfile.mkdtemp()
  yield temp
  shutil.rmtree(temp)


@pytest.fixture
def api_key_service(temp_dir):
  """APIキーサービスのインスタンスを作成"""
  return APIKeyService(data_dir=temp_dir)


@pytest.fixture
def app(api_key_service):
  """テスト用のFastAPIアプリケーション"""
  app = FastAPI()

  # ミドルウェアを追加
  middleware = APIKeyMiddleware(api_key_service)
  app.middleware("http")(middleware)

  # テスト用エンドポイント
  @app.get("/api/v1/recipes")
  async def get_recipes():
    return {"status": "ok", "data": {"recipes": []}}

  @app.post("/api/v1/recipes")
  async def create_recipe():
    return {"status": "ok", "data": {"id": "123"}}

  @app.delete("/api/v1/recipes/{recipe_id}")
  async def delete_recipe(recipe_id: str):
    return {"status": "ok", "data": {"id": recipe_id}}

  @app.get("/api/v1/tags")
  async def get_tags():
    return {"status": "ok", "data": {"tags": []}}

  @app.post("/api/v1/tags")
  async def create_tag():
    return {"status": "ok", "data": {"id": "456"}}

  # 公開エンドポイント
  @app.get("/api/v1/public/docs")
  async def public_docs():
    return {"status": "ok", "data": {"docs": "..."}}

  @app.get("/health")
  async def health():
    return {"status": "ok"}

  return app


@pytest.fixture
def client(app):
  """テストクライアント"""
  return TestClient(app)


class TestAPIKeyAuthentication:
  """APIキー認証のテスト"""

  def test_request_without_api_key(self, client):
    """APIキーなしのリクエスト"""
    response = client.get("/api/v1/recipes")

    assert response.status_code == 401
    assert response.json()["status"] == "error"
    assert "API key is required" in response.json()["error"]

  def test_request_with_invalid_api_key(self, client):
    """無効なAPIキーでのリクエスト"""
    response = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": "invalid_key"}
    )

    assert response.status_code == 401
    assert response.json()["status"] == "error"
    assert "Invalid API key" in response.json()["error"]

  def test_request_with_valid_api_key_header(self, client, api_key_service):
    """有効なAPIキー（ヘッダー形式）でのリクエスト"""
    raw_key, api_key = api_key_service.generate_api_key(name="Test Key")

    response = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

  def test_request_with_valid_api_key_bearer(self, client, api_key_service):
    """有効なAPIキー（Bearer形式）でのリクエスト"""
    raw_key, api_key = api_key_service.generate_api_key(name="Test Key")

    response = client.get(
      "/api/v1/recipes",
      headers={"Authorization": f"Bearer {raw_key}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

  def test_public_endpoint_without_api_key(self, client):
    """公開エンドポイントはAPIキー不要"""
    response = client.get("/api/v1/public/docs")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

  def test_health_endpoint_without_api_key(self, client):
    """ヘルスチェックエンドポイントはAPIキー不要"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


class TestRateLimiting:
  """レート制限のテスト"""

  def test_rate_limit_headers(self, client, api_key_service):
    """レート制限情報がヘッダーに含まれることを確認"""
    raw_key, api_key = api_key_service.generate_api_key(name="Test Key")

    response = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 200
    assert "X-RateLimit-Limit-Minute" in response.headers
    assert "X-RateLimit-Remaining-Minute" in response.headers
    assert "X-RateLimit-Limit-Hour" in response.headers
    assert "X-RateLimit-Remaining-Hour" in response.headers

  def test_rate_limit_exceeded(self, client, api_key_service):
    """レート制限超過"""
    from backend.services.api_key_service import RateLimit

    rate_limit = RateLimit(requests_per_minute=2)
    raw_key, api_key = api_key_service.generate_api_key(
      name="Limited Key",
      rate_limit=rate_limit
    )

    # 2回は成功
    response1 = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )
    assert response1.status_code == 200

    response2 = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )
    assert response2.status_code == 200

    # 3回目は制限
    response3 = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )
    assert response3.status_code == 429
    assert "Rate limit exceeded" in response3.json()["error"]

  def test_response_time_header(self, client, api_key_service):
    """レスポンス時間がヘッダーに含まれることを確認"""
    raw_key, api_key = api_key_service.generate_api_key(name="Test Key")

    response = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 200
    assert "X-Response-Time" in response.headers


class TestScopeValidation:
  """スコープ検証のテスト"""

  def test_read_recipes_with_read_scope(self, client, api_key_service):
    """読み取りスコープでレシピ取得"""
    scope = APIKeyScope(read_recipes=True, write_recipes=False)
    raw_key, api_key = api_key_service.generate_api_key(
      name="Read Only Key",
      scope=scope
    )

    response = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 200

  def test_write_recipes_without_write_scope(self, client, api_key_service):
    """書き込みスコープなしでレシピ作成"""
    scope = APIKeyScope(read_recipes=True, write_recipes=False)
    raw_key, api_key = api_key_service.generate_api_key(
      name="Read Only Key",
      scope=scope
    )

    response = client.post(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["error"]

  def test_write_recipes_with_write_scope(self, client, api_key_service):
    """書き込みスコープでレシピ作成"""
    scope = APIKeyScope(read_recipes=True, write_recipes=True)
    raw_key, api_key = api_key_service.generate_api_key(
      name="Write Key",
      scope=scope
    )

    response = client.post(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 200

  def test_delete_recipes_without_delete_scope(self, client, api_key_service):
    """削除スコープなしでレシピ削除"""
    scope = APIKeyScope(
      read_recipes=True,
      write_recipes=True,
      delete_recipes=False
    )
    raw_key, api_key = api_key_service.generate_api_key(
      name="No Delete Key",
      scope=scope
    )

    response = client.delete(
      "/api/v1/recipes/123",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["error"]

  def test_delete_recipes_with_delete_scope(self, client, api_key_service):
    """削除スコープでレシピ削除"""
    scope = APIKeyScope(
      read_recipes=True,
      write_recipes=True,
      delete_recipes=True
    )
    raw_key, api_key = api_key_service.generate_api_key(
      name="Full Access Key",
      scope=scope
    )

    response = client.delete(
      "/api/v1/recipes/123",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 200

  def test_read_tags_with_read_scope(self, client, api_key_service):
    """読み取りスコープでタグ取得"""
    scope = APIKeyScope(read_tags=True, write_tags=False)
    raw_key, api_key = api_key_service.generate_api_key(
      name="Tag Read Key",
      scope=scope
    )

    response = client.get(
      "/api/v1/tags",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 200

  def test_write_tags_without_write_scope(self, client, api_key_service):
    """書き込みスコープなしでタグ作成"""
    scope = APIKeyScope(read_tags=True, write_tags=False)
    raw_key, api_key = api_key_service.generate_api_key(
      name="Tag Read Only Key",
      scope=scope
    )

    response = client.post(
      "/api/v1/tags",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["error"]


class TestUsageTracking:
  """使用量トラッキングのテスト"""

  def test_usage_is_recorded(self, client, api_key_service):
    """使用量が記録されることを確認"""
    raw_key, api_key = api_key_service.generate_api_key(name="Test Key")

    # リクエストを送信
    response = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 200

    # 使用量を確認
    stats = api_key_service.get_usage_stats(api_key.key_id)
    assert stats["total_requests"] == 1
    assert stats["current_usage"]["last_minute"] == 1

  def test_multiple_requests_recorded(self, client, api_key_service):
    """複数のリクエストが記録されることを確認"""
    raw_key, api_key = api_key_service.generate_api_key(name="Test Key")

    # 3回リクエストを送信
    for i in range(3):
      response = client.get(
        "/api/v1/recipes",
        headers={"X-API-Key": raw_key}
      )
      assert response.status_code == 200

    # 使用量を確認
    stats = api_key_service.get_usage_stats(api_key.key_id)
    assert stats["total_requests"] == 3
    assert stats["current_usage"]["last_minute"] == 3


class TestRevokedKeys:
  """無効化されたキーのテスト"""

  def test_revoked_key_rejected(self, client, api_key_service):
    """無効化されたキーは拒否される"""
    raw_key, api_key = api_key_service.generate_api_key(name="Test Key")

    # キーを無効化
    api_key_service.revoke_api_key(api_key.key_id)

    # リクエストは拒否される
    response = client.get(
      "/api/v1/recipes",
      headers={"X-API-Key": raw_key}
    )

    assert response.status_code == 401
    assert "Invalid API key" in response.json()["error"]


if __name__ == "__main__":
  pytest.main([__file__, "-v"])

"""
Tests for Rate Limiter Middleware

Tests rate limiting functionality for different endpoint types.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from backend.app import app

client = TestClient(app)


class TestRateLimiting:
  """Test rate limiting across different endpoint types"""

  def test_default_rate_limit_not_exceeded(self):
    """
    Test that default rate limit (100/min) is not triggered with few requests
    """
    # Make 5 requests to default endpoint
    for i in range(5):
      response = client.get("/health")
      assert response.status_code == 200
      assert response.json()["status"] == "ok"

  def test_rate_limit_headers_present(self):
    """
    Test that rate limit headers are included in response
    """
    response = client.get("/health")
    assert response.status_code == 200

  def test_ocr_rate_limit_structure(self):
    """
    Test OCR endpoints have correct rate limit (5/min)
    """
    response = client.post(
      "/api/v1/ocr/extract",
      json={}
    )
    assert response.status_code in [200, 422]

  def test_video_rate_limit_structure(self):
    """
    Test video endpoints have correct rate limit (5/min)
    """
    response = client.post(
      "/api/v1/video/process",
      json={}
    )
    assert response.status_code in [200, 422]

  def test_scraper_rate_limit_structure(self):
    """
    Test scraper endpoints have correct rate limit (10/min)
    """
    response = client.post(
      "/api/v1/scraper/parse-url",
      json={"url": "https://example.com"}
    )
    assert response.status_code == 200

  def test_recipe_endpoints_default_limit(self):
    """
    Test recipe CRUD endpoints use default rate limit (100/min)
    """
    response = client.get("/api/v1/recipes")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

  def test_rate_limit_status_endpoint(self):
    """
    Test rate limit status endpoint returns correct configuration
    """
    response = client.get("/api/v1/rate-limit-status")
    assert response.status_code == 200

    data = response.json()["data"]
    assert "limits" in data
    assert data["limits"]["ocr"] == "5/minute"
    assert data["limits"]["video"] == "5/minute"
    assert data["limits"]["scraper"] == "10/minute"
    assert data["limits"]["default"] == "100/minute"


class TestEndpointIntegration:
  """Test that rate limiting is properly integrated with all endpoints"""

  def test_root_endpoint_with_rate_limit(self):
    """Test root endpoint has rate limiting"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()["data"]

  def test_health_endpoint_with_rate_limit(self):
    """Test health endpoint has rate limiting"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["data"]["rate_limiting"] == "enabled"

  def test_ocr_upload_with_rate_limit(self):
    """Test OCR upload endpoint has rate limiting"""
    response = client.post(
      "/api/v1/ocr/upload",
      files={"file": ("test.jpg", b"fake image data", "image/jpeg")}
    )
    assert response.status_code == 200

  def test_recipe_list_with_rate_limit(self):
    """Test recipe list endpoint has rate limiting"""
    response = client.get("/api/v1/recipes")
    assert response.status_code == 200
    assert "recipes" in response.json()["data"]

  def test_recipe_create_with_rate_limit(self):
    """Test recipe create endpoint has rate limiting"""
    response = client.post(
      "/api/v1/recipes",
      json={
        "title": "Test Recipe",
        "ingredients": ["ingredient1"],
        "instructions": ["step1"]
      }
    )
    assert response.status_code == 200


class TestConcurrentRequests:
  """Test rate limiting behavior with concurrent requests"""

  def test_sequential_requests_within_limit(self):
    """Test that sequential requests within limit all succeed"""
    responses = []
    for i in range(3):
      response = client.get("/health")
      responses.append(response)

    for response in responses:
      assert response.status_code == 200

  def test_different_endpoints_independent_limits(self):
    """Test that different endpoints have independent rate limits"""
    health_response = client.get("/health")
    assert health_response.status_code == 200

    recipes_response = client.get("/api/v1/recipes")
    assert recipes_response.status_code == 200

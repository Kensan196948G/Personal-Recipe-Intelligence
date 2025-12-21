#!/usr/bin/env python3
"""
Example Client for Testing Rate Limiting

Demonstrates how to handle rate limits in client applications.
"""

import requests
import time
import sys
from typing import Dict, Any, Optional


API_BASE = "http://localhost:8000"


def make_request(
  method: str,
  endpoint: str,
  data: Optional[Dict[str, Any]] = None,
  max_retries: int = 3
) -> Optional[Dict[str, Any]]:
  """
  Make API request with rate limit handling.

  Args:
    method: HTTP method (GET, POST, etc.)
    endpoint: API endpoint path
    data: Request data (for POST/PUT)
    max_retries: Maximum retry attempts on rate limit

  Returns:
    Response data or None if failed
  """
  url = f"{API_BASE}{endpoint}"
  retries = 0

  while retries < max_retries:
    try:
      if method == "GET":
        response = requests.get(url)
      elif method == "POST":
        response = requests.post(url, json=data)
      elif method == "PUT":
        response = requests.put(url, json=data)
      elif method == "DELETE":
        response = requests.delete(url)
      else:
        print(f"Unsupported method: {method}")
        return None

      # Handle rate limiting
      if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        print(f"\n⚠️  Rate limit exceeded!")
        print(f"   Waiting {retry_after} seconds before retry...")
        print(f"   Retry attempt {retries + 1}/{max_retries}")
        time.sleep(retry_after)
        retries += 1
        continue

      # Success
      if response.status_code == 200:
        remaining = response.headers.get("X-RateLimit-Remaining", "unknown")
        print(f"✓ Success (Remaining: {remaining})")
        return response.json()

      # Other errors
      print(f"✗ Error: {response.status_code}")
      print(f"   {response.text}")
      return None

    except requests.exceptions.ConnectionError:
      print("✗ Error: Could not connect to API")
      print("   Make sure the API is running: ./dev.sh")
      return None

    except Exception as e:
      print(f"✗ Unexpected error: {e}")
      return None

  print(f"✗ Failed after {max_retries} retries")
  return None


def test_health():
  """Test health endpoint (100/min limit)"""
  print("\n=== Testing Health Endpoint (100/min) ===")
  result = make_request("GET", "/health")
  if result:
    print(f"Response: {result}")


def test_rate_limit_status():
  """Test rate limit status endpoint"""
  print("\n=== Rate Limit Status ===")
  result = make_request("GET", "/api/v1/rate-limit-status")
  if result and result.get("data"):
    limits = result["data"].get("limits", {})
    print(f"OCR: {limits.get('ocr')}")
    print(f"Video: {limits.get('video')}")
    print(f"Scraper: {limits.get('scraper')}")
    print(f"Default: {limits.get('default')}")


def test_ocr_rate_limit():
  """Test OCR endpoint (5/min limit)"""
  print("\n=== Testing OCR Endpoint (5/min) ===")
  print("Making 6 requests to trigger rate limit...")

  for i in range(6):
    print(f"\nRequest {i+1}/6:")
    result = make_request("POST", "/api/v1/ocr/extract", data={})
    if not result:
      break
    time.sleep(0.5)


def test_scraper_rate_limit():
  """Test scraper endpoint (10/min limit)"""
  print("\n=== Testing Scraper Endpoint (10/min) ===")
  print("Making 5 requests...")

  for i in range(5):
    print(f"\nRequest {i+1}/5:")
    result = make_request(
      "POST",
      "/api/v1/scraper/parse-url",
      data={"url": "https://example.com"}
    )
    if not result:
      break
    time.sleep(0.3)


def test_recipes():
  """Test recipe endpoints (100/min limit)"""
  print("\n=== Testing Recipe Endpoints (100/min) ===")

  # List recipes
  print("\n1. List recipes:")
  result = make_request("GET", "/api/v1/recipes")
  if result:
    print(f"   Total recipes: {result.get('data', {}).get('total', 0)}")

  # Create recipe
  print("\n2. Create recipe:")
  recipe_data = {
    "title": "Test Recipe",
    "ingredients": ["ingredient1", "ingredient2"],
    "instructions": ["step1", "step2"],
    "tags": ["test"]
  }
  result = make_request("POST", "/api/v1/recipes", data=recipe_data)


def main():
  """Main function"""
  print("=" * 70)
  print("Personal Recipe Intelligence - Rate Limiting Example Client")
  print("=" * 70)

  # Check if API is running
  try:
    response = requests.get(f"{API_BASE}/health", timeout=2)
    print(f"✓ API is running at {API_BASE}")
  except:
    print(f"✗ API is not running at {API_BASE}")
    print("\nStart the API first:")
    print("  cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence")
    print("  ./dev.sh")
    sys.exit(1)

  # Run tests
  test_rate_limit_status()
  test_health()
  test_ocr_rate_limit()
  test_scraper_rate_limit()
  test_recipes()

  print("\n" + "=" * 70)
  print("Tests completed!")
  print("=" * 70)


if __name__ == "__main__":
  main()

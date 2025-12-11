"""
Rate Limiter Middleware for Personal Recipe Intelligence API

IP-based rate limiting with different limits for different endpoints:
- OCR endpoints: 5 requests/minute
- Video endpoints: 5 requests/minute
- Scraper endpoints: 10 requests/minute
- Default: 100 requests/minute
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Callable
import logging

logger = logging.getLogger(__name__)


def get_client_identifier(request: Request) -> str:
  """
  Get client identifier for rate limiting.
  Uses X-Forwarded-For header if available, otherwise remote address.

  Args:
    request: FastAPI request object

  Returns:
    Client IP address as string
  """
  # Check for X-Forwarded-For header (proxy/load balancer)
  forwarded_for = request.headers.get("X-Forwarded-For")
  if forwarded_for:
    # Take the first IP in the chain
    client_ip = forwarded_for.split(",")[0].strip()
    logger.debug(f"Rate limit identifier from X-Forwarded-For: {client_ip}")
    return client_ip

  # Fallback to direct remote address
  client_ip = get_remote_address(request)
  logger.debug(f"Rate limit identifier from remote address: {client_ip}")
  return client_ip


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
  """
  Custom error handler for rate limit exceeded.
  Returns consistent JSON response format.

  Args:
    request: FastAPI request object
    exc: RateLimitExceeded exception

  Returns:
    JSONResponse with error details
  """
  client_ip = get_client_identifier(request)
  logger.warning(
    f"Rate limit exceeded for {client_ip} on {request.url.path}",
    extra={
      "client_ip": client_ip,
      "path": request.url.path,
      "method": request.method,
    }
  )

  return JSONResponse(
    status_code=429,
    content={
      "status": "error",
      "data": None,
      "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Rate limit exceeded. Please try again later.",
        "detail": str(exc.detail) if hasattr(exc, 'detail') else "Too many requests"
      }
    },
    headers={
      "Retry-After": "60",  # Suggest retry after 60 seconds
      "X-RateLimit-Limit": str(exc.detail).split()[0] if hasattr(exc, 'detail') else "Unknown"
    }
  )


# Initialize limiter with custom key function
limiter = Limiter(
  key_func=get_client_identifier,
  default_limits=["100/minute"],
  storage_uri="memory://",  # In-memory storage for simplicity
  strategy="fixed-window",  # Fixed window strategy
  headers_enabled=True,  # Add rate limit headers to responses
)


# Rate limit decorators for different endpoint types
def ocr_rate_limit() -> Callable:
  """
  Rate limiter for OCR endpoints (expensive operations).
  Limit: 5 requests per minute
  """
  return limiter.limit("5/minute")


def video_rate_limit() -> Callable:
  """
  Rate limiter for video processing endpoints (expensive operations).
  Limit: 5 requests per minute
  """
  return limiter.limit("5/minute")


def scraper_rate_limit() -> Callable:
  """
  Rate limiter for web scraping endpoints (moderate operations).
  Limit: 10 requests per minute
  """
  return limiter.limit("10/minute")


def default_rate_limit() -> Callable:
  """
  Default rate limiter for general endpoints.
  Limit: 100 requests per minute
  """
  return limiter.limit("100/minute")


def get_rate_limit_status(request: Request) -> dict:
  """
  Get current rate limit status for a client.

  Args:
    request: FastAPI request object

  Returns:
    Dictionary with rate limit status information
  """
  client_ip = get_client_identifier(request)

  return {
    "client_ip": client_ip,
    "limits": {
      "ocr": "5/minute",
      "video": "5/minute",
      "scraper": "10/minute",
      "default": "100/minute"
    },
    "strategy": "fixed-window"
  }


def log_rate_limit_info(request: Request) -> None:
  """
  Log rate limit information for monitoring.

  Args:
    request: FastAPI request object
  """
  client_ip = get_client_identifier(request)
  logger.info(
    f"Rate limit check for {client_ip}",
    extra={
      "client_ip": client_ip,
      "path": request.url.path,
      "method": request.method,
    }
  )

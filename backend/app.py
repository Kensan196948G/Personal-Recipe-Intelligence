"""
Personal Recipe Intelligence - Main API Application

FastAPI application with rate limiting, CORS, and structured routing.
Follows CLAUDE.md specifications for PRI project.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import logging
from pathlib import Path

from backend.middleware.rate_limiter import (
  limiter,
  rate_limit_exceeded_handler,
  get_rate_limit_status,
  default_rate_limit,
)
from backend.api.v1 import (
  ocr_router,
  video_router,
  scraper_router,
)
# Use the full implementation router instead of stub
from backend.api.routers.recipes import router as recipes_router
from backend.api.routers.collector import router as collector_router

# Database initialization
from backend.core.database import create_db_and_tables
# Import models to register them with SQLModel
from backend.models import Recipe, Ingredient, Tag, RecipeTag, Step

# Configure logging
log_dir = Path(__file__).resolve().parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
  level=logging.INFO,
  format='{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
  handlers=[
    logging.StreamHandler(),
    logging.FileHandler(log_dir / "api.log")
  ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
  title="Personal Recipe Intelligence API",
  description="API for recipe collection, parsing, and management with rate limiting",
  version="1.0.0",
  docs_url="/api/docs",
  redoc_url="/api/redoc",
  openapi_url="/api/openapi.json"
)

# Add rate limiter to app state
app.state.limiter = limiter

# Register rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configure CORS
# For development: use specific origins; avoid wildcard "*" with credentials
import os
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173").split(",")

app.add_middleware(
  CORSMiddleware,
  allow_origins=CORS_ORIGINS,
  allow_credentials=True,
  allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
  allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Include routers with rate limiting
app.include_router(ocr_router)
app.include_router(video_router)
app.include_router(scraper_router)
app.include_router(recipes_router)
app.include_router(collector_router)


@app.on_event("startup")
async def startup_event():
  """
  Application startup event handler
  """
  logger.info("Starting Personal Recipe Intelligence API")

  # Initialize database tables
  logger.info("Initializing database tables...")
  create_db_and_tables()
  logger.info("Database tables initialized")

  logger.info(f"Rate limiting enabled with slowapi")
  logger.info(f"Docs available at /api/docs")


@app.on_event("shutdown")
async def shutdown_event():
  """
  Application shutdown event handler
  """
  logger.info("Shutting down Personal Recipe Intelligence API")


@app.get("/")
@default_rate_limit()
async def root(request: Request):
  """
  Root endpoint - API information
  Rate limit: 100 requests/minute (default)
  """
  return {
    "status": "ok",
    "data": {
      "name": "Personal Recipe Intelligence API",
      "version": "1.0.0",
      "docs": "/api/docs",
      "endpoints": {
        "recipes": "/api/v1/recipes",
        "ocr": "/api/v1/ocr",
        "video": "/api/v1/video",
        "scraper": "/api/v1/scraper"
      }
    },
    "error": None
  }


@app.get("/health")
@default_rate_limit()
async def health_check(request: Request):
  """
  Health check endpoint - no authentication required
  Rate limit: 100 requests/minute (default)
  """
  return {
    "status": "ok",
    "data": {
      "service": "healthy",
      "rate_limiting": "enabled"
    },
    "error": None
  }


@app.get("/api/v1/rate-limit-status")
@default_rate_limit()
async def rate_limit_status(request: Request):
  """
  Get current rate limit configuration and status
  Rate limit: 100 requests/minute (default)
  """
  status = get_rate_limit_status(request)
  return {
    "status": "ok",
    "data": status,
    "error": None
  }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
  """
  Global exception handler for unhandled errors
  """
  logger.error(
    f"Unhandled exception on {request.url.path}: {str(exc)}",
    exc_info=True,
    extra={
      "path": request.url.path,
      "method": request.method,
      "client_host": request.client.host if request.client else "unknown"
    }
  )

  # Only expose error details in development mode
  is_debug = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

  return JSONResponse(
    status_code=500,
    content={
      "status": "error",
      "data": None,
      "error": {
        "code": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred",
        "detail": str(exc) if is_debug else None
      }
    }
  )


if __name__ == "__main__":
  import uvicorn
  logger.info("Starting development server...")
  uvicorn.run(
    "backend.app:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="info"
  )

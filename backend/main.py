"""
Personal Recipe Intelligence - FastAPI Backend

メインアプリケーションエントリポイント。
CLAUDE.md に準拠した API 設計・認証・エラーハンドリングを実装。
"""

import os
import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.middleware.auth_middleware import AuthMiddleware
from backend.core.config import settings

# 環境変数読み込み
load_dotenv()

# ロギング設定（CLAUDE.md Section 6.2準拠）
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logger = logging.getLogger(__name__)

# アプリケーション設定
APP_VERSION = "1.0.0"
APP_TITLE = "Personal Recipe Intelligence API"
APP_DESCRIPTION = "個人向け料理レシピ収集・解析・管理システム"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションライフサイクル管理

    起動時・終了時の処理を定義。
    """
    # 起動時処理（JSON形式ログ）
    logger.info(f"Personal Recipe Intelligence API starting - Version: {APP_VERSION}, Environment: {settings.app_env}")

    # データディレクトリ確認
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)

    yield

    # 終了時処理
    logger.info("Personal Recipe Intelligence API shutting down")


# FastAPI アプリケーション
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS ミドルウェア（CLAUDE.md Section 5準拠 - セキュリティ強化）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # 設定ファイルから取得
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    max_age=3600,  # プリフライトキャッシュ
)

# 認証ミドルウェア追加
# /health, /docs, /openapi.json, /redoc は認証除外
app.add_middleware(
    AuthMiddleware,
    excluded_paths=["/health", "/docs", "/openapi.json", "/redoc", "/", "/api/v1/recipes"],
)

# ============================================================
# ルーター登録
# ============================================================
from backend.api.routers import (
    recipes_router,
    tags_router,
    scraper_router,
    ocr_router,
    translation_router,
    search_router,
    nutrition_router,
    cache_router,
)
from backend.api.routers.csv_import import router as csv_import_router
from backend.api.routers.collector import router as collector_router
from backend.api.routers.auth import router as auth_router

app.include_router(auth_router)  # 認証（認証不要）
app.include_router(recipes_router)
app.include_router(tags_router)
app.include_router(scraper_router)
app.include_router(ocr_router)
app.include_router(translation_router)
app.include_router(search_router)
app.include_router(nutrition_router)
app.include_router(cache_router)
app.include_router(csv_import_router)
app.include_router(collector_router)


# ============================================================
# ヘルスチェック（認証不要）
# ============================================================
@app.get(
    "/health",
    tags=["system"],
    summary="ヘルスチェック",
    response_model=dict,
)
async def health_check():
    """
    API ヘルスチェックエンドポイント（認証不要）

    Returns:
      dict: ステータス情報
    """
    return {
        "status": "ok",
        "data": {
            "service": "Personal Recipe Intelligence API",
            "version": APP_VERSION,
            "health": "healthy",
        },
        "error": None,
    }


@app.get(
    "/",
    tags=["system"],
    summary="ルートエンドポイント",
    response_model=dict,
)
async def root():
    """
    ルートエンドポイント（認証不要）

    Returns:
      dict: API 情報
    """
    return {
        "status": "ok",
        "data": {
            "message": "Personal Recipe Intelligence API",
            "version": APP_VERSION,
            "docs": "/docs",
        },
        "error": None,
    }


# ============================================================
# レシピ API（認証必要）
# ============================================================
# Note: All recipe endpoints are handled by recipes_router
# from api.routers.recipes - no duplicate endpoints needed


# ============================================================
# グローバルエラーハンドラ
# ============================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    グローバル例外ハンドラ

    Args:
      request: リクエスト
      exc: 例外

    Returns:
      JSONResponse: エラーレスポンス
    """
    # エラーID生成（追跡用）
    error_id = uuid.uuid4().hex[:12]

    # 内部ログに詳細を記録（CLAUDE.md Section 6準拠）
    logger.error(
        f"Error ID {error_id}: {str(exc)}",
        exc_info=True,
        extra={
            "error_id": error_id,
            "path": str(request.url.path),
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

    # セキュリティ: 本番環境では詳細なエラーメッセージを隠す
    if settings.debug:
        error_detail = str(exc)
    else:
        error_detail = f"Internal server error. Error ID: {error_id}"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "data": None,
            "error": error_detail,
            "error_id": error_id,
        },
    )


# ============================================================
# アプリケーション起動
# ============================================================
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )
